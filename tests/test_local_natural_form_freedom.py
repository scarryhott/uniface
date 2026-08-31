from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.closure_ui_contract import (
    RETURN_ENDPOINT_TEMPLATE,
    validate_ui_contract,
)
from closure_supernet.config import RuntimeConfig
from closure_supernet.local_natural_form_freedom import (
    derive_local_natural_form_freedom,
    validate_local_natural_form_freedom,
)
from closure_supernet.minimal_projection_runtime import (
    derive_local_projection_commitment,
)
from closure_supernet.natural_form_atlas import (
    STATIC_FAMILIES,
    derive_versioned_natural_form_atlas,
)


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "local-natural-form-freedom.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _return_payload(contract: dict[str, Any], exact_source: str) -> dict[str, Any]:
    relation = contract["return_relation"]
    payload = {
        "return_relation_id": relation["id"],
        "perspective_id": contract["perspective_id"],
        "focus_event_id": contract["focus_event_id"],
        "exact_source_return": exact_source,
        "closure_equation_system_id": contract[
            "closure_naturality_equations"
        ]["id"],
    }
    payload["local_projection_commitment"] = derive_local_projection_commitment(
        contract,
        return_relation_id=payload["return_relation_id"],
        perspective_id=payload["perspective_id"],
        focus_event_id=payload["focus_event_id"],
        exact_source_return=payload["exact_source_return"],
    )
    return payload


def _interact(
    client: TestClient,
    contract: dict[str, Any],
    exact_source: str,
) -> dict[str, Any]:
    response = client.post(
        RETURN_ENDPOINT_TEMPLATE.format(contract_id=contract["id"]),
        json=_return_payload(contract, exact_source),
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["returned"] is True
    return payload["closure_ui_contract"]


def test_every_retained_family_is_a_local_proposal_without_authored_equality() -> None:
    atlas = derive_versioned_natural_form_atlas(
        truth_derivation={},
        interactive_translation={},
        active_perspective_id="perspective:test",
        active_reading={},
    )
    field = derive_local_natural_form_freedom(atlas)
    validation = validate_local_natural_form_freedom(field, atlas=atlas)

    family_ids = {row["family"] for row in field["families"]}
    assert set(STATIC_FAMILIES).issubset(family_ids)
    assert validation["valid"] is True
    assert field["local_constraint"][
        "all_retained_families_locally_admissible_as_proposals"
    ] is True
    assert field["local_constraint"][
        "unwitnessed_family_selection_authors_truth"
    ] is False
    assert field["selection_freedom"]["selection_is_set_valued"] is True
    assert field["selection_freedom"]["selection_filters_families"] is False
    assert field["selection_freedom"]["future_resolution_guaranteed"] is False
    assert field["fidelity_profile"]["configured_threshold"] is None
    assert field["fidelity_profile"]["similarity_epsilon"] is None
    assert all(row["selection_executes_as_equality"] is False for row in field["families"])
    assert all(row["status"] == "OPEN" for row in field["families"])


def test_returned_interaction_changes_exact_fidelity_without_restricting_family_freedom(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    perspective = "perspective:local-freedom"

    with TestClient(app) as client:
        opened = client.get(
            "/supernet/interface",
            params={"perspective_id": perspective},
        ).json()["closure_ui_contract"]
        first = _interact(
            client,
            opened,
            "A returned source establishes the first local closure relation.",
        )
        second = _interact(
            client,
            first,
            "A second returned source refines the same local interaction history.",
        )

    opened_field = opened["local_natural_form_freedom"]
    first_field = first["local_natural_form_freedom"]
    second_field = second["local_natural_form_freedom"]

    assert opened_field["id"] != first_field["id"]
    assert first_field["id"] != second_field["id"]
    assert opened_field["fidelity_profile"]["runtime_state_count"] == 0
    assert first_field["fidelity_profile"]["runtime_state_count"] == 1
    assert second_field["fidelity_profile"]["runtime_state_count"] == 2

    required = set(STATIC_FAMILIES)
    for contract, field in ((opened, opened_field), (first, first_field), (second, second_field)):
        admissible = set(field["selection_freedom"]["admissible_family_ids"])
        assert required.issubset(admissible)
        assert field["selection_freedom"]["selection_is_set_valued"] is True
        assert field["selection_freedom"]["external_limit_authors_selection"] is False
        assert field["selection_freedom"]["configured_threshold_authors_selection"] is False
        assert field["selection_freedom"]["remaining_limits_are_open_selection_frontiers"] is True
        assert field["selection_freedom"]["later_return_may_resolve_open_frontier"] is True
        assert field["selection_freedom"]["future_resolution_guaranteed"] is False
        assert field["fidelity_profile"]["fidelity_authored_only_by_exact_returns"] is True
        assert contract["supernet_closure_certificate"]["supernet_closed"] is True
        assert contract["supernet_closure_certificate"][
            "local_natural_form_freedom_id"
        ] == field["id"]
        assert validate_ui_contract(contract)["valid"] is True

    # Interaction adds return evidence; it does not remove the historical
    # proposal families from the local constraint.
    assert required.issubset(
        set(second_field["selection_freedom"]["open_family_ids"])
        | set(second_field["selection_freedom"]["witnessed_family_ids"])
    )


def test_tampered_local_freedom_cannot_pass_interface_validation(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        contract = client.get(
            "/supernet/interface",
            params={"perspective_id": "perspective:tamper"},
        ).json()["closure_ui_contract"]

    forged = deepcopy(contract)
    forged["local_natural_form_freedom"]["selection_freedom"][
        "future_resolution_guaranteed"
    ] = True
    validation = validate_ui_contract(forged)
    assert validation["valid"] is False
    assert "local-natural-form-freedom:not-derived" in validation["atlas_errors"]
