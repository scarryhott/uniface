from decimal import Decimal

from closure_supernet.trading_live_interaction_integration_nrrf892 import (
    derive_live_interaction_integration,
)


def _action(fid="A", truth="TA", horizon=5):
    return {
        "family_id": fid,
        "closure_truth_id": truth,
        "status": "WITNESSED",
        "relative_hair_horizon_return_steps": horizon,
    }


def _render(fid="A", truth="TA", side="BUY", delta="1"):
    return {
        "family_id": fid,
        "closure_truth_id": truth,
        "status": "WITNESSED",
        "unique_slide_amount": delta,
        "market_side": side,
        "market_side_status": "WITNESSED",
    }


def _current(action=None, *, profit_status="WITNESSED", profit_delta="0", total="0"):
    return {
        "current_revision": 1,
        "translational_truth_action_field": {
            "actions": [action or _action()],
        },
        "realized_profit_projection": {
            "status": profit_status,
            "new_realized_profit_delta_quote": profit_delta,
            "realized_net_profit_quote": total,
            "open_net_profit_temporal_closure_ids": [] if profit_status == "WITNESSED" else ["c-open"],
        },
    }


def _trading(qid, bid, ask):
    return {
        "symbol": "BTC/USD",
        "quote_projections": [
            {
                "source_event_id": qid,
                "timestamp": qid,
                "best_bid": str(bid),
                "best_ask": str(ask),
            }
        ],
    }


def test_same_rendering_persists_over_new_quote_returns_and_integrates_gross_move():
    first = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(_action(horizon=7)),
        nrrf892_rendering={"renderings": [_render()]},
    )
    second = derive_live_interaction_integration(
        trading_receipt=_trading("q2", 102, 104),
        continuous_current=_current(_action(horizon=7)),
        nrrf892_rendering={"renderings": [_render(delta="3/2")]},
        prior_integration=first,
    )
    row = second["family_integrations"][0]
    assert row["formal_tt_horizon_return_steps"] == 7
    assert row["vision_horizon_quote_returns"] == 2
    assert Decimal(row["vision_run_gross_bps"]) > 0
    assert row["vision_horizon_substitutes_for_formal_tt_horizon"] is False
    assert row["fixed_holding_period_used"] is False
    assert row["future_return_used"] is False


def test_replayed_quote_does_not_extend_vision_horizon_or_double_count_gross():
    first = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(),
        nrrf892_rendering={"renderings": [_render()]},
    )
    second = derive_live_interaction_integration(
        trading_receipt=_trading("q2", 102, 104),
        continuous_current=_current(),
        nrrf892_rendering={"renderings": [_render()]},
        prior_integration=first,
    )
    replay = derive_live_interaction_integration(
        trading_receipt=_trading("q2", 102, 104),
        continuous_current=_current(),
        nrrf892_rendering={"renderings": [_render()]},
        prior_integration=second,
    )
    a = second["family_integrations"][0]
    b = replay["family_integrations"][0]
    assert replay["new_quote_return"] is False
    assert b["vision_horizon_quote_returns"] == a["vision_horizon_quote_returns"]
    assert b["vision_run_gross_bps"] == a["vision_run_gross_bps"]


def test_side_flip_naturally_ends_prior_vision_run_without_fixed_horizon():
    first = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(),
        nrrf892_rendering={"renderings": [_render(side="BUY")]},
    )
    second = derive_live_interaction_integration(
        trading_receipt=_trading("q2", 103, 105),
        continuous_current=_current(),
        nrrf892_rendering={"renderings": [_render(side="SELL", delta="-1")]},
        prior_integration=first,
    )
    assert second["completed_vision_run_count"] == 1
    closed = second["completed_vision_runs"][-1]
    assert closed["prior_market_side"] == "BUY"
    assert closed["ended_by_rendering_change"] is True
    assert closed["gross_interaction_bps"] is not None
    assert closed["spread_lower_bound_bps"] is not None
    assert second["family_integrations"][0]["market_side"] == "SELL"
    assert second["family_integrations"][0]["vision_horizon_quote_returns"] == 1


def test_spread_margin_is_only_lower_bound_not_realized_profit():
    result = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(),
        nrrf892_rendering={"renderings": [_render()]},
    )
    row = result["family_integrations"][0]
    assert row["spread_lower_bound_bps"] is not None
    assert row["spread_is_complete_execution_cost"] is False
    assert row["public_mid_move_is_realized_profit"] is False
    assert result["spread_lower_bound_is_not_realized_profit"] is True


def test_actual_returned_profit_is_exposed_separately_from_shadow_margin():
    result = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(profit_status="WITNESSED", profit_delta="1.25", total="5.5"),
        nrrf892_rendering={"renderings": [_render()]},
    )
    realized = result["realized_profit"]
    assert realized["status"] == "WITNESSED"
    assert realized["new_realized_profit_delta_quote"] == "1.25"
    assert realized["realized_net_profit_quote"] == "5.5"
    assert realized["is_authoritative_returned_profit"] is True
    assert result["diagnostic_authors_action"] is False


def test_incomplete_returned_cost_keeps_actual_profit_open_without_changing_action():
    result = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(profit_status="OPEN", profit_delta="0", total="0"),
        nrrf892_rendering={"renderings": [_render()]},
    )
    assert result["realized_profit"]["status"] == "OPEN"
    assert result["family_integrations"][0]["market_side"] == "BUY"
    assert result["diagnostic_authors_action"] is False
    assert result["diagnostic_authors_truth"] is False


def test_noop_has_zero_vision_horizon_and_no_spread_trade_claim():
    result = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(),
        nrrf892_rendering={"renderings": [_render(side="NOOP", delta="0")]},
    )
    row = result["family_integrations"][0]
    assert row["vision_horizon_quote_returns"] == 0
    assert row["spread_lower_bound_bps"] is None
    assert row["spread_lower_bound_positive"] is None
