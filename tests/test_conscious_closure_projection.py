from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.closure_ui_contract import RETURN_ENDPOINT_TEMPLATE
from closure_supernet.config import RuntimeConfig
from closure_supernet.minimal_projection_runtime import (
    TranslationalReturnLedger,
    derive_local_projection_commitment,
)
from closure_supernet.supernet_store import SupernetIntegrationStore
from closure_supernet.translational_truth_axiometry import derive_closure


PERSPECTIVE_A = "perspective:harry"
PERSPECTIVE_B = "perspective:other"


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "conscious-closure.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def kernel(reading: Mapping[str, Any]) -> frozenset[frozenset[str]]:
    fibres: dict[str, set[str]] = {}
    for state_id, value in reading.items():
        fibres.setdefault(str(value), set()).add(str(state_id))
    return frozenset(frozenset(members) for members in fibres.values())


def close(
    reading: Mapping[str, Any],
    seed: set[str],
) -> frozenset[str]:
    image = {str(reading[state_id]) for state_id in seed}
    return frozenset(
        str(state_id)
        for state_id, value in reading.items()
        if str(value) in image
    )


def fibre_partition(contract: Mapping[str, Any]) -> frozenset[frozenset[str]]:
    return frozenset(
        frozenset(str(item) for item in fibre["member_state_ids"])
        for fibre in contract["projection"]["equality_fibres"]
    )


def return_request(
    contract: Mapping[str, Any],
    exact_source: str,
    *,
    source_stream: str,
) -> dict[str, Any]:
    payload = {
        "return_relation_id": contract["return_relation"]["id"],
        "perspective_id": contract["perspective_id"],
        "focus_event_id": contract["focus_event_id"],
        "exact_source_return": exact_source,
        "closure_equation_system_id": contract[
            "closure_naturality_equations"
        ]["id"],
        "source_stream": source_stream,
    }
    payload["local_projection_commitment"] = derive_local_projection_commitment(
        contract,
        return_relation_id=payload["return_relation_id"],
        perspective_id=payload["perspective_id"],
        focus_event_id=payload["focus_event_id"],
        exact_source_return=payload["exact_source_return"],
    )
    return payload


def execute_return(
    client: TestClient,
    contract: Mapping[str, Any],
    exact_source: str,
    *,
    source_stream: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    request = return_request(
        contract,
        exact_source,
        source_stream=source_stream,
    )
    response = client.post(
        RETURN_ENDPOINT_TEMPLATE.format(contract_id=contract["id"]),
        json=request,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    return request, payload


def event_rows(database: Path) -> list[dict[str, Any]]:
    with sqlite3.connect(database) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """SELECT seq,id,perspective_id,source_stream,created_at
            FROM supernet_integration_events ORDER BY seq"""
        ).fetchall()
    return [dict(row) for row in rows]


def assert_no_absolute_claims(contract: Mapping[str, Any]) -> None:
    claims = contract["claims"]
    assert claims["truth_issued"] is False
    assert claims["physical_law_claimed"] is False
    assert claims["consciousness_claimed"] is False
    assert claims["external_resource_admitted"] is False

    boundary = contract["closure_process"]["boundary"]
    assert boundary["source_preserved"] is True
    assert boundary["truth_issued"] is False
    assert boundary["physical_law_claimed"] is False
    assert boundary["consciousness_claimed"] is False
    assert boundary["external_resource_admitted"] is False


def assert_closure_process(
    contract: Mapping[str, Any],
    *,
    continuation_index: int,
) -> None:
    process = contract["closure_process"]

    axioms = process["relative_axioms"]
    assert axioms["status"] == "WITNESSED"
    assert axioms["formal_implication_under_conscious_hypothesis"] is True
    assert axioms["runtime_translated_chart_family_verified"] is True
    assert axioms["runtime_claim_body_soundness_verified"] is False
    assert axioms["runtime_closure_registration_verified"] is False
    assert axioms["external_absolute_step_claims_admitted"] is False

    proofs = process["relative_proofs"]
    assert proofs["status"] == "WITNESSED"
    assert proofs["formal_implication_under_conscious_hypothesis"] is True
    assert proofs["runtime_composite_closure_witness_verified"] is False
    assert proofs["runtime_additive_content_verified"] is False
    assert proofs["source_returns_preserved"] is True

    understanding = process["understanding"]
    assert understanding["status"] == "WITNESSED"
    assert (
        understanding["formal_implication_under_conscious_hypothesis"] is True
    )
    assert understanding["runtime_translated_chart_family_verified"] is True

    continuation = process["continuing_existence"]
    assert continuation["status"] == "WITNESSED"
    assert continuation["continuation_index"] == continuation_index
    assert len(continuation["continuation_lineage_ids"]) == continuation_index
    assert continuation["continuation_lineage_ids"] == contract[
        "continuation_lineage_ids"
    ]
    assert continuation["runtime_continuation_is_append_only_lineage"] is True
    assert continuation["formal_n_fold_defect_verified_by_runtime"] is False
    assert continuation["reopens_after_return"] is True
    assert continuation["terminal"] is False

    assert_no_absolute_claims(contract)


def assert_translated_perspective_closure(
    contract: Mapping[str, Any],
    left: str,
    right: str,
) -> None:
    perspective_closure = contract["perspective_closure"]
    assert perspective_closure["status"] == "WITNESSED"
    assert perspective_closure["active_perspective_id"] == contract["perspective_id"]

    readings = perspective_closure["readings"]
    assert {left, right}.issubset(readings)
    left_reading = readings[left]
    right_reading = readings[right]
    assert set(left_reading) == set(right_reading)
    assert left_reading != right_reading
    assert kernel(left_reading) == kernel(right_reading)
    for state_id in left_reading:
        assert close(left_reading, {state_id}) == close(right_reading, {state_id})

    witnesses = [
        item
        for item in perspective_closure["translations"]
        if {
            item["source_perspective_id"],
            item["target_perspective_id"],
        }
        == {left, right}
    ]
    assert witnesses, "the equal kernels need an explicit chart translation"
    witness = witnesses[0]
    assert witness["witnessed"] is True
    assert witness["faithful"] is True
    assert witness["same_kernel"] is True
    assert witness["source_return_ids"]

    source = readings[witness["source_perspective_id"]]
    target = readings[witness["target_perspective_id"]]
    translation = witness["display_translation"]
    assert len(translation) == len(set(source.values()))
    assert len(set(translation.values())) == len(translation)
    for state_id, source_value in source.items():
        assert translation[str(source_value)] == target[state_id]

    active_reading = readings[contract["perspective_id"]]
    assert contract["projection"]["reading"] == active_reading
    assert fibre_partition(contract) == kernel(active_reading)


def test_translated_charts_have_the_same_nontrivial_closure_relation() -> None:
    forms = [
        {
            "id": "a",
            "state": {"source_stream": "human-intent"},
            "source_return_ids": ["return:a"],
        },
        {
            "id": "b",
            "state": {"source_stream": "digital-interaction"},
            "source_return_ids": ["return:b"],
        },
        {
            "id": "c",
            "state": {"source_stream": "sensor-return"},
            "source_return_ids": ["return:c"],
        },
    ]
    readings = {
        PERSPECTIVE_A: {"a": "violet", "b": "violet", "c": "amber"},
        PERSPECTIVE_B: {"a": "unity", "b": "unity", "c": "solitary"},
    }
    translation = {
        "id": "translation:harry-other",
        "source": PERSPECTIVE_A,
        "target": PERSPECTIVE_B,
        "display_translation": {"violet": "unity", "amber": "solitary"},
        "witnessed": True,
        "source_return_ids": ["return:a", "return:b", "return:c"],
    }

    derived = derive_closure(
        forms,
        perspective_readings=readings,
        perspective_translations=[translation],
    )
    assert derived.status == "WITNESSED"
    assert derived.supernet_open is False
    assert kernel(readings[PERSPECTIVE_A]) == kernel(readings[PERSPECTIVE_B])
    assert kernel(readings[PERSPECTIVE_A]) == frozenset(
        {frozenset({"a", "b"}), frozenset({"c"})}
    )
    assert set(map(frozenset, derived.equivalence_closure.classes)) == kernel(
        readings[PERSPECTIVE_A]
    )
    for state_id in ("a", "b", "c"):
        assert frozenset(derived.vis_closure([state_id])) == close(
            readings[PERSPECTIVE_A], {state_id}
        )
        assert close(readings[PERSPECTIVE_A], {state_id}) == close(
            readings[PERSPECTIVE_B], {state_id}
        )

    chart_witness = derived.perspective_visual_mirror.translation_witnesses[0]
    assert chart_witness.witnessed is True
    assert chart_witness.faithful is True
    assert chart_witness.same_kernel is True

    changed_provenance = [
        {
            **form,
            "state": {
                **form["state"],
                "source_stream": f"changed:{index}",
            },
        }
        for index, form in enumerate(forms)
    ]
    changed = derive_closure(
        changed_provenance,
        perspective_readings=readings,
        perspective_translations=[translation],
    )
    assert changed.id != derived.id
    assert changed.equivalence_closure.classes == derived.equivalence_closure.classes
    assert {
        frozenset(form.members) for form in changed.natural_forms
    } == {frozenset(form.members) for form in derived.natural_forms}

    unwitnessed = derive_closure(
        forms,
        perspective_readings=readings,
    )
    assert unwitnessed.status == "OPEN_UNTRANSLATED_PERSPECTIVES"
    assert unwitnessed.supernet_open is True
    assert unwitnessed.natural_forms == ()


def test_legacy_event_store_adds_source_stream_idempotently(tmp_path: Path) -> None:
    database = tmp_path / "legacy-source-stream.db"
    with sqlite3.connect(database) as connection:
        connection.executescript(
            """
            CREATE TABLE supernet_integration_events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT NOT NULL UNIQUE,
                external_key TEXT UNIQUE,
                exact_source_ids TEXT NOT NULL,
                authored_by TEXT NOT NULL,
                perspective_id TEXT,
                problem_id TEXT,
                action_id TEXT,
                form_label TEXT NOT NULL,
                language_label TEXT,
                visibility TEXT NOT NULL,
                capabilities TEXT NOT NULL,
                constraints TEXT NOT NULL,
                relation_hints TEXT NOT NULL,
                causal_predecessor_ids TEXT NOT NULL,
                parent_event_ids TEXT NOT NULL,
                affected_perspectives TEXT NOT NULL,
                evidence_status TEXT NOT NULL,
                adapter_label TEXT,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE supernet_integration_states (
                id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL REFERENCES supernet_integration_events(id),
                stage TEXT NOT NULL,
                verdict TEXT NOT NULL,
                reason TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                rigidity_scope TEXT NOT NULL,
                rigidity_receipt TEXT,
                determined_form TEXT,
                unitary_path_partition TEXT,
                returned_resource_ids TEXT NOT NULL,
                successor_potential TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        connection.execute(
            """INSERT INTO supernet_integration_events(
                id,external_key,exact_source_ids,authored_by,perspective_id,
                problem_id,action_id,form_label,language_label,visibility,
                capabilities,constraints,relation_hints,causal_predecessor_ids,
                parent_event_ids,affected_perspectives,evidence_status,
                adapter_label,metadata,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                "event:legacy",
                "legacy-key",
                json.dumps(["occurrence:legacy"]),
                "legacy-author",
                PERSPECTIVE_A,
                None,
                None,
                "legacy source",
                None,
                "PUBLIC",
                "[]",
                "[]",
                "[]",
                "[]",
                "[]",
                json.dumps([PERSPECTIVE_A]),
                "ORIGINAL_NOTE",
                None,
                "{}",
                "2026-08-31T00:00:00+00:00",
            ),
        )
        connection.execute(
            """INSERT INTO supernet_integration_states(
                id,event_id,stage,verdict,reason,actor_id,rigidity_scope,
                rigidity_receipt,determined_form,unitary_path_partition,
                returned_resource_ids,successor_potential,metadata,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                "state:legacy",
                "event:legacy",
                "SOURCE_PRESERVED",
                "OPEN",
                "Legacy exact source entered the field",
                "legacy-author",
                "[]",
                None,
                None,
                None,
                "[]",
                "[]",
                "{}",
                "2026-08-31T00:00:00+00:00",
            ),
        )
        connection.commit()

    store = SupernetIntegrationStore(database)
    try:
        columns = {
            str(row["name"]): row
            for row in store._conn.execute(  # noqa: SLF001 - migration contract
                "PRAGMA table_info(supernet_integration_events)"
            ).fetchall()
        }
        assert columns["source_stream"]["notnull"] == 1
        assert columns["source_stream"]["dflt_value"] == "'legacy'"

        legacy = store.get_event("event:legacy")
        assert legacy["seq"] == 1
        assert legacy["source_stream"] == "legacy"
        assert legacy["exact_source_ids"] == ["occurrence:legacy"]
        assert legacy["current_stage"] == "SOURCE_PRESERVED"
        assert legacy["current_verdict"] == "OPEN"

        current, created = store.create_event(
            {
                "external_key": "current-key",
                "exact_source_ids": ["occurrence:current"],
                "authored_by": "current-author",
                "perspective_id": PERSPECTIVE_B,
                "form_label": "current source",
                "source_stream": "human-intent",
            }
        )
        assert created is True
        assert current["source_stream"] == "human-intent"

        replay, created = store.create_event(
            {
                "external_key": "current-key",
                "exact_source_ids": ["occurrence:replacement"],
                "authored_by": "replacement-author",
                "form_label": "replacement source",
                "source_stream": "sensor-return",
            }
        )
        assert created is False
        assert replay["id"] == current["id"]
        assert replay["source_stream"] == "human-intent"
    finally:
        store.close()

    reopened = SupernetIntegrationStore(database)
    try:
        assert reopened.get_event("event:legacy")["source_stream"] == "legacy"
        persisted = reopened.get_by_external_key("current-key")
        assert persisted is not None
        assert persisted["source_stream"] == "human-intent"
        assert len(reopened.list_events()) == 2
    finally:
        reopened.close()


def test_public_projection_uses_one_canonical_store_and_continues_after_restart(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    database = config.database_path

    app = create_app(config)
    with TestClient(app) as client:
        initial = client.get(
            "/supernet/interface",
            params={"perspective_id": PERSPECTIVE_A},
        ).json()["closure_ui_contract"]
        assert initial["status"] == "OPEN_SOURCE_BOUNDARY"
        assert initial["perspective_closure"]["status"] == "OPEN_SOURCE_BOUNDARY"
        assert initial["perspective_closure"]["readings"] == {}
        assert initial["perspective_closure"]["translations"] == []
        assert initial["closure_process"]["continuing_existence"][
            "continuation_index"
        ] == 0
        assert_no_absolute_claims(initial)

        forged = client.post(
            RETURN_ENDPOINT_TEMPLATE.format(contract_id=initial["id"]),
            json={
                **return_request(
                    initial,
                    "A client-authored certificate must not enter closure.",
                    source_stream="human-intent",
                ),
                "truth_issued": True,
                "perspective_closure": {"status": "WITNESSED"},
                "closure_process": {"status": "WITNESSED"},
            },
        )
        assert forged.status_code == 422
        assert event_rows(database) == []

        first_request, first_payload = execute_return(
            client,
            initial,
            "I intend to grow food with my neighbors.",
            source_stream="human-intent",
        )
        first = first_payload["closure_ui_contract"]
        assert first_payload["replayed"] is False
        assert first["status"] == "WITNESSED"
        assert_closure_process(first, continuation_index=1)

        replay = client.post(
            RETURN_ENDPOINT_TEMPLATE.format(contract_id=initial["id"]),
            json=first_request,
        )
        assert replay.status_code == 200, replay.text
        assert replay.json()["replayed"] is True
        assert replay.json()["focus_event_id"] == first_payload["focus_event_id"]
        assert replay.json()["closure_ui_contract"] == first

        other_view = client.get(
            "/supernet/interface",
            params={"perspective_id": PERSPECTIVE_B},
        ).json()["closure_ui_contract"]
        second_request, second_payload = execute_return(
            client,
            other_view,
            "The same garden returns through another perspective.",
            source_stream="digital-interaction",
        )
        second = second_payload["closure_ui_contract"]
        assert second_payload["replayed"] is False
        assert_closure_process(second, continuation_index=2)
        assert_translated_perspective_closure(
            second,
            PERSPECTIVE_A,
            PERSPECTIVE_B,
        )

        harry_view = client.get(
            "/supernet/interface",
            params={"perspective_id": PERSPECTIVE_A},
        ).json()["closure_ui_contract"]
        assert_translated_perspective_closure(
            harry_view,
            PERSPECTIVE_A,
            PERSPECTIVE_B,
        )
        assert harry_view["closure_derivation_id"] == second[
            "closure_derivation_id"
        ]
        assert harry_view["visual_closure_id"] == second["visual_closure_id"]
        assert harry_view["projection"]["reading"] != second["projection"][
            "reading"
        ]

        rows = event_rows(database)
        assert len(rows) == 2
        assert [row["source_stream"] for row in rows] == [
            "human-intent",
            "digital-interaction",
        ]
        states_by_event = {
            state["event_id"]: state["id"]
            for state in second["projection"]["states"]
        }
        first_state = states_by_event[first_payload["focus_event_id"]]
        second_state = states_by_event[second_payload["focus_event_id"]]
        assert any(
            {first_state, second_state}.issubset(fibre["member_state_ids"])
            for fibre in second["projection"]["equality_fibres"]
        )

        with sqlite3.connect(database) as connection:
            connection.row_factory = sqlite3.Row
            tables = {
                str(row[0])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            receipts = connection.execute(
                """SELECT id,source_event_id,parent_receipt_ids,receipt
                FROM supernet_visual_closure_receipts ORDER BY seq"""
            ).fetchall()
        assert "supernet_integration_events" in tables
        assert "translational_returns" not in tables
        assert len(receipts) == 2
        first_receipt = json.loads(receipts[0]["receipt"])
        second_receipt = json.loads(receipts[1]["receipt"])
        assert first_receipt["protocol"] == (
            "closure.supernet/conscious-interactive-projection-v1"
        )
        assert first_receipt["source_provenance"]["source_stream"] == (
            "human-intent"
        )
        assert json.loads(receipts[0]["parent_receipt_ids"]) == []
        assert json.loads(receipts[1]["parent_receipt_ids"]) == [
            receipts[0]["id"]
        ]
        assert second_receipt["source_provenance"]["source_stream"] == (
            "digital-interaction"
        )
        assert second_receipt["source_provenance"][
            "source_stream_defines_equality"
        ] is False
        assert second_receipt["external_resource_admitted"] is False

    restarted = create_app(config)
    with TestClient(restarted) as client:
        resumed = client.get(
            "/supernet/interface",
            params={"perspective_id": PERSPECTIVE_A},
        ).json()["closure_ui_contract"]
        assert_closure_process(resumed, continuation_index=2)
        assert {state["source_trace"] for state in resumed["projection"]["states"]} == {
            "I intend to grow food with my neighbors.",
            "The same garden returns through another perspective.",
        }

        replay = client.post(
            RETURN_ENDPOINT_TEMPLATE.format(contract_id=other_view["id"]),
            json=second_request,
        )
        assert replay.status_code == 200, replay.text
        assert replay.json()["replayed"] is True
        assert len(event_rows(database)) == 2

        _third_request, third_payload = execute_return(
            client,
            resumed,
            "The returned closure opens the next exact continuation.",
            source_stream="human-intent",
        )
        third = third_payload["closure_ui_contract"]
        assert_closure_process(third, continuation_index=3)
        assert len(event_rows(database)) == 3
        assert len(third["projection"]["states"]) == 3
        assert third["return_relation"]["reclose_after_return"] is True

        with sqlite3.connect(database) as connection:
            connection.row_factory = sqlite3.Row
            receipts = connection.execute(
                """SELECT id,parent_receipt_ids
                FROM supernet_visual_closure_receipts ORDER BY seq"""
            ).fetchall()
            executions = connection.execute(
                """SELECT status FROM supernet_closure_ui_executions
                ORDER BY created_at"""
            ).fetchall()
        assert len(receipts) == 3
        assert json.loads(receipts[-1]["parent_receipt_ids"]) == [
            receipts[-2]["id"]
        ]
        assert [row["status"] for row in executions] == [
            "COMPLETED",
            "COMPLETED",
            "COMPLETED",
        ]


def test_return_enumeration_pages_past_one_hundred_thousand(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    ledger = TranslationalReturnLedger(tmp_path / "pagination.db")
    total = 100_003
    offsets: list[int] = []
    public_event = {"visibility": "PUBLIC"}

    def fake_list_events(*, limit: int, offset: int) -> list[dict[str, Any]]:
        offsets.append(offset)
        remaining = max(0, total - offset)
        return [public_event] * min(limit, remaining)

    monkeypatch.setattr(ledger.supernet, "list_events", fake_list_events)
    monkeypatch.setattr(ledger, "_return_from_event", lambda event: event)
    try:
        returns = ledger.list_returns()
    finally:
        ledger.close()

    assert len(returns) == total
    assert offsets[0] == 0
    assert 100_000 in offsets


def test_branched_continuations_keep_focused_lineage_and_receipt_parent(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    app = create_app(config)
    with TestClient(app) as client:
        initial = client.get(
            "/supernet/interface",
            params={"perspective_id": PERSPECTIVE_A},
        ).json()["closure_ui_contract"]
        _request, first_payload = execute_return(
            client,
            initial,
            "The root closure returns.",
            source_stream="human-intent",
        )
        first_id = first_payload["focus_event_id"]

        first_focus = client.get(
            "/supernet/interface",
            params={
                "perspective_id": PERSPECTIVE_A,
                "focus_event_id": first_id,
            },
        ).json()["closure_ui_contract"]
        _request, left_payload = execute_return(
            client,
            first_focus,
            "The left continuation returns.",
            source_stream="digital-interaction",
        )
        left_id = left_payload["focus_event_id"]
        assert left_payload["closure_ui_contract"][
            "continuation_lineage_ids"
        ] == [first_id, left_id]

        first_focus_again = client.get(
            "/supernet/interface",
            params={
                "perspective_id": PERSPECTIVE_B,
                "focus_event_id": first_id,
            },
        ).json()["closure_ui_contract"]
        assert first_focus_again["continuation_lineage_ids"] == [first_id]
        _request, right_payload = execute_return(
            client,
            first_focus_again,
            "The right continuation returns independently.",
            source_stream="sensor-return",
        )
        right_id = right_payload["focus_event_id"]
        right_contract = right_payload["closure_ui_contract"]
        assert right_contract["continuation_lineage_ids"] == [first_id, right_id]
        assert right_contract["continuation_index"] == 2
        assert len(right_contract["source_return_ids"]) == 3

        receipts = app.state.runtime.ledger.supernet.list_visual_closure_receipts()
        by_event = {str(item["source_event_id"]): item for item in receipts}
        assert by_event[first_id]["parent_receipt_ids"] == []
        assert by_event[left_id]["parent_receipt_ids"] == [
            by_event[first_id]["id"]
        ]
        assert by_event[right_id]["parent_receipt_ids"] == [
            by_event[first_id]["id"]
        ]


def test_stranded_execution_retries_without_duplicate_durable_artifacts(
    tmp_path: Path,
) -> None:
    for fault_after_receipt in (False, True):
        config = make_config(tmp_path / str(fault_after_receipt))
        app = create_app(config)
        with TestClient(app, raise_server_exceptions=False) as client:
            initial = client.get(
                "/supernet/interface",
                params={"perspective_id": PERSPECTIVE_A},
            ).json()["closure_ui_contract"]
            request = return_request(
                initial,
                "A fault cannot exhaust this exact return.",
                source_stream="fault-injection",
            )
            store = app.state.runtime.ledger.supernet
            original_append_receipt = store.append_visual_closure_receipt
            faulted = False

            def inject_fault(*args: Any, **kwargs: Any) -> Any:
                nonlocal faulted
                if faulted:
                    return original_append_receipt(*args, **kwargs)
                faulted = True
                if not fault_after_receipt:
                    raise RuntimeError("injected fault after event")
                result = original_append_receipt(*args, **kwargs)
                raise RuntimeError("injected fault after receipt")

            store.append_visual_closure_receipt = inject_fault
            failed = client.post(
                RETURN_ENDPOINT_TEMPLATE.format(contract_id=initial["id"]),
                json=request,
            )
            assert failed.status_code == 500
            store.append_visual_closure_receipt = original_append_receipt

            recovered = client.post(
                RETURN_ENDPOINT_TEMPLATE.format(contract_id=initial["id"]),
                json=request,
            )
            assert recovered.status_code == 200, recovered.text
            recovered_payload = recovered.json()
            assert recovered_payload["replayed"] is True
            assert recovered_payload["returned"] is True
            assert recovered_payload["closure_ui_contract"][
                "continuation_lineage_ids"
            ] == [recovered_payload["focus_event_id"]]

            with sqlite3.connect(config.database_path) as connection:
                occurrence_count = connection.execute(
                    "SELECT COUNT(*) FROM occurrences"
                ).fetchone()[0]
                event_count = connection.execute(
                    "SELECT COUNT(*) FROM supernet_integration_events"
                ).fetchone()[0]
                receipt_count = connection.execute(
                    "SELECT COUNT(*) FROM supernet_visual_closure_receipts"
                ).fetchone()[0]
                execution = connection.execute(
                    """SELECT status FROM supernet_closure_ui_executions"""
                ).fetchone()[0]
            assert occurrence_count == 1
            assert event_count == 1
            assert receipt_count == 1
            assert execution == "COMPLETED"
