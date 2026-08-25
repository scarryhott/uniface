from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from closure_supernet.api import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.living_models import (
    ActionReturnCreate,
    CollectiveActionCreate,
    NoteCreate,
    ParticipantCreate,
    PerspectiveCreate,
    ProblemCreate,
    ReintegrationDecisionCreate,
    ReintegrationStatus,
)
from closure_supernet.models import Verdict
from closure_supernet.runtime import ClosureSupernetRuntime


def make_runtime(tmp_path: Path) -> ClosureSupernetRuntime:
    return ClosureSupernetRuntime(
        RuntimeConfig(
            database_path=tmp_path / "living.db",
            inbox_dir=tmp_path / "inbox",
            autonomy_enabled=False,
            public_interface_enabled=True,
            agentic_reintegration_enabled=True,
        )
    )


def create_problem_graph(runtime: ClosureSupernetRuntime):
    author = runtime.living.create_participant(ParticipantCreate(display_name="Author"))
    perspective = runtime.living.create_perspective(
        PerspectiveCreate(
            participant_id=author["id"],
            label="Author's current perspective",
            description="A relative presentation rather than a total identity",
        )
    )

    async def scenario():
        problem = await runtime.living.create_problem(
            ProblemCreate(
                title="How can the field coordinate a return?",
                exact_text="A real problem presents a shared situation with discretion remaining.",
                situations=["A source has been authored", "Several responses remain possible"],
                created_by=author["id"],
                perspective_id=perspective["id"],
                affected_perspectives=[perspective["id"]],
            )
        )
        return author, perspective, problem

    return asyncio.run(scenario())


def test_empty_problem_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ProblemCreate(
            title="Nothing",
            exact_text="Nothing",
            situations=[],
            created_by="participant",
        )


def test_note_is_loop_step_and_solution_is_interaction(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        author, perspective, problem = create_problem_graph(runtime)

        async def scenario():
            note = await runtime.living.add_note(
                problem["id"],
                NoteCreate(
                    author_id=author["id"],
                    perspective_id=perspective["id"],
                    exact_text="A note changes the interface without forcing or leaving it untouched.",
                    affected_perspectives=[perspective["id"]],
                ),
            )
            interaction = note["interaction"]
            receipt = runtime.living_store.get_solution_receipt_by_interaction(
                interaction["id"]
            )
            assert interaction["kind"] == "NOTE"
            assert interaction["from_problem_id"] == interaction["to_problem_id"]
            assert receipt["interaction_id"] == interaction["id"]
            assert receipt["verdict"] == Verdict.OPEN
            assert runtime.store.get_occurrence(interaction["occurrence_id"])[
                "exact_text"
            ].startswith("A note changes")
            assert runtime.living_store.get_problem(problem["id"])[
                "current_state"
            ] == "ACTIVE"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_returned_consequence_reopens_problem_and_creates_open_reintegration(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        author, perspective, problem = create_problem_graph(runtime)

        async def scenario():
            action = await runtime.living.create_action(
                CollectiveActionCreate(
                    problem_id=problem["id"],
                    title="Run a shared experiment",
                    exact_intent="Participants act together and return what happened.",
                    created_by=author["id"],
                    participant_ids=[author["id"]],
                    affected_perspectives=[perspective["id"]],
                    open_assumptions=["The return may contradict the intent"],
                )
            )
            returned = await runtime.living.add_action_return(
                action["id"],
                ActionReturnCreate(
                    exact_text="The action changed the situation, but the affected perspective was omitted from the report.",
                    authored_by=author["id"],
                    affected_perspectives=[],
                ),
            )
            assert runtime.living.reintegrate() == 1
            assert runtime.living.reintegrate() == 0
            proposal = runtime.living_store.list_reintegration_proposals()[0]
            assert proposal["return_id"] == returned["id"]
            assert proposal["current_status"] == "OPEN"
            assert runtime.living_store.get_problem(problem["id"])[
                "current_state"
            ] == "REOPENED"
            assert runtime.living_store.get_action(action["id"])[
                "current_state"
            ] == "REOPENED"
            assert runtime.store.list_open_seams()
            field = runtime.living.field_projection(runtime.black_mirror())
            assert field["stats"]["quantity_quality_rankings"] == 0
            assert field["stats"]["nonterminal"] is True
            assert field["source_reverse_index"][f"return:{returned['id']}"] == [
                returned["occurrence_id"]
            ]

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_author_decision_is_applied_without_erasing_prior_open_admission(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        author, perspective, problem = create_problem_graph(runtime)

        async def scenario():
            action = await runtime.living.create_action(
                CollectiveActionCreate(
                    problem_id=problem["id"],
                    title="Return a consequence",
                    exact_intent="Act and reopen the problem through the result.",
                    created_by=author["id"],
                    participant_ids=[author["id"]],
                    affected_perspectives=[perspective["id"]],
                )
            )
            await runtime.living.add_action_return(
                action["id"],
                ActionReturnCreate(
                    exact_text="The returned consequence is ready for relative admission.",
                    authored_by=author["id"],
                    affected_perspectives=[perspective["id"]],
                ),
            )
            first = await runtime.cycle()
            assert first.living_reintegrations == 1
            proposal = runtime.living_store.list_reintegration_proposals()[0]
            admissions_before = runtime.store.list_admissions()
            assert any(row["verdict"] == Verdict.OPEN for row in admissions_before)
            runtime.living.decide_reintegration(
                proposal["id"],
                ReintegrationDecisionCreate(
                    status=ReintegrationStatus.AUTHOR_CONFIRMED,
                    reason="The author confirms this relative reintegration at this level.",
                    author_id=author["id"],
                ),
            )
            second = await runtime.cycle()
            assert second.living_decisions_applied >= 1
            admissions_after = runtime.store.list_admissions()
            assert any(row["verdict"] == Verdict.TRUE for row in admissions_after)
            assert any(row["verdict"] == Verdict.OPEN for row in admissions_after)
            assert runtime.living_store.get_reintegration_proposal(proposal["id"])[
                "current_status"
            ] == "AUTHOR_CONFIRMED"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_public_living_network_api(tmp_path: Path) -> None:
    config = RuntimeConfig(
        database_path=tmp_path / "api.db",
        inbox_dir=tmp_path / "inbox",
        autonomy_enabled=False,
        public_interface_enabled=True,
        agentic_reintegration_enabled=True,
    )
    with TestClient(create_app(config)) as client:
        root = client.get("/")
        assert root.status_code == 200
        assert "Closure Supernet Living Field" in root.text
        assert "quantity" in root.text
        assert "Closure Supernet Runtime" in client.get("/runtime").text

        author = client.post(
            "/network/participants", json={"display_name": "Public participant"}
        ).json()
        problem = client.post(
            "/network/problems",
            json={
                "title": "Public problem",
                "exact_text": "A public situation is presented for interaction.",
                "situations": ["The situation exists"],
                "created_by": author["id"],
            },
        )
        assert problem.status_code == 200
        problem_data = problem.json()
        note = client.post(
            f"/network/problems/{problem_data['id']}/notes",
            json={
                "author_id": author["id"],
                "exact_text": "This public note is one loop step.",
            },
        )
        assert note.status_code == 200
        action = client.post(
            "/network/actions",
            json={
                "problem_id": problem_data["id"],
                "title": "Public action",
                "exact_intent": "Coordinate an action and return its consequence.",
                "created_by": author["id"],
                "participant_ids": [author["id"]],
            },
        ).json()
        returned = client.post(
            f"/network/actions/{action['id']}/returns",
            json={
                "exact_text": "The consequence returns to the public field.",
                "authored_by": author["id"],
            },
        )
        assert returned.status_code == 200
        reintegration = client.post("/network/reintegrate")
        assert reintegration.status_code == 200
        field = client.get("/network/field").json()
        assert field["stats"]["participants"] == 1
        assert field["stats"]["problems"] == 1
        assert field["stats"]["interactions"] == 1
        assert field["stats"]["actions"] == 1
        assert field["stats"]["returns"] == 1
        assert field["stats"]["open_reintegration"] == 1
