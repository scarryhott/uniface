from __future__ import annotations

import hashlib
import json
from itertools import combinations
from typing import Any, Iterable


PROTOCOL = "closure.supernet/nrrf837-continuum-v1"
FORMAL_SOURCE = "NRRF837SupernetSocioeconomicSuperBrainInterfaceMonoidModalityEquality.lean"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(prefix: str, value: Any) -> str:
    encoded = _stable(value).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(encoded).hexdigest()[:24]}"


def _unique(values: Iterable[Any]) -> list[str]:
    return list(
        dict.fromkeys(
            str(value)
            for value in values
            if value is not None and str(value)
        )
    )


def _event_order(event: dict[str, Any] | None, occurrence_id: str) -> tuple[Any, ...]:
    if event is None:
        return (1, 2**63 - 1, "", occurrence_id)
    try:
        seq = int(event.get("seq") or 0)
    except (TypeError, ValueError):
        seq = 0
    return (
        0,
        seq,
        str(event.get("created_at") or ""),
        str(event.get("id") or occurrence_id),
    )


def _event_indexes(
    field_events: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    events_by_id = {str(event["id"]): event for event in field_events}
    event_by_occurrence: dict[str, dict[str, Any]] = {}
    for event in sorted(
        field_events,
        key=lambda item: _event_order(item, str(item.get("id") or "")),
    ):
        for occurrence_id in event.get("exact_source_ids", []):
            event_by_occurrence.setdefault(str(occurrence_id), event)
    return events_by_id, event_by_occurrence


def _occurrence_indexes(
    field_occurrences: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    return {str(item["id"]): item for item in field_occurrences}


def _natural_form_rows(closure_level: dict[str, Any]) -> list[dict[str, Any]]:
    raw = closure_level.get("truth_closes_level_alone", {}).get(
        "natural_forms", []
    )
    rows: list[dict[str, Any]] = []
    for index, form in enumerate(raw):
        members = sorted(_unique(form.get("members", [])))
        if not members:
            continue
        rows.append(
            {
                "index": index,
                "label": str(form.get("natural_form") or f"L/{index}"),
                "members": members,
                "representative_is_not_privileged": bool(
                    form.get("representative_is_not_privileged", True)
                ),
            }
        )
    return rows


def _unity_declaration(event: dict[str, Any] | None) -> bool:
    if event is None:
        return False
    metadata = event.get("metadata", {})
    return any(
        metadata.get(key) is True
        for key in (
            "nrrf837_unity",
            "natural_form_selected",
            "unity_selected",
        )
    )


def _select_unity_member(
    members: list[str],
    event_by_occurrence: dict[str, dict[str, Any]],
) -> tuple[str, str, list[str]]:
    declared = [
        occurrence_id
        for occurrence_id in members
        if _unity_declaration(event_by_occurrence.get(occurrence_id))
    ]
    if len(declared) == 1:
        return declared[0], "DECLARED_PRODUCT_DATA", []
    conflict = sorted(declared) if len(declared) > 1 else []
    selected = min(
        members,
        key=lambda occurrence_id: _event_order(
            event_by_occurrence.get(occurrence_id), occurrence_id
        ),
    )
    origin = (
        "DECLARATION_CONFLICT_DETERMINISTIC_FALLBACK"
        if conflict
        else "SOURCE_PRESERVING_PRODUCT_DEFAULT"
    )
    return selected, origin, conflict


def _finite_equivalence_audit(
    local_ids: list[str], compose: dict[str, str]
) -> dict[str, bool]:
    related = {
        (left, right): compose.get(left) == compose.get(right)
        for left in local_ids
        for right in local_ids
    }
    reflexive = all(related[(item, item)] for item in local_ids)
    symmetric = all(
        related[(left, right)] == related[(right, left)]
        for left in local_ids
        for right in local_ids
    )
    transitive = all(
        not (related[(left, middle)] and related[(middle, right)])
        or related[(left, right)]
        for left in local_ids
        for middle in local_ids
        for right in local_ids
    )
    return {
        "reflexive": reflexive,
        "symmetric": symmetric,
        "transitive": transitive,
    }


def _event_occurrence_ids(
    event_id: str,
    events_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    event = events_by_id.get(str(event_id))
    if event is None:
        return []
    return _unique(event.get("exact_source_ids", []))


def _references_to_occurrences(
    references: Iterable[Any],
    *,
    events_by_id: dict[str, dict[str, Any]],
    known_occurrences: set[str],
) -> list[str]:
    result: list[str] = []
    for raw in references:
        reference = str(raw or "")
        if not reference:
            continue
        if reference in known_occurrences:
            result.append(reference)
        result.extend(_event_occurrence_ids(reference, events_by_id))
    return _unique(result)


def _global_ids_for_event(
    event_id: str,
    *,
    events_by_id: dict[str, dict[str, Any]],
    compose: dict[str, str],
) -> list[str]:
    return _unique(
        compose[occurrence_id]
        for occurrence_id in _event_occurrence_ids(event_id, events_by_id)
        if occurrence_id in compose
    )


def _annotate_paths(
    coordination: dict[str, Any],
    *,
    events_by_id: dict[str, dict[str, Any]],
    compose: dict[str, str],
    global_by_id: dict[str, dict[str, Any]],
    modality: dict[str, str],
) -> dict[str, Any]:
    intent_event_id = str(
        coordination.get("intent", {}).get("event_id")
        or coordination.get("intent_event_id")
        or ""
    )
    intent_occurrence_ids = _event_occurrence_ids(intent_event_id, events_by_id)
    intent_globals = _unique(
        compose[item] for item in intent_occurrence_ids if item in compose
    )
    natural_form_paths: list[str] = []
    open_candidate_paths: list[str] = []

    paths = coordination.get("paths") or coordination.get("suggestions") or []
    for path in paths:
        target_event_id = str(
            path.get("target_event_id") or path.get("event_id") or ""
        )
        target_occurrence_ids = _event_occurrence_ids(target_event_id, events_by_id)
        target_globals = _unique(
            compose[item] for item in target_occurrence_ids if item in compose
        )
        shared = sorted(set(intent_globals) & set(target_globals))
        shared_labels = [
            str(global_by_id[item]["natural_form_label"])
            for item in shared
            if item in global_by_id
        ]
        relation = "SAME_NATURAL_FORM" if shared else "OPEN_AI_CANDIDATE"
        path_id = str(path.get("id") or target_event_id)
        if shared:
            natural_form_paths.append(path_id)
        else:
            open_candidate_paths.append(path_id)
        path["natural_form_suggestion"] = bool(shared)
        path["shared_global_state_ids"] = shared
        path["shared_natural_form_labels"] = shared_labels
        why = path.setdefault("why", {})
        if not isinstance(why, dict):
            why = {"rationale": str(why)}
            path["why"] = why
        why["nrrf837"] = {
            "suggestion_relation": relation,
            "equivalence_admitted": bool(shared),
            "intent_global_state_ids": intent_globals,
            "target_global_state_ids": target_globals,
            "shared_global_state_ids": shared,
            "shared_natural_form_labels": shared_labels,
            "intent_modality_local_ids": _unique(
                modality[item] for item in intent_occurrence_ids if item in modality
            ),
            "target_modality_local_ids": _unique(
                modality[item] for item in target_occurrence_ids if item in modality
            ),
            "explanation": (
                "The local intent and target compose to the same active global state; "
                "the displayed suggestion is their shared selected natural form."
                if shared
                else "AI surfaced this as an OPEN candidate, but the active equality "
                "level does not yet place the two local presentations in one natural form."
            ),
            "global_truth_claimed": False,
        }

    return {
        "relation": "local presentations are suggested by natural-form equality",
        "intent_event_id": intent_event_id,
        "intent_global_state_ids": intent_globals,
        "natural_form_path_ids": natural_form_paths,
        "open_ai_candidate_path_ids": open_candidate_paths,
        "equivalence_only_for_natural_form_paths": True,
        "ai_candidates_not_silently_promoted": True,
    }


def _annotate_authorship(
    coordination: dict[str, Any],
    *,
    events_by_id: dict[str, dict[str, Any]],
    compose: dict[str, str],
    modality: dict[str, str],
    unity: set[str],
) -> dict[str, Any]:
    mutual = coordination.setdefault("mutual_authorship", {})
    contributors = mutual.get("contributors", [])
    known_occurrences = set(compose)
    normalized: list[dict[str, Any]] = []

    for index, contributor in enumerate(contributors):
        references = [
            *contributor.get("event_ids", []),
            *contributor.get("source_event_ids", []),
            *contributor.get("source_reverse_path", []),
        ]
        local_ids = _references_to_occurrences(
            references,
            events_by_id=events_by_id,
            known_occurrences=known_occurrences,
        )
        global_ids = _unique(compose[item] for item in local_ids if item in compose)
        canonical_ids = _unique(
            modality[item] for item in local_ids if item in modality
        )
        is_natural = bool(local_ids) and all(item in unity for item in local_ids)
        contributor["nrrf837"] = {
            "local_presentation_ids": local_ids,
            "global_state_ids": global_ids,
            "modality_local_ids": canonical_ids,
            "authorship_is_natural_form": is_natural,
            "same_global_reading_alone_implies_identity": False,
        }
        normalized.append(
            {
                "index": index,
                "role": str(contributor.get("role") or f"CONTRIBUTOR_{index}"),
                "local_ids": local_ids,
                "global_ids": global_ids,
                "canonical_ids": canonical_ids,
                "is_natural": is_natural,
            }
        )

    redundant_pairs: list[dict[str, Any]] = []
    same_global_noncanonical_pairs: list[dict[str, Any]] = []
    distinct_global_pairs: list[dict[str, Any]] = []
    for left, right in combinations(normalized, 2):
        shared_globals = sorted(set(left["global_ids"]) & set(right["global_ids"]))
        pair = {
            "left_index": left["index"],
            "right_index": right["index"],
            "left_role": left["role"],
            "right_role": right["role"],
            "shared_global_state_ids": shared_globals,
        }
        if not shared_globals:
            distinct_global_pairs.append(pair)
            continue
        if left["is_natural"] and right["is_natural"]:
            pair["identity_admitted"] = True
            pair["reason"] = (
                "Both authorships are selected natural forms with the same global reading."
            )
            redundant_pairs.append(pair)
        else:
            pair["identity_admitted"] = False
            pair["reason"] = (
                "The global reading agrees, but at least one authorship is not a fixed "
                "natural form; the converse is not assumed."
            )
            same_global_noncanonical_pairs.append(pair)

    classes: dict[str, dict[str, Any]] = {}
    for item in normalized:
        for global_id in item["global_ids"]:
            entry = classes.setdefault(
                global_id,
                {
                    "global_state_id": global_id,
                    "contributor_indices": [],
                    "roles": [],
                    "canonical_local_ids": [],
                },
            )
            entry["contributor_indices"].append(item["index"])
            entry["roles"].append(item["role"])
            entry["canonical_local_ids"].extend(item["canonical_ids"])
    class_rows = []
    for entry in classes.values():
        entry["contributor_indices"] = sorted(set(entry["contributor_indices"]))
        entry["roles"] = _unique(entry["roles"])
        entry["canonical_local_ids"] = _unique(entry["canonical_local_ids"])
        class_rows.append(entry)
    class_rows.sort(key=lambda item: item["global_state_id"])

    result = {
        "raw_roles_remain_distinguishable": True,
        "canonicalized_authorship_classes": class_rows,
        "redundant_natural_form_pairs": redundant_pairs,
        "same_global_noncanonical_pairs": same_global_noncanonical_pairs,
        "distinct_global_pairs": distinct_global_pairs,
        "mutual_authorship_redundant_rule": (
            "same global reading implies literal authorship identity only when both "
            "authorship presentations are fixed natural forms"
        ),
        "converse_without_natural_form_rejected": True,
        "economic_credit_computed": False,
        "human_ai_living_roles_collapsed": False,
    }
    mutual["nrrf837"] = result
    return result


def _gate_factorization(coordination: dict[str, Any]) -> dict[str, Any]:
    operator = coordination.get("natural_form_operator", {})
    token_gate = coordination.get("token_gate", {})
    paths = coordination.get("paths") or coordination.get("suggestions") or []
    path_ids = _unique(
        path.get("id") or path.get("target_event_id") or path.get("event_id")
        for path in paths
    )
    enabled_forms = _unique(operator.get("enabled_forms", []))
    if not enabled_forms:
        enabled_forms = ["DISCOVER", "CONNECT", "AGREE", "COMMIT"]
    product_pair_count = len(path_ids) * len(enabled_forms)

    active = coordination.get("active_proposal") or {}
    correlated: list[dict[str, Any]] = []
    for target_event_id in active.get("target_event_ids", []):
        correlated.append(
            {
                "kind": "TARGET_SPECIFIC_COMMITMENT",
                "form": "ACT",
                "interaction_event_id": str(target_event_id),
            }
        )
    for participant_id in active.get("required_participant_ids", []):
        correlated.append(
            {
                "kind": "PARTICIPANT_SPECIFIC_CONSENT",
                "form": "COMMIT",
                "participant_id": str(participant_id),
            }
        )
    for condition in active.get("resource_conditions", []):
        correlated.append(
            {
                "kind": "SCOPED_RESOURCE_CONDITION",
                "form": "ACT",
                "condition": str(condition),
            }
        )

    relational_required = bool(correlated)
    result = {
        "ai_coordinate": {
            "name": "INTERACTION_ADMISSION_TO_ACTIVE_FORM",
            "admitted_path_ids": path_ids,
            "gates_ordinary_communication": False,
            "can_bind_human_consent": False,
        },
        "token_coordinate": {
            "name": "FORM_AVAILABILITY_POST_SETTLEMENT",
            "enabled_forms": enabled_forms,
            "gated_forms": _unique(token_gate.get("gated_forms", [])),
            "gates_ordinary_communication": False,
            "currency_issued": bool(token_gate.get("currency_issued", False)),
        },
        "independent_joint_gate": {
            "shape": "PRODUCT",
            "interaction_count": len(path_ids),
            "form_count": len(enabled_forms),
            "admitted_pair_count": product_pair_count,
            "joint_gate_iff_product": True,
            "each_gate_blind_to_other_coordinate": True,
        },
        "correlated_constraints": correlated,
        "non_product_gate_not_realisable_by_independent_pair": relational_required,
        "relational_policy_layer_required": relational_required,
        "relational_policy_layer_present": bool(active) if relational_required else True,
        "relational_policy_layer": (
            "commitment proposal + participant-specific decisions + scoped action conditions"
            if relational_required
            else "not required by the current open state"
        ),
        "ordinary_interaction_remains_open": True,
    }
    coordination["ai_gate"] = result["ai_coordinate"]
    coordination["gate_factorization"] = result
    token_gate["nrrf837_coordinate"] = "FORM"
    token_gate["independent_of_ordinary_interaction_permission"] = True
    return result


def _agreement_modality(
    coordination: dict[str, Any],
    *,
    events_by_id: dict[str, dict[str, Any]],
    compose: dict[str, str],
) -> dict[str, Any]:
    active = coordination.get("active_proposal") or {}
    intent_event_id = str(
        coordination.get("intent", {}).get("event_id")
        or coordination.get("intent_event_id")
        or ""
    )
    target_event_ids = _unique(active.get("target_event_ids", []))
    if not target_event_ids:
        draft = coordination.get("draft_agreement") or {}
        target_event_ids = _unique(draft.get("target_event_ids", []))
    input_event_ids = _unique([intent_event_id, *target_event_ids])
    input_global_ids = _unique(
        global_id
        for event_id in input_event_ids
        for global_id in _global_ids_for_event(
            event_id,
            events_by_id=events_by_id,
            compose=compose,
        )
    )
    proposal_event_id = str(active.get("proposal_event_id") or "") or None
    status = str(active.get("status") or "OPEN")
    joint_content_id = (
        _digest(
            "joint-content",
            {
                "input_global_state_ids": sorted(input_global_ids),
                "terms": active.get("exact_terms") or active.get("title") or "",
            },
        )
        if input_event_ids
        else None
    )
    result = {
        "operation": "M(t * n)",
        "input_event_ids": input_event_ids,
        "input_global_state_ids": input_global_ids,
        "joint_global_content_id": joint_content_id,
        "selected_agreement_event_id": proposal_event_id,
        "displayable": bool(proposal_event_id or coordination.get("draft_agreement")),
        "unique_under_declared_unity": bool(proposal_event_id),
        "status": status,
        "settled_for_action": status in {"ACCEPTED", "RETURNED"},
        "post_settlement_freedom_range": _unique(
            coordination.get("natural_form_operator", {}).get("local_open", [])
        ),
        "ordinary_interaction_restricted": False,
        "runtime_scope": (
            "The receipt identifies the product witness; the Lean theorem supplies "
            "the abstract uniqueness law under the declared Continuum assumptions."
        ),
    }
    coordination["agreement_modality"] = result
    return result


def derive_continuum_receipt(
    *,
    event: dict[str, Any],
    field_events: list[dict[str, Any]],
    field_occurrences: list[dict[str, Any]],
    relation_receipts: list[dict[str, Any]],
    closure_level: dict[str, Any],
    coordination: dict[str, Any],
) -> dict[str, Any]:
    """Project one live finite Supernet field through the NRRF837 contract.

    This function does not re-prove the Lean theorems and does not infer a
    value system. It makes the active finite `compose`, declared `unity`,
    `form`, and `modality = form ∘ compose` tables inspectable and audits the
    consequences that can be checked directly on that finite receipt.
    """

    events_by_id, event_by_occurrence = _event_indexes(field_events)
    occurrences_by_id = _occurrence_indexes(field_occurrences)
    form_rows = _natural_form_rows(closure_level)

    compose: dict[str, str] = {}
    form: dict[str, str] = {}
    modality: dict[str, str] = {}
    global_states: list[dict[str, Any]] = []
    local_presentations: list[dict[str, Any]] = []
    unity_conflicts: list[dict[str, Any]] = []

    for row in form_rows:
        global_id = _digest(
            "global",
            {
                "level_id": closure_level.get("level_id"),
                "members": row["members"],
            },
        )
        selected, origin, conflict = _select_unity_member(
            row["members"], event_by_occurrence
        )
        form[global_id] = selected
        if conflict:
            unity_conflicts.append(
                {
                    "global_state_id": global_id,
                    "declared_local_ids": conflict,
                    "selected_fallback_local_id": selected,
                }
            )
        global_states.append(
            {
                "global_state_id": global_id,
                "natural_form_label": row["label"],
                "freedom_range_local_ids": list(row["members"]),
                "freedom_range_size": len(row["members"]),
                "selected_natural_form_local_id": selected,
                "selected_natural_form_event_id": (
                    event_by_occurrence.get(selected, {}).get("id")
                ),
                "unity_selection_origin": origin,
                "representative_was_extra_product_data": True,
                "underlying_quotient_privileged_no_representative": bool(
                    row["representative_is_not_privileged"]
                ),
            }
        )
        for local_id in row["members"]:
            compose[local_id] = global_id
            modality[local_id] = selected

    unity = set(form.values())
    for local_id in sorted(compose):
        owner = event_by_occurrence.get(local_id)
        occurrence = occurrences_by_id.get(local_id, {})
        local_presentations.append(
            {
                "local_id": local_id,
                "event_id": owner.get("id") if owner else None,
                "authored_by": owner.get("authored_by") if owner else None,
                "exact_text": occurrence.get("exact_text"),
                "global_state_id": compose[local_id],
                "modality_local_id": modality[local_id],
                "is_natural_form": local_id in unity,
                "current_stage": owner.get("current_stage") if owner else None,
            }
        )

    local_ids = sorted(compose)
    fixed_points = {item for item in local_ids if modality.get(item) == item}
    idempotent = all(
        modality.get(modality[item]) == modality[item] for item in local_ids
    )
    modality_eq_iff_global_eq = all(
        (modality[left] == modality[right])
        == (compose[left] == compose[right])
        for left in local_ids
        for right in local_ids
    )
    freedom_nonempty = all(item["freedom_range_size"] > 0 for item in global_states)
    unity_once = all(
        len(set(item["freedom_range_local_ids"]) & unity) == 1
        for item in global_states
    )
    global_form_bijection = (
        len(global_states) == len(unity) == len(set(form.values()))
    )
    equivalence = _finite_equivalence_audit(local_ids, compose)

    executable_audits = {
        "modality_idempotent": idempotent,
        "fixed_points_exactly_unity": fixed_points == unity,
        "modality_equality_iff_global_equality": modality_eq_iff_global_eq,
        "freedom_ranges_nonempty": freedom_nonempty,
        "unity_intersects_each_freedom_range_once": unity_once,
        "natural_forms_biject_global_states": global_form_bijection,
        "suggestion_relation_reflexive": equivalence["reflexive"],
        "suggestion_relation_symmetric": equivalence["symmetric"],
        "suggestion_relation_transitive": equivalence["transitive"],
        "unity_declaration_conflict_free": not unity_conflicts,
    }
    all_active_finite_audits_pass = bool(global_states) and all(
        executable_audits.values()
    )

    global_by_id = {
        str(item["global_state_id"]): item for item in global_states
    }
    suggestion = _annotate_paths(
        coordination,
        events_by_id=events_by_id,
        compose=compose,
        global_by_id=global_by_id,
        modality=modality,
    )
    authorship = _annotate_authorship(
        coordination,
        events_by_id=events_by_id,
        compose=compose,
        modality=modality,
        unity=unity,
    )
    gates = _gate_factorization(coordination)
    agreement = _agreement_modality(
        coordination,
        events_by_id=events_by_id,
        compose=compose,
    )

    active_occurrence_ids = _unique(event.get("exact_source_ids", []))
    active_local_id = next(
        (item for item in active_occurrence_ids if item in compose), None
    )
    active_global_id = compose.get(active_local_id) if active_local_id else None
    active_global = global_by_id.get(str(active_global_id)) if active_global_id else None

    continuum_id = _digest(
        "continuum",
        {
            "level_id": closure_level.get("level_id"),
            "compose": compose,
            "form": form,
            "unity_policy": [
                (
                    item["global_state_id"],
                    item["selected_natural_form_local_id"],
                    item["unity_selection_origin"],
                )
                for item in global_states
            ],
        },
    )

    return {
        "protocol": PROTOCOL,
        "formal_source": FORMAL_SOURCE,
        "continuum_id": continuum_id,
        "runtime_scope": "finite active equality-level projection of the live Supernet field",
        "structure": {
            "local_monoid": {
                "name": "L",
                "carrier": "source-preserved local interaction presentations",
                "active_generator_ids": local_ids,
                "composition": "append/source-lineage composition",
            },
            "global_monoid": {
                "name": "G",
                "carrier": "collective natural-form equality states",
                "active_state_ids": [
                    item["global_state_id"] for item in global_states
                ],
                "composition": "global content composition inherited through compose",
            },
            "compose": {
                "type": "L →* G",
                "active_generator_map": compose,
            },
            "unity": {
                "selected_local_ids": sorted(unity),
                "extra_product_data": True,
                "policy": (
                    "one explicit nrrf837_unity declaration per freedom range; otherwise "
                    "the earliest source-preserved event is the deterministic product default"
                ),
                "declaration_conflicts": unity_conflicts,
            },
            "form": {
                "type": "G → L",
                "active_map": form,
            },
            "modality": {
                "definition": "form ∘ compose",
                "active_map": modality,
            },
        },
        "local_presentations": local_presentations,
        "global_states": global_states,
        "active_form": {
            "source_event_id": str(event.get("id") or ""),
            "local_id": active_local_id,
            "global_state_id": active_global_id,
            "natural_form_label": (
                active_global.get("natural_form_label") if active_global else None
            ),
            "selected_natural_form_local_id": (
                active_global.get("selected_natural_form_local_id")
                if active_global
                else None
            ),
            "selected_natural_form_event_id": (
                active_global.get("selected_natural_form_event_id")
                if active_global
                else None
            ),
            "freedom_range_local_ids": (
                active_global.get("freedom_range_local_ids", [])
                if active_global
                else []
            ),
            "freedom_range_size": (
                active_global.get("freedom_range_size", 0)
                if active_global
                else 0
            ),
            "fixed_by_modality": bool(active_local_id in unity),
        },
        "audits": {
            **executable_audits,
            "all_active_finite_audits_pass": all_active_finite_audits_pass,
            "non_vacuous_multi_point_freedom_range": any(
                item["freedom_range_size"] > 1 for item in global_states
            ),
            "monoid_congruence": {
                "status": "FORMAL_THEOREM",
                "runtime_check": "generator equality projection only",
            },
            "modality_multiplicative_up_to_itself": {
                "status": "FORMAL_THEOREM",
                "runtime_check": "not re-proved from event JSON",
            },
            "selector_unique_once_unity_fixed": {
                "status": "FORMAL_THEOREM",
                "runtime_witness": not unity_conflicts,
            },
        },
        "suggestion_relation": suggestion,
        "authorship": authorship,
        "gates": gates,
        "agreement_modality": agreement,
        "formal_scope": {
            "lean_theorems_reproved_by_runtime": False,
            "runtime_tables_audited": True,
            "unity_is_extra_product_data": True,
            "economic_or_value_claim_made": False,
            "historical_novelty_claim_made": False,
            "physical_truth_claim_made": False,
            "truth_issued": False,
        },
        "relation_receipt_count": len(relation_receipts),
        "truth_issued": False,
    }


def attach_continuum_to_visual_receipt(
    receipt: dict[str, Any],
    *,
    event: dict[str, Any],
    field_events: list[dict[str, Any]],
    field_occurrences: list[dict[str, Any]],
    relation_receipts: list[dict[str, Any]],
    closure_level: dict[str, Any],
) -> dict[str, Any]:
    """Attach NRRF837 to the existing visual receipt without a second runtime."""

    coordination = receipt.setdefault("coordination", {})
    continuum = derive_continuum_receipt(
        event=event,
        field_events=field_events,
        field_occurrences=field_occurrences,
        relation_receipts=relation_receipts,
        closure_level=closure_level,
        coordination=coordination,
    )
    coordination["continuum"] = continuum
    receipt["nrrf837_continuum"] = {
        "protocol": continuum["protocol"],
        "continuum_id": continuum["continuum_id"],
        "active_form": continuum["active_form"],
        "audits": continuum["audits"],
        "full_receipt_path": "coordination.continuum",
        "truth_issued": False,
    }
    receipt.setdefault("formal_runtime_contracts", []).append("NRRF837")
    receipt["formal_runtime_contracts"] = _unique(
        receipt["formal_runtime_contracts"]
    )
    operational = receipt.setdefault("operational_closure", {})
    operational["nrrf837_continuum_derived"] = True
    operational["nrrf837_active_finite_audits_pass"] = continuum["audits"][
        "all_active_finite_audits_pass"
    ]
    receipt["truth_issued"] = False
    return receipt
