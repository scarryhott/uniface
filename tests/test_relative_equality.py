from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from closure_supernet.api_equality import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.equality_models import (
    CoherenceSide,
    EqualityChartCreate,
    EqualityContextCreate,
    EqualityContextReopenCreate,
    EqualityDecisionCreate,
    RelativeEqualityCreate,
    ReturnCoherenceCreate,
)
from closure_supernet.models import OccurrenceCreate, Verdict
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.translation_models import (
    RelativeFormRef,
    TranslationEventCreate,
    TranslationKind,
    TranslationRole,
    TranslationState,
    TranslationStateCreate,
)


def make_runtime(tmp_path: Path) -> ClosureSupernetRuntime:
    return ClosureSupernetRuntime(
        RuntimeConfig(
            database_path=tmp_path / "equality.db",
            inbox_dir=tmp_path / "inbox",
            autonomy_enabled=False,
        )
    )


async def occurrence(runtime: ClosureSupernetRuntime, text: str) -> dict:
    return await runtime.ingest(
        OccurrenceCreate(exact_text=text, source_id=f"test:{text[:16]}")
    )


def form(name: str, occurrence_id: str, language: str) -> RelativeFormRef:
    return RelativeFormRef(
        form_type="test-form",
        form_id=name,
        occurrence_id=occurrence_id,
        role=TranslationRole.SOURCE,
        label=name,
        metadata={"language_label": language},
    )


def translation(
    runtime: ClosureSupernetRuntime,
    source: RelativeFormRef,
    target: RelativeFormRef,
    source_ids: list[str],
    *,
    protocol_verdict: bool | None = None,
    admit: bool = True,
) -> dict:
    created = runtime.translation.create(
        TranslationEventCreate(
            kind=TranslationKind.FRAME_TRANSLATION,
            exact_source_ids=source_ids,
            source_forms=[source.model_copy(update={"role": TranslationRole.SOURCE})],
            target_forms=[target.model_copy(update={"role": TranslationRole.TARGET})],
            relation_type=f"{source.form_id}-to-{target.form_id}",
            preserves=["exact source", "relative form"],
            transforms=["frame presentation"],
            untranslated=[],
            frame_and_scope="test relative frame",
            admission_scope="test context",
            generated_by="test-participant",
            transport={
                "protocol_verdict": protocol_verdict,
                "protocol_verdict_is_not_truth": True,
            },
        )
    )
    if admit:
        created = runtime.translation.transition(
            created["id"],
            TranslationStateCreate(
                state=TranslationState.ADMITTED,
                verdict=Verdict.TRUE,
                reason="Directed translation admitted at the test scope",
                actor_id="test-participant",
            ),
        )
    return created


async def reversible_fixture(runtime: ClosureSupernetRuntime):
    a_occ = await occurrence(runtime, "source form A")
    b_occ = await occurrence(runtime, "source form B")
    a = form("A", a_occ["id"], "language-A")
    b = form("B", b_occ["id"], "language-B")
    sources = [a_occ["id"], b_occ["id"]]
    forward = translation(
        runtime, a, b, sources, protocol_verdict=False, admit=True
    )
    reverse = translation(
        runtime, b, a, sources, protocol_verdict=True, admit=True
    )
    return a_occ, b_occ, a, b, sources, forward, reverse


def build_admitted_witness(
    runtime: ClosureSupernetRuntime,
    context_id: str,
    a: RelativeFormRef,
    b: RelativeFormRef,
    sources: list[str],
    forward: dict,
    reverse: dict,
) -> dict:
    witness = runtime.relative_equality.create_witness(
        RelativeEqualityCreate(
            context_id=context_id,
            left_form=a,
            right_form=b,
            forward_translation_id=forward["id"],
            reverse_translation_id=reverse["id"],
            exact_source_ids=sources,
            invariant=["translation-preserved relation"],
            residue=["literal presentations remain distinct"],
            authored_by="test-participant",
        )
    )
    left = runtime.relative_equality.create_coherence(
        ReturnCoherenceCreate(
            witness_id=witness["id"],
            side=CoherenceSide.LEFT,
            path_translation_ids=[forward["id"], reverse["id"]],
            return_form=a,
            exact_source_ids=sources,
            authored_by="test-participant",
        )
    )
    right = runtime.relative_equality.create_coherence(
        ReturnCoherenceCreate(
            witness_id=witness["id"],
            side=CoherenceSide.RIGHT,
            path_translation_ids=[reverse["id"], forward["id"]],
            return_form=b,
            exact_source_ids=sources,
            authored_by="test-participant",
        )
    )
    for coherence in (left, right):
        runtime.relative_equality.decide_coherence(
            coherence["id"],
            EqualityDecisionCreate(
                verdict=Verdict.TRUE,
                reason="The ordered inverse path returns the selected form at this scope",
                decided_by="test-participant",
            ),
        )
    return runtime.relative_equality.decide_witness(
        witness["id"],
        EqualityDecisionCreate(
            verdict=Verdict.TRUE,
            reason="Both forms are admitted as relative presentations of one completion",
            decided_by="test-participant",
        ),
    )


def test_directed_translation_does_not_become_equality_without_reverse(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario() -> None:
            a_occ = await occurrence(runtime, "only forward A")
            b_occ = await occurrence(runtime, "only forward B")
            a = form("A", a_occ["id"], "A-language")
            b = form("B", b_occ["id"], "B-language")
            sources = [a_occ["id"], b_occ["id"]]
            forward = translation(runtime, a, b, sources)
            context = runtime.relative_equality.create_context(
                EqualityContextCreate(
                    label="one-way context",
                    exact_source_ids=sources,
                    authored_by="test-participant",
                )
            )
            witness = runtime.relative_equality.create_witness(
                RelativeEqualityCreate(
                    context_id=context["id"],
                    left_form=a,
                    right_form=b,
                    forward_translation_id=forward["id"],
                    exact_source_ids=sources,
                    authored_by="test-participant",
                )
            )
            assert witness["current_verdict"] == "OPEN"
            assert witness["reversible"] is False
            with pytest.raises(ValueError):
                runtime.relative_equality.decide_witness(
                    witness["id"],
                    EqualityDecisionCreate(
                        verdict=Verdict.TRUE,
                        reason="This must fail without reverse closure",
                        decided_by="test-participant",
                    ),
                )
            components = runtime.relative_equality.natural_components(context["id"])
            assert len(components) == 2

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_reverse_and_two_return_coherences_generate_one_natural_component(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario() -> None:
            _ao, _bo, a, b, sources, forward, reverse = await reversible_fixture(runtime)
            context = runtime.relative_equality.create_context(
                EqualityContextCreate(
                    label="reversible completion context",
                    exact_source_ids=sources,
                    authored_by="test-participant",
                )
            )
            witness = build_admitted_witness(
                runtime, context["id"], a, b, sources, forward, reverse
            )
            assert witness["current_state"] == "ADMITTED"
            assert witness["current_verdict"] == "TRUE"
            assert witness["reversible"] is True
            assert witness["coherent"] is True
            components = runtime.relative_equality.natural_components(context["id"])
            assert len(components) == 1
            assert len(components[0]["member_forms"]) == 2
            assert components[0]["canonical_form"] is None
            assert components[0]["canonical_language"] is None
            assert set(components[0]["language_labels"]) == {
                "language-A",
                "language-B",
            }
            # Opposed protocol receipts do not decide the truth verdict.
            assert forward["transport"]["protocol_verdict"] is False
            assert reverse["transport"]["protocol_verdict"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_same_forms_can_be_true_in_one_context_and_open_in_another(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario() -> None:
            _ao, _bo, a, b, sources, forward, reverse = await reversible_fixture(runtime)
            first = runtime.relative_equality.create_context(
                EqualityContextCreate(
                    label="first context",
                    exact_source_ids=sources,
                    authored_by="test-participant",
                )
            )
            second = runtime.relative_equality.create_context(
                EqualityContextCreate(
                    label="second context",
                    exact_source_ids=sources,
                    authored_by="test-participant",
                )
            )
            admitted = build_admitted_witness(
                runtime, first["id"], a, b, sources, forward, reverse
            )
            open_witness = runtime.relative_equality.create_witness(
                RelativeEqualityCreate(
                    context_id=second["id"],
                    left_form=a,
                    right_form=b,
                    forward_translation_id=forward["id"],
                    reverse_translation_id=reverse["id"],
                    exact_source_ids=sources,
                    authored_by="test-participant",
                )
            )
            assert admitted["current_verdict"] == "TRUE"
            assert open_witness["current_verdict"] == "OPEN"
            assert len(runtime.relative_equality.natural_components(first["id"])) == 1
            assert len(runtime.relative_equality.natural_components(second["id"])) == 2

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_reopening_preserves_prior_context_and_reopens_prior_true_witness(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario() -> None:
            a_occ, b_occ, a, b, sources, forward, reverse = await reversible_fixture(runtime)
            context = runtime.relative_equality.create_context(
                EqualityContextCreate(
                    label="prior context",
                    exact_source_ids=sources,
                    authored_by="test-participant",
                )
            )
            admitted = build_admitted_witness(
                runtime, context["id"], a, b, sources, forward, reverse
            )
            runtime.translation.transition(
                forward["id"],
                TranslationStateCreate(
                    state=TranslationState.REOPENED,
                    verdict=Verdict.OPEN,
                    reason="A later interaction reopened the forward reading",
                    actor_id="test-participant",
                ),
            )
            reopened_witness = runtime.relative_equality.evaluate_witness(admitted["id"])
            assert reopened_witness["current_state"] == "REOPENED"
            assert reopened_witness["current_verdict"] == "OPEN"
            assert any(
                item["verdict"] == "TRUE"
                for item in reopened_witness["decision_history"]
            )

            c_occ = await occurrence(runtime, "returned successor context source")
            c = form("C", c_occ["id"], "language-C")
            return_translation = translation(
                runtime,
                a,
                c,
                [a_occ["id"], c_occ["id"]],
                admit=False,
            )
            successor = runtime.relative_equality.reopen_context(
                context["id"],
                EqualityContextReopenCreate(
                    label="successor context",
                    exact_source_ids=[a_occ["id"], b_occ["id"], c_occ["id"]],
                    reopening_translation_id=return_translation["id"],
                    authored_by="test-participant",
                ),
            )
            prior = runtime.relative_equality_store.get_context(context["id"])
            assert successor["predecessor_context_id"] == context["id"]
            assert prior["predecessor_context_id"] is None
            assert prior["label"] == "prior context"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_source_axiometry_charts_remain_literal_and_noncanonical(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario() -> None:
            poles = await occurrence(runtime, "0 ↔ ∞ are reciprocal poles")
            ball = await occurrence(runtime, "ball ↔ hair")
            first = runtime.relative_equality.create_chart(
                EqualityChartCreate(
                    name="0 ↔ ∞",
                    exact_source_ids=[poles["id"]],
                    carrier_context="reciprocal-pole chart",
                    generator="polar reversal",
                    inverse_reading="0 and ∞ exchange as reciprocal frame poles",
                    invariant=["one reciprocal relation"],
                    residue=["the full axiometry is not exhausted by the poles"],
                    return_form="unit-fixed reciprocal reading",
                    reopening="translate into r/i and further source operators",
                    authored_by="author",
                )
            )
            second = runtime.relative_equality.create_chart(
                EqualityChartCreate(
                    name="ball ↔ hair",
                    exact_source_ids=[ball["id"]],
                    carrier_context="local return and residual trajectory",
                    generator="ball self-limit",
                    inverse_reading="hair reopening trajectory",
                    invariant=["shared returned relation"],
                    residue=["ordered trajectory remains visible"],
                    return_form="ball-hair natural form",
                    reopening="returned ball becomes later sensor potential",
                    authored_by="author",
                )
            )
            projection = runtime.relative_equality.projection()
            assert {first["name"], second["name"]} == {"0 ↔ ∞", "ball ↔ hair"}
            assert projection["canonical_language_selected"] is False
            assert projection["automatic_global_truth"] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_reverse_translation_reconciliation_only_proposes_open_equality(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario() -> None:
            await reversible_fixture(runtime)
            created = runtime.reconcile_relative_equalities()
            assert created >= 1
            witnesses = runtime.relative_equality_store.list_witnesses()
            assert witnesses
            evaluated = runtime.relative_equality.evaluate_witness(witnesses[0]["id"])
            assert evaluated["current_verdict"] == "OPEN"
            assert evaluated["coherent"] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_relative_equality_api_preserves_all_prior_interfaces(tmp_path: Path) -> None:
    app = create_app(
        RuntimeConfig(
            database_path=tmp_path / "api.db",
            inbox_dir=tmp_path / "inbox",
            autonomy_enabled=False,
        )
    )
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/translation").status_code == 200
        assert client.get("/resources").status_code == 200
        assert client.get("/reopening").status_code == 200
        assert client.get("/equality").status_code == 200
        capabilities = client.get("/network/equality/capabilities")
        assert capabilities.status_code == 200
        body = capabilities.json()
        assert body["witness_valued"] is True
        assert body["context_indexed"] is True
        assert body["directed_translation_precedes_equality"] is True
        field = client.get("/network/equality/field")
        assert field.status_code == 200
        assert field.json()["canonical_language_selected"] is False
