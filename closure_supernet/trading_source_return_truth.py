from __future__ import annotations

"""Verified source-return boundary for current translational truth.

A caller cannot create truth by setting ``returned=True``, inventing source ids,
choosing edge ids, injecting hair, or supplying execution/size flags. Trusted
source adapters sign exact returned semantic payloads with Ed25519; the current
closure runtime verifies those signatures with configured public keys before any
relation reaches closure.

External hair is never accepted as semantic input. Verified returns enter the
current closure in canonical zero-hair presentation; hair is then a derived/local
presentation freedom governed by the closure equations. This prevents arbitrary
caller hair from either manufacturing or suppressing returned truth.

A signed source event may be consumed only once within a supplied history. A
replayed event is forced OPEN, so replay cannot increase empirical hair fidelity,
horizon, discovery counts, or actionability.

Production public keys are supplied by ``CLOSURE_SOURCE_WITNESS_PUBLIC_KEYS`` as
a JSON mapping of authority id to base64 raw Ed25519 public key. Private keys
belong only in trusted source adapters and are never required by closure.
"""

import base64
from decimal import Decimal, InvalidOperation
import json
import os
from typing import Any, Mapping, Sequence

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/verified-source-return-truth-v2-canonical-replay-safe"
PUBLIC_KEYS_ENV = "CLOSURE_SOURCE_WITNESS_PUBLIC_KEYS"
TRADING_KIND = "TRADING_RELATION_RETURN"
ATLAS_KIND = "ATLAS_TRANSLATION_RETURN"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _first(value: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in value and value[key] is not None:
            return value[key]
    return None


def _decimal_text(value: Any) -> str | None:
    if value is None:
        return None
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if not result.is_finite():
        return None
    if result == 0:
        return "0"
    return format(result.normalize(), "f")


def _b64encode(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


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
            result[str(authority)] = Ed25519PublicKey.from_public_bytes(_b64decode(str(encoded)))
        except Exception:
            continue
    return result


def encode_public_key(public_key: Ed25519PublicKey) -> str:
    return _b64encode(public_key.public_bytes_raw())


def encode_private_key(private_key: Ed25519PrivateKey) -> str:
    return _b64encode(private_key.private_bytes_raw())


def private_key_from_base64(value: str) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(_b64decode(value))


def _trading_body(
    *, observer_id: str | None, authority_id: str, source_event_id: str,
    source_stream: str, row: Mapping[str, Any],
) -> dict[str, Any]:
    source = str(_first(row, "source_token", "source_node", "from_token", "from", "source") or "")
    target = str(_first(row, "target_token", "target_node", "to_token", "to", "target") or "")
    relation_value = _decimal_text(_first(
        row, "relation_value", "relative_value", "observed_value", "total_cost", "cost", "value"
    ))
    relative_size = _decimal_text(_first(
        row, "relative_ball_size", "relative_size", "executable_relative_size", "relative_capacity", "translated_size"
    ))
    relative_unit = str(_first(row, "relative_size_unit", "capacity_unit") or "") or None
    return {
        "protocol": PROTOCOL,
        "kind": TRADING_KIND,
        "authority_id": authority_id,
        "observer_id": observer_id,
        "source_event_id": source_event_id,
        "source_stream": source_stream,
        "source_token": source or None,
        "target_token": target or None,
        "relation_value": relation_value,
        "timestamp": _first(row, "timestamp", "observed_at", "returned_at"),
        "authenticated": row.get("authenticated") is True,
        "cost_complete": row.get("cost_complete") is True,
        "relative_size": relative_size,
        "relative_size_unit": relative_unit,
    }


def _atlas_body(
    *, observer_id: str | None, authority_id: str, source_event_id: str,
    source_stream: str, row: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "kind": ATLAS_KIND,
        "authority_id": authority_id,
        "observer_id": observer_id,
        "source_event_id": source_event_id,
        "source_stream": source_stream,
        "source_chart_id": str(row.get("source_chart_id") or "") or None,
        "target_chart_id": str(row.get("target_chart_id") or "") or None,
        "closure_commutes": row.get("closure_commutes") is True,
        "return_preserved": row.get("return_preserved") is True,
        "timestamp": _first(row, "timestamp", "observed_at", "returned_at"),
    }


def _issue(body: Mapping[str, Any], private_key: Ed25519PrivateKey) -> dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "authority_id": body["authority_id"],
        "body": dict(body),
        "signature": _b64encode(private_key.sign(_stable(body).encode("utf-8"))),
    }


def issue_trading_source_witness(
    *, private_key: Ed25519PrivateKey, authority_id: str, observer_id: str | None,
    source_event_id: str, source_stream: str, row: Mapping[str, Any],
) -> dict[str, Any]:
    return _issue(_trading_body(
        observer_id=observer_id, authority_id=authority_id,
        source_event_id=source_event_id, source_stream=source_stream, row=row,
    ), private_key)


def issue_atlas_translation_witness(
    *, private_key: Ed25519PrivateKey, authority_id: str, observer_id: str | None,
    source_event_id: str, source_stream: str, row: Mapping[str, Any],
) -> dict[str, Any]:
    return _issue(_atlas_body(
        observer_id=observer_id, authority_id=authority_id,
        source_event_id=source_event_id, source_stream=source_stream, row=row,
    ), private_key)


def _verify_witness(
    *, witness: Mapping[str, Any] | None, expected_body: Mapping[str, Any],
) -> tuple[bool, str, dict[str, Any] | None]:
    if not isinstance(witness, Mapping):
        return False, "SOURCE_WITNESS_MISSING", None
    if witness.get("protocol") != PROTOCOL:
        return False, "SOURCE_WITNESS_PROTOCOL_MISMATCH", None
    body = witness.get("body")
    if not isinstance(body, Mapping):
        return False, "SOURCE_WITNESS_BODY_MISSING", None
    authority = str(witness.get("authority_id") or body.get("authority_id") or "")
    if not authority:
        return False, "SOURCE_WITNESS_AUTHORITY_MISSING", None
    public_key = _trusted_public_keys().get(authority)
    if public_key is None:
        return False, "SOURCE_WITNESS_AUTHORITY_UNTRUSTED", dict(body)
    if dict(body) != dict(expected_body):
        return False, "SOURCE_WITNESS_SEMANTIC_MISMATCH", dict(body)
    try:
        public_key.verify(
            _b64decode(str(witness.get("signature") or "")),
            _stable(body).encode("utf-8"),
        )
    except (ValueError, InvalidSignature, TypeError):
        return False, "SOURCE_WITNESS_SIGNATURE_INVALID", dict(body)
    return True, "SOURCE_WITNESS_VERIFIED", dict(body)


def _witness_coordinates(witness: Any) -> tuple[Mapping[str, Any] | None, str, str, str]:
    if not isinstance(witness, Mapping):
        return None, "", "", ""
    body = witness.get("body")
    body_map = body if isinstance(body, Mapping) else {}
    authority = str(body_map.get("authority_id") or witness.get("authority_id") or "")
    return witness, authority, str(body_map.get("source_event_id") or ""), str(body_map.get("source_stream") or "")


def _canonicalize_hair(row: dict[str, Any]) -> None:
    for key in (
        "hair_delta", "potential_delta", "hair_source", "hair_target",
        "source_potential", "target_potential", "natural_form_value",
    ):
        row.pop(key, None)
    row["hair_delta"] = "0"


def _strip_action_capacity(row: dict[str, Any]) -> None:
    for key in (
        "relative_ball_size", "relative_size", "executable_relative_size", "relative_capacity",
        "translated_size", "relative_size_unit", "capacity_unit",
    ):
        row.pop(key, None)


def _force_trading_open(row: Mapping[str, Any], *, reason: str) -> dict[str, Any]:
    sanitized = dict(row)
    sanitized.update({
        "returned": False,
        "witnessed": False,
        "source_ids": [],
        "authenticated": False,
        "cost_complete": False,
        "source_witness_verified": False,
        "source_witness_reason": reason,
        "source_witness_protocol": PROTOCOL,
    })
    _strip_action_capacity(sanitized)
    _canonicalize_hair(sanitized)
    return sanitized


def verify_trading_source_return(
    *, observer_id: str | None, row: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = dict(row)
    witness, authority, source_event_id, source_stream = _witness_coordinates(raw.get("source_witness"))
    expected = _trading_body(
        observer_id=observer_id, authority_id=authority,
        source_event_id=source_event_id, source_stream=source_stream, row=raw,
    )
    ok, reason, verified_body = _verify_witness(witness=witness, expected_body=expected)
    if ok and verified_body is not None:
        sanitized = dict(raw)
        # Semantic relation identity comes from the signed exact source event,
        # never from a caller-selected edge id.
        sanitized.update({
            "id": verified_body["source_event_id"],
            "return_id": verified_body["source_event_id"],
            "source": verified_body["source_token"],
            "target": verified_body["target_token"],
            "value": verified_body["relation_value"],
            "timestamp": verified_body["timestamp"],
            "returned": True,
            "witnessed": True,
            "source_ids": [verified_body["source_event_id"]],
            "authenticated": verified_body["authenticated"],
            "cost_complete": verified_body["cost_complete"],
            "source_witness_verified": True,
            "source_witness_reason": reason,
            "source_witness_protocol": PROTOCOL,
            "source_authority_id": verified_body["authority_id"],
            "source_stream": verified_body["source_stream"],
        })
        _strip_action_capacity(sanitized)
        if verified_body.get("relative_size") is not None and verified_body.get("relative_size_unit"):
            sanitized["relative_size"] = verified_body["relative_size"]
            sanitized["relative_size_unit"] = verified_body["relative_size_unit"]
        _canonicalize_hair(sanitized)
    else:
        sanitized = _force_trading_open(raw, reason=reason)

    audit = {
        "status": WITNESSED_STATUS if ok else OPEN_STATUS,
        "verified": ok,
        "reason": reason,
        "authority_id": authority or None,
        "source_event_id": source_event_id or None,
        "source_stream": source_stream or None,
        "caller_returned_flag_authors_truth": False,
        "caller_source_ids_author_truth": False,
        "caller_return_id_authors_geometry": False,
        "caller_authenticated_flag_authors_execution": False,
        "caller_cost_complete_flag_authors_execution": False,
        "caller_size_authors_action": False,
        "caller_hair_authors_truth": False,
        "verified_external_return_uses_canonical_hair_presentation": True,
    }
    return sanitized, audit


def verify_trading_feedback(
    *, observer_id: str | None, feedback: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw in feedback:
        row, audit = verify_trading_source_return(observer_id=observer_id, row=raw)
        key = (str(audit.get("authority_id") or ""), str(audit.get("source_event_id") or ""))
        if audit["verified"] and key in seen:
            row = _force_trading_open(row, reason="SOURCE_WITNESS_REPLAYED")
            audit = {**audit, "status": OPEN_STATUS, "verified": False, "reason": "SOURCE_WITNESS_REPLAYED", "replay_rejected": True}
        elif audit["verified"]:
            seen.add(key)
        rows.append(row)
        audits.append(audit)
    verified = sum(1 for audit in audits if audit["verified"])
    return rows, {
        "protocol": PROTOCOL,
        "status": WITNESSED_STATUS if audits and verified == len(audits) else OPEN_STATUS,
        "input_count": len(audits),
        "verified_count": verified,
        "open_count": len(audits) - verified,
        "returns": audits,
        "truth_requires_verified_source_witness": True,
        "unsigned_or_untrusted_return_remains_open": True,
        "duplicate_source_event_replay_remains_open": True,
        "source_witness_public_key_is_server_configuration": True,
        "private_key_required_by_closure_runtime": False,
    }


def verify_trading_history(
    *, observer_id: str | None, history: Sequence[Sequence[Mapping[str, Any]]],
) -> tuple[list[list[dict[str, Any]]], list[dict[str, Any]]]:
    """Verify a returned history while consuming each signed source event once."""
    verified_history: list[list[dict[str, Any]]] = []
    history_audits: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for frame in history:
        frame_rows: list[dict[str, Any]] = []
        frame_audits: list[dict[str, Any]] = []
        for raw in frame:
            row, audit = verify_trading_source_return(observer_id=observer_id, row=raw)
            key = (str(audit.get("authority_id") or ""), str(audit.get("source_event_id") or ""))
            if audit["verified"] and key in seen:
                row = _force_trading_open(row, reason="SOURCE_WITNESS_REPLAYED")
                audit = {**audit, "status": OPEN_STATUS, "verified": False, "reason": "SOURCE_WITNESS_REPLAYED", "replay_rejected": True}
            elif audit["verified"]:
                seen.add(key)
            frame_rows.append(row)
            frame_audits.append(audit)
        count = sum(1 for audit in frame_audits if audit["verified"])
        verified_history.append(frame_rows)
        history_audits.append({
            "protocol": PROTOCOL,
            "status": WITNESSED_STATUS if frame_audits and count == len(frame_audits) else OPEN_STATUS,
            "input_count": len(frame_audits),
            "verified_count": count,
            "open_count": len(frame_audits) - count,
            "returns": frame_audits,
            "duplicate_source_event_replay_remains_open": True,
        })
    return verified_history, history_audits


def _verify_atlas_translation_row(
    *, observer_id: str | None, row: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = dict(row)
    witness, authority, source_event_id, source_stream = _witness_coordinates(raw.get("source_witness"))
    expected = _atlas_body(
        observer_id=observer_id, authority_id=authority,
        source_event_id=source_event_id, source_stream=source_stream, row=raw,
    )
    ok, reason, verified_body = _verify_witness(witness=witness, expected_body=expected)
    sanitized = dict(raw)
    if ok and verified_body is not None:
        sanitized.update({
            "source_chart_id": verified_body["source_chart_id"],
            "target_chart_id": verified_body["target_chart_id"],
            "returned": True,
            "source_preserved": True,
            "closure_commutes": verified_body["closure_commutes"],
            "return_preserved": verified_body["return_preserved"],
            "source_return_ids": [verified_body["source_event_id"]],
            "source_authority_id": verified_body["authority_id"],
            "source_stream": verified_body["source_stream"],
        })
    else:
        sanitized.update({
            "returned": False,
            "source_preserved": False,
            "closure_commutes": False,
            "return_preserved": False,
            "source_return_ids": [],
        })
    sanitized["source_witness_verified"] = ok
    sanitized["source_witness_reason"] = reason
    return sanitized, {
        "status": WITNESSED_STATUS if ok else OPEN_STATUS,
        "verified": ok,
        "reason": reason,
        "authority_id": authority or None,
        "source_event_id": source_event_id or None,
    }


def verify_atlas_translation_sources(
    *, observer_id: str | None, sources: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Verify every explicit atlas translation, including nested containers."""
    sanitized_sources: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw_source in sources:
        source = dict(raw_source)
        nested = source.get("atlas_translations")
        if isinstance(nested, Sequence) and not isinstance(nested, (str, bytes)):
            sanitized_nested: list[dict[str, Any]] = []
            for raw_translation in nested:
                if not isinstance(raw_translation, Mapping):
                    continue
                sanitized, audit = _verify_atlas_translation_row(observer_id=observer_id, row=raw_translation)
                key = (str(audit.get("authority_id") or ""), str(audit.get("source_event_id") or ""))
                if audit["verified"] and key in seen:
                    sanitized.update({
                        "returned": False, "source_preserved": False,
                        "closure_commutes": False, "return_preserved": False,
                        "source_return_ids": [], "source_witness_verified": False,
                        "source_witness_reason": "SOURCE_WITNESS_REPLAYED",
                    })
                    audit = {**audit, "status": OPEN_STATUS, "verified": False, "reason": "SOURCE_WITNESS_REPLAYED", "replay_rejected": True}
                elif audit["verified"]:
                    seen.add(key)
                sanitized_nested.append(sanitized)
                audits.append(audit)
            source["atlas_translations"] = sanitized_nested
            source.pop("source_witness", None)
            sanitized_sources.append(source)
        else:
            sanitized, audit = _verify_atlas_translation_row(observer_id=observer_id, row=source)
            key = (str(audit.get("authority_id") or ""), str(audit.get("source_event_id") or ""))
            if audit["verified"] and key in seen:
                sanitized.update({
                    "returned": False, "source_preserved": False,
                    "closure_commutes": False, "return_preserved": False,
                    "source_return_ids": [], "source_witness_verified": False,
                    "source_witness_reason": "SOURCE_WITNESS_REPLAYED",
                })
                audit = {**audit, "status": OPEN_STATUS, "verified": False, "reason": "SOURCE_WITNESS_REPLAYED", "replay_rejected": True}
            elif audit["verified"]:
                seen.add(key)
            sanitized_sources.append(sanitized)
            audits.append(audit)
    verified = sum(1 for audit in audits if audit["verified"])
    return sanitized_sources, {
        "protocol": PROTOCOL,
        "status": WITNESSED_STATUS if audits and verified == len(audits) else OPEN_STATUS,
        "input_count": len(audits),
        "verified_count": verified,
        "open_count": len(audits) - verified,
        "translations": audits,
        "atlas_admissibility_requires_verified_source_witness": True,
        "nested_atlas_translations_verified_individually": True,
        "outer_container_witness_cannot_author_nested_translation": True,
        "duplicate_source_event_replay_remains_open": True,
    }


__all__ = [
    "ATLAS_KIND", "PROTOCOL", "PUBLIC_KEYS_ENV", "TRADING_KIND",
    "encode_private_key", "encode_public_key", "issue_atlas_translation_witness",
    "issue_trading_source_witness", "private_key_from_base64",
    "verify_atlas_translation_sources", "verify_trading_feedback",
    "verify_trading_history", "verify_trading_source_return",
]
