from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.closure_ui_contract import validate_ui_contract
from closure_supernet.config import RuntimeConfig
from closure_supernet.natural_form_projection_runtime import (
    derive_local_projection_commitment,
)


OBSOLETE_NAMED_TEMPLATES = {
    "INTERBOUND_POLAR_RING_STRING",
    "DIMENSIONAL_TRIANGULARIZATION",
    "SEAM_FOLD_INVERSION",
    "REFINEMENT_SPIRAL_HIDDEN_PATH",
    "BALL_HAIR_RADIAL_FIELD",
    "MIRROR_ELLIPTIC_REFLECTION",
    "SHEAF_FIBRE_BUNDLE",
    "CURVATURE_LIGHTCONE_WARP",
    "AI_TOKEN_RETURN_FLOW",
    "DUAL_CONE_HORIZON",
}


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "natural-render.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _return_payload(contract: dict, source: str, *, relation_source_stream: str | None = None) -> dict:
    relation = contract["return_relation"]
    payload = {
        "return_relation_id": relation["id"],
        "perspective_id": contract["perspective_id"],
        "focus_event_id": contract["focus_event_id"],
        "exact_source_return": source,
        "closure_equation_system_id": contract["closure_naturality_equations"]["id"],
    }
    if relation_source_stream is not None:
        payload["source_stream"] = relation_source_stream
    payload["local_projection_commitment"] = derive_local_projection_commitment(
        contract,
        return_relation_id=payload["return_relation_id"],
        perspective_id=payload["perspective_id"],
        focus_event_id=payload["focus_event_id"],
        exact_source_return=payload["exact_source_return"],
    )
    return payload


def test_production_surface_is_the_interactive_natural_form_closure_itself(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/")
        opened = client.get(
            "/supernet/interface",
            params={"perspective_id": "perspective:natural-solver"},
        ).json()["closure_ui_contract"]

    assert page.status_code == 200
    html = page.text
    assert "data-supernet-equality-surface" in html
    assert "data-visible-is-interactive" in html
    assert "data-visible-equals-interaction" in html
    assert "data-same-object-visible-and-interactive" in html
    assert "data-legacy-renderer-substrate" in html
    assert 'data-legacy-renderer-substrate":"false"' in html
    assert ".closure-relation" in html
    assert "pointer-events:stroke" in html
    assert "activateRelation" in html
    assert "activateFibre" in html
    assert "RETURN_APERTURE" in html
    assert "natural-form-relation:" in html
    assert "solvePoint" in html
    assert "GENERIC_BOUNDED_HARMONIC_EQUALITY_CLOSURE_BASIS" in html
    assert "natural-form-family-layer" not in html
    assert "legacy renderer" not in html.lower()
    assert "switch (family)" not in html
    assert "naturalFormFamilyOperators" not in html
    for template in OBSOLETE_NAMED_TEMPLATES:
        assert template not in html

    # The authored page remains one blank physical relation aperture. The text
    # sensor is created by the same runtime only after a relation is entered.
    static_body = html.split("<body>", 1)[1].split("<script>", 1)[0].strip()
    assert static_body == '<main id="translational-mirror"></main>'
    assert 'document.createElement("textarea")' in html
    assert 'sensor.id = "return-sensor"' in html
    for control in ("<button", "<input", "<textarea", "<select", "<nav", "<form"):
        assert control not in static_body

    solver = opened["interactive_natural_form_solver"]
    assert solver["natural_form_is_interactive_interface_equality_closure"] is True
    assert solver["natural_form_is_posthoc_visual_template"] is False
    assert solver["family_switch_present"] is False
    assert solver["named_geometry_templates_present"] is False
    assert solver["rendering_can_witness_equality"] is False
    assert solver["solution_count"] == len(opened["local_natural_form_freedom"]["families"])
    assert opened["supernet_closure_certificate"]["interactive_natural_form_solver_id"] == solver["id"]
    assert opened["supernet_closure_certificate"]["supernet_closed"] is True
    assert validate_ui_contract(opened)["valid"] is True


def test_visible_open_relation_return_refines_the_same_closure_surface(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    perspective = "perspective:natural-solver-return"
    with TestClient(app) as client:
        opened = client.get(
            "/supernet/interface", params={"perspective_id": perspective}
        ).json()["closure_ui_contract"]
        selected_relation_id = opened["return_relation"]["id"]
        relation_source_stream = f"natural-form-relation:{selected_relation_id}"
        response = client.post(
            f"/supernet/interface/projections/{opened['id']}/return",
            json=_return_payload(
                opened,
                "The visible OPEN relation is itself the interaction aperture and returned closure path.",
                relation_source_stream=relation_source_stream,
            ),
        )
        assert response.status_code == 200, response.text
        successor = response.json()["closure_ui_contract"]

    assert response.json()["returned"] is True
    opened_solver = opened["interactive_natural_form_solver"]
    successor_solver = successor["interactive_natural_form_solver"]
    assert successor["id"] != opened["id"]
    assert successor_solver["id"] != opened_solver["id"]
    assert opened_solver["equality_closure_signature"]["state_count"] == 0
    assert successor_solver["equality_closure_signature"]["state_count"] == 1
    assert successor_solver["equality_closure_signature"]["source_return_ids"]

    opened_by_family = {row["family_id"]: row for row in opened_solver["solutions"]}
    successor_by_family = {row["family_id"]: row for row in successor_solver["solutions"]}
    assert set(opened_by_family).issubset(successor_by_family)
    assert successor_solver["solution_count"] >= opened_solver["solution_count"]
    assert any(
        successor_by_family[family]["coefficients"] != opened_by_family[family]["coefficients"]
        for family in opened_by_family
    )

    assert successor["supernet_closure_certificate"]["interactive_natural_form_solver_id"] == successor_solver["id"]
    assert successor["supernet_closure_certificate"]["supernet_closed"] is True
    assert successor_solver["rendering_can_witness_equality"] is False
    assert successor_solver["only_return_refines_equality_closure"] is True
    assert successor["natural_form_atlas"]["cross_form_equality_requires_returned_translation"] is True
    assert validate_ui_contract(successor)["valid"] is True
