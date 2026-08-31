from __future__ import annotations

"""NRRF870 translation-based natural trading closure runtime.

Truth is generated only by source-preserving returned interaction.

Finite returned sensor relations are read as a directed chart. The open sensor
reads the complete simple-cycle geometry of that chart; every finite closed walk
decomposes into simple cycles, so graph traversal order has no semantic role.

For each returned closed itinerary:
* curvature is the hair-blind closed-itinerary sum of natural-form values;
* natural profit is the negative curvature;
* available amplitude is the negative part max(0, -curvature);
* the raw ball partition is running P&L on the presented chart and is not hair
  invariant;
* the normalized closure ball partition pushes all path hair into the return,
  so its maximum equals amplitude;
* clock duration is provenance only;
* signal and trade are equal relative readings of the same closure translation.

No successor quote, fixed horizon, feature selector, route nomination, BFS path,
or undirected connectivity may author truth.
"""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import (
    OPEN_STATUS,
    WITNESSED_STATUS,
    computation_boundary_open,
    unique_strings,
)
from .interactive_derivation_calculus import (
    REFUTED_STATUS,
    loop_refutation_certificate,
    translation_certificate,
)

PROTOCOL = "closure.supernet/open-sensor-trading-translation-closure-nrrf870-v1"


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


def _text(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _first(value: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in value and value[key] is not None:
            return value[key]
    return None


def _source_ids(value: Mapping[str, Any]) -> list[str]:
    raw = _first(value, "source_return_ids", "source_ids", "exact_source_ids")
    if raw is None:
        raw = []
    if isinstance(raw, str):
        raw = [raw]
    return unique_strings(raw)


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


def _bounded_prefix(
    values: Sequence[Mapping[str, Any]],
    *,
    limit: int | None,
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]], dict[str, Any] | None]:
    if limit is None:
        return list(values), [], None
    normalized = max(0, int(limit))
    selected = list(values[:normalized])
    remainder = list(values[normalized:])
    boundary = None
    if remainder:
        boundary = computation_boundary_open(
            boundary="OPEN_SENSOR_TRADING_RETURN_LIMIT",
            configured_limit=normalized,
            observed=len(values),
        )
    return selected, remainder, boundary


def _normalize_return(index: int, raw: Mapping[str, Any]) -> dict[str, Any]:
    item = dict(raw)
    return_id = str(_first(item, "return_id", "id") or f"sensor-return-{index}")
    source = str(
        _first(
            item,
            "source_token",
            "source_node",
            "from_token",
            "from",
            "source",
        )
        or ""
    )
    target = str(
        _first(
            item,
            "target_token",
            "target_node",
            "to_token",
            "to",
            "target",
        )
        or ""
    )
    source_ids = _source_ids(item)
    returned = item.get("returned") is True or item.get("witnessed") is True
    if "returned" not in item and "witnessed" not in item:
        returned = bool(source_ids)

    parse_error: str | None = None
    relation_value: Decimal | None
    hair_delta: Decimal | None
    natural_value: Decimal | None
    try:
        relation_value = _decimal(
            _first(
                item,
                "relation_value",
                "relative_value",
                "observed_value",
                "total_cost",
                "cost",
                "value",
            ),
            field="relation_value",
        )
        explicit_hair_delta = _first(item, "hair_delta", "potential_delta")
        if explicit_hair_delta is not None:
            hair_delta = _decimal(explicit_hair_delta, field="hair_delta")
        else:
            hair_source = _first(item, "hair_source", "source_potential")
            hair_target = _first(item, "hair_target", "target_potential")
            if hair_source is None and hair_target is None:
                hair_delta = Decimal("0")
            elif hair_source is None or hair_target is None:
                raise ValueError("hair_source and hair_target must be supplied together")
            else:
                hair_delta = _decimal(
                    hair_target, field="hair_target"
                ) - _decimal(hair_source, field="hair_source")
        natural_value = relation_value - hair_delta
    except ValueError as exc:
        relation_value = None
        hair_delta = None
        natural_value = None
        parse_error = str(exc)

    source_preserved = bool(source and target and source_ids and returned)
    cost_complete = item.get("cost_complete") is True
    authenticated = item.get("authenticated") is True
    valid = bool(source_preserved and parse_error is None)

    return {
        "index": index,
        "return_id": return_id,
        "source_token": source or None,
        "target_token": target or None,
        "source_ids": source_ids,
        "returned": returned,
        "source_preserved": source_preserved,
        "authenticated": authenticated,
        "cost_complete": cost_complete,
        "relation_value": _text(relation_value),
        "hair_delta": _text(hair_delta),
        "natural_form_value": _text(natural_value),
        "timestamp": _first(item, "timestamp", "observed_at", "returned_at"),
        "parse_error": parse_error,
        "status": WITNESSED_STATUS if valid else OPEN_STATUS,
        "successor_quote_used": False,
        "fixed_horizon_used": False,
        "feature_selector_used": False,
    }


def _adjacency(edges: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for raw in edges:
        edge = dict(raw)
        if edge.get("status") != WITNESSED_STATUS:
            continue
        adjacency.setdefault(str(edge["source_token"]), []).append(edge)
    for rows in adjacency.values():
        rows.sort(key=lambda row: (int(row["index"]), str(row["return_id"])))
    return adjacency


def _strongly_connected_components(
    edges: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Directed closure fibres; undirected connectivity never authors a ball."""

    adjacency = _adjacency(edges)
    nodes = sorted(
        {
            str(endpoint)
            for edge in edges
            if edge.get("status") == WITNESSED_STATUS
            for endpoint in (edge.get("source_token"), edge.get("target_token"))
            if endpoint
        }
    )
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    components: list[list[str]] = []

    def strongconnect(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for edge in adjacency.get(node, []):
            target = str(edge["target_token"])
            if target not in indices:
                strongconnect(target)
                lowlink[node] = min(lowlink[node], lowlink[target])
            elif target in on_stack:
                lowlink[node] = min(lowlink[node], indices[target])

        if lowlink[node] == indices[node]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            components.append(sorted(component))

    for node in nodes:
        if node not in indices:
            strongconnect(node)

    rows: list[dict[str, Any]] = []
    for members in sorted(components):
        self_loop = any(
            edge.get("status") == WITNESSED_STATUS
            and str(edge.get("source_token")) == str(edge.get("target_token"))
            and str(edge.get("source_token")) in members
            for edge in edges
        )
        supports_closed_itinerary = len(members) > 1 or self_loop
        body = {"member_tokens": members}
        rows.append(
            {
                "ball_id": _digest("trading-closure-fibre", body),
                "member_tokens": members,
                "supports_closed_itinerary": supports_closed_itinerary,
                "partition_is_return_generated": True,
                "partition_is_directed_translation_fibre": True,
                "undirected_connectivity_authors_truth": False,
                "partition_label_authors_truth": False,
            }
        )
    return rows


def _canonical_relation_cycle(
    edges: Sequence[Mapping[str, Any]],
) -> tuple[tuple[str, str], ...]:
    pairs = [
        (str(edge["source_token"]), str(edge["target_token"]))
        for edge in edges
    ]
    if not pairs:
        return ()
    rotations = [
        tuple(pairs[index:] + pairs[:index])
        for index in range(len(pairs))
    ]
    return min(rotations)


def _canonical_edge_cycle(edges: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    edge_ids = [str(edge["return_id"]) for edge in edges]
    if not edge_ids:
        return ()
    rotations = [
        tuple(edge_ids[index:] + edge_ids[:index])
        for index in range(len(edge_ids))
    ]
    return min(rotations)


def _all_simple_cycles(edges: Sequence[Mapping[str, Any]]) -> list[list[dict[str, Any]]]:
    """Enumerate every simple directed returned cycle.

    Every finite closed walk decomposes into simple cycles, so this set
    determines the whole closed-itinerary geometry without choosing one path.
    """

    adjacency = _adjacency(edges)
    nodes = sorted(
        {
            str(endpoint)
            for edge in edges
            if edge.get("status") == WITNESSED_STATUS
            for endpoint in (edge.get("source_token"), edge.get("target_token"))
            if endpoint
        }
    )
    found: dict[tuple[str, ...], list[dict[str, Any]]] = {}

    def visit(
        start: str,
        current: str,
        visited: set[str],
        path: list[dict[str, Any]],
    ) -> None:
        for edge in adjacency.get(current, []):
            target = str(edge["target_token"])
            if target == start:
                cycle = [*path, edge]
                signature = _canonical_edge_cycle(cycle)
                found.setdefault(signature, cycle)
            elif target not in visited:
                visit(start, target, {*visited, target}, [*path, edge])

    for start in nodes:
        visit(start, start, {start}, [])

    return [
        found[key]
        for key in sorted(found)
    ]


def _ball_for_cycle(
    edges: Sequence[Mapping[str, Any]],
    balls: Sequence[Mapping[str, Any]],
) -> dict[str, Any] | None:
    members = {
        str(endpoint)
        for edge in edges
        for endpoint in (edge["source_token"], edge["target_token"])
    }
    for ball in balls:
        if members.issubset(set(map(str, ball.get("member_tokens", [])))):
            return dict(ball)
    return None


def _support_metadata(edges: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    indices = [int(edge["index"]) for edge in edges]
    parsed = [
        parsed
        for edge in edges
        if (parsed := _timestamp(edge.get("timestamp"))) is not None
    ]
    opened_at = min(parsed).isoformat() if parsed else None
    closed_at = max(parsed).isoformat() if parsed else None
    duration_seconds = (
        _text(Decimal(str((max(parsed) - min(parsed)).total_seconds())))
        if len(parsed) >= 2
        else None
    )
    return {
        "maze_return_ids": [str(edge["return_id"]) for edge in edges],
        "maze_steps": len(edges),
        "support_start_index": min(indices),
        "support_end_index": max(indices),
        "opened_at": opened_at,
        "closed_at": closed_at,
        "duration_seconds": duration_seconds,
        "fixed_horizon": None,
        "clock_duration_is_semantic_timing": False,
        "support_metadata_only": True,
    }


def _running_profit(
    edges: Sequence[Mapping[str, Any]],
    *,
    value_field: str,
) -> list[Decimal]:
    running = Decimal("0")
    values = [running]
    for edge in edges:
        running -= _decimal(edge[value_field], field=value_field)
        values.append(running)
    return values


def _ball_partition(values: Sequence[Decimal]) -> dict[str, Any]:
    maximum = max(values) if values else Decimal("0")
    first_index = next(
        (index for index, value in enumerate(values) if value == maximum),
        0,
    )
    return {
        "running_profit": [_text(value) for value in values],
        "max": _text(maximum),
        "first_max_index": first_index,
    }


def _closure_ball_partition(
    *,
    edge_count: int,
    natural_profit: Decimal,
) -> dict[str, Any]:
    """Normal form along one closed itinerary.

    Hair normalization makes every proper prefix free and leaves the entire
    closed-itinerary curvature on the return. Therefore the partition maximum
    is max(0, natural_profit), exactly the NRRF870 amplitude.
    """

    values = [Decimal("0")] * max(1, edge_count)
    values.append(natural_profit)
    partition = _ball_partition(values)
    partition.update(
        {
            "normalized_closure": True,
            "entry_leg_free": True,
            "return_attains_timing": True,
            "immediately_succeeding_quote_is_not_timing_rule": True,
        }
    )
    return partition


def _cycle_row(
    *,
    observer_id: str,
    edges: Sequence[dict[str, Any]],
    balls: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    edge_ids = [str(edge["return_id"]) for edge in edges]
    token_path = [str(edges[0]["source_token"])] + [
        str(edge["target_token"]) for edge in edges
    ]
    ball = _ball_for_cycle(edges, balls)
    ball_id = str(ball["ball_id"]) if ball else None
    relation_signature = _canonical_relation_cycle(edges)

    relation_sum = sum(
        (_decimal(edge["relation_value"], field="relation_value") for edge in edges),
        Decimal("0"),
    )
    hair_sum = sum(
        (_decimal(edge["hair_delta"], field="hair_delta") for edge in edges),
        Decimal("0"),
    )
    curvature = sum(
        (
            _decimal(edge["natural_form_value"], field="natural_form_value")
            for edge in edges
        ),
        Decimal("0"),
    )
    natural_profit = -curvature
    amplitude = max(Decimal("0"), natural_profit)
    hair_closed = hair_sum == 0

    source_ids = unique_strings(
        source_id
        for edge in edges
        for source_id in edge.get("source_ids", [])
    )
    source_witnessed = bool(observer_id and ball_id and source_ids)
    closure_witnessed = bool(source_witnessed and hair_closed)
    closure_status = WITNESSED_STATUS if closure_witnessed else OPEN_STATUS

    closure_translation_id = _digest(
        "trading-closure-truth",
        {
            "observer_id": observer_id,
            "directed_relations": relation_signature,
            "unitary_curvature": _text(curvature),
        },
    )
    interaction_witness_id = _digest(
        "trading-return-witness",
        {
            "observer_id": observer_id,
            "return_ids": edge_ids,
            "source_ids": source_ids,
        },
    )

    raw_partition = _ball_partition(
        _running_profit(edges, value_field="relation_value")
    )
    raw_partition.update(
        {
            "hair_invariant": False,
            "semantic_timing": False,
            "translation_id": interaction_witness_id,
        }
    )

    closure_partition = _closure_ball_partition(
        edge_count=len(edges),
        natural_profit=natural_profit,
    )
    closure_partition.update(
        {
            "hair_invariant": True,
            "semantic_timing": True,
            "translation_id": closure_translation_id,
        }
    )
    timing_value = _decimal(closure_partition["max"], field="timing")
    support = _support_metadata(edges)

    if closure_witnessed and curvature == 0:
        calculus_status = WITNESSED_STATUS
        derivation_certificate = translation_certificate(
            observer_id=observer_id,
            source_id=token_path[0],
            target_id=token_path[-1],
            relation_id=closure_translation_id,
            source_return_ids=source_ids,
        )
        loop_refutation = None
    elif closure_witnessed:
        calculus_status = REFUTED_STATUS
        derivation_certificate = None
        loop_refutation = loop_refutation_certificate(
            observer_id=observer_id,
            source_id=token_path[0],
            target_id=token_path[-1],
            relation_id=closure_translation_id,
            source_return_ids=source_ids,
            loop_witness={
                "return_ids": edge_ids,
                "token_path": token_path,
                "unitary_curvature": _text(curvature),
                "natural_profit": _text(natural_profit),
                "amplitude": _text(amplitude),
                "ball_id": ball_id,
            },
        )
    else:
        calculus_status = OPEN_STATUS
        derivation_certificate = None
        loop_refutation = None

    if natural_profit > 0:
        orientation = "PROFITABLE"
    elif natural_profit < 0:
        orientation = "COSTLY"
    else:
        orientation = "FLAT"

    amplitude_projection = {
        "translation_id": closure_translation_id,
        "unitary_curvature": _text(curvature),
        "amplitude": _text(amplitude),
        "amplitude_is_negative_curvature_part": True,
    }
    timing = {
        "translation_id": closure_translation_id,
        "value": _text(timing_value),
        "ball_partition_max": _text(timing_value),
        "running_profit": closure_partition["running_profit"],
        "first_max_index": closure_partition["first_max_index"],
        "return_attains_timing": True,
        "entry_leg_free_in_closure": True,
        "fixed_horizon": None,
        "timing_is_ball_partition_max": True,
        "clock_duration_authors_timing": False,
        "support": support,
        "maze_steps": support["maze_steps"],
        "support_start_index": support["support_start_index"],
        "support_end_index": support["support_end_index"],
        "opened_at": support["opened_at"],
        "closed_at": support["closed_at"],
        "duration_seconds": support["duration_seconds"],
    }

    all_authenticated = all(edge.get("authenticated") is True for edge in edges)
    all_cost_complete = all(edge.get("cost_complete") is True for edge in edges)
    execution_return_witnessed = bool(all_authenticated and all_cost_complete)

    signal = {
        "projection": "RELATIVE_SIGNAL",
        "translation_id": closure_translation_id,
        "ball_id": ball_id,
        "orientation": orientation,
        "value": _text(natural_profit),
        "amplitude": _text(amplitude),
        "natural_profit": _text(natural_profit),
        "status": closure_status,
        "signal_is_completed_round_trip_profit": True,
    }
    trade = {
        "projection": "RELATIVE_TRADE",
        "translation_id": closure_translation_id,
        "ball_id": ball_id,
        "orientation": orientation,
        "value": _text(natural_profit),
        "amplitude": _text(amplitude),
        "natural_profit": _text(natural_profit),
        "status": closure_status,
        "execution_return_status": (
            WITNESSED_STATUS if execution_return_witnessed else OPEN_STATUS
        ),
        "admissible": bool(
            closure_witnessed
            and amplitude > 0
            and execution_return_witnessed
        ),
        "automatic_order_submission": False,
    }

    return {
        "closure_id": closure_translation_id,
        "closure_truth_id": closure_translation_id,
        "interaction_witness_id": interaction_witness_id,
        "status": closure_status,
        "ball_id": ball_id,
        "return_ids": edge_ids,
        "token_path": token_path,
        "directed_relation_signature": [
            {"source_token": source, "target_token": target}
            for source, target in relation_signature
        ],
        "source_ids": source_ids,
        "relation_sum": _text(relation_sum),
        "hair_sum": _text(hair_sum),
        "hair_closes_on_return": hair_closed,
        "unitary_curvature": _text(curvature),
        "natural_profit": _text(natural_profit),
        "amplitude": _text(amplitude),
        "available_amplitude": _text(amplitude),
        "orientation": orientation,
        "raw_ball_partition": raw_partition,
        "closure_ball_partition": closure_partition,
        "timing": timing,
        "support": support,
        "amplitude_projection": amplitude_projection,
        "signal_projection": signal,
        "trade_projection": trade,
        "amplitude_timing_translation_equal": (
            amplitude_projection["translation_id"] == timing["translation_id"]
        ),
        "amplitude_timing_numerically_identical": amplitude == timing_value,
        "signal_trade_translation_equal": (
            signal["translation_id"] == trade["translation_id"]
        ),
        "signal_trade_value_equal": signal["value"] == trade["value"],
        "signal_precedes_trade_semantically": False,
        "trade_precedes_signal_semantically": False,
        "clock_duration_is_timing": False,
        "bfs_selected_route_authors_truth": False,
        "zero_curvature_calculus_status": calculus_status,
        "translation_witness": derivation_certificate,
        "loop_refutation": loop_refutation,
        "existence_witnessed_by_nonzero_curvature": bool(
            closure_witnessed and curvature != 0
        ),
        "continuation_status": OPEN_STATUS,
        "open_reasons": [
            reason
            for condition, reason in (
                (bool(observer_id), "MISSING_RELATIVE_OBSERVER"),
                (bool(ball_id), "DIRECTED_CLOSURE_FIBRE_NOT_DERIVED"),
                (bool(source_ids), "MISSING_SOURCE_RETURN"),
                (hair_closed, "HAIR_EQUATIONS_DO_NOT_CLOSE"),
            )
            if not condition
        ],
    }


def resolve_open_sensor_trading_closure(
    *,
    observer_id: str | None,
    sensor_feedback: Sequence[Mapping[str, Any]],
    max_returns: int | None = None,
) -> dict[str, Any]:
    """Resolve NRRF870 trading closure from returned open-sensor interaction."""

    observer = str(observer_id or "")
    selected, remainder, boundary = _bounded_prefix(
        sensor_feedback,
        limit=max_returns,
    )
    returns = [
        _normalize_return(index, raw)
        for index, raw in enumerate(selected)
    ]
    witnessed_edges = [
        row for row in returns if row["status"] == WITNESSED_STATUS
    ]

    balls = _strongly_connected_components(witnessed_edges)
    cycles = [
        _cycle_row(observer_id=observer, edges=cycle, balls=balls)
        for cycle in _all_simple_cycles(witnessed_edges)
    ]
    witnessed_cycles = [
        cycle for cycle in cycles if cycle["status"] == WITNESSED_STATUS
    ]

    cycle_ball_ids = {
        str(cycle["ball_id"])
        for cycle in witnessed_cycles
        if cycle.get("ball_id")
    }
    open_balls = [
        {
            **ball,
            "status": OPEN_STATUS,
            "open_reason": "NO_WITNESSED_HAIR_CLOSED_ITINERARY_YET",
        }
        for ball in balls
        if str(ball["ball_id"]) not in cycle_ball_ids
    ]

    relation_coordinates = sorted(
        {
            (str(edge["source_token"]), str(edge["target_token"]))
            for edge in witnessed_edges
        }
    )
    status = (
        WITNESSED_STATUS
        if observer and witnessed_cycles and not remainder
        else OPEN_STATUS
    )

    body: dict[str, Any] = {
        "protocol": PROTOCOL,
        "equation": (
            "returned interaction -> open-sensor closed-itinerary geometry -> "
            "unique normalized closure -> unitary curvature -> "
            "amplitude = timing = max(0,-curvature); signal = trade relative "
            "to the same translation"
        ),
        "status": status,
        "observer_id": observer or None,
        "sensor_returns": returns,
        "unprocessed_sensor_returns": [dict(item) for item in remainder],
        "ball_partition": balls,
        "open_balls": open_balls,
        "natural_forms": cycles,
        "closed_itinerary_geometry": cycles,
        "witnessed_natural_form_count": len(witnessed_cycles),
        "relation_coordinates": [
            {"source_token": source, "target_token": target}
            for source, target in relation_coordinates
        ],
        "continuum_dimension": len(relation_coordinates),
        "relational_closure_continuum": True,
        "relation_form_truth_translation_same_continuum": True,
        "open_sensor_runs_all_closed_itineraries": True,
        "simple_cycles_determine_finite_closed_itinerary_geometry": True,
        "bfs_route_authors_truth": False,
        "undirected_connectivity_authors_ball": False,
        "ball_partition_is_directed_translation_fibre": True,
        "feedback_hair_equation_general_solution_is_closure_plus_hair": True,
        "feedback_equation_unique_normalized_solution": True,
        "feedback_is_idempotent": True,
        "feedback_is_hair_blind": True,
        "profit_is_local_reading_of_global_cost_closure": True,
        "unitary_curvature_gives_amplitude": True,
        "amplitude_is_negative_curvature_part": True,
        "ball_partition_max_gives_timing": True,
        "normalized_closure_timing_equals_amplitude": True,
        "clock_duration_authors_timing": False,
        "amplitude_timing_are_equal_in_closure": True,
        "signal_trade_are_equal_relative_to_translation": True,
        "signals_of_completed_round_trips_are_hair_blind": True,
        "ask_to_immediately_succeeding_bid_is_definition": False,
        "successor_observation_authors_closure": False,
        "fixed_horizon": None,
        "horizon_is_semantic": False,
        "feature_selection_is_semantic": False,
        "strategy_selection_is_semantic": False,
        "route_nomination_authors_truth": False,
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "automatic_order_submission": False,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
    }
    if boundary is not None:
        body["boundary_receipt"] = boundary
    body["id"] = _digest("open-sensor-trading-translation-closure", body)
    return body


__all__ = ["PROTOCOL", "resolve_open_sensor_trading_closure"]
