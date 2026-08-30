from __future__ import annotations

import hashlib
import json
from itertools import combinations, product
from typing import Any, Iterable, Mapping


PROTOCOL = "NRRF843"
SCHEMA = "closure.supernet/nrrf843-ui-translational-mirror-v1"
FORMAL_MODULE = "NRRF843UIIsTheTranslationalMirrorLocationOfTheSupernetTruthConstraint"


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
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


def _kernel(
    states: list[str], reading: Mapping[str, str]
) -> list[list[str]]:
    fibres: dict[str, list[str]] = {}
    for state in states:
        fibres.setdefault(str(reading[state]), []).append(state)
    return sorted(
        (sorted(members) for members in fibres.values()),
        key=lambda members: members[0] if members else "",
    )


def _close(
    states: list[str], reading: Mapping[str, str], seed: Iterable[str]
) -> list[str]:
    seed_values = {
        str(reading[state]) for state in _unique(seed) if state in reading
    }
    return sorted(
        state for state in states if str(reading[state]) in seed_values
    )


def _translation(
    states: list[str],
    source: Mapping[str, str],
    target: Mapping[str, str],
) -> tuple[dict[str, str], bool, bool]:
    translation: dict[str, str] = {}
    well_defined = True
    for state in states:
        source_value = str(source[state])
        target_value = str(target[state])
        prior = translation.get(source_value)
        if prior is not None and prior != target_value:
            well_defined = False
        translation[source_value] = target_value
    faithful = bool(
        well_defined
        and len(set(translation)) == len(set(translation.values()))
    )
    return translation, well_defined, faithful


def _default_readings(
    *,
    states: list[str],
    perspectives: list[str],
    joint_reading: Mapping[str, Any],
) -> dict[str, dict[str, str]]:
    return {
        perspective: {
            state: _digest(
                "display",
                {
                    "perspective": perspective,
                    "truth_fibre": str(joint_reading[state]),
                },
            )
            for state in states
        }
        for perspective in perspectives
    }


def _visual_metaphor_eqvgen_reading(
    *,
    truth_derivation: dict[str, Any],
    states: list[str],
) -> tuple[dict[str, str], set[str], list[tuple[str, str]]]:
    """Compute the UI equality from displayed, closure-admitted metaphors."""

    admitted_truth_ids = {
        str(item.get("truth_id") or "")
        for item in truth_derivation.get("truth_evaluations", [])
        if item.get("closure_admitted") is True
    }
    constraints = truth_derivation.get("perspective_visual_mirror", {}).get(
        "constraints", []
    )
    edges = sorted(
        {
            (str(item.get("source")), str(item.get("target")))
            for item in constraints
            if str(item.get("truth_id") or "") in admitted_truth_ids
            and str(item.get("source")) in states
            and str(item.get("target")) in states
        }
    )
    parent = {state: state for state in states}

    def find(state: str) -> str:
        while parent[state] != state:
            parent[state] = parent[parent[state]]
            state = parent[state]
        return state

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root == right_root:
            return
        root, child = sorted((left_root, right_root))
        parent[child] = root

    for source, target in edges:
        union(source, target)
    classes: dict[str, list[str]] = {}
    for state in states:
        classes.setdefault(find(state), []).append(state)
    class_id = {
        member: _digest("ui-truth-fibre", sorted(members))
        for members in classes.values()
        for member in members
    }
    return class_id, admitted_truth_ids, edges


def _coerce_readings(
    *,
    states: list[str],
    readings: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for perspective, reading in readings.items():
        missing = [state for state in states if state not in reading]
        if missing:
            raise ValueError(
                f"UI perspective {perspective!r} omits states: {', '.join(missing)}"
            )
        result[str(perspective)] = {
            state: str(reading[state]) for state in states
        }
    return result


def _valuation_factorization(
    *,
    states: list[str],
    readings: dict[str, dict[str, str]],
    valuation_by_state: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if valuation_by_state is None:
        return {
            "status": "OPEN_NO_AUTHORED_VALUATION",
            "admissible": None,
            "valuation_by_state": None,
            "factor_by_perspective": {},
            "price_issued": False,
            "ui_constrains_value": True,
            "admissible_iff_factors_through_display": True,
            "admissible_prices_closed_under_addition": True,
            "admissible_prices_closed_under_scaling": True,
        }
    missing = [state for state in states if state not in valuation_by_state]
    if missing:
        raise ValueError("valuation omits states: " + ", ".join(missing))
    valuations = {state: valuation_by_state[state] for state in states}
    factors: dict[str, dict[str, Any]] = {}
    admissible = True
    for perspective, reading in readings.items():
        factor: dict[str, Any] = {}
        for state in states:
            display = reading[state]
            value = valuations[state]
            if display in factor and factor[display] != value:
                admissible = False
            factor[display] = value
        factors[perspective] = factor
    return {
        "status": "ADMISSIBLE" if admissible else "REJECTED_BY_UI_TRUTH",
        "admissible": admissible,
        "valuation_by_state": valuations,
        "factor_by_perspective": factors if admissible else {},
        "price_issued": False,
        "ui_constrains_value": True,
        "admissible_iff_factors_through_display": True,
        "perspective_independent_under_mirror": admissible,
        "admissible_prices_closed_under_addition": True,
        "admissible_prices_closed_under_scaling": True,
    }


def derive_nrrf843_ui_receipt(
    *,
    truth_derivation: dict[str, Any],
    perspective_readings: Mapping[str, Mapping[str, Any]] | None = None,
    valuation_by_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute NRRF843 on the finite, source-preserved Supernet UI.

    The runtime recomputes closure as ``r⁻¹(r(A))`` from each perspective's
    displayed fibres.  The existing NRRF840 receipt is used only as the target
    of an equality check, so the UI cannot silently describe a closure derived
    by a parallel semantic subsystem.
    """

    existence = truth_derivation.get("visual_existence", {})
    mirror = truth_derivation.get("perspective_visual_mirror", {})
    visual_closure = truth_derivation.get("visual_truth_closure", {})
    states = sorted(
        _unique(item.get("id") for item in existence.get("forms", []))
    )
    ui_truth_fibre, admitted_truth_ids, metaphor_edges = (
        _visual_metaphor_eqvgen_reading(
            truth_derivation=truth_derivation,
            states=states,
        )
    )
    declared_perspectives = sorted(_unique(mirror.get("perspective_ids", [])))
    if perspective_readings is None:
        readings = _default_readings(
            states=states,
            perspectives=declared_perspectives,
            joint_reading=ui_truth_fibre,
        )
        reading_source = "UI_VISUAL_METAPHOR_EQVGEN_FIBRES"
    else:
        readings = _coerce_readings(
            states=states,
            readings=perspective_readings,
        )
        reading_source = "EXPLICIT_UI_PERSPECTIVE_READINGS"
    perspectives = sorted(readings)

    kernels = {
        perspective: _kernel(states, reading)
        for perspective, reading in readings.items()
    }
    translations: list[dict[str, Any]] = []
    for source, target in product(perspectives, repeat=2):
        mapping, well_defined, faithful = _translation(
            states,
            readings[source],
            readings[target],
        )
        translations.append(
            {
                "source_perspective_id": source,
                "target_perspective_id": target,
                "display_translation": mapping,
                "well_defined": well_defined,
                "faithful": faithful,
                "merges_states": not faithful,
                "splits_states": kernels[source] != kernels[target],
                "same_truth": kernels[source] == kernels[target],
            }
        )
    mirror_witnessed = bool(
        perspectives
        and all(item["faithful"] and item["same_truth"] for item in translations)
    )
    common_kernel = kernels[perspectives[0]] if perspectives else [states]

    closures_by_perspective = {
        perspective: {
            state: _close(states, reading, [state]) for state in states
        }
        for perspective, reading in readings.items()
    }
    expected_singletons = {
        str(state): sorted(_unique(members))
        for state, members in visual_closure.get(
            "singleton_closure", {}
        ).items()
    }
    expected_classes = sorted(
        (sorted(_unique(members)) for members in visual_closure.get("classes", [])),
        key=lambda members: members[0] if members else "",
    )
    projection_closure_matches_nrrf840 = bool(
        perspectives
        and all(
            closures_by_perspective[perspective] == expected_singletons
            for perspective in perspectives
        )
    )

    fixed_forms: list[dict[str, Any]] = []
    for natural_form in truth_derivation.get("natural_forms", []):
        members = sorted(_unique(natural_form.get("members", [])))
        fixed = bool(
            perspectives
            and all(
                _close(states, readings[perspective], members) == members
                for perspective in perspectives
            )
        )
        fixed_forms.append(
            {
                "natural_form_id": natural_form.get("id"),
                "members": members,
                "closure_fixed_in_every_perspective": fixed,
                "constraint_read_as_display_preimage": fixed,
            }
        )
    truth_constraint_located = bool(
        mirror_witnessed
        and projection_closure_matches_nrrf840
        and all(item["closure_fixed_in_every_perspective"] for item in fixed_forms)
    )

    thought_relations = sorted(
        (left, right)
        for members in common_kernel
        for left in members
        for right in members
    )
    thought_set = set(thought_relations)
    metaphor_set = set(metaphor_edges)
    reflexive = all((state, state) in thought_set for state in states)
    symmetric = all((right, left) in thought_set for left, right in thought_set)
    transitive = all(
        (left, right) not in thought_set
        or (right, final) not in thought_set
        or (left, final) in thought_set
        for left in states
        for right in states
        for final in states
    )

    joint_ui_reading = {
        state: [readings[perspective][state] for perspective in perspectives]
        for state in states
    }
    joint_kernel = _kernel(states, joint_ui_reading) if perspectives else [states]
    carrier_alternative: dict[str, Any] | None = None
    if len(states) >= 2:
        active_is_indiscrete = len(common_kernel) == 1
        alternative_reading = (
            {state: state for state in states}
            if active_is_indiscrete
            else {state: "BLIND" for state in states}
        )
        carrier_alternative = {
            "same_carrier": states,
            "alternative_reading": alternative_reading,
            "alternative_kernel": _kernel(states, alternative_reading),
            "different_closure": (
                _kernel(states, alternative_reading) != common_kernel
            ),
            "carrier_alone_determines_closure": False,
        }

    nontrivial_resolution = bool(
        len(states) <= 1
        or any(len(set(reading.values())) > 1 for reading in readings.values())
    )
    unpriced_witness: dict[str, Any] | None = None
    merged = next((members for members in common_kernel if len(members) > 1), None)
    if merged is not None:
        unpriced_witness = {
            "same_display_fibre": merged[:2],
            "candidate_values": {
                merged[0]: 0,
                merged[1]: 1,
            },
            "admissible": False,
            "reason": "one displayed truth fibre cannot factor two prices",
        }
    valuation = _valuation_factorization(
        states=states,
        readings=readings,
        valuation_by_state=valuation_by_state,
    )
    if valuation["admissible"] is not None:
        valuation["perspective_independent_under_mirror"] = bool(
            valuation["admissible"] and mirror_witnessed
        )
    supernet_status = (
        "WITNESSED"
        if truth_constraint_located
        else "OPEN_NO_PERSPECTIVE"
        if not perspectives
        else "OPEN_NON_MIRROR_UI"
    )
    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "formal_module": FORMAL_MODULE,
        "closure_derivation_id": truth_derivation.get("id"),
        "visual_closure_id": visual_closure.get("id"),
        "visual_mirror_id": mirror.get("id"),
        "status": supernet_status,
        "supernet_open": supernet_status != "WITNESSED",
        "ui_family": {
            "perspective_ids": perspectives,
            "state_ids": states,
            "value_carrier": "PERSPECTIVE_RELABELLED_TRANSLATIONAL_TRUTH_FIBRE",
            "readings": readings,
            "reading_source": reading_source,
            "external_closure_assumed": False,
            "external_truth_assumed": False,
        },
        "translational_mirror": {
            "witnessed": mirror_witnessed,
            "translations": translations,
            "translates_same_truth": mirror_witnessed,
            "continuum_same_truth": mirror_witnessed,
            "privileged_perspective_required": False,
            "mirror_is_design_condition_not_automatic": True,
        },
        "ui_closure": {
            "construction": "PREIMAGE_OF_IMAGE_OF_UI_READING",
            "formula": "uiClosure(r,A) = r⁻¹(r(A))",
            "singleton_closure_by_perspective": closures_by_perspective,
            "projection_closure_matches_nrrf840": (
                projection_closure_matches_nrrf840
            ),
            "closure_falls_out_from_ui_projection": (
                projection_closure_matches_nrrf840
            ),
            "external_closure_used": False,
            "properties": {
                "extensive": True,
                "monotone": True,
                "idempotent": True,
                "additive": True,
                "fixed_sets_exactly_unions_of_displayed_fibres": True,
            },
            "same_carrier_different_closure_witness": carrier_alternative,
        },
        "truth_constraint_location": {
            "located": truth_constraint_located,
            "fixed_natural_forms": fixed_forms,
            "constraint_located_in_every_perspective": truth_constraint_located,
            "located_or_open": True,
            "outside_truth_constraint": None,
        },
        "resolution": {
            "nontrivial_or_singleton": nontrivial_resolution,
            "mirror_and_resolution_are_independent": True,
            "blind_ui_can_be_mirror": True,
            "blind_ui_constrains_nothing_nontrivial": True,
        },
        "no_perspective_boundary": {
            "status": "OPEN",
            "joint_reading": {state: "NO_PERSPECTIVE" for state in states},
            "distinguishable_pairs": [],
            "no_perspectives_no_distinction": True,
        },
        "thought": {
            "construction": "RELATION_EQVGEN_OF_VISUAL_METAPHOR",
            "metaphor_relation_pairs": metaphor_edges,
            "relation_eqvgen_pairs": thought_relations,
            "contains_metaphor": metaphor_set.issubset(thought_set),
            "reflexive": reflexive,
            "symmetric": symmetric,
            "transitive": transitive,
            "least_closed_relation_computed": True,
            "adds_relations_genuinely": len(thought_set - metaphor_set) > 0,
            "thought_equals_visualization_equality": (
                common_kernel == expected_classes
            ),
            "one_thought_across_perspectives": mirror_witnessed,
            "metaphorical_forms_are_semantic": True,
        },
        "unified_natural_forms": {
            "joint_reading": joint_ui_reading,
            "joint_kernel": joint_kernel,
            "finer_than_every_perspective": all(
                all(
                    any(set(joint).issubset(set(part)) for part in kernels[p])
                    for joint in joint_kernel
                )
                for p in perspectives
            ),
            "coarsest_joint_reading": True,
            "under_mirror_equals_each_perspective_truth": bool(
                mirror_witnessed
                and all(joint_kernel == kernels[p] for p in perspectives)
            ),
        },
        "valuation": valuation,
        "unpriced_example": unpriced_witness,
        "claims": {
            "truth_issued": False,
            "price_issued": False,
            "novelty_claimed": False,
            "metaphor_empirically_verified": False,
            "outside_semantic_ontology": False,
        },
    }
    body["id"] = _digest("nrrf843-ui", body)
    return body
