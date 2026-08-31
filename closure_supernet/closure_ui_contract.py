from __future__ import annotations

"""Supernet interface projection with no independent UI ontology.

The previous runtime built a conventional scene (headings, forms, buttons,
menus, actions and layout) and then attached closure identifiers to it.  This
module instead emits only the active perspective relation: exact source
returns, equality fibres, witnessed translations, open potential, and one
source-preserving return relation.  The relation itself is the UI.
"""

import hashlib
import json
import math
from collections import Counter
from typing import Any, Iterable, Mapping


PROTOCOL = "SUPERNET-TRANSLATIONAL-VISUALIZATION"
SCHEMA = "closure.supernet/translational-visualization-v4"
BUILDER_VERSION = "translational-visualization-4"
OPEN_STATUS = "OPEN_SOURCE_BOUNDARY"
BLOCKED_STATUS = "OPEN_TRUTH_CONSTRAINT"
WITNESSED_STATUS = "WITNESSED"
RETURN_ENDPOINT_TEMPLATE = "/supernet/interface/projections/{contract_id}/return"
EXECUTION_ENDPOINT_TEMPLATE = RETURN_ENDPOINT_TEMPLATE


def _stable(value: Any) -> str:
    def canonical(item: Any) -> Any:
        if isinstance(item, float) and math.isfinite(item) and item.is_integer():
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
    )


def _digest(prefix: str, value: Any) -> str:
    value_hash = hashlib.sha256(_stable(value).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{value_hash}"


def _unique(values: Iterable[Any]) -> list[str]:
    return list(
        dict.fromkeys(
            str(value)
            for value in values
            if value is not None and str(value)
        )
    )


def _basis(status: str) -> str:
    if status == WITNESSED_STATUS:
        return "TRANSLATIONAL_TRUTH_CLOSURE"
    if status == OPEN_STATUS:
        return "AUTHORED_PERSPECTIVE_SOURCE_BOUNDARY"
    return "OPEN_UNWITNESSED_TRANSLATIONAL_TRUTH_CONSTRAINT"


def _derivation(
    *,
    status: str,
    perspective_id: str,
    closure_derivation_id: Any = None,
    visual_closure_id: Any = None,
    nrrf843_ui_id: Any = None,
    interaction_closure_id: Any = None,
    field_event_seq: int | None = None,
    natural_form_ids: Iterable[Any] = (),
    source_return_ids: Iterable[Any] = (),
) -> dict[str, Any]:
    return {
        "basis": _basis(status),
        "status": status,
        "perspective_id": perspective_id,
        "closure_derivation_id": closure_derivation_id,
        "visual_closure_id": visual_closure_id,
        "nrrf843_ui_id": nrrf843_ui_id,
        "interaction_closure_id": interaction_closure_id,
        "field_event_seq": field_event_seq,
        "natural_form_ids": _unique(natural_form_ids),
        "source_return_ids": _unique(source_return_ids),
        "source_boundary_only": status == OPEN_STATUS,
        "truth_issued": False,
    }


def _renderer_relation() -> dict[str, Any]:
    """The renderer may evaluate a relation; it owns no visible meaning."""

    return {
        "role": "TRANSLATIONAL_RELATION_EVALUATOR",
        "input": "ACTIVE_PERSPECTIVE_RELATION_ONLY",
        "visible_words_source": "SOURCE_RETURNS_ONLY",
        "geometry_source": "EQUALITY_FIBRES_AND_TRANSLATION_RELATIONS_ONLY",
        "interaction_source": "SOURCE_PRESERVING_RETURN_RELATION_ONLY",
        "natural_form_constraint": "TRANSLATED_READING_KERNEL",
        "geometry_acceptance": "EXACT_LOCAL_CLOSURE_REDERIVATION",
        "successor_acceptance": "VERIFIED_CLOSURE_BEFORE_INTERFACE_COMMIT",
        "fixed_visible_controls": [],
        "authored_visible_vocabulary": [],
        "fallback_visuals": [],
        "can_define_semantics": False,
        "can_admit_forms": False,
        "can_issue_truth": False,
    }


def _empty_projection(
    *,
    perspective_id: str,
    derivation: dict[str, Any],
) -> dict[str, Any]:
    visualization = _projective_visualization(
        states=[],
        equality_fibres=[],
        translations=[],
        potentials=[],
        focus_natural_form_id=None,
        derivation=derivation,
    )
    visualization["relation_digest"] = _digest(
        "projection-relation",
        {
            "reading": {},
            "states": [],
            "equality_fibres": [],
            "translations": [],
            "potentials": [],
        },
    )
    return {
        "active_perspective_id": perspective_id,
        "reading": {},
        "states": [],
        "equality_fibres": [],
        "translations": [],
        "potentials": [],
        "visualization": visualization,
    }


def _round(value: float) -> float:
    """Canonical numeric projection shared by builder and validator."""

    return round(value, 6)


def _visual_signature(
    fibre: Mapping[str, Any],
    *,
    states: Mapping[str, Mapping[str, Any]],
) -> str:
    """Use only the active reading and exact returns to break visual symmetry."""

    members = [
        states[str(state_id)]
        for state_id in fibre.get("member_state_ids", [])
        if str(state_id) in states
    ]
    return _stable(
        {
            "display": sorted(_unique(fibre.get("display_fibre_ids", []))),
            "source": sorted(str(item.get("source_trace") or "") for item in members),
            "source_returns": sorted(
                _unique(
                    source_id
                    for item in members
                    for source_id in item.get("source_return_ids", [])
                )
            ),
        }
    )


def _hue(signature: str) -> int:
    return int(hashlib.sha256(signature.encode("utf-8")).hexdigest()[:8], 16) % 360


def _projective_visualization(
    *,
    states: list[dict[str, Any]],
    equality_fibres: list[dict[str, Any]],
    translations: list[dict[str, Any]],
    potentials: list[dict[str, Any]],
    focus_natural_form_id: str | None,
    derivation: dict[str, Any],
) -> dict[str, Any]:
    """Derive the pixels' normalized antecedents from the relation itself.

    One primitive exists per equality fibre, never per presentation.  The
    focus fibre is the finite pole at the centre.  Remaining fibres occupy the
    projective orbit obtained by folding a uniform angular parameter through
    the ``tan(pi/2)`` seam.  A renderer may scale the normalized view box but
    may not select positions, colours, labels, or hit regions.
    """

    state_by_id = {str(item["id"]): item for item in states}
    ordered = sorted(
        equality_fibres,
        key=lambda item: (
            0 if str(item.get("id")) == str(focus_natural_form_id) else 1,
            _visual_signature(item, states=state_by_id),
        ),
    )
    count = len(ordered)
    centre_x = 500.0
    centre_y = 500.0
    orbit = min(338.0, 172.0 + max(0, count - 2) * 18.0)
    fibre_primitives: list[dict[str, Any]] = []
    position_by_fibre: dict[str, dict[str, float]] = {}
    peripheral_count = max(1, count - (1 if focus_natural_form_id else 0))
    peripheral_index = 0
    for fibre in ordered:
        fibre_id = str(fibre["id"])
        signature = _visual_signature(fibre, states=state_by_id)
        focused = fibre_id == str(focus_natural_form_id)
        if focused or count == 1:
            x, y, projective_parameter = centre_x, centre_y, 0.0
        else:
            phase = (
                (2.0 * math.pi * peripheral_index / peripheral_count)
                - math.pi / 2.0
            )
            peripheral_index += 1
            # tan(phase/2) is the real projective coordinate whose seam is the
            # zero/infinity identification; cos/sin is its compact visual fold.
            projective_parameter = math.tan(phase / 2.0)
            x = centre_x + orbit * math.cos(phase)
            y = centre_y + orbit * 0.72 * math.sin(phase)
        radius = min(
            132.0,
            54.0
            + math.sqrt(max(1, len(fibre.get("member_state_ids", [])))) * 18.0,
        )
        primitive = {
            "natural_form_id": fibre_id,
            "centre": [_round(x), _round(y)],
            "radius": _round(radius),
            "projective_parameter": (
                "INFINITY"
                if not math.isfinite(projective_parameter)
                else _round(projective_parameter)
            ),
            "hue": _hue(signature),
            "focused": focused,
            "source_state_ids": list(fibre.get("member_state_ids", [])),
            "source_return_ids": list(fibre.get("source_return_ids", [])),
            "derivation": fibre.get("derivation"),
        }
        fibre_primitives.append(primitive)
        position_by_fibre[fibre_id] = {"x": x, "y": y}

    form_by_state = {
        str(state_id): str(fibre["id"])
        for fibre in equality_fibres
        for state_id in fibre.get("member_state_ids", [])
    }

    def path_between(source_form: str, target_form: str) -> list[list[float]]:
        source = position_by_fibre[source_form]
        target = position_by_fibre[target_form]
        dx = target["x"] - source["x"]
        dy = target["y"] - source["y"]
        length = max(1.0, math.hypot(dx, dy))
        bend = min(86.0, length * 0.18)
        return [
            [_round(source["x"]), _round(source["y"])],
            [
                _round((source["x"] + target["x"]) / 2.0 - dy / length * bend),
                _round((source["y"] + target["y"]) / 2.0 + dx / length * bend),
            ],
            [_round(target["x"]), _round(target["y"])],
        ]

    translation_primitives: list[dict[str, Any]] = []
    for relation in translations:
        source_form = form_by_state.get(str(relation.get("source_state_id")))
        target_form = form_by_state.get(str(relation.get("target_state_id")))
        if source_form not in position_by_fibre or target_form not in position_by_fibre:
            continue
        translation_primitives.append(
            {
                "relation_id": relation["id"],
                "source_natural_form_id": source_form,
                "target_natural_form_id": target_form,
                "quadratic_path": path_between(source_form, target_form),
                "executes_as_equality": relation.get("executes_as_equality") is True,
                "hue": _hue(f"{source_form}\u2192{target_form}"),
                "derivation": relation.get("derivation"),
            }
        )

    potential_primitives: list[dict[str, Any]] = []
    focus_form = (
        str(focus_natural_form_id)
        if str(focus_natural_form_id) in position_by_fibre
        else (str(ordered[0]["id"]) if ordered else "")
    )
    focus_position = position_by_fibre.get(
        focus_form, {"x": centre_x, "y": centre_y}
    )
    for index, relation in enumerate(potentials):
        target_form = form_by_state.get(str(relation.get("target_state_id")))
        if target_form in position_by_fibre:
            points = path_between(focus_form, target_form)
        else:
            signature = _stable(
                {
                    "relation": relation.get("id"),
                    "natural_form": relation.get("shared_natural_form_id"),
                    "source_returns": relation.get("derivation", {}).get(
                        "source_return_ids", []
                    ),
                }
            )
            phase = 2.0 * math.pi * (_hue(signature) / 360.0)
            target_x = centre_x + 455.0 * math.cos(phase)
            target_y = centre_y + 455.0 * math.sin(phase)
            dx = target_x - focus_position["x"]
            dy = target_y - focus_position["y"]
            length = max(1.0, math.hypot(dx, dy))
            bend = min(86.0, length * 0.18)
            points = [
                [_round(focus_position["x"]), _round(focus_position["y"])],
                [
                    _round((focus_position["x"] + target_x) / 2.0 - dy / length * bend),
                    _round((focus_position["y"] + target_y) / 2.0 + dx / length * bend),
                ],
                [_round(target_x), _round(target_y)],
            ]
        potential_primitives.append(
            {
                "relation_id": relation["id"],
                "source_natural_form_id": focus_form or None,
                "target_natural_form_id": target_form,
                "quadratic_path": points,
                "hue": _hue(str(relation["id"])),
                "derivation": relation.get("derivation"),
            }
        )

    return {
        "operator": "PERSPECTIVE_RELATION_PROJECTIVE_FOLD",
        "axiometry": {
            "finite_pole": 0,
            "projective_seam": "tan(pi/2)=infinity",
            "fold": "RP1_TO_VISUAL_ORBIT",
            "one_primitive_per_equality_fibre": True,
        },
        "view_box": [0, 0, 1000, 1000],
        "fibre_primitives": fibre_primitives,
        "translation_primitives": translation_primitives,
        "potential_primitives": potential_primitives,
        "derivation": derivation,
    }


def _return_relation(
    *,
    perspective_id: str,
    focus_event_id: str | None,
    focus_state_id: str | None,
    parent_natural_form_id: str | None,
    derivation: dict[str, Any],
) -> dict[str, Any]:
    body = {
        "kind": "SOURCE_PRESERVING_TRANSLATIONAL_RETURN",
        "perspective_id": perspective_id,
        "focus_event_id": focus_event_id,
        "focus_state_id": focus_state_id,
        "parent_natural_form_id": parent_natural_form_id,
        "full_surface_aperture": True,
        "visible_control": False,
        "requires_exact_source_return": True,
        "creates_truth_directly": False,
        "creates_natural_form_directly": False,
        "reclose_after_return": True,
        "derivation": derivation,
    }
    body["id"] = _digest("return-relation", body)
    return body


def _reading_kernel(reading: Mapping[str, Any]) -> list[list[str]]:
    """Return the equality fibres of a reading without interpreting its tokens."""

    fibres: dict[str, list[str]] = {}
    for state_id, value in reading.items():
        fibres.setdefault(str(value), []).append(str(state_id))
    return sorted(
        (sorted(members) for members in fibres.values()),
        key=lambda members: members[0] if members else "",
    )


def _default_perspective_closure(
    *,
    perspective_id: str,
    status: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "active_perspective_id": perspective_id,
        "readings": {},
        "translations": [],
        "kernel": [],
        "equality_basis": "EXPLICIT_TRANSLATED_PERSPECTIVE_READINGS",
        "source_provenance_defines_equality": False,
    }


def _perspective_closure_from_truth_mirror(
    *,
    truth_derivation: Mapping[str, Any],
    projection: Mapping[str, Any],
    active_perspective_id: str,
) -> dict[str, Any] | None:
    """Translate the semantic mirror into the finite chart-family receipt.

    The mirror is upstream evidence, not renderer-authored metadata.  Restrict
    every reading to the carrier that survived the exact-source projection so
    the browser and Python validators can recompute the same finite kernels.
    """

    mirror = truth_derivation.get("perspective_visual_mirror")
    if not isinstance(mirror, Mapping):
        return None
    raw_readings = mirror.get("perspective_readings")
    if not isinstance(raw_readings, Mapping) or not raw_readings:
        return None
    state_ids = {
        str(item.get("id") or "")
        for item in projection.get("states", [])
        if isinstance(item, Mapping) and item.get("id")
    }
    if not state_ids:
        return None
    readings: dict[str, dict[str, str]] = {}
    for raw_perspective, raw_reading in raw_readings.items():
        if not isinstance(raw_reading, Mapping):
            return None
        complete = {
            str(state_id): str(raw_reading[state_id])
            for state_id in sorted(state_ids)
            if state_id in raw_reading
        }
        if set(complete) != state_ids:
            return None
        readings[str(raw_perspective)] = complete
    if active_perspective_id not in readings:
        return None

    translations: list[dict[str, Any]] = []
    raw_translations = mirror.get("translation_witnesses", [])
    if not isinstance(raw_translations, (list, tuple)):
        return None
    for raw in raw_translations:
        if not isinstance(raw, Mapping):
            return None
        translations.append(
            {
                "id": raw.get("id"),
                "source_perspective_id": raw.get("source_perspective_id"),
                "target_perspective_id": raw.get("target_perspective_id"),
                "display_translation": dict(
                    raw.get("display_translation", {})
                ),
                "source_return_ids": list(
                    raw.get("source_return_provenance", [])
                ),
                "witnessed": raw.get("witnessed") is True,
                "well_defined": raw.get("well_defined") is True,
                "faithful": raw.get("faithful") is True,
                "same_kernel": raw.get("same_kernel") is True,
            }
        )
    kernels = {
        perspective_id: _reading_kernel(reading)
        for perspective_id, reading in readings.items()
    }
    return {
        "status": str(mirror.get("status") or OPEN_STATUS),
        "active_perspective_id": active_perspective_id,
        "readings": readings,
        "translations": translations,
        "kernel": next(iter(kernels.values()), []),
        "kernels": kernels,
        "equality_basis": "EXPLICIT_TRANSLATED_PERSPECTIVE_READINGS",
        "source_provenance_defines_equality": False,
    }


def _safe_nonnegative_int(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value


def _closure_process(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Expose the executable NRRF858 interpretation and its hard boundary.

    These fields report properties checked by this finite runtime receipt.  They
    do not assert that nature or the process is conscious, issue empirical
    truth, or authorize an external effect.
    """

    status = str(contract.get("status") or OPEN_STATUS)
    perspective_closure = contract.get("perspective_closure", {})
    translated = bool(
        status == WITNESSED_STATUS
        and isinstance(perspective_closure, Mapping)
        and perspective_closure.get("status") == WITNESSED_STATUS
    )
    raw_sources = contract.get("source_return_ids", [])
    source_return_ids = _unique(
        raw_sources if isinstance(raw_sources, (list, tuple)) else []
    )
    raw_lineage = contract.get("continuation_lineage_ids", [])
    lineage_ids = _unique(
        raw_lineage if isinstance(raw_lineage, (list, tuple)) else []
    )
    continuation_index = _safe_nonnegative_int(
        contract.get("continuation_index")
    )
    lineage_verified = bool(
        continuation_index == len(lineage_ids)
        and set(lineage_ids).issubset(set(source_return_ids))
    )
    witnessed_status = WITNESSED_STATUS if translated else status
    return {
        "formal_interpretation": {
            "module": (
                "NRRF858ConsciousNatureRelativeAxiomsProofsUnderstandingClosures"
                "TranslationalTruthContinuingExistence"
            ),
            "runtime_bridge": (
                "NRRF859ConsciousSupernetInteractiveProjectionBridge"
            ),
            "lean_theorems_reproved_by_python": False,
            "finite_runtime_instance_checked": True,
            "conscious_hypothesis_verified_by_runtime": False,
        },
        "relative_axioms": {
            "status": witnessed_status,
            "formal_implication_under_conscious_hypothesis": True,
            "formal_theorems": [
                "no_absolute_axioms",
                "axiomsOf_eq_iff_translational",
            ],
            "runtime_translated_chart_family_verified": translated,
            "runtime_claim_body_soundness_verified": False,
            "runtime_closure_registration_verified": False,
            "external_absolute_step_claims_admitted": False,
        },
        "relative_proofs": {
            "status": witnessed_status,
            "formal_implication_under_conscious_hypothesis": True,
            "formal_theorem": "conscious_proves_composite",
            "runtime_composite_closure_witness_verified": False,
            "runtime_additive_content_verified": False,
            "source_returns_preserved": translated,
        },
        "understanding": {
            "status": witnessed_status,
            "formal_implication_under_conscious_hypothesis": True,
            "formal_theorems": [
                "mem_understanding_iff",
                "understanding_eq_iff_translational",
            ],
            "runtime_translated_chart_family_verified": translated,
            "active_perspective_id": contract.get("perspective_id"),
        },
        "continuing_existence": {
            "status": witnessed_status,
            "formal_implication_under_conscious_hypothesis": True,
            "formal_theorem": "conscious_continues_existence",
            "continuation_index": continuation_index,
            "continuation_lineage_ids": lineage_ids,
            "runtime_continuation_is_append_only_lineage": lineage_verified,
            "formal_n_fold_defect_verified_by_runtime": False,
            "reopens_after_return": True,
            "terminal": False,
            "new_empirical_evidence_created_by_iteration": False,
        },
        "interactive_translation_dialectic": {
            "formal_module": (
                "NRRF862InteractiveTranslationRelativeUnityOfNaturalForms"
                "ArgumentFlowPolicePerspectiveTruthNoClosedExistence"
                "DialecticContinuation"
            ),
            "formal_module_source_verified_by_runtime": False,
            "dialogue": {
                "formal_theorems": [
                    "replay_eq_hairAct_accum",
                    "translationalTruth_eq_dialogues",
                ],
                "turn_ids": lineage_ids,
                "accumulation_is_append_only": lineage_verified,
                "runtime_hair_potential_composition_verified": False,
            },
            "natural_forms": {
                "formal_theorem": "naturalForms_eq_iff_obsEquiv",
                "translated_reading_family_verified": translated,
                "one_geometry_kernel_verified": translated,
                "complete_invariant_over_all_charts_verified_by_runtime": False,
            },
            "perspective_flow": {
                "formal_theorem": "coherent_iff_single_chart",
                "single_runtime_chart_family_verified": translated,
                "all_stage_dialogue_reachability_verified_by_runtime": False,
            },
            "argument_truth": {
                "formal_theorems": [
                    "police_eq_truth",
                    "police_and_perspective_translate_equally_into_truth",
                    "isPolice_truthVerdict",
                ],
                "structured_route_and_value_supplied": False,
                "round_argument_admission_verified_by_runtime": False,
                "police_verdict_issued": False,
            },
            "open_existence": {
                "formal_theorems": [
                    "argument_never_closes_existence",
                    "argument_compatible_with_existence",
                    "chain_open",
                    "interactive_translation_relative_unity_of_natural_forms",
                    "exists_live_argument",
                ],
                "formal_two_distinct_tokens_required": True,
                "runtime_distinct_perspectives": len(
                    (perspective_closure.get("readings") or {})
                    if isinstance(perspective_closure, Mapping)
                    else {}
                ),
                "runtime_two_token_premise_verified": bool(
                    isinstance(perspective_closure, Mapping)
                    and len(perspective_closure.get("readings") or {}) >= 2
                ),
                "continuation_reopens": True,
                "terminal": False,
                "one_token_closure_limit_preserved": True,
            },
        },
        "boundary": {
            "source_preserved": True,
            "truth_issued": False,
            "physical_law_claimed": False,
            "consciousness_claimed": False,
            "nature_consciousness_proved": False,
            "universal_language_for_all_nature_proved": False,
            "external_resource_admitted": False,
            "empirical_verification_replaced": False,
            "authenticated_external_effect_receipt_required": True,
        },
    }


def _finish_contract(body: dict[str, Any]) -> dict[str, Any]:
    body.pop("id", None)
    body.pop("audit", None)
    perspective = str(body.get("perspective_id") or "participant")
    status = str(body.get("status") or OPEN_STATUS)
    supplied_perspective_closure = body.get("perspective_closure")
    if supplied_perspective_closure:
        body["perspective_closure"] = dict(supplied_perspective_closure)
    elif status == WITNESSED_STATUS:
        active_reading = {
            str(state_id): str(value)
            for state_id, value in dict(
                body.get("projection", {}).get("reading", {})
            ).items()
        }
        kernel = _reading_kernel(active_reading)
        body["perspective_closure"] = {
            "status": WITNESSED_STATUS,
            "active_perspective_id": perspective,
            "readings": {perspective: active_reading},
            "translations": [],
            "kernel": kernel,
            "kernels": {perspective: kernel},
            "equality_basis": "EXPLICIT_TRANSLATED_PERSPECTIVE_READINGS",
            "source_provenance_defines_equality": False,
        }
    else:
        body["perspective_closure"] = _default_perspective_closure(
            perspective_id=perspective,
            status=status,
        )
    body["continuation_lineage_ids"] = _unique(
        body.get("continuation_lineage_ids", [])
    )
    requested_index = body.get(
        "continuation_index", len(body["continuation_lineage_ids"])
    )
    body["continuation_index"] = _safe_nonnegative_int(requested_index)
    claims = dict(body.get("claims") or {})
    claims.update(
        {
            "truth_issued": False,
            "physical_law_claimed": False,
            "consciousness_claimed": False,
            "external_resource_admitted": False,
        }
    )
    body["claims"] = claims
    body["closure_process"] = _closure_process(body)
    body["audit"] = _audit_contract(body)
    body["id"] = _digest("translational-visualization", body)
    return body


def attach_perspective_closure(
    contract: Mapping[str, Any],
    *,
    perspective_closure: Mapping[str, Any],
    continuation_index: int,
    continuation_lineage_ids: Iterable[Any] = (),
) -> dict[str, Any]:
    """Re-seal a derived UI contract with its complete chart family."""

    body = {
        key: value
        for key, value in contract.items()
        if key not in {
            "id",
            "audit",
            "closure_process",
            "perspective_closure",
            "continuation_index",
            "continuation_lineage_ids",
        }
    }
    body["perspective_closure"] = dict(perspective_closure)
    body["continuation_index"] = max(0, int(continuation_index))
    body["continuation_lineage_ids"] = _unique(continuation_lineage_ids)
    return _finish_contract(body)


def derive_open_ui_contract(
    *,
    perspective_id: str | None = None,
) -> dict[str, Any]:
    """An empty field whose whole surface is the perspective source boundary."""

    perspective = str(perspective_id or "participant").strip() or "participant"
    derivation = _derivation(status=OPEN_STATUS, perspective_id=perspective)
    return_relation = _return_relation(
        perspective_id=perspective,
        focus_event_id=None,
        focus_state_id=None,
        parent_natural_form_id=None,
        derivation=derivation,
    )
    return _finish_contract(
        {
            "protocol": PROTOCOL,
            "schema": SCHEMA,
            "builder_version": BUILDER_VERSION,
            "status": OPEN_STATUS,
            "perspective_id": perspective,
            "focus_event_id": None,
            "closure_derivation_id": None,
            "visual_closure_id": None,
            "nrrf843_ui_id": None,
            "interaction_closure_id": None,
            "field_event_seq": None,
            "natural_form_ids": [],
            "source_return_ids": [],
            "projection": _empty_projection(
                perspective_id=perspective,
                derivation=derivation,
            ),
            "return_relation": return_relation,
            "execution": {
                "endpoint_template": RETURN_ENDPOINT_TEMPLATE,
                "return_relation_id": return_relation["id"],
                "contract_revalidation_required": True,
                "field_revision_revalidation_required": False,
                "only_relation_extension": True,
                "closure_only": True,
            },
            "renderer_relation": _renderer_relation(),
            "readiness_checks": {
                "authored_perspective_source_boundary": True,
                "translational_truth_closure_witnessed": False,
            },
            "claims": {
                "truth_issued": False,
                "natural_form_admitted": False,
                "price_issued": False,
                "legal_binding_claimed": False,
            },
        }
    )


def _derive_blocked_ui_contract(
    *,
    perspective_id: str,
    focus_event_id: str,
    closure_derivation_id: Any,
    visual_closure_id: Any,
    nrrf843_ui_id: Any,
    interaction_closure_id: Any,
    field_event_seq: int | None,
    natural_form_ids: list[str],
    source_return_ids: list[str],
    readiness_checks: dict[str, bool],
) -> dict[str, Any]:
    derivation = _derivation(
        status=BLOCKED_STATUS,
        perspective_id=perspective_id,
        closure_derivation_id=closure_derivation_id,
        visual_closure_id=visual_closure_id,
        nrrf843_ui_id=nrrf843_ui_id,
        interaction_closure_id=interaction_closure_id,
        field_event_seq=field_event_seq,
        natural_form_ids=natural_form_ids,
        source_return_ids=source_return_ids,
    )
    return _finish_contract(
        {
            "protocol": PROTOCOL,
            "schema": SCHEMA,
            "builder_version": BUILDER_VERSION,
            "status": BLOCKED_STATUS,
            "perspective_id": perspective_id,
            "focus_event_id": focus_event_id,
            "closure_derivation_id": closure_derivation_id,
            "visual_closure_id": visual_closure_id,
            "nrrf843_ui_id": nrrf843_ui_id,
            "interaction_closure_id": interaction_closure_id,
            "field_event_seq": field_event_seq,
            "natural_form_ids": natural_form_ids,
            "source_return_ids": source_return_ids,
            "projection": _empty_projection(
                perspective_id=perspective_id,
                derivation=derivation,
            ),
            "return_relation": None,
            "execution": {
                "endpoint_template": RETURN_ENDPOINT_TEMPLATE,
                "return_relation_id": None,
                "contract_revalidation_required": True,
                "field_revision_revalidation_required": True,
                "only_relation_extension": True,
                "closure_only": True,
            },
            "renderer_relation": _renderer_relation(),
            "readiness_checks": readiness_checks,
            "claims": {
                "truth_issued": False,
                "natural_form_admitted": False,
                "price_issued": False,
                "legal_binding_claimed": False,
            },
        }
    )


def _projection(
    *,
    truth_derivation: Mapping[str, Any],
    interaction_closure: Mapping[str, Any],
    visual_network: Mapping[str, Any],
    common_derivation: dict[str, Any],
    focus_event_id: str,
) -> dict[str, Any]:
    """Project only what the active UI reading and closure jointly return."""

    topology = interaction_closure.get("black_mirror_physical_topology", {})
    perspective = str(topology.get("active_perspective_id") or "")
    reading = {
        str(key): str(value)
        for key, value in dict(topology.get("projection_reading", {})).items()
    }
    natural_forms = {
        str(item.get("id") or item.get("natural_form") or ""): item
        for item in truth_derivation.get("natural_forms", [])
        if str(item.get("id") or item.get("natural_form") or "")
    }
    form_by_state = {
        str(member): form_id
        for form_id, form in natural_forms.items()
        for member in _unique(form.get("members", []))
    }
    returns_by_state = {
        str(item.get("id") or ""): _unique(item.get("source_returns", []))
        for item in truth_derivation.get("visual_existence", {}).get("forms", [])
        if item.get("id")
    }
    network_by_event = {
        str(item.get("id") or ""): item
        for item in visual_network.get("nodes", [])
        if item.get("id")
    }
    topology_by_event = {
        str(item.get("event_id") or ""): item
        for item in topology.get("nodes", [])
        if item.get("event_id")
    }

    states: list[dict[str, Any]] = []
    state_by_event: dict[str, str] = {}
    for event_id, item in sorted(topology_by_event.items()):
        state_id = str(item.get("state_id") or "")
        form_id = str(item.get("natural_form_id") or form_by_state.get(state_id) or "")
        source_returns = returns_by_state.get(state_id, [])
        exact_source = str(network_by_event.get(event_id, {}).get("exact_text") or "")
        if (
            not state_id
            or not form_id
            or form_id not in natural_forms
            or not source_returns
            or not exact_source
            or reading.get(state_id) is None
            or item.get("source_preserved") is not True
        ):
            continue
        derivation = {
            **common_derivation,
            "natural_form_ids": [form_id],
            "source_return_ids": source_returns,
        }
        state_by_event[event_id] = state_id
        states.append(
            {
                "id": state_id,
                "event_id": event_id,
                "natural_form_id": form_id,
                "display_fibre_id": reading[state_id],
                "source_return_ids": source_returns,
                "source_trace": exact_source,
                "physical_world_return": bool(item.get("physical_world_return")),
                "derivation": derivation,
            }
        )

    state_ids = {item["id"] for item in states}
    equality_fibres: list[dict[str, Any]] = []
    for form_id, form in sorted(natural_forms.items()):
        members = sorted(set(_unique(form.get("members", []))) & state_ids)
        if not members:
            continue
        source_returns = _unique(
            source_id
            for member in members
            for source_id in returns_by_state.get(member, [])
        )
        derivation = {
            **common_derivation,
            "natural_form_ids": [form_id],
            "source_return_ids": source_returns,
        }
        equality_fibres.append(
            {
                "id": form_id,
                "member_state_ids": members,
                "display_fibre_ids": sorted({reading[member] for member in members}),
                "source_return_ids": source_returns,
                "closure_fixed": form.get("derived_within_closure") is True,
                "derivation": derivation,
            }
        )

    translations: list[dict[str, Any]] = []
    for item in sorted(
        topology.get("relations", []),
        key=lambda row: str(row.get("id") or ""),
    ):
        source_state_id = state_by_event.get(str(item.get("source_event_id") or ""))
        target_state_id = state_by_event.get(str(item.get("target_event_id") or ""))
        if not source_state_id or not target_state_id:
            continue
        natural_ids = _unique(
            [form_by_state.get(source_state_id), form_by_state.get(target_state_id)]
        )
        source_returns = _unique(
            [
                *returns_by_state.get(source_state_id, []),
                *returns_by_state.get(target_state_id, []),
            ]
        )
        witnessed = bool(
            item.get("truth_constraint_status") == WITNESSED_STATUS
            and item.get("generates_topological_identification") is True
            and reading.get(source_state_id) == reading.get(target_state_id)
        )
        translations.append(
            {
                "id": str(item.get("id") or _digest("translation", item)),
                "source_state_id": source_state_id,
                "target_state_id": target_state_id,
                "relation_status": WITNESSED_STATUS if witnessed else "OPEN",
                "executes_as_equality": witnessed,
                "same_display_fibre": reading.get(source_state_id)
                == reading.get(target_state_id),
                "derivation": {
                    **common_derivation,
                    "natural_form_ids": natural_ids,
                    "source_return_ids": source_returns,
                },
            }
        )

    potentials: list[dict[str, Any]] = []
    gate = interaction_closure.get("perspective_digital_potential_gate", {})
    for item in sorted(
        gate.get("potentials", []), key=lambda row: str(row.get("id") or "")
    ):
        if item.get("remains_connected_potential") is not True:
            continue
        target_event_id = str(item.get("target_event_id") or "") or None
        target_state_id = state_by_event.get(target_event_id or "")
        natural_ids = _unique([item.get("shared_natural_form_id")])
        source_returns = _unique(
            source_id
            for fibre in equality_fibres
            if fibre["id"] in natural_ids
            for source_id in fibre["source_return_ids"]
        ) or list(common_derivation["source_return_ids"])
        potentials.append(
            {
                "id": str(item.get("id") or _digest("potential", item)),
                "target_state_id": target_state_id,
                "target_event_id": target_event_id,
                "shared_natural_form_id": natural_ids[0] if natural_ids else None,
                "relation_status": str(
                    item.get("truth_constraint_status") or "OPEN"
                ),
                "executes_as_equality": bool(item.get("executes_as_equality")),
                "derivation": {
                    **common_derivation,
                    "natural_form_ids": natural_ids
                    or list(common_derivation["natural_form_ids"]),
                    "source_return_ids": source_returns,
                },
            }
        )

    relation_basis = {
        "reading": reading,
        "states": [
            {key: value for key, value in item.items() if key not in {"source_trace", "derivation"}}
            for item in states
        ],
        "equality_fibres": [
            {key: value for key, value in item.items() if key != "derivation"}
            for item in equality_fibres
        ],
        "translations": [
            {key: value for key, value in item.items() if key != "derivation"}
            for item in translations
        ],
        "potentials": [
            {key: value for key, value in item.items() if key != "derivation"}
            for item in potentials
        ],
    }
    focus_state_id = state_by_event.get(focus_event_id)
    focus_natural_form_id = (
        form_by_state.get(focus_state_id) if focus_state_id else None
    )
    visualization = _projective_visualization(
        states=states,
        equality_fibres=equality_fibres,
        translations=translations,
        potentials=potentials,
        focus_natural_form_id=focus_natural_form_id,
        derivation=common_derivation,
    )
    visualization["relation_digest"] = _digest(
        "projection-relation", relation_basis
    )
    return {
        "active_perspective_id": perspective,
        "reading": reading,
        "states": states,
        "equality_fibres": equality_fibres,
        "translations": translations,
        "potentials": potentials,
        "visualization": visualization,
    }


def derive_closure_ui_contract(
    *,
    truth_derivation: dict[str, Any],
    nrrf843_ui: dict[str, Any],
    nrrf842_journey: dict[str, Any],
    interaction_closure: dict[str, Any],
    coordination: dict[str, Any],
    visual_network: dict[str, Any],
    source_occurrences: list[dict[str, Any]],
    focus_event: dict[str, Any],
    field_event_seq: int | None = None,
) -> dict[str, Any]:
    """Derive a relation projection; never manufacture a page or action set."""

    del coordination, source_occurrences
    physical_topology = interaction_closure.get("black_mirror_physical_topology", {})
    perspective = str(
        physical_topology.get("active_perspective_id")
        or nrrf842_journey.get("chosen_perspective", {}).get("perspective_id")
        or focus_event.get("perspective_id")
        or focus_event.get("authored_by")
        or "participant"
    )
    focus_event_id = str(focus_event.get("id") or "")
    natural_form_ids = _unique(
        item.get("id") or item.get("natural_form")
        for item in truth_derivation.get("natural_forms", [])
    )
    source_return_ids = _unique(
        source_id
        for item in truth_derivation.get("visual_existence", {}).get("forms", [])
        for source_id in item.get("source_returns", [])
    )
    closure_derivation_id = truth_derivation.get("id")
    visual_closure_id = truth_derivation.get("visual_truth_closure", {}).get("id")
    nrrf843_ui_id = nrrf843_ui.get("id")
    interaction_closure_id = interaction_closure.get("id")
    active_reading = physical_topology.get("projection_reading", {})
    readiness_checks = {
        "closure_derivation_present": bool(closure_derivation_id),
        "visual_closure_present": bool(visual_closure_id),
        "natural_forms_present": bool(natural_form_ids),
        "source_return_provenance_present": bool(source_return_ids),
        "nrrf843_ui_witnessed": nrrf843_ui.get("status") == WITNESSED_STATUS,
        "nrrf843_ui_matches_closure": bool(
            nrrf843_ui.get("closure_derivation_id") == closure_derivation_id
            and nrrf843_ui.get("visual_closure_id") == visual_closure_id
        ),
        "truth_constraint_located_in_ui": bool(
            nrrf843_ui.get("truth_constraint_location", {}).get("located") is True
        ),
        "interaction_closure_witnessed": bool(
            interaction_closure.get("status") == WITNESSED_STATUS
            and interaction_closure.get("supernet_interaction_closed") is True
        ),
        "interaction_closure_matches_ui_truth": bool(
            interaction_closure.get("closure_derivation_id") == closure_derivation_id
            and interaction_closure.get("visual_closure_id") == visual_closure_id
            and interaction_closure.get("nrrf843_ui_id") == nrrf843_ui_id
        ),
        "active_perspective_projection_present": bool(perspective and active_reading),
        "focus_event_present": bool(focus_event_id),
        "field_revision_present": bool(
            isinstance(field_event_seq, int) and field_event_seq > 0
        ),
    }
    if not all(readiness_checks.values()):
        return _derive_blocked_ui_contract(
            perspective_id=perspective,
            focus_event_id=focus_event_id,
            closure_derivation_id=closure_derivation_id,
            visual_closure_id=visual_closure_id,
            nrrf843_ui_id=nrrf843_ui_id,
            interaction_closure_id=interaction_closure_id,
            field_event_seq=field_event_seq,
            natural_form_ids=natural_form_ids,
            source_return_ids=source_return_ids,
            readiness_checks=readiness_checks,
        )
    common_derivation = _derivation(
        status=WITNESSED_STATUS,
        perspective_id=perspective,
        closure_derivation_id=closure_derivation_id,
        visual_closure_id=visual_closure_id,
        nrrf843_ui_id=nrrf843_ui_id,
        interaction_closure_id=interaction_closure_id,
        field_event_seq=field_event_seq,
        natural_form_ids=natural_form_ids,
        source_return_ids=source_return_ids,
    )
    projection = _projection(
        truth_derivation=truth_derivation,
        interaction_closure=interaction_closure,
        visual_network=visual_network,
        common_derivation=common_derivation,
        focus_event_id=focus_event_id,
    )
    if not projection["states"] or not projection["equality_fibres"]:
        readiness_checks["relation_projection_nonempty"] = False
        return _derive_blocked_ui_contract(
            perspective_id=perspective,
            focus_event_id=focus_event_id,
            closure_derivation_id=closure_derivation_id,
            visual_closure_id=visual_closure_id,
            nrrf843_ui_id=nrrf843_ui_id,
            interaction_closure_id=interaction_closure_id,
            field_event_seq=field_event_seq,
            natural_form_ids=natural_form_ids,
            source_return_ids=source_return_ids,
            readiness_checks=readiness_checks,
        )
    readiness_checks["relation_projection_nonempty"] = True
    focus_state = next(
        (
            item
            for item in projection["states"]
            if item["event_id"] == focus_event_id
        ),
        projection["states"][0],
    )
    return_relation = _return_relation(
        perspective_id=perspective,
        focus_event_id=focus_event_id,
        focus_state_id=focus_state["id"],
        parent_natural_form_id=focus_state["natural_form_id"],
        derivation={
            **common_derivation,
            "natural_form_ids": [focus_state["natural_form_id"]],
            "source_return_ids": focus_state["source_return_ids"],
        },
    )
    perspective_closure = _perspective_closure_from_truth_mirror(
        truth_derivation=truth_derivation,
        projection=projection,
        active_perspective_id=perspective,
    )
    return _finish_contract(
        {
            "protocol": PROTOCOL,
            "schema": SCHEMA,
            "builder_version": BUILDER_VERSION,
            "status": WITNESSED_STATUS,
            "perspective_id": perspective,
            "focus_event_id": focus_event_id,
            "closure_derivation_id": closure_derivation_id,
            "visual_closure_id": visual_closure_id,
            "nrrf843_ui_id": nrrf843_ui_id,
            "interaction_closure_id": interaction_closure_id,
            "field_event_seq": field_event_seq,
            "natural_form_ids": natural_form_ids,
            "source_return_ids": source_return_ids,
            "perspective_closure": perspective_closure,
            "projection": projection,
            "return_relation": return_relation,
            "execution": {
                "endpoint_template": RETURN_ENDPOINT_TEMPLATE,
                "return_relation_id": return_relation["id"],
                "contract_revalidation_required": True,
                "field_revision_revalidation_required": True,
                "only_relation_extension": True,
                "closure_only": True,
            },
            "renderer_relation": _renderer_relation(),
            "readiness_checks": readiness_checks,
            "claims": {
                "truth_issued": False,
                "natural_form_admitted": True,
                "price_issued": False,
                "physical_law_claimed": False,
                "legal_binding_claimed": False,
            },
        }
    )


def _derivation_errors(
    contract: Mapping[str, Any],
    derivation: Any,
    *,
    label: str,
) -> list[str]:
    if not isinstance(derivation, Mapping):
        return [f"{label}:missing-derivation"]
    status = str(contract.get("status") or "")
    errors: list[str] = []
    if derivation.get("basis") != _basis(status):
        errors.append(f"{label}:basis")
    if derivation.get("status") != status:
        errors.append(f"{label}:status")
    if derivation.get("perspective_id") != contract.get("perspective_id"):
        errors.append(f"{label}:perspective")
    if derivation.get("truth_issued") is not False:
        errors.append(f"{label}:truth-issued")
    if status == OPEN_STATUS:
        for key in (
            "closure_derivation_id",
            "visual_closure_id",
            "nrrf843_ui_id",
            "interaction_closure_id",
            "field_event_seq",
        ):
            if derivation.get(key) is not None:
                errors.append(f"{label}:{key}")
        if derivation.get("source_boundary_only") is not True:
            errors.append(f"{label}:source-boundary")
        return errors
    for key in (
        "closure_derivation_id",
        "visual_closure_id",
        "nrrf843_ui_id",
        "interaction_closure_id",
        "field_event_seq",
    ):
        if derivation.get(key) != contract.get(key):
            errors.append(f"{label}:{key}")
    if status == WITNESSED_STATUS:
        contract_forms = set(_unique(contract.get("natural_form_ids", [])))
        contract_sources = set(_unique(contract.get("source_return_ids", [])))
        derived_forms = set(_unique(derivation.get("natural_form_ids", [])))
        derived_sources = set(_unique(derivation.get("source_return_ids", [])))
        if not derived_forms or not derived_forms.issubset(contract_forms):
            errors.append(f"{label}:natural-forms")
        if not derived_sources or not derived_sources.issubset(contract_sources):
            errors.append(f"{label}:source-returns")
        if derivation.get("source_boundary_only") is not False:
            errors.append(f"{label}:not-source-boundary")
    return errors


def _perspective_closure_errors(contract: Mapping[str, Any]) -> list[str]:
    closure = contract.get("perspective_closure")
    if not isinstance(closure, Mapping):
        return ["perspective-closure:missing"]
    errors: list[str] = []
    perspective = str(contract.get("perspective_id") or "")
    status = str(contract.get("status") or "")
    if closure.get("active_perspective_id") != perspective:
        errors.append("perspective-closure:active-perspective")
    if closure.get("equality_basis") != (
        "EXPLICIT_TRANSLATED_PERSPECTIVE_READINGS"
    ):
        errors.append("perspective-closure:equality-basis")
    if closure.get("source_provenance_defines_equality") is not False:
        errors.append("perspective-closure:provenance-authority")

    readings = closure.get("readings")
    translations = closure.get("translations")
    if not isinstance(readings, Mapping):
        errors.append("perspective-closure:readings")
        readings = {}
    if not isinstance(translations, list):
        errors.append("perspective-closure:translations")
        translations = []
    projection = contract.get("projection", {})
    states = {
        str(item.get("id") or "")
        for item in projection.get("states", [])
        if isinstance(item, Mapping) and item.get("id")
    }

    if status != WITNESSED_STATUS:
        if closure.get("status") != status:
            errors.append("perspective-closure:status")
        if readings or translations or closure.get("kernel") not in ([], None):
            errors.append("perspective-closure:open-content")
        return errors

    if closure.get("status") != WITNESSED_STATUS:
        errors.append("perspective-closure:status")
    normalized: dict[str, dict[str, str]] = {}
    for raw_perspective, raw_reading in readings.items():
        perspective_id = str(raw_perspective)
        if not perspective_id or not isinstance(raw_reading, Mapping):
            errors.append("perspective-closure:reading-shape")
            continue
        reading = {
            str(state_id): str(value)
            for state_id, value in raw_reading.items()
        }
        if set(reading) != states:
            errors.append(f"perspective-closure:{perspective_id}:carrier")
        normalized[perspective_id] = reading
    if perspective not in normalized:
        errors.append("perspective-closure:active-reading")
    elif dict(projection.get("reading", {})) != normalized[perspective]:
        errors.append("perspective-closure:projection-reading")

    kernels = {
        perspective_id: _reading_kernel(reading)
        for perspective_id, reading in normalized.items()
    }
    common_kernel = next(iter(kernels.values()), [])
    if any(kernel != common_kernel for kernel in kernels.values()):
        errors.append("perspective-closure:unequal-kernels")
    if closure.get("kernel") != common_kernel:
        errors.append("perspective-closure:kernel")
    if closure.get("kernels") != kernels:
        errors.append("perspective-closure:kernels")

    graph = {perspective_id: set() for perspective_id in normalized}
    contract_sources = set(_unique(contract.get("source_return_ids", [])))
    translation_ids: list[str] = []
    for raw in translations:
        if not isinstance(raw, Mapping):
            errors.append("perspective-closure:translation-shape")
            continue
        translation_id = str(raw.get("id") or "")
        translation_ids.append(translation_id)
        source = str(raw.get("source_perspective_id") or "")
        target = str(raw.get("target_perspective_id") or "")
        mapping = raw.get("display_translation")
        if (
            not translation_id
            or source == target
            or source not in normalized
            or target not in normalized
            or not isinstance(mapping, Mapping)
        ):
            errors.append(f"perspective-closure:{translation_id}:endpoints")
            continue
        expected: dict[str, str] = {}
        well_defined = True
        for state_id in states:
            source_value = normalized[source].get(state_id)
            target_value = normalized[target].get(state_id)
            if source_value is None or target_value is None:
                well_defined = False
                continue
            prior = expected.get(source_value)
            if prior is not None and prior != target_value:
                well_defined = False
            expected[source_value] = target_value
        faithful = bool(
            well_defined
            and {str(key): str(value) for key, value in mapping.items()} == expected
            and len(set(expected)) == len(set(expected.values()))
        )
        source_ids = set(_unique(raw.get("source_return_ids", [])))
        if not source_ids or not source_ids.issubset(contract_sources):
            errors.append(f"perspective-closure:{translation_id}:provenance")
        if (
            raw.get("witnessed") is not True
            or raw.get("well_defined") is not True
            or raw.get("faithful") is not True
            or raw.get("same_kernel") is not True
            or not faithful
            or kernels.get(source) != kernels.get(target)
        ):
            errors.append(f"perspective-closure:{translation_id}:not-faithful")
        else:
            graph[source].add(target)
            graph[target].add(source)
    if len(translation_ids) != len(set(translation_ids)):
        errors.append("perspective-closure:duplicate-translation")
    if graph:
        reached = {next(iter(graph))}
        frontier = list(reached)
        while frontier:
            current = frontier.pop()
            for neighbour in graph[current]:
                if neighbour not in reached:
                    reached.add(neighbour)
                    frontier.append(neighbour)
        if reached != set(graph):
            errors.append("perspective-closure:disconnected")
    return errors


def _audit_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if contract.get("protocol") != PROTOCOL:
        errors.append("contract:protocol")
    if contract.get("schema") != SCHEMA:
        errors.append("contract:schema")
    if contract.get("builder_version") != BUILDER_VERSION:
        errors.append("contract:builder-version")
    status = str(contract.get("status") or "")
    if status not in {OPEN_STATUS, BLOCKED_STATUS, WITNESSED_STATUS}:
        errors.append("contract:status")
    if contract.get("renderer_relation") != _renderer_relation():
        errors.append("renderer:external-vocabulary-or-authority")
    errors.extend(_perspective_closure_errors(contract))
    continuation_index = contract.get("continuation_index")
    raw_lineage = contract.get("continuation_lineage_ids")
    if (
        not isinstance(continuation_index, int)
        or isinstance(continuation_index, bool)
        or continuation_index < 0
    ):
        errors.append("continuation:index")
    if not isinstance(raw_lineage, list):
        errors.append("continuation:lineage-shape")
        lineage_ids: list[str] = []
    else:
        lineage_ids = _unique(raw_lineage)
        if lineage_ids != [str(item) for item in raw_lineage]:
            errors.append("continuation:lineage-unique")
    if isinstance(continuation_index, int) and not isinstance(
        continuation_index, bool
    ):
        if continuation_index != len(lineage_ids):
            errors.append("continuation:lineage-count")
    raw_source_ids = contract.get("source_return_ids", [])
    source_ids = set(
        _unique(raw_source_ids)
        if isinstance(raw_source_ids, (list, tuple))
        else []
    )
    if not set(lineage_ids).issubset(source_ids):
        errors.append("continuation:lineage-provenance")
    focus_event_id = str(contract.get("focus_event_id") or "")
    if (
        status == WITNESSED_STATUS
        and lineage_ids
        and focus_event_id in source_ids
        and lineage_ids[-1] != focus_event_id
    ):
        errors.append("continuation:focus")
    if contract.get("closure_process") != _closure_process(contract):
        errors.append("closure-process:not-derived")
    claims = contract.get("claims", {})
    for claim in (
        "truth_issued",
        "physical_law_claimed",
        "consciousness_claimed",
        "external_resource_admitted",
    ):
        if claims.get(claim) is not False:
            errors.append(f"claims:{claim}")

    projection = contract.get("projection", {})
    if projection.get("active_perspective_id") != contract.get("perspective_id"):
        errors.append("projection:perspective")
    reading = projection.get("reading", {})
    if not isinstance(reading, Mapping):
        errors.append("projection:reading")
        reading = {}
    states = list(projection.get("states", []))
    fibres = list(projection.get("equality_fibres", []))
    translations = list(projection.get("translations", []))
    potentials = list(projection.get("potentials", []))
    state_ids = [
        str(item.get("id") or "")
        for item in states
        if isinstance(item, Mapping)
    ]
    event_ids = [
        str(item.get("event_id") or "")
        for item in states
        if isinstance(item, Mapping)
    ]
    if any(not item for item in state_ids) or len(state_ids) != len(set(state_ids)):
        errors.append("projection:state-identity")
    if any(not item for item in event_ids) or len(event_ids) != len(set(event_ids)):
        errors.append("projection:event-identity")
    forms = set(_unique(contract.get("natural_form_ids", [])))
    sources = set(_unique(contract.get("source_return_ids", [])))
    for item in states:
        if not isinstance(item, Mapping):
            errors.append("projection:state-not-object")
            continue
        state_id = str(item.get("id") or "")
        item_sources = set(_unique(item.get("source_return_ids", [])))
        if status == WITNESSED_STATUS and (
            item.get("natural_form_id") not in forms
            or not item_sources
            or not item_sources.issubset(sources)
        ):
            errors.append(f"state:{state_id}:not-admitted")
        if reading.get(state_id) != item.get("display_fibre_id"):
            errors.append(f"state:{state_id}:not-active-reading")
        if not isinstance(item.get("source_trace"), str) or not item.get("source_trace"):
            errors.append(f"state:{state_id}:not-source-return")
        errors.extend(
            _derivation_errors(contract, item.get("derivation"), label=f"state:{state_id}")
        )

    fibre_members: list[str] = []
    fibre_ids: list[str] = []
    for item in fibres:
        if not isinstance(item, Mapping):
            errors.append("projection:fibre-not-object")
            continue
        fibre_id = str(item.get("id") or "")
        members = _unique(item.get("member_state_ids", []))
        fibre_ids.append(fibre_id)
        fibre_members.extend(members)
        if fibre_id not in forms:
            errors.append(f"fibre:{fibre_id}:not-natural-form")
        if not members or not set(members).issubset(set(state_ids)):
            errors.append(f"fibre:{fibre_id}:members")
        if item.get("closure_fixed") is not True:
            errors.append(f"fibre:{fibre_id}:not-closure-fixed")
        expected_displays = sorted(
            {str(reading[member]) for member in members if member in reading}
        )
        if sorted(set(item.get("display_fibre_ids", []))) != expected_displays:
            errors.append(f"fibre:{fibre_id}:reading")
        errors.extend(
            _derivation_errors(contract, item.get("derivation"), label=f"fibre:{fibre_id}")
        )
    if len(fibre_ids) != len(set(fibre_ids)):
        errors.append("projection:duplicate-fibre-id")
    if status == WITNESSED_STATUS and sorted(fibre_members) != sorted(state_ids):
        errors.append("projection:fibres-do-not-partition-states")

    relation_ids: list[str] = []
    for kind, rows in (("translation", translations), ("potential", potentials)):
        for item in rows:
            if not isinstance(item, Mapping):
                errors.append(f"projection:{kind}-not-object")
                continue
            relation_id = str(item.get("id") or "")
            relation_ids.append(relation_id)
            if not relation_id:
                errors.append(f"{kind}:empty-id")
            if kind == "translation":
                if str(item.get("source_state_id") or "") not in state_ids:
                    errors.append(f"translation:{relation_id}:source")
                if str(item.get("target_state_id") or "") not in state_ids:
                    errors.append(f"translation:{relation_id}:target")
                if item.get("executes_as_equality") is True and reading.get(
                    item.get("source_state_id")
                ) != reading.get(item.get("target_state_id")):
                    errors.append(f"translation:{relation_id}:cross-fibre-equality")
            elif item.get("target_state_id") is not None and str(
                item.get("target_state_id")
            ) not in state_ids:
                errors.append(f"potential:{relation_id}:target")
            if (
                item.get("relation_status") != WITNESSED_STATUS
                and item.get("executes_as_equality") is True
            ):
                errors.append(f"{kind}:{relation_id}:open-equality")
            errors.extend(
                _derivation_errors(
                    contract,
                    item.get("derivation"),
                    label=f"{kind}:{relation_id}",
                )
            )
    if len(relation_ids) != len(set(relation_ids)):
        errors.append("projection:duplicate-relation-id")

    visualization = projection.get("visualization", {})
    errors.extend(
        _derivation_errors(
            contract,
            visualization.get("derivation"),
            label="visualization",
        )
    )
    relation_basis = {
        "reading": dict(reading),
        "states": [
            {
                key: value
                for key, value in item.items()
                if key not in {"source_trace", "derivation"}
            }
            for item in states
            if isinstance(item, Mapping)
        ],
        "equality_fibres": [
            {key: value for key, value in item.items() if key != "derivation"}
            for item in fibres
            if isinstance(item, Mapping)
        ],
        "translations": [
            {key: value for key, value in item.items() if key != "derivation"}
            for item in translations
            if isinstance(item, Mapping)
        ],
        "potentials": [
            {key: value for key, value in item.items() if key != "derivation"}
            for item in potentials
            if isinstance(item, Mapping)
        ],
    }
    focus_form = (
        str((contract.get("return_relation") or {}).get("parent_natural_form_id"))
        if (contract.get("return_relation") or {}).get("parent_natural_form_id")
        else None
    )
    expected_visualization = _projective_visualization(
        states=[dict(item) for item in states if isinstance(item, Mapping)],
        equality_fibres=[
            dict(item) for item in fibres if isinstance(item, Mapping)
        ],
        translations=[
            dict(item) for item in translations if isinstance(item, Mapping)
        ],
        potentials=[dict(item) for item in potentials if isinstance(item, Mapping)],
        focus_natural_form_id=focus_form,
        derivation=dict(visualization.get("derivation") or {}),
    )
    expected_visualization["relation_digest"] = _digest(
        "projection-relation", relation_basis
    )
    if visualization != expected_visualization:
        errors.append("visualization:not-exact-projection")

    return_relation = contract.get("return_relation")
    execution = contract.get("execution", {})
    if status == BLOCKED_STATUS:
        if return_relation is not None:
            errors.append("blocked:return-relation")
        if states or fibres or translations or potentials:
            errors.append("blocked:visible-relation")
    elif not isinstance(return_relation, Mapping):
        errors.append("return:missing")
    else:
        if return_relation.get("kind") != "SOURCE_PRESERVING_TRANSLATIONAL_RETURN":
            errors.append("return:kind")
        if return_relation.get("full_surface_aperture") is not True:
            errors.append("return:not-full-surface")
        if return_relation.get("visible_control") is not False:
            errors.append("return:visible-control")
        if return_relation.get("requires_exact_source_return") is not True:
            errors.append("return:not-exact-source")
        if return_relation.get("creates_truth_directly") is not False:
            errors.append("return:creates-truth")
        errors.extend(
            _derivation_errors(contract, return_relation.get("derivation"), label="return")
        )
        relation_body = {
            key: value for key, value in return_relation.items() if key != "id"
        }
        if return_relation.get("id") != _digest("return-relation", relation_body):
            errors.append("return:id")
        if execution.get("return_relation_id") != return_relation.get("id"):
            errors.append("execution:return-relation")
    if execution.get("endpoint_template") != RETURN_ENDPOINT_TEMPLATE:
        errors.append("execution:endpoint-template")
    if execution.get("contract_revalidation_required") is not True:
        errors.append("execution:revalidation")
    if execution.get("only_relation_extension") is not True:
        errors.append("execution:not-relation-only")
    if execution.get("closure_only") is not True:
        errors.append("execution:not-closure-only")

    if status == OPEN_STATUS:
        if states or fibres or translations or potentials:
            errors.append("open:substitute-content")
        if forms or sources:
            errors.append("open:claims-derived-carrier")
        if contract.get("claims", {}).get("natural_form_admitted") is not False:
            errors.append("open:claims-natural-form")
    elif status == WITNESSED_STATUS:
        for key in (
            "closure_derivation_id",
            "visual_closure_id",
            "nrrf843_ui_id",
            "interaction_closure_id",
            "field_event_seq",
            "focus_event_id",
        ):
            if not contract.get(key):
                errors.append(f"witnessed:{key}")
        if not forms or not sources or not states or not fibres:
            errors.append("witnessed:empty-projection")
        if not all(contract.get("readiness_checks", {}).values()):
            errors.append("witnessed:readiness")
        if contract.get("claims", {}).get("natural_form_admitted") is not True:
            errors.append("witnessed:claims-natural-form")

    ordered_errors = sorted(Counter(errors))
    derivation_error = any(
        suffix in item
        for item in ordered_errors
        for suffix in (
            ":basis",
            ":status",
            ":perspective",
            ":closure_derivation_id",
            ":visual_closure_id",
            ":nrrf843_ui_id",
            ":interaction_closure_id",
            ":field_event_seq",
            ":natural-forms",
            ":source-returns",
            ":missing-derivation",
        )
    )
    return {
        "state_count": len(states),
        "equality_fibre_count": len(fibres),
        "translation_count": len(translations),
        "potential_count": len(potentials),
        "all_visual_existence_has_exact_derivation": not derivation_error,
        "every_visible_word_is_a_source_return": not any(
            item.endswith(":not-source-return") for item in ordered_errors
        ),
        "equality_fibres_partition_visible_states": (
            "projection:fibres-do-not-partition-states" not in ordered_errors
        ),
        "active_reading_determines_projection": not any(
            item.endswith(":not-active-reading") for item in ordered_errors
        ),
        "visualization_is_exact_relation_projection": (
            "visualization:not-exact-projection" not in ordered_errors
        ),
        "open_relations_do_not_execute_as_equality": not any(
            item.endswith(":open-equality") for item in ordered_errors
        ),
        "full_surface_is_only_return_aperture": not any(
            item.startswith("return:") or item.startswith("execution:")
            for item in ordered_errors
        ),
        "fixed_visible_controls": [],
        "authored_visible_vocabulary": [],
        "semantic_fallback": False,
        "errors": ordered_errors,
        "closure_only_execution": not ordered_errors,
    }


def validate_ui_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    structural = _audit_contract(contract)
    stored_audit = contract.get("audit")
    audit_matches = isinstance(stored_audit, Mapping) and dict(stored_audit) == structural
    body = {key: value for key, value in contract.items() if key != "id"}
    expected_id = _digest("translational-visualization", body)
    id_matches = contract.get("id") == expected_id
    return {
        **structural,
        "stored_audit_matches_recomputation": audit_matches,
        "contract_id_matches_content": id_matches,
        "valid": bool(structural["closure_only_execution"] and audit_matches and id_matches),
    }


__all__ = [
    "BLOCKED_STATUS",
    "BUILDER_VERSION",
    "EXECUTION_ENDPOINT_TEMPLATE",
    "OPEN_STATUS",
    "PROTOCOL",
    "RETURN_ENDPOINT_TEMPLATE",
    "SCHEMA",
    "WITNESSED_STATUS",
    "attach_perspective_closure",
    "derive_closure_ui_contract",
    "derive_open_ui_contract",
    "validate_ui_contract",
]
