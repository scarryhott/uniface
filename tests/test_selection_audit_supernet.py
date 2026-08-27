from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_selection import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.selection_models import SelectionReadingCreate
from closure_supernet.supernet_models import ResourceEnvelope


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "selection.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


def test_complete_reading_is_naturally_selected(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            reading = await runtime.selection.create_reading(
                SelectionReadingCreate(
                    name="complete point reading",
                    authored_by="participant",
                    field_symbols=["point", "line"],
                    admissible_symbols=["point"],
                )
            )
            evaluation = reading["evaluation"]
            assert evaluation["state"] == "NATURAL_SELECTION"
            assert evaluation["complete"] is True
            assert evaluation["natural_selection"] is True
            assert evaluation["forced_isolation"] is False
            assert evaluation["removed_admissible_symbols"] == []
            assert evaluation["selected_symbol_fixed_by_all_reading_symmetries"] is True
            event = runtime.supernet_store.get_event(reading["integration_event_id"])
            determined = next(
                state for state in event["state_history"] if state["stage"] == "DETERMINED"
            )
            assert determined["verdict"] == "OPEN"
            assert determined["rigidity_receipt"]["prior_reading_complete"] is True
            assert determined["rigidity_receipt"]["strict_strengthening"] is False
            assert determined["metadata"]["truth_issued"] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_branching_selection_is_forced_isolation(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            reading = await runtime.selection.create_reading(
                SelectionReadingCreate(
                    name="authored hardware presentation",
                    authored_by="operator",
                    field_symbols=["phase-a", "phase-b", "phase-c"],
                    admissible_symbols=["phase-a", "phase-b"],
                    selected_symbol="phase-a",
                    selection_scope="bounded-device-presentation",
                )
            )
            evaluation = reading["evaluation"]
            assert evaluation["state"] == "FORCED_ISOLATION"
            assert evaluation["complete"] is False
            assert evaluation["branching"] is True
            assert evaluation["natural_selection"] is False
            assert evaluation["forced_isolation"] is True
            assert evaluation["strict_strengthening"] is True
            assert evaluation["removed_admissible_symbols"] == ["phase-b"]
            assert evaluation["symmetry_witness"]["swaps"] == ["phase-a", "phase-b"]
            assert evaluation["symmetry_witness"]["preserves_original_admissibility"] is True
            event = runtime.supernet_store.get_event(reading["integration_event_id"])
            determined = next(
                state for state in event["state_history"] if state["stage"] == "DETERMINED"
            )
            assert determined["verdict"] == "OPEN"
            assert determined["rigidity_receipt"]["prior_reading_complete"] is False
            assert determined["rigidity_receipt"]["post_selection_reading_complete"] is True
            assert determined["rigidity_receipt"]["determination_origin"] == "FORCED_ISOLATION"
            assert determined["determined_form"]["canonical_presentation"] is None

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_branching_without_choice_and_empty_reading_remain_open(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            branching = await runtime.selection.create_reading(
                SelectionReadingCreate(
                    name="open branch",
                    field_symbols=["a", "b"],
                    admissible_symbols=["a", "b"],
                )
            )
            empty = await runtime.selection.create_reading(
                SelectionReadingCreate(
                    name="empty field contact",
                    field_symbols=["a", "b"],
                    admissible_symbols=[],
                )
            )
            assert branching["evaluation"]["state"] == "OPEN_BRANCHING"
            assert branching["evaluation"]["no_natural_selector_away_from_completeness"] is True
            assert empty["evaluation"]["state"] == "EMPTY_TOTAL_ISOLATION"
            assert empty["evaluation"]["total_isolation_from_field"] is True
            for reading in (branching, empty):
                event = runtime.supernet_store.get_event(reading["integration_event_id"])
                assert event["current_verdict"] == "OPEN"
                assert not any(
                    state["stage"] == "DETERMINED"
                    for state in event["state_history"]
                )

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_event_linked_selection_api_and_selector_lens(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/selector-audit")
        assert page.status_code == 404

        source = client.post(
            "/supernet/integrate",
            json={
                "exact_text": "Two orbit forms remain admitted.",
                "authored_by": "participant",
                "form_label": "orbit reading",
                "adapter_label": "selector",
            },
        )
        assert source.status_code == 200
        event_id = source.json()["event_id"]

        selected = client.post(
            f"/supernet/events/{event_id}/select",
            json={
                "name": "deadline isolation",
                "authored_by": "participant",
                "field_symbols": ["orbit-0", "orbit-1"],
                "admissible_symbols": ["orbit-0", "orbit-1"],
                "selected_symbol": "orbit-0",
                "selection_scope": "temporary-action",
            },
        )
        assert selected.status_code == 200
        payload = selected.json()
        assert payload["source_event_id"] == event_id
        assert payload["evaluation"]["state"] == "FORCED_ISOLATION"
        assert event_id in payload["source_ids"] or payload["source_ids"]

        field = client.get("/network/selections/field")
        assert field.status_code == 200
        assert field.json()["stats"]["forced_isolations"] == 1
        assert field.json()["determination_issues_truth"] is False

        lens = client.get("/supernet/project", params={"lens": "selector"})
        assert lens.status_code == 200
        assert lens.json()["lens"] == "selector"
        assert lens.json()["stats"]["visible_events"] >= 2

        capabilities = client.get("/supernet/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["complete_iff_natural_selection"] is True
        assert capabilities.json()["incomplete_choice_is_forced_isolation"] is True
        assert capabilities.json()["forced_isolation_retains_removed_alternatives"] is True
