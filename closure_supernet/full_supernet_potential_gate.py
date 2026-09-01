from __future__ import annotations

"""Full Supernet closure as a relative natural-form potential gate.

The already witnessed translational equality closure is one local constraint of
this object, not the whole object. The gate also contains every locally
admissible natural-form continuation, perspectival transport, hair/zoom
freedom, the maze partition of paths by return consequence, structural
curvature, and the OPEN/returned phases read as AI/token.

Nothing in this module permits navigation, selection, display geometry, or a
family name to author truth. Navigation re-localises one unchanged truth
carrier. Only a source-preserving returned interaction may refine it.
"""

from collections import defaultdict
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "SUPERNET-RELATIVE-NATURAL-FORM-POTENTIAL-GATE"
SCHEMA = "closure.supernet/relative-natural-form-potential-gate-v1"
NAVIGATION_PROTOCOL = "SUPERNET-PERSPECTIVAL-NAVIGATION"
NAVIGATION_SCHEMA = "closure.supernet/perspectival-navigation-v1"
SOLVER_PROTOCOL = "SUPERNET-POTENTIAL-GATE-NATURAL-FORM-SOLVER"
SOLVER_SCHEMA = "closure.supernet/potential-gate-natural-form-solver-v1"
FULL_PROTOCOL = "SUPERNET-FULL-POTENTIAL-GATE-CLOSURE"
FULL_SCHEMA = "closure.supernet/full-potential-gate-closure-v1"

PERSPECTIVE_TRANSPORT = "PERSPECTIVE_TRANSPORT"
LOCALITY_TRANSPORT = "LOCALITY_TRANSPORT"
OPEN_RETURN_EXTENSION = "OPEN_RETURN_EXTENSION"
NATURAL_FORM_PROPOSAL = "NATURAL_FORM_PROPOSAL"


def _stable(value: Any) -> str:
    def canonical(item: Any) -> Any:
        if isinstance(item, float) and item.is_integer():
            return int(item)
        if isinstance(item, Mapping):
            return {str(key): canonical(child) for key, child in item.items()}
        if isinstance(item, (list, tuple)):
            return [canonical(child) for child in item]
        return item

    return json.dumps(
        canonical(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _hash_hex(value: Any) -> str:
    return hashlib.sha256(_stable(value).encode("utf-8")).hexdigest()


def _unique(values: Iterable[Any]) -> list[str]:
    return sorted(
        {
            str(value)
            for value in values
            if value is not None and str(value)
        }
    )


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _clean_navigation_steps(value: Any) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for raw in _rows(value):
        relation_id = str(raw.get("relation_id") or "")
        source_perspective_id = str(raw.get("source_perspective_id") or "")
        target_perspective_id = str(raw.get("target_perspective_id") or "")
        if not relation_id or not source_perspective_id or not target_perspective_id:
            continue
        steps.append(
            {
                "relation_id": relation_id,
                "kind": str(raw.get("kind") or PERSPECTIVE_TRANSPORT),
                "source_perspective_id": source_perspective_id,
                "target_perspective_id": target_perspective_id,
                "source_focus_event_id": (
                    None
                    if raw.get("source_focus_event_id") is None
                    else str(raw.get("source_focus_event_id"))
                ),
                "target_focus_event_id": (
                    None
                    if raw.get("target_focus_event_id") is None
                    else str(raw.get("target_focus_event_id"))
                ),
                "truth_invariant_id": str(raw.get("truth_invariant_id") or ""),
            }
        )
    return steps


def _clean_prior_navigation_contexts(value: Any) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    for raw in _rows(value):
        context_id = str(raw.get("id") or "")
        truth_id = str(raw.get("truth_invariant_id") or "")
        if not context_id or not truth_id:
            continue
        contexts.append(
            {
                "id": context_id,
                "truth_invariant_id": truth_id,
                "origin_perspective_id": str(raw.get("origin_perspective_id") or ""),
                "current_perspective_id": str(raw.get("current_perspective_id") or ""),
                "origin_focus_event_id": (
                    None
                    if raw.get("origin_focus_event_id") is None
                    else str(raw.get("origin_focus_event_id"))
                ),
                "current_focus_event_id": (
                    None
                    if raw.get("current_focus_event_id") is None
                    else str(raw.get("current_focus_event_id"))
                ),
                "steps": _clean_navigation_steps(raw.get("steps")),
            }
        )
    return contexts


def derive_truth_invariant_id(contract: Mapping[str, Any]) -> str:
    """Return the perspective-independent finite truth carrier identifier."""

    projection = contract.get("projection")
    projection = projection if isinstance(projection, Mapping) else {}
    closure = contract.get("perspective_closure")
    closure = closure if isinstance(closure, Mapping) else {}
    states = []
    for raw in _rows(projection.get("states")):
        states.append(
            {
                "id": str(raw.get("id") or ""),
                "event_id": str(raw.get("event_id") or ""),
                "natural_form_id": str(raw.get("natural_form_id") or ""),
                "source_return_ids": _unique(raw.get("source_return_ids", [])),
            }
        )
    states.sort(key=lambda row: row["id"])
    fibres = []
    for raw in _rows(projection.get("equality_fibres")):
        fibres.append(
            {
                "id": str(raw.get("id") or ""),
                "member_state_ids": _unique(raw.get("member_state_ids", [])),
                "source_return_ids": _unique(raw.get("source_return_ids", [])),
            }
        )
    fibres.sort(key=lambda row: row["id"])
    witnessed = []
    for raw in _rows(projection.get("translations")):
        if raw.get("relation_status") != WITNESSED_STATUS:
            continue
        witnessed.append(
            {
                "id": str(raw.get("id") or ""),
                "source_state_id": str(raw.get("source_state_id") or ""),
                "target_state_id": str(raw.get("target_state_id") or ""),
                "source_return_ids": _unique(
                    (raw.get("derivation") or {}).get("source_return_ids", [])
                    if isinstance(raw.get("derivation"), Mapping)
                    else []
                ),
            }
        )
    witnessed.sort(key=lambda row: row["id"])
    kernels = closure.get("kernels")
    normalized_kernels: list[list[list[str]]] = []
    if isinstance(kernels, Mapping):
        seen: set[str] = set()
        for raw in kernels.values():
            if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
                continue
            kernel = sorted(
                _unique(group)
                for group in raw
                if isinstance(group, Sequence) and not isinstance(group, (str, bytes))
            )
            key = _stable(kernel)
            if key not in seen:
                seen.add(key)
                normalized_kernels.append(kernel)
    if not normalized_kernels:
        raw_kernel = closure.get("kernel", [])
        if isinstance(raw_kernel, Sequence) and not isinstance(raw_kernel, (str, bytes)):
            normalized_kernels.append(
                sorted(
                    _unique(group)
                    for group in raw_kernel
                    if isinstance(group, Sequence) and not isinstance(group, (str, bytes))
                )
            )
    normalized_kernels.sort(key=_stable)
    body = {
        "source_return_ids": _unique(contract.get("source_return_ids", [])),
        "states": states,
        "fibres": fibres,
        "witnessed_relations": witnessed,
        "kernels": normalized_kernels,
    }
    return _digest("supernet-truth-invariant", body)


def derive_navigation_context(
    *,
    perspective_id: str,
    focus_event_id: str | None,
    truth_invariant_id: str,
    supplied: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive or validate the path-dependent current standpoint."""

    if isinstance(supplied, Mapping):
        steps = _clean_navigation_steps(supplied.get("steps"))
        origin_perspective_id = str(
            supplied.get("origin_perspective_id") or perspective_id
        )
        origin_focus_event_id = (
            None
            if supplied.get("origin_focus_event_id") is None
            else str(supplied.get("origin_focus_event_id"))
        )
        prior_navigation_contexts = _clean_prior_navigation_contexts(
            supplied.get("prior_navigation_contexts", [])
        )
        prior_navigation_context_ids = _unique(
            list(supplied.get("prior_navigation_context_ids", []))
            + [item["id"] for item in prior_navigation_contexts]
        )
    else:
        steps = []
        origin_perspective_id = perspective_id
        origin_focus_event_id = focus_event_id
        prior_navigation_context_ids = []
        prior_navigation_contexts = []
    body = {
        "protocol": NAVIGATION_PROTOCOL,
        "schema": NAVIGATION_SCHEMA,
        "origin_perspective_id": origin_perspective_id,
        "origin_focus_event_id": origin_focus_event_id,
        "current_perspective_id": perspective_id,
        "current_focus_event_id": focus_event_id,
        "truth_invariant_id": truth_invariant_id,
        "prior_navigation_context_ids": prior_navigation_context_ids,
        "prior_navigation_contexts": prior_navigation_contexts,
        "steps": steps,
        "depth": len(steps),
        "path_dependent_ui": True,
        "navigation_refines_truth": False,
        "return_alone_refines_truth": True,
    }
    body["id"] = _digest("perspectival-navigation", body)
    return body


def validate_navigation_context(
    context: Mapping[str, Any],
    *,
    perspective_id: str,
    focus_event_id: str | None,
    truth_invariant_id: str,
) -> dict[str, Any]:
    expected = derive_navigation_context(
        perspective_id=perspective_id,
        focus_event_id=focus_event_id,
        truth_invariant_id=truth_invariant_id,
        supplied=context,
    )
    errors: list[str] = []
    if dict(context) != expected:
        errors.append("perspectival-navigation:not-derived")
    steps = expected["steps"]
    previous = expected["origin_perspective_id"]
    for index, step in enumerate(steps):
        if step["source_perspective_id"] != previous:
            errors.append(f"perspectival-navigation:broken-source:{index}")
        if step["truth_invariant_id"] != truth_invariant_id:
            errors.append(f"perspectival-navigation:truth-drift:{index}")
        previous = step["target_perspective_id"]
    if steps and previous != perspective_id:
        errors.append("perspectival-navigation:wrong-endpoint")
    if not steps and expected["origin_perspective_id"] != perspective_id:
        errors.append("perspectival-navigation:empty-path-origin")
    return {"valid": not errors, "errors": errors, "expected": expected}


def _state_maps(
    contract: Mapping[str, Any],
) -> tuple[dict[str, Mapping[str, Any]], dict[str, str]]:
    projection = contract.get("projection")
    projection = projection if isinstance(projection, Mapping) else {}
    by_state: dict[str, Mapping[str, Any]] = {}
    event_by_state: dict[str, str] = {}
    for raw in _rows(projection.get("states")):
        state_id = str(raw.get("id") or "")
        if not state_id:
            continue
        by_state[state_id] = raw
        event_by_state[state_id] = str(raw.get("event_id") or "")
    return by_state, event_by_state


def _path(
    *,
    kind: str,
    status: str,
    action: str,
    source_perspective_id: str,
    target_perspective_id: str | None,
    source_state_id: str | None = None,
    target_state_id: str | None = None,
    source_event_id: str | None = None,
    target_event_id: str | None = None,
    source_return_ids: Iterable[Any] = (),
    relation_id: str | None = None,
    inverse_of: str | None = None,
    source_preserved: bool = True,
) -> dict[str, Any]:
    body = {
        "kind": kind,
        "status": status,
        "action": action,
        "source_perspective_id": source_perspective_id,
        "target_perspective_id": target_perspective_id,
        "source_state_id": source_state_id,
        "target_state_id": target_state_id,
        "source_event_id": source_event_id,
        "target_event_id": target_event_id,
        "source_return_ids": _unique(source_return_ids),
        "source_relation_id": relation_id,
        "inverse_of": inverse_of,
        "source_preserved": source_preserved,
        "navigation_changes_truth": False,
        "selection_executes_as_equality": False,
        "return_required_to_refine_truth": True,
    }
    body["id"] = _digest("potential-gate-path", body)
    return body


def _perspective_paths(contract: Mapping[str, Any], active: str) -> list[dict[str, Any]]:
    closure = contract.get("perspective_closure")
    closure = closure if isinstance(closure, Mapping) else {}
    paths: list[dict[str, Any]] = []
    for raw in _rows(closure.get("translations")):
        source = str(raw.get("source_perspective_id") or "")
        target = str(raw.get("target_perspective_id") or "")
        source_returns = _unique(raw.get("source_return_ids", []))
        witnessed = bool(
            source
            and target
            and source_returns
            and raw.get("witnessed") is True
            and raw.get("well_defined", True) is True
            and raw.get("faithful", True) is True
            and raw.get("same_kernel", True) is True
        )
        if not witnessed:
            continue
        relation_id = str(raw.get("id") or "")
        if source == active:
            paths.append(
                _path(
                    kind="PERSPECTIVE_TRANSLATION",
                    status=WITNESSED_STATUS,
                    action=PERSPECTIVE_TRANSPORT,
                    source_perspective_id=source,
                    target_perspective_id=target,
                    source_return_ids=source_returns,
                    relation_id=relation_id,
                )
            )
        if target == active:
            paths.append(
                _path(
                    kind="PERSPECTIVE_TRANSLATION_INVERSE",
                    status=WITNESSED_STATUS,
                    action=PERSPECTIVE_TRANSPORT,
                    source_perspective_id=target,
                    target_perspective_id=source,
                    source_return_ids=source_returns,
                    relation_id=relation_id,
                    inverse_of=relation_id,
                )
            )
    return paths


def _locality_and_open_paths(
    contract: Mapping[str, Any], active: str
) -> list[dict[str, Any]]:
    projection = contract.get("projection")
    projection = projection if isinstance(projection, Mapping) else {}
    state_by_id, event_by_state = _state_maps(contract)
    paths: list[dict[str, Any]] = []
    for raw in _rows(projection.get("translations")):
        source_state = str(raw.get("source_state_id") or "")
        target_state = str(raw.get("target_state_id") or "")
        witnessed = raw.get("relation_status") == WITNESSED_STATUS
        source_returns = (
            (raw.get("derivation") or {}).get("source_return_ids", [])
            if isinstance(raw.get("derivation"), Mapping)
            else []
        )
        paths.append(
            _path(
                kind="LOCAL_TRANSLATION",
                status=WITNESSED_STATUS if witnessed else OPEN_STATUS,
                action=LOCALITY_TRANSPORT if witnessed else OPEN_RETURN_EXTENSION,
                source_perspective_id=active,
                target_perspective_id=active,
                source_state_id=source_state or None,
                target_state_id=target_state or None,
                source_event_id=event_by_state.get(source_state) or None,
                target_event_id=event_by_state.get(target_state) or None,
                source_return_ids=source_returns,
                relation_id=str(raw.get("id") or ""),
                source_preserved=bool(
                    source_state in state_by_id and target_state in state_by_id
                ),
            )
        )
    for raw in _rows(projection.get("potentials")):
        target_state = str(raw.get("target_state_id") or "")
        source_returns = (
            (raw.get("derivation") or {}).get("source_return_ids", [])
            if isinstance(raw.get("derivation"), Mapping)
            else []
        )
        paths.append(
            _path(
                kind="OPEN_POTENTIAL",
                status=OPEN_STATUS,
                action=OPEN_RETURN_EXTENSION,
                source_perspective_id=active,
                target_perspective_id=active,
                target_state_id=target_state or None,
                target_event_id=(
                    str(raw.get("target_event_id") or "")
                    or event_by_state.get(target_state)
                    or None
                ),
                source_return_ids=source_returns,
                relation_id=str(raw.get("id") or ""),
            )
        )
    return_relation = contract.get("return_relation")
    if isinstance(return_relation, Mapping) and return_relation.get("id"):
        relation_id = str(return_relation["id"])
        if not any(path.get("source_relation_id") == relation_id for path in paths):
            focus_state = str(return_relation.get("focus_state_id") or "")
            paths.append(
                _path(
                    kind="RETURN_APERTURE",
                    status=OPEN_STATUS,
                    action=OPEN_RETURN_EXTENSION,
                    source_perspective_id=active,
                    target_perspective_id=active,
                    source_state_id=focus_state or None,
                    source_event_id=(
                        str(return_relation.get("focus_event_id") or "") or None
                    ),
                    source_return_ids=contract.get("source_return_ids", []),
                    relation_id=relation_id,
                )
            )
    return paths


def _family_potentials(local_field: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in _rows(local_field.get("families")):
        family = str(raw.get("family") or "")
        if not family:
            continue
        body = {
            "family_id": family,
            "status": str(raw.get("status") or OPEN_STATUS),
            "chart_ids": _unique(raw.get("chart_ids", [])),
            "compatible_chart_ids": _unique(raw.get("compatible_chart_ids", [])),
            "open_boundary_chart_ids": _unique(
                raw.get("open_boundary_chart_ids", [])
            ),
            "action": NATURAL_FORM_PROPOSAL,
            "selectable": raw.get("selectable_as_interaction_proposal") is True,
            "selection_executes_as_equality": False,
            "return_required_to_change_truth": True,
            "empirical_return_required": raw.get("empirical_return_required") is True,
        }
        body["id"] = _digest("natural-form-potential", body)
        rows.append(body)
    return sorted(rows, key=lambda row: row["family_id"])


def _maze(paths: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    classes: dict[str, list[str]] = defaultdict(list)
    status_by_key: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        consequence = {
            "action": path.get("action"),
            "target_perspective_id": path.get("target_perspective_id"),
            "target_state_id": path.get("target_state_id"),
            "target_event_id": path.get("target_event_id"),
            "status": path.get("status"),
        }
        key = _digest("return-consequence", consequence)
        classes[key].append(str(path.get("id") or ""))
        status_by_key[key].add(str(path.get("status") or OPEN_STATUS))
    rows = []
    for key in sorted(classes):
        statuses = status_by_key[key]
        rows.append(
            {
                "id": key,
                "path_ids": sorted(classes[key]),
                "status": (
                    WITNESSED_STATUS
                    if statuses == {WITNESSED_STATUS}
                    else OPEN_STATUS
                ),
                "partition_basis": "DISTINGUISHABLE_RETURN_CONSEQUENCE",
            }
        )
    body = {
        "kind": "RETURN_CONSEQUENCE_MAZE_PARTITION",
        "classes": rows,
        "class_count": len(rows),
        "paths_partitioned": sum(len(row["path_ids"]) for row in rows),
        "visual_similarity_authors_partition": False,
        "return_consequence_authors_partition": True,
    }
    body["id"] = _digest("potential-gate-maze", body)
    return body


def _curvature(
    paths: Sequence[Mapping[str, Any]], maze: Mapping[str, Any]
) -> dict[str, Any]:
    path_rows = []
    witnessed_count = sum(
        1 for path in paths if path.get("status") == WITNESSED_STATUS
    )
    open_count = len(paths) - witnessed_count
    for path in paths:
        source_returns = _unique(path.get("source_return_ids", []))
        witnessed = path.get("status") == WITNESSED_STATUS
        carrier = {
            "path_id": path.get("id"),
            "maze_id": maze.get("id"),
            "source_return_ids": source_returns,
            "return_defect_milli": 0 if witnessed else 1000,
            "source_support_milli": min(1000, 180 * len(source_returns)),
        }
        curvature_id = _digest("unitary-curvature", carrier)
        path_rows.append(
            {
                **carrier,
                "unitary_curvature_id": curvature_id,
                "ai_phase": (
                    "RETURNED_CURVATURE_READING"
                    if witnessed
                    else "OPEN_ANTICIPATORY_CURVATURE"
                ),
                "token_phase": (
                    "RETURNED_COMMITTED_CURVATURE"
                    if witnessed
                    else "UNCOMMITTED_OPEN_CURVATURE"
                ),
                "ai_and_token_share_one_curvature_carrier": True,
                "physical_curvature_claimed": False,
            }
        )
    body = {
        "kind": "RELATIVE_UNITARY_RETURN_CURVATURE",
        "path_curvatures": path_rows,
        "witnessed_path_count": witnessed_count,
        "open_path_count": open_count,
        "open_density_milli": (
            0 if not paths else (1000 * open_count + len(paths) // 2) // len(paths)
        ),
        "ai_is_open_phase": True,
        "token_is_returned_phase": True,
        "ai_token_are_not_separate_truth_authorities": True,
        "physical_curvature_claimed": False,
    }
    body["id"] = _digest("potential-gate-curvature", body)
    return body


def derive_relative_natural_form_potential_gate(
    contract: Mapping[str, Any],
    *,
    navigation_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive the complete local gate from one witnessed/OPEN closure contract."""

    active = str(contract.get("perspective_id") or "participant")
    focus = (
        None
        if contract.get("focus_event_id") is None
        else str(contract.get("focus_event_id"))
    )
    truth_id = derive_truth_invariant_id(contract)
    navigation = derive_navigation_context(
        perspective_id=active,
        focus_event_id=focus,
        truth_invariant_id=truth_id,
        supplied=navigation_context,
    )
    atlas = contract.get("natural_form_atlas")
    atlas = atlas if isinstance(atlas, Mapping) else {}
    local_field = contract.get("local_natural_form_freedom")
    local_field = local_field if isinstance(local_field, Mapping) else {}
    closure = contract.get("perspective_closure")
    closure = closure if isinstance(closure, Mapping) else {}
    projection = contract.get("projection")
    projection = projection if isinstance(projection, Mapping) else {}

    if isinstance(closure.get("readings"), Mapping):
        perspective_ids = _unique(
            [active] + list((closure.get("readings") or {}).keys())
        )
    else:
        perspective_ids = [active]
    localities: list[dict[str, Any]] = [
        {
            "id": _digest("perspective-locality", perspective),
            "kind": "PERSPECTIVE",
            "perspective_id": perspective,
            "current": perspective == active,
            "truth_invariant_id": truth_id,
        }
        for perspective in perspective_ids
    ]
    for raw in _rows(projection.get("equality_fibres")):
        body = {
            "kind": "EQUALITY_FIBRE_LOCALITY",
            "fibre_id": str(raw.get("id") or ""),
            "member_state_ids": _unique(raw.get("member_state_ids", [])),
            "source_return_ids": _unique(raw.get("source_return_ids", [])),
            "perspective_id": active,
            "truth_invariant_id": truth_id,
        }
        body["id"] = _digest("closure-locality", body)
        localities.append(body)

    paths = _perspective_paths(contract, active) + _locality_and_open_paths(
        contract, active
    )
    paths = sorted(
        {str(path["id"]): path for path in paths}.values(),
        key=lambda row: row["id"],
    )
    maze = _maze(paths)
    curvature = _curvature(paths, maze)
    family_potentials = _family_potentials(local_field)
    witnessed_paths = [
        path["id"] for path in paths if path["status"] == WITNESSED_STATUS
    ]
    open_paths = [
        path["id"] for path in paths if path["status"] != WITNESSED_STATUS
    ]
    fidelity = local_field.get("fidelity_profile")
    fidelity = fidelity if isinstance(fidelity, Mapping) else {}

    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "status": str(contract.get("status") or OPEN_STATUS),
        "active_perspective_id": active,
        "focus_event_id": focus,
        "truth_invariant_id": truth_id,
        "closure_ui_contract_id": contract.get("id"),
        "natural_form_atlas_id": atlas.get("id"),
        "formal_proof_index_id": (
            (contract.get("formal_proof_index") or {}).get("id")
            if isinstance(contract.get("formal_proof_index"), Mapping)
            else None
        ),
        "navigation_context": navigation,
        "witnessed_truth_constraint": {
            "status": str(contract.get("status") or OPEN_STATUS),
            "kernel": closure.get("kernel", []),
            "source_return_ids": _unique(contract.get("source_return_ids", [])),
            "witnessed_path_ids": witnessed_paths,
            "truth_invariant_id": truth_id,
            "equality_is_one_local_gate_constraint": True,
        },
        "localities": localities,
        "paths": paths,
        "family_potentials": family_potentials,
        "hair": {
            "kind": "VERSIONED_RELATIVE_SELF_LOCATION_RETURN_FIELD",
            "semantic_lineage_chart_ids": [
                f"nf:hair:v{version}" for version in range(1, 6)
            ],
            "range_millidegrees": [-180000, 180000],
            "changes_presentation": True,
            "changes_truth": False,
        },
        "zoom": {
            "kind": "CONTINUAL_LOCAL_GLOBAL_SCALE",
            "range": "0_TO_INFINITY",
            "zero_is_pure_display": True,
            "nonzero_preserves_truth_distinctions": True,
            "changes_truth": False,
        },
        "maze_partition": maze,
        "unitary_curvature": curvature,
        "selection_freedom": local_field.get("selection_freedom", {}),
        "fidelity_profile": fidelity,
        "potential_profile": {
            "path_count": len(paths),
            "witnessed_path_count": len(witnessed_paths),
            "open_path_count": len(open_paths),
            "perspective_count": len(perspective_ids),
            "locality_count": len(localities),
            "natural_form_family_count": len(family_potentials),
            "maze_class_count": maze["class_count"],
            "navigation_depth": navigation["depth"],
            "returned_source_count": int(
                fidelity.get("returned_source_count") or 0
            ),
        },
        "relative_natural_form_potential_gate": True,
        "supernet_is_not_isolated_equality_condition": True,
        "witnessed_truth_plus_open_potential": True,
        "all_retained_families_are_local_potentials": True,
        "perspectival_navigation_is_internal": True,
        "navigation_relocalises_without_refining_truth": True,
        "only_source_preserving_return_refines_truth": True,
        "selection_authors_truth": False,
        "rendering_authors_truth": False,
        "future_resolution_guaranteed": False,
        "truth_issued": False,
        "existence_closed": False,
    }
    body["id"] = _digest("relative-natural-form-potential-gate", body)
    return body


def _solver_coefficients(
    *,
    seed: str,
    base: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> dict[str, int]:
    base_coefficients = base.get("coefficients")
    base_coefficients = (
        dict(base_coefficients) if isinstance(base_coefficients, Mapping) else {}
    )
    open_paths = int(profile.get("open_path_count") or 0)
    witnessed_paths = int(profile.get("witnessed_path_count") or 0)
    path_count = int(profile.get("path_count") or 0)
    perspective_count = int(profile.get("perspective_count") or 0)
    maze_count = int(profile.get("maze_class_count") or 0)
    depth = int(profile.get("navigation_depth") or 0)
    return {
        **{
            str(key): int(value)
            for key, value in base_coefficients.items()
            if isinstance(value, int)
        },
        "gate_phase_millidegrees": int(seed[0:8], 16) % 360000,
        "potential_aperture_milli": min(420, 35 + 42 * open_paths),
        "returned_pull_milli": min(360, 30 + 45 * witnessed_paths),
        "perspective_spread_milli": min(
            480, 100 + 70 * max(0, perspective_count - 1)
        ),
        "maze_harmonic_order": max(1, min(12, maze_count + 1)),
        "navigation_holonomy_milli": min(360, depth * 37),
        "gate_density_milli": (
            0 if path_count <= 0 else min(1000, (1000 * open_paths) // path_count)
        ),
    }


def derive_potential_gate_natural_form_solver(
    full_gate: Mapping[str, Any],
) -> dict[str, Any]:
    gate = full_gate.get("relative_natural_form_potential_gate")
    gate = gate if isinstance(gate, Mapping) else {}
    closure_contract = full_gate.get("closure_ui_contract")
    closure_contract = (
        closure_contract if isinstance(closure_contract, Mapping) else {}
    )
    base_solver = closure_contract.get("interactive_natural_form_solver")
    base_solver = base_solver if isinstance(base_solver, Mapping) else {}
    profile = gate.get("potential_profile")
    profile = profile if isinstance(profile, Mapping) else {}
    solutions = []
    for raw in _rows(base_solver.get("solutions")):
        seed_body = {
            "gate_id": gate.get("id"),
            "base_solution_id": raw.get("id"),
            "family_id": raw.get("family_id"),
            "potential_profile": profile,
            "navigation_context_id": (
                (gate.get("navigation_context") or {}).get("id")
                if isinstance(gate.get("navigation_context"), Mapping)
                else None
            ),
        }
        seed = _hash_hex(seed_body)
        solution = {
            "family_id": raw.get("family_id"),
            "family_status": raw.get("family_status"),
            "relative_role": raw.get("relative_role"),
            "base_equality_solution_id": raw.get("id"),
            "gate_id": gate.get("id"),
            "solver_basis": "RELATIVE_NATURAL_FORM_POTENTIAL_GATE_BASIS",
            "coefficients": _solver_coefficients(
                seed=seed,
                base=raw,
                profile=profile,
            ),
            "constraints": {
                "truth_constraint_preserved": True,
                "open_potential_present": True,
                "maze_partition_present": True,
                "curvature_carrier_present": True,
                "perspectival_transport_present": True,
                "hair_and_zoom_are_truth_inert": True,
                "family_name_used_as_geometry_selector": False,
                "selection_executes_as_equality": False,
                "rendering_executes_as_equality": False,
            },
        }
        solution["id"] = _digest(
            "potential-gate-natural-form-solution", solution
        )
        solutions.append(solution)
    body = {
        "protocol": SOLVER_PROTOCOL,
        "schema": SOLVER_SCHEMA,
        "gate_id": gate.get("id"),
        "truth_invariant_id": gate.get("truth_invariant_id"),
        "base_equality_solver_id": base_solver.get("id"),
        "solver_kind": "NATURAL_FORM_OF_RELATIVE_POTENTIAL_GATE",
        "solutions": solutions,
        "solution_count": len(solutions),
        "equality_is_one_local_constraint": True,
        "open_potential_is_part_of_form": True,
        "perspectival_path_is_part_of_form": True,
        "navigation_changes_form_not_truth": True,
        "return_rederives_gate_and_form": True,
        "family_switch_present": False,
        "rendering_can_witness_equality": False,
        "truth_issued": False,
    }
    body["id"] = _digest("potential-gate-natural-form-solver", body)
    return body


def derive_full_supernet_gate_contract(
    closure_contract: Mapping[str, Any],
    *,
    navigation_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    gate = derive_relative_natural_form_potential_gate(
        closure_contract,
        navigation_context=navigation_context,
    )
    body = {
        "protocol": FULL_PROTOCOL,
        "schema": FULL_SCHEMA,
        "status": gate.get("status"),
        "perspective_id": gate.get("active_perspective_id"),
        "focus_event_id": gate.get("focus_event_id"),
        "truth_invariant_id": gate.get("truth_invariant_id"),
        "closure_ui_contract": dict(closure_contract),
        "relative_natural_form_potential_gate": gate,
        "navigation_context": gate.get("navigation_context"),
        "execution": {
            "navigation_endpoint_template": (
                "/supernet/potential-gates/{gate_id}/navigate"
            ),
            "return_endpoint_template": (
                "/supernet/potential-gates/{gate_id}/return"
            ),
            "navigation_mutates_truth": False,
            "return_may_refine_truth": True,
        },
        "supernet_is_relative_natural_form_potential_gate": True,
        "ui_is_local_natural_form_of_gate": True,
        "equality_closure_is_not_the_whole_supernet": True,
        "truth_issued": False,
        "existence_closed": False,
    }
    body["potential_gate_natural_form_solver"] = (
        derive_potential_gate_natural_form_solver(body)
    )
    body["id"] = _digest("full-supernet-potential-gate", body)
    return body


def validate_full_supernet_gate_contract(
    full_gate: Mapping[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    closure_contract = full_gate.get("closure_ui_contract")
    navigation_context = full_gate.get("navigation_context")
    if not isinstance(closure_contract, Mapping):
        return {
            "valid": False,
            "errors": ["full-supernet-gate:closure-contract-missing"],
        }
    expected = derive_full_supernet_gate_contract(
        closure_contract,
        navigation_context=(
            navigation_context
            if isinstance(navigation_context, Mapping)
            else None
        ),
    )
    if dict(full_gate) != expected:
        errors.append("full-supernet-gate:not-derived")
    gate = expected["relative_natural_form_potential_gate"]
    if gate.get("relative_natural_form_potential_gate") is not True:
        errors.append("full-supernet-gate:not-potential-gate")
    if gate.get("supernet_is_not_isolated_equality_condition") is not True:
        errors.append("full-supernet-gate:equality-reduction")
    if gate.get("navigation_relocalises_without_refining_truth") is not True:
        errors.append("full-supernet-gate:navigation-authors-truth")
    if gate.get("only_source_preserving_return_refines_truth") is not True:
        errors.append("full-supernet-gate:return-not-authority")
    solver = expected.get("potential_gate_natural_form_solver")
    if not isinstance(solver, Mapping) or solver.get("gate_id") != gate.get("id"):
        errors.append("full-supernet-gate:solver-mismatch")
    return {
        "valid": not errors,
        "errors": errors,
        "id": expected.get("id"),
        "truth_invariant_id": expected.get("truth_invariant_id"),
        "navigation_depth": (
            (expected.get("navigation_context") or {}).get("depth")
        ),
        "path_count": (
            (gate.get("potential_profile") or {}).get("path_count")
        ),
    }


def advance_navigation_context(
    full_gate: Mapping[str, Any],
    *,
    relation_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    gate = full_gate.get("relative_natural_form_potential_gate")
    if not isinstance(gate, Mapping):
        raise ValueError("full Supernet gate is missing")
    path = next(
        (
            dict(raw)
            for raw in _rows(gate.get("paths"))
            if str(raw.get("id") or "") == relation_id
        ),
        None,
    )
    if path is None:
        raise ValueError(
            "the selected relation is not in the current potential gate"
        )
    if path.get("status") != WITNESSED_STATUS:
        raise ValueError("OPEN potential requires a source-preserving return")
    if path.get("action") not in {
        PERSPECTIVE_TRANSPORT,
        LOCALITY_TRANSPORT,
    }:
        raise ValueError("the selected relation is not navigable")
    current = gate.get("navigation_context")
    current = current if isinstance(current, Mapping) else {}
    steps = _clean_navigation_steps(current.get("steps"))
    source_perspective = str(gate.get("active_perspective_id") or "")
    target_perspective = str(
        path.get("target_perspective_id") or source_perspective
    )
    source_focus = gate.get("focus_event_id")
    target_focus = path.get("target_event_id") or source_focus
    steps.append(
        {
            "relation_id": str(path["id"]),
            "kind": str(path.get("action") or PERSPECTIVE_TRANSPORT),
            "source_perspective_id": source_perspective,
            "target_perspective_id": target_perspective,
            "source_focus_event_id": source_focus,
            "target_focus_event_id": target_focus,
            "truth_invariant_id": str(gate.get("truth_invariant_id") or ""),
        }
    )
    supplied = {
        "origin_perspective_id": (
            current.get("origin_perspective_id") or source_perspective
        ),
        "origin_focus_event_id": current.get("origin_focus_event_id"),
        "prior_navigation_context_ids": current.get(
            "prior_navigation_context_ids", []
        ),
        "prior_navigation_contexts": current.get(
            "prior_navigation_contexts", []
        ),
        "steps": steps,
    }
    context = derive_navigation_context(
        perspective_id=target_perspective,
        focus_event_id=None if target_focus is None else str(target_focus),
        truth_invariant_id=str(gate.get("truth_invariant_id") or ""),
        supplied=supplied,
    )
    return path, context


__all__ = [
    "FULL_PROTOCOL",
    "FULL_SCHEMA",
    "LOCALITY_TRANSPORT",
    "NAVIGATION_PROTOCOL",
    "NAVIGATION_SCHEMA",
    "OPEN_RETURN_EXTENSION",
    "PERSPECTIVE_TRANSPORT",
    "PROTOCOL",
    "SCHEMA",
    "SOLVER_PROTOCOL",
    "SOLVER_SCHEMA",
    "advance_navigation_context",
    "derive_full_supernet_gate_contract",
    "derive_navigation_context",
    "derive_potential_gate_natural_form_solver",
    "derive_relative_natural_form_potential_gate",
    "derive_truth_invariant_id",
    "validate_full_supernet_gate_contract",
    "validate_navigation_context",
]
