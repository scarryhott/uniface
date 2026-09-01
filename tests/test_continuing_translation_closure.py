from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.continuing_closure_full_gate import (
    validate_full_supernet_gate_contract,
)


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "continuing-closure.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _gate(client: TestClient, perspective_id: str = "perspective:continuing") -> dict:
    response = client.get(
        "/supernet/interface",
        params={"perspective_id": perspective_id, "potential_gate": True},
    )
    assert response.status_code == 200, response.text
    return response.json()["supernet_potential_gate"]


def test_published_closure_has_only_returned_and_continuing_states(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        full = _gate(client)

    validation = validate_full_supernet_gate_contract(full)
    assert validation["valid"] is True, validation
    assert full["published_relation_states"] == ["RETURNED", "CONTINUING"]
    assert full["legacy_status_vocabulary_is_compatibility_only"] is True
    assert full["closure_is_continuation_of_all"] is True
    assert full["nonreturned_does_not_mean_outside_closure"] is True

    gate = full["relative_natural_form_potential_gate"]
    continuum = gate["continuing_translation_closure"]
    assert continuum["continuation_is_inside_closure"] is True
    assert continuum["closure_contains_every_current_translation"] is True
    assert continuum["closure_contains_every_current_natural_form_family"] is True
    assert continuum["returned_is_determination_not_membership"] is True
    assert continuum["relation_count"] == len(gate["paths"])

    relation_ids = {row["id"] for row in continuum["relations"]}
    returned_ids = set(continuum["returned_relation_ids"])
    continuing_ids = set(continuum["continuing_relation_ids"])
    assert returned_ids.isdisjoint(continuing_ids)
    assert returned_ids | continuing_ids == relation_ids
    assert all(
        row["closure_state"] in {"RETURNED", "CONTINUING"}
        and row["returned"] is not row["continuing"]
        for row in continuum["relations"]
    )
    assert all(
        row["closure_state"] in {"RETURNED", "CONTINUING"}
        and row["returned"] is not row["continuing"]
        for row in continuum["natural_form_families"]
    )
    # The canonical continuum itself contains no legacy OPEN ontology.
    assert "OPEN" not in json.dumps(continuum, sort_keys=True)


def test_a_return_refines_the_same_closure_family_instead_of_creating_closure(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        before = _gate(client, "perspective:return-continuation")
        continuum = before["relative_natural_form_potential_gate"][
            "continuing_translation_closure"
        ]
        relation = next(row for row in continuum["relations"] if row["continuing"])
        response = client.post(
            f"/supernet/interface/projections/{before['id']}/return",
            json={
                "interaction_kind": "POTENTIAL_GATE_RETURN",
                "relation_id": relation["path_id"],
                "perspective_id": before["perspective_id"],
                "focus_event_id": before["focus_event_id"],
                "navigation_context": before["navigation_context"],
                "exact_source_return": "a returned continuation inside one closure",
                "local_perspective_hair_millidegrees": 0,
                "local_perspective_zoom_milli": 1000,
            },
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["returned"] is True
        after = payload["supernet_potential_gate"]

    assert after["closure_is_continuation_of_all"] is True
    assert after["continuing_translation_closure_id"] != before[
        "continuing_translation_closure_id"
    ]
    assert after["truth_invariant_id"] != before["truth_invariant_id"]
    after_continuum = after["relative_natural_form_potential_gate"][
        "continuing_translation_closure"
    ]
    assert after_continuum["return_refines_determination"] is True
    assert after_continuum["continuation_is_inside_closure"] is True
    assert "OPEN" not in json.dumps(after_continuum, sort_keys=True)
    validation = validate_full_supernet_gate_contract(after)
    assert validation["valid"] is True, validation


def test_browser_uses_continuum_state_for_interaction(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/")
        capabilities = client.get("/supernet/interface/capabilities").json()

    assert page.status_code == 200
    html = page.text
    assert "continuing_translation_closure" in html
    assert "continuumRelation(active,path)" in html
    assert 'data-closure-is-continuation-of-all' in html
    assert 'data-published-relation-states' in html
    assert 'data-continuing' in html
    assert '.gate-path[data-status="RETURNED"]' in html
    assert '.gate-path[data-status="CONTINUING"]' in html
    assert '.gate-path[data-status="OPEN"]' not in html
    assert capabilities["closure_semantics"] == (
        "CONTINUING_FAMILY_OF_TRANSLATIONAL_TRUTH"
    )
    assert capabilities["published_relation_states"] == ["RETURNED", "CONTINUING"]
    assert capabilities["continuation_is_inside_closure"] is True
    assert capabilities["closure_has_external_nonclosure_region"] is False
    assert capabilities["return_changes_determination_not_membership"] is True
    assert capabilities["legacy_status_vocabulary_is_compatibility_only"] is True
