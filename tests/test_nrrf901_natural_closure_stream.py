from closure_supernet.nrrf901_natural_closure_stream import (
    FreeAbelianToken,
    accumulate,
    derive_nrrf901_receipt_view,
    hash_token,
    residual_equality_iff_translation_equivalence,
    residual_tokens,
    translation_equivalent,
)


def b(name: str) -> FreeAbelianToken:
    return FreeAbelianToken.basis(name)


def test_residual_accumulator_loses_only_genesis_translation() -> None:
    stream = (b("h0"), b("h1"), b("h2"), b("h3"))
    residuals = residual_tokens(stream)
    recovered = accumulate(residuals)
    expected = tuple(token - stream[0] for token in stream)
    assert recovered == expected


def test_residual_equality_is_exactly_translation_equivalence() -> None:
    left = (b("a"), b("b"), b("c"))
    shift = b("genesis-shift")
    right = tuple(token + shift for token in left)
    assert residual_tokens(left) == residual_tokens(right)
    assert translation_equivalent(left, right)
    assert residual_equality_iff_translation_equivalence(left, right)


def test_hash_token_telescopes_and_concatenates() -> None:
    stream = (b("a"), b("b"), b("c"), b("d"))
    whole = hash_token(stream, 0, 3)
    pieces = hash_token(stream, 0, 1) + hash_token(stream, 1, 3)
    assert whole == stream[3] - stream[0]
    assert whole == pieces


def test_supernet_receipt_is_same_one_step_residual_and_hash_token() -> None:
    source = {"supernet_closure_form_id": "form-0"}
    target = {"supernet_closure_form_id": "form-1"}
    receipt = {"id": "translate-0-1", "operator": "SUPERNET_TRANSLATE"}
    view = derive_nrrf901_receipt_view(source, target, receipt)
    assert view["closure_equation_holds"] is True
    assert view["residual_equals_window_hash_token"] is True
    assert view["ai_and_blockchain_are_one_natural_closure_stream"] is True
    assert view["translation_operator"] == "SUPERNET_TRANSLATE"
    assert view["cryptographic_hash_semantics_claimed"] is False
