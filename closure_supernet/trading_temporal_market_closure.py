from __future__ import annotations

"""Single-market temporal trading closure derived from verified source events.

The empirical arena is one market through time.  Quotes, market trades, orders,
and fills are returned source events.  They are not themselves completed trades.
The temporal closure is derived only after the ordered fill history returns the
relative base-inventory coordinate to a previously visited value.

For a chronological fill path q_0 -> q_1 -> ... -> q_n, a primitive returned
interval is the segment between consecutive visits to the same relative
inventory coordinate.  Longer returns are compositions of these primitive
returns.  This is the temporal analogue of simple-cycle decomposition, but time
order is part of the relation and cannot be permuted by a graph traversal.

For each primitive returned interval the normalized closure puts all realized
cost curvature on the return:

    K = sum(buy quote cash out) - sum(sell quote cash in) + returned fees
    Pi_nat = -K

If fee/cost evidence is incomplete, the geometric interval is still returned
but execution remains OPEN.  Spread and slippage are local diagnostics; actual
fill prices already carry their realized market impact and therefore are not
added a second time.
"""

import base64
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from typing import Any, Iterable, Mapping, Sequence

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .current_closure_relative_natural_form_atlas import derive_current_closure_relative_atlas
from .trading_natural_form_closure import resolve_open_sensor_trading_closure
from .trading_open_boundary_natural_selection import derive_open_boundary_natural_selection
from .trading_relative_hair_horizon_ball_size import derive_preaction_relative_coordinates
from .trading_source_return_truth import PUBLIC_KEYS_ENV
from .trading_translational_truth_partition import derive_translational_truth_partition
from .trading_unified_natural_form_field import derive_unified_natural_form_field


PROTOCOL = "closure.supernet/single-market-temporal-trading-closure-v1"
ALPACA_EVENT_PROTOCOL = "closure.supernet/alpaca-temporal-source-event-v2"


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()}"


def _decimal(value: Any, *, field: str) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a finite decimal") from exc
    if not result.is_finite():
        raise ValueError(f"{field} must be a finite decimal")
    return result


def _positive_decimal(value: Any, *, field: str) -> Decimal:
    result = _decimal(value, field=field)
    if result <= 0:
        raise ValueError(f"{field} must be positive")
    return result


def _text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _b64decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"), validate=True)


def _trusted_public_keys() -> dict[str, Ed25519PublicKey]:
    raw = os.environ.get(PUBLIC_KEYS_ENV, "").strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, Mapping):
        return {}
    result: dict[str, Ed25519PublicKey] = {}
    for authority, encoded in payload.items():
        try:
            result[str(authority)] = Ed25519PublicKey.from_public_bytes(
                _b64decode(str(encoded))
            )
        except Exception:
            continue
    return result


def _event_id(*, event_kind: str, source_event: Mapping[str, Any]) -> str:
    return _digest(
        "alpaca-source-event",
        {"event_kind": event_kind, "source_event": dict(source_event)},
    )


def verify_temporal_source_events(
    *,
    observer_id: str,
    source_events: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Verify signed raw event history before temporal closure derivation."""

    trusted = _trusted_public_keys()
    verified: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for raw in source_events:
        witness = dict(raw)
        body_raw = witness.get("body")
        body = dict(body_raw) if isinstance(body_raw, Mapping) else {}
        authority = str(body.get("authority_id") or witness.get("authority_id") or "")
        event_kind = str(body.get("event_kind") or "")
        source_event_raw = body.get("source_event")
        source_event = (
            dict(source_event_raw) if isinstance(source_event_raw, Mapping) else {}
        )
        source_event_id = str(body.get("source_event_id") or "")
        reason = "SOURCE_EVENT_VERIFIED"
        ok = True

        if witness.get("protocol") != ALPACA_EVENT_PROTOCOL:
            ok = False
            reason = "SOURCE_EVENT_PROTOCOL_MISMATCH"
        elif body.get("protocol") != ALPACA_EVENT_PROTOCOL:
            ok = False
            reason = "SOURCE_EVENT_BODY_PROTOCOL_MISMATCH"
        elif body.get("observer_id") != observer_id:
            ok = False
            reason = "SOURCE_EVENT_OBSERVER_MISMATCH"
        elif not authority or authority not in trusted:
            ok = False
            reason = "SOURCE_EVENT_AUTHORITY_UNTRUSTED"
        elif not event_kind or not source_event:
            ok = False
            reason = "SOURCE_EVENT_BODY_INCOMPLETE"
        elif source_event_id != _event_id(
            event_kind=event_kind,
            source_event=source_event,
        ):
            ok = False
            reason = "SOURCE_EVENT_ID_MISMATCH"
        elif (authority, source_event_id) in seen:
            ok = False
            reason = "SOURCE_EVENT_REPLAYED"
        else:
            try:
                trusted[authority].verify(
                    _b64decode(str(witness.get("signature") or "")),
                    _stable(body).encode("utf-8"),
                )
            except (ValueError, InvalidSignature, TypeError):
                ok = False
                reason = "SOURCE_EVENT_SIGNATURE_INVALID"

        if ok:
            seen.add((authority, source_event_id))
            verified.append(
                {
                    **body,
                    "source_event": source_event,
                    "source_event_verified": True,
                }
            )

        audit_rows.append(
            {
                "status": WITNESSED_STATUS if ok else OPEN_STATUS,
                "verified": ok,
                "reason": reason,
                "authority_id": authority or None,
                "source_event_id": source_event_id or None,
                "event_kind": event_kind or None,
            }
        )

    count = sum(1 for row in audit_rows if row["verified"])
    return verified, {
        "protocol": PROTOCOL,
        "status": (
            WITNESSED_STATUS
            if audit_rows and count == len(audit_rows)
            else OPEN_STATUS
        ),
        "input_event_count": len(audit_rows),
        "verified_event_count": count,
        "open_event_count": len(audit_rows) - count,
        "events": audit_rows,
        "source_event_signature": "ED25519",
        "source_event_replay_authors_history": False,
        "unsigned_event_authors_temporal_truth": False,
        "adapter_authors_temporal_closure": False,
    }


def _side(value: Any) -> str | None:
    text = str(value or "").lower().split(".")[-1]
    return text if text in {"buy", "sell"} else None


def _order_time(order: Mapping[str, Any]) -> datetime | None:
    for key in ("updated_at", "filled_at", "submitted_at", "created_at"):
        parsed = _timestamp(order.get(key))
        if parsed is not None:
            return parsed
    return None


def _fee_state(order: Mapping[str, Any], *, quote: str) -> tuple[Decimal | None, bool]:
    """Read only explicitly unit-qualified cumulative quote fees."""

    candidates = (
        ("fee_amount", "fee_currency"),
        ("commission", "commission_currency"),
        ("fees", "fees_currency"),
    )
    for amount_key, currency_key in candidates:
        if amount_key not in order or order.get(amount_key) is None:
            continue
        currency = str(order.get(currency_key) or "").upper()
        if currency != quote.upper():
            return None, False
        try:
            amount = _decimal(order.get(amount_key), field=amount_key)
        except ValueError:
            return None, False
        if amount < 0:
            return None, False
        return amount, True
    return None, False


def derive_fill_increments(
    *,
    symbol: str,
    verified_events: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Derive incremental fills from returned cumulative order/fill states."""

    base, quote = symbol.split("/", 1)
    normalized_symbol = symbol.replace("/", "").upper()
    fill_states: list[dict[str, Any]] = []
    for body in verified_events:
        if body.get("event_kind") != "FILL_STATE":
            continue
        event = dict(body.get("source_event") or {})
        event_symbol = str(event.get("symbol") or "").replace("/", "").upper()
        if event_symbol != normalized_symbol:
            continue
        when = _order_time(event)
        if when is None:
            continue
        fill_states.append(
            {
                "body": dict(body),
                "event": event,
                "when": when,
            }
        )

    fill_states.sort(
        key=lambda row: (
            row["when"],
            str(row["event"].get("id") or ""),
            str(row["body"].get("source_event_id") or ""),
        )
    )

    previous: dict[str, dict[str, Any]] = {}
    increments: list[dict[str, Any]] = []
    corrections: list[dict[str, Any]] = []

    for item in fill_states:
        order = item["event"]
        order_id = str(order.get("id") or "")
        side = _side(order.get("side"))
        if not order_id or side is None:
            continue
        try:
            qty = _positive_decimal(order.get("filled_qty"), field="filled_qty")
            avg_price = _positive_decimal(
                order.get("filled_avg_price"),
                field="filled_avg_price",
            )
        except ValueError:
            continue

        cumulative_notional = qty * avg_price
        cumulative_fee, fee_known = _fee_state(order, quote=quote)
        prior = previous.get(order_id)
        prior_qty = Decimal("0") if prior is None else prior["qty"]
        prior_notional = Decimal("0") if prior is None else prior["notional"]
        prior_fee = Decimal("0") if prior is None or prior["fee"] is None else prior["fee"]

        if qty < prior_qty:
            corrections.append(
                {
                    "order_id": order_id,
                    "reason": "RETURNED_FILLED_QUANTITY_DECREASED",
                    "previous_qty": _text(prior_qty),
                    "current_qty": _text(qty),
                    "status": OPEN_STATUS,
                }
            )
            previous[order_id] = {
                "qty": qty,
                "notional": cumulative_notional,
                "fee": cumulative_fee,
            }
            continue

        delta_qty = qty - prior_qty
        delta_notional = cumulative_notional - prior_notional
        if delta_qty <= 0:
            previous[order_id] = {
                "qty": qty,
                "notional": cumulative_notional,
                "fee": cumulative_fee,
            }
            continue
        if delta_notional <= 0:
            delta_notional = delta_qty * avg_price

        delta_fee: Decimal | None = None
        if fee_known and cumulative_fee is not None:
            delta_fee = cumulative_fee - prior_fee
            if delta_fee < 0:
                delta_fee = None
                fee_known = False

        increments.append(
            {
                "source_event_id": item["body"]["source_event_id"],
                "authority_id": item["body"]["authority_id"],
                "order_id": order_id,
                "symbol": symbol,
                "base": base,
                "quote": quote,
                "side": side,
                "timestamp": item["when"].isoformat(),
                "base_quantity": _text(delta_qty),
                "quote_notional": _text(delta_notional),
                "fill_price": _text(delta_notional / delta_qty),
                "fee_quote": _text(delta_fee),
                "fee_returned": bool(fee_known and delta_fee is not None),
                "authenticated": True,
                "cost_complete": bool(fee_known and delta_fee is not None),
            }
        )
        previous[order_id] = {
            "qty": qty,
            "notional": cumulative_notional,
            "fee": cumulative_fee,
        }

    return increments, {
        "status": WITNESSED_STATUS if increments else OPEN_STATUS,
        "fill_state_count": len(fill_states),
        "fill_increment_count": len(increments),
        "open_correction_count": len(corrections),
        "open_corrections": corrections,
        "incremental_fill_is_derived_from_returned_cumulative_state": True,
        "fifo_matching_used": False,
        "lifo_matching_used": False,
        "cost_basis_selector_present": False,
    }


def derive_quote_projections(
    *,
    symbol: str,
    verified_events: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for body in verified_events:
        if body.get("event_kind") != "CRYPTO_ORDERBOOK":
            continue
        event = dict(body.get("source_event") or {})
        if str(event.get("symbol") or "").upper() != symbol.upper():
            continue
        bids = event.get("bids") or []
        asks = event.get("asks") or []
        if not bids or not asks:
            continue
        try:
            bid = _positive_decimal(bids[0]["price"], field="best_bid")
            ask = _positive_decimal(asks[0]["price"], field="best_ask")
        except (KeyError, TypeError, ValueError):
            continue
        rows.append(
            {
                "kind": "CURRENT_SPREAD_FRICTION_PROJECTION",
                "status": WITNESSED_STATUS,
                "source_event_id": body["source_event_id"],
                "timestamp": event.get("timestamp"),
                "best_bid": _text(bid),
                "best_ask": _text(ask),
                "log_spread_curvature": _text(ask.ln() - bid.ln()),
                "instantaneous_spread_is_completed_trade": False,
                "authors_temporal_closure": False,
                "semantic_authority": False,
            }
        )
    rows.sort(key=lambda row: str(row.get("timestamp") or ""))
    return rows


def _latest_quote_before(
    *,
    quote_projections: Sequence[Mapping[str, Any]],
    timestamp: str,
) -> Mapping[str, Any] | None:
    target = _timestamp(timestamp)
    if target is None:
        return None
    candidate: Mapping[str, Any] | None = None
    candidate_time: datetime | None = None
    for row in quote_projections:
        when = _timestamp(row.get("timestamp"))
        if when is None or when > target:
            continue
        if candidate_time is None or when >= candidate_time:
            candidate = row
            candidate_time = when
    return candidate


def attach_fill_diagnostics(
    *,
    increments: Sequence[Mapping[str, Any]],
    quote_projections: Sequence[Mapping[str, Any]],
    verified_events: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    order_events: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for body in verified_events:
        if body.get("event_kind") not in {"ORDER_STATE", "FILL_STATE"}:
            continue
        event = body.get("source_event")
        if isinstance(event, Mapping) and event.get("id") is not None:
            order_events[str(event["id"])].append(event)

    rows: list[dict[str, Any]] = []
    for raw in increments:
        row = dict(raw)
        quote = _latest_quote_before(
            quote_projections=quote_projections,
            timestamp=str(row["timestamp"]),
        )
        fill_price = _positive_decimal(row["fill_price"], field="fill_price")
        qty = _positive_decimal(row["base_quantity"], field="base_quantity")
        slippage: Decimal | None = None
        reference: Decimal | None = None
        if quote is not None:
            if row["side"] == "buy":
                reference = _positive_decimal(quote["best_ask"], field="best_ask")
                slippage = (fill_price - reference) * qty
            else:
                reference = _positive_decimal(quote["best_bid"], field="best_bid")
                slippage = (reference - fill_price) * qty

        latency: Decimal | None = None
        states = order_events.get(str(row["order_id"]), [])
        submitted_times = [
            parsed
            for state in states
            if (parsed := _timestamp(state.get("submitted_at"))) is not None
        ]
        fill_time = _timestamp(row["timestamp"])
        if submitted_times and fill_time is not None:
            latency = Decimal(str((fill_time - min(submitted_times)).total_seconds()))

        row.update(
            {
                "reference_quote_source_event_id": (
                    quote.get("source_event_id") if quote is not None else None
                ),
                "reference_touch_price": _text(reference),
                "realized_slippage_quote": _text(slippage),
                "execution_latency_seconds": _text(latency),
                "slippage_is_diagnostic_not_double_counted": True,
                "fill_price_already_contains_realized_spread_and_slippage": True,
            }
        )
        rows.append(row)
    return rows


def derive_primitive_temporal_returns(
    *,
    symbol: str,
    fill_increments: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Find primitive chronological returns of the relative inventory state."""

    base, quote = symbol.split("/", 1)
    inventory = Decimal("0")
    last_visit: dict[Decimal, int] = {Decimal("0"): 0}
    legs: list[dict[str, Any]] = []
    closures: list[dict[str, Any]] = []

    for raw in fill_increments:
        fill = dict(raw)
        qty = _positive_decimal(fill["base_quantity"], field="base_quantity")
        notional = _positive_decimal(fill["quote_notional"], field="quote_notional")
        fee = (
            _decimal(fill["fee_quote"], field="fee_quote")
            if fill.get("fee_quote") is not None
            else None
        )
        before = inventory
        if fill["side"] == "buy":
            after = before + qty
            known_cost = notional + (fee or Decimal("0"))
            gross_cost = notional
        else:
            after = before - qty
            known_cost = -notional + (fee or Decimal("0"))
            gross_cost = -notional

        leg = {
            **fill,
            "inventory_before": _text(before),
            "inventory_after": _text(after),
            "known_cost_curvature_quote": _text(known_cost),
            "gross_cost_curvature_quote": _text(gross_cost),
        }
        legs.append(leg)
        inventory = after
        boundary_index = len(legs)

        if after in last_visit:
            start_index = last_visit[after]
            interval = legs[start_index:boundary_index]
            if interval:
                closure_event_ids = [str(item["source_event_id"]) for item in interval]
                K_known = sum(
                    (_decimal(item["known_cost_curvature_quote"], field="known_cost") for item in interval),
                    Decimal("0"),
                )
                K_gross = sum(
                    (_decimal(item["gross_cost_curvature_quote"], field="gross_cost") for item in interval),
                    Decimal("0"),
                )
                cost_complete = all(item.get("cost_complete") is True for item in interval)
                fee_total = (
                    sum(
                        (_decimal(item["fee_quote"], field="fee_quote") for item in interval),
                        Decimal("0"),
                    )
                    if cost_complete
                    else None
                )
                buys = [item for item in interval if item["side"] == "buy"]
                sells = [item for item in interval if item["side"] == "sell"]
                buy_qty = sum(
                    (_decimal(item["base_quantity"], field="base_quantity") for item in buys),
                    Decimal("0"),
                )
                sell_qty = sum(
                    (_decimal(item["base_quantity"], field="base_quantity") for item in sells),
                    Decimal("0"),
                )
                buy_notional = sum(
                    (_decimal(item["quote_notional"], field="quote_notional") for item in buys),
                    Decimal("0"),
                )
                sell_notional = sum(
                    (_decimal(item["quote_notional"], field="quote_notional") for item in sells),
                    Decimal("0"),
                )
                closed_base = min(buy_qty, sell_qty)
                ball_quote = min(buy_notional, sell_notional)
                closure_id = _digest(
                    "temporal-inventory-return",
                    {
                        "symbol": symbol,
                        "source_event_ids": closure_event_ids,
                        "baseline_inventory": _text(after),
                    },
                )
                baseline_token = f"TEMPORAL:{symbol}:RELATIVE_INVENTORY_BASELINE"
                interior_token = f"TEMPORAL:{symbol}:RETURN_INTERIOR"
                start_time = str(interval[0].get("timestamp") or "") or None
                end_time = str(interval[-1].get("timestamp") or "") or None
                frame = [
                    {
                        "id": f"{closure_id}:open",
                        "source": baseline_token,
                        "target": interior_token,
                        "value": "0",
                        "hair_delta": "0",
                        "source_ids": closure_event_ids,
                        "returned": True,
                        "authenticated": True,
                        "cost_complete": cost_complete,
                        "relative_size": _text(ball_quote),
                        "relative_size_unit": f"{quote}-notional",
                        "timestamp": start_time,
                    },
                    {
                        "id": f"{closure_id}:return",
                        "source": interior_token,
                        "target": baseline_token,
                        "value": _text(K_known),
                        "hair_delta": "0",
                        "source_ids": closure_event_ids,
                        "returned": True,
                        "authenticated": True,
                        "cost_complete": cost_complete,
                        "relative_size": _text(ball_quote),
                        "relative_size_unit": f"{quote}-notional",
                        "timestamp": end_time,
                    },
                ]
                closures.append(
                    {
                        "temporal_closure_id": closure_id,
                        "symbol": symbol,
                        "base": base,
                        "quote": quote,
                        "baseline_inventory": _text(after),
                        "path_fill_count": len(interval),
                        "source_event_ids": closure_event_ids,
                        "opened_at": start_time,
                        "returned_at": end_time,
                        "gross_curvature_quote": _text(K_gross),
                        "gross_profit_quote": _text(-K_gross),
                        "known_cost_curvature_quote": _text(K_known),
                        "known_cost_profit_quote": _text(-K_known),
                        "fee_quote": _text(fee_total),
                        "cost_complete": cost_complete,
                        "net_profit_status": WITNESSED_STATUS if cost_complete else OPEN_STATUS,
                        "net_profit_quote": _text(-K_known) if cost_complete else None,
                        "closed_base_quantity": _text(closed_base),
                        "relative_ball_size_quote": _text(ball_quote),
                        "relative_ball_size_unit": f"{quote}-notional",
                        "inventory_return_exact": True,
                        "temporal_order_preserved": True,
                        "first_return_rule_used": False,
                        "next_bid_rule_used": False,
                        "fifo_matching_used": False,
                        "adapter_selected_exit": False,
                        "frame": frame,
                        "path": [dict(item) for item in interval],
                    }
                )

        last_visit[after] = boundary_index

    return closures, {
        "status": WITNESSED_STATUS if closures else OPEN_STATUS,
        "primitive_temporal_return_count": len(closures),
        "fill_increment_count": len(legs),
        "current_relative_inventory": _text(inventory),
        "current_inventory_status": (
            WITNESSED_STATUS if inventory == 0 else OPEN_STATUS
        ),
        "temporal_closure_is_inventory_state_return": True,
        "primitive_return_is_consecutive_visit_to_same_inventory_state": True,
        "longer_returns_are_compositions": True,
        "temporal_order_is_semantic": True,
        "graph_permutation_authors_temporal_closure": False,
        "fifo_matching_used": False,
        "adapter_authors_closure": False,
    }


def _atlas_boundary_adapter(relative_atlas: Mapping[str, Any]) -> dict[str, Any]:
    forms: list[dict[str, Any]] = []
    for index, raw in enumerate(relative_atlas.get("action_projections", [])):
        action = dict(raw)
        if action.get("status") != OPEN_STATUS or action.get("requires_return") is not True:
            continue
        family_id = action.get("family_id")
        kind = (
            f"OPEN_ATLAS_FAMILY_TRANSLATION:{family_id}"
            if action.get("kind") == "RETURN_SOURCE_PRESERVING_ATLAS_TRANSLATION"
            else f"OPEN_CURRENT_RELATIVE_ATLAS_FORM:{action.get('kind')}:{index}"
        )
        forms.append(
            {
                "form_id": action.get("projection_id")
                or action.get("boundary_id")
                or f"atlas-open-{index}",
                "kind": kind,
                "status": OPEN_STATUS,
                "closure_id": action.get("closure_id") or action.get("current_tt_id"),
                "source_token": action.get("source_token"),
                "target_token": action.get("target_token"),
                "family_id": family_id,
                "action_projection": action,
            }
        )
    return {"open_natural_forms": forms}


def resolve_single_market_temporal_closure(
    *,
    observer_id: str,
    symbol: str,
    source_events: Sequence[Mapping[str, Any]],
    max_returns: int | None = None,
) -> dict[str, Any]:
    """Resolve the current full atlas from one verified temporal market history."""

    verified_events, source_audit = verify_temporal_source_events(
        observer_id=observer_id,
        source_events=source_events,
    )
    quote_projections = derive_quote_projections(
        symbol=symbol,
        verified_events=verified_events,
    )
    increments, fill_audit = derive_fill_increments(
        symbol=symbol,
        verified_events=verified_events,
    )
    increments = attach_fill_diagnostics(
        increments=increments,
        quote_projections=quote_projections,
        verified_events=verified_events,
    )
    closures, temporal_audit = derive_primitive_temporal_returns(
        symbol=symbol,
        fill_increments=increments,
    )
    history = [list(item["frame"]) for item in closures]
    current_feedback = list(history[-1]) if history else []

    natural = resolve_open_sensor_trading_closure(
        observer_id=observer_id,
        sensor_feedback=current_feedback,
        max_returns=max_returns,
    )
    truth_partition = (
        derive_translational_truth_partition(
            observer_id=observer_id,
            sensor_history=history,
            max_returns_per_frame=max_returns,
        )
        if history
        else None
    )
    coordinates = derive_preaction_relative_coordinates(
        observer_id=observer_id,
        natural_closure=natural,
        current_feedback=current_feedback,
        sensor_history=history,
        max_returns=max_returns,
    )
    trading_projection = derive_unified_natural_form_field(
        natural_closure=natural,
        preaction_coordinates=coordinates.get("by_closure_id", {}),
    )
    relative_atlas = derive_current_closure_relative_atlas(
        observer_id=observer_id,
        natural_closure=natural,
        preaction_coordinates=coordinates.get("by_closure_id", {}),
        trading_projection_field=trading_projection,
        additional_translation_sources=(),
    )
    open_boundary_selection = derive_open_boundary_natural_selection(
        natural_form_field=_atlas_boundary_adapter(relative_atlas),
        preaction_relative_coordinates=coordinates,
        translational_truth_partition=truth_partition,
    )

    relative_atlas["returned_natural_forms"] = list(
        trading_projection.get("returned_natural_forms", [])
    )
    relative_atlas["returned_natural_form_count"] = trading_projection.get(
        "returned_natural_form_count", 0
    )
    relative_atlas["profitable_returned_natural_forms"] = list(
        trading_projection.get("profitable_returned_natural_forms", [])
    )
    relative_atlas["open_boundary_natural_selection"] = open_boundary_selection
    relative_atlas["learning_interactions"] = list(
        open_boundary_selection.get("boundary_interactions", [])
    )
    relative_atlas["source_truth_audit"] = source_audit

    current_temporal = closures[-1] if closures else None
    current_net_profit = bool(
        current_temporal
        and current_temporal.get("cost_complete") is True
        and _decimal(
            current_temporal.get("net_profit_quote"),
            field="net_profit_quote",
        )
        > 0
    )
    current_geometric_profit = any(
        form.get("orientation") == "PROFITABLE"
        for form in natural.get("natural_forms", [])
    )

    body = dict(natural)
    body.update(
        {
            "protocol": PROTOCOL,
            "observer_id": observer_id,
            "symbol": symbol,
            "source_truth_audit": source_audit,
            "fill_derivation_audit": fill_audit,
            "temporal_closure_audit": temporal_audit,
            "quote_projections": quote_projections,
            "fill_increments": increments,
            "temporal_closures": [
                {k: v for k, v in closure.items() if k != "frame"}
                for closure in closures
            ],
            "temporal_closure_count": len(closures),
            "current_temporal_closure": (
                {k: v for k, v in current_temporal.items() if k != "frame"}
                if current_temporal
                else None
            ),
            "translational_truth_partition": truth_partition,
            "translational_truth_learning": truth_partition,
            "preaction_relative_coordinates": coordinates,
            "current_closure_relative_atlas": relative_atlas,
            "natural_form_field": relative_atlas,
            "natural_form_selection": relative_atlas,
            "trading_projection_field": trading_projection,
            "open_boundary_natural_selection": open_boundary_selection,
            "selected_interactions": list(relative_atlas.get("action_projections", [])),
            "learning_interactions": list(
                open_boundary_selection.get("boundary_interactions", [])
            ),
            "current_profit_truth_witnessed": current_geometric_profit,
            "current_net_profit_truth_witnessed": current_net_profit,
            "learned_profit": (
                truth_partition.get("learned_profit") is True
                if truth_partition is not None
                else current_geometric_profit
            ),
            "empirical_arena_is_one_market_through_time": True,
            "quotes_are_local_friction_projections": True,
            "instantaneous_ask_bid_cycle_authors_trade": False,
            "successor_bid_authors_exit": False,
            "multi_asset_cycle_required": False,
            "temporal_order_authors_relation": True,
            "adapter_authors_temporal_closure": False,
            "closure_derives_inventory_return": True,
            "relative_hair_horizon_from_returned_history": True,
            "relative_ball_size_from_returned_execution": True,
            "fees_must_return_for_net_profit": True,
            "slippage_is_realized_in_fill_price": True,
            "latency_is_returned_provenance_not_fixed_horizon": True,
            "automatic_order_submission": False,
        }
    )
    body["id"] = _digest(
        "single-market-temporal-trading-closure",
        {
            "observer_id": observer_id,
            "symbol": symbol,
            "source_event_ids": [
                row.get("source_event_id") for row in verified_events
            ],
            "current_closure_id": (
                natural.get("natural_forms", [{}])[0].get("closure_id")
                if natural.get("natural_forms")
                else None
            ),
        },
    )
    return body


__all__ = [
    "ALPACA_EVENT_PROTOCOL",
    "PROTOCOL",
    "attach_fill_diagnostics",
    "derive_fill_increments",
    "derive_primitive_temporal_returns",
    "derive_quote_projections",
    "resolve_single_market_temporal_closure",
    "verify_temporal_source_events",
]
