from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_natural_interface import create_app
from closure_supernet.closure_ui_contract import (
    BLOCKED_STATUS,
    OPEN_STATUS,
    SCHEMA,
    WITNESSED_STATUS,
    derive_closure_ui_contract,
    validate_ui_contract,
)
from closure_supernet.config import RuntimeConfig


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "closure-only-ui.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def walk(node: dict) -> list[dict]:
    return [
        node,
        *[
            descendant
            for child in node.get("children", [])
            for descendant in walk(child)
        ],
    ]


def open_values(
    *,
    thought: str,
    author: str = "harry",
    kind: str = "intent",
) -> dict[str, str]:
    return {
        "author": author,
        "perspective": author,
        "coordination_kind": kind,
        "location": "Berkeley, California",
        "thought": thought,
    }


def execution_payload(
    contract: dict,
    *,
    action_id: str,
    values: dict[str, str],
) -> dict:
    """Carry only the closure contract's authored execution context."""

    return {
        "action_id": action_id,
        "perspective_id": contract["perspective_id"],
        "focus_event_id": contract["focus_event_id"],
        "values": values,
    }


def test_empty_surface_is_the_complete_open_perspective_contract(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/")
        interface = client.get(
            "/supernet/interface", params={"perspective_id": "harry"}
        ).json()

    body_before_program = page.text.split("<body>", 1)[1].split(
        "<script>", 1
    )[0].strip()
    assert body_before_program == (
        '<main id="closure-contract-root" '
        "data-closure-only-contract></main>"
    )
    for tag in ("<button", "<input", "<textarea", "<select", "<svg", "<h1"):
        assert tag not in body_before_program
    for route in (
        "/supernet/interface/offer",
        "/supernet/interface/intents",
        "/supernet/interface/commitments",
        "/supernet/interface/selections",
        "/supernet/interface/collective",
    ):
        assert route not in page.text
    assert "innerHTML" not in page.text
    assert "localStorage" not in page.text
    assert "prompt(" not in page.text
    assert "validateContract" in page.text

    contract = interface["closure_ui_contract"]
    assert contract["schema"] == SCHEMA
    assert contract["status"] == OPEN_STATUS
    assert contract["perspective_id"] == "harry"
    assert contract["claims"]["natural_form_admitted"] is False
    assert contract["execution"]["source_boundary_actions_only"] is True
    assert [item["id"] for item in contract["action_bindings"]] == [
        "offer-source"
    ]
    nodes = walk(contract["root"])
    assert {item["id"] for item in nodes if item["kind"] in {
        "input", "textarea", "select"
    }} == {
        "author",
        "perspective",
        "coordination_kind",
        "location",
        "thought",
    }
    assert all(
        item["derivation"]["basis"]
        == "OPEN_AUTHORED_PERSPECTIVE_SOURCE_BOUNDARY"
        for item in nodes
    )
    assert validate_ui_contract(contract)["valid"] is True


def test_contract_executor_derives_the_successor_and_rejects_client_semantics(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        first_page = client.get("/").text
        contract = client.get(
            "/supernet/interface", params={"perspective_id": "harry"}
        ).json()["closure_ui_contract"]
        values = open_values(thought="I want to start a community garden.")
        executed = client.post(
            f"/supernet/interface/contracts/{contract['id']}/execute",
            json=execution_payload(
                contract,
                action_id="offer-source",
                values=values,
            ),
        )
        assert executed.status_code == 200, executed.text
        payload = executed.json()
        successor = payload["closure_ui_contract"]
        visual = payload["interface"]["visual_closure"]

        assert payload["status"] == "EXECUTED"
        assert payload["executed"] is True
        assert successor["status"] == WITNESSED_STATUS
        assert successor == visual["closure_ui_contract"]
        assert successor == visual["interface_natural_form"]["render_state"][
            "closure_ui_contract"
        ]
        assert successor["closure_derivation_id"] == visual[
            "translational_truth_axiometry"
        ]["id"]
        assert successor["visual_closure_id"] == visual[
            "translational_truth_axiometry"
        ]["visual_truth_closure"]["id"]
        assert successor["nrrf843_ui_id"] == visual["nrrf843_ui"]["id"]
        assert successor["interaction_closure_id"] == visual[
            "interaction_closure"
        ]["id"]
        assert visual["unified_truth_runtime"][
            "closure_ui_contract_id"
        ] == successor["id"]
        assert validate_ui_contract(successor)["valid"] is True
        assert all(
            item["derivation"]["closure_derivation_id"]
            == successor["closure_derivation_id"]
            for item in walk(successor["root"])
        )
        assert client.get("/").text == first_page

        event_count = len(
            app.state.runtime.supernet_store.list_events(limit=100_000)
        )
        repeated = client.post(
            f"/supernet/interface/contracts/{contract['id']}/execute",
            json=execution_payload(
                contract,
                action_id="offer-source",
                values=values,
            ),
        )
        assert repeated.status_code == 200, repeated.text
        assert repeated.json()["replayed"] is True
        assert repeated.json()["result"]["event_id"] == payload["result"][
            "event_id"
        ]
        assert len(
            app.state.runtime.supernet_store.list_events(limit=100_000)
        ) == event_count

        changed_open = client.post(
            f"/supernet/interface/contracts/{contract['id']}/execute",
            json=execution_payload(
                contract,
                action_id="offer-source",
                values=open_values(
                    thought="An old source boundary cannot author twice."
                ),
            ),
        )
        assert changed_open.status_code == 409, changed_open.text
        assert changed_open.json()["status"] == "STALE_CONTRACT"
        assert len(
            app.state.runtime.supernet_store.list_events(limit=100_000)
        ) == event_count

        altered_schema = client.post(
            f"/supernet/interface/contracts/{successor['id']}/execute",
            json=execution_payload(
                successor,
                action_id="continue-local-interaction",
                values={
                    key: value
                    for key, value in open_values(
                        thought="Invite neighbors to plan the first meeting."
                    ).items()
                    if key != "location"
                },
            ),
        )
        assert altered_schema.status_code == 400
        unknown_action = client.post(
            f"/supernet/interface/contracts/{successor['id']}/execute",
            json=execution_payload(
                successor,
                action_id="invent-external-action",
                values=open_values(thought="This must not execute."),
            ),
        )
        assert unknown_action.status_code == 400
        client_route = client.post(
            f"/supernet/interface/contracts/{successor['id']}/execute",
            json={
                **execution_payload(
                    successor,
                    action_id="continue-local-interaction",
                    values=open_values(thought="This must not execute."),
                ),
                "endpoint": "https://example.invalid",
            },
        )
        assert client_route.status_code == 422

        mismatched_values = client.post(
            f"/supernet/interface/contracts/{successor['id']}/execute",
            json=execution_payload(
                successor,
                action_id="continue-local-interaction",
                values=open_values(
                    thought="This cannot escape the active perspective.",
                    author="mallory",
                ),
            ),
        )
        assert mismatched_values.status_code == 400

        missing_context = client.post(
            f"/supernet/interface/contracts/{successor['id']}/execute",
            json={
                "action_id": "continue-local-interaction",
                "values": open_values(thought="No authored context."),
            },
        )
        assert missing_context.status_code == 422

        tampered = deepcopy(successor)
        tampered["action_bindings"][0]["operation"] = "DELETE_EXTERNAL_STATE"
        tampered["action_bindings"][0]["endpoint"] = "https://example.invalid"
        validation = validate_ui_contract(tampered)
        assert validation["valid"] is False
        assert validation["closure_only_execution"] is False


def test_non_mirror_truth_constraint_produces_no_semantic_fallback(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        created = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": "A source-preserved perspective.",
                "authored_by": "person-a",
                "perspective_id": "person-a",
                "form_label": "intent",
                "coordination_kind": "intent",
            },
        ).json()
        interface = client.get(
            "/supernet/interface",
            params={"focus_event_id": created["event_id"]},
        ).json()

    visual = interface["visual_closure"]
    non_mirror = deepcopy(visual["nrrf843_ui"])
    non_mirror["status"] = "OPEN_NON_MIRROR_UI"
    non_mirror["translational_mirror"]["witnessed"] = False
    non_mirror["truth_constraint_location"]["located"] = False
    blocked = derive_closure_ui_contract(
        truth_derivation=visual["translational_truth_axiometry"],
        nrrf843_ui=non_mirror,
        nrrf842_journey=visual["nrrf842_journey"],
        interaction_closure=visual["interaction_closure"],
        coordination=visual["coordination"],
        visual_network=visual["visual_network"],
        source_occurrences=visual["interface_natural_form"]["render_state"][
            "source_fibre"
        ],
        focus_event=interface["focus_event"],
        field_event_seq=visual["closure_ui_contract"]["field_event_seq"],
    )
    assert blocked["status"] == BLOCKED_STATUS
    assert blocked["root"]["visible"] is False
    assert blocked["action_bindings"] == []
    assert blocked["execution"]["allowed_action_ids"] == []
    assert blocked["renderer_contract"]["semantic_fallback"] is False
    assert validate_ui_contract(blocked)["valid"] is True


def test_closure_only_contract_carries_proposal_and_independent_consent(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        collaborator = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": (
                    "Maya can help organize a Berkeley community garden "
                    "on weekends."
                ),
                "authored_by": "maya",
                "perspective_id": "maya",
                "form_label": "garden collaborator",
                "coordination_kind": "person",
                "location_label": "Berkeley, California",
                "relation_hints": ["community garden", "Berkeley"],
            },
        )
        assert collaborator.status_code == 200, collaborator.text
        open_contract = client.get(
            "/supernet/interface", params={"perspective_id": "harry"}
        ).json()["closure_ui_contract"]
        intent = client.post(
            f"/supernet/interface/contracts/{open_contract['id']}/execute",
            json=execution_payload(
                open_contract,
                action_id="offer-source",
                values=open_values(
                    thought="I want to start a Berkeley community garden."
                ),
            ),
        )
        assert intent.status_code == 200, intent.text
        intent_contract = intent.json()["closure_ui_contract"]
        proposal_action = next(
            item
            for item in intent_contract["action_bindings"]
            if item["operation"] == "PROPOSE_AGREEMENT"
        )
        target_id = proposal_action["immutable"][
            "allowed_target_event_ids"
        ][0]
        proposed = client.post(
            f"/supernet/interface/contracts/{intent_contract['id']}/execute",
            json=execution_payload(
                intent_contract,
                action_id=proposal_action["id"],
                values={
                    "author": "harry",
                    "perspective": "harry",
                    "proposal_target": target_id,
                    "proposal_title": "Community garden agreement",
                    "proposal_terms": (
                        "Harry and Maya may plan together only after each "
                        "separately accepts these exact terms."
                    ),
                    "proposal_resources": "weekends only",
                },
            ),
        )
        assert proposed.status_code == 200, proposed.text
        consent_contract = proposed.json()["closure_ui_contract"]
        operations = {
            item["operation"] for item in consent_contract["action_bindings"]
        }
        assert "DECIDE_AGREEMENT" in operations
        assert "RETURN_AGREEMENT" not in operations
        assert {
            item["immutable"].get("decision")
            for item in consent_contract["action_bindings"]
            if item["operation"] == "DECIDE_AGREEMENT"
        } == {"ACCEPT", "REJECT", "WITHDRAW"}
        assert validate_ui_contract(consent_contract)["valid"] is True

        maya_interface = client.get(
            "/supernet/interface",
            params={
                "focus_event_id": consent_contract["focus_event_id"],
                "perspective_id": "maya",
            },
        ).json()
        maya_contract = maya_interface["closure_ui_contract"]
        assert maya_contract["status"] == WITNESSED_STATUS
        assert maya_contract["perspective_id"] == "maya"
        assert maya_contract["id"] != consent_contract["id"]
        assert validate_ui_contract(maya_contract)["valid"] is True
        maya_render = maya_interface["visual_closure"][
            "interface_natural_form"
        ]["render_state"]
        assert maya_render["closure_ui_contract"] == maya_contract
        maya_form = maya_interface["visual_closure"][
            "interface_natural_form"
        ]
        assert maya_form["render_state_factorized"] is True
        assert all(
            payload["render_state"]["closure_ui_contract"] == maya_contract
            for payload in maya_form["closure_projection"].values()
        )
        assert all(
            payload["render_state"]["closure_ui_contract"] == maya_contract
            for payload in maya_form["quotient_render_state"].values()
        )
        maya_fields = {
            item["id"]: item
            for item in walk(maya_contract["root"])
            if item["kind"] in {"input", "textarea", "select"}
        }
        assert maya_fields["decision_participant"]["value"] == "maya"
        field_by_id = {
            item["id"]: item
            for item in walk(consent_contract["root"])
            if item["kind"] in {"input", "textarea", "select"}
        }
        decision_values = {
            "decision_participant": field_by_id[
                "decision_participant"
            ]["value"],
            "perspective": "harry",
            "decision_text": "I separately accept these exact terms.",
            "decision_resources": "",
            "decision_constraints": "",
        }
        accepted = client.post(
            f"/supernet/interface/contracts/{consent_contract['id']}/execute",
            json=execution_payload(
                consent_contract,
                action_id="decide-accept",
                values=decision_values,
            ),
        )
        assert accepted.status_code == 200, accepted.text
        assert accepted.json()["closure_ui_contract"]["id"] != (
            consent_contract["id"]
        )
        completed_retry = client.post(
            f"/supernet/interface/contracts/{consent_contract['id']}/execute",
            json=execution_payload(
                consent_contract,
                action_id="decide-accept",
                values=decision_values,
            ),
        )
        assert completed_retry.status_code == 200, completed_retry.text
        assert completed_retry.json()["replayed"] is True
        changed_retry = client.post(
            f"/supernet/interface/contracts/{consent_contract['id']}/execute",
            json=execution_payload(
                consent_contract,
                action_id="decide-accept",
                values={
                    **decision_values,
                    "decision_text": "A changed stale decision must not execute.",
                },
            ),
        )
        assert changed_retry.status_code == 409
        assert changed_retry.json()["status"] == "STALE_CONTRACT"
        assert changed_retry.json()["executed"] is False


def test_wrong_focus_is_refused_before_sense_side_effects(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        first = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": "First witnessed source.",
                "authored_by": "harry",
                "perspective_id": "harry",
                "form_label": "intent",
                "coordination_kind": "intent",
            },
        ).json()
        second = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": "Second witnessed source.",
                "authored_by": "maya",
                "perspective_id": "maya",
                "form_label": "project",
                "coordination_kind": "project",
            },
        ).json()
        contract = client.get(
            "/supernet/interface",
            params={
                "focus_event_id": first["event_id"],
                "perspective_id": "harry",
            },
        ).json()["closure_ui_contract"]
        unknown = client.get(
            "/supernet/interface",
            params={
                "focus_event_id": first["event_id"],
                "perspective_id": "unwitnessed-perspective",
            },
        ).json()
        assert unknown["closure_ui_contract"]["status"] == OPEN_STATUS
        assert unknown["visual_closure"] is None
        stage_count = len(
            app.state.runtime.supernet_store.list_stages(limit=100_000)
        )
        refused = client.post(
            f"/supernet/interface/contracts/{contract['id']}/execute",
            json={
                **execution_payload(
                    contract,
                    action_id="continue-local-interaction",
                    values=open_values(thought="Must not run against another focus."),
                ),
                "focus_event_id": second["event_id"],
            },
        )
        assert refused.status_code == 409, refused.text
        assert refused.json()["executed"] is False
        assert len(
            app.state.runtime.supernet_store.list_stages(limit=100_000)
        ) == stage_count

        third = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": "A later field event invalidates old contracts.",
                "authored_by": "river",
                "perspective_id": "river",
                "form_label": "resource",
                "coordination_kind": "resource",
            },
        )
        assert third.status_code == 200, third.text
        stage_count = len(
            app.state.runtime.supernet_store.list_stages(limit=100_000)
        )
        stale_field = client.post(
            f"/supernet/interface/contracts/{contract['id']}/execute",
            json=execution_payload(
                contract,
                action_id="continue-local-interaction",
                values=open_values(thought="This contract predates the field."),
            ),
        )
        assert stale_field.status_code == 409, stale_field.text
        assert stale_field.json()["refresh_required"] is True
        assert len(
            app.state.runtime.supernet_store.list_stages(limit=100_000)
        ) == stage_count
        refreshed = client.get(
            "/supernet/interface",
            params={
                "focus_event_id": first["event_id"],
                "perspective_id": "harry",
            },
        ).json()["closure_ui_contract"]
        assert refreshed["status"] == WITNESSED_STATUS
        assert refreshed["id"] != contract["id"]


def test_completed_witnessed_execution_replays_after_restart(
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    app = create_app(config)
    with TestClient(app) as client:
        open_contract = client.get(
            "/supernet/interface", params={"perspective_id": "harry"}
        ).json()["closure_ui_contract"]
        offered = client.post(
            f"/supernet/interface/contracts/{open_contract['id']}/execute",
            json=execution_payload(
                open_contract,
                action_id="offer-source",
                values=open_values(thought="A restart-safe source."),
            ),
        )
        assert offered.status_code == 200, offered.text
        witnessed = offered.json()["closure_ui_contract"]
        request_payload = execution_payload(
            witnessed,
            action_id="continue-local-interaction",
            values=open_values(thought="A restart-safe continuation."),
        )
        first = client.post(
            f"/supernet/interface/contracts/{witnessed['id']}/execute",
            json=request_payload,
        )
        assert first.status_code == 200, first.text
        first_payload = first.json()
    restarted = create_app(config)
    with TestClient(restarted) as client:
        event_count = len(
            restarted.state.runtime.supernet_store.list_events(
                limit=100_000
            )
        )
        replay = client.post(
            f"/supernet/interface/contracts/{witnessed['id']}/execute",
            json=request_payload,
        )
        assert replay.status_code == 200, replay.text
        assert replay.json()["replayed"] is True
        assert replay.json()["result"]["event_id"] == first_payload[
            "result"
        ]["event_id"]
        assert len(
            restarted.state.runtime.supernet_store.list_events(
                limit=100_000
            )
        ) == event_count


def test_field_revision_uses_authoritative_sequence_and_all_pages(
    tmp_path: Path,
    monkeypatch,
) -> None:
    app = create_app(make_config(tmp_path))
    store = app.state.runtime.supernet_store
    pages = {
        0: [{"id": "first", "seq": 200_000}],
        1: [{"id": "later", "seq": 200_001}],
        2: [],
    }
    monkeypatch.setattr(
        store,
        "list_events",
        lambda *, limit, offset=0: pages.get(offset, []),
    )
    monkeypatch.setattr(store, "latest_event_sequence", lambda: 200_001)

    events, revision = app.state.runtime.live_sense._field_events_snapshot(
        batch_size=1
    )

    assert [item["id"] for item in events] == ["first", "later"]
    assert revision == 200_001
