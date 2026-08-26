from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_translation import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.living_models import (
    ActionReturnCreate,
    CollectiveActionCreate,
    NoteCreate,
    ParticipantCreate,
    ProblemCreate,
)
from closure_supernet.models import OccurrenceCreate, Verdict
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.translation_models import (
    RelativeFormRef,
    TranslationCompositionCreate,
    TranslationEventCreate,
    TranslationKind,
    TranslationRole,
    TranslationState,
    TranslationStateCreate,
)


def make_runtime(tmp_path: Path) -> ClosureSupernetRuntime:
    return ClosureSupernetRuntime(
        RuntimeConfig(
            database_path=tmp_path / "runtime.db",
            inbox_dir=tmp_path / "inbox",
            autonomy_enabled=False,
        )
    )


def test_translation_history_is_source_reversible_and_nonterminal(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            source = await runtime.ingest(
                OccurrenceCreate(exact_text="source presentation", source_id="source")
            )
            target = await runtime.ingest(
                OccurrenceCreate(exact_text="target presentation", source_id="target")
            )
            translation = runtime.translation.create(
                TranslationEventCreate(
                    kind=TranslationKind.LANGUAGE_TRANSLATION,
                    exact_source_ids=[source["id"], target["id"]],
                    source_forms=[
                        RelativeFormRef(
                            form_type="occurrence",
                            form_id=source["id"],
                            occurrence_id=source["id"],
                            role=TranslationRole.SOURCE,
                        )
                    ],
                    target_forms=[
                        RelativeFormRef(
                            form_type="occurrence",
                            form_id=target["id"],
                            occurrence_id=target["id"],
                            role=TranslationRole.TARGET,
                        )
                    ],
                    relation_type="AUTHOR_INTERPRETED_TRANSLATION",
                    preserves=["literal sources", "meaning under declared frame"],
                    transforms=["presentation language"],
                    untranslated=["future cultural readings"],
                    generated_by="author",
                )
            )
            assert translation["current_state"] == "PROPOSED"
            assert translation["current_verdict"] == "OPEN"

            runtime.translation.transition(
                translation["id"],
                TranslationStateCreate(
                    state=TranslationState.RETURNED,
                    verdict=Verdict.TRUE,
                    reason="A relative form returned under the declared frame",
                    actor_id="author",
                ),
            )
            reopened = runtime.translation.transition(
                translation["id"],
                TranslationStateCreate(
                    state=TranslationState.REOPENED,
                    verdict=Verdict.OPEN,
                    reason="A later interaction reopened the returned form",
                    actor_id="participant-b",
                ),
            )
            assert reopened["current_state"] == "REOPENED"
            assert reopened["current_verdict"] == "OPEN"
            assert [state["state"] for state in reopened["state_history"]] == [
                "PROPOSED",
                "RETURNED",
                "REOPENED",
            ]
            assert runtime.store.get_occurrence(source["id"])["exact_text"] == "source presentation"
            assert runtime.store.get_occurrence(target["id"])["exact_text"] == "target presentation"
            projection = runtime.translation.projection()
            assert translation["id"] in projection["reopened_translations"]
            assert projection["protocol_is_transport_only"] is True
            assert projection["closure_reading"] == "translational truth through interaction"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_candidate_interpretation_and_admission_are_derived_translation_states(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            source = await runtime.ingest(
                OccurrenceCreate(exact_text="0 and infinity are reciprocal poles", source_id="a")
            )
            target = await runtime.ingest(
                OccurrenceCreate(exact_text="the two ends admit a geometric reading", source_id="b")
            )
            candidate, _ = runtime.store.create_candidate_relation(
                source["id"],
                target["id"],
                "FRAME_TRANSLATION",
                0.9,
                "Explicit candidate frame translation",
                "test",
            )
            interpretation, _ = runtime.store.create_interpretation(
                {
                    "candidate_relation_id": candidate["id"],
                    "source_operator_path": source["operator_path"],
                    "target_operator_path": target["operator_path"],
                    "preserved_structure": ["two reciprocal presentations"],
                    "transformed_structure": ["numeric reading becomes geometric reading"],
                    "omitted_or_hidden_structure": ["the wider axiometry"],
                    "frame_and_scope": "configured reciprocal-pole chart",
                    "reverse_path": [target["id"], source["id"]],
                    "affected_perspectives": [],
                    "formal_scope": "interpreted relation only",
                    "empirical_scope": "none",
                    "reopening": "new source may refine the chart",
                    "generated_by": "test",
                },
                "test-engine",
            )
            admission, _ = runtime.store.create_admission(
                interpretation["id"],
                Verdict.TRUE,
                {"SOURCE_REVERSIBLE": True},
                "Author-admitted relative translation",
                "test-rule",
                "author",
            )
            counts = runtime.translation.reconcile()
            assert counts["candidate_relations"] == 1
            translated = runtime.translation_store.get_by_external_key(
                f"candidate_relation:{candidate['id']}"
            )
            assert translated is not None
            assert translated["current_state"] == "ADMITTED"
            assert translated["current_verdict"] == "TRUE"
            history = translated["state_history"]
            assert any(state["interpretation_id"] == interpretation["id"] for state in history)
            assert any(state["admission_id"] == admission["id"] for state in history)
            assert translated["transport"]["protocol_is_transport_only"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_living_note_action_and_return_reconcile_as_translation_forms(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            person = runtime.living.create_participant(
                ParticipantCreate(display_name="Author")
            )
            problem = await runtime.living.create_problem(
                ProblemCreate(
                    title="Translate collective action",
                    exact_text="A real problem enters the shared field.",
                    situations=["The participants must act and observe the return."],
                    created_by=person["id"],
                )
            )
            note = await runtime.living.add_note(
                problem["id"],
                NoteCreate(
                    author_id=person["id"],
                    exact_text="This note changes the problem as one loop step.",
                ),
            )
            action = await runtime.living.create_action(
                CollectiveActionCreate(
                    problem_id=problem["id"],
                    title="Act together",
                    exact_intent="Test one collective response.",
                    created_by=person["id"],
                    participant_ids=[person["id"]],
                )
            )
            returned = await runtime.living.add_action_return(
                action["id"],
                ActionReturnCreate(
                    exact_text="The action returned an unexpected consequence.",
                    authored_by=person["id"],
                ),
            )
            counts = runtime.translation.reconcile()
            assert counts["living_interactions"] >= 1
            assert counts["collective_actions"] == 1
            assert counts["action_returns"] == 1

            note_translation = runtime.translation_store.get_by_external_key(
                f"living_interaction:{note['interaction']['id']}"
            )
            return_translation = runtime.translation_store.get_by_external_key(
                f"action_return:{returned['id']}"
            )
            assert note_translation is not None
            assert note_translation["kind"] == "NOTE_LOOP_STEP"
            assert return_translation is not None
            assert return_translation["current_state"] == "REOPENED"
            assert return_translation["current_verdict"] == "OPEN"
            assert problem["occurrence_id"] in return_translation["exact_source_ids"]
            assert return_translation["successor_potential"][0]["form_type"] == "problem"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_translation_composition_retains_predecessors_and_open_scope(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            occurrences = []
            for text in ["first form", "middle form", "returned form"]:
                occurrences.append(
                    await runtime.ingest(OccurrenceCreate(exact_text=text, source_id="compose"))
                )

            def translation_between(left, right):
                return runtime.translation.create(
                    TranslationEventCreate(
                        exact_source_ids=[left["id"], right["id"]],
                        source_forms=[
                            RelativeFormRef(
                                form_type="occurrence",
                                form_id=left["id"],
                                occurrence_id=left["id"],
                                role=TranslationRole.SOURCE,
                            )
                        ],
                        target_forms=[
                            RelativeFormRef(
                                form_type="occurrence",
                                form_id=right["id"],
                                occurrence_id=right["id"],
                                role=TranslationRole.TARGET,
                            )
                        ],
                    )
                )

            first = translation_between(occurrences[0], occurrences[1])
            second = translation_between(occurrences[1], occurrences[2])
            composed = runtime.translation.compose(
                TranslationCompositionCreate(
                    predecessor_translation_ids=[first["id"], second["id"]],
                    generated_by="author",
                )
            )
            assert composed["kind"] == "COMPOSED"
            assert composed["predecessor_translation_ids"] == [first["id"], second["id"]]
            assert composed["current_state"] == "INTERPRETED"
            assert composed["current_verdict"] == "OPEN"
            assert set(composed["exact_source_ids"]) == {
                item["id"] for item in occurrences
            }

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_translation_api_and_autonomous_cycle(tmp_path: Path) -> None:
    config = RuntimeConfig(
        database_path=tmp_path / "api.db",
        inbox_dir=tmp_path / "inbox",
        autonomy_enabled=False,
    )
    app = create_app(config)
    with TestClient(app) as client:
        source = client.post(
            "/occurrences",
            json={"exact_text": "source via API", "source_id": "api"},
        ).json()
        target = client.post(
            "/occurrences",
            json={"exact_text": "target via API", "source_id": "api"},
        ).json()
        payload = {
            "kind": "LANGUAGE_TRANSLATION",
            "exact_source_ids": [source["id"], target["id"]],
            "source_forms": [
                {
                    "form_type": "occurrence",
                    "form_id": source["id"],
                    "occurrence_id": source["id"],
                    "role": "SOURCE",
                }
            ],
            "target_forms": [
                {
                    "form_type": "occurrence",
                    "form_id": target["id"],
                    "occurrence_id": target["id"],
                    "role": "TARGET",
                }
            ],
            "relation_type": "API_TRANSLATION",
            "generated_by": "api-author",
        }
        response = client.post("/network/translations", json=payload)
        assert response.status_code == 200, response.text
        translation = response.json()
        field = client.get("/network/translations/field")
        assert field.status_code == 200
        assert field.json()["protocol_is_transport_only"] is True
        assert translation["id"] in field.json()["source_reverse_index"]
        cycle = client.post("/runtime/cycle")
        assert cycle.status_code == 200, cycle.text
        assert cycle.json()["translation_events"] >= 1
        status = client.get("/runtime/status").json()
        assert status["translation_field_enabled"] is True
        assert status["protocol_is_transport_only"] is True
        assert client.get("/translation").status_code == 200
