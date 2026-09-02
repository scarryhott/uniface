from decimal import Decimal

from closure_supernet.trading_live_interaction_integration_nrrf892 import derive_live_interaction_integration


def _action(fid="A", truth="TA", horizon=5, delta="1", size="1000"):
    return {
        "family_id": fid,
        "closure_truth_id": truth,
        "status": "WITNESSED",
        "unique_slide_amount": delta,
        "relative_hair_horizon_return_steps": horizon,
        "relative_ball_size": size,
        "relative_ball_size_unit": "USD-notional",
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
        "translational_truth_action_field": {"actions": [action or _action()]},
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
        "quote_projections": [{
            "source_event_id": qid,
            "timestamp": qid,
            "best_bid": str(bid),
            "best_ask": str(ask),
        }],
    }


def test_exact_same_slide_persists_and_integrates_gross_move():
    first = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(_action(horizon=2, delta="1")),
        nrrf892_rendering={"renderings": [_render(delta="1")]},
    )
    second = derive_live_interaction_integration(
        trading_receipt=_trading("q2", 102, 104),
        continuous_current=_current(_action(horizon=2, delta="1")),
        nrrf892_rendering={"renderings": [_render(delta="1")]},
        prior_integration=first,
    )
    row = second["family_integrations"][0]
    assert row["same_exact_slide_as_prior_return"] is True
    assert row["exact_slide_horizon_quote_returns"] == 2
    assert row["formal_tt_horizon_return_steps"] == 2
    assert row["formal_horizon_reached_by_exact_slide_persistence"] is True
    assert Decimal(row["exact_slide_run_gross_bps"]) > 0
    assert row["fixed_holding_period_used"] is False
    assert row["future_return_used"] is False


def test_same_buy_rendering_but_changed_delta_ends_exact_slide_episode():
    first = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(_action(delta="1")),
        nrrf892_rendering={"renderings": [_render(side="BUY", delta="1")]},
    )
    second = derive_live_interaction_integration(
        trading_receipt=_trading("q2", 102, 104),
        continuous_current=_current(_action(delta="3/2")),
        nrrf892_rendering={"renderings": [_render(side="BUY", delta="3/2")]},
        prior_integration=first,
    )
    row = second["family_integrations"][0]
    assert row["market_side"] == "BUY"
    assert row["same_exact_slide_as_prior_return"] is False
    assert row["exact_slide_changed"] is True
    assert row["exact_slide_horizon_quote_returns"] == 1
    assert row["side_rendering_horizon_quote_returns"] == 2
    assert second["side_only_persistence_authors_interaction_integral"] is False
    assert second["completed_vision_run_count"] == 1
    closed = second["completed_vision_runs"][-1]
    assert closed["ended_by_exact_slide_change"] is True
    assert closed["ended_by_side_change"] is False


def test_side_flip_also_ends_exact_slide_episode():
    first = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(_action(delta="1")),
        nrrf892_rendering={"renderings": [_render(side="BUY", delta="1")]},
    )
    second = derive_live_interaction_integration(
        trading_receipt=_trading("q2", 103, 105),
        continuous_current=_current(_action(delta="-1")),
        nrrf892_rendering={"renderings": [_render(side="SELL", delta="-1")]},
        prior_integration=first,
    )
    closed = second["completed_vision_runs"][-1]
    assert closed["prior_market_side"] == "BUY"
    assert closed["ended_by_exact_slide_change"] is True
    assert closed["ended_by_side_change"] is True
    assert second["family_integrations"][0]["market_side"] == "SELL"
    assert second["family_integrations"][0]["exact_slide_horizon_quote_returns"] == 1


def test_replayed_quote_does_not_extend_exact_slide_horizon_or_gross():
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
    assert b["exact_slide_horizon_quote_returns"] == a["exact_slide_horizon_quote_returns"]
    assert b["exact_slide_run_gross_bps"] == a["exact_slide_run_gross_bps"]


def test_spread_margin_ratio_and_ball_projection_are_shadow_only():
    first = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(_action(size="1000")),
        nrrf892_rendering={"renderings": [_render()]},
    )
    second = derive_live_interaction_integration(
        trading_receipt=_trading("q2", 110, 112),
        continuous_current=_current(_action(size="1000")),
        nrrf892_rendering={"renderings": [_render()]},
        prior_integration=first,
    )
    row = second["family_integrations"][0]
    assert Decimal(row["spread_lower_bound_margin_bps"]) > 0
    assert Decimal(row["spread_lower_bound_ratio"]) > 1
    assert Decimal(row["shadow_margin_at_relative_ball_quote"]) > 0
    assert row["spread_is_complete_execution_cost"] is False
    assert row["public_mid_move_is_realized_profit"] is False
    assert row["exact_slide_profit_function_authors_action"] is False


def test_returned_profit_remains_separate_authoritative_projection():
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
    assert result["diagnostic_authors_truth"] is False


def test_incomplete_returned_cost_does_not_change_slide_action():
    result = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(profit_status="OPEN", profit_delta="0", total="0"),
        nrrf892_rendering={"renderings": [_render()]},
    )
    assert result["realized_profit"]["status"] == "OPEN"
    assert result["family_integrations"][0]["market_side"] == "BUY"
    assert result["diagnostic_authors_action"] is False


def test_noop_has_zero_exact_slide_horizon_and_no_spread_trade_claim():
    result = derive_live_interaction_integration(
        trading_receipt=_trading("q1", 100, 102),
        continuous_current=_current(_action(delta="0")),
        nrrf892_rendering={"renderings": [_render(side="NOOP", delta="0")]},
    )
    row = result["family_integrations"][0]
    assert row["exact_slide_horizon_quote_returns"] == 0
    assert row["spread_lower_bound_bps"] is None
    assert row["spread_lower_bound_positive"] is None
