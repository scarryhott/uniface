from __future__ import annotations

"""Runtime bridge for NRRF901: residual tokens and hash tokens are one closure stream.

The Lean theorem is stated over an additive token group Q.  Supernet closure-form
IDs are opaque symbols, so this bridge embeds them into the free Abelian group on
those symbols.  No numeric metric, cryptographic digest semantics, or external
state machine is introduced: a runtime state is a basis token and a transition
is exactly the residual between consecutive basis tokens.
"""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

FORMAL_REFERENCE = (
    "NRRF901AiTokenAndBlockchainTokenRefineToResidualTokensAndTheHashToken"
    "OneNaturalClosureStream.lean"
)
SCHEMA = "closure.supernet/nrrf901-natural-closure-stream-v1"


@dataclass(frozen=True)
class FreeAbelianToken:
    """Finite formal integer combination of opaque Supernet state symbols."""

    terms: tuple[tuple[str, int], ...] = ()

    @staticmethod
    def _normalize(items: Iterable[tuple[str, int]]) -> tuple[tuple[str, int], ...]:
        merged: dict[str, int] = {}
        for symbol, coefficient in items:
            key = str(symbol)
            merged[key] = merged.get(key, 0) + int(coefficient)
        return tuple(sorted((key, value) for key, value in merged.items() if value))

    @classmethod
    def basis(cls, symbol: str) -> "FreeAbelianToken":
        if not symbol:
            raise ValueError("a closure-form symbol is required")
        return cls(((str(symbol), 1),))

    def __add__(self, other: "FreeAbelianToken") -> "FreeAbelianToken":
        return FreeAbelianToken(self._normalize((*self.terms, *other.terms)))

    def __neg__(self) -> "FreeAbelianToken":
        return FreeAbelianToken(tuple((symbol, -coefficient) for symbol, coefficient in self.terms))

    def __sub__(self, other: "FreeAbelianToken") -> "FreeAbelianToken":
        return self + (-other)

    def as_dict(self) -> dict[str, int]:
        return dict(self.terms)


ZERO = FreeAbelianToken()


def state_token(state: Mapping[str, Any]) -> FreeAbelianToken:
    symbol = str(state.get("supernet_closure_form_id") or state.get("id") or "")
    return FreeAbelianToken.basis(symbol)


def residual_tokens(stream: Sequence[FreeAbelianToken]) -> tuple[FreeAbelianToken, ...]:
    return tuple(stream[index + 1] - stream[index] for index in range(len(stream) - 1))


def accumulate(residuals: Sequence[FreeAbelianToken]) -> tuple[FreeAbelianToken, ...]:
    total = ZERO
    result = [ZERO]
    for token in residuals:
        total = total + token
        result.append(total)
    return tuple(result)


def hash_token(stream: Sequence[FreeAbelianToken], start: int, stop: int) -> FreeAbelianToken:
    if not 0 <= start <= stop < len(stream):
        raise IndexError("hash-token window is outside the closure stream")
    return stream[stop] - stream[start]


def translation_equivalent(
    left: Sequence[FreeAbelianToken], right: Sequence[FreeAbelianToken]
) -> bool:
    if len(left) != len(right):
        return False
    if not left:
        return True
    delta = right[0] - left[0]
    return all(r == l + delta for l, r in zip(left, right))


def residual_equality_iff_translation_equivalence(
    left: Sequence[FreeAbelianToken], right: Sequence[FreeAbelianToken]
) -> bool:
    return (residual_tokens(left) == residual_tokens(right)) == translation_equivalent(left, right)


def closure_stream(states: Sequence[Mapping[str, Any]]) -> tuple[FreeAbelianToken, ...]:
    return tuple(state_token(state) for state in states)


def derive_nrrf901_receipt_view(
    source_gate: Mapping[str, Any],
    successor_gate: Mapping[str, Any],
    translation_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Read one existing SUPERNET_TRANSLATE receipt as the NRRF901 residual half."""

    source = state_token(source_gate)
    target = state_token(successor_gate)
    residual = target - source
    window = (source, target)
    return {
        "schema": SCHEMA,
        "formal_reference": FORMAL_REFERENCE,
        "runtime_reproves_formal_theorem": False,
        "carrier": "FREE_ABELIAN_GROUP_ON_SUPERNET_CLOSURE_FORM_IDS",
        "source_hash_state": source.as_dict(),
        "target_hash_state": target.as_dict(),
        "residual_token": residual.as_dict(),
        "hash_token": hash_token(window, 0, 1).as_dict(),
        "residual_equals_window_hash_token": residual == hash_token(window, 0, 1),
        "closure_equation_holds": target == source + residual,
        "translation_operator": translation_receipt.get("operator"),
        "translation_receipt_id": translation_receipt.get("id"),
        "ai_token_is_residual_reading": True,
        "blockchain_token_is_hash_state_reading": True,
        "ai_and_blockchain_are_one_natural_closure_stream": True,
        "genesis_is_only_accumulation_translation": True,
        "cryptographic_hash_semantics_claimed": False,
        "market_semantics_claimed": False,
        "model_semantics_claimed": False,
    }


__all__ = [
    "FORMAL_REFERENCE",
    "FreeAbelianToken",
    "SCHEMA",
    "ZERO",
    "accumulate",
    "closure_stream",
    "derive_nrrf901_receipt_view",
    "hash_token",
    "residual_equality_iff_translation_equivalence",
    "residual_tokens",
    "state_token",
    "translation_equivalent",
]
