from __future__ import annotations

"""Primitive observer-observed interaction semantics for Supernet closure.

Closure is not equality between detached observations and is not a fixed return.
The primitive object is a relative interaction:

    observer + observed + admissible interaction -> translation witness

A return is only a source-preserving witness carried by that interaction.  The
translation fibres induced by witnessed interactions are then compared with the
natural-form fibres.  Chart/UI equality is therefore derived after interaction,
not used to define interaction itself.
"""

import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS, partition_signature, unique_strings

PROTOCOL = "closure.supernet/observer-observed-interactive-translation-v1"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def derive_relative_interactions(
    *,
    observer_id: str | None,
    projection_reading: Mapping[str, Any],
    form_by_member: Mapping[str, str],
    visual_nodes: Sequence[Mapping[str, Any]],
    visual_edges: Sequence[Mapping[str, Any]],
    truth_members: Iterable[str],
    physical_sensor_attached: bool = False,
) -> dict[str, Any]:
    """Derive translation witnesses from observer-observed relations first.

    The observer is the returned perspective.  The observed are source states.
    An edge is an admissible interaction proposal.  It becomes a witnessed
    translation only when both endpoint source states are preserved and the
    observer reads them in one relative fibre.  Natural-form agreement is not
    consulted when deciding whether the interaction itself exists; it is tested
    afterward as a derived closure consequence.
    """

    observer = str(observer_id or "")
    members = set(map(str, truth_members))
    reading = {str(k): v for k, v in projection_reading.items()}

    event_to_state: dict[str, str] = {}
    nodes: list[dict[str, Any]] = []
    for raw in visual_nodes:
        node = dict(raw)
        event_id = str(node.get("id") or "")
        state_id = str(node.get("occurrence_id") or event_id)
        if not event_id or state_id not in members or state_id not in reading:
            continue
        event_to_state[event_id] = state_id
        nodes.append(
            {
                "event_id": event_id,
                "state_id": state_id,
                "observer_id": observer or None,
                "observed_id": state_id,
                "relative_reading": reading[state_id],
                "source_preserved": True,
                "physical_world_return": bool(physical_sensor_attached),
            }
        )

    interactions: list[dict[str, Any]] = []
    witnessed_pairs: list[tuple[str, str]] = []
    for raw in visual_edges:
        edge = dict(raw)
        source_event = str(edge.get("source") or "")
        target_event = str(edge.get("target") or "")
        source_state = event_to_state.get(source_event)
        target_state = event_to_state.get(target_event)
        if not source_state or not target_state:
            continue

        source_preserved = source_state in members
        target_preserved = target_state in members
        same_relative_reading = reading.get(source_state) == reading.get(target_state)
        interaction_witnessed = bool(observer and source_preserved and target_preserved and same_relative_reading)
        status = WITNESSED_STATUS if interaction_witnessed else OPEN_STATUS
        relation_id = str(edge.get("id") or _digest("interaction", edge))
        return_witness_id = _digest(
            "translation-return",
            {
                "observer": observer,
                "source": source_state,
                "target": target_state,
                "relation": relation_id,
                "reading": reading.get(source_state) if same_relative_reading else None,
            },
        ) if interaction_witnessed else None

        natural_form_equal = form_by_member.get(source_state) == form_by_member.get(target_state)
        closure_preserved = bool(interaction_witnessed and natural_form_equal)
        if interaction_witnessed:
            witnessed_pairs.append((source_state, target_state))

        interactions.append(
            {
                "id": relation_id,
                "observer_id": observer or None,
                "observed_source_id": source_state,
                "observed_target_id": target_state,
                "interaction_status": status,
                "translation_relation_witnessed": interaction_witnessed,
                "relative_reading_equal": same_relative_reading,
                "return_witness_id": return_witness_id,
                "return_is_semantic_primitive": False,
                "return_is_interaction_witness": True,
                "natural_form_equal_after_translation": natural_form_equal,
                "closure_preserved_after_translation": closure_preserved,
                "fixed_return_required": False,
                "continuation_status": OPEN_STATUS,
            }
        )

    # Translation fibres are induced by the observer's relative reading over
    # preserved source members.  Their comparison with natural-form fibres is a
    # theorem/check after the interaction carrier has been constructed.
    translation_partition = partition_signature(
        {member: reading[member] for member in sorted(members) if member in reading}
    )
    natural_form_partition = partition_signature(
        {member: form_by_member[member] for member in sorted(members) if member in form_by_member}
    )
    total = bool(observer and members and set(reading) == members and set(form_by_member) == members)
    closure_equations_derived = bool(total and translation_partition == natural_form_partition)

    body = {
        "protocol": PROTOCOL,
        "primitive": "OBSERVER_OBSERVED_INTERACTIVE_TRANSLATION",
        "observer_id": observer or None,
        "truth_member_ids": sorted(members),
        "nodes": nodes,
        "interactions": interactions,
        "translation_partition": [list(group) for group in translation_partition],
        "natural_form_partition": [list(group) for group in natural_form_partition],
        "translation_reading_total": total,
        "closure_equations_derived": closure_equations_derived,
        "chart_equivalence_is_primitive": False,
        "observation_equality_is_primitive": False,
        "return_is_primitive": False,
        "fixed_return_required": False,
        "observer_observed_relation_is_primitive": True,
        "continuation_status": OPEN_STATUS,
        "existence_closed": False,
    }
    body["id"] = _digest("interactive-translation", body)
    return body


def translation_equivalence(interactions: Mapping[str, Any]) -> bool:
    """Derived chart/natural-form equality from one relative interaction carrier."""

    return bool(interactions.get("closure_equations_derived") is True)


__all__ = ["PROTOCOL", "derive_relative_interactions", "translation_equivalence"]
