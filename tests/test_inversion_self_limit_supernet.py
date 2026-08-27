from __future__ import annotations

import asyncio
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_inversion import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.inversion_models import (
    DemonConstructionCreate,
    EntanglementConstructionCreate,
    LocalRelationCreate,
    SingularityConstructionCreate,
    SuperpositionConstructionCreate,
)
from closure_supernet.runtime import ClosureSupernetRuntime


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "inversion.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


def test_relation_derives_one_inversion_and_exact_self_limit(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            relation = await runtime.inversion.create_relation(
                LocalRelationCreate(
                    name="generic relation",
                    authored_by="participant",
                    matrix=[[2, -3, 0], [1, 4, -5], [6, 2, -1]],
                )
            )
            evaluation = relation["evaluation"]
            assert evaluation["return_inversion_involutive"] is True
            assert evaluation["reconstruction_exact"] is True
            assert evaluation["axial_reconstruction_exact"] is True
            assert evaluation["divergence_reversed_by_inversion"] is True
            assert evaluation["hair_preserved_by_inversion"] is True
            assert evaluation["hair_sector_fixed"] is True
            assert evaluation["return_symmetric_sector_anti_fixed"] is True
            assert evaluation["neutral_sector_anti_fixed"] is True
            assert evaluation["self_limit_exact"] is True
            assert evaluation["self_limit_inversion_invariant"] is True
            assert evaluation["joint_saturation_iff_neutral_zero"] is True
            assert evaluation["representation_required"] is False
            assert evaluation["physical_law_claimed"] is False
            event = runtime.supernet_store.get_event(relation["integration_event_id"])
            determined = next(
                state for state in event["state_history"] if state["stage"] == "DETERMINED"
            )
            assert determined["verdict"] == "OPEN"
            assert determined["rigidity_receipt"]["representation_used"] is False
            assert determined["determined_form"]["canonical_representation"] is None
            assert event["current_stage"] == "RETURNED"
            assert event["current_verdict"] == "OPEN"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_pure_scale_and_pure_hair_saturate_their_own_readings(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        tolerance = Decimal("1e-24")
        scale = runtime.inversion.evaluate_relation(
            [[2, 0, 0], [0, 2, 0], [0, 0, 2]], tolerance
        )
        hair = runtime.inversion.evaluate_relation(
            [[0, -3, 2], [3, 0, -1], [-2, 1, 0]], tolerance
        )
        assert scale.pure_scale is True
        assert scale.scale_saturation is True
        assert scale.neutral_zero is True
        assert hair.pure_hair is True
        assert hair.hair_saturation is True
        assert hair.normalized_hair == ["1", "2", "3"]
    finally:
        runtime.close()


def test_four_named_constructions_share_one_hair_chart(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            entanglement = await runtime.inversion.create_entanglement(
                EntanglementConstructionCreate(
                    name="axial order defect",
                    left_hair=[1, 0, 0],
                    right_hair=[0, 1, 0],
                )
            )
            assert entanglement["evaluation"]["source_free"] is True
            assert entanglement["evaluation"]["pure_hair"] is True
            assert entanglement["evaluation"]["antisymmetric_in_pair"] is True
            assert entanglement["evaluation"]["genuinely_nonzero"] is True
            assert entanglement["evaluation"]["physical_entanglement_claimed"] is False

            superposition = await runtime.inversion.create_superposition(
                SuperpositionConstructionCreate(
                    name="destructive hair with neutral residue",
                    summands=[
                        [[1, -1, 0], [1, -1, 0], [0, 0, 0]],
                        [[1, 1, 0], [-1, -1, 0], [0, 0, 0]],
                    ],
                )
            )
            assert superposition["evaluation"]["hair_linearity"] is True
            assert superposition["evaluation"]["destructive_hair_interference"] is True
            assert superposition["evaluation"]["neutral_residue_nonzero"] is True
            assert superposition["evaluation"]["reading_cancellation_not_state_annihilation"] is True

            singularity = await runtime.inversion.create_singularity(
                SingularityConstructionCreate(
                    name="typed seam field",
                    direction=[0, 0, 1],
                    angle_radians="1.5707963267948966",
                    at_seam=True,
                )
            )
            assert singularity["evaluation"]["ratio_reading_empty_at_seam"] is True
            assert singularity["evaluation"]["seam_field_hair_extinguished"] is True
            assert singularity["evaluation"]["seam_chart_value_is_not_a_finite_ratio_solution"] is True
            assert singularity["evaluation"]["physical_singularity_claimed"] is False

            demon = await runtime.inversion.create_demon(
                DemonConstructionCreate(
                    name="neutral no-gain witness",
                    neutral_input=[[1, 0, 0], [0, -1, 0], [0, 0, 0]],
                    submitted_output=[[1, 0, 0], [0, -1, 0], [0, 0, 0]],
                )
            )
            assert demon["evaluation"]["input_is_neutral"] is True
            assert demon["evaluation"]["premises_hold_on_submitted_witness"] is True
            assert demon["evaluation"]["output_is_neutral"] is True
            assert demon["evaluation"]["source_gain_zero"] is True
            assert demon["evaluation"]["physical_thermodynamic_claimed"] is False

            for item in (entanglement, superposition, singularity, demon):
                event = runtime.supernet_store.get_event(item["integration_event_id"])
                assert event["current_verdict"] == "OPEN"
                assert any(state["stage"] == "DETERMINED" for state in event["state_history"])

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_inversion_api_interface_and_supernet_lens(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/self-limit")
        assert page.status_code == 200
        assert "One inversion" in page.text
        relation = client.post(
            "/network/inversion/relations",
            json={
                "name": "API relation",
                "authored_by": "participant",
                "matrix": [[1, -1, 0], [1, 0, -2], [0, 2, -1]],
            },
        )
        assert relation.status_code == 200
        assert relation.json()["evaluation"]["self_limit_exact"] is True
        assert relation.json()["evaluation"]["representation_required"] is False

        field = client.get("/network/inversion/field")
        assert field.status_code == 200
        assert field.json()["stats"]["relations"] == 1
        assert field.json()["physical_law_claimed"] is False

        lens = client.get("/supernet/project", params={"lens": "inversion"})
        assert lens.status_code == 200
        assert lens.json()["lens"] == "inversion"
        assert lens.json()["stats"]["visible_events"] >= 1

        capabilities = client.get("/supernet/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["return_inversion_is_minus_transpose"] is True
        assert capabilities.json()["representation_required"] is False
        assert capabilities.json()["physical_law_claimed"] is False
