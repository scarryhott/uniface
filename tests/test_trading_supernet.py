from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_trading import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.trading_models import (
    CircuitEdgeCreate,
    ClassicalTransactionCreate,
    NumeraireEvaluationCreate,
    PnLEvaluationCreate,
    PriceShiftEvaluationCreate,
    TradingCircuitEvaluationCreate,
    TradingSystemEvaluationCreate,
)


def config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "trading.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


def test_crossing_buy_is_selector_determined_open_and_net_is_negative_cost(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(config(tmp_path))
    try:
        async def scenario() -> None:
            tx = await runtime.trading.create_transaction(
                ClassicalTransactionCreate(
                    symbol="DEMO",
                    signed_size="2",
                    bid="99",
                    ask="101",
                    mark="100",
                    fee="0.5",
                    authored_by="trader-a",
                )
            )
            evaluation = tx["evaluation"]
            assert tx["fill"] == "101"
            assert evaluation["side"] == "BUY"
            assert evaluation["execution_rigid"] is True
            assert evaluation["inf_cost"] == "2.5"
            assert evaluation["net_flow"] == "-2.5"
            assert evaluation["net_eq_neg_cost"] is True
            assert evaluation["crossing_strictly_negative"] is True
            assert evaluation["layers_complete"] is True
            assert evaluation["drop_fill_not_complete"] is True

            event = runtime.supernet_store.get_event(tx["integration_event_id"])
            assert event["current_stage"] == "RETURNED"
            assert event["current_verdict"] == "OPEN"
            determined = [state for state in event["state_history"] if state["stage"] == "DETERMINED"]
            assert len(determined) == 1
            assert determined[0]["rigidity_receipt"]["admissible_fills"] == ["101"]
            assert determined[0]["metadata"]["truth_issued"] is False
            assert runtime.supernet_field("trading")["stats"]["visible_events"] >= 1

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_sell_crossing_and_system_friction_identity(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(config(tmp_path))
    try:
        async def scenario() -> None:
            buy = await runtime.trading.create_transaction(
                ClassicalTransactionCreate(
                    symbol="DEMO", signed_size="1", bid="99", ask="101", mark="100", fee="0"
                )
            )
            sell = await runtime.trading.create_transaction(
                ClassicalTransactionCreate(
                    symbol="DEMO", signed_size="-1", bid="99", ask="101", mark="100", fee="0"
                )
            )
            assert sell["fill"] == "99"
            assert sell["evaluation"]["net_flow"] == "-1"
            system = await runtime.trading.evaluate_system(
                TradingSystemEvaluationCreate(transaction_ids=[buy["id"], sell["id"]])
            )
            assert system["total_cost"] == "2"
            assert system["total_net"] == "-2"
            assert system["sys_net_eq_neg_sys_cost"] is True
            assert system["strictly_negative_once_charged"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_shift_and_numeraire_invariance(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(config(tmp_path))
    try:
        async def scenario() -> None:
            tx = await runtime.trading.create_transaction(
                ClassicalTransactionCreate(
                    symbol="DEMO", signed_size="3", bid="10", ask="12", mark="11", fee="2"
                )
            )
            shift = await runtime.trading.evaluate_shift(
                PriceShiftEvaluationCreate(transaction_id=tx["id"], shift="100")
            )
            assert shift["flow_shift_invariant"] is True
            assert shift["cost_shift_invariant"] is True
            assert shift["local_price_layer_changed"] is True

            scale = await runtime.trading.evaluate_numeraire(
                NumeraireEvaluationCreate(transaction_id=tx["id"], scale="7")
            )
            assert scale["cost_scales"] is True
            assert scale["flow_scales"] is True
            assert scale["flow_cost_ratio_invariant"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_exact_circuit_loses_friction_and_profit_requires_holonomy(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(config(tmp_path))
    try:
        async def scenario() -> None:
            exact = await runtime.trading.evaluate_circuit(
                TradingCircuitEvaluationCreate(
                    symbol="DEMO",
                    edges=[
                        CircuitEdgeCreate(edge_id="a", local_price_move="2", charge="0.5"),
                        CircuitEdgeCreate(edge_id="b", local_price_move="-2", charge="0.5"),
                    ],
                )
            )
            assert exact["exact_price_field"] is True
            assert exact["global_token_exists"] is True
            assert exact["net_flow"] == "-1.0"
            assert exact["exact_round_trip_eq_neg_cost"] is True
            assert exact["bound_holds"] is True
            assert exact["profitable"] is False

            profitable = await runtime.trading.evaluate_circuit(
                TradingCircuitEvaluationCreate(
                    symbol="DEMO",
                    edges=[
                        CircuitEdgeCreate(edge_id="a", local_price_move="3", charge="0.4"),
                        CircuitEdgeCreate(edge_id="b", local_price_move="-1", charge="0.4"),
                    ],
                )
            )
            assert profitable["profitable"] is True
            assert profitable["profit_needs_arbitrage"] is True
            assert profitable["profit_needs_nonexact"] is True
            assert profitable["global_token_exists"] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_returning_market_pnl_is_minus_cost(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(config(tmp_path))
    try:
        async def scenario() -> None:
            pnl = await runtime.trading.evaluate_pnl(
                PnLEvaluationCreate(
                    symbol="DEMO",
                    position="10",
                    start_mark="100",
                    end_mark="100",
                    accumulated_cost="3.25",
                )
            )
            assert pnl["returning_market"] is True
            assert pnl["pnl"] == "-3.25"
            assert pnl["returning_market_pnl"] == "-3.25"
            assert pnl["returning_market_nonpositive"] is True
            assert pnl["pnl_pos_iff_price_move_beats_cost"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_trading_api_is_simulation_only_and_integrated(tmp_path: Path) -> None:
    app = create_app(config(tmp_path))
    with TestClient(app) as client:
        capabilities = client.get("/network/trading/capabilities")
        assert capabilities.status_code == 200
        cap = capabilities.json()
        assert cap["direct_market_execution"] is False
        assert cap["brokerage_connected"] is False
        assert cap["canonical_runtime_operation"] == "integrate"

        response = client.post(
            "/network/trading/transactions",
            json={
                "symbol": "API",
                "signed_size": "1",
                "bid": "49",
                "ask": "51",
                "mark": "50",
                "fee": "0",
                "authored_by": "api-trader",
            },
        )
        assert response.status_code == 200
        tx = response.json()
        assert tx["evaluation"]["net_eq_neg_cost"] is True

        lens = client.get("/supernet/project", params={"lens": "trading"})
        assert lens.status_code == 200
        assert lens.json()["stats"]["visible_events"] >= 1

        page = client.get("/trading")
        assert page.status_code == 200
        assert "Classical Trading Lens" in page.text
