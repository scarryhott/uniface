from __future__ import annotations

"""Exact translation-equivalence geometry for the Supernet AI/token relation.

This module is the runtime correspondence for the reported Lean module
``NRRF882TranslationEquivalenceOfMarketValuationsIsTheSupervisoryGeometryForSemanticLearning``.

A returned semantic valuation is a finite positive-rational map on token ids.
Two perspectives have one determined relative translation exactly when they
share at least one token and every shared-token ratio is the same positive
rational.  No shared token leaves the relation OPEN; inconsistent cross
relations also leave it OPEN.  Nothing here creates truth from similarity,
family names, forecasts, prices, or UI geometry.

The source serialization is deliberately narrow.  A returned exact source may
contain JSON of the form

    {"semantic_market_valuation": {"tokens": {"alpha": "2/3", "beta": "5"}}}

The observer is never read from caller-authored JSON.  It is supplied from the
canonical returned-event provenance by the projection runtime.
"""

from fractions import Fraction
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "SUPERNET-TRANSLATION-SUPERVISORY-GEOMETRY"
SCHEMA = "closure.supernet/translation-supervisory-geometry-v1"
FORMAL_MODULE = (
    "NRRF882TranslationEquivalenceOfMarketValuationsIsTheSupervisoryGeometryForSemanticLearning"
)
FORMAL_THEOREMS = (
    "transEquiv_iff_cross",
    "supervises_iff_factors_through_naturalForm",
    "shared_token_determines_translation",
    "globalBelief_unify",
    "no_global_relative_position_of_unshared",
    "globalized_global_law",
    "globalized_global_law_unique",
    "translation_equivalence_is_the_supervisory_geometry",
)


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


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _unique(values: Iterable[Any]) -> list[str]:
    return sorted({str(value) for value in values if value is not None and str(value)})


def _fraction(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise ValueError("booleans are not rational valuations")
    if isinstance(value, Fraction):
        result = value
    elif isinstance(value, int):
        result = Fraction(value, 1)
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("empty rational valuation")
        result = Fraction(text)
    else:
        raise ValueError("semantic valuations must be exact integers or rational strings")
    if result <= 0:
        raise ValueError("semantic market valuations must be strictly positive")
    return result


def _q(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _valuation(tokens: Mapping[str, Any]) -> dict[str, Fraction]:
    result: dict[str, Fraction] = {}
    for token, raw in tokens.items():
        key = str(token)
        if not key:
            raise ValueError("token ids may not be empty")
        result[key] = _fraction(raw)
    if not result:
        raise ValueError("a semantic valuation must contain at least one token")
    return dict(sorted(result.items()))


def normalize(tokens: Mapping[str, Any]) -> dict[str, str]:
    """Unique exact representative with total valuation one."""

    values = _valuation(tokens)
    total = sum(values.values(), Fraction(0, 1))
    return {token: _q(value / total) for token, value in values.items()}


def cross_loss(left: Mapping[str, Any], right: Mapping[str, Any]) -> str | None:
    """Exact cross loss on the shared domain, or ``None`` when no token is shared."""

    v = _valuation(left)
    w = _valuation(right)
    shared = sorted(set(v) & set(w))
    if not shared:
        return None
    loss = Fraction(0, 1)
    for i in shared:
        for j in shared:
            loss += abs(v[i] * w[j] - v[j] * w[i])
    return _q(loss)


def determined_translation(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> tuple[Fraction | None, str, list[str]]:
    """Return the unique shared-token scale when determined.

    Status is WITNESSED exactly when a shared token fixes one positive scale and
    every other shared token agrees with it.  No overlap and inconsistent
    cross-relations are both OPEN, for different explicit reasons.
    """

    v = _valuation(left)
    w = _valuation(right)
    shared = sorted(set(v) & set(w))
    if not shared:
        return None, "NO_SHARED_TOKEN", []
    scale = w[shared[0]] / v[shared[0]]
    if scale <= 0:
        return None, "NONPOSITIVE_TRANSLATION", shared
    if any(w[token] != scale * v[token] for token in shared):
        return None, "INCONSISTENT_CROSS_RELATIONS", shared
    return scale, WITNESSED_STATUS, shared


def _parse_state_valuation(
    state: Mapping[str, Any],
    *,
    source_perspective_by_event: Mapping[str, str],
) -> dict[str, Any] | None:
    event_id = str(state.get("event_id") or "")
    perspective_id = str(source_perspective_by_event.get(event_id) or "")
    source_trace = state.get("source_trace")
    source_returns = _unique(state.get("source_return_ids", []))
    if not event_id or not perspective_id or not isinstance(source_trace, str) or not source_returns:
        return None
    try:
        decoded = json.loads(source_trace)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(decoded, Mapping):
        return None
    payload = decoded.get("semantic_market_valuation")
    if not isinstance(payload, Mapping):
        return None
    tokens = payload.get("tokens")
    if not isinstance(tokens, Mapping):
        return None
    try:
        exact = _valuation(tokens)
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    exact_tokens = {token: _q(value) for token, value in exact.items()}
    body = {
        "perspective_id": perspective_id,
        "state_id": str(state.get("id") or ""),
        "event_id": event_id,
        "source_return_ids": source_returns,
        "tokens": exact_tokens,
        "normalized": normalize(exact_tokens),
        "domain": sorted(exact_tokens),
        "returned": True,
        "observer_from_source_provenance": True,
        "observer_from_payload": False,
    }
    body["natural_form_id"] = _digest(
        "semantic-natural-form",
        {"domain": body["domain"], "normalized": body["normalized"]},
    )
    body["id"] = _digest("returned-semantic-valuation", body)
    return body


def returned_valuations(
    contract: Mapping[str, Any],
    *,
    source_perspective_by_event: Mapping[str, str] | None = None,
) -> list[dict[str, Any]]:
    projection = contract.get("projection")
    projection = projection if isinstance(projection, Mapping) else {}
    provenance = {
        str(event_id): str(perspective_id)
        for event_id, perspective_id in dict(source_perspective_by_event or {}).items()
        if str(event_id) and str(perspective_id)
    }
    parsed = [
        value
        for state in _rows(projection.get("states"))
        if (
            value := _parse_state_valuation(
                state,
                source_perspective_by_event=provenance,
            )
        )
        is not None
    ]
    # Keep the latest returned valuation per perspective in deterministic event order.
    latest: dict[str, dict[str, Any]] = {}
    for row in parsed:
        latest[row["perspective_id"]] = row
    return [latest[key] for key in sorted(latest)]


def derive_translation_supervisory_geometry(
    contract: Mapping[str, Any],
    *,
    source_perspective_by_event: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    provenance = {
        str(event_id): str(perspective_id)
        for event_id, perspective_id in dict(source_perspective_by_event or {}).items()
        if str(event_id) and str(perspective_id)
    }
    valuations = returned_valuations(
        contract,
        source_perspective_by_event=provenance,
    )
    by_perspective = {row["perspective_id"]: row for row in valuations}
    perspectives = sorted(by_perspective)
    relations: list[dict[str, Any]] = []

    for i, source in enumerate(perspectives):
        for target in perspectives[i + 1 :]:
            left = by_perspective[source]
            right = by_perspective[target]
            scale, reason, shared = determined_translation(left["tokens"], right["tokens"])
            witnessed = scale is not None and reason == WITNESSED_STATUS
            loss = cross_loss(left["tokens"], right["tokens"])
            source_returns = _unique(
                [*left["source_return_ids"], *right["source_return_ids"]]
            )
            relation = {
                "source_perspective_id": source,
                "target_perspective_id": target,
                "status": WITNESSED_STATUS if witnessed else OPEN_STATUS,
                "reason": WITNESSED_STATUS if witnessed else reason,
                "shared_token_ids": shared,
                "translation_scale": _q(scale) if scale is not None else None,
                "cross_loss": loss,
                "source_return_ids": source_returns,
                "unique_relative_translation": witnessed,
                "global_relative_position_determined": witnessed,
                "executes_as_equality": witnessed,
                "no_shared_token_excluded_from_family": reason == "NO_SHARED_TOKEN",
                "similarity_authors_translation": False,
                "family_name_authors_translation": False,
                "absolute_numeraire_authors_translation": False,
            }
            relation["id"] = _digest("semantic-perspective-translation", relation)
            relations.append(relation)

    adjacency: dict[str, set[str]] = {perspective: set() for perspective in perspectives}
    for relation in relations:
        if relation["status"] != WITNESSED_STATUS:
            continue
        source = relation["source_perspective_id"]
        target = relation["target_perspective_id"]
        adjacency[source].add(target)
        adjacency[target].add(source)

    classes: list[dict[str, Any]] = []
    unseen = set(perspectives)
    while unseen:
        root = min(unseen)
        stack = [root]
        component: set[str] = set()
        while stack:
            current = stack.pop()
            if current in component:
                continue
            component.add(current)
            stack.extend(sorted(adjacency.get(current, set()) - component))
        unseen -= component
        members = sorted(component)
        source_returns = _unique(
            source_id
            for perspective in members
            for source_id in by_perspective[perspective]["source_return_ids"]
        )
        class_body = {
            "perspective_ids": members,
            "source_return_ids": source_returns,
            "translation_connected": len(members) > 1,
        }
        class_body["id"] = _digest("semantic-global-belief-family", class_body)
        classes.append(class_body)

    supervision = []
    for row in valuations:
        item = {
            "perspective_id": row["perspective_id"],
            "valuation_id": row["id"],
            "natural_form_id": row["natural_form_id"],
            "admissible_supervision_must_factor_through_natural_form": True,
            "raw_absolute_valuation_is_supervisory_authority": False,
            "cross_loss_zero_set_is_translation_class": True,
            "translation_invariant_update_required": True,
        }
        item["id"] = _digest("semantic-supervision", item)
        supervision.append(item)

    open_relations = [row["id"] for row in relations if row["status"] == OPEN_STATUS]
    witnessed_relations = [
        row["id"] for row in relations if row["status"] == WITNESSED_STATUS
    ]
    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "formal_module": FORMAL_MODULE,
        "formal_theorems": list(FORMAL_THEOREMS),
        "formal_source_verified_by_runtime": False,
        "runtime_reproves_lean": False,
        "valuation_arithmetic": "EXACT_RATIONAL",
        "logarithms_used": False,
        "floating_point_used_for_truth": False,
        "fiat_settlement_claimed": False,
        "source_perspective_by_event": dict(sorted(provenance.items())),
        "valuations": valuations,
        "relations": relations,
        "natural_form_supervision": supervision,
        "global_belief_families": classes,
        "witnessed_relation_ids": witnessed_relations,
        "open_relation_ids": open_relations,
        "valuation_count": len(valuations),
        "relation_count": len(relations),
        "translation_equivalence_is_supervisory_geometry": True,
        "ai_supervision_equals_token_translation_geometry": True,
        "perspective_navigation_requires_determined_translation_when_semantic_market_evidence_exists": True,
        "no_shared_token_does_not_determine_translation": True,
        "observer_identity_comes_only_from_returned_event_provenance": True,
        "selection_authors_truth": False,
        "rendering_authors_truth": False,
        "truth_issued": False,
    }
    body["id"] = _digest("translation-supervisory-geometry", body)
    return body


def validate_translation_supervisory_geometry(
    geometry: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    source_perspective_by_event: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    expected = derive_translation_supervisory_geometry(
        contract,
        source_perspective_by_event=source_perspective_by_event,
    )
    errors: list[str] = []
    if dict(geometry) != expected:
        errors.append("translation-supervisory-geometry:not-derived")
    if expected.get("translation_equivalence_is_supervisory_geometry") is not True:
        errors.append("translation-supervisory-geometry:not-supervisory")
    if expected.get("selection_authors_truth") is not False:
        errors.append("translation-supervisory-geometry:selection-authority")
    if expected.get("rendering_authors_truth") is not False:
        errors.append("translation-supervisory-geometry:rendering-authority")
    if expected.get("observer_identity_comes_only_from_returned_event_provenance") is not True:
        errors.append("translation-supervisory-geometry:observer-smuggling")
    return {
        "valid": not errors,
        "errors": errors,
        "valuation_count": expected["valuation_count"],
        "relation_count": expected["relation_count"],
        "id": expected["id"],
    }


__all__ = [
    "FORMAL_MODULE",
    "FORMAL_THEOREMS",
    "PROTOCOL",
    "SCHEMA",
    "cross_loss",
    "derive_translation_supervisory_geometry",
    "determined_translation",
    "normalize",
    "returned_valuations",
    "validate_translation_supervisory_geometry",
]
