from __future__ import annotations

"""Live interaction integration for continuous NRRF879–892 trading closure.

The economic diagnostic is a function of the exact current translational action,
not merely of its BUY/SELL rendering.  For family i define the live action truth

    Theta_(i,t) = (closure_truth_id_i, Delta_(i,t))

where Delta_i = (P q)_i - q_i.  A causal interaction episode persists exactly
while Theta is unchanged.  No fixed holding period or profit threshold is used.

The already-derived formal horizon H_TT remains the exact returned-step
relative-hair fidelity coordinate carried by the natural form.  Separately,
H_slide counts new causal quote returns inside the current exact-slide episode.
The observable price integral is

    dG = sign(Delta) * 10^4 * (m_(t+1) / m_t - 1),

and the public spread gives only the lower-bound friction projection

    C_spread = entry_half_spread + current_half_spread.

Thus the live shadow profitability function is

    Phi_slide = G_slide - C_spread,
    rho_slide = G_slide / C_spread  (when C_spread > 0).

Phi_slide and rho_slide never author q, P, action, side, horizon, size, or truth.
Authoritative profit remains the returned cost-complete temporal inventory
closure computed by the continuous runtime.
"""

from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any, Mapping

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/trading-live-interaction-integration-nrrf892-v2-exact-slide"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return result if result.is_finite() else None


def _text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _latest_quote(trading: Mapping[str, Any]) -> dict[str, Any] | None:
    rows: list[dict[str, Any]] = []
    for raw in trading.get("quote_projections", []):
        row = dict(raw)
        bid = _decimal(row.get("best_bid"))
        ask = _decimal(row.get("best_ask"))
        if bid is None or ask is None or bid <= 0 or ask <= bid:
            continue
        rows.append(row)
    if not rows:
        return None
    rows.sort(key=lambda row: str(row.get("timestamp") or ""))
    return rows[-1]


def _quote_coordinates(quote: Mapping[str, Any] | None) -> dict[str, Any]:
    if not quote:
        return {"status": OPEN_STATUS, "quote_key": None, "mid": None, "half_spread_bps": None,
                "source_event_id": None, "timestamp": None}
    bid = _decimal(quote.get("best_bid"))
    ask = _decimal(quote.get("best_ask"))
    if bid is None or ask is None or bid <= 0 or ask <= bid:
        return {"status": OPEN_STATUS, "quote_key": None, "mid": None, "half_spread_bps": None,
                "source_event_id": quote.get("source_event_id"), "timestamp": quote.get("timestamp")}
    mid = (bid + ask) / Decimal("2")
    half = (ask - bid) / (Decimal("2") * mid) * Decimal("10000")
    source_id = quote.get("source_event_id")
    key = f"source:{source_id}" if source_id is not None else _digest(
        "quote", {"timestamp": quote.get("timestamp"), "best_bid": str(bid), "best_ask": str(ask)}
    )
    return {"status": WITNESSED_STATUS, "quote_key": key, "mid": _text(mid),
            "half_spread_bps": _text(half), "source_event_id": source_id,
            "timestamp": quote.get("timestamp"), "best_bid": _text(bid), "best_ask": _text(ask)}


def _side_sign(side: Any) -> int | None:
    text = str(side or "").upper()
    return 1 if text == "BUY" else -1 if text == "SELL" else 0 if text == "NOOP" else None


def _action_by_family(current: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    field = dict(current.get("translational_truth_action_field") or {})
    return {str(row.get("family_id")): dict(row) for row in field.get("actions", []) if row.get("family_id")}


def _prior_by_truth(prior: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row.get("truth_key")): dict(row) for row in prior.get("family_integrations", []) if row.get("truth_key")}


def _completed_runs(prior: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in prior.get("completed_vision_runs", [])]


def _run_margin(gross: Decimal, entry_half: Decimal, exit_half: Decimal) -> tuple[Decimal, Decimal, Decimal | None]:
    spread = entry_half + exit_half
    margin = gross - spread
    ratio = gross / spread if spread > 0 else None
    return spread, margin, ratio


def _slide_key(truth_key: str, delta: Any) -> str | None:
    value = _decimal(delta)
    if value is None:
        return None
    return _digest("exact-slide-truth", {"truth_key": truth_key, "delta": _text(value)})


def _shadow_quote_margin(size: Any, unit: Any, margin_bps: Decimal | None) -> Decimal | None:
    amount = _decimal(size)
    text = str(unit or "").upper()
    if amount is None or amount < 0 or margin_bps is None or "NOTIONAL" not in text:
        return None
    return amount * margin_bps / Decimal("10000")


def derive_live_interaction_integration(
    *,
    trading_receipt: Mapping[str, Any],
    continuous_current: Mapping[str, Any],
    nrrf892_rendering: Mapping[str, Any],
    prior_integration: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Integrate exact-slide persistence and live curvature without selecting trades."""

    trading = dict(trading_receipt)
    current = dict(continuous_current)
    prior = dict(prior_integration or {})
    quote = _quote_coordinates(_latest_quote(trading))
    mid = _decimal(quote.get("mid"))
    half_spread = _decimal(quote.get("half_spread_bps"))
    quote_key = quote.get("quote_key")
    prior_quote_key = prior.get("last_quote_key")
    prior_mid = _decimal(prior.get("last_mid"))
    new_quote = bool(quote_key and quote_key != prior_quote_key)

    actions = _action_by_family(current)
    prior_rows = _prior_by_truth(prior)
    completed = _completed_runs(prior)
    integrations: list[dict[str, Any]] = []

    for raw in nrrf892_rendering.get("renderings", []):
        rendering = dict(raw)
        family_id = str(rendering.get("family_id") or "")
        truth_id = str(rendering.get("closure_truth_id") or "")
        truth_key = truth_id or family_id
        side = rendering.get("market_side")
        sign = _side_sign(side)
        action = actions.get(family_id, {})
        delta = action.get("unique_slide_amount", rendering.get("unique_slide_amount"))
        slide_truth_key = _slide_key(truth_key, delta)

        formal_h = action.get("relative_hair_horizon_return_steps")
        formal_h_status = WITNESSED_STATUS if action.get("status") == WITNESSED_STATUS and formal_h is not None else OPEN_STATUS
        size = action.get("relative_ball_size")
        size_unit = action.get("relative_ball_size_unit")

        previous = prior_rows.get(truth_key, {})
        previous_side = previous.get("market_side")
        previous_sign = _side_sign(previous_side)
        previous_slide_key = previous.get("slide_truth_key")
        previous_gross = _decimal(previous.get("exact_slide_run_gross_bps", previous.get("vision_run_gross_bps"))) or Decimal("0")
        previous_exact_h = int(previous.get("exact_slide_horizon_quote_returns") or 0)
        previous_side_h = int(previous.get("side_rendering_horizon_quote_returns", previous.get("vision_horizon_quote_returns")) or 0)
        previous_entry_half = _decimal(previous.get("entry_half_spread_bps"))

        interval_gross = Decimal("0")
        if new_quote and prior_mid is not None and mid is not None and prior_mid > 0 and previous_sign not in (None, 0):
            interval_gross = Decimal(previous_sign) * (mid / prior_mid - Decimal("1")) * Decimal("10000")

        same_side = bool(previous and previous_side == side and previous_sign not in (None, 0))
        same_exact_slide = bool(
            previous and slide_truth_key is not None and previous_slide_key == slide_truth_key and previous_sign not in (None, 0)
        )

        side_h = previous_side_h + (1 if new_quote else 0) if same_side else (1 if sign not in (None, 0) else 0)

        if same_exact_slide:
            run_gross = previous_gross + interval_gross
            exact_h = previous_exact_h + (1 if new_quote else 0)
            entry_half = previous_entry_half if previous_entry_half is not None else half_spread
        else:
            if previous and previous_sign not in (None, 0) and prior_mid is not None and mid is not None:
                closed_gross = previous_gross + interval_gross
                if previous_entry_half is not None and half_spread is not None:
                    spread_cost, margin, ratio = _run_margin(closed_gross, previous_entry_half, half_spread)
                else:
                    spread_cost, margin, ratio = None, None, None
                completed.append({
                    "truth_key": truth_key,
                    "closure_truth_id": truth_id or None,
                    "prior_market_side": previous_side,
                    "prior_slide_truth_key": previous_slide_key,
                    "ended_by_exact_slide_change": True,
                    "ended_by_side_change": previous_side != side,
                    "exact_slide_horizon_quote_returns": previous_exact_h + (1 if new_quote else 0),
                    "gross_interaction_bps": _text(closed_gross),
                    "spread_lower_bound_bps": _text(spread_cost),
                    "spread_lower_bound_margin_bps": _text(margin),
                    "spread_lower_bound_ratio": _text(ratio),
                    "exit_quote_key": quote_key,
                    "exit_mid": _text(mid),
                    "actual_realized_profit_claimed": False,
                })
            run_gross = Decimal("0")
            exact_h = 1 if sign not in (None, 0) and new_quote else 0
            entry_half = half_spread if sign not in (None, 0) else None

        if sign in (None, 0):
            exact_h = 0
            side_h = 0
            run_gross = Decimal("0")
            entry_half = None

        spread_lower = margin = ratio = None
        if sign not in (None, 0) and entry_half is not None and half_spread is not None:
            spread_lower, margin, ratio = _run_margin(run_gross, entry_half, half_spread)

        formal_reached = None
        if formal_h_status == WITNESSED_STATUS:
            try:
                formal_reached = exact_h >= int(formal_h)
            except (TypeError, ValueError):
                formal_reached = None

        shadow_quote = _shadow_quote_margin(size, size_unit, margin)
        integrations.append({
            "family_id": family_id,
            "closure_truth_id": truth_id or None,
            "truth_key": truth_key,
            "status": WITNESSED_STATUS if rendering.get("status") == WITNESSED_STATUS and sign is not None else OPEN_STATUS,
            "market_side": side,
            "unique_slide_amount": _text(_decimal(delta)),
            "slide_truth_key": slide_truth_key,
            "same_exact_slide_as_prior_return": same_exact_slide,
            "exact_slide_changed": bool(previous) and not same_exact_slide,
            "formal_tt_horizon_status": formal_h_status,
            "formal_tt_horizon_return_steps": formal_h,
            "formal_tt_horizon_is_exact_relative_hair_fidelity": True,
            "exact_slide_horizon_quote_returns": exact_h,
            "exact_slide_truth_persistence": True,
            "formal_horizon_reached_by_exact_slide_persistence": formal_reached,
            "side_rendering_horizon_quote_returns": side_h,
            "vision_horizon_quote_returns": side_h,
            "side_rendering_horizon_is_weaker_than_exact_slide_truth": True,
            "vision_horizon_substitutes_for_formal_tt_horizon": False,
            "exact_slide_run_gross_bps": _text(run_gross),
            "vision_run_gross_bps": _text(run_gross),
            "new_gross_interaction_bps": _text(interval_gross),
            "entry_half_spread_bps": _text(entry_half),
            "current_half_spread_bps": _text(half_spread),
            "spread_lower_bound_bps": _text(spread_lower),
            "spread_lower_bound_margin_bps": _text(margin),
            "spread_lower_bound_ratio": _text(ratio),
            "spread_lower_bound_positive": margin > 0 if margin is not None else None,
            "relative_ball_size": size,
            "relative_ball_size_unit": size_unit,
            "shadow_margin_at_relative_ball_quote": _text(shadow_quote),
            "spread_is_complete_execution_cost": False,
            "public_mid_move_is_realized_profit": False,
            "profit_used_to_author_action": False,
            "exact_slide_profit_function_authors_action": False,
            "fixed_holding_period_used": False,
            "future_return_used": False,
        })

    profit = dict(current.get("realized_profit_projection") or {})
    body = {
        "protocol": PROTOCOL,
        "status": WITNESSED_STATUS if quote.get("status") == WITNESSED_STATUS and integrations else OPEN_STATUS,
        "equation": "I_t=(Theta_t,H_TT,H_slide,G_slide,C_spread,rho_spread,Pi_returned)",
        "slide_truth_equation": "Theta_(i,t)=(closure_truth_id_i,Delta_(i,t))",
        "live_profit_function": "Phi_slide=G_slide-C_spread_lower_bound; rho_slide=G_slide/C_spread_lower_bound; Pi_real only returned cost-complete temporal closure",
        "quote": quote,
        "new_quote_return": new_quote,
        "family_integrations": integrations,
        "completed_vision_runs": completed[-200:],
        "completed_vision_run_count": int(prior.get("completed_vision_run_count", 0)) + max(0, len(completed) - len(_completed_runs(prior))),
        "last_quote_key": quote_key if quote_key is not None else prior_quote_key,
        "last_mid": _text(mid) if mid is not None else prior.get("last_mid"),
        "last_half_spread_bps": _text(half_spread) if half_spread is not None else prior.get("last_half_spread_bps"),
        "continuous_revision": current.get("current_revision"),
        "realized_profit": {
            "status": profit.get("status") or OPEN_STATUS,
            "new_realized_profit_delta_quote": profit.get("new_realized_profit_delta_quote"),
            "realized_net_profit_quote": profit.get("realized_net_profit_quote"),
            "open_net_profit_temporal_closure_ids": list(profit.get("open_net_profit_temporal_closure_ids", [])),
            "is_authoritative_returned_profit": True,
        },
        "exact_slide_truth_authors_interaction_integral": True,
        "side_only_persistence_authors_interaction_integral": False,
        "spread_lower_bound_is_not_realized_profit": True,
        "formal_horizon_and_exact_slide_horizon_are_kept_distinct": True,
        "repeated_poll_without_new_quote_does_not_extend_exact_slide_horizon": True,
        "diagnostic_authors_action": False,
        "diagnostic_authors_truth": False,
        "automatic_order_submission": False,
    }
    body["id"] = _digest("trading-live-interaction-integration-nrrf892", body)
    return body


__all__ = ["PROTOCOL", "derive_live_interaction_integration"]
