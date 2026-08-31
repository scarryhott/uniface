from __future__ import annotations

"""Proof-indexed formal witness registry for the versioned Supernet atlas.

The runtime does not re-prove Lean.  This registry records the existing
machine-checked modules and the natural-form charts to which their proved
statements apply.  Merely appearing in a proof bundle never collapses two
historical forms into one atlas equality: a proof may certify an invariant,
projection, naturality square, or domain theorem without asserting cross-form
identity.
"""

import hashlib
import json
from typing import Any, Mapping

PROTOCOL = "SUPERNET-FORMAL-PROOF-INDEX"
SCHEMA = "closure.supernet/formal-proof-index-v1"


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


# These names are restricted to theorem names or module-level claims already
# present in the formal/runtime record.  `machine_checked_reported` records the
# formal corpus status; `source_verified_by_runtime` remains false because this
# Python runtime does not load or re-run the Lean kernel.
PROOF_BUNDLES: tuple[dict[str, Any], ...] = (
    {
        "module": "NRRF849NaturalFormPredictionProfitCurvatureAdversaryCostsRelativeClosureTranslationalHistory",
        "theorem_names": (
            "profit_translate",
            "naturalForm_predicts_profit",
            "naturalForm_iff_profit_prediction",
        ),
        "chart_names": (
            "NaturalForm",
            "profit curvature",
            "completed round-trip profit functional",
            "trading maze",
        ),
        "proof_kind": "CLOSED_ITINERARY_PREDICTION_INVARIANT",
        "proved_scope": "Natural-form equality is exactly round-trip profit prediction in the trading chart.",
    },
    {
        "module": "NRRF858ConsciousNatureRelativeAxiomsProofsUnderstandingClosuresTranslationalTruthContinuingExistence",
        "theorem_names": (
            "no_absolute_axioms",
            "axiomsOf_eq_iff_translational",
            "conscious_proves_composite",
            "mem_understanding_iff",
            "understanding_eq_iff_translational",
            "conscious_continues_existence",
        ),
        "chart_names": (
            "conscious closure receipt",
            "consciousness as closed self-world mirror",
            "TranslationalTruth",
            "relation-normalized chart",
        ),
        "proof_kind": "RELATIVE_AXIOM_PROOF_UNDERSTANDING_CLOSURE",
        "proved_scope": "Relative axioms, proof and understanding factor through translational closure without closing existence.",
    },
    {
        "module": "NRRF859ConsciousSupernetInteractiveProjectionBridge",
        "theorem_names": (),
        "chart_names": (
            "VisualTranslation",
            "Black Mirror",
            "relation-normalized chart",
        ),
        "proof_kind": "FORMAL_RUNTIME_PROJECTION_BRIDGE",
        "proved_scope": "Formal closure is bridged to a relative interactive projection rather than an absolute UI ontology.",
    },
    {
        "module": "NRRF861ConsciousnessOperatorOfTranslationalTruthDigitalRuntimeInteractiveInterface",
        "theorem_names": ("consciousness_derived",),
        "chart_names": (
            "observer mirror",
            "conscious closure receipt",
            "consciousness as closed self-world mirror",
            "relation-normalized chart",
            "TranslationalTruth",
        ),
        "proof_kind": "NORMALIZED_OBSERVER_CLOSURE_OPERATOR",
        "proved_scope": "The observer-relative normalized chart is uniquely derived from translational truth and is hair-blind.",
    },
    {
        "module": "NRRF862InteractiveTranslationRelativeUnityOfNaturalFormsArgumentFlowPolicePerspectiveTruthNoClosedExistenceDialecticContinuation",
        "theorem_names": (
            "replay_eq_hairAct_accum",
            "translationalTruth_eq_dialogues",
            "naturalForms_eq_iff_obsEquiv",
            "coherent_iff_single_chart",
            "police_eq_truth",
            "police_and_perspective_translate_equally_into_truth",
            "isPolice_truthVerdict",
            "argument_never_closes_existence",
            "argument_compatible_with_existence",
            "chain_open",
            "interactive_translation_relative_unity_of_natural_forms",
            "exists_live_argument",
        ),
        "chart_names": (
            "Black Mirror",
            "Slearn",
            "loop sensor",
            "NaturalForm",
            "TranslationalTruth",
            "OPEN seam",
            "natural-form selector",
        ),
        "proof_kind": "INTERACTIVE_DIALOGUE_TRANSLATIONAL_CONTINUATION",
        "proved_scope": "Dialogue, perspective flow and natural forms share translational truth while existence remains OPEN.",
    },
    {
        "module": "NRRF865UniversalClosureOfEnergyResourceUnity",
        "theorem_names": (),
        "chart_names": ("resource/energy proportional form",),
        "proof_kind": "ENERGY_RESOURCE_TRANSLATIONAL_UNITY",
        "proved_scope": "Resource and energy charts are unified exactly at the proportional closed-itinerary relation.",
    },
    {
        "module": "NRRF866ClosureNaturalityIsTranslationalTruthIsTheGrowthOfTheUniverse",
        "theorem_names": (
            "closure_naturality_is_translational_truth_is_the_growth_of_the_universe",
        ),
        "chart_names": (
            "VisualTranslation",
            "StructuralTranslation",
            "NaturalForm",
            "TranslationalTruth",
            "relation-normalized chart",
        ),
        "proof_kind": "NATURALITY_PULL_TRANSLATIONAL_GROWTH",
        "proved_scope": "Natural form commutes with pull/relabeling and relative distinctions grow functorially with the arena.",
    },
    {
        "module": "NRRF870ClosureOfTradingIsTheOpenSensorFeedbackHairEquationNotEnterAtAskReturnAtNextBid",
        "theorem_names": (),
        "chart_names": (
            "trading maze",
            "unitary curvature",
            "token as returned curvature",
            "completed round-trip profit functional",
            "zero-cost loop",
        ),
        "proof_kind": "OPEN_SENSOR_TRADING_RETURN_CLOSURE",
        "proved_scope": "Trading closure is returned closed-itinerary geometry, not a successor-quote or fixed-horizon rule.",
    },
    {
        "module": "NRRF872UIIsTheClosureBallInteractionIsTheHairZoomRotationMoveSupernetTranslation",
        "theorem_names": (
            "chart_from_view_and_closure",
            "uiSplit",
            "view_forced",
            "view_carries_no_truth",
            "views_are_the_interaction_orbit",
            "ai_and_token_agree_in_the_closure",
            "edge_eq_closure_plus_view",
            "reach_iff_closure_reach_tilted",
            "act_one",
            "act_comp",
            "act_inv",
            "act_geometry",
            "act_closure",
            "ui_is_the_closure_ball_and_the_supernet_closes",
        ),
        "chart_names": (
            "closure ball",
            "hair",
            "maze partition",
            "unitary curvature",
            "light cone",
            "rotation",
            "relation-normalized chart",
        ),
        "proof_kind": "BALL_VIEW_HAIR_MOVE_CHART_FAMILY",
        "proved_scope": "Within the ball chart family, UI/view, hair interaction, curvature, maze, light-cone, zoom/rotation and move preserve one closure geometry.",
    },
    {
        "module": "NRRF874OpenBoundaryNaturalSelectionSupportWideningDerivedFromTranslationalTruth",
        "theorem_names": (
            "select_authors_no_truth",
            "return_state_eq_close",
            "return_in_support_is_same",
            "return_in_support_is_hair",
            "return_outside_support_extends",
            "profitable_return_discovers_profitable_class",
            "boundaryDriven_verdict_ne_same",
            "boundaryDriven_open_or_extends",
            "openBoundary_comb_world",
            "orbit_comb_world",
            "verdictAt_comb_world",
            "resampling_never_profits",
            "open_boundary_beats_resampling",
            "eventually_witnessed_of_fair",
            "eventual_learning_conditional",
            "orbit_subset_reachable",
            "fair_selector_is_closure_complete",
            "truthDerived_iff_factors",
            "truthDerived_comb",
            "ballSelector_not_truthDerived",
            "open_boundary_natural_selection_closes_the_support_gap",
        ),
        "chart_names": (
            "NaturalForm",
            "TranslationalTruth",
            "natural-form selector",
            "OPEN seam",
            "trading maze",
            "hair",
            "closure ball",
        ),
        "proof_kind": "OPEN_BOUNDARY_TRUTH_DERIVED_SELECTION_SUPPORT_WIDENING",
        "proved_scope": "OPEN-boundary selection is hair-blind and support-inert until a return; returns inside support are hair, returns outside support strictly widen reachable translational truth, and eventual profitable learning remains conditional on reachability and fair persistent boundary resolution.",
    },
)

REQUIRED_CORE_MODULES = (
    "NRRF858ConsciousNatureRelativeAxiomsProofsUnderstandingClosuresTranslationalTruthContinuingExistence",
    "NRRF859ConsciousSupernetInteractiveProjectionBridge",
    "NRRF862InteractiveTranslationRelativeUnityOfNaturalFormsArgumentFlowPolicePerspectiveTruthNoClosedExistenceDialecticContinuation",
    "NRRF866ClosureNaturalityIsTranslationalTruthIsTheGrowthOfTheUniverse",
    "NRRF872UIIsTheClosureBallInteractionIsTheHairZoomRotationMoveSupernetTranslation",
)


def derive_formal_proof_index(atlas: Mapping[str, Any]) -> dict[str, Any]:
    charts = [
        dict(chart)
        for chart in atlas.get("charts", [])
        if isinstance(chart, Mapping) and chart.get("id")
    ]
    ids_by_name: dict[str, list[str]] = {}
    for chart in charts:
        ids_by_name.setdefault(str(chart.get("name") or ""), []).append(str(chart["id"]))

    proofs: list[dict[str, Any]] = []
    unresolved_chart_names: list[dict[str, str]] = []
    for bundle in PROOF_BUNDLES:
        resolved: list[str] = []
        unresolved: list[str] = []
        for name in bundle["chart_names"]:
            matches = ids_by_name.get(str(name), [])
            if matches:
                resolved.extend(matches)
            else:
                unresolved.append(str(name))
                unresolved_chart_names.append(
                    {"module": str(bundle["module"]), "chart_name": str(name)}
                )
        body = {
            "module": bundle["module"],
            "theorem_names": list(bundle["theorem_names"]),
            "proof_kind": bundle["proof_kind"],
            "proved_scope": bundle["proved_scope"],
            "chart_names": list(bundle["chart_names"]),
            "chart_ids": sorted(set(resolved)),
            "unresolved_chart_names": unresolved,
            "machine_checked_reported": True,
            "standard_axiom_boundary_reported": True,
            "source_verified_by_runtime": False,
            "runtime_reproves_lean": False,
            "cross_form_equality_authored": False,
            "formal_witness_is_not_visual_resemblance": True,
        }
        body["id"] = _digest("formal-proof-witness", body)
        proofs.append(body)

    modules = {str(item["module"]) for item in proofs}
    required_present = all(module in modules for module in REQUIRED_CORE_MODULES)
    proof_index_closed = bool(
        proofs
        and required_present
        and not unresolved_chart_names
        and all(item["machine_checked_reported"] is True for item in proofs)
        and all(item["cross_form_equality_authored"] is False for item in proofs)
    )
    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "atlas_id": atlas.get("id"),
        "proofs": proofs,
        "required_core_modules": list(REQUIRED_CORE_MODULES),
        "required_core_modules_present": required_present,
        "unresolved_chart_names": unresolved_chart_names,
        "proof_index_closed": proof_index_closed,
        "lean_source_verified_by_runtime": False,
        "runtime_reproves_lean": False,
        "proofs_may_certify_named_properties_without_identifying_forms": True,
        "formal_witness_does_not_erase_version_history": True,
        "truth_issued": False,
    }
    body["id"] = _digest("formal-proof-index", body)
    return body


def validate_formal_proof_index(
    proof_index: Mapping[str, Any],
    *,
    atlas: Mapping[str, Any],
) -> dict[str, Any]:
    expected = derive_formal_proof_index(atlas)
    errors: list[str] = []
    if dict(proof_index) != expected:
        errors.append("formal-proof-index:not-derived")
    if expected.get("proof_index_closed") is not True:
        errors.append("formal-proof-index:not-closed")
    return {
        "valid": not errors,
        "errors": errors,
        "proof_count": len(expected.get("proofs", [])),
        "required_core_modules_present": expected.get(
            "required_core_modules_present"
        ) is True,
        "lean_source_verified_by_runtime": False,
        "runtime_reproves_lean": False,
    }


__all__ = [
    "PROTOCOL",
    "SCHEMA",
    "PROOF_BUNDLES",
    "REQUIRED_CORE_MODULES",
    "derive_formal_proof_index",
    "validate_formal_proof_index",
]
