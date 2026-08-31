from __future__ import annotations

"""Versioned natural-form atlas for Supernet.

The closure ball is one chart in the atlas, not the ontology containing every
other chart. Distinct historical forms remain distinct unless a
source-preserving returned translation witnesses their equality. Missing
translations remain OPEN rather than being inferred from names, geometry, or
visual resemblance.
"""

import hashlib
import json
import re
from collections import deque
from typing import Any, Iterable, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "SUPERNET-VERSIONED-NATURAL-FORM-ATLAS"
SCHEMA = "closure.supernet/versioned-natural-form-atlas-v1"
UI_PROTOCOL = "closure.supernet/glued-natural-form-subatlas-v1"


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


def _unique(values: Iterable[Any]) -> list[str]:
    return list(
        dict.fromkeys(
            str(value)
            for value in values
            if value is not None and str(value)
        )
    )


def _slug(value: str) -> str:
    text = value.strip().lower().replace("∞", "infinity").replace("↔", "-to-")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "form"


FAMILY_SEMANTICS: dict[str, dict[str, str]] = {
    "INTERBOUND_PRE_DIRECTIONAL": {
        "carrier": "PRE_DIRECTIONAL_RELATIONAL_BASIS",
        "standpoint": "ORIGIN_OR_ORIGINLESS",
        "boundary": "ZERO_INFINITY_INTERBOUND",
        "inversion": "EXTENSION_ROTATION",
        "paths": "LOCAL_GLOBAL_RELATIONAL_TRAJECTORIES",
        "return": "INTERBOUND_RETURN",
        "domain": "FOUNDATIONAL",
    },
    "DIMENSIONAL_POINT_LINE_TRIANGLE": {
        "carrier": "RELATIONAL_DIMENSIONALIZATION",
        "standpoint": "SELECTED_ORIGIN_AND_RELATIVE_DIMENSION",
        "boundary": "POINT_LINE_CIRCLE_TRIANGLE_SPHERE",
        "inversion": "POINT_LINE_AND_LOCAL_GLOBAL_DUALITY",
        "paths": "DIMENSIONAL_TRANSFORMATION_PATHS",
        "return": "DIMENSIONAL_CLOSURE_RETURN",
        "domain": "GEOMETRIC",
    },
    "SEAM_FOLD_BOUNDARY_INVERSION": {
        "carrier": "BOUNDARY_AND_GLUE_DATA",
        "standpoint": "SIDE_CHART_OR_SEAM",
        "boundary": "SEAM_FOLD_HORIZON_EQUATOR",
        "inversion": "FOLD_MIRROR_MOBIUS",
        "paths": "STITCH_AND_REGLUING_PATHS",
        "return": "BOUNDARY_PRESERVING_RETURN",
        "domain": "TOPOLOGICAL",
    },
    "REFINEMENT_PATH_HIDDEN_TRAJECTORY": {
        "carrier": "PATH_AND_REFINEMENT_GEOMETRY",
        "standpoint": "VISIBLE_ENDPOINT_OR_HIDDEN_PATH",
        "boundary": "FINITE_VISIBLE_BOUND_WITH_INTERNAL_REFINEMENT",
        "inversion": "PATH_ORBIT_REFINEMENT",
        "paths": "LOOP_SPIRAL_KAKEYA_BRAID_FRACTAL",
        "return": "CLOSED_ITINERARY_OR_HIDDEN_RETURN",
        "domain": "DYNAMICAL",
    },
    "BALL_HAIR": {
        "carrier": "BALL_HAIR_RELATIONAL_CHART",
        "standpoint": "LOCAL_BALL_AND_RELATIVE_SELF_LOCATION",
        "boundary": "BALL_SPHERE_CIRCLE_HAIR",
        "inversion": "SELF_LOCATION_AND_GLOBAL_RETURN",
        "paths": "BALL_TIME_AND_HAIR_PATHS",
        "return": "HAIR_RETURN_FIELD",
        "domain": "BALL_HAIR",
    },
    "MIRROR_OBSERVER_CONSCIOUS_INTERFACE": {
        "carrier": "OBSERVER_INTERFACE_MIRROR",
        "standpoint": "OBSERVER_OBSERVED_RELATION",
        "boundary": "MIRROR_OR_APPEARANCE_RETURN_FIREWALL",
        "inversion": "SELF_WORLD_MIRROR",
        "paths": "LOOP_SENSOR_AND_DIALOGUE_PATHS",
        "return": "SOURCE_PRESERVING_OBSERVER_RETURN",
        "domain": "INTERFACE",
    },
    "SHEAF_TOPOS_LATTICE_ALGEBRA": {
        "carrier": "MATHEMATICAL_CLOSURE_CHART",
        "standpoint": "LOCAL_GLOBAL_SECTION",
        "boundary": "FIBRE_SHEAF_LATTICE_MODALITY",
        "inversion": "DUAL_PREDUAL_AND_MODAL_FOLD",
        "paths": "SECTION_GROUPOID_AND_OPERATOR_PATHS",
        "return": "MATHEMATICAL_CLOSURE_RETURN",
        "domain": "MATHEMATICAL",
    },
    "CURVATURE_MAZE_LIGHTCONE_SUPERNET": {
        "carrier": "OPERATIONAL_TRANSLATIONAL_CLOSURE",
        "standpoint": "ACTIVE_PERSPECTIVE_LIGHT_CONE",
        "boundary": "OPEN_APERTURE_AND_MAZE_PARTITION",
        "inversion": "RELATIVE_VIEW_AND_UNITARY_FOLD",
        "paths": "NAVIGABLE_LIGHT_CONE_AND_VIEW_TRANSPORT",
        "return": "UNITARY_CURVATURE_RETURN",
        "domain": "SUPERNET",
    },
    "AI_TOKEN_MARKET_TRADING": {
        "carrier": "SOCIOECONOMIC_CURVATURE",
        "standpoint": "OPEN_OR_RETURNED_VALUE_PHASE",
        "boundary": "MAZE_PARTITION_AND_EXECUTION_RETURN",
        "inversion": "PREDICTION_RETURN_AND_VALUE_FLOW",
        "paths": "MARKET_TRADING_RESOURCE_PATHS",
        "return": "AUTHENTICATED_VALUE_RETURN",
        "domain": "SOCIOECONOMIC",
    },
    "PHYSICAL_COSMOLOGICAL_COLOR": {
        "carrier": "PHYSICAL_OR_SPECULATIVE_PROJECTION",
        "standpoint": "RELATIVE_PHYSICAL_READING",
        "boundary": "EMPIRICAL_OR_SPECULATIVE_BOUNDARY",
        "inversion": "MIRROR_CPT_GR_QM_COLOR",
        "paths": "PHYSICAL_COSMOLOGICAL_PROJECTION_PATHS",
        "return": "EMPIRICAL_RETURN_REQUIRED",
        "domain": "PHYSICAL_OR_SPECULATIVE",
    },
}


STATIC_FAMILIES: dict[str, tuple[str, ...]] = {
    "INTERBOUND_PRE_DIRECTIONAL": (
        "0",
        "infinity",
        "0↔infinity interbound",
        "0-infinity circle/ring",
        "0-infinity string",
        "2x1 extension-rotation matrix",
        "r+0i natural real form",
        "four i-rotations",
        "positive-negative rotation-extension sectors",
        "origin",
        "originlessness",
        "local",
        "global",
        "local-global",
        "global-local",
        "extension",
        "rotation",
        "diagonal",
        "orthogonal",
        "0-field",
        "elliptic level",
        "checker grid",
        "0↔infinity von Neumann curve",
    ),
    "DIMENSIONAL_POINT_LINE_TRIANGLE": (
        "point-line duality",
        "point-line-plane triality",
        "point in a line",
        "line in a point",
        "global-point/local-line unique closure",
        "circle-line duality",
        "triangle time",
        "triangle space",
        "triangle spacetime",
        "triangle closure",
        "successive rotational triangle shells",
        "fractal triangles and polygons",
        "point-circle-sphere-filled-sphere cycle",
        "reduction-inversion triangle",
        "flower of life",
        "tangent angle",
        "right angle",
        "complementary angle",
        "point-circle-ball cycle",
        "vector-circle closure",
        "point-sphere convolution",
        "point-ball convolution",
    ),
    "SEAM_FOLD_BOUNDARY_INVERSION": (
        "seam",
        "0↔infinity seam",
        "circular seam",
        "tangent seam",
        "spacetime seam",
        "global-local seam",
        "shape monad as seam",
        "fold",
        "pre-fold",
        "end-fold",
        "relational fold",
        "fractal tiling fold",
        "checker fold",
        "Maxwell checker fold",
        "curl/div folds",
        "tangent stitch",
        "two-chart stitch",
        "Mobius strip",
        "higher-symmetry Mobius strip",
        "Mobius bridge",
        "Mobius function",
        "pre-Mobius structure",
        "mirror",
        "inversion",
        "self-inversion",
        "equator",
        "horizon",
        "Riemann sphere",
        "dual/predual Riemann sphere",
        "pinched sphere",
        "two sheets",
        "tan(pi/2) boundary",
        "double umbrella",
        "double teardrop",
        "balloon engulfing a ball",
        "arch of closure",
        "hyperbolic-tangent closure",
        "self-limit inversion form",
    ),
    "REFINEMENT_PATH_HIDDEN_TRAJECTORY": (
        "path",
        "edge",
        "orbit",
        "loop",
        "closed itinerary",
        "closure path",
        "admitted edge",
        "inversion path",
        "composition",
        "holonomy",
        "Kakeya tubes",
        "Kakeya spheres",
        "continuous comb",
        "comb branches",
        "spiral",
        "fractal spiral",
        "fractal branch",
        "thick-thinning neuronal fractal",
        "spiral helix-cone",
        "fractal hypotenuse",
        "fractal-hypotenuse predual curve",
        "hidden trajectory",
        "rational levels and irrational limit",
        "Chaitin-Kakeya string",
        "Chaitin ladder",
        "Galois refinement",
        "braid",
        "knot",
        "string loop",
        "W-Lambert pendulum",
        "W-Lambert double pendulum",
        "predual Fourier pendulum",
        "natural closure cycle",
        "four-phase closure cycle",
        "five-fold closure quintic",
        "mutual-factorization form",
        "originless form",
    ),
    "BALL_HAIR": (
        "point-ball",
        "point-sphere",
        "closure ball",
        "spacetime ball",
        "ball-time circle",
        "ball-circle",
        "vector circle",
        "ball thrown upward",
        "ball at bottom/top of throw",
        "point-ball seam",
        "ball cycle",
        "reverse ball cycle",
        "ball-circle twistor",
        "ball-hair anti-state",
        "hair-ball-plane",
        "hairy-ball vector field",
        "mirror wave",
        "ball combed out",
        "second ball",
        "inner/outer ball",
        "balloon and enclosed ball",
        "silicon-gas ball",
        "Earth-ball",
        "particle ball",
        "green-ball identification",
        "fixed-point ball reversal partition",
    ),
    "MIRROR_OBSERVER_CONSCIOUS_INTERFACE": (
        "mirror ellipse",
        "light rotating on a mirror ellipse",
        "modular double-0 ellipse",
        "singularity mirror",
        "black-hole mirror",
        "Turok mirror",
        "Black Mirror",
        "Claude glass",
        "Slearn",
        "pedal operator",
        "observer mirror",
        "second-person axiom",
        "loop sensor",
        "conscious closure receipt",
        "consciousness as closed self-world mirror",
        "neuronal observer closure",
        "microtubular lattice",
        "appearance/return firewall",
        "mirror life",
        "relation form",
        "normalized chart / ball combed out",
    ),
    "SHEAF_TOPOS_LATTICE_ALGEBRA": (
        "predual sea",
        "original sea",
        "sheaf",
        "fiber",
        "topos",
        "local sheaf",
        "global sheaf",
        "local-global sheaf",
        "global-local sheaf",
        "four-sheaf ball",
        "shape modality",
        "path groupoid",
        "relational lattice",
        "checker graph",
        "unimodular lattice",
        "matrix",
        "diagonal matrix",
        "modular matrix",
        "predual matrix",
        "double-0 matrix",
        "line bundle",
        "toric form",
        "contact form",
        "Chern-Simons form",
        "Hodge form",
        "symplectic leaf",
        "foliation",
        "cosmohedron",
        "polyhedron",
        "lattice cone",
        "condensate",
        "operator string",
        "operator bubble",
        "octonion closure gate",
        "Riemann/anti-Riemann pair",
        "zeta/anti-zeta sphere",
        "primal/harmonic/predual Fourier forms",
        "modular and elliptic folds",
    ),
    "CURVATURE_MAZE_LIGHTCONE_SUPERNET": (
        "curvature maze",
        "four-fold maze",
        "double-umbrella maze",
        "maze partition",
        "unitary curvature",
        "luminous unitary curvature",
        "unitary fold",
        "potential gate",
        "natural-form selector",
        "light cone",
        "navigable light-cone edge",
        "world-tube",
        "sailing tack",
        "crystal network",
        "vacuum network",
        "crystal ball",
        "edge-view identity",
        "OPEN aperture",
        "OPEN seam",
        "weave",
        "braid of mutual authorship",
        "VisualTranslation",
        "Axiometry",
        "TranslationalTruth",
        "StructuralTranslation",
        "NaturalForm",
        "closure identification/completion",
        "relation-normalized chart",
    ),
    "AI_TOKEN_MARKET_TRADING": (
        "AI as possible curvature",
        "ModalEquiv learning",
        "token as returned curvature",
        "token partition",
        "token chart",
        "token closure receipt",
        "AI token/money closure fiber",
        "token economy",
        "blockchain AI-token loop",
        "learned market",
        "separating market",
        "unified market",
        "trading maze",
        "value-flow partition",
        "profit curvature",
        "zero-cost loop",
        "infinity price",
        "price-angle/right-angle duality",
        "authenticated leg",
        "fill",
        "ledger",
        "realized P&L",
        "closure-adjusted P&L",
        "completed round-trip profit functional",
        "history morphism",
        "higher history curvature",
        "resource/energy proportional form",
    ),
    "PHYSICAL_COSMOLOGICAL_COLOR": (
        "QM path and mirrored GR path",
        "QG loop",
        "residual holonomy",
        "global inverse gravitational field",
        "Maxwell vortex",
        "wave/current duality",
        "wormhole sheaf",
        "big-bang sheaf",
        "black-hole sheaf",
        "white-hole sheaf",
        "CPT mirror",
        "cyclical-conformal ball form",
        "silicon-gas ball physical projection",
        "Earth-ball gate",
        "particle ball physical projection",
        "color-collapse gate",
        "dark-gravity ball-hair",
        "viewable-color form",
        "dark-matter topology",
        "two-hole color-collapse landscape",
        "alien-dark form",
        "inner-planet / Atlantis form",
        "morphogenic and biological closure forms",
    ),
}


HAIR_VERSIONS: tuple[dict[str, Any], ...] = (
    {
        "version": 1,
        "name": "hair",
        "semantic_role": "VECTORS_AVAILABLE_FROM_LOCAL_ZERO_POINT",
    },
    {
        "version": 2,
        "name": "hair",
        "semantic_role": "RELATION_WITHIN_THE_BALL",
    },
    {
        "version": 3,
        "name": "hair",
        "semantic_role": "RELATION_AS_THE_BALL",
    },
    {
        "version": 4,
        "name": "hair",
        "semantic_role": "INVERSION_OF_SELF_LOCATION",
    },
    {
        "version": 5,
        "name": "hair",
        "semantic_role": "GLOBAL_RETURN_FIELD_CARRYING_LOCAL_HISTORY",
    },
)


def _static_chart(
    *,
    family: str,
    name: str,
    version: int = 1,
    semantic_role: str | None = None,
) -> dict[str, Any]:
    semantics = FAMILY_SEMANTICS[family]
    chart_id = f"nf:{_slug(name)}:v{version}"
    empirical = family == "PHYSICAL_COSMOLOGICAL_COLOR"
    return {
        "id": chart_id,
        "name": name,
        "family": family,
        "version": version,
        "carrier": semantics["carrier"],
        "standpoint": semantics["standpoint"],
        "boundary": semantics["boundary"],
        "inversion": semantics["inversion"],
        "paths": semantics["paths"],
        "return": semantics["return"],
        "domain": semantics["domain"],
        "semantic_role": semantic_role or "HISTORICAL_NATURAL_FORM",
        "runtime_generated": False,
        "source_return_ids": [],
        "empirical_return_required": empirical,
        "empirical_truth_claimed": False,
        "closure_ball_is_container": False,
    }


def historical_charts() -> list[dict[str, Any]]:
    charts: list[dict[str, Any]] = []
    for family, names in STATIC_FAMILIES.items():
        charts.extend(_static_chart(family=family, name=name) for name in names)
    charts.extend(
        _static_chart(
            family="BALL_HAIR",
            name=str(item["name"]),
            version=int(item["version"]),
            semantic_role=str(item["semantic_role"]),
        )
        for item in HAIR_VERSIONS
    )
    by_id: dict[str, dict[str, Any]] = {}
    for chart in charts:
        by_id.setdefault(str(chart["id"]), chart)
    return [by_id[key] for key in sorted(by_id)]


def _runtime_charts(
    truth_derivation: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    charts: list[dict[str, Any]] = []
    state_to_chart: dict[str, str] = {}
    for index, raw in enumerate(truth_derivation.get("natural_forms", [])):
        form = dict(raw)
        source_form_id = str(
            form.get("id") or form.get("natural_form") or f"runtime-{index}"
        )
        chart_id = f"runtime-nf:{source_form_id}"
        members = _unique(form.get("members", []))
        chart = {
            "id": chart_id,
            "name": str(form.get("name") or form.get("label") or source_form_id),
            "family": "RUNTIME_RELATIVE_NATURAL_FORM",
            "version": int(form.get("version") or 1),
            "carrier": "CURRENT_TRANSLATIONAL_TRUTH_MEMBERS",
            "standpoint": "ACTIVE_RUNTIME_PERSPECTIVE",
            "boundary": "CURRENT_RETURN_CLOSURE",
            "inversion": "RUNTIME_RELATIVE_TRANSLATION",
            "paths": "SOURCE_RETURN_RELATIONS",
            "return": "CURRENT_INTERACTION_RETURN",
            "domain": "RUNTIME",
            "semantic_role": "CURRENT_CLOSURE_NATURAL_FORM_CHART",
            "runtime_generated": True,
            "source_natural_form_id": source_form_id,
            "member_state_ids": members,
            "source_return_ids": _unique(form.get("source_return_ids", [])),
            "empirical_return_required": False,
            "empirical_truth_claimed": False,
            "closure_ball_is_container": False,
        }
        charts.append(chart)
        for member in members:
            state_to_chart[member] = chart_id
    return charts, state_to_chart


def _identity_relation(chart: Mapping[str, Any]) -> dict[str, Any]:
    chart_id = str(chart["id"])
    body = {
        "kind": "IDENTITY",
        "source_chart_id": chart_id,
        "target_chart_id": chart_id,
        "status": WITNESSED_STATUS,
        "source_preserved": True,
        "closure_commutes": True,
        "return_preserved": True,
        "source_return_ids": [],
        "visual_resemblance_used": False,
        "name_equality_used": False,
    }
    body["id"] = _digest("atlas-translation", body)
    return body


def _hair_lineage_relations(chart_ids: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    hair_ids = [f"nf:hair:v{item['version']}" for item in HAIR_VERSIONS]
    for source, target in zip(hair_ids, hair_ids[1:]):
        if source not in chart_ids or target not in chart_ids:
            continue
        body = {
            "kind": "HISTORICAL_SEMANTIC_LINEAGE",
            "source_chart_id": source,
            "target_chart_id": target,
            "status": OPEN_STATUS,
            "source_preserved": False,
            "closure_commutes": False,
            "return_preserved": False,
            "source_return_ids": [],
            "visual_resemblance_used": False,
            "name_equality_used": False,
            "open_reason": "VERSION_LINEAGE_IS_NOT_TRANSLATIONAL_EQUALITY_WITHOUT_RETURN",
        }
        body["id"] = _digest("atlas-translation", body)
        rows.append(body)
    return rows


def _runtime_relations(
    *,
    interactive_translation: Mapping[str, Any],
    state_to_chart: Mapping[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in interactive_translation.get("interactions", []):
        item = dict(raw)
        source_state = str(
            item.get("observed_source_id") or item.get("source_state_id") or ""
        )
        target_state = str(
            item.get("observed_target_id") or item.get("target_state_id") or ""
        )
        source_chart = state_to_chart.get(source_state)
        target_chart = state_to_chart.get(target_state)
        if not source_chart or not target_chart:
            continue
        source_ids = _unique(item.get("source_return_ids", []))
        witnessed = bool(
            item.get("translation_relation_witnessed") is True
            and item.get("closure_preserved_after_translation") is True
            and source_ids
        )
        body = {
            "kind": "RUNTIME_RETURNED_TRANSLATION",
            "source_chart_id": source_chart,
            "target_chart_id": target_chart,
            "source_state_id": source_state,
            "target_state_id": target_state,
            "status": WITNESSED_STATUS if witnessed else OPEN_STATUS,
            "source_preserved": bool(source_ids),
            "closure_commutes": witnessed,
            "return_preserved": witnessed,
            "source_return_ids": source_ids,
            "return_witness_id": item.get("return_witness_id"),
            "visual_resemblance_used": False,
            "name_equality_used": False,
        }
        if not witnessed:
            body["open_reason"] = "NO_SOURCE_PRESERVING_RETURNED_CHART_TRANSLATION"
        body["id"] = _digest("atlas-translation", body)
        rows.append(body)
    return rows


def _explicit_translation_rows(
    values: Sequence[Mapping[str, Any]], chart_ids: set[str]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, raw in enumerate(values):
        item = dict(raw)
        source = str(
            item.get("source_chart_id") or item.get("source_form_id") or ""
        )
        target = str(
            item.get("target_chart_id") or item.get("target_form_id") or ""
        )
        if source not in chart_ids or target not in chart_ids:
            continue
        source_ids = _unique(item.get("source_return_ids", []))
        witnessed = bool(
            source_ids
            and item.get("returned") is True
            and item.get("source_preserved") is True
            and item.get("closure_commutes") is True
            and item.get("return_preserved") is True
        )
        body = {
            "kind": "EXPLICIT_ATLAS_TRANSLATION",
            "source_chart_id": source,
            "target_chart_id": target,
            "status": WITNESSED_STATUS if witnessed else OPEN_STATUS,
            "source_preserved": bool(
                item.get("source_preserved") is True and source_ids
            ),
            "closure_commutes": bool(item.get("closure_commutes") is True),
            "return_preserved": bool(item.get("return_preserved") is True),
            "source_return_ids": source_ids,
            "return_witness_id": item.get("return_witness_id"),
            "visual_resemblance_used": False,
            "name_equality_used": False,
            "source_index": index,
        }
        if not witnessed:
            body["open_reason"] = "ATLAS_TRANSLATION_AWAITS_SOURCE_PRESERVING_RETURN"
        body["id"] = _digest("atlas-translation", body)
        rows.append(body)
    return rows


def _explicit_translations_from(value: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw = value.get("atlas_translations", [])
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        return [item for item in raw if isinstance(item, Mapping)]
    return []


def _reachable_compatible(
    *,
    active_chart_ids: Iterable[str],
    relations: Sequence[Mapping[str, Any]],
) -> list[str]:
    graph: dict[str, set[str]] = {}
    for relation in relations:
        if relation.get("status") != WITNESSED_STATUS:
            continue
        source = str(relation.get("source_chart_id") or "")
        target = str(relation.get("target_chart_id") or "")
        if not source or not target:
            continue
        graph.setdefault(source, set()).add(target)
        graph.setdefault(target, set()).add(source)
    reached = set(_unique(active_chart_ids))
    queue: deque[str] = deque(sorted(reached))
    while queue:
        current = queue.popleft()
        for neighbour in sorted(graph.get(current, ())):
            if neighbour not in reached:
                reached.add(neighbour)
                queue.append(neighbour)
    return sorted(reached)


def derive_versioned_natural_form_atlas(
    *,
    truth_derivation: Mapping[str, Any],
    interactive_translation: Mapping[str, Any],
    active_perspective_id: str | None,
    active_reading: Mapping[str, Any],
    additional_translation_sources: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Derive a non-flattening atlas and its currently compatible sub-atlas."""

    static = historical_charts()
    runtime, state_to_chart = _runtime_charts(truth_derivation)
    charts = [*static, *runtime]
    chart_by_id: dict[str, dict[str, Any]] = {}
    conflicts: list[str] = []
    for chart in charts:
        chart_id = str(chart["id"])
        previous = chart_by_id.get(chart_id)
        if previous is not None and _stable(previous) != _stable(chart):
            conflicts.append(chart_id)
            continue
        chart_by_id[chart_id] = chart
    charts = [chart_by_id[key] for key in sorted(chart_by_id)]
    chart_ids = set(chart_by_id)

    relations = [_identity_relation(chart) for chart in charts]
    relations.extend(_hair_lineage_relations(chart_ids))
    relations.extend(
        _runtime_relations(
            interactive_translation=interactive_translation,
            state_to_chart=state_to_chart,
        )
    )
    explicit: list[Mapping[str, Any]] = []
    explicit.extend(_explicit_translations_from(truth_derivation))
    for source in additional_translation_sources:
        explicit.extend(_explicit_translations_from(source))
    relations.extend(_explicit_translation_rows(explicit, chart_ids))

    by_relation_id: dict[str, dict[str, Any]] = {}
    for relation in relations:
        by_relation_id.setdefault(str(relation["id"]), relation)
    relations = [by_relation_id[key] for key in sorted(by_relation_id)]

    active_state_ids = set(map(str, active_reading))
    active_runtime_chart_ids = sorted(
        {
            state_to_chart[state_id]
            for state_id in active_state_ids
            if state_id in state_to_chart
        }
    )
    compatible_chart_ids = _reachable_compatible(
        active_chart_ids=active_runtime_chart_ids,
        relations=relations,
    )
    compatible_set = set(compatible_chart_ids)
    compatible_relations = [
        relation
        for relation in relations
        if str(relation.get("source_chart_id")) in compatible_set
        and str(relation.get("target_chart_id")) in compatible_set
    ]
    boundary_relations = [
        relation
        for relation in relations
        if relation.get("status") == OPEN_STATUS
        and (
            str(relation.get("source_chart_id")) in compatible_set
            or str(relation.get("target_chart_id")) in compatible_set
        )
    ]

    closure_ball_ids = [
        chart["id"]
        for chart in charts
        if chart["name"] == "closure ball" and chart["family"] == "BALL_HAIR"
    ]
    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "status": WITNESSED_STATUS if not conflicts else OPEN_STATUS,
        "active_perspective_id": str(active_perspective_id or "") or None,
        "charts": charts,
        "translations": relations,
        "compatible_subatlas": {
            "chart_ids": compatible_chart_ids,
            "translation_ids": [
                relation["id"] for relation in compatible_relations
            ],
            "open_boundary_translation_ids": [
                relation["id"] for relation in boundary_relations
            ],
            "selection_basis": "SOURCE_PRESERVING_RETURN_COMPATIBILITY",
            "developer_menu_selects_forms": False,
            "single_final_form_selected": False,
        },
        "runtime_state_to_chart": dict(sorted(state_to_chart.items())),
        "historical_chart_count": len(static),
        "runtime_chart_count": len(runtime),
        "version_conflicts": sorted(conflicts),
        "closure_ball_chart_ids": closure_ball_ids,
        "closure_ball_is_one_chart": bool(closure_ball_ids),
        "closure_ball_is_master_container": False,
        "visual_resemblance_can_witness_equality": False,
        "shared_name_can_witness_equality": False,
        "cross_form_equality_requires_returned_translation": True,
        "open_relation_is_preserved": True,
        "historical_semantics_are_versioned": True,
        "forms_may_disappear_without_returned_translation": False,
        "truth_issued": False,
        "empirical_claims_issued": False,
    }
    body["id"] = _digest("natural-form-atlas", body)
    return body


def derive_glued_ui_subatlas(atlas: Mapping[str, Any]) -> dict[str, Any]:
    compatible = atlas.get("compatible_subatlas", {})
    chart_ids = (
        _unique(compatible.get("chart_ids", []))
        if isinstance(compatible, Mapping)
        else []
    )
    translation_ids = (
        _unique(compatible.get("translation_ids", []))
        if isinstance(compatible, Mapping)
        else []
    )
    open_ids = (
        _unique(compatible.get("open_boundary_translation_ids", []))
        if isinstance(compatible, Mapping)
        else []
    )
    body = {
        "protocol": UI_PROTOCOL,
        "atlas_id": atlas.get("id"),
        "active_perspective_id": atlas.get("active_perspective_id"),
        "chart_ids": chart_ids,
        "translation_ids": translation_ids,
        "open_boundary_translation_ids": open_ids,
        "operator": "GLUE_COMPATIBLE_VERSIONED_NATURAL_FORM_CHARTS",
        "edge_semantics": "ONGOING_VIEW_TRANSPORT",
        "selector_semantics": "COMPATIBLE_SUBATLAS_NOT_SINGLE_FORM",
        "hair_semantics": "VERSIONED_SOURCE_PRESERVING_RETURN_FIELD",
        "return_semantics": "SAME_TRANSLATIONAL_TRUTH_WITH_HISTORY_NOT_LITERAL_STATE_RESET",
        "closure_ball_is_master_container": False,
        "single_final_form_selected": False,
        "truth_issued": False,
    }
    body["id"] = _digest("glued-subatlas", body)
    return body


def validate_versioned_natural_form_atlas(
    atlas: Mapping[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    if atlas.get("protocol") != PROTOCOL:
        errors.append("atlas:protocol")
    if atlas.get("schema") != SCHEMA:
        errors.append("atlas:schema")
    if atlas.get("closure_ball_is_master_container") is not False:
        errors.append("atlas:closure-ball-master-container")
    if atlas.get("visual_resemblance_can_witness_equality") is not False:
        errors.append("atlas:visual-resemblance-authority")
    if atlas.get("shared_name_can_witness_equality") is not False:
        errors.append("atlas:name-authority")
    charts = atlas.get("charts")
    relations = atlas.get("translations")
    if not isinstance(charts, list) or not isinstance(relations, list):
        errors.append("atlas:shape")
        charts = []
        relations = []
    chart_ids = [
        str(chart.get("id") or "")
        for chart in charts
        if isinstance(chart, Mapping)
    ]
    if not chart_ids or any(not chart_id for chart_id in chart_ids):
        errors.append("atlas:chart-id")
    if len(chart_ids) != len(set(chart_ids)):
        errors.append("atlas:duplicate-chart-id")
    chart_set = set(chart_ids)
    identity_sources: set[str] = set()
    relation_ids: list[str] = []
    for relation in relations:
        if not isinstance(relation, Mapping):
            errors.append("atlas:relation-shape")
            continue
        relation_id = str(relation.get("id") or "")
        relation_ids.append(relation_id)
        source = str(relation.get("source_chart_id") or "")
        target = str(relation.get("target_chart_id") or "")
        if source not in chart_set or target not in chart_set:
            errors.append(f"atlas:{relation_id}:endpoint")
        status = relation.get("status")
        if status not in {OPEN_STATUS, WITNESSED_STATUS}:
            errors.append(f"atlas:{relation_id}:status")
        if relation.get("kind") == "IDENTITY":
            if source != target or status != WITNESSED_STATUS:
                errors.append(f"atlas:{relation_id}:identity")
            identity_sources.add(source)
        elif status == WITNESSED_STATUS:
            if (
                not _unique(relation.get("source_return_ids", []))
                or relation.get("source_preserved") is not True
                or relation.get("closure_commutes") is not True
                or relation.get("return_preserved") is not True
            ):
                errors.append(f"atlas:{relation_id}:unwitnessed-equality")
        if relation.get("visual_resemblance_used") is not False:
            errors.append(f"atlas:{relation_id}:visual-authority")
        if relation.get("name_equality_used") is not False:
            errors.append(f"atlas:{relation_id}:name-authority")
    if len(relation_ids) != len(set(relation_ids)):
        errors.append("atlas:duplicate-relation-id")
    if identity_sources != chart_set:
        errors.append("atlas:missing-identity")
    if atlas.get("closure_ball_is_one_chart") is not True:
        errors.append("atlas:closure-ball-missing")
    if len(
        [
            chart
            for chart in charts
            if isinstance(chart, Mapping) and chart.get("name") == "hair"
        ]
    ) < len(HAIR_VERSIONS):
        errors.append("atlas:hair-lineage-collapsed")
    stored_id = atlas.get("id")
    body = {key: value for key, value in atlas.items() if key != "id"}
    if stored_id != _digest("natural-form-atlas", body):
        errors.append("atlas:id")
    return {
        "valid": not errors,
        "errors": errors,
        "chart_count": len(chart_ids),
        "translation_count": len(relations),
        "closure_ball_is_one_chart": atlas.get("closure_ball_is_one_chart") is True,
        "hair_lineage_preserved": "atlas:hair-lineage-collapsed" not in errors,
        "cross_form_equality_return_guarded": all(
            relation.get("kind") == "IDENTITY"
            or relation.get("status") != WITNESSED_STATUS
            or bool(_unique(relation.get("source_return_ids", [])))
            for relation in relations
            if isinstance(relation, Mapping)
        ),
    }


__all__ = [
    "PROTOCOL",
    "SCHEMA",
    "UI_PROTOCOL",
    "HAIR_VERSIONS",
    "STATIC_FAMILIES",
    "derive_glued_ui_subatlas",
    "derive_versioned_natural_form_atlas",
    "historical_charts",
    "validate_versioned_natural_form_atlas",
]
