from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app as create_projection_app
from closure_supernet.closure_ui_contract import (
    OPEN_STATUS,
    PROTOCOL,
    RETURN_ENDPOINT_TEMPLATE,
    SCHEMA,
    WITNESSED_STATUS,
    validate_ui_contract,
)
from closure_supernet.config import RuntimeConfig


def make_config(
    tmp_path: Path,
    *,
    environment: str = "test",
    projection_only_mode: bool = False,
) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "closure-only-ui.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment=environment,
        projection_only_mode=projection_only_mode,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def return_payload(contract: dict[str, Any], exact_source: str) -> dict[str, Any]:
    relation = contract["return_relation"]
    return {
        "return_relation_id": relation["id"],
        "perspective_id": contract["perspective_id"],
        "focus_event_id": contract["focus_event_id"],
        "exact_source_return": exact_source,
    }


def execute_return(
    client: TestClient,
    contract: dict[str, Any],
    exact_source: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    response = client.post(
        RETURN_ENDPOINT_TEMPLATE.format(contract_id=contract["id"]),
        json=return_payload(contract, exact_source),
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    return payload, payload["closure_ui_contract"]


def assert_equality_fibres_partition_projection(contract: dict[str, Any]) -> None:
    projection = contract["projection"]
    states = {state["id"]: state for state in projection["states"]}
    member_counts = Counter(
        member
        for fibre in projection["equality_fibres"]
        for member in fibre["member_state_ids"]
    )

    assert member_counts == Counter({state_id: 1 for state_id in states})
    assert set(projection["reading"]) == set(states)
    for state_id, state in states.items():
        assert projection["reading"][state_id] == state["display_fibre_id"]
    for fibre in projection["equality_fibres"]:
        displays = {
            projection["reading"][state_id]
            for state_id in fibre["member_state_ids"]
        }
        assert displays == set(fibre["display_fibre_ids"])
        assert fibre["closure_fixed"] is True


def test_open_projection_has_no_authored_page_or_substitute_content(
    tmp_path: Path,
) -> None:
    app = create_projection_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/")
        receipt = client.get(
            "/supernet/interface",
            params={"perspective_id": "perspective:harry"},
        ).json()

    static_body = page.text.split("<body>", 1)[1].split("<script>", 1)[0].strip()
    assert static_body == '<main id="translational-mirror"></main>'
    for visible_element in (
        "<button",
        "<input",
        "<textarea",
        "<select",
        "<h1",
        "<nav",
        "<form",
    ):
        assert visible_element not in static_body
    assert "localStorage" not in page.text
    assert "prompt(" not in page.text

    assert set(receipt) == {"closure_ui_contract"}
    contract = receipt["closure_ui_contract"]
    assert contract["protocol"] == PROTOCOL
    assert contract["schema"] == SCHEMA
    assert contract["status"] == OPEN_STATUS
    assert contract["perspective_id"] == "perspective:harry"
    assert contract["projection"]["states"] == []
    assert contract["projection"]["equality_fibres"] == []
    assert contract["projection"]["translations"] == []
    assert contract["projection"]["potentials"] == []
    assert contract["projection"]["reading"] == {}
    assert contract["natural_form_ids"] == []
    assert contract["source_return_ids"] == []
    assert contract["claims"]["natural_form_admitted"] is False

    relation = contract["return_relation"]
    assert relation["kind"] == "SOURCE_PRESERVING_TRANSLATIONAL_RETURN"
    assert relation["full_surface_aperture"] is True
    assert relation["visible_control"] is False
    assert relation["requires_exact_source_return"] is True
    assert relation["creates_truth_directly"] is False
    assert contract["execution"]["return_relation_id"] == relation["id"]
    assert contract["execution"]["only_relation_extension"] is True
    assert contract["renderer_relation"]["fixed_visible_controls"] == []
    assert contract["renderer_relation"]["authored_visible_vocabulary"] == []
    assert contract["renderer_relation"]["fallback_visuals"] == []
    for removed_app_layer in (
        "root",
        "scene",
        "action_bindings",
        "fields",
        "theme",
        "layout",
        "controls",
    ):
        assert removed_app_layer not in contract
    assert validate_ui_contract(contract)["valid"] is True


def test_universal_return_derives_the_only_visible_source_and_successor_closure(
    tmp_path: Path,
) -> None:
    app = create_projection_app(make_config(tmp_path))
    exact_source = "I want to start a community garden with my neighbors."

    with TestClient(app) as client:
        open_contract = client.get(
            "/supernet/interface",
            params={"perspective_id": "perspective:harry"},
        ).json()["closure_ui_contract"]
        payload, successor = execute_return(client, open_contract, exact_source)

    assert payload["status"] == "RETURNED"
    assert payload["returned"] is True
    assert payload["replayed"] is False
    assert payload["truth_issued"] is False
    assert "result" not in payload
    assert "interface" not in payload
    assert "action" not in payload

    assert successor["status"] == WITNESSED_STATUS
    assert successor["focus_event_id"] == payload["focus_event_id"]
    assert successor["claims"]["natural_form_admitted"] is True
    assert successor["claims"]["truth_issued"] is False
    assert {state["source_trace"] for state in successor["projection"]["states"]} == {
        exact_source
    }
    assert all(
        state["source_return_ids"]
        and state["natural_form_id"] in successor["natural_form_ids"]
        for state in successor["projection"]["states"]
    )
    assert successor["renderer_relation"]["visible_words_source"] == (
        "SOURCE_RETURNS_ONLY"
    )
    assert successor["renderer_relation"]["authored_visible_vocabulary"] == []
    assert successor["return_relation"]["kind"] == (
        "SOURCE_PRESERVING_TRANSLATIONAL_RETURN"
    )
    assert_equality_fibres_partition_projection(successor)
    visualization = successor["projection"]["visualization"]
    assert visualization["operator"] == "PERSPECTIVE_RELATION_PROJECTIVE_FOLD"
    assert visualization["axiometry"]["finite_pole"] == 0
    assert visualization["axiometry"]["projective_seam"] == (
        "tan(pi/2)=infinity"
    )
    assert len(visualization["fibre_primitives"]) == len(
        successor["projection"]["equality_fibres"]
    )

    validation = validate_ui_contract(successor)
    assert validation["valid"] is True
    assert validation["every_visible_word_is_a_source_return"] is True
    assert validation["equality_fibres_partition_visible_states"] is True
    assert validation["active_reading_determines_projection"] is True


def test_each_return_recloses_one_carrier_and_preserves_exact_source_traces(
    tmp_path: Path,
) -> None:
    app = create_projection_app(make_config(tmp_path))
    first_source = "First exact source return."
    second_source = "Second exact source return; no action category selected."

    with TestClient(app) as client:
        open_contract = client.get(
            "/supernet/interface", params={"perspective_id": "perspective:one"}
        ).json()["closure_ui_contract"]
        _, first = execute_return(client, open_contract, first_source)
        _, second = execute_return(client, first, second_source)

    assert second["id"] != first["id"]
    assert second["field_event_seq"] > first["field_event_seq"]
    assert {state["source_trace"] for state in second["projection"]["states"]} == {
        first_source,
        second_source,
    }
    assert_equality_fibres_partition_projection(second)
    # The second source was returned through the focused first fibre.  The UI
    # interaction itself therefore supplies the equal visual reading; no text
    # classifier or separate action is allowed to merge it afterward.
    assert len(second["projection"]["equality_fibres"]) == 1
    assert len(set(second["projection"]["reading"].values())) == 1
    for relation in second["projection"]["translations"]:
        if relation["executes_as_equality"]:
            reading = second["projection"]["reading"]
            assert relation["relation_status"] == WITNESSED_STATUS
            assert reading[relation["source_state_id"]] == reading[
                relation["target_state_id"]
            ]
    assert validate_ui_contract(second)["valid"] is True


def test_server_rejects_action_vocab_and_noncurrent_return_relation(
    tmp_path: Path,
) -> None:
    app = create_projection_app(make_config(tmp_path))
    with TestClient(app) as client:
        contract = client.get(
            "/supernet/interface", params={"perspective_id": "perspective:one"}
        ).json()["closure_ui_contract"]
        event_count = len(app.state.runtime.ledger.list_returns())

        invented_action = client.post(
            RETURN_ENDPOINT_TEMPLATE.format(contract_id=contract["id"]),
            json={
                **return_payload(contract, "The source return itself."),
                "action_id": "BUY_NOW",
                "values": {"price": "100"},
            },
        )
        assert invented_action.status_code == 422

        wrong_relation = client.post(
            RETURN_ENDPOINT_TEMPLATE.format(contract_id=contract["id"]),
            json={
                **return_payload(contract, "The source return itself."),
                "return_relation_id": "return-relation:invented",
            },
        )
        assert wrong_relation.status_code == 400
        assert len(app.state.runtime.ledger.list_returns()) == event_count


def test_replay_is_idempotent_and_changed_return_against_old_projection_is_stale(
    tmp_path: Path,
) -> None:
    app = create_projection_app(make_config(tmp_path))
    exact_source = "One source, one return, one successor."
    with TestClient(app) as client:
        contract = client.get(
            "/supernet/interface", params={"perspective_id": "perspective:one"}
        ).json()["closure_ui_contract"]
        endpoint = RETURN_ENDPOINT_TEMPLATE.format(contract_id=contract["id"])
        request = return_payload(contract, exact_source)
        first = client.post(endpoint, json=request)
        assert first.status_code == 200, first.text
        event_count = len(app.state.runtime.ledger.list_returns())

        replay = client.post(endpoint, json=request)
        assert replay.status_code == 200, replay.text
        assert replay.json()["replayed"] is True
        assert replay.json()["focus_event_id"] == first.json()["focus_event_id"]
        assert replay.json()["closure_ui_contract"] == first.json()[
            "closure_ui_contract"
        ]
        assert len(app.state.runtime.ledger.list_returns()) == event_count

        changed = client.post(
            endpoint,
            json=return_payload(contract, "A different source needs the successor."),
        )
        assert changed.status_code == 409, changed.text
        assert changed.json()["status"] == "STALE_CONTRACT"
        assert changed.json()["returned"] is False
        assert len(app.state.runtime.ledger.list_returns()) == event_count


def test_contract_content_and_provenance_tampering_are_rejected(
    tmp_path: Path,
) -> None:
    app = create_projection_app(make_config(tmp_path))
    with TestClient(app) as client:
        open_contract = client.get(
            "/supernet/interface", params={"perspective_id": "perspective:one"}
        ).json()["closure_ui_contract"]
        _, contract = execute_return(client, open_contract, "Exact source witness.")

    forged_source = deepcopy(contract)
    forged_source["projection"]["states"][0]["source_trace"] = (
        "Interface-authored substitute."
    )
    forged_source_validation = validate_ui_contract(forged_source)
    assert forged_source_validation["valid"] is False
    assert forged_source_validation["contract_id_matches_content"] is False
    assert forged_source_validation["stored_audit_matches_recomputation"] is False

    forged_provenance = deepcopy(contract)
    forged_provenance["projection"]["states"][0]["derivation"][
        "source_return_ids"
    ] = ["source-return:not-in-the-carrier"]
    provenance_validation = validate_ui_contract(forged_provenance)
    assert provenance_validation["valid"] is False
    assert provenance_validation["all_visual_existence_has_exact_derivation"] is False
    assert any(
        error.endswith(":source-returns")
        for error in provenance_validation["errors"]
    )

    forged_reading = deepcopy(contract)
    state = forged_reading["projection"]["states"][0]
    forged_reading["projection"]["reading"][state["id"]] = "display:external"
    reading_validation = validate_ui_contract(forged_reading)
    assert reading_validation["valid"] is False
    assert reading_validation["active_reading_determines_projection"] is False

    forged_geometry = deepcopy(contract)
    forged_geometry["projection"]["visualization"]["fibre_primitives"][0][
        "centre"
    ] = [12, 34]
    geometry_validation = validate_ui_contract(forged_geometry)
    assert geometry_validation["valid"] is False
    assert "visualization:not-exact-projection" in geometry_validation["errors"]


def test_production_exposes_only_projection_return_and_runtime_health(
    tmp_path: Path,
) -> None:
    app = create_projection_app(
        make_config(
            tmp_path,
            environment="production",
            projection_only_mode=True,
        )
    )
    expected_paths = {
        "/",
        "/supernet",
        "/natural-interface",
        "/supernet/interface",
        "/supernet/interface/capabilities",
        "/supernet/interface/projections/{contract_id}/return",
        "/livez",
        "/readyz",
    }
    assert {str(route.path) for route in app.router.routes} == expected_paths

    with TestClient(app) as client:
        root = client.get("/")
        assert root.status_code == 200
        assert client.get("/supernet").text == root.text
        assert client.get("/natural-interface").text == root.text
        assert client.get(
            "/supernet/interface",
            params={"perspective_id": "perspective:production"},
        ).status_code == 200
        for removed_surface in (
            "/docs",
            "/openapi.json",
            "/mcp",
            "/trading",
            "/supernet/integrate",
            "/supernet/interface/offer",
            "/supernet/interface/intents",
            "/supernet/interface/commitments",
            "/supernet/interface/selections",
            "/supernet/interface/collective",
        ):
            assert client.get(removed_surface).status_code == 404


def test_published_runtime_closes_returns_through_the_selected_visual_fibre(
    tmp_path: Path,
) -> None:
    app = create_projection_app(
        make_config(
            tmp_path,
            environment="production",
            projection_only_mode=True,
        )
    )
    with TestClient(app) as client:
        initial = client.get(
            "/supernet/interface", params={"perspective_id": "perspective:live"}
        ).json()["closure_ui_contract"]
        first_payload, first = execute_return(
            client, initial, "A living community garden."
        )
        replay = client.post(
            RETURN_ENDPOINT_TEMPLATE.format(contract_id=initial["id"]),
            json=return_payload(initial, "A living community garden."),
        )
        assert replay.status_code == 200
        assert replay.json()["replayed"] is True
        assert replay.json()["focus_event_id"] == first_payload["focus_event_id"]
        _, second = execute_return(
            client,
            first,
            "Neighbors, tools, land, and a shared agreement.",
        )

    assert first["status"] == second["status"] == WITNESSED_STATUS
    assert len(second["projection"]["states"]) == 2
    assert len(second["projection"]["equality_fibres"]) == 1
    assert len(set(second["projection"]["reading"].values())) == 1
    assert validate_ui_contract(second)["valid"] is True
