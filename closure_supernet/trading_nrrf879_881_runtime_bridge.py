from __future__ import annotations

"""Runtime correspondence for the NRRF879–881 single-market trading stack.

This module is intentionally a projection/validation layer. It does not define
trading closure, translational truth, horizon, size, support learning, or action
admissibility. Those are read from ``trading_temporal_market_closure`` and the
existing current-relative atlas. The bridge only packages the already-derived
objects as the digital environment and UI/action surface described by NRRF881.
"""

from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/nrrf879-881-runtime-correspondence-v1"
FORMAL_MODULES = (
    "NRRF879SingleMarketTemporalTradingClosureDerivedFromTranslationalTruth",
    "NRRF880TemporalTradingTruthHorizonSupportActionAndTheAntiSmugglingTheorems",
    "NRRF881DigitalMarketEnvironmentAdversarialityAndTheUIDerivedFromTheClosureBall",
)
ACTION_KINDS = ("OBSERVE", "WAIT", "MARKET", "LIMIT", "CANCEL", "REPLACE", "NOOP")


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return result if result.is_finite() else None


def _latest(values: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    return dict(values[-1]) if values else None


def _book_market_state(trading: Mapping[str, Any]) -> dict[str, Any]:
    quotes = [dict(row) for row in trading.get("quote_projections", [])]
    return {
        "symbol": trading.get("symbol"),
        "latest_spread_projection": _latest(quotes),
        "quote_projection_count": len(quotes),
        "whole_book_source_preserved_upstream": True,
        "spread_authors_temporal_closure": False,
        "market_state_is_environment_not_truth": True,
    }


def _account_state(trading: Mapping[str, Any]) -> dict[str, Any]:
    temporal = dict(trading.get("temporal_closure_audit") or {})
    closures = [dict(row) for row in trading.get("temporal_closures", [])]
    return {
        "relative_base_inventory": temporal.get("current_relative_inventory"),
        "relative_inventory_status": temporal.get("current_inventory_status", OPEN_STATUS),
        "completed_temporal_return_count": len(closures),
        "free_reserved_resources_are_venue_account_state": True,
        "account_state_authors_truth": False,
        "inventory_return_is_derived_not_adapter_selected": True,
    }


def _action_schema() -> list[dict[str, Any]]:
    rows = []
    for kind in ACTION_KINDS:
        body: dict[str, Any] = {
            "kind": kind,
            "selectable_environment_operation": True,
            "semantic_authority": False,
            "authors_truth": False,
            "automatic_execution": False,
        }
        if kind == "MARKET": body["coordinates"] = ["side", "quantity"]
        if kind == "LIMIT": body["coordinates"] = ["side", "price", "quantity"]
        if kind == "CANCEL": body["coordinates"] = ["order_id"]
        if kind == "REPLACE": body["coordinates"] = ["order_id", "price?", "quantity?"]
        rows.append(body)
    return rows


def _selected_open_interactions(trading: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [{**dict(raw), "runtime_strategy_score": None, "expected_profit": None,
             "forecast": None, "runtime_tie_breaker": None,
             "bridge_authors_selection": False}
            for raw in trading.get("selected_interactions", [])]


def _closure_ball_ui(trading: Mapping[str, Any]) -> dict[str, Any]:
    current = trading.get("current_temporal_closure")
    current_map = dict(current) if isinstance(current, Mapping) else {}
    radius = _decimal(current_map.get("relative_ball_size_quote"))
    return {
        "semantic_plane": {"x_min": 0, "x_max": 1000, "y_min": 0, "y_max": 1000},
        "status": WITNESSED_STATUS if radius is not None and radius >= 0 else OPEN_STATUS,
        "closure_ball_radius": str(radius) if radius is not None else None,
        "closure_ball_unit": current_map.get("relative_ball_size_unit"),
        "radius_is_returned_bottleneck_capacity": radius is not None,
        "drag_is_hair": True,
        "wheel_is_local_global_scale": True,
        "drag_authors_truth": False,
        "wheel_authors_truth": False,
        "hit_testing_is_transport": True,
        "rendering_authors_truth": False,
    }


def _formal_correspondence(trading: Mapping[str, Any]) -> dict[str, Any]:
    temporal = dict(trading.get("temporal_closure_audit") or {})
    fill = dict(trading.get("fill_derivation_audit") or {})
    return {
        "formal_modules": list(FORMAL_MODULES),
        "lean_kernel_executed_by_runtime": False,
        "runtime_reproves_lean": False,
        "nrrf879": {
            "single_market": trading.get("empirical_arena_is_one_market_through_time") is True,
            "returned_event_order_semantic": trading.get("temporal_order_authors_relation") is True,
            "fill_increments_derived": fill.get("incremental_fill_is_derived_from_returned_cumulative_state") is True,
            "fifo_absent": fill.get("fifo_matching_used") is False,
            "lifo_absent": fill.get("lifo_matching_used") is False,
            "inventory_return_is_derived": trading.get("closure_derives_inventory_return") is True,
            "quote_not_trade": trading.get("instantaneous_ask_bid_cycle_authors_trade") is False,
            "fees_required_for_net": trading.get("fees_must_return_for_net_profit") is True,
            "temporal_closure_present": temporal.get("temporal_closure_is_inventory_state_return") is True,
        },
        "nrrf880": {
            "truth_partition_present": trading.get("translational_truth_partition") is not None,
            "hair_horizon_from_returned_history": trading.get("relative_hair_horizon_from_returned_history") is True,
            "ball_from_returned_execution": trading.get("relative_ball_size_from_returned_execution") is True,
            "open_boundary_present": trading.get("open_boundary_natural_selection") is not None,
            "selection_authors_truth": False,
            "action_authors_truth": False,
            "only_return_recloses": True,
        },
        "nrrf881": {
            "market_environment_is_separate": True,
            "selectable_action_space_present": True,
            "external_evolution_uncontrolled": True,
            "ui_radius_from_closure_ball": True,
            "drag_hair_truth_inert": True,
            "wheel_scale_truth_inert": True,
        },
        "atlas_carrier_present": bool(trading.get("current_closure_relative_atlas")),
    }


def validate_no_runtime_semantic_smuggling(trading: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    checks = (
        ("instantaneous_ask_bid_cycle_authors_trade", False, "instantaneous-ask-bid-cycle"),
        ("successor_bid_authors_exit", False, "successor-bid-exit"),
        ("multi_asset_cycle_required", False, "multi-asset-cycle"),
        ("adapter_authors_temporal_closure", False, "adapter-authors-closure"),
        ("automatic_order_submission", False, "automatic-order-submission"),
    )
    for key, expected, name in checks:
        if trading.get(key) is not expected: failures.append(name)
    fill = dict(trading.get("fill_derivation_audit") or {})
    if fill.get("fifo_matching_used") is not False: failures.append("fifo-selector")
    if fill.get("lifo_matching_used") is not False: failures.append("lifo-selector")
    if fill.get("cost_basis_selector_present") is not False: failures.append("cost-basis-selector")
    return {
        "status": WITNESSED_STATUS if not failures else OPEN_STATUS,
        "valid": not failures,
        "failures": sorted(set(failures)),
        "runtime_semantic_author_present": bool(failures),
        "formal_stack_is_authoritative": True,
    }


def derive_nrrf879_881_runtime_bridge(*, temporal_trading_receipt: Mapping[str, Any]) -> dict[str, Any]:
    trading = dict(temporal_trading_receipt)
    audit = validate_no_runtime_semantic_smuggling(trading)
    body = {
        "protocol": PROTOCOL,
        "status": trading.get("status", OPEN_STATUS),
        "symbol": trading.get("symbol"),
        "formal_correspondence": _formal_correspondence(trading),
        "market_state": _book_market_state(trading),
        "account_state": _account_state(trading),
        "selectable_action_space": _action_schema(),
        "current_natural_form_field": trading.get("natural_form_field"),
        "open_or_selected_interactions": _selected_open_interactions(trading),
        "closure_ball_ui": _closure_ball_ui(trading),
        "anti_smuggling_audit": audit,
        "environment_transition": {
            "form": "X_(t+1)=F(X_t,a_t,omega_t)",
            "external_evolution_is_environment_input": True,
            "agent_controls_external_evolution": False,
            "action_attempt_authors_truth": False,
            "verified_return_may_reclose": True,
        },
        "network": {"operations": ["GET_VIEW", "NAVIGATE", "RETURN"],
                    "append_only_store": True, "monotone_revision": True,
                    "network_transport_authors_truth": False},
        "automatic_order_submission": False,
        "bridge_defines_new_closure_law": False,
        "bridge_defines_new_selector": False,
        "bridge_defines_new_profit_model": False,
    }
    body["id"] = _digest("nrrf879-881-runtime-bridge", body)
    return body


__all__ = ["ACTION_KINDS", "FORMAL_MODULES", "PROTOCOL",
           "derive_nrrf879_881_runtime_bridge", "validate_no_runtime_semantic_smuggling"]
