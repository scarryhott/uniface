from __future__ import annotations

from closure_supernet.nrrf837_runtime import (
    _enforce_agreement_natural_form_witness,
)


def receipt(*, proposal_event_id: str, is_natural_form: bool) -> dict:
    return {
        "coordination": {
            "continuum": {
                "agreement_modality": {
                    "selected_agreement_event_id": proposal_event_id,
                    "unique_under_declared_unity": True,
                },
                "local_presentations": [
                    {
                        "local_id": "proposal-local",
                        "event_id": proposal_event_id,
                        "is_natural_form": is_natural_form,
                    }
                ],
            }
        }
    }


def test_agreement_uniqueness_is_witnessed_only_at_a_modality_fixpoint() -> None:
    fixed = _enforce_agreement_natural_form_witness(
        receipt(proposal_event_id="proposal", is_natural_form=True)
    )
    agreement = fixed["coordination"]["continuum"]["agreement_modality"]
    assert agreement["unique_under_declared_unity"] is True
    assert agreement["selected_agreement_is_fixed_natural_form"] is True
    assert agreement["uniqueness_status"] == "WITNESSED_FIXED_NATURAL_FORM"

    noncanonical = _enforce_agreement_natural_form_witness(
        receipt(proposal_event_id="proposal", is_natural_form=False)
    )
    agreement = noncanonical["coordination"]["continuum"][
        "agreement_modality"
    ]
    assert agreement["unique_under_declared_unity"] is False
    assert agreement["selected_agreement_is_fixed_natural_form"] is False
    assert agreement["uniqueness_status"] == "OPEN_NOT_SELECTED_BY_UNITY"


def test_agreement_outside_the_active_continuum_remains_open() -> None:
    data = {
        "coordination": {
            "continuum": {
                "agreement_modality": {
                    "selected_agreement_event_id": "unseen-proposal",
                    "unique_under_declared_unity": True,
                },
                "local_presentations": [],
            }
        }
    }
    guarded = _enforce_agreement_natural_form_witness(data)
    agreement = guarded["coordination"]["continuum"]["agreement_modality"]
    assert agreement["unique_under_declared_unity"] is False
    assert agreement["selected_agreement_in_active_continuum"] is False
    assert agreement["uniqueness_status"] == "OPEN_OUTSIDE_ACTIVE_CONTINUUM"
