from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_natural_interface import create_app
from closure_supernet.config import RuntimeConfig


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "completed-black-mirror.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def test_primary_surface_contains_no_required_core_navigation(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200
        text = page.text
        static_body = text.split("<script>", 1)[0]
        assert "data-closure-only-contract" in static_body
        assert "validateContract" in text
        assert "action_bindings" in text
        assert "Live relational field" not in text
        assert "fieldKind" not in text
        assert "drawUnifiedClosure" not in text
        assert "closureContinue" not in text
        assert "/supernet/interface/offer" not in text
        assert "/supernet/interface/intents" not in text
        assert "/supernet/interface/commitments" not in text
        assert "/supernet/interface/selections" not in text
        assert "/supernet/interface/collective" not in text
        for tag in ("<button", "<input", "<textarea", "<select", "<svg", "<h1"):
            assert tag not in static_body

        contract = client.get("/supernet/interface").json()[
            "closure_ui_contract"
        ]
        assert contract["status"] == "OPEN_SOURCE_BOUNDARY"
        assert [item["id"] for item in contract["action_bindings"]] == [
            "offer-source"
        ]
        assert contract["execution"]["source_boundary_actions_only"] is True
        assert contract["audit"]["closure_only_execution"] is True

        caps = client.get("/supernet/interface/capabilities").json()
        assert caps["single_complete_operational_surface"] is True
        assert caps["core_action_requires_subsystem_page"] is False
        assert caps["perspective_carried_by_primary_composer"] is True
        assert caps["eight_sheaf_entry_on_primary_surface"] is True
        assert caps["primary_surface_component_selector"] is False
        assert caps["slearn_black_mirror_ai_tokenomic_visual_closure"] is True
        assert caps["truth_issued_by_presentation"] is False
        assert caps["closure_only_ui_contract"] is True
        assert caps["hardcoded_visible_ui_instances"] is False
        assert caps["primary_browser_client_authored_action_routes"] is False


def test_offer_sense_selection_and_collective_share_one_event_field(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        first = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": "A participant learns through a shared Black Mirror relation.",
                "authored_by": "person-a",
                "form_label": "learning interaction",
                "perspective_id": "person-a",
                "sheaf": "SLEARN_PERSPECTIVE",
            },
        )
        assert first.status_code == 200, first.text
        first_payload = first.json()
        first_id = first_payload["event_id"]
        assert first_payload["lens"] == "embodied"
        assert first_payload["sheaf"] == "SLEARN_PERSPECTIVE"
        assert first_payload["sense_receipt"]["formal_pipeline_reused"] is True
        assert first_payload["truth_issued"] is False

        first_event = client.get(f"/supernet/events/{first_id}").json()
        assert first_event["adapter_label"] == "embodied"
        assert first_event["perspective_id"] == "person-a"
        assert "person-a" in first_event["affected_perspectives"]
        assert first_event["metadata"]["sheaf"] == "SLEARN_PERSPECTIVE"

        first_ui = client.get(
            "/supernet/interface", params={"focus_event_id": first_id}
        ).json()
        assert any(
            source["exact_text"]
            == "A participant learns through a shared Black Mirror relation."
            for source in first_ui["source_fibre"]
        )

        second = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": "A participant learns through a shared Black Mirror relation.",
                "authored_by": "person-b",
                "form_label": "learning interaction",
                "perspective_id": "person-b",
                "sheaf": "HUMAN_INTERACTION",
            },
        )
        assert second.status_code == 200, second.text
        second_payload = second.json()
        second_id = second_payload["event_id"]
        sense = second_payload["sense_receipt"]
        assert sense["candidate_relation_ids"]
        assert sense["selection_reading"]["evaluation"]["natural_selection"] is True
        candidate = sense["admissible_relation_ids"][0]

        selection = client.post(
            "/supernet/interface/selections",
            json={
                "source_event_id": second_id,
                "selected_relation_id": candidate,
                "authored_by": "person-b",
                "perspective_id": "person-b",
            },
        )
        assert selection.status_code == 200, selection.text
        selected = selection.json()
        assert selected["evaluation"]["state"] == "NATURAL_SELECTION"
        assert selected["evaluation"]["forced_isolation"] is False
        assert selected["metadata"]["removed_alternatives_retained"] is True

        collective = client.post(
            "/supernet/interface/collective",
            json={
                "event_ids": [first_id, second_id],
                "exact_text": "Two perspectives return one shared trajectory without becoming identical.",
                "authored_by": "person-a",
                "perspective_id": "person-a",
                "affected_perspectives": ["person-a", "person-b"],
            },
        )
        assert collective.status_code == 200, collective.text
        collective_payload = collective.json()
        assert collective_payload["focus_event_id"]
        assert collective_payload["sense_receipt"]["formal_pipeline_reused"] is True
        assert collective_payload["truth_issued"] is False

        field = client.get("/supernet/field").json()
        ids = {event["id"] for event in field["events"]}
        assert first_id in ids
        assert second_id in ids
        assert collective_payload["focus_event_id"] in ids
        assert field["subsystems_are_lenses"] is True
