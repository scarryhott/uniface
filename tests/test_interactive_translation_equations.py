from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from closure_supernet.api_interactive_translation import create_app
from closure_supernet.interactive_translation_equations import (
    resolve_closure_equations,
    resolve_legacy_equation,
    resolve_reopening_equation,
    resolve_resource_equation,
    resolve_rule_chart_equation,
    resolve_trading_equation,
)


def test_reopening_is_generated_by_returned_readings_not_a_mode_enum() -> None:
    receipt = resolve_reopening_equation(
        assumption_ids=["a", "b", "c"],
        returned_readings=[
            {"id": "return-a", "held_ids": ["a", "b"]},
            {"id": "return-b", "held_ids": ["b", "c"]},
        ],
    )

    assert receipt["status"] == "WITNESSED"
    assert receipt["relative_unity_residue_ids"] == ["b"]
    assert receipt["mode_enum"] is None
    assert receipt["mode_is_semantic"] is False
    assert all(
        item["operation_enum"] is None
        for item in receipt["returned_readings"]
    )


def test_reopening_computation_bound_is_open_not_a_residue() -> None:
    receipt = resolve_reopening_equation(
        assumption_ids=["a", "b"],
        returned_readings=[
            {"id": "return-a", "held_ids": ["a"]},
            {"id": "return-b", "held_ids": ["b"]},
        ],
        max_readings=1,
    )

    assert receipt["status"] == "OPEN"
    assert receipt["relative_unity_residue_ids"] is None
    assert receipt["boundary_receipt"]["status"] == "OPEN"
    assert receipt["boundary_receipt"]["limit_is_semantic"] is False


def test_participant_rule_charts_translate_by_equal_closure_not_syntax() -> None:
    receipt = resolve_rule_chart_equation(
        charts=[
            {
                "id": "chart-p",
                "label": "first syntax",
                "seed": ["a"],
                "rules": [
                    {
                        "premise_occurrence_ids": ["a"],
                        "conclusion_occurrence_id": "b",
                    }
                ],
                "source_ids": ["return-p"],
            },
            {
                "id": "chart-q",
                "label": "other syntax",
                "seed": ["a", "b"],
                "rules": [],
                "source_ids": ["return-q"],
            },
        ]
    )

    assert receipt["status"] == "WITNESSED"
    assert len(receipt["relative_closure_classes"]) == 1
    assert set(receipt["relative_closure_classes"][0]["chart_ids"]) == {
        "chart-p",
        "chart-q",
    }
    assert all(
        item["syntax_labels_define_equality"] is False
        for item in receipt["charts"]
    )


def test_trading_quote_proposal_is_inert_until_authenticated_return() -> None:
    proposal = {
        "form_id": "form",
        "relation": {"route": ["USD", "BTC", "USD"]},
        "estimated_profit": "100",
        "source_ids": ["quote"],
    }
    proposed = resolve_trading_equation(proposals=[proposal])

    assert proposed["status"] == "OPEN"
    assert proposed["proposals"][0]["proposal_can_gate"] is False
    assert proposed["forms"][0]["gate_open"] is False

    returned = resolve_trading_equation(
        proposals=[proposal],
        receipts=[
            {
                "form_id": "form",
                "relation": {"route": ["USD", "BTC", "USD"]},
                "id": "fill-return",
                "authenticated": True,
                "closed": True,
                "realized_profit": "4",
                "rate": "2",
                "duration": {"opened": "t0", "closed": "t1"},
            }
        ],
    )

    form = returned["forms"][0]
    assert returned["status"] == "WITNESSED"
    assert form["gate_open"] is True
    assert form["profit_floor"] == "4"
    assert form["base_energy_profit_floor"] == "2"
    assert form["fixed_horizon"] is None
    assert form["horizon_is_semantic"] is False


def test_authenticated_trading_loss_witnesses_a_closed_gate() -> None:
    receipt = resolve_trading_equation(
        receipts=[
            {
                "relation": ["a", "b", "a"],
                "id": "loss-return",
                "authenticated": True,
                "closed_relation": True,
                "realized_profit": "-1",
            }
        ]
    )

    form = receipt["forms"][0]
    assert form["status"] == "WITNESSED"
    assert form["gate_open"] is False
    assert form["profit_floor"] == "-1"


def test_unauthenticated_or_open_trading_receipt_cannot_instantiate_form() -> None:
    receipt = resolve_trading_equation(
        receipts=[
            {
                "relation": ["a", "b"],
                "id": "not-closed",
                "authenticated": True,
                "closed_relation": False,
                "realized_profit": "99",
            },
            {
                "relation": ["a", "b", "a"],
                "id": "not-authenticated",
                "authenticated": False,
                "closed_relation": True,
                "realized_profit": "99",
            },
        ]
    )

    assert receipt["status"] == "OPEN"
    assert len(receipt["unmatched_or_open_receipts"]) == 2
    assert all(item["status"] == "OPEN" for item in receipt["forms"])


def test_resource_schedule_is_dependency_closure_and_limit_is_open() -> None:
    returns = [
        {
            "id": "return-a",
            "source_resource_id": "source",
            "returned_resource_id": "middle",
            "exact_source": "first return",
        },
        {
            "id": "return-b",
            "source_resource_id": "middle",
            "returned_resource_id": "target",
            "dependencies": ["return-a"],
            "exact_source": "second return",
        },
    ]
    complete = resolve_resource_equation(pending_returns=returns)

    assert complete["status"] == "WITNESSED"
    assert [
        item["return_id"] for item in complete["selected_returns"]
    ] == ["return-a", "return-b"]
    assert complete["dependency_waves"] == [["return-a"], ["return-b"]]
    assert complete["queue_order_is_semantic"] is False

    bounded = resolve_resource_equation(
        pending_returns=returns,
        limit=1,
    )
    assert bounded["status"] == "OPEN"
    assert bounded["boundary_receipt"]["limit_is_semantic"] is False
    assert bounded["open_returns"][0]["return_id"] == "return-b"


def test_resource_dependency_cycle_remains_open() -> None:
    receipt = resolve_resource_equation(
        pending_returns=[
            {
                "id": "a",
                "source_resource_id": "x",
                "returned_resource_id": "y",
                "dependencies": ["b"],
                "exact_source": "a",
            },
            {
                "id": "b",
                "source_resource_id": "y",
                "returned_resource_id": "x",
                "dependencies": ["a"],
                "exact_source": "b",
            },
        ]
    )

    assert receipt["status"] == "OPEN"
    assert not receipt["selected_returns"]
    assert all(
        item["open_reason"] == "UNRETURNED_OR_CYCLIC_DEPENDENCY"
        for item in receipt["open_returns"]
    )


def test_legacy_runtime_is_a_nonblocking_compatibility_reading() -> None:
    receipt = resolve_legacy_equation(
        closure_derivation_id="closure-1",
        components={
            "current_projection": {"closure_derivation_id": "closure-1"},
            "historical_trading_manager": {"status": "TRUE"},
        },
        production_components=["current_projection"],
        legacy_test_modules=["tests/test_trading_supernet.py"],
    )

    assert receipt["status"] == "WITNESSED"
    assert receipt["legacy_runtime_can_gate"] is False
    assert receipt["test_lanes"]["core"]["blocking"] is True
    assert receipt["test_lanes"]["legacy_runtime"]["blocking"] is False
    assert receipt["test_lanes"]["legacy_runtime"]["failures_remain_visible"] is True


def test_bundle_uses_one_equation_and_passes_continuity_audit() -> None:
    receipt = resolve_closure_equations(
        {
            "reopening": {
                "assumption_ids": ["a"],
                "returned_readings": [{"id": "r", "held_ids": ["a"]}],
            },
            "resources": {
                "pending_returns": [
                    {
                        "id": "resource-return",
                        "source_resource_id": "a",
                        "returned_resource_id": "b",
                        "exact_source": "return",
                    }
                ]
            },
        }
    )

    assert receipt["status"] == "WITNESSED"
    assert receipt["only_returned_interaction_recloses"] is True
    assert receipt["continuity_audit"]["status"] == "WITNESSED"
    assert receipt["dialectic_continuation_status"] == "OPEN"


def test_published_api_resolves_equations_without_mutating_projection(tmp_path) -> None:
    app = create_app(
        SimpleNamespace(database_path=tmp_path / "closure-equations.db")
    )
    with TestClient(app) as client:
        before = client.get("/supernet/interface").json()["closure_ui_contract"]
        capabilities = client.get(
            "/supernet/closure-equations/capabilities"
        )
        assert capabilities.status_code == 200
        assert capabilities.json()["only_returned_interaction_recloses"] is True

        response = client.post(
            "/supernet/closure-equations/resolve",
            json={
                "trading": {
                    "receipts": [
                        {
                            "relation": ["USD", "A", "USD"],
                            "id": "receipt",
                            "authenticated": True,
                            "closed_relation": True,
                            "realized_profit": "1",
                        }
                    ]
                }
            },
        )
        assert response.status_code == 200
        assert response.json()["trading"]["forms"][0]["gate_open"] is True

        after = client.get("/supernet/interface").json()["closure_ui_contract"]
        assert after["id"] == before["id"]
