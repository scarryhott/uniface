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


def _return_payload(contract: dict, source: str) -> dict:
    relation = contract["return_relation"]
    payload = {
        "return_relation_id": relation["id"],
        "perspective_id": contract["perspective_id"],
        "focus_event_id": contract["focus_event_id"],
        "exact_source_return": source,
        "closure_equation_system_id": contract["closure_naturality_equations"]["id"],
    }
    payload["local_projection_commitment"] = derive_local_projection_commitment(
        contract,
        return_relation_id=payload["return_relation_id"],
        perspective_id=payload["perspective_id"],
        focus_event_id=payload["focus_event_id"],
        exact_source_return=payload["exact_source_return"],
    )
    return payload


def test_production_surface_solves_natural_forms_from_equality_closure(
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
    assert "INTERACTIVE_EQUALITY_CLOSURE_SOLVER" in html
    assert "deriveInteractiveEqualityClosureSignature" in html
    assert "deriveInteractiveNaturalFormSolver" in html
    assert "interactiveNaturalFormSolverMatches" in html
    assert "solveNaturalFormPoint" in html
    assert "GENERIC_BOUNDED_HARMONIC_EQUALITY_CLOSURE_BASIS" in html
    assert "data-natural-form-is-interface-equality-closure" in html
    assert "data-rendering-can-witness-equality" in html
    assert "switch (family)" not in html
    assert "naturalFormFamilyOperators" not in html
    for template in OBSOLETE_NAMED_TEMPLATES:
        assert template not in html

    # The renderer remains one blank authored surface: there is no menu through
    # which a developer or user can select a geometry as truth.
    static_body = html.split("<body>", 1)[1].split("<script>", 1)[0].strip()
    assert static_body == '<main id="translational-mirror"></main>'
    for control in ("<button", "<select", "<nav", "<form"):
        assert control not in static_body

    solver = opened["interactive_natural_form_solver"]
    assert solver["natural_form_is_interactive_interface_equality_closure"] is True
    assert solver["natural_form_is_posthoc_visual_template"] is False
    assert solver["family_switch_present"] is False
    assert solver["named_geometry_templates_present"] is False
    assert solver["family_name_authors_geometry"] is False
    assert solver["rendering_can_witness_equality"] is False
    assert solver["solution_count"] == len(
        opened["local_natural_form_freedom"]["families"]
    )
    assert opened["supernet_closure_certificate"][
        "interactive_natural_form_solver_id"
    ] == solver["id"]
    assert opened["supernet_closure_certificate"]["supernet_closed"] is True
    assert validate_ui_contract(opened)["valid"] is True


def test_return_refines_the_closure_and_resolves_a_new_natural_form_solution(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    perspective = "perspective:natural-solver-return"
    with TestClient(app) as client:
        opened = client.get(
            "/supernet/interface", params={"perspective_id": perspective}
        ).json()["closure_ui_contract"]
        response = client.post(
            f"/supernet/interface/projections/{opened['id']}/return",
            json=_return_payload(
                opened,
                "The returned interaction changes equality closure; the interface natural form is solved again from that return.",
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
    assert successor_solver["solution_count"] == opened_solver["solution_count"]
    assert successor_solver["solutions"][0]["coefficients"] != opened_solver[
        "solutions"
    ][0]["coefficients"]
    assert successor["supernet_closure_certificate"][
        "interactive_natural_form_solver_id"
    ] == successor_solver["id"]
    assert successor["supernet_closure_certificate"]["supernet_closed"] is True
    assert successor_solver["rendering_can_witness_equality"] is False
    assert successor_solver["only_return_refines_equality_closure"] is True
    assert successor["natural_form_atlas"][
        "cross_form_equality_requires_returned_translation"
    ] is True
    assert validate_ui_contract(successor)["valid"] is True
