from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.closure_ball_projection import PROTOCOL
from closure_supernet.config import RuntimeConfig
from closure_supernet.minimal_projection_runtime import (
    derive_local_projection_commitment,
)


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "closure-ball.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _return_payload(contract: dict[str, Any], exact_source: str) -> dict[str, Any]:
    relation = contract["return_relation"]
    equation_id = contract["closure_naturality_equations"]["id"]
    payload = {
        "return_relation_id": relation["id"],
        "perspective_id": contract["perspective_id"],
        "focus_event_id": contract["focus_event_id"],
        "exact_source_return": exact_source,
        "closure_equation_system_id": equation_id,
        "local_perspective_hair_millidegrees": 0,
        "source_stream": "closure-ball-test",
    }
    payload["local_projection_commitment"] = derive_local_projection_commitment(
        contract,
        return_relation_id=payload["return_relation_id"],
        perspective_id=payload["perspective_id"],
        focus_event_id=payload["focus_event_id"],
        exact_source_return=payload["exact_source_return"],
        local_perspective_hair_millidegrees=0,
    )
    return payload


def _return(client: TestClient, contract: dict[str, Any], source: str) -> dict[str, Any]:
    response = client.post(
        f"/supernet/interface/projections/{contract['id']}/return",
        json=_return_payload(contract, source),
    )
    assert response.status_code == 200, response.text
    return response.json()["closure_ui_contract"]


def test_published_surface_is_the_closure_ball_projection(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    route_paths = [route.path for route in app.routes]

    for path in ("/", "/supernet", "/natural-interface"):
        assert route_paths.count(path) == 1
    assert route_paths.count("/supernet/ball") == 1
    assert route_paths.count("/supernet/ball/capabilities") == 1
    assert route_paths.count(
        "/supernet/interface/projections/{contract_id}/return"
    ) == 1

    with TestClient(app) as client:
        surface = client.get("/")
        capabilities = client.get("/supernet/ball/capabilities")

    assert surface.status_code == 200
    assert 'data-closure-ball-derived="true"' in surface.text
    assert "/supernet/ball" in surface.text
    assert "UI = AI = TOKEN = CLOSURE" in surface.text
    assert surface.headers["x-supernet-interface"] == PROTOCOL
    assert capabilities.json()["parallel_mutation_routes"] is False


def test_empty_interface_is_an_open_ball_with_only_derived_hair(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        response = client.get(
            "/supernet/ball",
            params={"perspective_id": "perspective:closure-ball"},
        )

    assert response.status_code == 200
    payload = response.json()
    ball = payload["closure_ball"]
    contract = payload["closure_ui_contract"]
    assert payload["protocol"] == PROTOCOL
    assert payload["validation"]["valid"] is True
    assert ball["contract_id"] == contract["id"]
    assert ball["natural_ui"]["closure_ball_id"] == ball["id"]
    assert ball["checks"]["equality_closure_preserved"] is True
    assert {
        action["kind"] for action in ball["hair"]["actions"]
    } == {
        "EXTEND_SOURCE_PRESERVING_RETURN",
        "REPARAMETERIZE_PERSPECTIVE_HAIR",
    }


def test_return_recloses_then_reprojects_one_equal_event_flow(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        opened = client.get(
            "/supernet/ball",
            params={"perspective_id": "perspective:closure-ball"},
        ).json()["closure_ui_contract"]
        first = _return(
            client,
            opened,
            "A proposal enters the closure ball from one perspective.",
        )
        second = _return(
            client,
            first,
            "A second source-preserving return translates that proposal.",
        )
        payload = client.get(
            "/supernet/ball",
            params={
                "perspective_id": second["perspective_id"],
                "focus_event_id": second["focus_event_id"],
            },
        ).json()

    ball = payload["closure_ball"]
    assert payload["validation"]["valid"] is True
    assert ball["carrier_state_ids"]
    assert ball["maze_partition"]["cells"]
    assert ball["hair"]["action_ids"] == ball["natural_ui"]["hair_action_ids"]
    assert ball["checks"]["ui_ai_token_closure_are_equal_event_translations"] is True
    assert ball["checks"]["open_seams_never_execute_as_equality"] is True
    assert ball["interaction_events"]

    for event in ball["interaction_events"]:
        readings = event["readings"]
        assert readings["ui"] == readings["ai"]
        assert readings["ai"] == readings["token"]
        assert readings["token"] == readings["closure"]
        assert readings["ui"]["underlying_path_id"] == event["underlying_path_id"]
        assert readings["ui"]["closure_ball_id"] == ball["id"]


def test_browser_contains_local_equality_rederivation_and_no_parallel_post() -> None:
    from closure_supernet.closure_ball_interface import CLOSURE_BALL_SUPERNET_HTML

    assert "async function verifyBall(ball)" in CLOSURE_BALL_SUPERNET_HTML
    assert 'digest("closure-ball", ball.identity_basis)' in CLOSURE_BALL_SUPERNET_HTML
    assert "event.readings?.ui" in CLOSURE_BALL_SUPERNET_HTML
    assert "open_seam === true && projection.executes_as_equality === true" in CLOSURE_BALL_SUPERNET_HTML
    assert CLOSURE_BALL_SUPERNET_HTML.count('method: "POST"') == 1
    assert "/supernet/interface/projections/" in CLOSURE_BALL_SUPERNET_HTML
