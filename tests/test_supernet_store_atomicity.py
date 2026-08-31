from __future__ import annotations

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from closure_supernet.supernet_store import SupernetIntegrationStore


def event_data(external_key: str) -> dict[str, object]:
    return {
        "external_key": external_key,
        "exact_source_ids": ["source-1"],
        "source_stream": "atomicity-test",
        "authored_by": "tester",
        "form_label": "test resource",
    }


def test_event_and_required_initial_state_rollback_together(
    tmp_path: Path,
) -> None:
    store = SupernetIntegrationStore(tmp_path / "supernet.db")
    try:
        with store._lock:  # noqa: SLF001 - deliberate failure injection
            store._conn.execute(  # noqa: SLF001 - deliberate failure injection
                """CREATE TRIGGER reject_initial_state
                BEFORE INSERT ON supernet_integration_states
                BEGIN
                    SELECT RAISE(ABORT, 'injected initial-state failure');
                END"""
            )
            store._conn.commit()  # noqa: SLF001 - deliberate failure injection

        with pytest.raises(sqlite3.IntegrityError):
            store.create_event(event_data("atomic-rollback"))

        event_count = store._conn.execute(  # noqa: SLF001 - invariant check
            "SELECT COUNT(*) FROM supernet_integration_events"
        ).fetchone()[0]
        state_count = store._conn.execute(  # noqa: SLF001 - invariant check
            "SELECT COUNT(*) FROM supernet_integration_states"
        ).fetchone()[0]
        assert (event_count, state_count) == (0, 0)
    finally:
        store.close()


def test_existing_external_key_without_state_is_repaired(
    tmp_path: Path,
) -> None:
    store = SupernetIntegrationStore(tmp_path / "supernet.db")
    try:
        original, created = store.create_event(event_data("repair-key"))
        assert created is True
        with store._lock, store._conn:  # noqa: SLF001 - legacy-row fixture
            store._conn.execute(  # noqa: SLF001 - legacy-row fixture
                "DELETE FROM supernet_integration_states WHERE event_id=?",
                (original["id"],),
            )

        recovered, created = store.create_event(event_data("repair-key"))

        assert created is False
        assert recovered["id"] == original["id"]
        assert [state["stage"] for state in recovered["state_history"]] == [
            "SOURCE_PRESERVED"
        ]
    finally:
        store.close()


def test_external_key_race_returns_one_valid_event(tmp_path: Path) -> None:
    database = tmp_path / "supernet.db"
    stores = [SupernetIntegrationStore(database) for _ in range(2)]
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(
                    lambda store: store.create_event(event_data("shared-key")),
                    stores,
                )
            )

        assert {result[0]["id"] for result in results} == {
            results[0][0]["id"]
        }
        assert sorted(result[1] for result in results) == [False, True]
        assert all(
            [state["stage"] for state in result[0]["state_history"]]
            == ["SOURCE_PRESERVED"]
            for result in results
        )
    finally:
        for store in stores:
            store.close()


def test_execution_completion_requires_exact_valid_transition(
    tmp_path: Path,
) -> None:
    store = SupernetIntegrationStore(tmp_path / "supernet.db")
    try:
        store.claim_closure_ui_execution(
            fingerprint="completed",
            contract_id="contract",
            action_id="return",
            perspective_id="perspective",
            focus_event_id=None,
            request_values={"value": 1},
        )
        response = {"ok": True, "nested": {"value": 1}}
        completed = store.complete_closure_ui_execution("completed", response)
        assert completed["status"] == "COMPLETED"
        assert completed["response"] == response

        replay = store.complete_closure_ui_execution("completed", response)
        assert replay == completed
        with pytest.raises(ValueError, match="different response"):
            store.complete_closure_ui_execution("completed", {"ok": False})

        store.claim_closure_ui_execution(
            fingerprint="failed",
            contract_id="failed-contract",
            action_id="failed-return",
            perspective_id="perspective",
            focus_event_id=None,
            request_values={"value": 2},
        )
        store.fail_closure_ui_execution("failed", "injected failure")
        with pytest.raises(RuntimeError, match="is failed"):
            store.complete_closure_ui_execution("failed", response)
        assert store.get_closure_ui_execution("failed")["status"] == "FAILED"

        with pytest.raises(KeyError, match="missing"):
            store.complete_closure_ui_execution("missing", response)
    finally:
        store.close()


def test_execution_claim_is_cross_connection_idempotent_and_one_shot(
    tmp_path: Path,
) -> None:
    database = tmp_path / "supernet.db"
    stores = [SupernetIntegrationStore(database) for _ in range(2)]

    def claim(store: SupernetIntegrationStore, fingerprint: str):
        return store.claim_closure_ui_execution(
            fingerprint=fingerprint,
            contract_id="contract-once",
            action_id="return-once",
            perspective_id="perspective",
            focus_event_id=None,
            request_values={"fingerprint": fingerprint},
        )

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            same = list(
                executor.map(
                    lambda store: claim(store, "same-fingerprint"),
                    stores,
                )
            )
        assert {item[0]["fingerprint"] for item in same} == {
            "same-fingerprint"
        }
        assert sorted(item[1] for item in same) == [False, True]

        consumed, newly_claimed = claim(stores[1], "different-fingerprint")
        assert newly_claimed is False
        assert consumed["fingerprint"] == "same-fingerprint"
        rows = stores[0]._conn.execute(  # noqa: SLF001 - invariant check
            "SELECT fingerprint FROM supernet_closure_ui_executions"
        ).fetchall()
        assert [str(row["fingerprint"]) for row in rows] == [
            "same-fingerprint"
        ]
    finally:
        for store in stores:
            store.close()


def test_visual_receipt_race_is_idempotent_and_parents_must_exist(
    tmp_path: Path,
) -> None:
    database = tmp_path / "supernet.db"
    stores = [SupernetIntegrationStore(database) for _ in range(2)]
    try:
        event, _ = stores[0].create_event(event_data("receipt-source"))

        def append(store: SupernetIntegrationStore):
            return store.append_visual_closure_receipt(
                source_event_id=event["id"],
                input_signature="receipt-signature",
                parent_receipt_ids=[],
                receipt={"protocol": "test", "source_event_id": event["id"]},
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(append, stores))
        assert {item[0]["id"] for item in results} == {results[0][0]["id"]}
        assert sorted(item[1] for item in results) == [False, True]

        with pytest.raises(ValueError, match="different content"):
            stores[0].append_visual_closure_receipt(
                source_event_id=event["id"],
                input_signature="receipt-signature",
                parent_receipt_ids=[],
                receipt={"protocol": "changed", "source_event_id": event["id"]},
            )

        with pytest.raises(ValueError, match="does not exist"):
            stores[0].append_visual_closure_receipt(
                source_event_id=event["id"],
                input_signature="missing-parent",
                parent_receipt_ids=["receipt:missing"],
                receipt={"protocol": "test", "source_event_id": event["id"]},
            )
    finally:
        for store in stores:
            store.close()
