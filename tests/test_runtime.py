from __future__ import annotations

import asyncio
from pathlib import Path

from closure_supernet.config import RuntimeConfig
from closure_supernet.models import OccurrenceCreate, RuleState, RuleVersionCreate, Verdict
from closure_supernet.runtime import ClosureSupernetRuntime


def make_runtime(tmp_path: Path, **overrides) -> ClosureSupernetRuntime:
    config = RuntimeConfig(
        database_path=tmp_path / "runtime.db",
        inbox_dir=tmp_path / "inbox",
        autonomy_enabled=False,
        **overrides,
    )
    return ClosureSupernetRuntime(config)


def test_source_is_immutable_and_exact_duplicate_can_close(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            note = "0 ↔ ∞\nr ↔ i\nball ↔ hair"
            first = await runtime.ingest(OccurrenceCreate(exact_text=note, source_id="a"))
            second = await runtime.ingest(OccurrenceCreate(exact_text=note, source_id="b"))
            assert first["id"] != second["id"]
            assert first["exact_text"] == note
            assert first["checksum"] == second["checksum"]
            result = await runtime.cycle()
            assert result.candidates >= 1
            admissions = runtime.store.list_admissions()
            assert any(row["verdict"] == Verdict.TRUE for row in admissions)
            projection = runtime.black_mirror()
            assert any(len(item["member_ids"]) == 2 for item in projection["classes"])
        asyncio.run(scenario())
    finally:
        runtime.close()


def test_operator_similarity_stays_open_and_reopens(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            await runtime.ingest(OccurrenceCreate(exact_text="ball ↔ hair as returned relation", source_id="a"))
            await runtime.ingest(OccurrenceCreate(exact_text="ball <-> hair as reopened trajectory", source_id="b"))
            await runtime.cycle()
            admissions = runtime.store.list_admissions()
            assert any(row["verdict"] == Verdict.OPEN for row in admissions)
            assert runtime.store.list_open_seams()
            projection = runtime.black_mirror()
            assert len(projection["classes"]) == 2
            assert any(edge["verdict"] == Verdict.OPEN for edge in projection["edges"])
        asyncio.run(scenario())
    finally:
        runtime.close()


def test_rule_versions_never_rewrite_history(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        original = runtime.store.list_rules()
        assert len(original) == 1 and original[0]["state"] == RuleState.ACTIVE
        proposal = runtime.store.create_rule_version(
            RuleVersionCreate(
                rule_id="source-preserving-admission",
                parent_version=original[0]["version"],
                exact_rule_text="Add an explicit review path while preserving every constitutional rule.",
                reason_for_change="test proposal",
                state=RuleState.PROPOSED,
            )
        )
        rules = runtime.store.list_rules()
        assert len(rules) == 2
        assert rules[0]["exact_rule_text"] != proposal["exact_rule_text"]
        runtime.store.activate_rule(proposal["id"])
        rules = runtime.store.list_rules()
        assert {row["state"] for row in rules} == {RuleState.RETIRED, RuleState.ACTIVE}
    finally:
        runtime.close()


def test_no_turing_completeness_assumption(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        status = runtime.status()
        assert status.turing_complete_assumed is False
        assert runtime.config.turing_complete_assumed is False
    finally:
        runtime.close()


def test_inbox_autonomy_is_idempotent(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        runtime.config.inbox_dir.mkdir(parents=True, exist_ok=True)
        note = runtime.config.inbox_dir / "note.md"
        note.write_text("loop ↔ sensor ↔ selection ↔ new loop", encoding="utf-8")
        async def scenario():
            first = await runtime.cycle()
            second = await runtime.cycle()
            assert first.ingested == 1
            assert second.ingested == 0
            assert len(runtime.store.list_occurrences()) == 1
        asyncio.run(scenario())
    finally:
        runtime.close()


def test_author_decision_supersedes_open_projection(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            await runtime.ingest(OccurrenceCreate(exact_text="loop ↔ sensor as one return", source_id="a"))
            await runtime.ingest(OccurrenceCreate(exact_text="loop <-> sensor as active continuity", source_id="b"))
            await runtime.cycle()
            interpretation = runtime.store.list_interpretations()[0]
            assert runtime.store.latest_admissions()[0]["verdict"] == Verdict.OPEN
            runtime.store.create_admission(
                interpretation["id"], Verdict.TRUE,
                {"AUTHOR_DECISION": True},
                "Author confirms this configured translation at the present level",
                "author:test:1", "author:test",
            )
            runtime.projection.run()
            projection = runtime.black_mirror()
            assert len(projection["classes"]) == 1
            assert projection["open_seams"] == []
        asyncio.run(scenario())
    finally:
        runtime.close()
