from __future__ import annotations

"""Closure equations for interactively translating runtime instantiations.

The module applies one law to reopening, rule charts, trading, resources and
legacy compatibility:

    proposal -> returned interaction -> re-closure -> WITNESSED or OPEN

A proposal, enum, horizon, score, queue order or finite limit can nominate work,
but it cannot author translational truth. Only a source-preserving returned
relation can enter the next closure state.
"""

from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

from .closure_continuity import (
    OPEN_STATUS,
    WITNESSED_STATUS,
    audit_translational_continuity,
    compatibility_reading_receipt,
    computation_boundary_open,
    finite_horn_closure,
    unique_strings,
)

PROTOCOL = "closure.supernet/interactive-translation-equations-v1"


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _decimal(value: Any, *, field: str) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a finite decimal") from exc
    if not result.is_finite():
        raise ValueError(f"{field} must be a finite decimal")
    return result


def _decimal_text(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _source_ids(value: Mapping[str, Any]) -> list[str]:
    raw = (
        value.get("source_return_ids")
        or value.get("source_ids")
        or value.get("exact_source_ids")
        or []
    )
    if isinstance(raw, str):
        raw = [raw]
    return unique_strings(raw)


def _bounded_prefix(
    values: Sequence[Any],
    *,
    boundary: str,
    limit: int | None,
) -> tuple[list[Any], list[Any], dict[str, Any] | None]:
    if limit is None:
        return list(values), [], None
    normalized = max(0, int(limit))
    selected = list(values[:normalized])
    remainder = list(values[normalized:])
    receipt = None
    if remainder:
        receipt = computation_boundary_open(
            boundary=boundary,
            configured_limit=normalized,
            observed=len(values),
        )
    return selected, remainder, receipt


def resolve_reopening_equation(
    *,
    assumption_ids: Iterable[str],
    returned_readings: Sequence[Mapping[str, Any]],
    rules: Sequence[Mapping[str, Any]] = (),
    max_readings: int | None = None,
    max_iterations: int | None = None,
) -> dict[str, Any]:
    """Derive reopening variants from returned readings, never from a mode enum.

    For every source-returned reading Hᵢ and its participant-relative rule chart
    R, compute Cᵢ = Close_R(Hᵢ). Relative unity is the intersection ∩ᵢ Cᵢ, but
    only when every reading in the supplied family has a source witness and its
    finite closure reaches a fixed point. Truncation leaves the family OPEN.
    """

    assumptions = unique_strings(assumption_ids)
    assumption_set = set(assumptions)
    unique_returns: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    for index, raw in enumerate(returned_readings):
        item = dict(raw)
        held = unique_strings(
            item.get("held_occurrence_ids")
            or item.get("held_ids")
            or item.get("members")
            or []
        )
        signature = tuple(sorted(held))
        if signature in seen:
            continue
        seen.add(signature)
        unique_returns.append(
            {
                "index": index,
                "return_id": str(item.get("return_id") or item.get("id") or ""),
                "held_occurrence_ids": held,
                "source_ids": _source_ids(item),
                "metadata": dict(item.get("metadata") or {}),
            }
        )

    selected, remainder, boundary = _bounded_prefix(
        unique_returns,
        boundary="REOPENING_RETURNED_READING_LIMIT",
        limit=max_readings,
    )
    readings: list[dict[str, Any]] = []
    closed_sets: list[set[str]] = []
    all_witnessed = bool(selected) and not remainder

    for item in selected:
        held = item["held_occurrence_ids"]
        unknown = sorted(set(held) - assumption_set)
        source_witnessed = bool(item["return_id"] or item["source_ids"])
        if unknown:
            closure_receipt = {
                "status": OPEN_STATUS,
                "members": held,
                "fixed_point_witnessed": False,
                "open_reason": "RETURNED_READING_OUTSIDE_ASSUMPTION_BALL",
            }
        else:
            closure_receipt = finite_horn_closure(
                held,
                rules,
                max_iterations=max_iterations,
            )
        witnessed = bool(
            source_witnessed
            and not unknown
            and closure_receipt.get("fixed_point_witnessed") is True
        )
        all_witnessed = all_witnessed and witnessed
        if witnessed:
            closed_sets.append(set(closure_receipt["members"]))
        readings.append(
            {
                **item,
                "status": WITNESSED_STATUS if witnessed else OPEN_STATUS,
                "source_return_witnessed": source_witnessed,
                "unknown_occurrence_ids": unknown,
                "closure_receipt": closure_receipt,
                "mode_authors_truth": False,
                "operation_enum": None,
            }
        )

    residue = (
        sorted(set.intersection(*closed_sets))
        if all_witnessed and closed_sets
        else None
    )
    status = WITNESSED_STATUS if residue is not None else OPEN_STATUS
    body = {
        "protocol": PROTOCOL,
        "equation": "C_i=Close_R(H_i); U=intersection_i(C_i)",
        "status": status,
        "assumption_ids": assumptions,
        "returned_readings": readings,
        "unprocessed_readings": remainder,
        "relative_unity_residue_ids": residue,
        "relative_unity_only": True,
        "mode_enum": None,
        "mode_is_semantic": False,
        "participant_rule_chart_is_universal_truth": False,
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
    }
    if boundary is not None:
        body["boundary_receipt"] = boundary
    body["id"] = _digest("reopening-equation", body)
    return body


def resolve_rule_chart_equation(
    *,
    charts: Sequence[Mapping[str, Any]],
    max_charts: int | None = None,
    max_iterations: int | None = None,
) -> dict[str, Any]:
    """Translate bespoke rule loops into relative closure classes.

    Two charts are in one relative unity exactly when their returned finite
    closures have the same member set. Labels and local rule syntax may differ;
    a chart without source-return provenance remains OPEN.
    """

    selected, remainder, boundary = _bounded_prefix(
        list(charts),
        boundary="RULE_CHART_TRANSLATION_LIMIT",
        limit=max_charts,
    )
    translated: list[dict[str, Any]] = []
    classes: dict[tuple[str, ...], list[str]] = {}

    for index, raw in enumerate(selected):
        chart = dict(raw)
        chart_id = str(chart.get("chart_id") or chart.get("id") or f"chart-{index}")
        receipt = finite_horn_closure(
            unique_strings(chart.get("seed") or chart.get("seed_ids") or []),
            list(chart.get("rules") or []),
            max_iterations=max_iterations,
        )
        source_ids = _source_ids(chart)
        witnessed = bool(
            source_ids and receipt.get("fixed_point_witnessed") is True
        )
        signature = tuple(receipt.get("members") or [])
        if witnessed:
            classes.setdefault(signature, []).append(chart_id)
        translated.append(
            {
                "chart_id": chart_id,
                "status": WITNESSED_STATUS if witnessed else OPEN_STATUS,
                "source_ids": source_ids,
                "closure_receipt": receipt,
                "syntax_label": chart.get("label"),
                "syntax_labels_define_equality": False,
                "rule_chart_is_universal_truth": False,
                "existence_closed": False,
                "continuation_status": OPEN_STATUS,
            }
        )

    class_rows = [
        {
            "id": _digest("rule-closure-class", list(signature)),
            "member_ids": list(signature),
            "chart_ids": sorted(chart_ids),
            "relative_unity": len(chart_ids) >= 1,
        }
        for signature, chart_ids in sorted(classes.items())
    ]
    status = (
        WITNESSED_STATUS
        if translated
        and not remainder
        and all(row["status"] == WITNESSED_STATUS for row in translated)
        else OPEN_STATUS
    )
    body = {
        "protocol": PROTOCOL,
        "equation": "Chart_p~Chart_q iff Close_Rp(A_p)=Close_Rq(A_q)",
        "status": status,
        "charts": translated,
        "relative_closure_classes": class_rows,
        "unprocessed_charts": [dict(item) for item in remainder],
        "fixed_rule_loop_authors_truth": False,
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
    }
    if boundary is not None:
        body["boundary_receipt"] = boundary
    body["id"] = _digest("rule-chart-equation", body)
    return body


def _form_identity(value: Mapping[str, Any]) -> tuple[str, str]:
    relation = value.get("relation")
    if relation is None:
        relation = value.get("route")
    if relation is None:
        relation = value.get("closure_relation")
    relation_signature = _stable(relation if relation is not None else {})
    form_id = str(value.get("form_id") or "") or _digest(
        "trading-form", relation_signature
    )
    return form_id, relation_signature


def resolve_trading_equation(
    *,
    proposals: Sequence[Mapping[str, Any]] = (),
    receipts: Sequence[Mapping[str, Any]] = (),
    minimum_receipts: int = 1,
    max_forms: int | None = None,
) -> dict[str, Any]:
    """Let authenticated completed routes instantiate the trading form.

    Quotes/proposals may nominate arbitrary relations, including arbitrary
    durations. They cannot update the gate. A form is witnessed only by an
    authenticated closed receipt with the same relation signature. The exact
    gate uses the observed profit floor; no fixed horizon or score is primitive.
    """

    minimum = max(1, int(minimum_receipts))
    forms: dict[str, dict[str, Any]] = {}
    proposal_rows: list[dict[str, Any]] = []

    for raw in proposals:
        proposal = dict(raw)
        form_id, signature = _form_identity(proposal)
        row = forms.setdefault(
            form_id,
            {
                "form_id": form_id,
                "relation_signature": signature,
                "relation": proposal.get("relation") or proposal.get("route") or {},
                "proposal_source_ids": [],
                "receipts": [],
            },
        )
        row["proposal_source_ids"] = unique_strings(
            [*row["proposal_source_ids"], *_source_ids(proposal)]
        )
        proposal_rows.append(
            {
                "form_id": form_id,
                "status": OPEN_STATUS,
                "source_ids": _source_ids(proposal),
                "estimated_profit": (
                    str(proposal.get("estimated_profit"))
                    if proposal.get("estimated_profit") is not None
                    else None
                ),
                "proposal_can_gate": False,
                "quote_authors_truth": False,
            }
        )

    unmatched_receipts: list[dict[str, Any]] = []
    for raw in receipts:
        receipt = dict(raw)
        form_id, signature = _form_identity(receipt)
        row = forms.setdefault(
            form_id,
            {
                "form_id": form_id,
                "relation_signature": signature,
                "relation": receipt.get("relation") or receipt.get("route") or {},
                "proposal_source_ids": [],
                "receipts": [],
            },
        )
        relation_matches = row["relation_signature"] == signature
        authenticated = receipt.get("authenticated") is True
        closed = receipt.get("closed_relation") is True or receipt.get("closed") is True
        source_ids = _source_ids(receipt)
        source_witnessed = bool(source_ids or receipt.get("receipt_id") or receipt.get("id"))
        try:
            realized = _decimal(receipt.get("realized_profit"), field="realized_profit")
            rate = _decimal(receipt.get("rate", 1), field="rate")
            rate_valid = rate > 0
            normalized = realized / rate if rate_valid else None
        except ValueError as exc:
            realized = None
            rate = None
            normalized = None
            rate_valid = False
            parse_error = str(exc)
        else:
            parse_error = None
        witnessed = bool(
            relation_matches
            and authenticated
            and closed
            and source_witnessed
            and realized is not None
            and rate_valid
        )
        normalized_row = {
            "receipt_id": str(receipt.get("receipt_id") or receipt.get("id") or ""),
            "source_ids": source_ids,
            "authenticated": authenticated,
            "closed_relation": closed,
            "relation_matches": relation_matches,
            "realized_profit": _decimal_text(realized),
            "rate": _decimal_text(rate),
            "base_energy_profit": _decimal_text(normalized),
            "rate_positive": rate_valid,
            "status": WITNESSED_STATUS if witnessed else OPEN_STATUS,
            "duration": receipt.get("duration"),
            "parse_error": parse_error,
        }
        if witnessed:
            row["receipts"].append(normalized_row)
        else:
            unmatched_receipts.append(normalized_row)

    ordered_forms = sorted(forms.values(), key=lambda item: item["form_id"])
    selected, remainder, boundary = _bounded_prefix(
        ordered_forms,
        boundary="TRADING_FORM_TRANSLATION_LIMIT",
        limit=max_forms,
    )
    form_rows: list[dict[str, Any]] = []
    for row in selected:
        profits = [
            _decimal(item["realized_profit"], field="realized_profit")
            for item in row["receipts"]
        ]
        base_profits = [
            _decimal(item["base_energy_profit"], field="base_energy_profit")
            for item in row["receipts"]
        ]
        profit_floor = min(profits) if profits else None
        base_floor = min(base_profits) if base_profits else None
        enough = len(profits) >= minimum
        gate_open = bool(enough and profit_floor is not None and profit_floor > 0)
        status = WITNESSED_STATUS if enough else OPEN_STATUS
        durations = [
            item["duration"] for item in row["receipts"] if item["duration"] is not None
        ]
        form_rows.append(
            {
                **row,
                "status": status,
                "authenticated_receipt_count": len(profits),
                "minimum_receipts": minimum,
                "profit_floor": _decimal_text(profit_floor),
                "base_energy_profit_floor": _decimal_text(base_floor),
                "gate_open": gate_open,
                "gate_basis": "AUTHENTICATED_CLOSED_RETURN_PROFIT_FLOOR",
                "duration_returns": durations,
                "fixed_horizon": None,
                "horizon_is_semantic": False,
                "proposal_can_gate": False,
                "price_level_authors_truth": False,
                "rate_scaling_preserves_profit_sign": True,
                "existence_closed": False,
                "continuation_status": OPEN_STATUS,
            }
        )

    status = (
        WITNESSED_STATUS
        if form_rows
        and not remainder
        and any(row["status"] == WITNESSED_STATUS for row in form_rows)
        else OPEN_STATUS
    )
    body = {
        "protocol": PROTOCOL,
        "equation": "Gate(form)=all authenticated closed returns profitable; profit_r=k*profit_e",
        "status": status,
        "proposals": proposal_rows,
        "forms": form_rows,
        "unprocessed_forms": [dict(item) for item in remainder],
        "unmatched_or_open_receipts": unmatched_receipts,
        "fixed_candidate_set": False,
        "fixed_horizon": None,
        "quote_authors_truth": False,
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
    }
    if boundary is not None:
        body["boundary_receipt"] = boundary
    body["id"] = _digest("trading-equation", body)
    return body


def resolve_resource_equation(
    *,
    pending_returns: Sequence[Mapping[str, Any]],
    completed_return_ids: Iterable[str] = (),
    limit: int | None = None,
) -> dict[str, Any]:
    """Schedule returned resources by dependency closure, never semantic rank.

    K_{n+1}=K_n union {r | deps(r) subset K_n}. A cycle limit may truncate
    transport, but every unprocessed returned relation remains OPEN rather than
    being rejected or ranked as less true.
    """

    completed = set(unique_strings(completed_return_ids))
    pending: dict[str, dict[str, Any]] = {}
    invalid: list[dict[str, Any]] = []
    for index, raw in enumerate(pending_returns):
        item = dict(raw)
        return_id = str(item.get("return_id") or item.get("id") or "")
        source = str(item.get("source_resource_id") or "")
        target = str(item.get("returned_resource_id") or item.get("target_resource_id") or "")
        deps = unique_strings(item.get("dependency_return_ids") or item.get("dependencies") or [])
        source_ids = _source_ids(item)
        valid = bool(return_id and source and target and (source_ids or item.get("exact_source")))
        normalized = {
            "index": index,
            "return_id": return_id,
            "source_resource_id": source,
            "returned_resource_id": target,
            "dependency_return_ids": deps,
            "source_ids": source_ids,
            "valid_return_relation": valid,
        }
        if not valid or return_id in pending:
            normalized["status"] = OPEN_STATUS
            normalized["open_reason"] = (
                "DUPLICATE_RETURN_ID" if return_id in pending else "INCOMPLETE_RETURN_RELATION"
            )
            invalid.append(normalized)
            continue
        pending[return_id] = normalized

    selected: list[dict[str, Any]] = []
    waves: list[list[str]] = []
    boundary = None
    normalized_limit = None if limit is None else max(0, int(limit))

    while pending:
        ready = sorted(
            (
                item for item in pending.values()
                if set(item["dependency_return_ids"]).issubset(completed)
            ),
            key=lambda item: (item["index"], item["return_id"]),
        )
        if not ready:
            break
        wave: list[str] = []
        for item in ready:
            if normalized_limit is not None and len(selected) >= normalized_limit:
                boundary = computation_boundary_open(
                    boundary="RESOURCE_REINTEGRATION_CYCLE_LIMIT",
                    configured_limit=normalized_limit,
                    observed=len(selected) + len(pending),
                )
                break
            return_id = item["return_id"]
            wave.append(return_id)
            selected.append(
                {
                    **item,
                    "status": WITNESSED_STATUS,
                    "selection_basis": "RETURN_RELATION_DEPENDENCY_CLOSURE",
                    "queue_position_authors_truth": False,
                    "schedule_authors_truth": False,
                }
            )
            completed.add(return_id)
            pending.pop(return_id, None)
        if wave:
            waves.append(wave)
        if boundary is not None:
            break

    open_rows = [
        {
            **item,
            "status": OPEN_STATUS,
            "open_reason": (
                "COMPUTATION_BOUNDARY"
                if boundary is not None
                else "UNRETURNED_OR_CYCLIC_DEPENDENCY"
            ),
            "queue_position_authors_truth": False,
            "schedule_authors_truth": False,
        }
        for item in sorted(pending.values(), key=lambda item: (item["index"], item["return_id"]))
    ]
    open_rows.extend(invalid)
    status = WITNESSED_STATUS if selected and not open_rows else OPEN_STATUS
    body = {
        "protocol": PROTOCOL,
        "equation": "K_(n+1)=K_n union {r | dependencies(r) subset K_n}",
        "status": status,
        "selected_returns": selected,
        "dependency_waves": waves,
        "open_returns": open_rows,
        "completed_return_ids": sorted(completed),
        "schedule_is_transport_only": True,
        "queue_order_is_semantic": False,
        "limit_is_semantic": False,
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
    }
    if boundary is not None:
        body["boundary_receipt"] = boundary
    body["id"] = _digest("resource-equation", body)
    return body


def resolve_legacy_equation(
    *,
    closure_derivation_id: str,
    components: Mapping[str, Mapping[str, Any]],
    production_components: Iterable[str] = (),
    legacy_test_modules: Iterable[str] = (),
) -> dict[str, Any]:
    """Separate current closure projection from historical compatibility lanes.

    A legacy component may factor through the current closure as a reading, but
    it never feeds back into or gates that closure. Legacy test failures remain
    visible in an informational lane and cannot be relabeled as core truth.
    """

    production = set(unique_strings(production_components))
    component_rows: list[dict[str, Any]] = []
    for name, value in sorted(components.items()):
        receipt = compatibility_reading_receipt(
            str(name),
            dict(value),
            closure_derivation_id=closure_derivation_id,
        )
        receipt["lane"] = "CURRENT_PROJECTION" if name in production else "LEGACY_COMPATIBILITY"
        receipt["may_feed_back_into_closure"] = False
        component_rows.append(receipt)

    production_rows = [row for row in component_rows if row["lane"] == "CURRENT_PROJECTION"]
    core_witnessed = bool(
        closure_derivation_id
        and production_rows
        and all(row["factors_through_current_closure"] for row in production_rows)
    )
    body = {
        "protocol": PROTOCOL,
        "equation": "Legacy_i=f_i(closure); Legacy_i never defines closure",
        "status": WITNESSED_STATUS if core_witnessed else OPEN_STATUS,
        "closure_derivation_id": closure_derivation_id,
        "components": component_rows,
        "test_lanes": {
            "core": {
                "blocking": True,
                "requires_current_closure": True,
            },
            "legacy_runtime": {
                "blocking": False,
                "informational": True,
                "module_paths": sorted(unique_strings(legacy_test_modules)),
                "failures_remain_visible": True,
                "failures_are_not_core_truth": True,
            },
        },
        "legacy_runtime_can_gate": False,
        "parallel_truth_runtime_present": False,
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
    }
    body["id"] = _digest("legacy-equation", body)
    return body


def resolve_closure_equations(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve every supplied subsystem through one interactive translation law."""

    result: dict[str, Any] = {
        "protocol": PROTOCOL,
        "equation": "Q_(t+1)=Close(Q_t + returned_interaction_t)",
        "proposal_status": OPEN_STATUS,
        "only_returned_interaction_recloses": True,
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
    }

    if payload.get("reopening") is not None:
        result["reopening"] = resolve_reopening_equation(**dict(payload["reopening"]))
    if payload.get("rule_charts") is not None:
        result["rule_charts"] = resolve_rule_chart_equation(**dict(payload["rule_charts"]))
    if payload.get("trading") is not None:
        result["trading"] = resolve_trading_equation(**dict(payload["trading"]))
    if payload.get("resources") is not None:
        result["resources"] = resolve_resource_equation(**dict(payload["resources"]))
    if payload.get("legacy") is not None:
        result["legacy"] = resolve_legacy_equation(**dict(payload["legacy"]))

    subsystem_rows = [
        value
        for key, value in result.items()
        if key in {"reopening", "rule_charts", "trading", "resources", "legacy"}
    ]
    result["status"] = (
        WITNESSED_STATUS
        if subsystem_rows and all(row.get("status") == WITNESSED_STATUS for row in subsystem_rows)
        else OPEN_STATUS
    )
    audit_target = dict(result)
    audit_target.pop("continuity_audit", None)
    result["continuity_audit"] = audit_translational_continuity(audit_target)
    result["id"] = _digest("closure-equations", result)
    return result


__all__ = [
    "PROTOCOL",
    "resolve_closure_equations",
    "resolve_legacy_equation",
    "resolve_reopening_equation",
    "resolve_resource_equation",
    "resolve_rule_chart_equation",
    "resolve_trading_equation",
]
