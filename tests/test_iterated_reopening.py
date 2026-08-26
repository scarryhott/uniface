from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_reopening import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.living_models import ParticipantCreate, ProblemCreate
from closure_supernet.models import OccurrenceCreate
from closure_supernet.reopening_models import (
    ClosureRuleSpec,
    MoralConnectionCreate,
    OrderEffect,
    OrderedReadingCreate,
    ReopeningFamilyCreate,
    ReopeningMode,
    ReopeningProcessCreate,
    ReopeningProcessState,
    ReopeningVariantSpec,
)
from closure_supernet.runtime import ClosureSupernetRuntime


def make_runtime(tmp_path: Path) -> ClosureSupernetRuntime:
    return ClosureSupernetRuntime(
        RuntimeConfig(
            database_path=tmp_path / "runtime.db",
            inbox_dir=tmp_path / "inbox",
            autonomy_enabled=False,
        )
    )


async def seed_field(runtime: ClosureSupernetRuntime):
    person = runtime.living.create_participant(ParticipantCreate(display_name="A"))
    other = runtime.living.create_participant(ParticipantCreate(display_name="B"))
    problem = await runtime.living.create_problem(
        ProblemCreate(
            title="Reopen the assumptions",
            exact_text="A real problem whose assumptions remain reopenable.",
            situations=["Several assumptions are held in a dependency order."],
            created_by=person["id"],
        )
    )
    occurrences = {}
    for name in ["a", "b", "c", "core", "extra"]:
        occurrences[name] = await runtime.ingest(
            OccurrenceCreate(
                exact_text=f"assumption or lesson {name}",
                source_id=f"test:{name}",
            )
        )
    return person, other, problem, occurrences


def test_remaining_star_is_intersection_of_explicit_closed_readings(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            person, _other, problem, occ = await seed_field(runtime)
            family = runtime.iterated_reopening.create_family(
                ReopeningFamilyCreate(
                    problem_id=problem["id"],
                    name="two admissible reopenings",
                    created_by=person["id"],
                    assumption_occurrence_ids=[occ["a"]["id"], occ["b"]["id"]],
                    mode=ReopeningMode.CUSTOM,
                    custom_variants=[
                        ReopeningVariantSpec(
                            label="read through a",
                            held_occurrence_ids=[occ["a"]["id"]],
                        ),
                        ReopeningVariantSpec(
                            label="read through b",
                            held_occurrence_ids=[occ["b"]["id"]],
                        ),
                    ],
                    closure_rules=[
                        ClosureRuleSpec(
                            premise_occurrence_ids=[occ["a"]["id"]],
                            conclusion_occurrence_id=occ["core"]["id"],
                        ),
                        ClosureRuleSpec(
                            premise_occurrence_ids=[occ["b"]["id"]],
                            conclusion_occurrence_id=occ["core"]["id"],
                        ),
                    ],
                )
            )
            assert family["remaining_star_ids"] == [occ["core"]["id"]]
            assert family["closure_verified"] is True
            assert len(family["variants"]) == 2
            projection = runtime.iterated_reopening.projection()
            assert projection["stats"]["final_core_state_available"] is False
            assert projection["source_reverse_index"][f"family:{family['id']}"]

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_dependency_reorder_separates_content_preservation_from_meaning_change(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            person, other, problem, occ = await seed_field(runtime)
            await runtime.iterated_reopening.create_ordered_reading(
                OrderedReadingCreate(
                    problem_id=problem["id"],
                    participant_id=person["id"],
                    exact_text="Read a, then b, as one cultural meaning.",
                    held_occurrence_ids=[occ["a"]["id"], occ["b"]["id"]],
                    dependency_edges=[(occ["a"]["id"], occ["b"]["id"])],
                    meaning_key="shared-meaning",
                )
            )
            await runtime.iterated_reopening.create_ordered_reading(
                OrderedReadingCreate(
                    problem_id=problem["id"],
                    participant_id=other["id"],
                    exact_text="Read b, then a, while preserving the cultural meaning.",
                    held_occurrence_ids=[occ["b"]["id"], occ["a"]["id"]],
                    dependency_edges=[(occ["b"]["id"], occ["a"]["id"])],
                    meaning_key="shared-meaning",
                )
            )
            await runtime.iterated_reopening.create_ordered_reading(
                OrderedReadingCreate(
                    problem_id=problem["id"],
                    participant_id=other["id"],
                    exact_text="Read b, then a, and the cultural meaning changes.",
                    held_occurrence_ids=[occ["b"]["id"], occ["a"]["id"]],
                    dependency_edges=[(occ["b"]["id"], occ["a"]["id"])],
                    meaning_key="changed-meaning",
                )
            )
            effects = {
                row["effect"]
                for row in runtime.iterated_reopening_store.list_order_assessments()
            }
            assert str(OrderEffect.CONTENT_PRESERVING) in effects
            assert str(OrderEffect.MEANING_CHANGING) in effects
            assert any(
                "meaning-changing dependency order" in seam["reason"]
                for seam in runtime.store.list_open_seams()
            )

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_iteration_strictly_reopens_then_stabilizes_only_at_finite_scope(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            person, _other, problem, occ = await seed_field(runtime)
            process = runtime.iterated_reopening.create_process(
                ReopeningProcessCreate(
                    problem_id=problem["id"],
                    name="joint suspension process",
                    created_by=person["id"],
                    initial_assumption_ids=[
                        occ["a"]["id"],
                        occ["b"]["id"],
                        occ["c"]["id"],
                    ],
                    mode=ReopeningMode.JOINT_SUSPENSION,
                    joint_suspensions=[[occ["a"]["id"]]],
                    max_rounds=8,
                )
            )
            first = runtime.iterated_reopening.advance_process(process["id"])
            assert first is not None and first["strictly_reopened"] is True
            assert set(first["remaining_star_ids"]) == {
                occ["b"]["id"],
                occ["c"]["id"],
            }
            second = runtime.iterated_reopening.advance_process(process["id"])
            assert second is not None and second["strictly_reopened"] is False
            current = runtime.iterated_reopening_store.get_process(process["id"])
            assert current["state"] == str(
                ReopeningProcessState.STABLE_AT_CURRENT_FINITE_SCOPE
            )
            assert "FINAL" not in current["state"]

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_moral_connection_agrees_on_residue_and_preserves_plurality(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            person, other, problem, occ = await seed_field(runtime)
            process = runtime.iterated_reopening.create_process(
                ReopeningProcessCreate(
                    problem_id=problem["id"],
                    name="residue connection",
                    created_by=person["id"],
                    initial_assumption_ids=[occ["a"]["id"], occ["b"]["id"]],
                    mode=ReopeningMode.JOINT_SUSPENSION,
                    joint_suspensions=[[occ["a"]["id"]]],
                )
            )
            residue_round = runtime.iterated_reopening.advance_process(process["id"])
            assert residue_round is not None
            connection = runtime.iterated_reopening.create_moral_connection(
                MoralConnectionCreate(
                    round_id=residue_round["id"],
                    participant_a_id=person["id"],
                    participant_b_id=other["id"],
                    understanding_a_ids=[occ["b"]["id"], occ["a"]["id"]],
                    understanding_b_ids=[occ["b"]["id"], occ["extra"]["id"]],
                )
            )
            assert connection["agrees_on_residue"] is True
            assert connection["plurality_a_ids"] == [occ["a"]["id"]]
            assert connection["plurality_b_ids"] == [occ["extra"]["id"]]
            assert connection["understanding_a_ids"] != connection["understanding_b_ids"]

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_autonomous_cycle_advances_active_reopening_process(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            person, _other, problem, occ = await seed_field(runtime)
            runtime.iterated_reopening.create_process(
                ReopeningProcessCreate(
                    problem_id=problem["id"],
                    name="autonomous reopening",
                    created_by=person["id"],
                    initial_assumption_ids=[occ["a"]["id"], occ["b"]["id"]],
                    mode=ReopeningMode.SINGLE_REMOVAL,
                )
            )
            result = await runtime.cycle()
            assert result.reopening_rounds == 1
            assert result.reopening_families >= 1
            assert runtime.iterated_reopening_store.list_rounds()
            field = runtime.living_field()
            assert field["iterated_reopening"]["stats"]["nonterminal"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_reopening_api_is_public_and_source_reversible(tmp_path: Path) -> None:
    config = RuntimeConfig(
        database_path=tmp_path / "api.db",
        inbox_dir=tmp_path / "inbox",
        autonomy_enabled=False,
    )
    app = create_app(config)
    with TestClient(app) as client:
        capabilities = client.get("/network/reopening/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["final_core_state_available"] is False
        assert client.get("/reopening").status_code == 200
        field = client.get("/network/reopening/field")
        assert field.status_code == 200
        assert field.json()["stats"]["finite_scope_stability_only"] is True
