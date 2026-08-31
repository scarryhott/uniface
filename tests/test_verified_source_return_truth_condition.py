from __future__ import annotations

import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from closure_supernet.interactive_translation_equations_current import (
    resolve_closure_equations,
    resolve_trading_equation,
)
from closure_supernet.trading_source_return_truth import (
    PUBLIC_KEYS_ENV,
    encode_public_key,
    issue_atlas_translation_witness,
    issue_trading_source_witness,
    verify_atlas_translation_sources,
)


def _row(
    return_id: str,
    source: str,
    target: str,
    value: str,
    *,
    hair_delta: str = "0",
    relative_size: str = "3",
) -> dict[str, object]:
    return {
        "id": return_id,
        "source": source,
        "target": target,
        "value": value,
        "hair_delta": hair_delta,
        # Deliberately include all historical caller claims. In VERIFIED mode
        # none of these is sufficient without the signed source witness.
        "source_ids": [f"caller:{return_id}"],
        "returned": True,
        "authenticated": True,
        "cost_complete": True,
        "relative_size": relative_size,
        "relative_size_unit": "risk-unit",
        "timestamp": f"2026-08-31T21:00:0{0 if return_id.endswith('a') else 1}+00:00",
    }


def _authority(monkeypatch: pytest.MonkeyPatch) -> tuple[Ed25519PrivateKey, str]:
    private = Ed25519PrivateKey.generate()
    authority = "test-source-adapter"
    monkeypatch.setenv(
        PUBLIC_KEYS_ENV,
        json.dumps({authority: encode_public_key(private.public_key())}),
    )
    return private, authority


def _sign(
    row: dict[str, object],
    *,
    private: Ed25519PrivateKey,
    authority: str,
    observer_id: str = "o",
) -> dict[str, object]:
    result = dict(row)
    result["source_witness"] = issue_trading_source_witness(
        private_key=private,
        authority_id=authority,
        observer_id=observer_id,
        source_event_id=f"exact-source:{row['id']}",
        source_stream="test-market-feed",
        row=row,
    )
    return result


def test_unsigned_caller_flags_cannot_author_current_truth(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(PUBLIC_KEYS_ENV, raising=False)
    receipt = resolve_trading_equation(
        observer_id="o",
        sensor_feedback=[
            _row("a", "A", "B", "-3"),
            _row("b", "B", "A", "2"),
        ],
    )

    assert receipt["source_return_truth_condition_enforced"] is True
    assert receipt["truth_requires_verified_source_witness"] is True
    assert receipt["caller_returned_flag_authors_truth"] is False
    assert receipt["caller_source_ids_author_truth"] is False
    assert receipt["status"] == "OPEN"
    assert receipt["natural_forms"] == []
    assert receipt["current_profit_truth_witnessed"] is False
    assert receipt["source_truth_audit"]["feedback"]["verified_count"] == 0


def test_signed_exact_source_returns_can_reclose_truth(monkeypatch: pytest.MonkeyPatch) -> None:
    private, authority = _authority(monkeypatch)
    feedback = [
        _sign(_row("a", "A", "B", "-3"), private=private, authority=authority),
        _sign(_row("b", "B", "A", "2"), private=private, authority=authority),
    ]
    receipt = resolve_trading_equation(observer_id="o", sensor_feedback=feedback)

    assert receipt["status"] == "WITNESSED"
    assert receipt["source_truth_audit"]["feedback"]["verified_count"] == 2
    assert len(receipt["natural_forms"]) == 1
    form = receipt["natural_forms"][0]
    assert form["unitary_curvature"] == "-1"
    assert form["natural_profit"] == "1"
    assert form["orientation"] == "PROFITABLE"


def test_tampering_with_signed_relation_value_forces_open(monkeypatch: pytest.MonkeyPatch) -> None:
    private, authority = _authority(monkeypatch)
    first = _sign(_row("a", "A", "B", "-3"), private=private, authority=authority)
    second = _sign(_row("b", "B", "A", "2"), private=private, authority=authority)
    first["value"] = "-300"

    receipt = resolve_trading_equation(observer_id="o", sensor_feedback=[first, second])
    assert receipt["status"] == "OPEN"
    assert receipt["natural_forms"] == []
    reasons = {
        row["reason"] for row in receipt["source_truth_audit"]["feedback"]["returns"]
    }
    assert "SOURCE_WITNESS_SEMANTIC_MISMATCH" in reasons


def test_source_witness_is_observer_relative_and_not_replayable(monkeypatch: pytest.MonkeyPatch) -> None:
    private, authority = _authority(monkeypatch)
    feedback = [
        _sign(_row("a", "A", "B", "-3"), private=private, authority=authority, observer_id="o"),
        _sign(_row("b", "B", "A", "2"), private=private, authority=authority, observer_id="o"),
    ]

    receipt = resolve_trading_equation(observer_id="other", sensor_feedback=feedback)
    assert receipt["status"] == "OPEN"
    assert receipt["natural_forms"] == []


def test_closed_hair_remains_presentation_and_needs_no_resigning(monkeypatch: pytest.MonkeyPatch) -> None:
    private, authority = _authority(monkeypatch)
    base = [
        _sign(_row("a", "A", "B", "-3"), private=private, authority=authority),
        _sign(_row("b", "B", "A", "2"), private=private, authority=authority),
    ]
    translated = [dict(base[0]), dict(base[1])]
    translated[0]["hair_delta"] = "5"
    translated[1]["hair_delta"] = "-5"

    left = resolve_trading_equation(observer_id="o", sensor_feedback=base)
    right = resolve_trading_equation(observer_id="o", sensor_feedback=translated)

    assert left["status"] == right["status"] == "WITNESSED"
    assert left["natural_forms"][0]["closure_id"] == right["natural_forms"][0]["closure_id"]
    assert left["natural_forms"][0]["natural_profit"] == right["natural_forms"][0]["natural_profit"] == "1"


def test_unsigned_atlas_translation_cannot_author_family_admissibility(monkeypatch: pytest.MonkeyPatch) -> None:
    private, authority = _authority(monkeypatch)
    raw = {
        "source_chart_id": "runtime-nf:truth",
        "target_chart_id": "historical:family",
        "returned": True,
        "source_preserved": True,
        "closure_commutes": True,
        "return_preserved": True,
        "source_return_ids": ["caller-id"],
    }
    unsigned, audit = verify_atlas_translation_sources(observer_id="o", sources=[raw])
    assert audit["verified_count"] == 0
    assert unsigned[0]["returned"] is False
    assert unsigned[0]["source_preserved"] is False

    signed = dict(raw)
    signed["source_witness"] = issue_atlas_translation_witness(
        private_key=private,
        authority_id=authority,
        observer_id="o",
        source_event_id="exact-source:atlas-1",
        source_stream="test-atlas-feed",
        row=raw,
    )
    verified, audit2 = verify_atlas_translation_sources(observer_id="o", sources=[signed])
    assert audit2["verified_count"] == 1
    assert verified[0]["returned"] is True
    assert verified[0]["source_preserved"] is True
    assert verified[0]["source_return_ids"] == ["exact-source:atlas-1"]


def test_external_resolver_forbids_formal_fixture_bypass() -> None:
    with pytest.raises(ValueError, match="require VERIFIED source truth"):
        resolve_closure_equations({
            "trading": {
                "observer_id": "o",
                "source_truth_mode": "FORMAL_FIXTURE",
                "sensor_feedback": [_row("a", "A", "B", "1")],
            }
        })


def test_formal_fixture_mode_is_explicit_direct_compatibility_only() -> None:
    receipt = resolve_trading_equation(
        observer_id="o",
        source_truth_mode="FORMAL_FIXTURE",
        sensor_feedback=[
            _row("a", "A", "B", "-3"),
            _row("b", "B", "A", "2"),
        ],
    )
    assert receipt["status"] == "WITNESSED"
    assert receipt["source_return_truth_condition_enforced"] is False
    assert receipt["source_truth_audit"]["formal_fixture_mode_is_not_externally_admissible"] is True
    assert receipt["formal_fixture_mode_is_not_external_truth"] is True
