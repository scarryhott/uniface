from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.translation_supervisory_full_gate import (
    validate_full_supernet_gate_contract,
)
from closure_supernet.translation_supervisory_geometry import (
    cross_loss,
    determined_translation,
    normalize,
)


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "translation-supervision.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _gate(client: TestClient, perspective: str) -> dict:
    response = client.get(
        "/supernet/interface",
        params={"perspective_id": perspective, "potential_gate": True},
    )
    assert response.status_code == 200, response.text
    return response.json()["supernet_potential_gate"]


def _open_return_path(full: dict) -> dict:
    return next(
        path
        for path in full["relative_natural_form_potential_gate"]["paths"]
        if path["status"] != "WITNESSED"
        and path["action"] == "OPEN_RETURN_EXTENSION"
        and path["kind"] != "OPEN_SEMANTIC_TRANSLATION"
    )


def _semantic_source(tokens: dict[str, str]) -> str:
    return json.dumps(
        {"semantic_market_valuation": {"tokens": tokens}},
        sort_keys=True,
        separators=(",", ":"),
    )


def _return_valuation(
    client: TestClient,
    *,
    perspective: str,
    tokens: dict[str, str],
) -> dict:
    full = _gate(client, perspective)
    path = _open_return_path(full)
    response = client.post(
        f"/supernet/interface/projections/{full['id']}/return",
        json={
            "interaction_kind": "POTENTIAL_GATE_RETURN",
            "relation_id": path["id"],
            "perspective_id": perspective,
            "focus_event_id": full["focus_event_id"],
            "navigation_context": full["navigation_context"],
            "exact_source_return": _semantic_source(tokens),
            "local_perspective_hair_millidegrees": 0,
            "local_perspective_zoom_milli": 1000,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["returned"] is True
    return response.json()["supernet_potential_gate"]


def test_exact_translation_loss_and_normal_form_are_numeraire_invariant() -> None:
    left = {"a": "1", "b": "3/2", "c": "7"}
    right = {"a": "5", "b": "15/2", "c": "35"}
    scale, status, shared = determined_translation(left, right)

    assert str(scale) == "5"
    assert status == "WITNESSED"
    assert shared == ["a", "b", "c"]
    assert cross_loss(left, right) == "0"
    assert normalize(left) == normalize(right)


def test_no_shared_token_has_no_global_relative_position() -> None:
    scale, reason, shared = determined_translation(
        {"a": "1", "b": "2"},
        {"c": "3", "d": "4"},
    )
    assert scale is None
    assert reason == "NO_SHARED_TOKEN"
    assert shared == []
    assert cross_loss({"a": "1"}, {"b": "2"}) is None


def test_returned_translation_geometry_is_ai_token_and_navigation_geometry(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        _return_valuation(
            client,
            perspective="perspective:a",
            tokens={"alpha": "1", "beta": "3"},
        )
        _return_valuation(
            client,
            perspective="perspective:b",
            tokens={"alpha": "2", "beta": "6"},
        )
        at_a = _gate(client, "perspective:a")

        assert validate_full_supernet_gate_contract(at_a)["valid"] is True
        gate = at_a["relative_natural_form_potential_gate"]
        geometry = gate["translation_supervisory_geometry"]
        assert geometry["valuation_count"] == 2
        assert geometry["relation_count"] == 1
        relation = geometry["relations"][0]
        assert relation["status"] == "WITNESSED"
        assert relation["translation_scale"] == "2"
        assert relation["cross_loss"] == "0"
        assert relation["shared_token_ids"] == ["alpha", "beta"]
        assert relation["unique_relative_translation"] is True
        assert geometry["ai_supervision_equals_token_translation_geometry"] is True
        assert geometry[
            "observer_identity_comes_only_from_returned_event_provenance"
        ] is True

        semantic_path = next(
            path
            for path in gate["paths"]
            if path["kind"] == "SEMANTIC_TRANSLATION_EQUIVALENCE"
            and path["target_perspective_id"] == "perspective:b"
        )
        assert semantic_path["status"] == "WITNESSED"
        assert semantic_path["action"] == "PERSPECTIVE_TRANSPORT"
        assert semantic_path["translation_scale"] == "2"
        assert semantic_path["cross_loss"] == "0"
        assert not any(
            path["kind"] in {
                "PERSPECTIVE_TRANSLATION",
                "PERSPECTIVE_TRANSLATION_INVERSE",
            }
            and path.get("target_perspective_id") == "perspective:b"
            for path in gate["paths"]
        )

        response = client.post(
            f"/supernet/interface/projections/{at_a['id']}/return",
            json={
                "interaction_kind": "PERSPECTIVE_NAVIGATION",
                "relation_id": semantic_path["id"],
                "perspective_id": at_a["perspective_id"],
                "focus_event_id": at_a["focus_event_id"],
                "navigation_context": at_a["navigation_context"],
            },
        )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["navigated"] is True
    assert payload["truth_refined"] is False
    at_b = payload["supernet_potential_gate"]
    assert at_b["perspective_id"] == "perspective:b"
    assert at_b["truth_invariant_id"] == at_a["truth_invariant_id"]


def test_unshared_returned_perspectives_stay_open_and_generic_path_cannot_bypass(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        _return_valuation(
            client,
            perspective="perspective:a",
            tokens={"alpha": "1"},
        )
        _return_valuation(
            client,
            perspective="perspective:b",
            tokens={"beta": "1"},
        )
        at_a = _gate(client, "perspective:a")

    gate = at_a["relative_natural_form_potential_gate"]
    geometry = gate["translation_supervisory_geometry"]
    relation = geometry["relations"][0]
    assert relation["status"] != "WITNESSED"
    assert relation["reason"] == "NO_SHARED_TOKEN"
    assert relation["global_relative_position_determined"] is False
    assert relation["no_shared_token_excluded_from_family"] is True

    open_semantic = next(
        path
        for path in gate["paths"]
        if path["kind"] == "OPEN_SEMANTIC_TRANSLATION"
        and path["target_perspective_id"] == "perspective:b"
    )
    assert open_semantic["status"] != "WITNESSED"
    assert open_semantic["action"] == "OPEN_RETURN_EXTENSION"
    assert not any(
        path["kind"] in {
            "PERSPECTIVE_TRANSLATION",
            "PERSPECTIVE_TRANSLATION_INVERSE",
            "SEMANTIC_TRANSLATION_EQUIVALENCE",
        }
        and path.get("target_perspective_id") == "perspective:b"
        and path["status"] == "WITNESSED"
        for path in gate["paths"]
    )


def test_inconsistent_cross_relations_are_open_not_similarity_supervision(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        _return_valuation(
            client,
            perspective="perspective:a",
            tokens={"alpha": "1", "beta": "2"},
        )
        _return_valuation(
            client,
            perspective="perspective:b",
            tokens={"alpha": "2", "beta": "5"},
        )
        at_a = _gate(client, "perspective:a")

    relation = at_a["relative_natural_form_potential_gate"][
        "translation_supervisory_geometry"
    ]["relations"][0]
    assert relation["status"] != "WITNESSED"
    assert relation["reason"] == "INCONSISTENT_CROSS_RELATIONS"
    assert relation["cross_loss"] != "0"
    assert relation["similarity_authors_translation"] is False
    assert relation["absolute_numeraire_authors_translation"] is False
