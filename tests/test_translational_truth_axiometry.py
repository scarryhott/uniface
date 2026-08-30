from __future__ import annotations

import json

import pytest

from closure_supernet.translational_truth_axiometry import (
    ConditionWitness,
    EXTERNAL_RENDERER_CONTRACT,
    RendererRole,
    TruthVerdict,
    WitnessKind,
    WitnessStatus,
    derive_closure,
    derive_interface_natural_form,
    derive_translational_truth_axiometry,
)


def _equation(
    equation_id: str,
    source: str,
    target: str,
    *,
    deterministic: bool = True,
) -> dict[str, object]:
    return {
        "id": equation_id,
        "source": source,
        "target": target,
        "equation": f"translate({source}) = translate({target})",
        "deterministic": deterministic,
        "source_return_ids": [f"return:{source}", f"return:{target}"],
        "provenance": [f"equation-receipt:{equation_id}"],
    }


def _admitted_truth(
    truth_id: str,
    source: str,
    target: str,
) -> dict[str, object]:
    return {
        "id": truth_id,
        "source": source,
        "target": target,
        "verdict": "TRUE",
        "visual_equation": _equation(f"eq:{truth_id}", source, target),
        "compatible": {
            "witnessed": True,
            "provenance": [f"compatibility-receipt:{truth_id}"],
        },
        "closure_explicit": {
            "witnessed": True,
            "provenance": [f"closure-explicit-receipt:{truth_id}"],
        },
        "source_return_ids": [f"source-return:{truth_id}"],
        "provenance": [f"truth-receipt:{truth_id}"],
    }


def test_only_true_compatible_explicit_cross_truth_generates_equality() -> None:
    derivation = derive_translational_truth_axiometry(
        ["a", "b", "c"],
        [
            _admitted_truth("truth:a-b", "a", "b"),
            {
                **_admitted_truth("truth:open", "b", "c"),
                "verdict": "OPEN",
            },
            {
                **_admitted_truth("truth:false", "a", "c"),
                "verdict": "FALSE",
            },
            _admitted_truth("truth:missing", "c", "missing"),
            {
                **_admitted_truth("truth:not-compatible", "b", "c"),
                "compatible": False,
            },
            {
                **_admitted_truth("truth:not-explicit", "b", "c"),
                "closure_explicit": False,
            },
        ],
    )

    identity_witnesses = [
        item for item in derivation.witnesses if item.kind is WitnessKind.IDENTITY
    ]
    cross_witnesses = [
        item
        for item in derivation.witnesses
        if item.kind is WitnessKind.RELATIVE_TRANSLATION
    ]
    assert len(identity_witnesses) == 3
    assert {item.truth_id for item in cross_witnesses} == {
        "truth:a-b",
        "truth:not-explicit",
    }
    assert set(derivation.equivalence_closure.classes) == {("a", "b"), ("c",)}
    assert derivation.relation("a", "b") is not None
    assert derivation.relation("b", "a") is not None
    assert derivation.relation("b", "c") is None

    evaluations = {item.truth_id: item for item in derivation.truth_evaluations}
    assert evaluations["truth:a-b"].status is WitnessStatus.WITNESSED
    assert evaluations["truth:a-b"].meets_visual_existence is True
    assert evaluations["truth:open"].reason == (
        "cross_translation_requires_true_verdict"
    )
    assert evaluations["truth:false"].status is WitnessStatus.NOT_WITNESSED
    assert evaluations["truth:missing"].endpoints_exist is False
    assert evaluations["truth:not-compatible"].reason == (
        "cross_translation_requires_compatibility_witness"
    )
    assert evaluations["truth:not-explicit"].status is WitnessStatus.WITNESSED
    assert evaluations["truth:not-explicit"].closure_admitted is False
    assert evaluations["truth:not-explicit"].reason == (
        "translational_truth_axiom_waits_for_explicit_closure_meeting"
    )
    meetings = {
        meeting.truth_id: meeting for meeting in derivation.closure_meetings
    }
    assert meetings["truth:a-b"].admitted is True
    assert meetings["truth:not-explicit"].admitted is False


def test_identity_is_intrinsic_and_cannot_be_revoked_by_false_claim() -> None:
    derivation = derive_closure(
        [{"id": "self", "existence_provenance": ["return:self"]}],
        [
            {
                "id": "false-self-reading",
                "source": "self",
                "target": "self",
                "verdict": TruthVerdict.FALSE,
            }
        ],
    )

    evaluation = derivation.truth_evaluations[0]
    assert evaluation.status is WitnessStatus.NOT_WITNESSED
    assert evaluation.reason == (
        "identity_relation_intrinsic_but_claim_verdict_not_true"
    )
    assert evaluation.witness_id is None
    relation = derivation.relation("self", "self")
    assert relation is not None
    assert relation.closure_operations == ("REFLEXIVITY",)
    assert len(derivation.axiometry.axioms) == 1


def test_authored_form_labels_and_selector_versions_cannot_define_equality() -> None:
    first = derive_closure(
        [
            {"id": "a", "natural_form_id": "authored-same"},
            {"id": "b", "natural_form_id": "authored-same"},
        ],
        [],
    )
    assert first.relation("a", "b") is None
    assert first.equivalence_closure.classes == (("a",), ("b",))

    truth = _admitted_truth("truth:a-b", "a", "b")
    second = derive_closure(
        ["b", "a"],
        [{**truth, "selector_version": "product-selector/arbitrary-v99"}],
    )
    third = derive_closure(
        ["a", "b"],
        [{**truth, "selector_version": "different-selector"}],
    )
    assert second.natural_form_for("a").id == third.natural_form_for("a").id
    assert second.natural_form_for("a").members == ("a", "b")


def test_natural_form_changes_only_when_truth_closure_changes() -> None:
    open_derivation = derive_closure(
        ["a", "b"],
        [{**_admitted_truth("truth:a-b", "a", "b"), "verdict": "OPEN"}],
    )
    closed_derivation = derive_closure(
        ["a", "b"],
        [_admitted_truth("truth:a-b", "a", "b")],
    )

    assert open_derivation.natural_form_for("a").members == ("a",)
    assert closed_derivation.natural_form_for("a").members == ("a", "b")
    assert (
        open_derivation.natural_form_for("a").id
        != closed_derivation.natural_form_for("a").id
    )


def test_true_alone_is_not_meets_and_equation_can_witness_explicitness() -> None:
    no_explicitness = derive_closure(
        ["a", "b"],
        [
            {
                "id": "truth-only",
                "source": "a",
                "target": "b",
                "verdict": True,
                "compatible": True,
            }
        ],
    )
    assert no_explicitness.relation("a", "b") is None

    declared_explicit_without_equation = derive_closure(
        ["a", "b"],
        [
            {
                "id": "declared-explicit-without-equation",
                "source": "a",
                "target": "b",
                "verdict": True,
                "compatible": True,
                "closure_explicit": True,
            }
        ],
    )
    assert declared_explicit_without_equation.relation("a", "b") is None
    rejected = declared_explicit_without_equation.relative_truths[0]
    assert rejected.closure_explicit.witnessed is False
    assert rejected.closure_explicit.basis == (
        "REJECTED_WITHOUT_MATCHING_DETERMINISTIC_VISUAL_EQUATION"
    )

    equation_explicitness = derive_closure(
        ["a", "b"],
        [
            {
                "id": "equation-derived-explicitness",
                "source": "a",
                "target": "b",
                "verdict": True,
                "compatible": True,
                "visual_equation": _equation("eq:a-b", "a", "b"),
            }
        ],
    )
    assert equation_explicitness.relation("a", "b") is not None
    truth = equation_explicitness.relative_truths[0]
    assert truth.closure_explicit.witnessed is True
    assert truth.closure_explicit.basis == "DETERMINISTIC_VISUAL_EQUATION"

    mismatched_equation = derive_closure(
        ["a", "b"],
        [
            {
                "id": "mismatch",
                "source": "a",
                "target": "b",
                "verdict": True,
                "compatible": True,
                "closure_explicit": True,
                "visual_equation": _equation("eq:mismatch", "b", "a"),
            }
        ],
    )
    assert mismatched_equation.relation("a", "b") is None

    nondeterministic = _equation(
        "eq:nondeterministic",
        "a",
        "b",
        deterministic=False,
    )
    nondeterministic_equation = derive_closure(
        ["a", "b"],
        [
            {
                "id": "nondeterministic",
                "source": "a",
                "target": "b",
                "verdict": True,
                "compatible": True,
                "closure_explicit": True,
                "visual_equation": nondeterministic,
            }
        ],
    )
    assert nondeterministic_equation.relation("a", "b") is None


def test_condition_and_determinism_witnesses_require_real_booleans() -> None:
    with pytest.raises(TypeError, match="condition witness must be a boolean"):
        ConditionWitness(witnessed="false")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="condition witness must be a boolean"):
        derive_closure(
            ["a", "b"],
            [
                {
                    **_admitted_truth("truth:string-condition", "a", "b"),
                    "compatible": {"witnessed": "false"},
                }
            ],
        )

    equation = _equation("eq:string-determinism", "a", "b")
    equation["deterministic"] = "false"
    with pytest.raises(
        TypeError, match="visual equation deterministic must be a boolean"
    ):
        derive_closure(
            ["a", "b"],
            [
                {
                    **_admitted_truth("truth:string-determinism", "a", "b"),
                    "visual_equation": equation,
                }
            ],
        )


def test_equivalence_closure_and_natural_form_retain_full_provenance() -> None:
    derivation = derive_closure(
        [
            {"id": "a", "existence_provenance": ["existence:a"]},
            {"id": "b", "existence_provenance": ["existence:b"]},
            {"id": "c", "existence_provenance": ["existence:c"]},
        ],
        [
            _admitted_truth("truth:a-b", "a", "b"),
            _admitted_truth("truth:b-c", "b", "c"),
        ],
    )

    transitive = derivation.relation("a", "c")
    assert transitive is not None
    assert transitive.path == ("a", "b", "c")
    assert "TRANSITIVITY" in transitive.closure_operations
    assert transitive.truth_ids == ("truth:a-b", "truth:b-c")
    assert len(derivation.axiometry.axioms) == len(derivation.witnesses)
    forward = derivation.relation("a", "b")
    reverse = derivation.relation("b", "a")
    assert forward is not None and "SYMMETRY" not in forward.closure_operations
    assert reverse is not None and "SYMMETRY" in reverse.closure_operations

    natural_form = derivation.natural_form_for("a")
    assert natural_form.members == ("a", "b", "c")
    assert natural_form.admitted is True
    assert natural_form.derived_within_closure is True
    assert natural_form.admission_basis == "TRANSLATIONAL_TRUTH_CLOSURE"
    assert "source-return:truth:a-b" in natural_form.source_return_provenance
    assert "eq:truth:a-b" in natural_form.visual_equation_provenance
    assert (
        "compatibility-receipt:truth:a-b"
        in natural_form.compatibility_provenance
    )
    assert (
        "closure-explicit-receipt:truth:b-c"
        in natural_form.closure_explicit_provenance
    )
    assert natural_form.truth_provenance
    assert natural_form.axiom_provenance
    assert natural_form.witness_provenance
    assert natural_form.factorization_provenance
    assert set(natural_form.existence_provenance) == {
        "existence:a",
        "existence:b",
        "existence:c",
    }


def test_interface_is_total_closed_reading_of_the_quotient() -> None:
    derivation = derive_closure(
        ["thought", "garden-project", "unrelated"],
        [_admitted_truth("truth:garden", "thought", "garden-project")],
    )
    shared_state = {
        "natural_form": "community garden",
        "geometry": {"operator": "DISCOVER", "color": "green"},
    }
    distinct_state = {
        "natural_form": "unrelated",
        "geometry": {"operator": "OPEN", "color": "violet"},
    }

    interface = derive_interface_natural_form(
        derivation,
        {
            "thought": shared_state,
            "garden-project": shared_state,
            "unrelated": distinct_state,
        },
    )

    assert interface.closure_internal is True
    assert interface.admission_basis == "TRANSLATIONAL_TRUTH_CLOSURE"
    assert len(interface.natural_form_ids) == 2
    assert len(interface.quotient_render_state) == 2
    assert interface.closure_projection["thought"] == shared_state
    assert interface.closure_projection["garden-project"] == shared_state
    assert interface.closure_projection["unrelated"] == distinct_state
    assert interface.factorization_provenance
    assert interface.existence_provenance
    assert interface.source_return_provenance
    assert interface.visual_equation_provenance
    assert interface.compatibility_provenance
    assert interface.closure_explicit_provenance
    assert interface.renderer_contract == EXTERNAL_RENDERER_CONTRACT
    assert interface.renderer_contract.role is RendererRole.TRANSPORT_ONLY
    assert interface.renderer_contract.can_witness_truth is False
    assert interface.renderer_contract.can_generate_axioms is False
    assert interface.renderer_contract.can_admit_forms is False
    assert interface.renderer_contract.can_change_closure is False

    serialized = interface.to_dict()
    assert serialized["renderer_contract"]["role"] == "TRANSPORT_ONLY"
    json.dumps(serialized)
    json.dumps(derivation.to_dict())


def test_interface_receipt_is_deeply_immutable_after_factorization() -> None:
    derivation = derive_closure(
        ["a", "b"],
        [_admitted_truth("truth:a-b", "a", "b")],
    )
    shared = {"geometry": {"color": "green", "paths": ["a", "b"]}}
    supplied = {"a": shared, "b": shared}
    interface = derive_interface_natural_form(derivation, supplied)

    shared["geometry"]["color"] = "mutated outside"
    shared["geometry"]["paths"].append("outside")
    assert interface.closure_projection["a"]["geometry"]["color"] == "green"
    assert interface.closure_projection["a"]["geometry"]["paths"] == (
        "a",
        "b",
    )
    with pytest.raises(TypeError):
        interface.closure_projection["a"]["geometry"]["color"] = "mutate receipt"


def test_empty_visual_existence_has_empty_total_interface_reading() -> None:
    derivation = derive_closure([], [])
    interface = derive_interface_natural_form(derivation, {})

    assert interface.members == ()
    assert interface.natural_form_ids == ()
    assert dict(interface.quotient_render_state) == {}
    assert dict(interface.closure_projection) == {}


def test_interface_cannot_hide_non_factorization_or_incomplete_existence() -> None:
    derivation = derive_closure(
        ["a", "b", "c"],
        [_admitted_truth("truth:a-b", "a", "b")],
    )

    with pytest.raises(ValueError, match="does not factor through closure truth"):
        derive_interface_natural_form(
            derivation,
            {
                "a": {"label": "one"},
                "b": {"label": "different"},
                "c": {"label": "third"},
            },
        )

    with pytest.raises(ValueError, match="missing forms: c"):
        derive_interface_natural_form(
            derivation,
            {"a": {"label": "one"}, "b": {"label": "one"}},
        )

    with pytest.raises(ValueError, match="outside visual existence: unknown"):
        derive_interface_natural_form(
            derivation,
            {
                "a": {"label": "one"},
                "b": {"label": "one"},
                "c": {"label": "third"},
                "unknown": {"label": "outside"},
            },
        )
