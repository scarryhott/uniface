from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_natural_interface import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.interaction_closure import derive_interaction_closure


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "interaction-closure.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def live_closure(tmp_path: Path) -> dict:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        response = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": "I want to coordinate a community garden.",
                "authored_by": "harry",
                "perspective_id": "harry",
                "form_label": "intent",
                "metadata": {"black_mirror_offer": True},
            },
        )
        assert response.status_code == 200, response.text
        return response.json()["sense_receipt"]["visual_closure"]


def test_black_mirror_and_digital_gate_are_one_truth_surface(
    tmp_path: Path,
) -> None:
    closure = live_closure(tmp_path)
    interaction = closure["interaction_closure"]
    ui = closure["nrrf843_ui"]

    assert interaction["status"] == "WITNESSED"
    assert interaction["supernet_interaction_closed"] is True
    assert interaction["nrrf843_ui_id"] == ui["id"]
    assert interaction["unification_constraint"][
        "all_components_share_one_translational_truth"
    ] is True

    physical = interaction["black_mirror_physical_topology"]
    assert physical["kind"] == (
        "EVOLVING_SOURCE_PRESERVED_PERSPECTIVE_TOPOLOGY"
    )
    assert physical["active_perspective_id"] == "harry"
    assert physical["closure_formula"] == "uiClosure(r,A) = r⁻¹(r(A))"
    assert physical["topology_basis"]
    assert physical["nodes"]
    assert physical["evolution_frames"]
    assert physical["static_external_map"] is False
    assert physical["physical_world_status"] == "OPEN_NO_PHYSICAL_SENSOR"

    digital = interaction["perspective_digital_potential_gate"]
    assert digital["status"] == "WITNESSED"
    assert digital["potential_count"] >= 1
    assert digital["open_potential_count"] >= 1
    assert all(
        item["remains_connected_potential"]
        for item in digital["potentials"]
    )
    assert all(
        item["executes_as_equality"] is False
        for item in digital["potentials"]
        if item["truth_constraint_status"] == "OPEN"
    )
    assert digital["ai_gate"]["can_bind"] is False
    assert digital["token_gate"]["gates_ordinary_interactions"] is False
    assert digital["independent_human_consent_required"] is True
    assert interaction["active_operation"]["ordinary_interaction"] is True
    assert interaction["active_operation"]["enabled"] is True


def test_nonmirror_ui_opens_the_entire_interaction_without_fallback(
    tmp_path: Path,
) -> None:
    closure = live_closure(tmp_path)
    ui = deepcopy(closure["nrrf843_ui"])
    ui["status"] = "OPEN_NON_MIRROR_UI"
    ui["translational_mirror"]["witnessed"] = False
    ui["truth_constraint_location"]["located"] = False
    receipt = derive_interaction_closure(
        truth_derivation=closure["translational_truth_axiometry"],
        nrrf843_ui=ui,
        nrrf842_journey=closure["nrrf842_journey"],
        coordination=closure["coordination"],
        ai_translation=closure["ai_translation"],
        tokenomic=closure["tokenomic"],
        visual_network=closure["visual_network"],
        black_mirror=closure["black_mirror"],
        network_return=closure["network_return"],
    )

    assert receipt["status"] == "OPEN"
    assert receipt["supernet_interaction_closed"] is False
    assert receipt["active_operation"]["enabled"] is False
    assert receipt["unification_constraint"]["checks"][
        "ui_translational_mirror_witnessed"
    ] is False
    assert receipt["unification_constraint"][
        "parallel_truth_runtime_present"
    ] is False
    assert receipt["perspective_digital_potential_gate"][
        "open_potential_executes_as_equality"
    ] is False
