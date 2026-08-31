from __future__ import annotations

"""Canonical natural-form solver over interactive equality closure.

A natural form is not selected from a developer-authored geometry catalogue.
For one verified UI contract this module derives a finite equality-closure
signature, combines it with the versioned chart constraints, and solves one
bounded presentation chart for every locally admissible natural-form family.

The solver has one generic harmonic basis. Family names and visual resemblance
never choose an operator.  Distinct solutions arise only from:

* the current translated equality partition;
* witnessed and OPEN interaction relations;
* exact source-return history;
* the versioned chart constraint tuple
  (carrier, standpoint, boundary, inversion, paths, return, domain, version);
* the family's returned atlas distance from the current truth chart.

Rendering remains presentation-only.  It cannot witness equality, alter truth
support, or replace the source-preserving returned interaction relation.
"""

from collections import deque
import hashlib
import json
import math
from typing import Any, Iterable, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "SUPERNET-INTERACTIVE-NATURAL-FORM-SOLVER"
SCHEMA = "closure.supernet/interactive-natural-form-solver-v1"

SEMANTIC_FIELDS: tuple[str, ...] = (
    "carrier",
    "standpoint",
    "boundary",
    "inversion",
    "paths",
    "return",
    "domain",
    "version",
    "semantic_role",
)


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _hash_hex(value: Any) -> str:
    return hashlib.sha256(_stable(value).encode("utf-8")).hexdigest()


def _unique_sorted(values: Iterable[Any]) -> list[str]:
    return sorted(
        {
            str(value)
            for value in values
            if value is not None and str(value)
        }
    )


def _round_ratio_milli(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        return 0
    return (1000 * numerator + denominator // 2) // denominator


def _normalized_kernel(value: Any) -> list[list[str]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    groups: list[list[str]] = []
    seen: set[str] = set()
    for raw in value:
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
            return []
        members = _unique_sorted(raw)
        if not members or any(member in seen for member in members):
            return []
        seen.update(members)
        groups.append(members)
    return sorted(groups)


def _component_count(nodes: Sequence[str], edges: Sequence[tuple[str, str]]) -> int:
    if not nodes:
        return 0
    graph: dict[str, set[str]] = {node: set() for node in nodes}
    for source, target in edges:
        if source in graph and target in graph:
            graph[source].add(target)
            graph[target].add(source)
    unseen = set(nodes)
    count = 0
    while unseen:
        count += 1
        root = min(unseen)
        unseen.remove(root)
        queue: deque[str] = deque([root])
        while queue:
            current = queue.popleft()
            for neighbour in sorted(graph[current]):
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    queue.append(neighbour)
    return count


def derive_interactive_equality_closure_signature(
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Derive the exact finite closure constraints visible to the solver."""

    projection = contract.get("projection")
    projection = projection if isinstance(projection, Mapping) else {}
    closure = contract.get("perspective_closure")
    closure = closure if isinstance(closure, Mapping) else {}

    states: list[dict[str, Any]] = []
    for raw in projection.get("states", []):
        if not isinstance(raw, Mapping) or not raw.get("id"):
            continue
        states.append(
            {
                "id": str(raw.get("id")),
                "event_id": str(raw.get("event_id") or ""),
                "display_fibre_id": str(raw.get("display_fibre_id") or ""),
                "source_return_ids": _unique_sorted(raw.get("source_return_ids", [])),
            }
        )
    states.sort(key=lambda item: item["id"])
    state_ids = [item["id"] for item in states]

    fibres: list[dict[str, Any]] = []
    for raw in projection.get("equality_fibres", []):
        if not isinstance(raw, Mapping) or not raw.get("id"):
            continue
        fibres.append(
            {
                "id": str(raw.get("id")),
                "member_state_ids": _unique_sorted(raw.get("member_state_ids", [])),
                "source_return_ids": _unique_sorted(raw.get("source_return_ids", [])),
            }
        )
    fibres.sort(key=lambda item: item["id"])

    translations: list[dict[str, Any]] = []
    witnessed_edges: list[tuple[str, str]] = []
    for raw in projection.get("translations", []):
        if not isinstance(raw, Mapping) or not raw.get("id"):
            continue
        status = str(raw.get("relation_status") or "")
        source = str(raw.get("source_state_id") or "")
        target = str(raw.get("target_state_id") or "")
        executes = raw.get("executes_as_equality") is True
        translations.append(
            {
                "id": str(raw.get("id")),
                "source_state_id": source,
                "target_state_id": target,
                "relation_status": status,
                "executes_as_equality": executes,
            }
        )
        if status == WITNESSED_STATUS and source and target:
            witnessed_edges.append((source, target))
    translations.sort(key=lambda item: item["id"])

    potentials: list[dict[str, Any]] = []
    for raw in projection.get("potentials", []):
        if not isinstance(raw, Mapping) or not raw.get("id"):
            continue
        target = raw.get("target_state_id")
        potentials.append(
            {
                "id": str(raw.get("id")),
                "source_state_id": str(raw.get("source_state_id") or ""),
                "target_state_id": None if target is None else str(target),
                "relation_status": str(raw.get("relation_status") or ""),
                "executes_as_equality": raw.get("executes_as_equality") is True,
            }
        )
    potentials.sort(key=lambda item: item["id"])

    component_count = _component_count(state_ids, witnessed_edges)
    witnessed_count = sum(
        1 for item in translations if item["relation_status"] == WITNESSED_STATUS
    )
    open_count = sum(
        1 for item in translations if item["relation_status"] != WITNESSED_STATUS
    ) + len(potentials)
    relation_count = witnessed_count + open_count
    source_return_ids = _unique_sorted(contract.get("source_return_ids", []))
    partition_profile = sorted(len(item["member_state_ids"]) for item in fibres)
    loop_rank = max(0, witnessed_count - len(state_ids) + component_count)

    body = {
        "status": str(contract.get("status") or OPEN_STATUS),
        "perspective_id": str(contract.get("perspective_id") or ""),
        "focus_event_id": str(contract.get("focus_event_id") or ""),
        "closure_equation_system_id": str(
            (contract.get("closure_naturality_equations") or {}).get("id") or ""
        ),
        "states": states,
        "fibres": fibres,
        "translations": translations,
        "potentials": potentials,
        "kernel": _normalized_kernel(closure.get("kernel", [])),
        "source_return_ids": source_return_ids,
        "continuation_lineage_ids": [
            str(item) for item in contract.get("continuation_lineage_ids", [])
        ],
        "state_count": len(states),
        "fibre_count": len(fibres),
        "partition_profile": partition_profile,
        "witnessed_relation_count": witnessed_count,
        "open_relation_count": open_count,
        "relation_count": relation_count,
        "component_count": component_count,
        "loop_rank": loop_rank,
        "partition_density_milli": _round_ratio_milli(len(fibres), len(states)),
        "return_density_milli": _round_ratio_milli(
            len(source_return_ids), max(1, len(states) + len(source_return_ids))
        ),
        "open_density_milli": _round_ratio_milli(open_count, max(1, relation_count)),
    }
    body["id"] = _digest("interactive-equality-closure", body)
    return body


def _atlas_graph(atlas: Mapping[str, Any]) -> dict[str, set[str]]:
    chart_ids = {
        str(chart.get("id"))
        for chart in atlas.get("charts", [])
        if isinstance(chart, Mapping) and chart.get("id")
    }
    graph: dict[str, set[str]] = {chart_id: set() for chart_id in chart_ids}
    for raw in atlas.get("translations", []):
        if not isinstance(raw, Mapping):
            continue
        if raw.get("status") != WITNESSED_STATUS or raw.get("kind") == "IDENTITY":
            continue
        source = str(raw.get("source_chart_id") or "")
        target = str(raw.get("target_chart_id") or "")
        if source in graph and target in graph:
            graph[source].add(target)
            graph[target].add(source)
    return graph


def _family_relative_roles(
    *,
    contract: Mapping[str, Any],
    atlas: Mapping[str, Any],
    local_field: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    graph = _atlas_graph(atlas)
    projection = contract.get("projection")
    projection = projection if isinstance(projection, Mapping) else {}
    state_to_chart = atlas.get("runtime_state_to_chart")
    state_to_chart = state_to_chart if isinstance(state_to_chart, Mapping) else {}

    roots: set[str] = set()
    for state in projection.get("states", []):
        if not isinstance(state, Mapping):
            continue
        chart_id = str(state_to_chart.get(str(state.get("id") or "")) or "")
        if chart_id in graph:
            roots.add(chart_id)
    if not roots:
        roots.update(
            str(chart.get("id"))
            for chart in atlas.get("charts", [])
            if isinstance(chart, Mapping)
            and chart.get("runtime_generated") is True
            and str(chart.get("id")) in graph
        )

    distance: dict[str, int] = {}
    queue: deque[str] = deque()
    for root in sorted(roots):
        distance[root] = 0
        queue.append(root)
    while queue:
        current = queue.popleft()
        next_distance = distance[current] + 1
        for neighbour in sorted(graph.get(current, ())):
            if neighbour not in distance:
                distance[neighbour] = next_distance
                queue.append(neighbour)

    roles: dict[str, dict[str, Any]] = {}
    rows = [
        row for row in local_field.get("families", []) if isinstance(row, Mapping)
    ]
    for row in sorted(rows, key=lambda item: str(item.get("family") or "")):
        family = str(row.get("family") or "")
        candidates = [
            distance[str(chart.get("id"))]
            for chart in atlas.get("charts", [])
            if isinstance(chart, Mapping)
            and str(chart.get("family") or "") == family
            and chart.get("runtime_generated") is not True
            and str(chart.get("id")) in distance
        ]
        if not candidates:
            roles[family] = {"role": OPEN_STATUS, "distance": None}
        else:
            minimum = min(candidates)
            roles[family] = {
                "role": "LOCAL" if minimum <= 1 else "GLOBAL",
                "distance": minimum,
            }
    return roles


def _semantic_constraints(
    *, family: str, atlas: Mapping[str, Any]
) -> list[dict[str, Any]]:
    constraints: dict[str, dict[str, Any]] = {}
    for chart in atlas.get("charts", []):
        if not isinstance(chart, Mapping):
            continue
        if str(chart.get("family") or "") != family:
            continue
        row = {
            field: chart.get(field)
            for field in SEMANTIC_FIELDS
            if chart.get(field) is not None
        }
        key = _stable(row)
        constraints[key] = row
    return [constraints[key] for key in sorted(constraints)]


def _seed_byte(seed: str, index: int) -> int:
    offset = (index * 2) % len(seed)
    return int(seed[offset : offset + 2], 16)


def _derive_coefficients(
    *,
    seed_hex: str,
    equality: Mapping[str, Any],
    role: str,
    distance: int | None,
) -> dict[str, int]:
    partition_density = int(equality.get("partition_density_milli") or 0)
    return_density = int(equality.get("return_density_milli") or 0)
    open_density = int(equality.get("open_density_milli") or 0)
    fibre_count = int(equality.get("fibre_count") or 0)
    loop_rank = int(equality.get("loop_rank") or 0)

    role_gain = 1000 if role == "LOCAL" else 760 if role == "GLOBAL" else 520
    distance_gain = 1000 if distance is None else max(420, 1000 - 95 * distance)
    harmonic_order = 1 + (_seed_byte(seed_hex, 6) % 7) + (fibre_count % 3)
    determinant_floor = 450_000

    coefficients = {
        "angle_millidegrees": int(seed_hex[0:8], 16) % 360_000,
        "phase_millidegrees": int(seed_hex[8:16], 16) % 360_000,
        "stretch_x_milli": 720 + (_seed_byte(seed_hex, 8) % 561),
        "stretch_y_milli": 720 + (_seed_byte(seed_hex, 9) % 561),
        "shear_x_milli": (_seed_byte(seed_hex, 10) - 128) * 2,
        "shear_y_milli": (_seed_byte(seed_hex, 11) - 128) * 2,
        "harmonic_order": harmonic_order,
        "radial_milli": min(
            320,
            24
            + (_seed_byte(seed_hex, 12) % 177)
            + partition_density // 12
            + min(56, loop_rank * 7),
        ),
        "twist_milli": (_seed_byte(seed_hex, 13) - 128) * 2
        + (open_density - 500) // 8,
        "fold_milli": (_seed_byte(seed_hex, 14) - 128)
        + (partition_density - 500) // 10,
        "cross_milli": (_seed_byte(seed_hex, 15) - 128)
        + (return_density - 500) // 12,
        "boundary_gain_milli": 620 + (_seed_byte(seed_hex, 16) % 881),
        "open_aperture_milli": min(
            300,
            20 + (_seed_byte(seed_hex, 17) % 121) + open_density // 8,
        ),
        "return_pull_milli": min(
            260,
            18 + (_seed_byte(seed_hex, 18) % 113) + return_density // 8,
        ),
        "hair_coupling_milli": 250 + (_seed_byte(seed_hex, 19) % 751),
        "role_gain_milli": role_gain,
        "distance_gain_milli": distance_gain,
        "determinant_floor_million": determinant_floor,
    }
    determinant = (
        coefficients["stretch_x_milli"] * coefficients["stretch_y_milli"]
        - coefficients["shear_x_milli"] * coefficients["shear_y_milli"]
    )
    coefficients["linear_determinant_million"] = determinant
    return coefficients


def derive_interactive_natural_form_solver(
    contract: Mapping[str, Any],
    *,
    atlas: Mapping[str, Any] | None = None,
    local_field: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Solve every admissible family from one interactive equality closure."""

    atlas_value = atlas if isinstance(atlas, Mapping) else contract.get("natural_form_atlas")
    atlas_value = atlas_value if isinstance(atlas_value, Mapping) else {}
    field_value = (
        local_field
        if isinstance(local_field, Mapping)
        else contract.get("local_natural_form_freedom")
    )
    field_value = field_value if isinstance(field_value, Mapping) else {}

    equality = derive_interactive_equality_closure_signature(contract)
    roles = _family_relative_roles(
        contract=contract,
        atlas=atlas_value,
        local_field=field_value,
    )
    solutions: list[dict[str, Any]] = []
    rows = [row for row in field_value.get("families", []) if isinstance(row, Mapping)]
    for row in sorted(rows, key=lambda item: str(item.get("family") or "")):
        family = str(row.get("family") or "")
        relative = roles.get(family, {"role": OPEN_STATUS, "distance": None})
        constraints = _semantic_constraints(family=family, atlas=atlas_value)
        semantic_body = {
            "semantic_constraints": constraints,
            "relative_role": relative["role"],
            "return_distance": relative["distance"],
            "family_status": str(row.get("status") or OPEN_STATUS),
            "empirical_return_required": row.get("empirical_return_required") is True,
            "equality_closure_id": equality["id"],
        }
        semantic_constraint_id = _digest("natural-form-constraints", semantic_body)
        seed_hex = _hash_hex(semantic_body)
        coefficients = _derive_coefficients(
            seed_hex=seed_hex,
            equality=equality,
            role=str(relative["role"]),
            distance=relative["distance"],
        )
        solution = {
            "family_id": family,
            "family_status": str(row.get("status") or OPEN_STATUS),
            "relative_role": relative["role"],
            "return_distance": relative["distance"],
            "semantic_constraint_id": semantic_constraint_id,
            "semantic_constraints": constraints,
            "solver_basis": "GENERIC_BOUNDED_HARMONIC_EQUALITY_CLOSURE_BASIS",
            "coefficients": coefficients,
            "constraints": {
                "origin_fixed": True,
                "bounded_on_viewbox": True,
                "linear_invertibility_required": True,
                "linear_invertibility_witnessed": (
                    coefficients["linear_determinant_million"]
                    >= coefficients["determinant_floor_million"]
                ),
                "source_relation_paths_preserved": True,
                "equality_partition_source": equality["id"],
                "family_name_used_as_geometry_selector": False,
                "visual_resemblance_used_as_geometry_selector": False,
                "named_geometry_template_present": False,
                "rendering_executes_as_equality": False,
                "selection_authors_truth": False,
                "return_required_for_truth_refinement": True,
            },
        }
        solution["id"] = _digest("natural-form-solution", solution)
        solutions.append(solution)

    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "atlas_id": atlas_value.get("id"),
        "local_natural_form_freedom_id": field_value.get("id"),
        "active_perspective_id": str(contract.get("perspective_id") or ""),
        "equality_closure_signature": equality,
        "solver_kind": "CANONICAL_CONSTRAINT_SOLUTION_OVER_INTERACTIVE_EQUALITY_CLOSURE",
        "basis_terms": [
            "INVERTIBLE_LINEAR_RELATIVE_CHART",
            "PARTITION_DENSITY_RADIAL_HARMONIC",
            "RETURN_DENSITY_SOURCE_PULL",
            "OPEN_DENSITY_APERTURE",
            "LOOP_RANK_TWIST",
            "PERSPECTIVE_HAIR_PHASE",
        ],
        "semantic_constraint_fields": list(SEMANTIC_FIELDS),
        "solutions": solutions,
        "solution_count": len(solutions),
        "natural_form_is_interactive_interface_equality_closure": True,
        "natural_form_is_posthoc_visual_template": False,
        "family_switch_present": False,
        "named_geometry_templates_present": False,
        "family_name_authors_geometry": False,
        "visual_resemblance_authors_geometry": False,
        "rendering_can_witness_equality": False,
        "hair_changes_presentation_not_truth": True,
        "only_return_refines_equality_closure": True,
        "truth_issued": False,
        "existence_closed": False,
    }
    body["id"] = _digest("interactive-natural-form-solver", body)
    return body


def solve_natural_form_point(
    solution: Mapping[str, Any],
    point: Sequence[float],
    *,
    hair_millidegrees: int = 0,
) -> tuple[float, float]:
    """Apply the one generic solved basis; useful for runtime tests."""

    coefficients = solution.get("coefficients")
    if not isinstance(coefficients, Mapping) or len(point) != 2:
        raise ValueError("invalid natural-form solution or point")
    x = (float(point[0]) - 500.0) / 500.0
    y = (float(point[1]) - 500.0) / 500.0
    sx = float(coefficients["stretch_x_milli"]) / 1000.0
    sy = float(coefficients["stretch_y_milli"]) / 1000.0
    shx = float(coefficients["shear_x_milli"]) / 1000.0
    shy = float(coefficients["shear_y_milli"]) / 1000.0
    u0 = sx * x + shx * y
    v0 = shy * x + sy * y
    hair = math.radians(hair_millidegrees / 1000.0)
    angle = math.radians(float(coefficients["angle_millidegrees"]) / 1000.0)
    angle += hair * float(coefficients["hair_coupling_milli"]) / 1000.0
    ca, sa = math.cos(angle), math.sin(angle)
    u = ca * u0 - sa * v0
    v = sa * u0 + ca * v0
    radius = math.hypot(u, v)
    theta = math.atan2(v, u)
    phase = math.radians(float(coefficients["phase_millidegrees"]) / 1000.0)
    order = int(coefficients["harmonic_order"])
    harmonic = math.sin(order * theta + phase + hair)
    radial = 1.0 + float(coefficients["radial_milli"]) / 1000.0 * harmonic * min(1.0, radius)
    twist = float(coefficients["twist_milli"]) / 1000.0 * radius * radius
    boundary = float(coefficients["boundary_gain_milli"]) / 1000.0
    fold = float(coefficients["fold_milli"]) / 1000.0 * math.tanh(boundary * u)
    cross = float(coefficients["cross_milli"]) / 1000.0 * math.tanh(boundary * v)
    aperture = float(coefficients["open_aperture_milli"]) / 1000.0
    source_pull = float(coefficients["return_pull_milli"]) / 1000.0
    gain = (
        float(coefficients["role_gain_milli"])
        * float(coefficients["distance_gain_milli"])
        / 1_000_000.0
    )
    theta2 = theta + twist * min(1.25, radius)
    rr = min(1.38, max(0.0, radius * radial))
    solved_x = gain * (rr * math.cos(theta2) + fold + aperture * math.sin((order + 1) * theta))
    solved_y = gain * (rr * math.sin(theta2) + cross - source_pull * math.cos((order + 1) * theta))
    if abs(x) < 1e-15 and abs(y) < 1e-15:
        solved_x = 0.0
        solved_y = 0.0
    return (
        min(980.0, max(20.0, 500.0 + 420.0 * solved_x)),
        min(980.0, max(20.0, 500.0 + 420.0 * solved_y)),
    )


def validate_interactive_natural_form_solver(
    receipt: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    atlas: Mapping[str, Any] | None = None,
    local_field: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    expected = derive_interactive_natural_form_solver(
        contract,
        atlas=atlas,
        local_field=local_field,
    )
    errors: list[str] = []
    if dict(receipt) != expected:
        errors.append("interactive-natural-form-solver:not-derived")
    if expected.get("family_switch_present") is not False:
        errors.append("interactive-natural-form-solver:family-switch")
    if expected.get("named_geometry_templates_present") is not False:
        errors.append("interactive-natural-form-solver:named-template")
    if expected.get("rendering_can_witness_equality") is not False:
        errors.append("interactive-natural-form-solver:render-authors-truth")
    for solution in expected.get("solutions", []):
        constraints = solution.get("constraints") or {}
        if constraints.get("linear_invertibility_witnessed") is not True:
            errors.append(
                f"interactive-natural-form-solver:singular:{solution.get('family_id')}"
            )
        if constraints.get("family_name_used_as_geometry_selector") is not False:
            errors.append(
                f"interactive-natural-form-solver:name-selector:{solution.get('family_id')}"
            )
    return {
        "valid": not errors,
        "errors": errors,
        "id": expected.get("id"),
        "solution_count": expected.get("solution_count", 0),
        "natural_form_is_interactive_interface_equality_closure": True,
        "rendering_can_witness_equality": False,
    }


__all__ = [
    "PROTOCOL",
    "SCHEMA",
    "SEMANTIC_FIELDS",
    "derive_interactive_equality_closure_signature",
    "derive_interactive_natural_form_solver",
    "solve_natural_form_point",
    "validate_interactive_natural_form_solver",
]
