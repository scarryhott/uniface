from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.natural_form_projection_runtime import (
    derive_local_projection_commitment,
)


FAMILY_OPERATORS = {
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


def test_production_surface_translates_verified_atlas_into_family_geometry(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/")
        opened = client.get(
            "/supernet/interface",
            params={"perspective_id": "perspective:natural-render"},
        ).json()["closure_ui_contract"]

    assert page.status_code == 200
    html = page.text
    assert "CURRENT_TT_RELATIVE_FAMILY_MORPH" in html
    assert "renderNaturalFormAtlas" in html
    assert "familyRelativeRoles" in html
    assert "transformNaturalFormPoint" in html
    assert "data-family-equality" in html
    assert "data-executes-as-equality" in html
    for operator in FAMILY_OPERATORS:
        assert operator in html

    # The renderer remains one blank authored surface: it adds no menu or
    # developer-selected natural-form controls. Family foregrounding is hair.
    static_body = html.split("<body>", 1)[1].split("<script>", 1)[0].strip()
    assert static_body == '<main id="translational-mirror"></main>'
    for control in ("<button", "<select", "<nav", "<form"):
        assert control not in static_body

    freedom = opened["local_natural_form_freedom"]
    assert freedom["selection_freedom"]["selection_is_set_valued"] is True
    assert freedom["selection_freedom"]["selection_filters_families"] is False
    assert freedom["selection_freedom"]["future_resolution_guaranteed"] is False


def test_return_refines_truth_while_render_family_freedom_remains_presentation_only(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    perspective = "perspective:natural-return"
    with TestClient(app) as client:
        opened = client.get(
            "/supernet/interface", params={"perspective_id": perspective}
        ).json()["closure_ui_contract"]
        response = client.post(
            f"/supernet/interface/projections/{opened['id']}/return",
            json=_return_payload(
                opened,
                "The returned interaction refines closure while natural forms remain relative views.",
            ),
        )
        assert response.status_code == 200, response.text
        successor = response.json()["closure_ui_contract"]

    assert response.json()["returned"] is True
    assert successor["id"] != opened["id"]
    assert successor["supernet_closure_certificate"]["supernet_closed"] is True
    assert successor["local_natural_form_freedom"]["id"] != opened[
        "local_natural_form_freedom"
    ]["id"]
    assert successor["local_natural_form_freedom"]["selection_freedom"][
        "selection_is_set_valued"
    ] is True
    assert successor["local_natural_form_freedom"]["local_constraint"][
        "unwitnessed_family_selection_authors_truth"
    ] is False
    assert successor["natural_form_atlas"][
        "visual_resemblance_can_witness_equality"
    ] is False
    assert successor["natural_form_atlas"][
        "cross_form_equality_requires_returned_translation"
    ] is True
