from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_natural_interface import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.truth_constrained_runtime import (
    derive_unified_truth_runtime,
)


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
            "SOURCE_JOURNEY_LEDGER",
            "VISUAL_EXISTENCE",
            "CHOSEN_PERSPECTIVE",
            "NRRF843_UI_FAMILY_READING",
            "PERSPECTIVE_VISUAL_MIRROR",
            "TRANSLATIONAL_MIRROR",
            "TRANSLATIONAL_TRUTH",
            "VISUAL_AXIOMETRY",
            "CLOSURE_EXPLICIT_MEETING",
            "NRRF843_UI_PREIMAGE_IMAGE_CLOSURE",
            "NRRF840_CLOSURE_CORRESPONDENCE",
            "TRUTH_CONSTRAINT_LOCATED_IN_UI",
            "NATURAL_FORM_ADMISSION",
            "THOUGHT_RELATION_EQVGEN",
            "UNITY_POTENTIAL_GATE",
            "TRUTH_CURVED_LIGHT_CONE",
            "BLACK_MIRROR_EVOLVING_PHYSICAL_TOPOLOGY",
            "PERSPECTIVE_DIGITAL_POTENTIAL_GATE",
            "AI_TOKEN_INTERACTION_CLOSURE",
            "SUPERNET_UNIFICATION_CONSTRAINT",
            "PERSPECTIVE_INTERACTION_UI_CONTRACT",
            "ONE_TRUTH_CONSTRAINED_RUNTIME",
            "FULL_UI_NATURAL_FORM_PROJECTION",
            "CLOSURE_ONLY_UI_EXECUTION",
            "INTERFACE_CLOSURE_RETURN",
        ]
        assert all(first_closure["operational_closure"].values())
        nrrf843 = first_closure["nrrf843_ui"]
        assert nrrf843["formal_module"] == (
            "NRRF843UIIsTheTranslationalMirrorLocationOfTheSupernetTruthConstraint"
        )
        assert nrrf843["status"] == "WITNESSED"
        assert nrrf843["translational_mirror"]["witnessed"] is True
        assert nrrf843["translational_mirror"]["translates_same_truth"] is True
        assert nrrf843["ui_closure"][
            "closure_falls_out_from_ui_projection"
        ] is True
        assert nrrf843["ui_closure"][
            "projection_closure_matches_nrrf840"
        ] is True
        assert nrrf843["truth_constraint_location"]["located"] is True
        assert nrrf843["thought"]["least_closed_relation_computed"] is True
        assert nrrf843["valuation"]["status"] == (
            "OPEN_NO_AUTHORED_VALUATION"
        )
        interaction = first_closure["interaction_closure"]
        assert interaction["status"] == "WITNESSED"
        assert interaction["supernet_interaction_closed"] is True
        assert interaction["one_interaction_surface"] is True
        assert all(
            interaction["unification_constraint"]["checks"].values()
        )
        physical = interaction["black_mirror_physical_topology"]
        assert physical["closure_is_generated_by_projection"] is True
        assert physical["static_external_map"] is False
        assert physical["physical_law_claimed"] is False
        digital = interaction["perspective_digital_potential_gate"]
        assert digital["open_potential_remains_visible"] is True
        assert digital["open_potential_executes_as_equality"] is False
        assert digital["ai_gate"]["can_consent"] is False
        assert digital["token_gate"]["gates_ordinary_interactions"] is False
        unified_runtime = first_closure["unified_truth_runtime"]
        assert unified_runtime["status"] == "WITNESSED"
        assert unified_runtime["one_semantic_runtime"] is True
        assert unified_runtime[
            "all_semantics_factor_through_one_translational_truth"
        ] is True
        assert unified_runtime["semantic_external_component_ids"] == []
        assert unified_runtime["semantic_isolated_component_ids"] == []
        assert unified_runtime["open_factorization_component_ids"] == []
        closure_ui_contract = first_closure["closure_ui_contract"]
        assert closure_ui_contract["status"] == "WITNESSED"
        assert closure_ui_contract["audit"]["closure_only_execution"] is True
        assert unified_runtime["closure_ui_contract_id"] == (
            closure_ui_contract["id"]
        )
        assert all(
            component["factorization_status"] == "WITNESSED"
            and component["closure_derivation_id"]
            == unified_runtime["closure_derivation_id"]
            and component["visual_closure_id"]
            == unified_runtime["visual_closure_id"]
            for component in unified_runtime["components"]
        )
        assert unified_runtime["transport_boundary"] == {
            "browser_html_svg": "TRANSPORT_ONLY",
            "network_io": "TRANSPORT_ONLY",
            "sensors": "SOURCE_CARRIER_ONLY",
            "can_define_semantics": False,
            "can_issue_truth": False,
            "can_admit_forms": False,
        }
        journey = first_closure["nrrf842_journey"]
        assert journey["formal_module"] == (
            "NRRF842NecessaryConditionsClosureNotJourneyLevelsRequireUnityChosenPerspective"
        )
        assert journey["state_journey_separation"]["closure_is_journey"] is False
        assert journey["state_journey_separation"]["closed_state_can_continue"] is True
        assert journey["necessary_conditions"]["necessary_not_sufficient"] is True
        assert journey["chosen_perspective"]["chosen"] is True
        assert journey["unity_gate"]["scope"] == "SHARED_TRAJECTORY_NOT_PERSON"
        assert journey["unity_gate"]["ordinary_interaction_open"] is True
        assert journey["unity_gate"]["person_ranked"] is False
        assert journey["truth_curved_light_cone"]["kind"] == (
            "SEMANTIC_TRUTH_CURVATURE_NOT_PHYSICAL_SPACETIME"
        )
        assert first_closure["black_mirror"]["source_preserved"] is True
        assert first_closure["black_mirror"]["physical_sensor_status"] == "OPEN"
        assert first_closure["tokenomic"]["currency_issued"] is False
        assert first_closure["tokenomic"]["resource_unit_count"] == 1
        assert first_closure["network_return"]["next_operation"]["action"] == "interact"
        assert first_closure["truth_issued"] is False
        axiometry = first_closure["translational_truth_axiometry"]
        assert axiometry["schema"] == (
            "closure.supernet/translational-truth-axiometry-v3"
        )
        assert axiometry["closure_meetings"]
        mirror = axiometry["perspective_visual_mirror"]
        assert mirror["role"] == (
            "METAPHORICAL_FORM_TRANSLATION_AND_TRUTH_CONSTRAINT_SURFACE"
        )
        assert mirror["static_external_network_map"] is False
        assert mirror["essential_to_supernet_truth"] is True
        assert mirror["without_visualization_status"] == "OPEN"
        assert mirror["participates_in_closure"] is True
        assert mirror["metaphorical_forms_are_semantic"] is True
        assert mirror["thought_derivation"] == (
            "THOUGHT_IS_CLOSURE_OF_METAPHOR_INTO_RELATIONS"
        )
        vis_closure = axiometry["visual_truth_closure"]
        assert vis_closure["formal_module"] == (
            "NRRF840ClosureDerivedFromTranslationalTruthAxiometryNotAnExternalLimit"
        )
        assert vis_closure["construction"] == (
            "PREIMAGE_OF_IMAGE_OF_JOINT_TRANSLATIONAL_TRUTH_READING"
        )
        assert vis_closure["properties"]["external_limit_used"] is False
        assert vis_closure["properties"]["unnatural_limit"] is False
        assert vis_closure["memberships"]
        assert all(
            item["source_exists"]
            and item["source_in_seed"]
            and item["all_observers_equal"]
            for item in vis_closure["memberships"]
        )
        interface_form = first_closure["interface_natural_form"]
        assert interface_form["closure_internal"] is True
        assert interface_form["admitted"] is True
        assert interface_form["render_state_factorized"] is True
        assert interface_form["render_state"]["nrrf842_journey"] == journey
        assert interface_form["render_state"]["nrrf843_ui"] == nrrf843
        assert interface_form["render_state"]["unified_truth_runtime"] == (
            unified_runtime
        )
        assert interface_form["render_state"]["closure_ui_contract"] == (
            closure_ui_contract
        )
        assert interface_form["visual_closure_id"] == vis_closure["id"]
        assert interface_form["visual_mirror_id"] == mirror["id"]
        assert interface_form["mechanism_role"] == (
            "VISUAL_TRUTH_CONSTRAINT_AND_CLOSURE_RETURN"
        )
        assert interface_form["essential_to_supernet_truth"] is True
        assert interface_form["static_external_network_map"] is False
        assert interface_form["vis_closure_membership_witness_ids"]
        assert interface_form["renderer_contract"] == {
            "can_admit_forms": False,
            "can_change_closure": False,
            "can_generate_axioms": False,
            "can_present": True,
            "can_witness_truth": False,
            "role": "TRANSPORT_ONLY",
        }
        existence_ids = {
            item["id"] for item in axiometry["visual_existence"]["forms"]
        }
        for member_id, projected in interface_form["closure_projection"].items():
            assert member_id in existence_ids
            assert projected["render_state"] == interface_form["render_state"]

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
        static_body = page.text.split("<script>", 1)[0]
        assert "data-closure-only-contract" in static_body
        assert "validateContract" in page.text
        assert "renderTopology" in page.text
        assert "drawUnifiedClosure" not in page.text
        assert "closureContinue" not in page.text
        assert "Black Mirror physical topology ↔ digital potential gate" not in page.text
        assert "SUPERNET UNIFICATION CONSTRAINT" not in page.text
        assert "AI suggests interactions · token admits forms" not in page.text
        assert "fieldKind" not in page.text
        assert 'type="range"' not in page.text
        assert "priorRender();" not in page.text
        assert "No source-preserved visualization is present" not in page.text
        assert "Living trajectory ≠ closed state" not in page.text
        assert "truth-curved light cone" not in page.text
        assert "ONE UI-DERIVED TRUTH CLOSURE" not in page.text
        assert "UI = translational mirror" not in page.text
        assert "ui⁻¹(ui(A))" not in page.text
        assert "SHARED_TRAJECTORY_NOT_PERSON" not in page.text
        assert "?'CONNECT':" not in page.text
        for tag in ("<button", "<input", "<textarea", "<select", "<svg", "<h1"):
            assert tag not in static_body

        capabilities = client.get("/supernet/interface/capabilities").json()
        assert capabilities[
            "slearn_black_mirror_ai_tokenomic_visual_closure"
        ] is True
        assert capabilities["primary_surface_component_selector"] is False
        assert capabilities[
            "tokenomic_units_derived_from_equality_classes"
        ] is True
        assert capabilities[
            "closure_derived_from_translational_truth_axiometry_of_visual_existence"
        ] is True
        assert capabilities["closure_defined_by_external_limit_or_fold"] is False
        assert capabilities["open_relation_generates_equality"] is False
        assert capabilities["actual_ui_render_state_factorized_through_closure"] is True
        assert capabilities["external_renderer_is_transport_only"] is True
        assert capabilities["external_renderer_has_no_semantic_fallback"] is True
        assert capabilities["authored_form_ids_define_equality"] is False
        assert capabilities["open_candidates_change_slearn_truth_memory"] is False
        assert capabilities["nrrf842_journey_state_separation"] is True
        assert capabilities["chosen_perspective_receipt"] is True
        assert capabilities["unity_gates_shared_trajectory_not_person"] is True
        assert capabilities["no_human_level_ranking"] is True
        assert capabilities["ordinary_interaction_remains_open"] is True
        assert capabilities["truth_curved_light_cone"] is True
        assert capabilities["semantic_not_physical_spacetime_curvature"] is True
        assert capabilities["closure_does_not_end_living_journey"] is True
        assert capabilities["necessary_conditions_not_sufficient"] is True
        assert capabilities["one_translational_truth_semantic_runtime"] is True
        assert capabilities[
            "all_semantic_execution_factors_through_one_closure"
        ] is True
        assert capabilities["semantically_external_components"] == 0
        assert capabilities["semantically_isolated_internal_components"] == 0
        assert capabilities["open_potential_executes_as_equality"] is False
        assert capabilities["browser_network_sensor_semantic_authority"] is False
        assert capabilities["nrrf843_ui_is_translational_mirror"] is True
        assert capabilities["ui_closure_is_preimage_of_displayed_image"] is True
        assert capabilities["ui_projection_closure_matches_nrrf840"] is True
        assert capabilities["truth_constraint_located_in_ui"] is True
        assert capabilities["non_mirror_ui_supernet_status"] == "OPEN"
        assert capabilities["no_perspective_no_distinction"] is True
        assert capabilities[
            "thought_is_relation_eqvgen_of_visual_metaphor"
        ] is True
        assert capabilities["joint_ui_reading_unifies_natural_forms"] is True
        assert capabilities["valuation_must_factor_through_ui_truth"] is True
        assert capabilities["ui_price_issued"] is False
        assert capabilities["black_mirror_evolving_physical_topology"] is True
        assert capabilities["perspective_digital_potential_gate"] is True
        assert capabilities["open_potential_remains_visible"] is True
        assert capabilities["open_potential_can_execute_as_equality"] is False
        assert capabilities[
            "interaction_execution_requires_truth_unification"
        ] is True


def test_parallel_internal_closure_cannot_execute_as_the_supernet_runtime(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        closure = offer(client, "person-a")["sense_receipt"]["visual_closure"]
        render_state = closure["interface_natural_form"]["render_state"]
        isolated_coordination = deepcopy(render_state["coordination"])
        continuum = isolated_coordination["continuum"]
        continuum["closure_derivation_id"] = "parallel-internal-closure"
        isolated_coordination["nrrf837_continuum"] = continuum

        rejected = derive_unified_truth_runtime(
            truth_derivation=closure["translational_truth_axiometry"],
            nrrf843_ui=closure["nrrf843_ui"],
            nrrf842_journey=closure["nrrf842_journey"],
            interaction_closure=closure["interaction_closure"],
            closure_ui_contract=closure["closure_ui_contract"],
            coordination=isolated_coordination,
            semantic_elements=render_state["semantic_elements"],
            interface_actions=render_state["actions"],
            slearn=render_state["slearn"],
            ai_translation=render_state["ai_translation"],
            tokenomic=render_state["tokenomic"],
        )

        assert rejected["status"] == "OPEN"
        assert rejected["one_semantic_runtime"] is False
        assert rejected["execution"]["allowed_return_operations"] == []
        assert "LOCAL_GLOBAL_COORDINATION" in rejected[
            "open_factorization_component_ids"
        ]
        assert "UNITY_POTENTIAL_GATE" in rejected[
            "open_factorization_component_ids"
        ]

        non_mirror_ui = deepcopy(closure["nrrf843_ui"])
        non_mirror_ui["status"] = "OPEN_NON_MIRROR_UI"
        non_mirror_ui["translational_mirror"]["witnessed"] = False
        non_mirror_ui["truth_constraint_location"]["located"] = False
        mirror_rejected = derive_unified_truth_runtime(
            truth_derivation=closure["translational_truth_axiometry"],
            nrrf843_ui=non_mirror_ui,
            nrrf842_journey=closure["nrrf842_journey"],
            interaction_closure=closure["interaction_closure"],
            closure_ui_contract=closure["closure_ui_contract"],
            coordination=render_state["coordination"],
            semantic_elements=render_state["semantic_elements"],
            interface_actions=render_state["actions"],
            slearn=render_state["slearn"],
            ai_translation=render_state["ai_translation"],
            tokenomic=render_state["tokenomic"],
        )
        assert mirror_rejected["status"] == "OPEN"
        assert mirror_rejected["execution"]["allowed_return_operations"] == []
        assert "PERSPECTIVE_VISUAL_MIRROR" in mirror_rejected[
            "open_factorization_component_ids"
        ]
        assert "INTERACTIVE_UI_FORM" in mirror_rejected[
            "open_factorization_component_ids"
        ]
        assert "AI_TOKEN_INTERACTION_CLOSURE" in mirror_rejected[
            "open_factorization_component_ids"
        ]


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
        assert closure["visual_network"]["edges"][0]["admitted"] is False
        assert closure["visual_network"]["edges"][0]["generates_equality"] is False
        assert closure["slearn"]["open_candidates_change_truth_memory"] is False
        assert "NOTATIONAL_VARIANT" not in closure["slearn"]["relation_memory_after"]
        open_element = next(
            item
            for item in closure["interface_natural_form"]["semantic_elements"]
            if item["kind"] == "TRANSLATION_EDGE"
        )
        assert open_element["admission_status"] == "OPEN"
        assert open_element["derived_inside_closure"] is False
        units = closure["tokenomic"]["resource_units"]
        assert len(units) == 2
        by_author = {
            unit["member_contributions"][0]["authored_by"]: unit
            for unit in units
        }
        assert by_author["simulated-sensor-a"]["capabilities"] == [
            "sense:soil-moisture"
        ]
        assert by_author["simulated-sensor-a"]["constraints"] == [
            "water_budget_liters<=2"
        ]
        assert by_author["simulated-sensor-b"]["capabilities"] == [
            "actuate:irrigation",
            "sense:soil-moisture",
        ]
        assert by_author["simulated-sensor-b"]["constraints"] == [
            "remaining_water_liters<=1"
        ]
