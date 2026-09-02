from __future__ import annotations

"""Deterministic execution kernel for the one Supernet translation.

The project has one semantic mutation:

    SUPERNET_TRANSLATE(source closure form, returned interaction)

Browser, agent and any future transport must invoke this exact callable.  The
kernel serialises returned interactions, derives content-addressed intent and
receipt identities without wall-clock input, and rejects two executions of the
same semantic intent if they produce different translational-truth results.

Wall-clock values may remain in source provenance, but never participate in the
runtime identity or deterministic translation receipt.
"""

import asyncio
import hashlib
import inspect
import json
import math
from copy import deepcopy
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

from fastapi import FastAPI
from fastapi.routing import APIRoute

from .supernet_closure_form import TRANSLATE_OPERATOR

DETERMINISTIC_TRANSLATION_PROTOCOL = (
    "closure.supernet/deterministic-supernet-translate-v1"
)
TRANSLATION_ENDPOINT = "/supernet/interface/projections/{contract_id}/return"

# These keys are allowed as provenance, but cannot author semantic identity.
_PROVENANCE_KEYS = {
    "created_at",
    "updated_at",
    "received_at",
    "sent_at",
    "requested_at",
    "responded_at",
    "wall_clock",
    "wall_clock_ns",
    "wall_clock_ms",
    "wall_clock_provenance",
    "client_time",
    "server_time",
    "latency",
    "latency_ms",
    "latency_ns",
}


def _plain(value: Any) -> Any:
    """Convert a value into an exact, canonical JSON-domain representation."""

    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="python", exclude_none=False)
    elif is_dataclass(value):
        value = asdict(value)

    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, Enum):
        return _plain(value.value)
    if isinstance(value, Fraction):
        return {
            "$fraction": [value.numerator, value.denominator],
        }
    if isinstance(value, Decimal):
        return {"$decimal": format(value, "f")}
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Non-finite floats cannot enter deterministic closure")
        # IEEE-754 hexadecimal form is exact and independent of locale.
        return {"$float_hex": value.hex()}
    if isinstance(value, Path):
        return {"$path": value.as_posix()}
    if isinstance(value, bytes):
        return {"$bytes_hex": value.hex()}
    if isinstance(value, Mapping):
        return {
            str(key): _plain(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, (set, frozenset)):
        rows = [_plain(item) for item in value]
        return sorted(rows, key=canonical_json)
    raise TypeError(f"Unsupported deterministic value: {type(value)!r}")


def _without_wall_clock(value: Any) -> Any:
    value = _plain(value)
    if isinstance(value, dict):
        return {
            key: _without_wall_clock(item)
            for key, item in value.items()
            if key.lower() not in _PROVENANCE_KEYS
            and "wall_clock" not in key.lower()
        }
    if isinstance(value, list):
        return [_without_wall_clock(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        _plain(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def content_id(namespace: str, value: Any) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return f"{namespace}:{digest[:32]}"


def deterministic_intent_payload(contract_id: str, payload: Any) -> dict[str, Any]:
    return {
        "protocol": DETERMINISTIC_TRANSLATION_PROTOCOL,
        "operator": TRANSLATE_OPERATOR,
        "source_contract_id": str(contract_id),
        "returned_interaction": _without_wall_clock(payload),
        "semantic_time": "RETURNED_EVENT_ORDER",
        "wall_clock_authors_identity": False,
    }


def derive_deterministic_intent_id(contract_id: str, payload: Any) -> str:
    return content_id(
        "supernet-translation-intent",
        deterministic_intent_payload(contract_id, payload),
    )


def _semantic_translation_result(result: Mapping[str, Any]) -> dict[str, Any]:
    translation = result.get("translation")
    translation = translation if isinstance(translation, Mapping) else {}
    target = result.get("supernet_potential_gate")
    target = target if isinstance(target, Mapping) else {}
    form = target.get("supernet_closure_form")
    form = form if isinstance(form, Mapping) else {}
    return {
        "operator": translation.get("operator") or result.get("operator"),
        "source_runtime_identity_id": translation.get(
            "source_runtime_identity_id"
        ),
        "target_runtime_identity_id": translation.get(
            "target_runtime_identity_id"
        ),
        "source_translation_truth_orbit_id": translation.get(
            "source_translation_truth_orbit_id"
        ),
        "target_translation_truth_orbit_id": translation.get(
            "target_translation_truth_orbit_id"
        ),
        "target_truth_invariant_id": form.get("truth_invariant_id"),
        "target_runtime_identity_from_form": form.get("runtime_identity_id"),
        "target_seen_id": form.get("seen_id"),
        "runtime_identity_is_translational_truth": translation.get(
            "runtime_identity_is_translational_truth"
        ),
        "runtime_state_change_is_this_translation": translation.get(
            "runtime_state_change_is_this_translation"
        ),
        "browser_trajectory_is_this_translation": translation.get(
            "browser_trajectory_is_this_translation"
        ),
    }


def derive_deterministic_receipt_id(
    intent_id: str,
    result: Mapping[str, Any],
) -> str:
    return content_id(
        "supernet-translation-receipt",
        {
            "protocol": DETERMINISTIC_TRANSLATION_PROTOCOL,
            "intent_id": intent_id,
            "semantic_result": _semantic_translation_result(result),
        },
    )


class DeterministicTranslationKernel:
    """Serial reducer and determinism witness for ``SUPERNET_TRANSLATE``."""

    def __init__(self, translate: Any) -> None:
        self._translate = translate
        self._lock = asyncio.Lock()
        self._receipt_by_intent: dict[str, str] = {}
        self._semantic_result_by_intent: dict[str, dict[str, Any]] = {}
        self._executions = 0

    async def translate(self, contract_id: str, payload: Any) -> dict[str, Any]:
        intent_id = derive_deterministic_intent_id(contract_id, payload)
        async with self._lock:
            result = self._translate(contract_id, payload)
            if inspect.isawaitable(result):
                result = await result
            if not isinstance(result, dict):
                raise TypeError("SUPERNET_TRANSLATE must return a mapping receipt")

            semantic_result = _semantic_translation_result(result)
            receipt_id = derive_deterministic_receipt_id(intent_id, result)
            previous_receipt = self._receipt_by_intent.get(intent_id)
            previous_result = self._semantic_result_by_intent.get(intent_id)
            if previous_receipt is not None and (
                previous_receipt != receipt_id or previous_result != semantic_result
            ):
                raise RuntimeError(
                    "One semantic Supernet intent produced two translational-truth "
                    "results"
                )

            self._receipt_by_intent[intent_id] = receipt_id
            self._semantic_result_by_intent[intent_id] = deepcopy(semantic_result)
            self._executions += 1
            return result

    def snapshot(self) -> dict[str, Any]:
        rows = [
            {
                "intent_id": intent_id,
                "receipt_id": self._receipt_by_intent[intent_id],
                "semantic_result": deepcopy(
                    self._semantic_result_by_intent[intent_id]
                ),
            }
            for intent_id in sorted(self._receipt_by_intent)
        ]
        return {
            "protocol": DETERMINISTIC_TRANSLATION_PROTOCOL,
            "operator": TRANSLATE_OPERATOR,
            "semantic_time": "RETURNED_EVENT_ORDER",
            "wall_clock_authors_identity": False,
            "single_serial_reducer": True,
            "execution_count": self._executions,
            "receipts": rows,
            "closure_id": content_id(
                "supernet-deterministic-kernel",
                {
                    "protocol": DETERMINISTIC_TRANSLATION_PROTOCOL,
                    "operator": TRANSLATE_OPERATOR,
                    "receipts": rows,
                },
            ),
        }


def _same_bound_callable(left: Any, right: Any) -> bool:
    return (
        getattr(left, "__self__", None) is getattr(right, "__self__", None)
        and getattr(left, "__func__", left) is getattr(right, "__func__", right)
    )


def attach_deterministic_translation_kernel(app: FastAPI) -> FastAPI:
    """Make HTTP, browser and agent mutation use one deterministic callable."""

    existing = getattr(app.state, "supernet_translation_kernel", None)
    if existing is not None:
        return app

    original = app.state.supernet_translate
    kernel = DeterministicTranslationKernel(original)
    app.state.supernet_translation_kernel = kernel
    app.state.supernet_translate = kernel.translate
    app.state.supernet_translate_deterministic = True
    app.state.supernet_semantic_time = "RETURNED_EVENT_ORDER"
    app.state.supernet_wall_clock_authors_identity = False

    matched = 0
    for route in app.router.routes:
        if not isinstance(route, APIRoute):
            continue
        if route.path != TRANSLATION_ENDPOINT or "POST" not in (route.methods or set()):
            continue
        # Keep FastAPI's already-derived parameter/dependency graph, but replace
        # the callable it invokes.  This makes the HTTP/browser transition the
        # identical bound method exposed to agent transports.
        route.endpoint = kernel.translate
        route.dependant.call = kernel.translate
        matched += 1

    if matched != 1:
        raise RuntimeError(
            "Deterministic closure requires exactly one published "
            f"SUPERNET_TRANSLATE route; found {matched}"
        )

    route_calls = [
        route.dependant.call
        for route in app.router.routes
        if isinstance(route, APIRoute)
        and route.path == TRANSLATION_ENDPOINT
        and "POST" in (route.methods or set())
    ]
    if len(route_calls) != 1 or not _same_bound_callable(
        route_calls[0], app.state.supernet_translate
    ):
        raise RuntimeError("Browser and runtime do not share one translation callable")
    return app


__all__ = [
    "DETERMINISTIC_TRANSLATION_PROTOCOL",
    "DeterministicTranslationKernel",
    "TRANSLATION_ENDPOINT",
    "attach_deterministic_translation_kernel",
    "canonical_json",
    "content_id",
    "derive_deterministic_intent_id",
    "derive_deterministic_receipt_id",
    "deterministic_intent_payload",
]
