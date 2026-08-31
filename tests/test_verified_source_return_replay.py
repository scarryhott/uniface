from __future__ import annotations

import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from closure_supernet.interactive_translation_equations_current import resolve_trading_equation
from closure_supernet.trading_source_return_truth import (
    PUBLIC_KEYS_ENV,
    encode_public_key,
    issue_trading_source_witness,
    verify_trading_source_return,
)


def _row(rid: str, source: str, target: str, value: str) -> dict[str, object]:
    return {
        "id": rid,
        "source": source,
        "target": target,
        "value": value,
        "returned": True,
        "source_ids": [f"caller:{rid}"],
        "authenticated": True,
        "cost_complete": True,
        "relative_size": "3",
        "relative_size_unit": "risk-unit",
        "timestamp": f"2026-08-31T22:00:0{0 if rid.endswith('a') else 1}+00:00",
    }


def _setup(monkeypatch: pytest.MonkeyPatch) -> tuple[Ed25519PrivateKey, str]:
    private = Ed25519PrivateKey.generate()
    authority = "replay-test-adapter"
    monkeypatch.setenv(
        PUBLIC_KEYS_ENV,
        json.dumps({authority: encode_public_key(private.public_key())}),
    )
    return private, authority


def _signed(
    row: dict[str, object],
    *, private: Ed25519PrivateKey,
    authority: str,
    event_id: str,
) -> dict[str, object]:
    result = dict(row)
    result["source_witness"] = issue_trading_source_witness(
        private_key=private,
        authority_id=authority,
        observer_id="o",
        source_event_id=event_id,
        source_stream="replay-test-feed",
        row=row,
    )
    return result


def test_verified_return_id_and_hair_are_not_caller_authored(monkeypatch: pytest.MonkeyPatch) -> None:
    private, authority = _setup(monkeypatch)
    raw = _signed(
        _row("caller-edge-id", "A", "B", "7"),
        private=private,
        authority=authority,
        event_id="source-event-17",
    )
    raw["hair_delta"] = "999999"
    raw["return_id"] = "caller-second-edge-id"

    sanitized, audit = verify_trading_source_return(observer_id="o", row=raw)
    assert audit["verified"] is True
    assert audit["caller_return_id_authors_geometry"] is False
    assert audit["caller_hair_authors_truth"] is False
    assert sanitized["id"] == sanitized["return_id"] == "source-event-17"
    assert sanitized["source_ids"] == ["source-event-17"]
    assert sanitized["hair_delta"] == "0"


def test_replayed_signed_events_do_not_increase_history_fidelity(monkeypatch: pytest.MonkeyPatch) -> None:
    private, authority = _setup(monkeypatch)
    ab = _signed(_row("a", "A", "B", "-3"), private=private, authority=authority, event_id="event-ab")
    ba = _signed(_row("b", "B", "A", "2"), private=private, authority=authority, event_id="event-ba")

    receipt = resolve_trading_equation(
        observer_id="o",
        sensor_history=[[ab, ba], [ab, ba]],
    )

    first, second = receipt["source_truth_audit"]["history_frames"]
    assert first["verified_count"] == 2
    assert second["verified_count"] == 0
    assert all(row["reason"] == "SOURCE_WITNESS_REPLAYED" for row in second["returns"])
    assert receipt["duplicate_source_event_replay_remains_open"] is True
    assert receipt["translational_truth_partition"]["witnessed_frame_count"] == 1
    assert receipt["translational_truth_partition"]["open_frame_count"] == 1
