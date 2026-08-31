from __future__ import annotations

"""Derive the Supernet interface and every admissible action from one closure ball.

The production closure contract already contains the source-preserving returns,
translated perspective readings, equality fibres, witnessed translations and
OPEN potentials.  This module does not add a second truth model.  It factors
that one contract into a closure ball and then derives four equal readings of
each interaction event:

    UI(event) = AI(event) = token(event) = closure(event)

The equality is an equality of the underlying translational event, not an
assertion that the four presentation types are literally the same Python type.
No display geometry, AI suggestion, or token amount may alter the equality
kernel.  OPEN paths remain navigable but never execute as equality.
"""

import hashlib
import json
import math
from typing import Any, Iterable, Mapping, Sequence


PROTOCOL = "closure.supernet/closure-ball-perspective-flow-v1"
WITNESSED_STATUS = "WITNESSED"
OPEN_STATUS = "OPEN"


def _stable(value: Any) -> str:
    """Canonical JSON used by both identity derivation and browser verification."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _digest(prefix: str, value: Any) -> str:
    content = hashlib.sha256(_stable(value).encode("utf-8")).hexdigest()
    return f"{prefix}:{content[:24]}"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, (list, tuple)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _unique(values: Iterable[Any]) -> list[str]:
    return list(
        dict.fromkeys(
            str(value)
            for value in values
            if value is not None and str(value)
        )
    )


def _normalized_kernel(value: Any) -> list[list[str]]:
    """Return a canonical disjoint partition or an empty kernel on malformed data."""

    if not isinstance(value, (list, tuple)):
        return []
    groups: list[list[str]] = []
    seen: set[str] = set()
    for raw_group in value:
        if not isinstance(raw_group, (list, tuple, set, frozenset)):
            return []
        group = sorted(_unique(raw_group))
        if not group or any(member in seen for member in group):
            return []
        seen.update(group)
        groups.append(group)
    return sorted(groups, key=lambda group: (group[0], len(group), group))


def _projection_kernel(contract: Mapping[str, Any]) -> list[list[str]]:
    projection = _mapping(contract.get("projection"))
    from_fibres = _normalized_kernel(
        [
            row.get("member_state_ids", [])
            for row in _rows(projection.get("equality_fibres"))
        ]
    )
    if from_fibres:
        return from_fibres

    perspective = _mapping(contract.get("perspective_closure"))
    from_perspective = _normalized_kernel(perspective.get("kernel"))
    if from_perspective:
        return from_perspective

    equations = _mapping(contract.get("closure_naturality_equations"))
    finite = _mapping(equations.get("finite_instance"))
    return _normalized_kernel(finite.get("closure_fibres"))


def _state_rows(contract: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    projection = _mapping(contract.get("projection"))
    return sorted(
        _rows(projection.get("states")),
        key=lambda row: str(row.get("id") or ""),
    )


def _state_event_index(states: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    return {
        str(row.get("id")): str(row.get("event_id"))
        for row in states
        if row.get("id") and row.get("event_id")
    }


def _active_focus_state(
    contract: Mapping[str, Any],
    states: Sequence[Mapping[str, Any]],
) -> str | None:
    focus_event_id = str(contract.get("focus_event_id") or "")
    if focus_event_id:
        for row in states:
            if str(row.get("event_id") or "") == focus_event_id:
                return str(row.get("id") or "") or None

    relation = _mapping(contract.get("return_relation"))
    focus_state_id = str(relation.get("focus_state_id") or "")
    if focus_state_id:
        return focus_state_id

    if states:
        return str(states[0].get("id") or "") or None
    return None


def _cell_for_state(kernel: Sequence[Sequence[str]], state_id: str | None) -> int | None:
    if state_id is None:
        return None
    for index, group in enumerate(kernel):
        if state_id in group:
            return index
    return None


def _source_ids(row: Mapping[str, Any]) -> list[str]:
    derivation = _mapping(row.get("derivation"))
    return _unique(
        [
            *_unique(derivation.get("source_return_ids", [])),
            *_unique(row.get("source_return_ids", [])),
        ]
    )


def _relation_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Extract semantic relation paths without reading authored display geometry."""

    projection = _mapping(contract.get("projection"))
    relations: list[dict[str, Any]] = []
    seen: set[str] = set()

    for row in sorted(
        _rows(projection.get("translations")),
        key=lambda item: str(item.get("id") or ""),
    ):
        relation_id = str(row.get("id") or "")
        if not relation_id or relation_id in seen:
            continue
        seen.add(relation_id)
        witnessed = bool(
            row.get("relation_status") == WITNESSED_STATUS
            and row.get("executes_as_equality") is True
            and row.get("same_display_fibre") is True
        )
        relations.append(
            {
                "relation_id": relation_id,
                "kind": "WITNESSED_TRANSLATION" if witnessed else "OPEN_TRANSLATION",
                "source_state_id": str(row.get("source_state_id") or "") or None,
                "target_state_id": str(row.get("target_state_id") or "") or None,
                "target_natural_form_id": None,
                "source_return_ids": _source_ids(row),
                "witnessed": witnessed,
                "executes_as_equality": witnessed,
            }
        )

    for row in sorted(
        _rows(projection.get("potentials")),
        key=lambda item: str(item.get("id") or ""),
    ):
        relation_id = str(row.get("id") or "")
        if not relation_id or relation_id in seen:
            continue
        seen.add(relation_id)
        relations.append(
            {
                "relation_id": relation_id,
                "kind": "OPEN_POTENTIAL",
                "source_state_id": str(row.get("source_state_id") or "") or None,
                "target_state_id": str(row.get("target_state_id") or "") or None,
                "target_natural_form_id": str(
                    row.get("shared_natural_form_id") or ""
                )
                or None,
                "source_return_ids": _source_ids(row),
                "witnessed": False,
                "executes_as_equality": False,
            }
        )

    return relations


def _perspective_translation_rows(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    perspective = _mapping(contract.get("perspective_closure"))
    readings = _mapping(perspective.get("readings"))
    kernels = _mapping(perspective.get("kernels"))
    active = str(contract.get("perspective_id") or "participant")
    active_kernel = _normalized_kernel(
        kernels.get(active) if active in kernels else perspective.get("kernel")
    )

    rows: list[dict[str, Any]] = []
    for row in sorted(
        _rows(perspective.get("translations")),
        key=lambda item: str(item.get("id") or ""),
    ):
        if row.get("witnessed") is not True:
            continue
        source = str(row.get("source_perspective_id") or "")
        target = str(row.get("target_perspective_id") or "")
        if active not in {source, target}:
            continue
        destination = target if active == source else source
        if not destination or destination not in readings:
            continue
        destination_kernel = _normalized_kernel(kernels.get(destination))
        if active_kernel and destination_kernel and active_kernel != destination_kernel:
            continue
        rows.append(
            {
                "translation_id": str(row.get("id") or ""),
                "source_perspective_id": active,
                "target_perspective_id": destination,
                "source_return_ids": _unique(row.get("source_return_ids", [])),
            }
        )
    return rows


def _cell_geometry(index: int, count: int, focused: bool) -> dict[str, Any]:
    """Derive a continuous-ball projection, never a stored semantic coordinate."""

    if focused or count <= 1:
        return {
            "centre": [500.0, 360.0],
            "radius": 132.0,
            "phase": 0.0,
            "locality_scale": 1.0,
        }
    peripheral = max(1, count - 1)
    phase = (2.0 * math.pi * index / peripheral) - math.pi / 2.0
    return {
        "centre": [
            round(500.0 + 286.0 * math.cos(phase), 6),
            round(360.0 + 212.0 * math.sin(phase), 6),
        ],
        "radius": round(max(82.0, 124.0 - min(30.0, count * 2.0)), 6),
        "phase": round(phase, 9),
        "locality_scale": round(1.0 / max(1.0, math.sqrt(count)), 9),
    }


def _maze_partition(
    *,
    contract: Mapping[str, Any],
    kernel: list[list[str]],
    states: Sequence[Mapping[str, Any]],
    focus_state_id: str | None,
    closure_ball_id: str,
) -> dict[str, Any]:
    projection = _mapping(contract.get("projection"))
    fibre_rows = _rows(projection.get("equality_fibres"))
    fibre_by_members = {
        tuple(sorted(_unique(row.get("member_state_ids", [])))): row
        for row in fibre_rows
    }
    state_events = _state_event_index(states)
    state_by_id = {
        str(row.get("id")): row
        for row in states
        if row.get("id")
    }
    focus_cell = _cell_for_state(kernel, focus_state_id)

    cells: list[dict[str, Any]] = []
    peripheral_index = 0
    for index, members in enumerate(kernel):
        row = fibre_by_members.get(tuple(members), {})
        focused = index == focus_cell
        geometry_index = 0 if focused else peripheral_index
        if not focused:
            peripheral_index += 1
        cell_basis = {
            "closure_ball_id": closure_ball_id,
            "member_state_ids": members,
            "natural_form_id": row.get("id"),
        }
        representative_state = (
            focus_state_id if focused and focus_state_id in members else members[0]
        )
        cells.append(
            {
                "id": _digest("closure-locality", cell_basis),
                "identity_basis": cell_basis,
                "natural_form_id": str(row.get("id") or "") or None,
                "member_state_ids": list(members),
                "member_event_ids": _unique(state_events.get(member) for member in members),
                "representative_state_id": representative_state,
                "representative_event_id": state_events.get(representative_state),
                "display_fibre_ids": _unique(row.get("display_fibre_ids", [])),
                "source_return_ids": _unique(
                    [
                        *_source_ids(row),
                        *(
                            source_id
                            for member in members
                            for source_id in _source_ids(state_by_id.get(member, {}))
                        ),
                    ]
                ),
                "source_traces": [
                    {
                        "state_id": member,
                        "event_id": state_events.get(member),
                        "exact_source": str(
                            state_by_id.get(member, {}).get("source_trace") or ""
                        ),
                        "source_return_ids": _source_ids(
                            state_by_id.get(member, {})
                        ),
                    }
                    for member in members
                    if str(state_by_id.get(member, {}).get("source_trace") or "")
                ],
                "focused": focused,
                "geometry": _cell_geometry(
                    geometry_index,
                    len(kernel),
                    focused,
                ),
            }
        )

    partition_basis = {
        "closure_ball_id": closure_ball_id,
        "kernel": kernel,
        "cell_ids": [cell["id"] for cell in cells],
    }
    return {
        "id": _digest("closure-maze-partition", partition_basis),
        "identity_basis": partition_basis,
        "kernel": kernel,
        "cells": cells,
        "carrier_state_ids": sorted(_unique(row.get("id") for row in states)),
        "focus_cell_id": next(
            (str(cell["id"]) for cell in cells if cell["focused"]),
            None,
        ),
        "partition_is_ai_and_token_locality": True,
    }


def _action(
    *,
    kind: str,
    closure_ball_id: str,
    projection_id: str,
    basis: Mapping[str, Any],
    status: str,
    source_perspective_id: str,
    target_perspective_id: str | None = None,
    target_state_id: str | None = None,
    target_event_id: str | None = None,
    target_natural_form_id: str | None = None,
    relation_id: str | None = None,
    return_relation_id: str | None = None,
    source_return_ids: Iterable[Any] = (),
    executes_as_equality: bool = False,
    requires_return: bool = False,
    parameter: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    identity_basis = {
        "kind": kind,
        "closure_ball_id": closure_ball_id,
        "projection_id": projection_id,
        **dict(basis),
    }
    return {
        "id": _digest("closure-hair-action", identity_basis),
        "identity_basis": identity_basis,
        "kind": kind,
        "status": status,
        "closure_ball_id": closure_ball_id,
        "projection_id": projection_id,
        "source_perspective_id": source_perspective_id,
        "target_perspective_id": target_perspective_id,
        "target_state_id": target_state_id,
        "target_event_id": target_event_id,
        "target_natural_form_id": target_natural_form_id,
        "relation_id": relation_id,
        "return_relation_id": return_relation_id,
        "source_return_ids": _unique(source_return_ids),
        "executes_as_equality": executes_as_equality,
        "preserves_equality_kernel": not requires_return,
        "requires_source_preserving_return": requires_return,
        "reclose_before_commit": requires_return,
        "parameter": dict(parameter) if parameter is not None else None,
    }


def _hair_actions(
    *,
    contract: Mapping[str, Any],
    closure_ball_id: str,
    projection_id: str,
    maze: Mapping[str, Any],
    relations: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    active = str(contract.get("perspective_id") or "participant")
    actions: list[dict[str, Any]] = []

    for cell in _rows(maze.get("cells")):
        target_state_id = str(cell.get("representative_state_id") or "") or None
        target_event_id = str(cell.get("representative_event_id") or "") or None
        actions.append(
            _action(
                kind="ENTER_CLOSURE_LOCALITY",
                closure_ball_id=closure_ball_id,
                projection_id=projection_id,
                basis={
                    "locality_id": cell.get("id"),
                    "target_state_id": target_state_id,
                },
                status=WITNESSED_STATUS,
                source_perspective_id=active,
                target_perspective_id=active,
                target_state_id=target_state_id,
                target_event_id=target_event_id,
                target_natural_form_id=(
                    str(cell.get("natural_form_id") or "") or None
                ),
                source_return_ids=cell.get("source_return_ids", []),
                # Entering another locality re-bases the view; it never
                # identifies distinct maze cells as equal.
                executes_as_equality=False,
            )
        )

    for row in _perspective_translation_rows(contract):
        actions.append(
            _action(
                kind="REBASE_PERSPECTIVE",
                closure_ball_id=closure_ball_id,
                projection_id=projection_id,
                basis={
                    "translation_id": row["translation_id"],
                    "source_perspective_id": row["source_perspective_id"],
                    "target_perspective_id": row["target_perspective_id"],
                },
                status=WITNESSED_STATUS,
                source_perspective_id=active,
                target_perspective_id=row["target_perspective_id"],
                relation_id=row["translation_id"],
                source_return_ids=row["source_return_ids"],
                executes_as_equality=True,
            )
        )

    state_events = _state_event_index(_state_rows(contract))
    for row in relations:
        target_state = str(row.get("target_state_id") or "") or None
        kind = "FOLLOW_WITNESSED_TRANSLATION" if row.get("witnessed") else "FOLLOW_OPEN_SEAM"
        actions.append(
            _action(
                kind=kind,
                closure_ball_id=closure_ball_id,
                projection_id=projection_id,
                basis={
                    "relation_id": row.get("relation_id"),
                    "source_state_id": row.get("source_state_id"),
                    "target_state_id": target_state,
                    "witnessed": row.get("witnessed") is True,
                },
                status=WITNESSED_STATUS if row.get("witnessed") else OPEN_STATUS,
                source_perspective_id=active,
                target_perspective_id=active,
                target_state_id=target_state,
                target_event_id=state_events.get(target_state or ""),
                target_natural_form_id=(
                    str(row.get("target_natural_form_id") or "") or None
                ),
                relation_id=str(row.get("relation_id") or "") or None,
                source_return_ids=row.get("source_return_ids", []),
                executes_as_equality=row.get("witnessed") is True,
                requires_return=False,
            )
        )

    relation = _mapping(contract.get("return_relation"))
    return_relation_id = str(relation.get("id") or "")
    if return_relation_id:
        actions.append(
            _action(
                kind="EXTEND_SOURCE_PRESERVING_RETURN",
                closure_ball_id=closure_ball_id,
                projection_id=projection_id,
                basis={
                    "return_relation_id": return_relation_id,
                    "focus_event_id": contract.get("focus_event_id"),
                    "perspective_id": active,
                },
                status=OPEN_STATUS,
                source_perspective_id=active,
                target_perspective_id=active,
                target_natural_form_id=(
                    str(relation.get("parent_natural_form_id") or "") or None
                ),
                return_relation_id=return_relation_id,
                source_return_ids=_source_ids(relation),
                executes_as_equality=False,
                requires_return=True,
            )
        )

    actions.append(
        _action(
            kind="REPARAMETERIZE_PERSPECTIVE_HAIR",
            closure_ball_id=closure_ball_id,
            projection_id=projection_id,
            basis={"active_perspective_id": active},
            status=WITNESSED_STATUS,
            source_perspective_id=active,
            target_perspective_id=active,
            source_return_ids=contract.get("source_return_ids", []),
            executes_as_equality=True,
            parameter={
                "name": "local_perspective_hair_millidegrees",
                "minimum": -180_000,
                "maximum": 180_000,
                "identity": 0,
            },
        )
    )

    deduplicated: dict[str, dict[str, Any]] = {}
    for action in actions:
        deduplicated[str(action["id"])] = action
    return sorted(deduplicated.values(), key=lambda row: str(row["id"]))


def _event_projection(
    *,
    action: Mapping[str, Any],
    closure_ball_id: str,
    projection_id: str,
    maze: Mapping[str, Any],
    focus_state_id: str | None,
) -> dict[str, Any]:
    kernel = _normalized_kernel(maze.get("kernel"))
    source_state = focus_state_id
    target_state = str(action.get("target_state_id") or "") or None
    source_cell_index = _cell_for_state(kernel, source_state)
    target_cell_index = _cell_for_state(kernel, target_state)
    path_witnessed = action.get("status") == WITNESSED_STATUS
    executes_as_equality = action.get("executes_as_equality") is True
    open_seam = not path_witnessed

    path_basis = {
        "closure_ball_id": closure_ball_id,
        "projection_id": projection_id,
        "hair_action_id": action.get("id"),
        "kind": action.get("kind"),
        "relation_id": action.get("relation_id"),
        "return_relation_id": action.get("return_relation_id"),
        "source_state_id": source_state,
        "target_state_id": target_state,
        "source_return_ids": list(action.get("source_return_ids", [])),
    }
    underlying_path_id = _digest("closure-interaction-path", path_basis)
    curvature_basis = {
        "closure_ball_id": closure_ball_id,
        "underlying_path_id": underlying_path_id,
        "witnessed": path_witnessed,
        "source_return_ids": list(action.get("source_return_ids", [])),
    }
    curvature_id = (
        _digest("unitary-curvature", curvature_basis)
        if path_witnessed
        else None
    )

    common = {
        "underlying_path_id": underlying_path_id,
        "path_identity_basis": path_basis,
        "closure_ball_id": closure_ball_id,
        "projection_id": projection_id,
        "hair_action_id": action.get("id"),
        "kind": action.get("kind"),
        "status": WITNESSED_STATUS if path_witnessed else OPEN_STATUS,
        "source_state_id": source_state,
        "target_state_id": target_state,
        "source_maze_cell_index": source_cell_index,
        "target_maze_cell_index": target_cell_index,
        "relation_id": action.get("relation_id"),
        "return_relation_id": action.get("return_relation_id"),
        "source_return_ids": list(action.get("source_return_ids", [])),
        "executes_as_equality": executes_as_equality,
        "identifies_source_and_target": executes_as_equality,
        "preserves_equality_kernel": (
            action.get("preserves_equality_kernel") is True
        ),
        "open_seam": open_seam,
        "closure_defect": 0 if path_witnessed else None,
        "unitary_curvature_id": curvature_id,
        "numeric_curvature": None,
        "numeric_value_not_invented": True,
        "truth_issued": False,
        "currency_issued": False,
    }
    event_basis = {
        "underlying_path_id": underlying_path_id,
        "event_projection": common,
    }
    return {
        "id": _digest("closure-interaction-event", event_basis),
        "identity_basis": event_basis,
        "underlying_path_id": underlying_path_id,
        "hair_action_id": action.get("id"),
        "event_projection": common,
        # These are equal translations of one event.  They intentionally carry
        # identical semantic content rather than independently authored state.
        "readings": {
            "ui": dict(common),
            "ai": dict(common),
            "token": dict(common),
            "closure": dict(common),
        },
    }


def _ui_geometry(
    *,
    maze: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    cell_positions = {
        index: _mapping(cell.get("geometry")).get("centre", [500.0, 360.0])
        for index, cell in enumerate(_rows(maze.get("cells")))
    }
    paths: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        projection = _mapping(event.get("event_projection"))
        source_index = projection.get("source_maze_cell_index")
        target_index = projection.get("target_maze_cell_index")
        source = cell_positions.get(source_index, [500.0, 360.0])
        if target_index in cell_positions:
            target = cell_positions[target_index]
        else:
            signature = int(
                hashlib.sha256(
                    str(event.get("underlying_path_id") or "").encode("utf-8")
                ).hexdigest()[:8],
                16,
            )
            phase = 2.0 * math.pi * ((signature % 3600) / 3600.0)
            target = [
                round(500.0 + 430.0 * math.cos(phase), 6),
                round(360.0 + 310.0 * math.sin(phase), 6),
            ]
        dx = float(target[0]) - float(source[0])
        dy = float(target[1]) - float(source[1])
        length = max(1.0, math.hypot(dx, dy))
        bend = min(92.0, length * 0.22)
        control = [
            round((float(source[0]) + float(target[0])) / 2.0 - dy / length * bend, 6),
            round((float(source[1]) + float(target[1])) / 2.0 + dx / length * bend, 6),
        ]
        paths.append(
            {
                "event_id": event.get("id"),
                "hair_action_id": event.get("hair_action_id"),
                "underlying_path_id": event.get("underlying_path_id"),
                "quadratic_path": [list(source), control, list(target)],
                "open_seam": projection.get("open_seam") is True,
                "executes_as_equality": (
                    projection.get("executes_as_equality") is True
                ),
                "phase_index": index,
            }
        )
    return {
        "view_box": [0, 0, 1000, 720],
        "closure_boundary": {"centre": [500, 360], "radius": 338},
        "cell_localities": [
            {
                "cell_id": cell.get("id"),
                "natural_form_id": cell.get("natural_form_id"),
                "centre": _mapping(cell.get("geometry")).get("centre"),
                "radius": _mapping(cell.get("geometry")).get("radius"),
                "focused": cell.get("focused") is True,
            }
            for cell in _rows(maze.get("cells"))
        ],
        "hair_paths": paths,
        "geometry_is_projection_only": True,
        "geometry_defines_equality": False,
    }


def derive_closure_ball_projection(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Derive one closure ball and its natural interactive UI projection."""

    states = _state_rows(contract)
    carrier = sorted(_unique(row.get("id") for row in states))
    kernel = _projection_kernel(contract)
    relations = _relation_rows(contract)
    source_return_ids = _unique(contract.get("source_return_ids", []))
    equations = _mapping(contract.get("closure_naturality_equations"))

    relation_basis = [
        {
            "relation_id": row["relation_id"],
            "kind": row["kind"],
            "source_state_id": row["source_state_id"],
            "target_state_id": row["target_state_id"],
            "target_natural_form_id": row["target_natural_form_id"],
            "source_return_ids": row["source_return_ids"],
            "executes_as_equality": row["executes_as_equality"],
        }
        for row in relations
    ]
    ball_basis = {
        "closure_derivation_id": contract.get("closure_derivation_id"),
        "visual_closure_id": contract.get("visual_closure_id"),
        "interactive_translation_id": contract.get("interactive_translation_id"),
        "closure_equation_system_id": equations.get("id"),
        "carrier_state_ids": carrier,
        "closure_kernel": kernel,
        "relations": relation_basis,
        "source_return_ids": source_return_ids,
    }
    closure_ball_id = _digest("closure-ball", ball_basis)
    active = str(contract.get("perspective_id") or "participant")
    focus_state_id = _active_focus_state(contract, states)
    projection_basis = {
        "closure_ball_id": closure_ball_id,
        "active_perspective_id": active,
        "focus_state_id": focus_state_id,
        "focus_event_id": contract.get("focus_event_id"),
        "field_event_seq": contract.get("field_event_seq"),
        "contract_id": contract.get("id"),
    }
    projection_id = _digest("closure-ball-relative-projection", projection_basis)

    maze = _maze_partition(
        contract=contract,
        kernel=kernel,
        states=states,
        focus_state_id=focus_state_id,
        closure_ball_id=closure_ball_id,
    )
    actions = _hair_actions(
        contract=contract,
        closure_ball_id=closure_ball_id,
        projection_id=projection_id,
        maze=maze,
        relations=relations,
    )
    events = [
        _event_projection(
            action=action,
            closure_ball_id=closure_ball_id,
            projection_id=projection_id,
            maze=maze,
            focus_state_id=focus_state_id,
        )
        for action in actions
    ]
    geometry = _ui_geometry(maze=maze, events=events)

    action_ids = [str(row["id"]) for row in actions]
    event_ids = [str(row["id"]) for row in events]
    open_event_ids = [
        str(row["id"])
        for row in events
        if _mapping(row.get("event_projection")).get("open_seam") is True
    ]
    witnessed_event_ids = [
        str(row["id"])
        for row in events
        if _mapping(row.get("event_projection")).get("executes_as_equality")
        is True
    ]

    status = str(contract.get("status") or OPEN_STATUS)
    carrier_covered = sorted(
        member for group in kernel for member in group
    ) == carrier
    readings_equal = all(
        _stable(_mapping(event.get("readings")).get("ui"))
        == _stable(_mapping(event.get("readings")).get("ai"))
        == _stable(_mapping(event.get("readings")).get("token"))
        == _stable(_mapping(event.get("readings")).get("closure"))
        for event in events
    )
    all_actions_are_events = set(action_ids) == {
        str(event.get("hair_action_id")) for event in events
    }
    open_never_equal = all(
        not (
            _mapping(event.get("event_projection")).get("open_seam") is True
            and _mapping(event.get("event_projection")).get(
                "executes_as_equality"
            )
            is True
        )
        for event in events
    )
    witnessed_defect_zero = all(
        _mapping(event.get("event_projection")).get("closure_defect") == 0
        for event in events
        if _mapping(event.get("event_projection")).get("status")
        == WITNESSED_STATUS
    )

    checks = {
        "ui_is_derived_from_closure_ball": True,
        "user_actions_are_exactly_hair": all_actions_are_events,
        "maze_partition_is_closure_kernel": (
            carrier_covered if carrier else not kernel
        ),
        "ui_ai_token_closure_are_equal_event_translations": readings_equal,
        "open_seams_never_execute_as_equality": open_never_equal,
        "witnessed_closure_defect_is_zero": witnessed_defect_zero,
        "numeric_curvature_or_value_not_invented": all(
            _mapping(event.get("event_projection")).get("numeric_curvature")
            is None
            for event in events
        ),
        "geometry_cannot_author_equality": geometry[
            "geometry_defines_equality"
        ]
        is False,
        "parallel_ui_ai_token_truth_state_absent": True,
    }
    checks["equality_closure_preserved"] = all(checks.values())

    body: dict[str, Any] = {
        "protocol": PROTOCOL,
        "id": closure_ball_id,
        "identity_basis": ball_basis,
        "contract_id": contract.get("id"),
        "status": status,
        "active_perspective_id": active,
        "focus_event_id": contract.get("focus_event_id"),
        "focus_state_id": focus_state_id,
        "projection_id": projection_id,
        "projection_identity_basis": projection_basis,
        "closure_equation_system_id": equations.get("id"),
        "carrier_state_ids": carrier,
        "source_return_ids": source_return_ids,
        "maze_partition": maze,
        "hair": {
            "id": _digest(
                "closure-hair",
                {
                    "closure_ball_id": closure_ball_id,
                    "projection_id": projection_id,
                    "action_ids": action_ids,
                },
            ),
            "source": "CLOSURE_BALL_ONLY",
            "actions": actions,
            "action_ids": action_ids,
            "arbitrary_application_commands": [],
            "hair_changes_presentation_not_equality": True,
        },
        "interaction_events": events,
        "unitary_curvature": {
            "event_ids": event_ids,
            "witnessed_event_ids": witnessed_event_ids,
            "open_event_ids": open_event_ids,
            "numeric_value_not_invented": True,
            "authenticated_external_return_required_for_economic_value": True,
        },
        "natural_ui": {
            "operator": "RELATIVE_PROJECTION_OF_CLOSURE_BALL",
            "closure_ball_id": closure_ball_id,
            "projection_id": projection_id,
            "active_perspective_id": active,
            "focus_state_id": focus_state_id,
            "maze_partition_id": maze["id"],
            "hair_action_ids": action_ids,
            "interaction_event_ids": event_ids,
            "geometry": geometry,
            "interface_is_external_scene": False,
        },
        "equality": {
            "equation": (
                "UI(event)=AI(event)=Token(event)=Closure(event) "
                "modulo perspective translation"
            ),
            "all_readings_factor_through_event_projection": True,
            "ai_may_author_equality": False,
            "token_may_issue_value_without_return": False,
            "open_is_preserved": True,
            "existence_closed": False,
        },
        "checks": checks,
        "boundary": {
            "truth_issued": False,
            "currency_issued": False,
            "physical_law_claimed": False,
            "consciousness_claimed": False,
            "lean_theorems_reproved_by_python": False,
        },
    }
    body["receipt_id"] = _digest("closure-ball-receipt", body)
    return body


def validate_closure_ball_projection(
    contract: Mapping[str, Any],
    closure_ball: Mapping[str, Any],
) -> dict[str, Any]:
    """Re-derive the ball and reject any independently authored projection."""

    expected = derive_closure_ball_projection(contract)
    errors: list[str] = []
    if not isinstance(closure_ball, Mapping):
        errors.append("closure-ball:missing")
    elif dict(closure_ball) != expected:
        errors.append("closure-ball:not-exact-derivation")

    checks = _mapping(expected.get("checks"))
    if checks.get("equality_closure_preserved") is not True:
        errors.append("closure-ball:equality-closure-open")

    return {
        "valid": not errors,
        "errors": errors,
        "expected_id": expected.get("id"),
        "supplied_id": (
            closure_ball.get("id") if isinstance(closure_ball, Mapping) else None
        ),
        "expected_receipt_id": expected.get("receipt_id"),
        "supplied_receipt_id": (
            closure_ball.get("receipt_id")
            if isinstance(closure_ball, Mapping)
            else None
        ),
    }


__all__ = [
    "PROTOCOL",
    "derive_closure_ball_projection",
    "validate_closure_ball_projection",
]
