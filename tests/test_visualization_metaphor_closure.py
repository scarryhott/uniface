from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.visualization_metaphor_closure import (
    derive_visualization_metaphor_closure,
    validate_full_supernet_gate_contract,
)


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "visualization-metaphor.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _synthetic_gate(*, same_natural_form: bool) -> dict:
    first_nf = "natural-form:alpha"
    second_nf = first_nf if same_natural_form else "natural-form:beta"
    relations = [
        {
            "path_id": "path:a",
            "closure_state": "RETURNED",
            "returned": True,
            "continuing": False,
            "maze_cell_id": "maze:a",
            "unitary_curvature_id": "curvature:a",
        },
        {
            "path_id": "path:b",
            "closure_state": "CONTINUING",
            "returned": False,
            "continuing": True,
            "maze_cell_id": "maze:b",
            "unitary_curvature_id": "curvature:b",
        },
    ]
    visual = [
        {
            "path_id": "path:a",
            "natural_form_id": first_nf,
            "semantic_family_id": "family:one",
        },
        {
            "path_id": "path:b",
            "natural_form_id": second_nf,
            "semantic_family_id": "family:one",
        },
    ]
    return {
        "relative_natural_form_potential_gate": {
            "continuing_translation_closure_id": "closure:continuum",
            "translation_supervisory_geometry_id": "geometry:translation",
            "continuing_translation_closure": {"relations": relations},
            "equal_user_token_visual_identification": {"relations": visual},
        }
    }


def test_seen_ignores_labels_renderer_hair_and_zoom() -> None:
    gate = _synthetic_gate(same_natural_form=True)
    first = derive_visualization_metaphor_closure(gate)

    relabelled = deepcopy(gate)
    relabelled["relative_natural_form_potential_gate"]["presentation"] = {
        "label": "a completely different metaphor",
        "svg_path": "M 3 7 C 9 11 13 17 19 23",
        "hair_millidegrees": 127000,
        "zoom_milli": 73000,
    }
    second = derive_visualization_metaphor_closure(relabelled)

    assert first["seen_id"] == second["seen_id"]
    assert first["metaphor_class_id"] == second["metaphor_class_id"]
    assert first["seen_fold_class_ids"] == second["seen_fold_class_ids"]
    assert first["labels_author_metaphor_equality"] is False
    assert first["renderer_coordinates_author_metaphor_equality"] is False
    assert first["hair_authors_metaphor_equality"] is False
    assert first["zoom_authors_metaphor_equality"] is False


def test_same_natural_form_currents_share_one_visualization_crystal_ball() -> None:
    visualization = derive_visualization_metaphor_closure(
        _synthetic_gate(same_natural_form=True)
    )
    currents = visualization["currents"]

    assert len(currents) == 2
    assert currents[0]["fold_class_id"] == currents[1]["fold_class_id"]
    assert currents[0]["rotation_class_id"] == currents[1]["rotation_class_id"]
    assert currents[0]["crystal_ball_id"] == currents[1]["crystal_ball_id"]
    assert len(visualization["seen_fold_class_ids"]) == 1
    assert len(visualization["crystal_balls"]) == 1
    assert visualization["crystal_ball_is_master_supernet_ontology"] is False
    assert visualization["crystal_ball_is_local_visualization_chart"] is True


def test_distinct_natural_forms_are_distinct_seen_fold_classes() -> None:
    visualization = derive_visualization_metaphor_closure(
        _synthetic_gate(same_natural_form=False)
    )
    currents = visualization["currents"]

    assert currents[0]["fold_class_id"] != currents[1]["fold_class_id"]
    assert currents[0]["crystal_ball_id"] != currents[1]["crystal_ball_id"]
    assert len(visualization["seen_fold_class_ids"]) == 2
    assert len(visualization["crystal_balls"]) == 2


def test_published_gate_carries_seen_metaphor_and_runtime_boundary(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        response = client.get(
            "/supernet/interface",
            params={"perspective_id": "perspective:seen", "potential_gate": True},
        )
        page = client.get("/")
        capabilities = client.get("/supernet/interface/capabilities").json()

    assert response.status_code == 200, response.text
    full = response.json()["supernet_potential_gate"]
    assert validate_full_supernet_gate_contract(full)["valid"] is True

    gate = full["relative_natural_form_potential_gate"]
    metaphor = gate["visualization_metaphor_closure"]
    assert full["seen_id"] == gate["seen_id"] == metaphor["seen_id"]
    assert full["metaphor_class_id"] == gate["metaphor_class_id"]
    assert full["visual_equality_is_seen_equality"] is True
    assert full["proof_by_visualization_uses_metaphor_equality"] is True
    assert metaphor["runtime_reproves_lean"] is False
    assert metaphor["formal_source_verified_by_runtime"] is False
    assert metaphor["analytic_tan_limit_claimed"] is False

    html = page.text
    assert "visualization_metaphor_closure" in html
    assert "SEEN_ID_EQUALITY" in html
    assert "data-seen-id" in html
    assert "data-metaphor-class-id" in html
    assert "data-crystal-ball-id" in html
    assert "data-fold-class-id" in html
    assert "data-labels-author-visual-equality" in html
    assert capabilities["visual_equality"] == "SEEN_ID_EQUALITY"
    assert capabilities["proof_by_visualization"] == "METAPHOR_EQUALITY"
    assert capabilities["crystal_ball_is_master_supernet_ontology"] is False
    assert capabilities["runtime_reproves_nrrf885"] is False
