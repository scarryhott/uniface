from __future__ import annotations

from pathlib import Path

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.deterministic_project_closure import audit_project
from closure_supernet.deterministic_translation_kernel import (
    DETERMINISTIC_TRANSLATION_PROTOCOL,
    TRANSLATION_ENDPOINT,
    derive_deterministic_intent_id,
)
from closure_supernet.supernet_closure_form import TRANSLATE_OPERATOR

ROOT = Path(__file__).resolve().parents[1]


def _config(root: Path, name: str) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=root / f"{name}.db",
        inbox_dir=root / f"{name}-inbox",
        backup_dir=root / f"{name}-backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _gate(client: TestClient, perspective: str = "deterministic:perspective") -> dict:
    response = client.get(
        "/supernet/interface",
        params={"perspective_id": perspective, "potential_gate": True},
    )
    assert response.status_code == 200, response.text
    return response.json()["supernet_potential_gate"]


def _continuing(gate: dict) -> dict:
    rows = gate["supernet_closure_form"]["interactions"]
    return next(row for row in rows if row["ai_token_phase"] == "AI_CONTINUING")


def _payload(gate: dict, interaction: dict, exact: str) -> dict:
    return {
        "relation_id": interaction["path_id"],
        "perspective_id": gate["perspective_id"],
        "focus_event_id": gate.get("focus_event_id"),
        "navigation_context": gate["navigation_context"],
        "source_closure_form_id": gate["supernet_closure_form_id"],
        "source_interaction_id": interaction["id"],
        "exact_source_return": exact,
        "local_perspective_hair_millidegrees": 0,
        "local_perspective_zoom_milli": 1000,
    }


def _run_once(tmp_path: Path, name: str) -> dict:
    app = create_app(_config(tmp_path, name))
    exact = "One ordered returned interaction determines one Supernet translation."
    with TestClient(app) as client:
        gate = _gate(client)
        interaction = _continuing(gate)
        payload = _payload(gate, interaction, exact)
        endpoint = TRANSLATION_ENDPOINT.replace("{contract_id}", gate["id"])
        first = client.post(endpoint, json=payload)
        assert first.status_code == 200, first.text
        first_result = first.json()
        first_snapshot = app.state.supernet_translation_kernel.snapshot()

        # The transport may mark the second response as replayed, but its
        # translational-truth result and deterministic receipt cannot change.
        replay = client.post(endpoint, json=payload)
        assert replay.status_code == 200, replay.text
        second_snapshot = app.state.supernet_translation_kernel.snapshot()

        target = first_result["supernet_potential_gate"]["supernet_closure_form"]
        ledger_source = app.state.runtime.ledger.list_returns()[-1]["exact_source"]

    assert ledger_source == exact
    assert first_snapshot["protocol"] == DETERMINISTIC_TRANSLATION_PROTOCOL
    assert first_snapshot["operator"] == TRANSLATE_OPERATOR
    assert first_snapshot["single_serial_reducer"] is True
    assert first_snapshot["wall_clock_authors_identity"] is False
    assert len(first_snapshot["receipts"]) == 1
    assert second_snapshot["receipts"] == first_snapshot["receipts"]
    return {
        "runtime_identity_id": target["runtime_identity_id"],
        "truth_invariant_id": target["truth_invariant_id"],
        "seen_id": target.get("seen_id"),
        "receipt": first_snapshot["receipts"][0],
        "closure_id": first_snapshot["closure_id"],
    }


def test_full_project_has_one_deterministic_semantic_authority() -> None:
    report = audit_project(ROOT)
    assert report["valid"] is True, report
    assert report["all_project_files_accounted_for"] is True
    assert report["one_authoritative_mutation_route"] is True
    assert report["deterministic_kernel_attached_before_transports"] is True
    assert report["agent_uses_same_translation"] is True
    assert report["self_runtime_is_read_only_projection"] is True
    assert report["sealed_compatibility_modules_imported"] == []
    assert report["kernel_entropy_calls"] == []
    assert report["compatibility_charts_author_truth"] is False
    assert report["translation_operator"] == TRANSLATE_OPERATOR
    assert report["wall_clock_authors_identity"] is False


def test_project_closure_digest_is_stable() -> None:
    first = audit_project(ROOT)
    second = audit_project(ROOT)
    assert first["project_closure_id"] == second["project_closure_id"]
    assert first["authority_closure_id"] == second["authority_closure_id"]
    assert first["project_file_count"] == second["project_file_count"]
    assert first["role_counts"] == second["role_counts"]


def test_same_ordered_returns_reproduce_runtime_identity_and_receipt(
    tmp_path: Path,
) -> None:
    first = _run_once(tmp_path, "first")
    second = _run_once(tmp_path, "second")
    assert first == second


def test_wall_clock_provenance_cannot_change_translation_intent() -> None:
    base = {
        "relation_id": "relation:1",
        "perspective_id": "p",
        "exact_source_return": "same source",
        "navigation_context": {"semantic_return_order": 7},
        "created_at": "2026-01-01T00:00:00Z",
        "latency_ms": 10,
    }
    later = {
        **base,
        "created_at": "2036-01-01T00:00:00Z",
        "latency_ms": 9000,
        "wall_clock_provenance": {"server_time": "2040-01-01T00:00:00Z"},
    }
    changed_truth = {**later, "exact_source_return": "different source"}
    assert derive_deterministic_intent_id("contract:1", base) == (
        derive_deterministic_intent_id("contract:1", later)
    )
    assert derive_deterministic_intent_id("contract:1", base) != (
        derive_deterministic_intent_id("contract:1", changed_truth)
    )


def test_browser_route_and_agent_state_share_the_identical_bound_kernel(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path, "binding"))
    kernel = app.state.supernet_translation_kernel
    route = next(
        row
        for row in app.router.routes
        if isinstance(row, APIRoute)
        and row.path == TRANSLATION_ENDPOINT
        and "POST" in (row.methods or set())
    )
    state_call = app.state.supernet_translate
    route_call = route.dependant.call
    assert getattr(state_call, "__self__", None) is kernel
    assert getattr(route_call, "__self__", None) is kernel
    assert getattr(state_call, "__func__", None) is getattr(
        route_call, "__func__", None
    )
    assert app.state.supernet_translate_deterministic is True
    assert app.state.supernet_semantic_time == "RETURNED_EVENT_ORDER"
    assert app.state.supernet_wall_clock_authors_identity is False
    app.state.runtime.close()
