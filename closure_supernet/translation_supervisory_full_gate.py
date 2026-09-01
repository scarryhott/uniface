from __future__ import annotations

"""Full-gate refinement by NRRF882 translation equivalence.

The base full gate remains the source of closure, OPEN continuation, hair,
maze, curvature, atlas freedom and navigation history. This module refines
its perspectival relation field with the exact translation-equivalence
geometry returned by ``translation_supervisory_geometry``.

When two perspectives both have returned semantic market valuations, the
semantic relation is authoritative for their relative translation:

* shared-token, cross-consistent valuations -> WITNESSED perspective transport;
* no shared token -> OPEN relative position;
* inconsistent cross relations -> OPEN relative position.

A pre-existing generic perspective path is removed for that pair so an older
same-kernel transport cannot bypass the stronger returned translation witness.
If no semantic valuation evidence exists for a pair, the prior Supernet path
semantics are preserved for compatibility with non-market perspectives.
"""

from copy import deepcopy
from typing import Any, Mapping

from . import full_supernet_potential_gate as _base
from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .translation_supervisory_geometry import (
    derive_translation_supervisory_geometry,
    validate_translation_supervisory_geometry,
)

PROTOCOL = "SUPERNET-NRRF882-TRANSLATION-SUPERVISORY-FULL-GATE"
SCHEMA = "closure.supernet/nrrf882-translation-supervisory-full-gate-v1"

# Runtime provenance is append-only and never caller-authored. The registry is
# only a bridge for the immediate successor gate because the legacy closure
# contract intentionally omits event authorship. Every emitted full-gate
# contract carries the exact map used to derive it, so validation does not rely
# on mutable process state.
_SOURCE_PERSPECTIVE_REGISTRY: dict[str, str] = {}


def set_source_perspective_registry(mapping: Mapping[str, str]) -> None:
    _SOURCE_PERSPECTIVE_REGISTRY.clear()
    _SOURCE_PERSPECTIVE_REGISTRY.update(
        {
            str(event_id): str(perspective_id)
            for event_id, perspective_id in mapping.items()
            if str(event_id) and str(perspective_id)
        }
    )


def update_source_perspective_registry(mapping: Mapping[str, str]) -> None:
    _SOURCE_PERSPECTIVE_REGISTRY.update(
        {
            str(event_id): str(perspective_id)
            for event_id, perspective_id in mapping.items()
            if str(event_id) and str(perspective_id)
        }
    )


def source_perspective_registry() -> dict[str, str]:
    return dict(sorted(_SOURCE_PERSPECTIVE_REGISTRY.items()))


def _semantic_pair_key(source: str, target: str) -> tuple[str, str]:
    return tuple(sorted((source, target)))


def _semantic_paths(
    geometry: Mapping[str, Any],
    *,
    active_perspective_id: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relation in geometry.get("relations", []):
        if not isinstance(relation, Mapping):
            continue
        source = str(relation.get("source_perspective_id") or "")
        target = str(relation.get("target_perspective_id") or "")
        if active_perspective_id not in {source, target}:
            continue
        other = target if source == active_perspective_id else source
        witnessed = relation.get("status") == WITNESSED_STATUS
        path = _base._path(
            kind=(
                "SEMANTIC_TRANSLATION_EQUIVALENCE"
                if witnessed
                else "OPEN_SEMANTIC_TRANSLATION"
            ),
            status=WITNESSED_STATUS if witnessed else OPEN_STATUS,
            action=(
                _base.PERSPECTIVE_TRANSPORT
                if witnessed
                else _base.OPEN_RETURN_EXTENSION
            ),
            source_perspective_id=active_perspective_id,
            target_perspective_id=other,
            source_return_ids=relation.get("source_return_ids", []),
            relation_id=str(relation.get("id") or ""),
            source_preserved=True,
        )
        path["translation_supervisory_relation_id"] = relation.get("id")
        path["shared_token_ids"] = list(relation.get("shared_token_ids", []))
        path["translation_scale"] = relation.get("translation_scale")
        path["cross_loss"] = relation.get("cross_loss")
        path["semantic_translation_determined"] = witnessed
        path["semantic_translation_reason"] = relation.get("reason")
        path.pop("id", None)
        path["id"] = _base._digest("potential-gate-path", path)
        rows.append(path)
    return rows


def _refine_gate(
    base_gate: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    source_perspective_by_event: Mapping[str, str],
) -> dict[str, Any]:
    gate = deepcopy(dict(base_gate))
    geometry = derive_translation_supervisory_geometry(
        contract,
        source_perspective_by_event=source_perspective_by_event,
    )
    active = str(gate.get("active_perspective_id") or "participant")

    semantic_perspectives = {
        str(row.get("perspective_id") or "")
        for row in geometry.get("valuations", [])
        if isinstance(row, Mapping) and row.get("perspective_id")
    }
    controlled_pairs = {
        _semantic_pair_key(
            str(row.get("source_perspective_id") or ""),
            str(row.get("target_perspective_id") or ""),
        )
        for row in geometry.get("relations", [])
        if isinstance(row, Mapping)
        and row.get("source_perspective_id")
        and row.get("target_perspective_id")
    }

    retained_paths: list[dict[str, Any]] = []
    for raw in gate.get("paths", []):
        if not isinstance(raw, Mapping):
            continue
        path = dict(raw)
        source = str(path.get("source_perspective_id") or "")
        target = str(path.get("target_perspective_id") or "")
        is_generic_perspective_path = str(path.get("kind") or "") in {
            "PERSPECTIVE_TRANSLATION",
            "PERSPECTIVE_TRANSLATION_INVERSE",
        }
        controlled = (
            is_generic_perspective_path
            and source in semantic_perspectives
            and target in semantic_perspectives
            and _semantic_pair_key(source, target) in controlled_pairs
        )
        if not controlled:
            retained_paths.append(path)

    semantic_paths = _semantic_paths(
        geometry,
        active_perspective_id=active,
    )
    paths = sorted(
        {
            str(path["id"]): path
            for path in [*retained_paths, *semantic_paths]
        }.values(),
        key=lambda row: str(row["id"]),
    )
    maze = _base._maze(paths)
    curvature = _base._curvature(paths, maze)
    witnessed_paths = [
        str(path["id"])
        for path in paths
        if path.get("status") == WITNESSED_STATUS
    ]
    open_paths = [
        str(path["id"])
        for path in paths
        if path.get("status") != WITNESSED_STATUS
    ]

    gate["paths"] = paths
    gate["maze_partition"] = maze
    gate["unitary_curvature"] = curvature
    gate["translation_supervisory_geometry"] = geometry
    gate["translation_supervisory_geometry_id"] = geometry["id"]
    gate["ai_supervision_is_token_translation_geometry"] = True
    gate["semantic_navigation_is_translation_determined"] = True
    gate["no_shared_token_relative_position_is_open"] = True
    gate["raw_absolute_valuation_authors_supervision"] = False
    gate["similarity_authors_perspective_translation"] = False

    profile = dict(gate.get("potential_profile") or {})
    profile.update(
        {
            "path_count": len(paths),
            "witnessed_path_count": len(witnessed_paths),
            "open_path_count": len(open_paths),
            "maze_class_count": maze.get("class_count", 0),
            "semantic_valuation_count": geometry.get("valuation_count", 0),
            "semantic_translation_relation_count": geometry.get(
                "relation_count", 0
            ),
            "semantic_witnessed_relation_count": len(
                geometry.get("witnessed_relation_ids", [])
            ),
            "semantic_open_relation_count": len(
                geometry.get("open_relation_ids", [])
            ),
        }
    )
    gate["potential_profile"] = profile
    gate.pop("id", None)
    gate["id"] = _base._digest("relative-natural-form-potential-gate", gate)
    return gate


def derive_full_supernet_gate_contract(
    closure_contract: Mapping[str, Any],
    *,
    navigation_context: Mapping[str, Any] | None = None,
    source_perspective_by_event: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    source_map = (
        source_perspective_registry()
        if source_perspective_by_event is None
        else {
            str(event_id): str(perspective_id)
            for event_id, perspective_id in source_perspective_by_event.items()
            if str(event_id) and str(perspective_id)
        }
    )
    base = _base.derive_full_supernet_gate_contract(
        closure_contract,
        navigation_context=navigation_context,
    )
    gate = _refine_gate(
        base["relative_natural_form_potential_gate"],
        contract=closure_contract,
        source_perspective_by_event=source_map,
    )
    body = dict(base)
    body.pop("id", None)
    body["protocol"] = PROTOCOL
    body["schema"] = SCHEMA
    body["relative_natural_form_potential_gate"] = gate
    body["navigation_context"] = gate["navigation_context"]
    body["source_perspective_by_event"] = dict(sorted(source_map.items()))
    body["translation_supervisory_geometry_id"] = gate[
        "translation_supervisory_geometry_id"
    ]
    body["ai_supervision_equals_token_translation_geometry"] = True
    body["perspective_navigation_uses_determined_equal_translation"] = True
    body["absolute_market_reading_is_not_supervision"] = True
    body["potential_gate_natural_form_solver"] = (
        _base.derive_potential_gate_natural_form_solver(body)
    )
    body["id"] = _base._digest("full-supernet-potential-gate", body)
    return body


def validate_full_supernet_gate_contract(
    full_gate: Mapping[str, Any],
) -> dict[str, Any]:
    closure_contract = full_gate.get("closure_ui_contract")
    navigation_context = full_gate.get("navigation_context")
    provenance = full_gate.get("source_perspective_by_event")
    provenance = provenance if isinstance(provenance, Mapping) else {}
    if not isinstance(closure_contract, Mapping):
        return {
            "valid": False,
            "errors": ["translation-supervisory-full-gate:closure-contract-missing"],
        }
    expected = derive_full_supernet_gate_contract(
        closure_contract,
        navigation_context=(
            navigation_context if isinstance(navigation_context, Mapping) else None
        ),
        source_perspective_by_event=provenance,
    )
    errors: list[str] = []
    if dict(full_gate) != expected:
        errors.append("translation-supervisory-full-gate:not-derived")
    gate = expected["relative_natural_form_potential_gate"]
    geometry = gate.get("translation_supervisory_geometry")
    if not isinstance(geometry, Mapping):
        errors.append("translation-supervisory-full-gate:geometry-missing")
    else:
        geometry_validation = validate_translation_supervisory_geometry(
            geometry,
            contract=closure_contract,
            source_perspective_by_event=provenance,
        )
        if geometry_validation.get("valid") is not True:
            errors.extend(geometry_validation.get("errors", []))
    if expected.get("ai_supervision_equals_token_translation_geometry") is not True:
        errors.append("translation-supervisory-full-gate:ai-token-split")
    if expected.get("perspective_navigation_uses_determined_equal_translation") is not True:
        errors.append("translation-supervisory-full-gate:navigation-translation-split")
    if expected.get("absolute_market_reading_is_not_supervision") is not True:
        errors.append("translation-supervisory-full-gate:absolute-supervision")
    return {
        "valid": not errors,
        "errors": errors,
        "id": expected.get("id"),
        "translation_supervisory_geometry_id": expected.get(
            "translation_supervisory_geometry_id"
        ),
        "semantic_valuation_count": (
            (gate.get("potential_profile") or {}).get("semantic_valuation_count")
        ),
    }


__all__ = [
    "PROTOCOL",
    "SCHEMA",
    "derive_full_supernet_gate_contract",
    "set_source_perspective_registry",
    "source_perspective_registry",
    "update_source_perspective_registry",
    "validate_full_supernet_gate_contract",
]
