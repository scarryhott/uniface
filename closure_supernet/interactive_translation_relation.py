from __future__ import annotations

"""Primitive observer-observed interactive translation for arbitrary feedback.

The semantic primitive is a returned relative interaction, not equality between
preselected observations, features, horizons, strategies, or fixed returns.
Any source adapter may supply observed states and returned relations; the same
kernel derives translation fibres from those witnessed relations.
"""

import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS, partition_signature

PROTOCOL = "closure.supernet/observer-observed-interactive-translation-v2"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _source_ids(value: Mapping[str, Any]) -> list[str]:
    raw = value.get("source_return_ids") or value.get("source_ids") or value.get("exact_source_ids") or []
    if isinstance(raw, str):
        raw = [raw]
    return list(dict.fromkeys(str(item) for item in raw if item is not None and str(item)))


def _components(members: Sequence[str], pairs: Sequence[tuple[str, str]]) -> tuple[tuple[str, ...], ...]:
    parent = {member: member for member in members}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for left, right in pairs:
        if left in parent and right in parent:
            union(left, right)

    groups: dict[str, list[str]] = {}
    for member in members:
        groups.setdefault(find(member), []).append(member)
    return tuple(sorted((tuple(sorted(group)) for group in groups.values()), key=lambda group: group))


def derive_feedback_translation(*, observer_id: str | None, returned_feedback: Sequence[Mapping[str, Any]], returned_interactions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Derive relative fibres only from source-preserving returned interactions."""
    observer = str(observer_id or "")
    observations: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(returned_feedback):
        item = dict(raw)
        observed_id = str(item.get("observed_id") or item.get("state_id") or item.get("id") or f"observed-{index}")
        source_ids = _source_ids(item)
        payload = item.get("payload", item.get("observed", item.get("value", item)))
        observations[observed_id] = {
            "observed_id": observed_id,
            "observer_id": observer or None,
            "source_ids": source_ids,
            "source_preserved": bool(source_ids),
            "payload_digest": _digest("observed", payload),
            "payload": payload,
        }

    interactions: list[dict[str, Any]] = []
    witnessed_pairs: list[tuple[str, str]] = []
    for index, raw in enumerate(returned_interactions):
        item = dict(raw)
        source = str(item.get("observed_source_id") or item.get("source_state_id") or item.get("source") or "")
        target = str(item.get("observed_target_id") or item.get("target_state_id") or item.get("target") or "")
        relation_id = str(item.get("relation_id") or item.get("id") or f"interaction-{index}")
        source_ids = _source_ids(item)
        endpoints_preserved = bool(source in observations and target in observations and observations[source]["source_preserved"] and observations[target]["source_preserved"])
        return_witnessed = item.get("returned") is True or item.get("witnessed") is True or bool(source_ids)
        witnessed = bool(observer and endpoints_preserved and return_witnessed)
        if witnessed:
            witnessed_pairs.append((source, target))
        interactions.append({
            "id": relation_id,
            "observer_id": observer or None,
            "observed_source_id": source or None,
            "observed_target_id": target or None,
            "interaction_status": WITNESSED_STATUS if witnessed else OPEN_STATUS,
            "translation_relation_witnessed": witnessed,
            "source_return_ids": source_ids,
            "return_witness_id": _digest("translation-return", {"observer": observer, "source": source, "target": target, "relation": relation_id, "source_ids": source_ids}) if witnessed else None,
            "return_is_semantic_primitive": False,
            "return_is_interaction_witness": True,
            "fixed_return_required": False,
            "observation_equality_used_to_witness": False,
            "fixed_feature_used_to_witness": False,
            "fixed_horizon_required": False,
            "continuation_status": OPEN_STATUS,
        })

    members = sorted(observations)
    translation_partition = _components(members, witnessed_pairs)
    all_feedback_source_preserved = bool(members) and all(row["source_preserved"] for row in observations.values())
    body = {
        "protocol": PROTOCOL,
        "primitive": "OBSERVER_OBSERVED_INTERACTIVE_TRANSLATION",
        "observer_id": observer or None,
        "observed_ids": members,
        "observations": [observations[member] for member in members],
        "interactions": interactions,
        "translation_partition": [list(group) for group in translation_partition],
        "translation_reading_total": bool(observer and all_feedback_source_preserved),
        "observer_observed_relation_is_primitive": True,
        "observation_equality_is_primitive": False,
        "chart_equivalence_is_primitive": False,
        "feature_selection_is_semantic": False,
        "horizon_selection_is_semantic": False,
        "strategy_selection_is_semantic": False,
        "return_is_primitive": False,
        "fixed_return_required": False,
        "continuation_status": OPEN_STATUS,
        "existence_closed": False,
    }
    body["id"] = _digest("feedback-translation", body)
    return body


def derive_relative_interactions(*, observer_id: str | None, projection_reading: Mapping[str, Any], form_by_member: Mapping[str, str], visual_nodes: Sequence[Mapping[str, Any]], visual_edges: Sequence[Mapping[str, Any]], truth_members: Iterable[str], physical_sensor_attached: bool = False) -> dict[str, Any]:
    """Adapt the current source-return visual contract into the generic kernel.

    The visual surface already returns a fibre reading.  The adapter translates
    only edges inside that returned fibre into returned relations; raw visual
    adjacency remains a proposal and cannot author equality.
    """
    observer = str(observer_id or "")
    members = set(map(str, truth_members))
    reading = {str(k): v for k, v in projection_reading.items()}
    event_to_state: dict[str, str] = {}
    feedback: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    for raw in visual_nodes:
        node = dict(raw)
        event_id = str(node.get("id") or "")
        state_id = str(node.get("occurrence_id") or event_id)
        if not event_id or state_id not in members or state_id not in reading:
            continue
        event_to_state[event_id] = state_id
        feedback.append({"observed_id": state_id, "source_ids": [state_id], "payload": {"relative_reading": reading[state_id], "physical_world_return": bool(physical_sensor_attached)}})
        nodes.append({"event_id": event_id, "state_id": state_id, "observer_id": observer or None, "observed_id": state_id, "relative_reading": reading[state_id], "source_preserved": True, "physical_world_return": bool(physical_sensor_attached)})

    returns: list[dict[str, Any]] = []
    open_visual_edges: list[str] = []
    for raw in visual_edges:
        edge = dict(raw)
        source_state = event_to_state.get(str(edge.get("source") or ""))
        target_state = event_to_state.get(str(edge.get("target") or ""))
        if not source_state or not target_state:
            continue
        relation_id = str(edge.get("id") or _digest("interaction", edge))
        source_return_fibre_witnessed = reading.get(source_state) == reading.get(target_state)
        if not source_return_fibre_witnessed:
            open_visual_edges.append(relation_id)
            continue
        returns.append({"id": relation_id, "source": source_state, "target": target_state, "source_ids": [source_state, target_state], "returned": True, "source_return_fibre_witnessed": True})

    generic = derive_feedback_translation(observer_id=observer, returned_feedback=feedback, returned_interactions=returns)
    natural_form_partition = partition_signature({member: form_by_member[member] for member in sorted(members) if member in form_by_member})
    translation_partition = tuple(tuple(group) for group in generic["translation_partition"])
    total = bool(generic["translation_reading_total"] and members and set(reading) == members and set(form_by_member) == members)
    closure_equations_derived = bool(total and translation_partition == natural_form_partition)

    interactions: list[dict[str, Any]] = []
    for row in generic["interactions"]:
        source = str(row.get("observed_source_id") or "")
        target = str(row.get("observed_target_id") or "")
        natural_form_equal = form_by_member.get(source) == form_by_member.get(target)
        interactions.append({**row, "relative_reading_equal": reading.get(source) == reading.get(target), "natural_form_equal_after_translation": natural_form_equal, "closure_preserved_after_translation": bool(row["translation_relation_witnessed"] and natural_form_equal)})

    body = {
        **generic,
        "nodes": nodes,
        "truth_member_ids": sorted(members),
        "interactions": interactions,
        "open_visual_edge_ids": open_visual_edges,
        "natural_form_partition": [list(group) for group in natural_form_partition],
        "translation_reading_total": total,
        "closure_equations_derived": closure_equations_derived,
        "projection_reading_is_semantic_authority": False,
        "display_labels_define_translation_fibres": False,
        "raw_visual_adjacency_authors_truth": False,
    }
    body["id"] = _digest("interactive-translation", body)
    return body


def translation_equivalence(interactions: Mapping[str, Any]) -> bool:
    return bool(interactions.get("closure_equations_derived") is True)


__all__ = ["PROTOCOL", "derive_feedback_translation", "derive_relative_interactions", "translation_equivalence"]
