from __future__ import annotations

import math
import re
from typing import Any

from .nrrf837_continuum import UNITY_SELECTOR_VERSION, build_continuum_receipt


_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = {
    "about",
    "after",
    "also",
    "been",
    "before",
    "being",
    "could",
    "from",
    "have",
    "into",
    "just",
    "local",
    "more",
    "other",
    "start",
    "that",
    "their",
    "there",
    "these",
    "they",
    "this",
    "through",
    "want",
    "with",
    "would",
}


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if str(value)))


def _stem(value: str) -> str:
    word = value.lower()
    if len(word) > 6 and word.endswith("ing"):
        word = word[:-3]
    elif len(word) > 5 and word.endswith("ed"):
        word = word[:-2]
    elif len(word) > 4 and word.endswith("es"):
        word = word[:-2]
    elif len(word) > 4 and word.endswith("s"):
        word = word[:-1]
    return word


def _terms(*values: Any) -> set[str]:
    result: set[str] = set()
    for value in values:
        if isinstance(value, (list, tuple, set)):
            result.update(_terms(*value))
            continue
        if isinstance(value, dict):
            result.update(_terms(*value.values()))
            continue
        for word in _TOKEN.findall(str(value or "").lower()):
            stemmed = _stem(word)
            if len(stemmed) >= 3 and stemmed not in _STOP:
                result.add(stemmed)
    return result


def _event_text(
    event: dict[str, Any], occurrences: dict[str, dict[str, Any]]
) -> str:
    texts = [
        str(occurrences[occurrence_id].get("exact_text") or "")
        for occurrence_id in event.get("exact_source_ids", [])
        if occurrence_id in occurrences
    ]
    return "\n".join(item for item in texts if item)


def _coordination_kind(event: dict[str, Any]) -> str:
    metadata = event.get("metadata", {})
    explicit = str(
        metadata.get("coordination_kind")
        or metadata.get("entity_kind")
        or ""
    ).upper()
    aliases = {
        "PERSON_INTENT": "PERSON",
        "PROFILE": "PERSON",
        "AGREEMENT_TEMPLATE": "AGREEMENT_TEMPLATE",
        "COLLECTIVE_ACTION": "AGREEMENT",
        "ACTION_RETURN": "LIVING_RETURN",
        "PROBLEM": "INTENT",
    }
    if explicit:
        return aliases.get(explicit, explicit)
    living = str(metadata.get("living_form") or "").upper()
    if living:
        return aliases.get(living, living)
    label = str(event.get("form_label") or "").lower()
    if "agreement" in label and "template" in label:
        return "AGREEMENT_TEMPLATE"
    if "commit" in label:
        return "COMMITMENT"
    if "return" in label or "consequence" in label:
        return "LIVING_RETURN"
    if "project" in label:
        return "PROJECT"
    if "person" in label or "profile" in label:
        return "PERSON"
    if "resource" in label or "template" in label:
        return "RESOURCE"
    if "intent" in label or "problem" in label or "goal" in label:
        return "INTENT"
    return "FORM"


def _authorship_role(event: dict[str, Any]) -> str:
    metadata = event.get("metadata", {})
    explicit = str(metadata.get("authorship_role") or "").upper()
    if explicit in {"HUMAN", "AI", "TOKEN", "LIVING_SYSTEM"}:
        return explicit
    kind = _coordination_kind(event)
    adapter = str(event.get("adapter_label") or "").lower()
    author = str(event.get("authored_by") or "").lower()
    if kind == "COMMITMENT":
        return "TOKEN"
    if kind == "LIVING_RETURN" or adapter == "hardware":
        return "LIVING_SYSTEM"
    if adapter == "agent" or "agent" in author or author.endswith("-ai"):
        return "AI"
    return "HUMAN"


def _authored_handle(event: dict[str, Any]) -> str:
    """Expose the submitted public author while retaining the internal actor ID."""

    metadata = event.get("metadata", {})
    return str(
        metadata.get("authored_handle")
        or metadata.get("submitted_authored_by")
        or metadata.get("authored_by")
        or event.get("authored_by")
        or "OPEN"
    )


def _internal_actor_id(event: dict[str, Any]) -> str:
    metadata = event.get("metadata", {})
    return str(
        metadata.get("internal_actor_id")
        or metadata.get("created_by")
        or metadata.get("authored_by")
        or event.get("authored_by")
        or _authored_handle(event)
    )


def _location(event: dict[str, Any]) -> tuple[str | None, tuple[float, float] | None]:
    metadata = event.get("metadata", {})
    raw = metadata.get("location")
    label = metadata.get("location_label") or metadata.get("locality")
    coordinates: tuple[float, float] | None = None
    if isinstance(raw, dict):
        label = label or raw.get("label")
        try:
            coordinates = (float(raw["lat"]), float(raw["lon"]))
        except (KeyError, TypeError, ValueError):
            coordinates = None
    elif raw:
        label = label or str(raw)
    source_location = metadata.get("source_location")
    return (
        str(label or source_location).strip() if label or source_location else None,
        coordinates,
    )


def _distance_km(
    left: tuple[float, float] | None, right: tuple[float, float] | None
) -> float | None:
    if left is None or right is None:
        return None
    lat1, lon1 = map(math.radians, left)
    lat2, lon2 = map(math.radians, right)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    hav = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(
        dlon / 2
    ) ** 2
    return 6371.0088 * 2 * math.asin(min(1.0, math.sqrt(hav)))


def _root_intent(
    event: dict[str, Any],
    events: dict[str, dict[str, Any]],
    proposals: list[dict[str, Any]],
) -> dict[str, Any]:
    metadata = event.get("metadata", {})
    direct = metadata.get("intent_event_id") or metadata.get("source_intent_event_id")
    if direct and str(direct) in events:
        return events[str(direct)]
    proposal_id = metadata.get("commitment_proposal_id")
    for proposal in proposals:
        if (
            proposal_id == proposal.get("id")
            or event.get("action_id") == proposal.get("action_id")
            or str(event.get("id"))
            in {str(item) for item in proposal.get("target_event_ids", [])}
        ):
            return events.get(str(proposal["intent_event_id"]), event)
    if _coordination_kind(event) == "INTENT":
        return event
    seen: set[str] = set()
    queue = list(event.get("parent_event_ids", []))
    while queue:
        event_id = str(queue.pop(0))
        if event_id in seen:
            continue
        seen.add(event_id)
        parent = events.get(event_id)
        if parent is None:
            continue
        if _coordination_kind(parent) == "INTENT":
            return parent
        queue.extend(parent.get("parent_event_ids", []))
    return event


def _relation_for_target(
    *,
    relation_receipts: list[dict[str, Any]],
    intent_occurrence_ids: set[str],
    target_occurrence_ids: set[str],
) -> dict[str, Any] | None:
    matches = []
    for relation in relation_receipts:
        endpoints = {
            str(relation.get("source_occurrence") or ""),
            str(relation.get("target_occurrence") or ""),
        }
        if endpoints & intent_occurrence_ids and endpoints & target_occurrence_ids:
            matches.append(relation)
    if not matches:
        return None
    return max(matches, key=lambda item: float(item.get("score") or 0.0))


def build_coordination_receipt(
    *,
    event: dict[str, Any],
    field_events: list[dict[str, Any]],
    field_occurrences: list[dict[str, Any]],
    relation_receipts: list[dict[str, Any]],
    commitment_proposals: list[dict[str, Any]],
    living_problems: list[dict[str, Any]],
    living_actions: list[dict[str, Any]],
    living_returns: list[dict[str, Any]],
    closure_level_id: str,
) -> dict[str, Any]:
    """Derive the intent-to-return product interface without issuing truth.

    Similarity and location are candidate evidence only.  AI suggests paths but
    cannot decide consent.  Commitment receipts constrain the selected action
    forms and never gate ordinary interaction.
    """

    events = {str(item["id"]): item for item in field_events}
    occurrences = {str(item["id"]): item for item in field_occurrences}
    # Preserve the first canonical event for a source occurrence.  Later
    # translations can reference the same occurrence but are derived lenses.
    event_by_occurrence = {}
    for candidate in field_events:
        for occurrence_id in candidate.get("exact_source_ids", []):
            event_by_occurrence.setdefault(str(occurrence_id), candidate)

    intent = _root_intent(event, events, commitment_proposals)
    intent_id = str(intent["id"])
    intent_text = _event_text(intent, occurrences)
    intent_location, intent_coordinates = _location(intent)
    intent_metadata = intent.get("metadata", {})
    radius_km = intent_metadata.get("radius_km")
    try:
        radius = float(radius_km) if radius_km is not None else None
    except (TypeError, ValueError):
        radius = None
    intent_terms = _terms(
        intent_text,
        intent.get("form_label"),
        intent.get("relation_hints", []),
        intent.get("capabilities", []),
        intent_metadata.get("intent_tags", []),
    )
    intent_occurrence_ids = {str(item) for item in intent.get("exact_source_ids", [])}
    intent_problem = next(
        (
            problem
            for problem in living_problems
            if str(problem.get("occurrence_id")) in intent_occurrence_ids
        ),
        None,
    )

    paths: list[dict[str, Any]] = []
    allowed_kinds = {"PERSON", "PROJECT", "RESOURCE", "AGREEMENT_TEMPLATE"}
    for target in field_events:
        target_id = str(target["id"])
        if target_id == intent_id:
            continue
        kind = _coordination_kind(target)
        if kind not in allowed_kinds:
            continue
        if _authorship_role(target) in {"AI", "TOKEN"}:
            continue
        target_text = _event_text(target, occurrences)
        target_terms = _terms(
            target_text,
            target.get("form_label"),
            target.get("relation_hints", []),
            target.get("capabilities", []),
            target.get("metadata", {}).get("intent_tags", []),
        )
        shared = sorted(intent_terms & target_terms)
        target_location, target_coordinates = _location(target)
        same_locality = bool(
            intent_location
            and target_location
            and intent_location.casefold() == target_location.casefold()
        )
        distance = _distance_km(intent_coordinates, target_coordinates)
        within_radius = bool(
            distance is not None and radius is not None and distance <= radius
        )
        relation = _relation_for_target(
            relation_receipts=relation_receipts,
            intent_occurrence_ids=intent_occurrence_ids,
            target_occurrence_ids={
                str(item) for item in target.get("exact_source_ids", [])
            },
        )
        if relation and str(relation.get("verdict") or "OPEN") == "FALSE":
            continue
        if not shared and not same_locality and not within_radius and relation is None:
            continue

        matched = [*(f"shared:{item}" for item in shared[:8])]
        if same_locality:
            matched.append(f"same-locality:{intent_location}")
        if within_radius and distance is not None:
            matched.append(f"within-authored-radius:{distance:.2f}km")
        if relation is not None:
            matched.append(
                f"relation:{relation.get('relation_type') or 'OPEN_RELATION'}"
            )
        score = (
            len(shared) * 0.12
            + (0.22 if same_locality else 0.0)
            + (0.28 if within_radius else 0.0)
            + (float(relation.get("score") or 0.0) if relation else 0.0)
        )
        label = str(
            target.get("metadata", {}).get("title")
            or target.get("metadata", {}).get("display_name")
            or target.get("form_label")
            or target.get("authored_by")
            or target_id[:8]
        )
        rationale = (
            str(relation.get("rationale") or "")
            if relation
            else f"Shared authored features: {', '.join(matched)}"
        )
        limitations = [
            "This is a suggested path, not an optimal or verified match.",
            "The target must independently choose whether to interact.",
        ]
        if intent_location or target_location:
            if not (same_locality or within_radius):
                limitations.append(
                    "The authored location data does not establish physical proximity."
                )
        else:
            limitations.append("No authored location evidence is available.")
        paths.append(
            {
                "id": f"coordination-path:{intent_id}:{target_id}",
                "target_event_id": target_id,
                "kind": kind,
                "label": label,
                "authored_by": target.get("authored_by"),
                "exact_text": target_text,
                "location_label": target_location,
                "distance_km": round(distance, 3) if distance is not None else None,
                "capabilities": target.get("capabilities", []),
                "constraints": target.get("constraints", []),
                "status": str((relation or {}).get("verdict") or "OPEN"),
                "binding": False,
                "proposed_by": "AI",
                "authorship_role": "AI",
                "equality_level_id": closure_level_id,
                "score": round(score, 6),
                "why": {
                    "relation_id": (relation or {}).get("candidate_relation_id"),
                    "relation_type": (relation or {}).get("relation_type"),
                    "rationale": rationale,
                    "admission_reason": (relation or {}).get("admission_reason"),
                    "verdict": str((relation or {}).get("verdict") or "OPEN"),
                    "score": (relation or {}).get("score", round(score, 6)),
                    "matched_features": matched,
                    "matched_terms": matched,
                    "source_event_id": intent_id,
                    "target_event_id": target_id,
                    "source_event_ids": [intent_id, target_id],
                    "source_occurrence_ids": _unique(
                        [
                            *intent.get("exact_source_ids", []),
                            *target.get("exact_source_ids", []),
                        ]
                    ),
                    "reverse_path": [target_id, intent_id],
                    "shared_equality_level_id": closure_level_id,
                    "limitations": limitations,
                    "global_truth_claimed": False,
                    "global_optimum_claimed": False,
                },
                "local_actions": ["DETAIL", "INTERACT", "MESSAGE", "DECLINE"],
                "collective_actions": ["DRAFT_AGREEMENT"],
                "truth_issued": False,
            }
        )
    paths.sort(key=lambda item: (-float(item["score"]), item["target_event_id"]))
    paths = paths[:12]

    proposals = [
        item
        for item in commitment_proposals
        if str(item.get("intent_event_id")) == intent_id
    ]
    active_proposal = None
    event_proposal_id = event.get("metadata", {}).get("commitment_proposal_id")
    for proposal in proposals:
        if (
            event_proposal_id == proposal.get("id")
            or str(event.get("id")) == str(proposal.get("proposal_event_id"))
            or (
                event.get("action_id") is not None
                and event.get("action_id") == proposal.get("action_id")
            )
        ):
            active_proposal = proposal
            break
    if active_proposal is None:
        target_proposals = [
            proposal
            for proposal in proposals
            if str(event.get("id"))
            in {str(item) for item in proposal.get("target_event_ids", [])}
        ]
        if target_proposals:
            active_proposal = max(
                target_proposals, key=lambda item: item.get("created_at", "")
            )
    if active_proposal is None and proposals:
        active_proposal = max(proposals, key=lambda item: item.get("created_at", ""))
    if active_proposal is not None:
        active_proposal = {
            **active_proposal,
            "consent_status": str(active_proposal.get("status") or "PROPOSED"),
        }

    actions = {str(item["id"]): item for item in living_actions}
    action = (
        actions.get(str(active_proposal.get("action_id")))
        if active_proposal
        else None
    )
    returns = [
        item
        for item in living_returns
        if action is not None and str(item.get("action_id")) == str(action["id"])
    ]
    latest_return = max(returns, key=lambda item: item.get("created_at", "")) if returns else None
    return_event = None
    latest_return_at = (
        str(latest_return.get("created_at") or "")
        if latest_return is not None
        else None
    )
    unanimous_acceptance_at = (
        active_proposal.get("unanimous_acceptance_at")
        if active_proposal is not None
        else None
    )
    return_follows_current_acceptance = bool(
        latest_return_at
        and unanimous_acceptance_at
        and latest_return_at >= str(unanimous_acceptance_at)
    )
    if latest_return is not None:
        return_event = event_by_occurrence.get(str(latest_return.get("occurrence_id")))
        if (
            active_proposal is not None
            and active_proposal.get("consent_status") == "ACCEPTED"
            and return_follows_current_acceptance
        ):
            active_proposal = {
                **active_proposal,
                "status_before_return": active_proposal.get("status"),
                "status": "RETURNED",
                "return_ids": [item["id"] for item in returns],
                "latest_return_at": latest_return_at,
                "return_follows_current_acceptance": True,
            }
        elif active_proposal is not None:
            active_proposal = {
                **active_proposal,
                "return_ids": [item["id"] for item in returns],
                "historical_return_present": True,
                "latest_return_at": latest_return_at,
                "return_follows_current_acceptance": False,
            }

    draft_path = paths[0] if paths else None
    draft_agreement = None
    if draft_path is not None:
        parties = _unique(
            [str(intent.get("authored_by") or "participant"), str(draft_path.get("authored_by") or "")]
        )
        draft_agreement = {
            "title": f"Coordinate: {draft_path['label']}",
            "purpose": intent_text,
            "target_event_ids": [draft_path["target_event_id"]],
            "required_participant_ids": parties,
            "resource_conditions": _unique(
                [
                    *intent.get("constraints", []),
                    *draft_path.get("constraints", []),
                ]
            ),
            "exact_terms": (
                f"We propose to coordinate on: {intent_text} "
                f"First path: {draft_path['label']}. Each participant must record "
                "their own decision; ordinary interaction remains open."
            ),
            "editable": True,
            "binding": False,
            "truth_issued": False,
        }

    status = str((active_proposal or {}).get("status") or "OPEN")
    consent_status = str(
        (active_proposal or {}).get("consent_status") or status
    )
    if (
        latest_return is not None
        and consent_status == "ACCEPTED"
        and return_follows_current_acceptance
    ):
        operator = "RETURN"
    elif consent_status == "ACCEPTED":
        operator = "ACT"
    elif consent_status == "PARTIAL":
        operator = "COMMIT"
    elif active_proposal is not None:
        operator = "AGREE"
    elif paths:
        operator = "DISCOVER"
    else:
        operator = "DISCOVER"

    humans_by_actor: dict[tuple[str, str], dict[str, Any]] = {}

    def add_human_contribution(
        actor_id: str,
        internal_actor_id: str,
        event_id: str,
        source_ids: list[str],
        contribution_type: str,
    ) -> None:
        actor = actor_id or "participant"
        internal_actor = internal_actor_id or actor
        contributor = humans_by_actor.setdefault(
            (actor, internal_actor),
            {
                "role": "HUMAN",
                "actor_id": actor,
                "internal_actor_ids": [],
                "contribution_types": [],
                "event_ids": [],
                "source_reverse_path": [],
                "can_bind_human_consent": True,
                "identity_verified": False,
            },
        )
        contributor["contribution_types"].append(contribution_type)
        contributor["internal_actor_ids"].append(internal_actor)
        contributor["event_ids"].append(event_id)
        contributor["source_reverse_path"].extend(reversed(source_ids))

    add_human_contribution(
        str(intent.get("authored_by") or "participant"),
        _internal_actor_id(intent),
        intent_id,
        [str(item) for item in intent.get("exact_source_ids", [])],
        "INTENT",
    )
    for proposal in ([active_proposal] if active_proposal is not None else []):
        for decision in proposal.get("decision_history", []):
            decision_event_id = str(decision.get("decision_event_id") or "")
            decision_event = events.get(decision_event_id, {})
            add_human_contribution(
                str(
                    decision.get("metadata", {}).get("authored_by")
                    or decision.get("participant_id")
                    or "participant"
                ),
                _internal_actor_id(decision_event),
                decision_event_id,
                [str(item) for item in decision_event.get("exact_source_ids", [])],
                "DECISION",
            )
    contributors: list[dict[str, Any]] = []
    for contributor in humans_by_actor.values():
        contributor["contribution_types"] = _unique(
            contributor["contribution_types"]
        )
        contributor["internal_actor_ids"] = _unique(
            contributor["internal_actor_ids"]
        )
        contributor["internal_actor_id"] = contributor["internal_actor_ids"][0]
        contributor["contribution"] = " + ".join(
            item.lower() for item in contributor["contribution_types"]
        )
        contributor["event_ids"] = _unique(contributor["event_ids"])
        contributor["source_reverse_path"] = _unique(
            contributor["source_reverse_path"]
        )
        contributors.append(contributor)
    contributors.append(
        {
            "role": "AI",
            "actor_id": "coordination-ai",
            "contribution": "explainable path translation and ordering",
            "event_ids": _unique(
                [
                    str(path["why"].get("relation_id") or path["id"])
                    for path in paths
                ]
            ),
            "source_reverse_path": _unique(
                [
                    occurrence_id
                    for path in paths
                    for occurrence_id in path["why"]["source_occurrence_ids"]
                ]
            ),
            "can_bind_human_consent": False,
            "truth_issued": False,
        }
    )
    if active_proposal is not None:
        contributors.append(
            {
                "role": "TOKEN",
                "actor_id": str(active_proposal.get("id") or "commitment-token"),
                "contribution": "non-transferable receipt of exact scoped terms and decisions",
                "event_ids": _unique(
                    [
                        str(active_proposal.get("proposal_event_id") or ""),
                        *[
                            str(item.get("decision_event_id") or "")
                            for item in active_proposal.get("decision_history", [])
                        ],
                    ]
                ),
                "source_reverse_path": _unique(
                    [
                        str(active_proposal.get("proposal_event_id") or ""),
                        intent_id,
                    ]
                ),
                "can_bind_human_consent": False,
                "transferable": False,
                "currency_issued": False,
            }
        )
    return_role: str | None = None
    if latest_return is not None:
        return_role = (
            _authorship_role(return_event)
            if return_event is not None
            else "LIVING_SYSTEM"
        )
        contributors.append(
            {
                "role": return_role,
                "role_label": return_role,
                "actor_id": (
                    _authored_handle(return_event)
                    if return_event is not None
                    else str(latest_return.get("authored_by") or "living-return")
                ),
                "internal_actor_id": str(
                    return_event.get("authored_by")
                    if return_event is not None
                    else latest_return.get("authored_by") or "living-return"
                ),
                "authored_by": (
                    _authored_handle(return_event)
                    if return_event is not None
                    else str(latest_return.get("authored_by") or "living-return")
                ),
                "contribution_type": "RETURN",
                "contribution": "returned consequence that reopens the field",
                "event_ids": _unique(
                    [str(return_event.get("id") if return_event else "")]
                ),
                "source_reverse_path": _unique(
                    [
                        str(latest_return.get("occurrence_id") or ""),
                        str(active_proposal.get("proposal_event_id") if active_proposal else ""),
                        *(
                            return_event.get("causal_predecessor_ids", [])
                            if return_event is not None
                            else []
                        ),
                        intent_id,
                    ]
                ),
                "can_bind_human_consent": False,
                "status": "OPEN",
            }
        )

    for contributor in contributors:
        contributor["equality_level_id"] = closure_level_id
        contributor["source_event_ids"] = list(contributor.get("event_ids", []))

    token_status = (
        "SATISFIED" if consent_status == "ACCEPTED" else "OPEN"
    )
    if consent_status in {"REJECTED", "WITHDRAWN"}:
        token_status = "REOPENED"
    freedom_actions = ["inspect", "message", "ask", "decline", "revise"]
    if consent_status == "ACCEPTED":
        enabled_forms = [
            "DISCOVER",
            "CONNECT",
            "AGREE",
            "COMMIT",
            "ACT",
            "RETURN",
        ]
    elif active_proposal is not None:
        enabled_forms = ["DISCOVER", "CONNECT", "AGREE", "COMMIT"]
    else:
        enabled_forms = ["DISCOVER", "CONNECT", "AGREE"]
    receipt = {
        "protocol": "closure.supernet/coordination-v2",
        "intent_event_id": intent_id,
        "optimization_scope": "visible source-preserved paths under the authored location and constraints",
        "global_optimum_claimed": False,
        "current_verdict": "OPEN",
        "intent": {
            "event_id": intent_id,
            "problem_id": (
                intent_problem.get("id")
                if intent_problem is not None
                else intent.get("problem_id")
            ),
            "exact_text": intent_text,
            "authored_by": intent.get("authored_by"),
            "perspective_id": intent.get("perspective_id"),
            "location_label": intent_location,
            "capabilities": intent.get("capabilities", []),
            "constraints": intent.get("constraints", []),
            "source_occurrence_ids": intent.get("exact_source_ids", []),
        },
        "paths": paths,
        "suggestions": paths,
        "path_count": len(paths),
        "draft_agreement": draft_agreement,
        "proposals": proposals,
        "active_proposal": active_proposal,
        "active_action": action,
        "living_return": (
            {
                "id": latest_return.get("id"),
                "event_id": return_event.get("id") if return_event else None,
                "occurrence_id": latest_return.get("occurrence_id"),
                "exact_text": (
                    _event_text(return_event, occurrences)
                    if return_event is not None
                    else ""
                ),
                "authored_by": (
                    _authored_handle(return_event)
                    if return_event is not None
                    else None
                ),
                "actor_id": (
                    _authored_handle(return_event)
                    if return_event is not None
                    else None
                ),
                "internal_actor_id": (
                    return_event.get("authored_by")
                    if return_event is not None
                    else None
                ),
                "authorship_role": return_role,
                "location_label": (
                    _location(return_event)[0]
                    if return_event is not None
                    else None
                ),
                "status": "OPEN",
                "source_reversible": True,
                "truth_issued": False,
            }
            if latest_return
            else None
        ),
        "mutual_authorship": {
            "contributors": contributors,
            "roles": [item["role"] for item in contributors],
            "canonical_author": None if len(contributors) > 1 else contributors[0]["role"],
            "all_sources_preserved": all(
                bool(item.get("source_reverse_path")) for item in contributors
            ),
            "one_equality_level_id": closure_level_id,
            "ai_may_suggest_but_not_bind": True,
            "token_may_record_conditions_but_not_consent": True,
            "equal_content_identifies_actors": False,
            "actor_identity_collapsed": False,
        },
        "natural_form_operator": {
            "natural_form": operator,
            "derived": True,
            "user_selected_phase": False,
            "local_open": freedom_actions,
            "global_transition": "DISCOVER→CONNECT→AGREE→COMMIT→ACT→RETURN",
            "token_gated_forms": ["ACT", "RETURN"],
            "enabled_forms": enabled_forms,
            "selector_version": str(
                (active_proposal or {}).get("unity_selector_version")
                or UNITY_SELECTOR_VERSION
            ),
            "selector_source": "versioned Supernet product policy",
            "unity_is_extra_data": True,
            "gates_interactions": False,
            "interactions_gated": False,
        },
        "token_gate": {
            "status": token_status,
            "gated_forms": ["ACT", "RETURN"],
            "gates_interactions": False,
            "interactions_gated": False,
            "non_transferable": True,
            "currency_issued": False,
            "human_worth_scored": False,
        },
        "local_global": {
            "local_event_id": str(event["id"]),
            "local_perspective_id": event.get("perspective_id"),
            "global_affected_perspectives": _unique(
                [
                    *intent.get("affected_perspectives", []),
                    *[
                        str(path.get("authored_by") or "") for path in paths
                    ],
                ]
            ),
            "interactions_continue_locally": True,
            "collective_transition_visible": True,
        },
        "source_lineage": {
            "intent_event_id": intent_id,
            "proposal_id": (
                active_proposal.get("id") if active_proposal is not None else None
            ),
            "proposal_event_id": (
                active_proposal.get("proposal_event_id")
                if active_proposal is not None
                else None
            ),
            "target_event_ids": (
                active_proposal.get("target_event_ids", [])
                if active_proposal is not None
                else []
            ),
            "decision_event_ids": (
                [
                    item.get("decision_event_id")
                    for item in active_proposal.get("decision_history", [])
                ]
                if active_proposal is not None
                else []
            ),
            "return_event_id": return_event.get("id") if return_event else None,
        },
        "security_enforcement": "OPEN",
        "identity_assurance": "DEVELOPMENT_ATTESTATION",
        "binding": False,
        "truth_issued": False,
        "two_person_E2E": "OPEN",
    }
    continuum_event_ids = _unique(
        [
            str(event.get("id") or ""),
            intent_id,
            *[str(path.get("target_event_id") or "") for path in paths],
            *(
                [
                    str(active_proposal.get("proposal_event_id") or ""),
                    *[
                        str(item)
                        for item in active_proposal.get("target_event_ids", [])
                    ],
                    *[
                        str(item.get("decision_event_id") or "")
                        for item in active_proposal.get("decision_history", [])
                    ],
                ]
                if active_proposal is not None
                else []
            ),
            str(return_event.get("id") if return_event is not None else ""),
        ]
    )
    continuum_field_events = [
        events[event_id]
        for event_id in continuum_event_ids
        if event_id in events
    ]
    continuum = build_continuum_receipt(
        local_event=event,
        intent=receipt["intent"],
        field_events=continuum_field_events,
        paths=paths,
        active_proposal=active_proposal,
        living_return=receipt["living_return"],
        operator=receipt["natural_form_operator"],
        enabled_forms=enabled_forms,
        freedom_actions=freedom_actions,
        closure_level_id=closure_level_id,
        contributors=contributors,
        token_status=receipt["token_gate"],
    )
    receipt["continuum"] = continuum
    receipt["nrrf837_continuum"] = continuum
    selected_form_id = str(continuum["selected_natural_form_id"])
    ranked_edges = {
        str(item.get("id")): item
        for item in continuum.get("suggestions", {}).get(
            "contextual_ranked_edges", []
        )
    }
    for path in paths:
        edge = ranked_edges.get(str(path.get("id")), {})
        shared_natural_form = bool(edge.get("shared_natural_form"))
        target_form_id = edge.get("target_natural_form_id") or edge.get(
            "natural_form_id"
        )
        path["natural_form_id"] = (
            str(target_form_id) if target_form_id else None
        )
        path["why"]["shared_natural_form_id"] = (
            str(edge.get("shared_natural_form_id") or target_form_id)
            if shared_natural_form
            else None
        )
        path["why"]["natural_form_equality"] = (
            "form(compose(intent)) = form(compose(target))"
            if shared_natural_form
            else "OPEN — contextual path; natural-form equality is not witnessed"
        )
        path["why"]["suggestion_equivalence"] = (
            "SAME_NATURAL_FORM" if shared_natural_form else "OPEN"
        )
        path["why"]["formal_suggestion_status"] = (
            "WITNESSED" if shared_natural_form else "OPEN"
        )
    authorship = continuum.get("authorship", {})
    contributor_records = authorship.get("contributor_records", [])
    for contributor, record in zip(contributors, contributor_records, strict=False):
        contributor["global_content_id"] = record.get("global_content_id")
        contributor["global_state_id"] = record.get("global_state_id")
        contributor["natural_form_id"] = record.get(
            "selected_natural_form_id"
        )
        contributor["equality_status"] = record.get("equality_status", "OPEN")
        contributor["equality_basis"] = record.get("equality_basis", "UNRESOLVED")
        contributor["unresolved_source_event_ids"] = record.get(
            "unresolved_source_event_ids", []
        )
    premise = authorship.get("mutual_authorship_redundancy_premise", {})
    witnessed_one_form = bool(
        premise.get("all_contributors_witnessed")
        and premise.get("same_witnessed_natural_form")
    )
    witnessed_one_global_reading = bool(
        premise.get("all_contributors_witnessed")
        and premise.get("same_witnessed_global_reading")
    )
    witnessed_form_ids = {
        str(record["selected_natural_form_id"])
        for record in contributor_records
        if record.get("selected_natural_form_id")
    }
    witnessed_global_ids = {
        str(record["global_content_id"])
        for record in contributor_records
        if record.get("global_content_id")
    }
    receipt["mutual_authorship"].update(
        {
            "one_natural_form_id": (
                next(iter(witnessed_form_ids))
                if witnessed_one_form and len(witnessed_form_ids) == 1
                else None
            ),
            "one_global_content_id": (
                next(iter(witnessed_global_ids))
                if witnessed_one_global_reading and len(witnessed_global_ids) == 1
                else None
            ),
            "natural_form_equality_status": (
                "WITNESSED" if witnessed_one_form else "OPEN"
            ),
            "global_reading_equality_status": (
                "WITNESSED" if witnessed_one_global_reading else "OPEN"
            ),
            "mutual_authorship_redundancy_applicable": authorship.get(
                "mutual_authorship_redundancy_applicable", False
            ),
            "redundancy_is_content_equality_only": True,
            "premise_injected": False,
        }
    )
    receipt["local_global"].update(
        {
            "local_closure_level_id": continuum.get("local_closure_level_id"),
            "global_content_id": continuum.get("global_content_id"),
            "global_state_id": continuum.get("global_state_id"),
            "selected_natural_form_id": selected_form_id,
        }
    )
    return receipt
