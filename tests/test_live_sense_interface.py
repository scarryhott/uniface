from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_natural_interface import create_app
from closure_supernet.config import RuntimeConfig


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "live-sense.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def test_public_interaction_runs_existing_formal_pipeline_without_autonomy(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        first = client.post(
            "/supernet/integrate",
            json={
                "exact_text": "ball hair translational source",
                "authored_by": "person-a",
                "form_label": "note",
                "perspective_id": "person-a",
            },
        )
        assert first.status_code == 200, first.text
        first_payload = first.json()
        assert first_payload["sense_receipt"]["formal_pipeline_reused"] is True
        assert first_payload["sense_receipt"]["background_autonomy_required"] is False
        assert first_payload["sense_receipt"]["candidate_relation_ids"] == []
        assert first_payload["sense_receipt"]["truth_issued"] is False

        second = client.post(
            "/supernet/integrate",
            json={
                "exact_text": "ball hair translational source",
                "authored_by": "person-b",
                "form_label": "note",
                "perspective_id": "person-b",
            },
        )
        assert second.status_code == 200, second.text
        payload = second.json()
        sense = payload["sense_receipt"]
        assert len(sense["candidate_relation_ids"]) == 1
        assert len(sense["relation_receipts"]) == 1
        relation = sense["relation_receipts"][0]
        assert relation["relation_type"] == "SAME_LITERAL_EQUATION"
        assert relation["verdict"] == "TRUE"
        assert sense["selection_reading"]["evaluation"]["state"] == "NATURAL_SELECTION"
        assert sense["selection_reading"]["evaluation"]["natural_selection"] is True
        assert sense["translation_ids"]
        assert sense["truth_issued"] is False

        interface = client.get(
            "/supernet/interface",
            params={"focus_event_id": payload["event_id"]},
        )
        assert interface.status_code == 200, interface.text
        ui = interface.json()
        assert ui["natural_chart"]["kind"] == "OPEN_SELECTOR"
        assert ui["natural_chart"]["title"] == "Natural relation selected"
        assert ui["sense_depth"]["natural_selection"] is True
        assert ui["sense_depth"]["formal_pipeline_reused"] is True
        assert any(
            source["exact_text"] == "ball hair translational source"
            for source in ui["source_fibre"]
        )


def test_interact_runs_sense_on_the_new_child_and_preserves_parent_lineage(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        parent = client.post(
            "/supernet/integrate",
            json={
                "exact_text": "point line loop return",
                "authored_by": "person-a",
                "form_label": "note",
            },
        ).json()
        interaction = client.post(
            f"/supernet/events/{parent['event_id']}/interact",
            json={
                "exact_text": "point line loop return",
                "authored_by": "person-b",
                "form_label": "interaction",
            },
        )
        assert interaction.status_code == 200, interaction.text
        payload = interaction.json()
        assert payload["sense_receipt"]["candidate_relation_ids"]
        child = client.get(
            f"/supernet/events/{payload['event_id']}"
        ).json()
        assert parent["event_id"] in child["parent_event_ids"]


def test_live_sense_capabilities_are_exposed_on_the_primary_ui(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        capabilities = client.get("/supernet/interface/capabilities")
        assert capabilities.status_code == 200
        payload = capabilities.json()
        assert payload["live_sense"]["interaction_time_sense"] is True
        assert payload["live_sense"]["uses_existing_understanding_agent"] is True
        assert payload["live_sense"]["uses_existing_nrrf790_selector"] is True
        assert payload["live_sense"]["background_autonomy_required"] is False
        assert payload["single_complete_operational_surface"] is True
        assert payload["core_action_requires_subsystem_page"] is False
        assert payload["nrrf837_continuum_on_primary_surface"] is True
        assert payload["versioned_unity_selector_is_extra_data"] is True
        assert payload["unity_selector_network_derived"] is False
        assert payload["modality_idempotence_checked"] is True
        assert payload["global_equality_kernel_exposed"] is True
        assert payload["global_equality_kernel_uses_only_truth_derived_compose"] is True
        assert payload["authored_form_ids_define_equality"] is False
        assert payload["actual_ui_render_state_factorized_through_closure"] is True
        assert payload["external_renderer_has_no_semantic_fallback"] is True
        assert payload["open_candidates_change_slearn_truth_memory"] is False
        assert payload["live_sense"]["open_candidates_change_slearn_truth_memory"] is False
        assert payload["freedom_fibre_exposed"] is True
        assert payload["content_equality_preserves_actor_identity"] is True
        assert payload["partial_consent_natural_form"] == "COMMIT"
        assert app.version == "3.17.0"
