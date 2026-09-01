from __future__ import annotations

"""Live interaction integration for continuous NRRF879–892 trading closure.

The remaining economic question is evaluated on the persistence interval that
comes from the interaction itself, never on an externally fixed hold:

    I_t = (H_TT, H_vision, G_vision, C_spread, Pi_returned).

``H_TT`` is not re-invented here.  It is the already-witnessed exact returned-
step relative-hair horizon carried by the translational action's natural form.
``H_vision`` is deliberately weaker and separately named: the number of causal
quote-return marks for which the NRRF892 BUY/SELL rendering has remained the
same.  It is useful for execution/turnover diagnostics but is not substituted
for exact translational-truth fidelity.

For a family whose previous rendered side is s in {-1,0,+1}, consecutive quote
marks m_t -> m_(t+1) contribute the causal shadow gross integral

    dG = s * 10^4 * (m_(t+1) / m_t - 1).

The observable spread supplies only a lower-bound friction projection.  Actual
profit remains the returned cost-complete temporal inventory closure already
computed by the continuous runtime; public spread never substitutes for fees,
slippage, or authenticated fills.

This module is diagnostic and empirical.  It never authors q, P, the action,
market side, horizon, size, or trading truth.
"""

from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/trading-live-interaction-integration-nrrf892-v1"


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
        return {
            "status": OPEN_STATUS,
            "quote_key": None,
            "mid": None,
            "half_spread_bps": None,
            "source_event_id": None,
            "timestamp": None,
        }
    bid = _decimal(quote.get("best_bid"))
    ask = _decimal(quote.get("best_ask"))
    if bid is None or ask is None or bid <= 0 or ask <= bid:
        return {
            "status": OPEN_STATUS,
            "quote_key": None,
            "mid": None,
            "half_spread_bps": None,
            "source_event_id": quote.get("source_event_id"),
            "timestamp": quote.get("timestamp"),
        }
    mid = (bid + ask) / Decimal("2")
    half_spread_bps = (ask - bid) / (Decimal("2") * mid) * Decimal("10000")
    source_id = quote.get("source_event_id")
    key = (
        f"source:{source_id}"
        if source_id is not None
        else _digest(
            "quote",
            {
                "timestamp": quote.get("timestamp"),
                "best_bid": str(bid),
                "best_ask": str(ask),
            },
        )
    )
    return {
        "status": WITNESSED_STATUS,
        "quote_key": key,
        "mid": _text(mid),
        "half_spread_bps": _text(half_spread_bps),
        "source_event_id": source_id,
        "timestamp": quote.get("timestamp"),
        "best_bid": _text(bid),
        "best_ask": _text(ask),
    }


def _side_sign(side: Any) -> int | None:
    text = str(side or "").upper()
    if text == "BUY":
        return 1
    if text == "SELL":
        return -1
    if text == "NOOP":
        return 0
    return None


def _action_by_family(current: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    field = dict(current.get("translational_truth_action_field") or {})
    return {
        str(row.get("family_id")): dict(row)
        for row in field.get("actions", [])
        if row.get("family_id")
    }


def _prior_by_truth(prior: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("truth_key")): dict(row)
        for row in prior.get("family_integrations", [])
        if row.get("truth_key")
    }


def _completed_runs(prior: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in prior.get("completed_vision_runs", [])]


def _run_margin(gross: Decimal, entry_half: Decimal, exit_half: Decimal) -> tuple[Decimal, Decimal]:
    spread = entry_half + exit_half
    return spread, gross - spread


def derive_live_interaction_integration(
    *,
    trading_receipt: Mapping[str, Any],
    continuous_current: Mapping[str, Any],
    nrrf892_rendering: Mapping[str, Any],
    prior_integration: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Integrate live slide persistence and price curvature without selecting trades."""

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
        side_sign = _side_sign(side)
        action = actions.get(family_id, {})
        formal_horizon = action.get("relative_hair_horizon_return_steps")
        formal_horizon_status = (
            WITNESSED_STATUS
            if action.get("status") == WITNESSED_STATUS and formal_horizon is not None
            else OPEN_STATUS
        )

        previous = prior_rows.get(truth_key, {})
        previous_side = previous.get("market_side")
        previous_sign = _side_sign(previous_side)
        previous_gross = _decimal(previous.get("vision_run_gross_bps")) or Decimal("0")
        previous_h = int(previous.get("vision_horizon_quote_returns") or 0)
        previous_entry_half = _decimal(previous.get("entry_half_spread_bps"))

        interval_gross = Decimal("0")
        if (
            new_quote
            and prior_mid is not None
            and mid is not None
            and prior_mid > 0
            and previous_sign not in (None, 0)
        ):
            interval_gross = Decimal(previous_sign) * (mid / prior_mid - Decimal("1")) * Decimal("10000")

        same_rendering = bool(previous and previous_side == side and previous_sign not in (None, 0))
        if same_rendering:
            run_gross = previous_gross + interval_gross
            vision_h = previous_h + (1 if new_quote else 0)
            entry_half = previous_entry_half if previous_entry_half is not None else half_spread
        else:
            if previous and previous_sign not in (None, 0) and prior_mid is not None and mid is not None:
                closed_gross = previous_gross + interval_gross
                if previous_entry_half is not None and half_spread is not None:
                    spread_cost, margin = _run_margin(closed_gross, previous_entry_half, half_spread)
                else:
                    spread_cost, margin = None, None
                completed.append({
                    "truth_key": truth_key,
                    "closure_truth_id": truth_id or None,
                    "prior_market_side": previous_side,
                    "ended_by_rendering_change": True,
                    "vision_horizon_quote_returns": previous_h + (1 if new_quote else 0),
                    "gross_interaction_bps": _text(closed_gross),
                    "spread_lower_bound_bps": _text(spread_cost),
                    "spread_lower_bound_margin_bps": _text(margin),
                    "exit_quote_key": quote_key,
                    "exit_mid": _text(mid),
                    "actual_realized_profit_claimed": False,
                })
            run_gross = Decimal("0")
            vision_h = 0 if side_sign in (None, 0) else 1
            entry_half = half_spread if side_sign not in (None, 0) else None

        if side_sign in (None, 0):
            vision_h = 0
            run_gross = Decimal("0")
            entry_half = None

        spread_lower = None
        spread_margin = None
        if side_sign not in (None, 0) and entry_half is not None and half_spread is not None:
            spread_lower, spread_margin = _run_margin(run_gross, entry_half, half_spread)

        integrations.append({
            "family_id": family_id,
            "closure_truth_id": truth_id or None,
            "truth_key": truth_key,
            "status": (
                WITNESSED_STATUS
                if rendering.get("status") == WITNESSED_STATUS and side_sign is not None
                else OPEN_STATUS
            ),
            "market_side": side,
            "formal_tt_horizon_status": formal_horizon_status,
            "formal_tt_horizon_return_steps": formal_horizon,
            "formal_tt_horizon_is_exact_relative_hair_fidelity": True,
            "vision_horizon_quote_returns": vision_h,
            "vision_horizon_is_weaker_chart_rendering_persistence": True,
            "vision_horizon_substitutes_for_formal_tt_horizon": False,
            "vision_run_gross_bps": _text(run_gross),
            "new_gross_interaction_bps": _text(interval_gross),
            "entry_half_spread_bps": _text(entry_half),
            "current_half_spread_bps": _text(half_spread),
            "spread_lower_bound_bps": _text(spread_lower),
            "spread_lower_bound_margin_bps": _text(spread_margin),
            "spread_lower_bound_positive": spread_margin > 0 if spread_margin is not None else None,
            "spread_is_complete_execution_cost": False,
            "public_mid_move_is_realized_profit": False,
            "profit_used_to_author_action": False,
            "fixed_holding_period_used": False,
            "future_return_used": False,
        })

    profit = dict(current.get("realized_profit_projection") or {})
    realized_status = profit.get("status") or OPEN_STATUS
    actual_delta = profit.get("new_realized_profit_delta_quote")

    body = {
        "protocol": PROTOCOL,
        "status": WITNESSED_STATUS if quote.get("status") == WITNESSED_STATUS and integrations else OPEN_STATUS,
        "equation": "I_t=(H_TT,H_vision,G_vision,C_spread,Pi_returned)",
        "live_profit_function": "Phi_vision=G_vision-C_spread_lower_bound; Pi_real is only returned cost-complete temporal closure",
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
            "status": realized_status,
            "new_realized_profit_delta_quote": actual_delta,
            "realized_net_profit_quote": profit.get("realized_net_profit_quote"),
            "open_net_profit_temporal_closure_ids": list(profit.get("open_net_profit_temporal_closure_ids", [])),
            "is_authoritative_returned_profit": True,
        },
        "spread_lower_bound_is_not_realized_profit": True,
        "formal_horizon_and_vision_horizon_are_kept_distinct": True,
        "repeated_poll_without_new_quote_does_not_extend_vision_horizon": True,
        "diagnostic_authors_action": False,
        "diagnostic_authors_truth": False,
        "automatic_order_submission": False,
    }
    body["id"] = _digest("trading-live-interaction-integration-nrrf892", body)
    return body


__all__ = ["PROTOCOL", "derive_live_interaction_integration"]
