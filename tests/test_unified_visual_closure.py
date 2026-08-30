from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_natural_interface import create_app
from closure_supernet.config import RuntimeConfig


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "unified-visual-closure.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def offer(client: TestClient, actor: str) -> dict:
    response = client.post(
        "/supernet/interface/offer",
        json={
            "exact_text": "One live occurrence translates through the shared closure field.",
            "authored_by": actor,
            "perspective_id": actor,
            "form_label": "live signal",
            "metadata": {"black_mirror_offer": True},
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_one_sense_executes_and_persists_all_visual_closure_functions(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        first = offer(client, "person-a")
        first_closure = first["sense_receipt"]["visual_closure"]
        assert first_closure["closure_relation"] == [
            "BLACK_MIRROR_SENSE",
            "SLEARN_MEMORY",
            "AI_TRANSLATION",
            "TOKENOMIC_ADMISSION",
            "VISUAL_CLOSURE",
            "NETWORK_RETURN",
            "BLACK_MIRROR_SENSE",
        ]
        assert all(first_closure["operational_closure"].values())
        assert first_closure["black_mirror"]["source_preserved"] is True
        assert first_closure["black_mirror"]["physical_sensor_status"] == "OPEN"
        assert first_closure["tokenomic"]["currency_issued"] is False
        assert first_closure["tokenomic"]["resource_unit_count"] == 1
        assert first_closure["network_return"]["next_operation"]["action"] == "interact"
        assert first_closure["truth_issued"] is False

        second = offer(client, "person-b")
        closure = second["sense_receipt"]["visual_closure"]
        assert closure["black_mirror"]["exact_source_occurrence_ids"]
        assert closure["ai_translation"]["relations"]
        assert closure["ai_translation"]["admitted_relation_ids"]
        assert closure["ai_translation"]["selection_state"] == "NATURAL_SELECTION"
        assert closure["tokenomic"]["resource_unit_count"] == 1
        assert closure["tokenomic"]["resource_units"][0]["member_event_ids"]
        assert closure["visual_network"]["nodes"]
        assert closure["visual_network"]["edges"]
        assert closure["visual_network"]["closure_level_endpoint"] == "⊤"
        assert closure["network_return"]["next_operation"]["action"] == "return"
        assert closure["network_return"]["next_operation"]["user_selected_phase"] is False
        assert closure["two_person_E2E"] == "OPEN"
        assert closure["truth_issued"] is False

        interface = client.get(
            "/supernet/interface",
            params={"focus_event_id": second["event_id"]},
        )
        assert interface.status_code == 200, interface.text
        interface_body = interface.json()
        assert interface_body["visual_closure"]["id"] == closure["id"]
        assert interface_body["sense_depth"][
            "all_desired_functions_in_occurrence"
        ] is True

        persisted = client.get(
            f"/supernet/events/{second['event_id']}/visual-closure"
        )
        assert persisted.status_code == 200, persisted.text
        assert persisted.json()["id"] == closure["id"]
        assert len(client.get("/supernet/visual-closure/receipts").json()) == 2

        default_interface = client.get("/supernet/interface")
        assert default_interface.status_code == 200, default_interface.text
        default_body = default_interface.json()
        assert default_body["focus_event"]["id"] == second["event_id"]
        assert default_body["visual_closure"]["id"] == closure["id"]

        third = offer(client, "person-c")
        learned = third["sense_receipt"]["visual_closure"]["slearn"]
        assert learned["relation_memory_before"]["SAME_LITERAL_EQUATION"] >= 1
        assert learned["memory_influence"]["SAME_LITERAL_EQUATION"] >= 1


def test_return_and_reopen_change_the_derived_network_operation(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        source = offer(client, "person-a")
        event_id = source["event_id"]

        returned = client.post(
            f"/supernet/events/{event_id}/return",
            json={
                "actor_id": "person-a",
                "exact_text": "The live field returns a new consequence.",
                "form_label": "returned signal",
            },
        )
        assert returned.status_code == 200, returned.text
        returned_sense = client.post(f"/supernet/events/{event_id}/sense")
        assert returned_sense.status_code == 200, returned_sense.text
        return_closure = returned_sense.json()["visual_closure"]
        assert return_closure["network_return"]["current_stage"] == "RETURNED"
        assert return_closure["network_return"]["next_operation"]["action"] == "reopen"

        reopened = client.post(
            f"/supernet/events/{event_id}/reopen",
            json={
                "actor_id": "person-a",
                "reason": "The returned consequence is the next open Sense.",
            },
        )
        assert reopened.status_code == 200, reopened.text
        reopened_sense = client.post(f"/supernet/events/{event_id}/sense")
        assert reopened_sense.status_code == 200, reopened_sense.text
        reopen_closure = reopened_sense.json()["visual_closure"]
        assert reopen_closure["id"] != return_closure["id"]
        assert return_closure["id"] in reopen_closure["parent_receipt_ids"]
        assert reopen_closure["network_return"]["current_stage"] == "REOPENED"
        assert reopen_closure["network_return"]["next_operation"]["action"] == "interact"


def test_primary_canvas_is_the_unified_network_ui_not_a_component_selector(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "drawUnifiedClosure" in page.text
        assert "closureContinue" in page.text
        assert "Visual translational closure" in page.text
        assert "fieldKind" not in page.text
        assert 'type="range"' not in page.text

        capabilities = client.get("/supernet/interface/capabilities").json()
        assert capabilities[
            "slearn_black_mirror_ai_tokenomic_visual_closure"
        ] is True
        assert capabilities["primary_surface_component_selector"] is False
        assert capabilities[
            "tokenomic_units_derived_from_equality_classes"
        ] is True


def test_resource_unit_keeps_source_capabilities_and_constraints_when_relations_add_events(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        first = client.post(
            "/supernet/sense",
            json={
                "exact_text": "Garden telemetry: 0↔∞; moisture 18; irrigation off.",
                "authored_by": "simulated-sensor-a",
                "form_label": "simulated garden telemetry",
                "capabilities": ["sense:soil-moisture"],
                "constraints": ["water_budget_liters<=2"],
                "metadata": {"simulation": True, "physical_claim": False},
            },
        )
        assert first.status_code == 200, first.text

        second = client.post(
            "/supernet/sense",
            json={
                "exact_text": "Garden telemetry: 0 <-> infinity; moisture 22; irrigation on.",
                "authored_by": "simulated-sensor-b",
                "form_label": "simulated garden telemetry",
                "capabilities": ["sense:soil-moisture", "actuate:irrigation"],
                "constraints": ["remaining_water_liters<=1"],
                "metadata": {"simulation": True, "physical_claim": False},
            },
        )
        assert second.status_code == 200, second.text
        closure = second.json()["sense_receipt"]["visual_closure"]

        assert closure["ai_translation"]["relations"][0]["relation_type"] == (
            "NOTATIONAL_VARIANT"
        )
        assert closure["ai_translation"]["relations"][0]["verdict"] == "OPEN"
        unit = closure["tokenomic"]["resource_units"][0]
        assert unit["capabilities"] == [
            "actuate:irrigation",
            "sense:soil-moisture",
        ]
        assert unit["constraints"] == [
            "remaining_water_liters<=1",
            "water_budget_liters<=2",
        ]
        assert set(unit["member_event_ids"]) == {
            first.json()["event_id"],
            second.json()["event_id"],
        }
        contributions = {
            item["authored_by"]: item for item in unit["member_contributions"]
        }
        assert contributions["simulated-sensor-a"]["capabilities"] == [
            "sense:soil-moisture"
        ]
        assert contributions["simulated-sensor-a"]["constraints"] == [
            "water_budget_liters<=2"
        ]
        assert contributions["simulated-sensor-b"]["capabilities"] == [
            "sense:soil-moisture",
            "actuate:irrigation",
        ]
        assert contributions["simulated-sensor-b"]["constraints"] == [
            "remaining_water_liters<=1"
        ]
