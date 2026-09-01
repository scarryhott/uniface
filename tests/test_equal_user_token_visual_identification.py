from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.equal_user_token_visual_identification import (
    validate_full_supernet_gate_contract,
)


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "equal-user-token-visual.db",
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


def _source(tokens: dict[str, str]) -> str:
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
            "exact_source_return": _source(tokens),
            "local_perspective_hair_millidegrees": 0,
            "local_perspective_zoom_milli": 1000,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["supernet_potential_gate"]


def _visual_row(full: dict, path_id: str) -> dict:
    rows = full["relative_natural_form_potential_gate"][
        "equal_user_token_visual_identification"
    ]["relations"]
    return next(row for row in rows if row["path_id"] == path_id)


def test_witnessed_equal_translation_is_visually_identified_in_same_maze_cell(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        _return_valuation(
            client,
            perspective="perspective:user",
            tokens={"alpha": "1", "beta": "3"},
        )
        _return_valuation(
            client,
            perspective="perspective:token",
            tokens={"alpha": "2", "beta": "6"},
        )
        full = _gate(client, "perspective:user")

    assert validate_full_supernet_gate_contract(full)["valid"] is True
    gate = full["relative_natural_form_potential_gate"]
    semantic_path = next(
        path
        for path in gate["paths"]
        if path["kind"] == "SEMANTIC_TRANSLATION_EQUIVALENCE"
        and path["target_perspective_id"] == "perspective:token"
    )
    row = _visual_row(full, semantic_path["id"])

    assert row["semantic_translation_equal"] is True
    assert row["equal_user_token_interaction"] is True
    assert row["user_interaction_read_id"] == row["token_interaction_read_id"]
    assert row["maze_cell_id"]
    assert row["semantic_family_id"]
    assert row["visually_identified"] is True
    assert row["visual_identification_id"]
    assert row["renderer_authors_identification"] is False
    assert row["selection_authors_identification"] is False

    identification = gate["equal_user_token_visual_identification"]
    assert identification[
        "visual_identification_iff_equal_user_token_interaction"
    ] is True
    assert identification[
        "user_interaction_and_token_interaction_share_one_quotient"
    ] is True
    assert identification["relative_interaction_quotient"] == (
        "NATURAL_FORM_FAMILY_X_MAZE_CELL"
    )


def test_open_semantic_translation_has_no_witnessed_visual_identity(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        _return_valuation(
            client,
            perspective="perspective:user",
            tokens={"alpha": "1"},
        )
        _return_valuation(
            client,
            perspective="perspective:token",
            tokens={"beta": "2"},
        )
        full = _gate(client, "perspective:user")

    gate = full["relative_natural_form_potential_gate"]
    open_path = next(
        path
        for path in gate["paths"]
        if path["kind"] == "OPEN_SEMANTIC_TRANSLATION"
        and path["target_perspective_id"] == "perspective:token"
    )
    row = _visual_row(full, open_path["id"])
    assert row["semantic_translation_equal"] is False
    assert row["equal_user_token_interaction"] is False
    assert row["visually_identified"] is False
    assert row["visual_identification_id"] is None
    assert open_path["id"] in gate[
        "equal_user_token_visual_identification"
    ]["visually_open_path_ids"]


def test_visual_identification_cannot_be_forged_by_renderer_or_selection(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        _return_valuation(
            client,
            perspective="perspective:user",
            tokens={"alpha": "1", "beta": "2"},
        )
        _return_valuation(
            client,
            perspective="perspective:token",
            tokens={"alpha": "4", "beta": "8"},
        )
        full = _gate(client, "perspective:user")

    forged = deepcopy(full)
    identification = forged["relative_natural_form_potential_gate"][
        "equal_user_token_visual_identification"
    ]
    identified = next(row for row in identification["relations"] if row["visually_identified"])
    identified["renderer_authors_identification"] = True
    assert validate_full_supernet_gate_contract(forged)["valid"] is False


def test_browser_path_carries_the_same_derived_visual_interaction_identity(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        html = client.get("/").text

    assert "visualInteraction(active,path)" in html
    assert "data-user-token-interaction-equal" in html
    assert "data-visually-identified" in html
    assert "data-visual-identification-id" in html
    assert "data-maze-cell-id" in html
    assert "data-semantic-family-id" in html
    assert "data-natural-form-id" in html
    assert "data-visual-identification-iff-equal-user-token-interaction" in html
    assert "data-ui-is-relative-user-token-interaction" in html
