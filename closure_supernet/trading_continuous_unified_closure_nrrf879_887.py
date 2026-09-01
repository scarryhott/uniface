from __future__ import annotations

"""Continuous unified trading closure for NRRF879–887.

Observation, market interaction, AI diffusion, order/fill return and action are
translation-equal readings of one continuously reclosed state.  This module
therefore has no semantic ENVIRONMENT -> TRADE pipeline and no accumulating
OPEN queue.  Every returned interaction is folded immediately into the same
current closure state:

    Q_(t+1) = Close(Q_t ⊕ R_(t+1))

OPEN is only the unresolved boundary of Q_(t+1).  It never becomes a second
history, selector, or gate.  Completed inventory-return trades remain one
projection of this current, not the point at which truth begins.

Realized net profit is another projection of that same state.  Observation may
change Q without changing realized P&L; realized P&L changes exactly when a new
cost-complete temporal inventory-return closure appears:

    Pi_real(Q_(t+1)) = Pi_real(Q_t)
                       + sum(Pi_nat(tau) for tau in NewClosed(Q_(t+1))).

Returned natural forms are readings of Q as well. Translation-family, AI,
action and profit objects are derived relative readings of the same current;
they do not create another stage or another closure revision.  When NRRF887
closure-number diffusion is witnessed, the action coordinate is the unique
relative slide

    Delta_i = (P_t q_t)_i - q_(t,i),

with horizon and size inherited only when they are family-invariant returned
coordinates of that same natural form.  Profit/forecast/novelty do not author
this action field.

This Python layer is a runtime correspondence; it does not execute or re-prove
Lean.
"""

from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .trading_action_as_translational_truth_nrrf886_887 import derive_translational_truth_action_field
from .trading_ai_diffusion_nrrf887 import derive_nrrf887_diffusion
from .trading_returned_family_kernel_nrrf887_attempt import derive_returned_family_kernel
from .trading_translation_family_nrrf884_886 import derive_translation_families

PROTOCOL = "closure.supernet/trading-continuous-unified-closure-nrrf879-887-v4-translational-action"


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


def _text(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _returned_readings(trading: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in trading.get("source_events", []):
        row = dict(raw)
        if row.get("source_event_verified") is True or row.get("returned") is True:
            rows.append({"kind": row.get("event_kind") or "SOURCE_RETURN", "reading": row})
    for raw in trading.get("quote_projections", []):
        rows.append({"kind": "QUOTE_OBSERVATION", "reading": dict(raw)})
    for raw in trading.get("market_trade_projections", []):
        rows.append({"kind": "MARKET_TRADE_OBSERVATION", "reading": dict(raw)})
    for raw in trading.get("fill_increments", []):
        rows.append({"kind": "FILL_RETURN", "reading": dict(raw)})
    for raw in trading.get("temporal_closures", []):
        rows.append({"kind": "TEMPORAL_TRADE_CLOSURE", "reading": dict(raw)})
    field = dict(trading.get("trading_projection_field") or {})
    for raw in field.get("returned_natural_forms", []):
        row = dict(raw)
        if row.get("returned_truth_member") is True:
            rows.append({"kind": "NATURAL_FORM_RETURN", "reading": row})
    return rows


def _reading_key(row: Mapping[str, Any]) -> str:
    kind = str(row.get("kind") or "RETURN")
    reading = dict(row.get("reading") or {})
    for key in (
        "source_event_id",
        "temporal_closure_id",
        "closure_id",
        "form_id",
        "order_id",
        "trade_id",
        "id",
    ):
        value = reading.get(key)
        if value is not None:
            return f"{kind}:{key}:{value}"
    return _digest("continuous-returned-reading", {"kind": kind, "reading": reading})


def _dedupe_new_readings(
    *,
    prior_readings: Sequence[Mapping[str, Any]],
    current_readings: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    all_rows = [dict(row) for row in prior_readings]
    seen = {_reading_key(row) for row in all_rows}
    new_rows: list[dict[str, Any]] = []
    for raw in current_readings:
        row = dict(raw)
        key = _reading_key(row)
        if key in seen:
            continue
        seen.add(key)
        new_rows.append(row)
        all_rows.append(row)
    return all_rows, new_rows


def _temporal_closure_id(row: Mapping[str, Any]) -> str:
    for key in ("temporal_closure_id", "closure_id", "id"):
        value = row.get(key)
        if value is not None:
            return str(value)
    return _digest(
        "temporal-closure-projection",
        {
            "source_event_ids": list(row.get("source_event_ids", [])),
            "opened_at": row.get("opened_at"),
            "returned_at": row.get("returned_at"),
        },
    )


def _realized_profit_projection(
    *,
    trading: Mapping[str, Any],
    prior: Mapping[str, Any],
) -> dict[str, Any]:
    prior_projection = dict(prior.get("realized_profit_projection") or {})
    prior_total = _decimal(prior_projection.get("realized_net_profit_quote")) or Decimal("0")
    realized_ids = {str(x) for x in prior_projection.get("realized_temporal_closure_ids", [])}
    seen_ids = {str(x) for x in prior_projection.get("seen_temporal_closure_ids", [])}
    unresolved_ids = {str(x) for x in prior_projection.get("open_net_profit_temporal_closure_ids", [])}

    delta = Decimal("0")
    newly_realized: list[str] = []
    current_closures = [dict(row) for row in trading.get("temporal_closures", [])]

    for closure in current_closures:
        closure_id = _temporal_closure_id(closure)
        seen_ids.add(closure_id)
        net = _decimal(closure.get("net_profit_quote"))
        net_witnessed = bool(
            closure.get("cost_complete") is True
            and closure.get("net_profit_status") == WITNESSED_STATUS
            and net is not None
        )
        if net_witnessed:
            unresolved_ids.discard(closure_id)
            if closure_id not in realized_ids:
                realized_ids.add(closure_id)
                newly_realized.append(closure_id)
                delta += net
        elif closure_id not in realized_ids:
            unresolved_ids.add(closure_id)

    total = prior_total + delta
    return {
        "status": OPEN_STATUS if unresolved_ids else WITNESSED_STATUS,
        "realized_net_profit_quote": _text(total),
        "new_realized_profit_delta_quote": _text(delta),
        "newly_realized_temporal_closure_ids": newly_realized,
        "realized_temporal_closure_ids": sorted(realized_ids),
        "seen_temporal_closure_ids": sorted(seen_ids),
        "open_net_profit_temporal_closure_ids": sorted(unresolved_ids),
        "completed_trade_projection_count": len(seen_ids),
        "realized_profit_projection_count": len(realized_ids),
        "recurrence": "Pi_real(Q_(t+1))=Pi_real(Q_t)+sum(Pi_nat(tau), tau in NewClosed(Q_(t+1)))",
        "profit_is_projection_of_same_continuous_closure": True,
        "observation_can_change_current_closure_without_changing_realized_profit": True,
        "realized_profit_changes_only_on_new_cost_complete_temporal_closure": True,
        "incomplete_fee_evidence_leaves_only_that_profit_projection_open": True,
        "unrealized_profit_authors_truth": False,
        "expected_profit_authors_truth": False,
    }


def derive_continuous_unified_closure(
    *,
    trading_receipt: Mapping[str, Any],
    prior_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    trading = dict(trading_receipt)
    prior = dict(prior_state or {})
    field = dict(trading.get("trading_projection_field") or {})

    families = derive_translation_families(
        natural_form_field=field,
        translational_truth_partition=trading.get("translational_truth_partition"),
    )
    kernel = derive_returned_family_kernel(
        translation_family_receipt=families,
        natural_form_field=field,
    )
    returned_kernel = trading.get("returned_diffusion_kernel") or kernel.get("returned_diffusion_kernel")
    diffusion = derive_nrrf887_diffusion(
        translation_family_receipt=families,
        returned_diffusion_kernel=returned_kernel,
    )
    translational_action = derive_translational_truth_action_field(
        translation_family_receipt=families,
        diffusion_receipt=diffusion,
    )

    receipt_readings = _returned_readings(trading)
    previous_readings = list(prior.get("returned_readings", []))
    all_readings, current_readings = _dedupe_new_readings(
        prior_readings=previous_readings,
        current_readings=receipt_readings,
    )
    profit_projection = _realized_profit_projection(trading=trading, prior=prior)

    derived_readings: list[dict[str, Any]] = []
    if families.get("family_count", 0):
        derived_readings.append({
            "kind": "TRANSLATION_FAMILY_FIELD",
            "reading": families,
            "authors_new_truth": False,
        })
    if diffusion.get("status") == WITNESSED_STATUS:
        derived_readings.append({
            "kind": "AI_DIFFUSION_PQ",
            "reading": diffusion,
            "authors_new_truth": False,
        })
    if translational_action.get("action_count", 0):
        derived_readings.append({
            "kind": "TRANSLATIONAL_TRUTH_ACTION_FIELD",
            "reading": translational_action,
            "authors_new_truth": False,
        })
    derived_readings.append({
        "kind": "REALIZED_PROFIT_PROJECTION",
        "reading": profit_projection,
        "authors_new_truth": False,
    })

    # One current boundary only. Reasons are recomputed from present unresolved
    # relations; stale reason strings are never accumulated as semantic objects.
    boundary: list[str] = []
    if not all_readings:
        boundary.append("NO_RETURNED_INTERACTION_YET")
    if families.get("unresolved_member_count", 0):
        boundary.append("UNRESOLVED_TRANSLATION_FAMILY")
    if families.get("family_count", 0) and diffusion.get("unresolved_coordinate_family_ids"):
        boundary.append("AUTHORITATIVE_CLOSURE_NUMBER_Q_OPEN")
    if families.get("family_count", 0) and kernel.get("status") != WITNESSED_STATUS and not trading.get("returned_diffusion_kernel"):
        boundary.append("RETURNED_RELATIVE_INTERACTION_KERNEL_P_OPEN")
    if translational_action.get("unresolved_family_ids"):
        boundary.append("TRANSLATIONAL_TRUTH_ACTION_COORDINATE_OPEN")
    if translational_action.get("action_count", 0) and not translational_action.get("market_side_bridge_complete"):
        boundary.append("CLOSURE_SLIDE_TO_CONCRETE_MARKET_SIDE_BRIDGE_OPEN")
    if profit_projection.get("open_net_profit_temporal_closure_ids"):
        boundary.append("RETURNED_NET_PROFIT_COST_EVIDENCE_OPEN")

    current_truth_witnessed = bool(all_readings)

    body = {
        "protocol": PROTOCOL,
        "equation": "Q_(t+1)=Close(Q_t⊕R_(t+1))",
        "action_equation": "Delta_i=(P_t q_t)_i-q_(t,i)",
        "profit_equation": "Pi_real(Q_(t+1))=Pi_real(Q_t)+sum(Pi_nat(NewClosed(Q_(t+1))))",
        "status": WITNESSED_STATUS if current_truth_witnessed else OPEN_STATUS,
        "current_revision": int(prior.get("current_revision", 0)) + len(current_readings),
        "returned_readings": all_readings,
        "new_returned_readings": current_readings,
        "new_returned_reading_count": len(current_readings),
        "derived_relative_readings": derived_readings,
        "current_relative_readings": [*all_readings, *derived_readings],
        "derived_readings_do_not_increment_revision": True,
        "observation_and_trading_are_translation_equal_readings": True,
        "natural_form_is_reading_of_same_current": True,
        "observation_is_not_presemantic_environment": True,
        "completed_trade_is_projection_not_truth_start": True,
        "quote_can_update_current_closure_without_realizing_pnl": True,
        "fill_can_update_current_closure_without_being_only_truth_source": True,
        "ai_diffusion_is_reading_of_same_current": True,
        "action_is_reading_of_same_current": True,
        "action_is_unique_relative_slide_not_prediction": True,
        "profit_is_reading_of_same_current": True,
        "translation_families": families,
        "returned_family_kernel": kernel,
        "ai_diffusion": diffusion,
        "translational_truth_action_field": translational_action,
        "realized_profit_projection": profit_projection,
        "completed_temporal_trade_count": profit_projection["completed_trade_projection_count"],
        "open_boundary": {
            "status": OPEN_STATUS if boundary else WITNESSED_STATUS,
            "unresolved_relations": boundary,
            "is_current_boundary_only": True,
            "accumulates_prior_open_failures": False,
            "authors_truth": False,
        },
        "open_count_is_progress_metric": False,
        "open_queue_present": False,
        "stage_gate_present": False,
        "separate_observation_pipeline_present": False,
        "only_returned_interaction_changes_current_closure": True,
        "automatic_order_submission": False,
    }
    body["id"] = _digest("continuous-unified-trading-closure", body)
    return body


__all__ = ["PROTOCOL", "derive_continuous_unified_closure"]
