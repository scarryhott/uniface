from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

import httpx
from fastapi.testclient import TestClient

from closure_supernet.api_natural_interface import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.nrrf837_continuum import UNITY_SELECTOR_VERSION, canonical_hash


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "community-garden-coordination.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def post(
    client: TestClient,
    path: str,
    payload: dict[str, Any],
    *,
    expected_status: int = 200,
) -> dict[str, Any]:
    response = client.post(path, json=payload)
    assert response.status_code == expected_status, response.text
    return response.json()


def seed_coordination_field(client: TestClient) -> dict[str, str]:
    person = post(
        client,
        "/supernet/interface/offer",
        {
            "exact_text": (
                "Maya wants to help start a Berkeley community garden and can "
                "share garden planning and composting experience on weekends."
            ),
            "authored_by": "maya",
            "perspective_id": "maya",
            "form_label": "nearby garden collaborator",
            "coordination_kind": "PERSON",
            "location_label": "Berkeley, California",
            "capabilities": ["garden planning", "composting", "weekend collaboration"],
            "constraints": ["weekends only", "mutual consent required"],
            "relation_hints": ["community garden", "Berkeley", "collaboration"],
            "metadata": {"profile_id": "maya-garden-profile"},
        },
    )
    project = post(
        client,
        "/supernet/interface/offer",
        {
            "exact_text": (
                "River Street Garden is a Berkeley community garden project with "
                "six open beds seeking organizers and weekend volunteers."
            ),
            "authored_by": "river-street-steward",
            "perspective_id": "river-street-steward",
            "form_label": "existing community garden",
            "coordination_kind": "PROJECT",
            "location_label": "Berkeley, California",
            "capabilities": ["six garden beds", "existing local project"],
            "constraints": ["water access unresolved", "tool budget unresolved"],
            "relation_hints": ["community garden", "Berkeley", "weekend volunteers"],
            "metadata": {"project_id": "river-street-garden"},
        },
    )
    resource = post(
        client,
        "/supernet/interface/offer",
        {
            "exact_text": (
                "Editable community garden collaboration proposal with roles, "
                "resource offers, constraints, consent, and a returned consequence."
            ),
            "authored_by": "proposal-library",
            "perspective_id": "proposal-library",
            "form_label": "garden collaboration proposal template",
            "coordination_kind": "RESOURCE",
            "location_label": "Berkeley, California",
            "capabilities": ["draft collaboration proposal"],
            "constraints": ["not a binding contract", "requires participant acceptance"],
            "relation_hints": ["community garden", "proposal", "resource commitment"],
            "metadata": {"resource_id": "garden-proposal-template"},
        },
    )
    return {
        "person": person["event_id"],
        "project": project["event_id"],
        "resource": resource["event_id"],
    }


def create_intent(client: TestClient) -> dict[str, Any]:
    return post(
        client,
        "/supernet/interface/intents",
        {
            "exact_text": "I want to start a community garden.",
            "authored_by": "harry",
            "perspective_id": "harry",
            "form_label": "community garden intent",
            "coordination_kind": "INTENT",
            "location_label": "Berkeley, California",
            "capabilities": ["organize a local project"],
            "constraints": ["weekends", "budget_usd<=100"],
            "relation_hints": ["community garden", "Berkeley", "collaboration"],
            "metadata": {"product_acceptance_fixture": True},
        },
    )


def create_commitment_proposal(
    client: TestClient,
    *,
    intent_event_id: str,
    target_event_ids: list[str],
) -> dict[str, Any]:
    result = post(
        client,
        "/supernet/interface/commitments",
        {
            "intent_event_id": intent_event_id,
            "target_event_ids": target_event_ids,
            "title": "River Street community garden collaboration proposal",
            "exact_terms": (
                "Harry proposes up to 25 USD of garden-tool resources and two "
                "weekend planning hours, subject to Maya's separate acceptance."
            ),
            "proposed_by": "harry",
            "perspective_id": "harry",
            "required_participant_ids": ["harry", "maya"],
            "resource_conditions": [
                "tools_only",
                "budget_usd<=25",
                "requires both participant acceptances",
            ],
        },
    )
    assert result["truth_issued"] is False
    return result


def paths_by_kind(coordination: dict[str, Any]) -> dict[str, dict[str, Any]]:
    paths = coordination.get("paths") or coordination.get("suggestions") or []
    return {str(path["kind"]): path for path in paths}


def assert_proposal_is_nonbinding(proposal: dict[str, Any]) -> None:
    assert proposal["binding"] is False
    assert proposal["transferable"] is False
    assert proposal["currency_issued"] is False
    assert proposal["interactions_gated"] is False
    assert proposal["truth_issued"] is False
    assert proposal["security_enforcement"] == "OPEN"


def assert_explainable_open_path(
    path: dict[str, Any],
    *,
    intent_event_id: str,
) -> None:
    assert path["status"] == "OPEN"
    assert path["binding"] is False
    assert path["truth_issued"] is False
    assert path["authorship_role"] == "AI"
    why = path["why"]
    assert why["rationale"]
    assert why["matched_terms"]
    assert why["limitations"]
    assert why["global_optimum_claimed"] is False
    assert why["formal_suggestion_status"] == "OPEN"
    assert why["suggestion_equivalence"] == "OPEN"
    assert why["shared_natural_form_id"] is None
    assert intent_event_id in why["source_event_ids"]
    assert path["target_event_id"] in why["source_event_ids"]


def continuum_of(coordination: dict[str, Any]) -> dict[str, Any]:
    continuum = coordination["nrrf837_continuum"]
    assert coordination["continuum"] == continuum
    return continuum


def assert_nrrf837_continuum_laws(
    coordination: dict[str, Any],
    *,
    phase: str,
    commitment_exists: bool,
) -> dict[str, Any]:
    continuum = continuum_of(coordination)
    assert continuum["formal_reading"] == "NRRF837"
    assert continuum["local_monoid"]["identity_verified"] is True
    assert continuum["local_monoid"]["associative"] is True
    assert continuum["compose"]["identity_preserved"] is True
    assert continuum["compose"]["concatenation_preserved"] is True
    assert continuum["compose"]["homomorphism_verified"] is True
    assert continuum["modality"]["operator"] == phase
    assert continuum["modality"]["idempotent"] is True
    assert continuum["modality"]["fixed_point"] is True
    assert continuum["modality"]["fixed_points_equal_unity"] is True
    assert continuum["freedom_fibre"]["nonempty"] is True
    assert continuum["freedom_fibre"]["exactly_one_unity_witness"] is True
    assert continuum["authorship"]["source_identities_preserved"] is False
    assert continuum["authorship"]["missing_source_identity_actor_ids"]
    assert continuum["authorship"]["actor_identity_collapsed"] is False
    assert (
        continuum["authorship"]["equal_global_content_identifies_actors"]
        is False
    )
    assert continuum["suggestions"]["equivalence"]["verified"] is True
    assert continuum["suggestions"]["ranking_is_contextual_not_equivalence"] is True
    assert continuum["suggestions"]["global_optimum_claimed"] is False
    assert continuum["gates"]["token"]["gates_forms"] is True
    assert (
        continuum["gates"]["token"]["gates_ordinary_interactions"] is False
    )
    assert continuum["gates"]["ai"]["can_consent"] is False
    assert continuum["gates"]["ai"]["can_bind"] is False
    assert continuum["gates"]["joint_product"]["joint_gate_iff_product"] is True
    assert continuum["commitment_relation"]["exists"] is commitment_exists
    assert continuum["commitment_relation"]["correlated"] is commitment_exists
    assert continuum["commitment_relation"]["separate_from_product_gates"] is True
    assert (
        continuum["commitment_relation"][
            "non_product_realisable_by_independent_gates"
        ]
        is False
    )
    assert continuum["unity_selector"]["network_derived"] is False
    assert continuum["unity_selector"]["extra_data"] is True
    assert continuum["claims"]["truth_issued"] is False
    assert continuum["claims"]["economic_value_claimed"] is False
    assert continuum["claims"]["value_claimed"] is False
    assert continuum["claims"]["global_optimum_claimed"] is False
    return continuum


def test_community_garden_intent_closes_through_mutual_authorship(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        seeds = seed_coordination_field(client)
        intent = create_intent(client)
        intent_event_id = intent["event_id"]
        coordination = intent["coordination"]

        assert intent["truth_issued"] is False
        assert coordination["truth_issued"] is False
        assert coordination["intent_event_id"] == intent_event_id
        assert coordination["optimization_scope"] == (
            "visible source-preserved paths under the authored location and constraints"
        )
        assert coordination["global_optimum_claimed"] is False

        by_kind = paths_by_kind(coordination)
        assert {"PERSON", "PROJECT", "RESOURCE"} <= set(by_kind)
        assert by_kind["PERSON"]["target_event_id"] == seeds["person"]
        assert by_kind["PROJECT"]["target_event_id"] == seeds["project"]
        assert by_kind["RESOURCE"]["target_event_id"] == seeds["resource"]
        assert_explainable_open_path(
            by_kind["PERSON"], intent_event_id=intent_event_id
        )
        assert_explainable_open_path(
            by_kind["PROJECT"], intent_event_id=intent_event_id
        )

        initial_operator = coordination["natural_form_operator"]
        assert initial_operator["natural_form"] == "DISCOVER"
        assert initial_operator["derived"] is True
        assert initial_operator["user_selected_phase"] is False
        assert initial_operator["token_gated_forms"] == ["ACT", "RETURN"]
        assert initial_operator["interactions_gated"] is False
        assert {"inspect", "message", "ask", "decline"} <= set(
            initial_operator["local_open"]
        )
        initial_continuum = assert_nrrf837_continuum_laws(
            coordination,
            phase="DISCOVER",
            commitment_exists=False,
        )
        intent_authorship = next(
            item
            for item in initial_continuum["authorship"][
                "event_authorship_records"
            ]
            if item["source_event_ids"] == [intent_event_id]
        )
        assert intent_authorship["actor_id"] == "harry"
        assert intent_authorship["internal_actor_id"] == intent["participant"]["id"]
        assert intent_authorship["internal_actor_id"] != intent_authorship[
            "actor_id"
        ]

        created = create_commitment_proposal(
            client,
            intent_event_id=intent_event_id,
            target_event_ids=[
                by_kind["PERSON"]["target_event_id"],
                by_kind["PROJECT"]["target_event_id"],
                by_kind["RESOURCE"]["target_event_id"],
            ],
        )
        proposal = created["proposal"]
        proposal_id = proposal["id"]
        assert proposal["status"] == "PROPOSED"
        assert proposal["exact_terms"].startswith("Harry proposes up to 25 USD")
        assert proposal["open_assumptions"] == []
        assert proposal["unity_selector_version"] == UNITY_SELECTOR_VERSION
        assert proposal["settled"] is False
        assert proposal["required_participant_ids"] == ["harry", "maya"]
        assert proposal["decisions"] == []
        assert_proposal_is_nonbinding(proposal)

        proposed_coordination = created["coordination"]
        proposed_operator = proposed_coordination["natural_form_operator"]
        assert proposed_operator["natural_form"] == "AGREE"
        assert proposed_operator["token_gated_forms"] == ["ACT", "RETURN"]
        assert proposed_operator["interactions_gated"] is False
        proposed_continuum = assert_nrrf837_continuum_laws(
            proposed_coordination,
            phase="AGREE",
            commitment_exists=True,
        )
        stable_global_content_id = proposed_continuum["global_content_id"]
        proposed_global_state_id = proposed_continuum["global_state_id"]
        proposed_form_id = proposed_continuum["selected_natural_form_id"]
        assert proposed_continuum["commitment_relation"]["tuple"][
            "exact_terms_hash"
        ] == canonical_hash(proposal["exact_terms"])
        intent_after_proposal = client.get(
            "/supernet/interface", params={"focus_event_id": intent_event_id}
        ).json()
        assert (
            intent_after_proposal["visual_closure"]["coordination"][
                "active_proposal"
            ]["status"]
            == "PROPOSED"
        )

        # A proposal token gates ACT/RETURN interface forms, not ordinary
        # interaction.  The interaction remains OPEN and nonbinding.
        interaction = post(
            client,
            f"/supernet/events/{intent_event_id}/sense-interact",
            {
                "exact_text": (
                    "Could we visit River Street Garden and compare weekend plans?"
                ),
                "authored_by": "harry",
                "perspective_id": "harry",
                "form_label": "garden coordination question",
                "capabilities": ["message a collaborator"],
                "constraints": ["no commitment implied"],
                "metadata": {"commitment_proposal_id": proposal_id},
            },
        )
        assert interaction["event_id"]
        assert interaction["sense_receipt"]["truth_issued"] is False

        first_accept = post(
            client,
            f"/supernet/interface/commitments/{proposal_id}/decisions",
            {
                "participant_id": "harry",
                "authored_by": "harry",
                "decision": "ACCEPT",
                "exact_text": (
                    "I accept my proposal to offer two weekend planning hours and "
                    "up to 25 USD of tool resources."
                ),
                "authorship_role": "HUMAN",
                "resource_offers": ["two weekend planning hours", "up to 25 USD tools"],
                "constraints": ["tools_only", "not a monetary settlement"],
            },
        )
        first_proposal = first_accept["proposal"]
        first_decision_event_id = first_accept["decision_event_id"]
        assert first_proposal["status"] == "PARTIAL"
        assert [item["participant_id"] for item in first_proposal["decisions"]] == [
            "harry"
        ]
        assert_proposal_is_nonbinding(first_proposal)
        partial_coordination = first_accept["coordination"]
        assert partial_coordination["natural_form_operator"]["natural_form"] == "COMMIT"
        partial_continuum = assert_nrrf837_continuum_laws(
            partial_coordination,
            phase="COMMIT",
            commitment_exists=True,
        )
        assert partial_continuum["global_content_id"] == stable_global_content_id
        assert partial_continuum["global_state_id"] != proposed_global_state_id
        assert partial_continuum["selected_natural_form_id"] != proposed_form_id
        assert (
            partial_continuum["one_tap"]["settlement"][
                "all_required_humans_accepted"
            ]
            is False
        )
        assert partial_continuum["one_tap"]["settlement"]["settled"] is False
        proposal_after_first_decision = client.get(
            "/supernet/interface",
            params={"focus_event_id": proposal["proposal_event_id"]},
        ).json()
        assert (
            proposal_after_first_decision["visual_closure"]["coordination"][
                "active_proposal"
            ]["status"]
            == "PARTIAL"
        )

        second_accept = post(
            client,
            f"/supernet/interface/commitments/{proposal_id}/decisions",
            {
                "participant_id": "maya",
                "authored_by": "maya",
                "decision": "ACCEPT",
                "exact_text": (
                    "I accept exploring the garden proposal while soil, water, and "
                    "future consent remain open."
                ),
                "authorship_role": "HUMAN",
                "resource_offers": ["garden planning", "composting experience"],
                "constraints": ["weekends only", "future actions require consent"],
            },
        )
        accepted = second_accept["proposal"]
        assert accepted["status"] == "ACCEPTED"
        assert {item["participant_id"] for item in accepted["decisions"]} == {
            "harry",
            "maya",
        }
        assert all(item["authorship_role"] == "HUMAN" for item in accepted["decisions"])
        assert_proposal_is_nonbinding(accepted)
        assert second_accept["truth_issued"] is False
        assert second_accept["coordination"]["current_verdict"] == "OPEN"
        second_decision_event_id = second_accept["decision_event_id"]
        first_participant_after_second_decision = client.get(
            "/supernet/interface",
            params={"focus_event_id": first_decision_event_id},
        ).json()
        accepted_from_first_participant_surface = (
            first_participant_after_second_decision["visual_closure"][
                "coordination"
            ]
        )
        assert (
            accepted_from_first_participant_surface["active_proposal"]["status"]
            == "ACCEPTED"
        )
        assert (
            accepted_from_first_participant_surface["token_gate"][
                "interactions_gated"
            ]
            is False
        )

        accepted_operator = second_accept["coordination"]["natural_form_operator"]
        assert accepted_operator["natural_form"] == "ACT"
        assert accepted_operator["derived"] is True
        assert accepted_operator["token_gated_forms"] == ["ACT", "RETURN"]
        assert accepted_operator["interactions_gated"] is False
        accepted_continuum = assert_nrrf837_continuum_laws(
            second_accept["coordination"],
            phase="ACT",
            commitment_exists=True,
        )
        assert accepted_continuum["global_content_id"] == stable_global_content_id
        assert accepted_continuum["global_state_id"] != partial_continuum[
            "global_state_id"
        ]
        assert accepted_continuum["selected_natural_form_id"] != partial_continuum[
            "selected_natural_form_id"
        ]
        assert (
            accepted_continuum["one_tap"]["settlement"][
                "all_required_humans_accepted"
            ]
            is True
        )
        assert accepted_continuum["one_tap"]["settlement"]["settled"] is True

        # Acceptance still does not gate a later ordinary interaction.
        after_acceptance = post(
            client,
            f"/supernet/events/{intent_event_id}/sense-interact",
            {
                "exact_text": "What soil test should we perform before choosing beds?",
                "authored_by": "maya",
                "perspective_id": "maya",
                "form_label": "open garden question",
                "constraints": ["proposal remains nonbinding"],
                "metadata": {"commitment_proposal_id": proposal_id},
            },
        )
        assert after_acceptance["event_id"]
        assert after_acceptance["sense_receipt"]["truth_issued"] is False

        returned = post(
            client,
            f"/supernet/interface/commitments/{proposal_id}/returns",
            {
                "exact_text": (
                    "Simulated living-system return: six beds fit; soil quality and "
                    "water access remain unresolved."
                ),
                "authored_by": "river-street-garden-test-double",
                "authorship_role": "LIVING_SYSTEM",
                "metadata": {"simulation": True, "physical_claim": False},
            },
        )
        returned_proposal = returned["proposal"]
        assert returned_proposal["status"] == "RETURNED"
        assert_proposal_is_nonbinding(returned_proposal)
        assert returned["truth_issued"] is False

        returned_coordination = returned["coordination"]
        assert returned_coordination["current_verdict"] == "OPEN"
        assert returned_coordination["living_return"]["exact_text"].startswith(
            "Simulated living-system return: six beds fit"
        )
        assert returned_coordination["living_return"]["truth_issued"] is False
        first_participant_after_return = client.get(
            "/supernet/interface",
            params={"focus_event_id": first_decision_event_id},
        ).json()
        assert (
            first_participant_after_return["visual_closure"]["coordination"][
                "active_proposal"
            ]["status"]
            == "RETURNED"
        )
        return_operator = returned_coordination["natural_form_operator"]
        assert return_operator["natural_form"] == "RETURN"
        assert return_operator["derived"] is True
        assert return_operator["user_selected_phase"] is False
        assert return_operator["token_gated_forms"] == ["ACT", "RETURN"]
        assert return_operator["interactions_gated"] is False
        assert {"inspect", "message", "ask", "decline", "revise"} <= set(
            return_operator["local_open"]
        )
        returned_continuum = assert_nrrf837_continuum_laws(
            returned_coordination,
            phase="RETURN",
            commitment_exists=True,
        )
        assert returned_continuum["global_content_id"] == stable_global_content_id
        assert returned_continuum["global_state_id"] != accepted_continuum[
            "global_state_id"
        ]
        assert returned_continuum["selected_natural_form_id"] != accepted_continuum[
            "selected_natural_form_id"
        ]

        mutual = returned_coordination["mutual_authorship"]
        assert {item["role"] for item in mutual["contributors"]} == {
            "HUMAN",
            "AI",
            "TOKEN",
            "LIVING_SYSTEM",
        }
        assert mutual["canonical_author"] is None
        assert mutual["all_sources_preserved"] is True
        assert mutual["equal_content_identifies_actors"] is False
        assert mutual["actor_identity_collapsed"] is False
        assert all(item["source_event_ids"] for item in mutual["contributors"])
        assert mutual["one_natural_form_id"] is None
        assert mutual["natural_form_equality_status"] == "OPEN"
        assert mutual["global_reading_equality_status"] == "OPEN"
        assert mutual["mutual_authorship_redundancy_applicable"] is False
        assert mutual["premise_injected"] is False
        assert any(
            item["equality_status"] == "OPEN"
            for item in mutual["contributors"]
        )
        human_contributors = {
            item["actor_id"]: item
            for item in mutual["contributors"]
            if item["role"] == "HUMAN" and item.get("contribution_type") != "RETURN"
        }
        assert {"harry", "maya"} <= set(human_contributors)
        assert first_decision_event_id in human_contributors["harry"]["event_ids"]
        assert second_decision_event_id in human_contributors["maya"]["event_ids"]
        assert second_decision_event_id not in human_contributors["harry"]["event_ids"]
        assert first_decision_event_id not in human_contributors["maya"]["event_ids"]
        assert human_contributors["harry"]["internal_actor_id"] != "harry"
        assert human_contributors["maya"]["internal_actor_id"] != "maya"

        lineage = returned_coordination["source_lineage"]
        assert lineage["intent_event_id"] == intent_event_id
        assert lineage["proposal_id"] == proposal_id
        assert set(lineage["target_event_ids"]) == {
            seeds["person"],
            seeds["project"],
            seeds["resource"],
        }
        assert len(lineage["decision_event_ids"]) == 2
        assert lineage["return_event_id"]
        return_event = app.state.runtime.supernet_store.get_event(
            lineage["return_event_id"]
        )
        assert {
            proposal["proposal_event_id"],
            first_decision_event_id,
            second_decision_event_id,
        } <= set(return_event["causal_predecessor_ids"])

        persisted_response = client.get(
            f"/supernet/interface/commitments/{proposal_id}"
        )
        assert persisted_response.status_code == 200, persisted_response.text
        persisted = persisted_response.json()
        assert persisted["proposal"]["id"] == proposal_id
        assert persisted["proposal"]["status"] == "RETURNED"
        assert persisted["coordination"]["mutual_authorship"] == mutual
        assert persisted["truth_issued"] is False

            # Every surface bound to the proposal is refreshed to the same
            # collective content/state.  Its semantic natural form remains the
            # truth class of that surface's own source return; a shared phase or
            # proposal is not allowed to manufacture equality between them.
        bound_surface_ids = [
            intent_event_id,
            proposal["proposal_event_id"],
            interaction["event_id"],
            after_acceptance["event_id"],
            first_decision_event_id,
            second_decision_event_id,
            *seeds.values(),
        ]
        for focus_event_id in bound_surface_ids:
            surface_response = client.get(
                "/supernet/interface", params={"focus_event_id": focus_event_id}
            )
            assert surface_response.status_code == 200, surface_response.text
            surface_coordination = surface_response.json()["visual_closure"][
                "coordination"
            ]
            assert surface_coordination["active_proposal"]["status"] == "RETURNED"
            surface_continuum = continuum_of(surface_coordination)
            assert surface_continuum["global_content_id"] == stable_global_content_id
            assert surface_continuum["global_state_id"] == returned_continuum[
                "global_state_id"
            ]
            assert surface_continuum["selected_natural_form_id"]
            assert surface_continuum["natural_form_admission_status"] == (
                "NATURALLY_ADMITTED"
            )
            assert surface_continuum["closure_derivation_id"]


def test_ai_authorship_cannot_accept_a_commitment_proposal(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        seeds = seed_coordination_field(client)
        intent = create_intent(client)
        intent_event_id = intent["event_id"]
        by_kind = paths_by_kind(intent["coordination"])
        created = create_commitment_proposal(
            client,
            intent_event_id=intent_event_id,
            target_event_ids=[
                by_kind["PERSON"]["target_event_id"],
                by_kind["PROJECT"]["target_event_id"],
                seeds["resource"],
            ],
        )
        proposal_id = created["proposal"]["id"]

        rejected = client.post(
            f"/supernet/interface/commitments/{proposal_id}/decisions",
            json={
                "participant_id": "coordination-ai",
                "authored_by": "coordination-ai",
                "decision": "ACCEPT",
                "exact_text": "The AI attempts to accept its own suggested path.",
                "authorship_role": "AI",
                "resource_offers": [],
                "constraints": [],
            },
        )
        assert rejected.status_code == 400, rejected.text
        detail = str(rejected.json()["detail"])
        assert "AI" in detail
        assert "accept" in detail.casefold()

        unchanged_response = client.get(
            f"/supernet/interface/commitments/{proposal_id}"
        )
        assert unchanged_response.status_code == 200, unchanged_response.text
        unchanged = unchanged_response.json()
        assert unchanged["proposal"]["status"] == "PROPOSED"
        assert unchanged["proposal"]["decisions"] == []
        assert_proposal_is_nonbinding(unchanged["proposal"])
        assert unchanged["truth_issued"] is False


def test_commitment_return_withdraw_reaccept_and_new_return_lifecycle(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        seeds = seed_coordination_field(client)
        intent = create_intent(client)
        by_kind = paths_by_kind(intent["coordination"])
        created = create_commitment_proposal(
            client,
            intent_event_id=intent["event_id"],
            target_event_ids=[
                by_kind["PERSON"]["target_event_id"],
                by_kind["PROJECT"]["target_event_id"],
                seeds["resource"],
            ],
        )
        proposal_id = created["proposal"]["id"]

        harry_accept = post(
            client,
            f"/supernet/interface/commitments/{proposal_id}/decisions",
            {
                "participant_id": "harry",
                "authored_by": "harry",
                "decision": "ACCEPT",
                "exact_text": "I accept my scoped garden contribution.",
                "authorship_role": "HUMAN",
            },
        )
        maya_accept = post(
            client,
            f"/supernet/interface/commitments/{proposal_id}/decisions",
            {
                "participant_id": "maya",
                "authored_by": "maya",
                "decision": "ACCEPT",
                "exact_text": "I independently accept my scoped garden contribution.",
                "authorship_role": "HUMAN",
            },
        )
        assert harry_accept["proposal"]["status"] == "PARTIAL"
        assert maya_accept["proposal"]["status"] == "ACCEPTED"
        first_act = assert_nrrf837_continuum_laws(
            maya_accept["coordination"],
            phase="ACT",
            commitment_exists=True,
        )
        stable_global_content_id = first_act["global_content_id"]

        first_return = post(
            client,
            f"/supernet/interface/commitments/{proposal_id}/returns",
            {
                "exact_text": (
                    "Living-system return: the first soil reading was recorded; "
                    "water access remains open."
                ),
                "authored_by": "river-street-soil-sensor",
                "authorship_role": "LIVING_SYSTEM",
                "metadata": {"simulation": True, "physical_claim": False},
            },
        )
        first_return_id = first_return["return_event_id"]
        assert first_return["proposal"]["status"] == "RETURNED"
        assert first_return["proposal"]["consent_status"] == "ACCEPTED"
        assert first_return["proposal"]["return_follows_current_acceptance"] is True
        first_return_continuum = assert_nrrf837_continuum_laws(
            first_return["coordination"],
            phase="RETURN",
            commitment_exists=True,
        )
        assert first_return_continuum["global_content_id"] == stable_global_content_id
        assert (
            first_return["coordination"]["living_return"]["authorship_role"]
            == "LIVING_SYSTEM"
        )

        withdrawn = post(
            client,
            f"/supernet/interface/commitments/{proposal_id}/decisions",
            {
                "participant_id": "maya",
                "authored_by": "maya",
                "decision": "WITHDRAW",
                "exact_text": "I withdraw until the water-access question is resolved.",
                "authorship_role": "HUMAN",
            },
        )
        assert withdrawn["proposal"]["status"] == "WITHDRAWN"
        assert withdrawn["proposal"]["consent_status"] == "WITHDRAWN"
        assert withdrawn["proposal"]["historical_return_present"] is True
        assert withdrawn["proposal"]["return_follows_current_acceptance"] is False
        assert withdrawn["coordination"]["token_gate"]["status"] == "REOPENED"
        withdrawn_continuum = assert_nrrf837_continuum_laws(
            withdrawn["coordination"],
            phase="AGREE",
            commitment_exists=True,
        )
        assert withdrawn_continuum["global_content_id"] == stable_global_content_id
        assert withdrawn_continuum["global_state_id"] != first_return_continuum[
            "global_state_id"
        ]
        assert withdrawn_continuum["selected_natural_form_id"] != (
            first_return_continuum["selected_natural_form_id"]
        )
        assert withdrawn_continuum["one_tap"]["settlement"]["settled"] is False

        gated_return = client.post(
            f"/supernet/interface/commitments/{proposal_id}/returns",
            json={
                "exact_text": "This return must not be admitted after withdrawal.",
                "authored_by": "harry",
                "authorship_role": "HUMAN",
            },
        )
        assert gated_return.status_code == 400, gated_return.text

        reaccepted = post(
            client,
            f"/supernet/interface/commitments/{proposal_id}/decisions",
            {
                "participant_id": "maya",
                "authored_by": "maya",
                "decision": "ACCEPT",
                "exact_text": (
                    "I independently re-accept after reviewing the open water condition."
                ),
                "authorship_role": "HUMAN",
            },
        )
        assert reaccepted["proposal"]["status"] == "ACCEPTED"
        assert reaccepted["proposal"]["consent_status"] == "ACCEPTED"
        assert reaccepted["proposal"]["historical_return_present"] is True
        assert reaccepted["proposal"]["return_follows_current_acceptance"] is False
        assert reaccepted["proposal"]["closure_phase"] == "ACT"
        reaccepted_continuum = assert_nrrf837_continuum_laws(
            reaccepted["coordination"],
            phase="ACT",
            commitment_exists=True,
        )
        assert reaccepted_continuum["global_content_id"] == stable_global_content_id
        assert reaccepted_continuum["global_state_id"] != withdrawn_continuum[
            "global_state_id"
        ]
        assert reaccepted_continuum["selected_natural_form_id"] != (
            withdrawn_continuum["selected_natural_form_id"]
        )
        assert reaccepted_continuum["one_tap"]["settlement"]["settled"] is True

        second_return = post(
            client,
            f"/supernet/interface/commitments/{proposal_id}/returns",
            {
                "exact_text": (
                    "Human-authored return: I checked the tap with the steward; "
                    "the irrigation schedule remains open."
                ),
                "authored_by": "harry",
                "authorship_role": "HUMAN",
                "metadata": {"first_person_report": True},
            },
        )
        assert second_return["return_event_id"] != first_return_id
        assert second_return["proposal"]["status"] == "RETURNED"
        assert second_return["proposal"]["consent_status"] == "ACCEPTED"
        assert second_return["proposal"]["return_follows_current_acceptance"] is True
        assert len(second_return["proposal"]["return_ids"]) == 2
        assert len(set(second_return["proposal"]["return_ids"])) == 2
        second_return_coordination = second_return["coordination"]
        assert second_return_coordination["living_return"]["authored_by"] == "harry"
        assert (
            second_return_coordination["living_return"]["authorship_role"]
            == "HUMAN"
        )
        return_contributors = [
            item
            for item in second_return_coordination["mutual_authorship"][
                "contributors"
            ]
            if item.get("contribution_type") == "RETURN"
        ]
        assert len(return_contributors) == 1
        assert return_contributors[0]["role"] == "HUMAN"
        assert return_contributors[0]["actor_id"] == "harry"
        assert second_return["return_event_id"] in return_contributors[0]["event_ids"]

        second_return_continuum = assert_nrrf837_continuum_laws(
            second_return_coordination,
            phase="RETURN",
            commitment_exists=True,
        )
        assert second_return_continuum["global_content_id"] == stable_global_content_id
        assert second_return_continuum["global_state_id"] != reaccepted_continuum[
            "global_state_id"
        ]
        assert second_return_continuum["selected_natural_form_id"] != (
            reaccepted_continuum["selected_natural_form_id"]
        )
        return_authorship = [
            item
            for item in second_return_continuum["authorship"]["records"]
            if second_return["return_event_id"] in item["source_event_ids"]
        ]
        assert any(
            item["actor_id"] == "harry" and item["authorship_role"] == "HUMAN"
            for item in return_authorship
        )


def test_parallel_proposals_keep_decision_authorship_scoped(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        seeds = seed_coordination_field(client)
        intent = create_intent(client)
        first = create_commitment_proposal(
            client,
            intent_event_id=intent["event_id"],
            target_event_ids=[seeds["person"], seeds["project"]],
        )
        second = post(
            client,
            "/supernet/interface/commitments",
            {
                "intent_event_id": intent["event_id"],
                "target_event_ids": [seeds["resource"]],
                "title": "Alternative garden planning proposal",
                "exact_terms": (
                    "Maya proposes a planning-only meeting with no tool budget "
                    "and no implied later commitment."
                ),
                "proposed_by": "maya",
                "perspective_id": "maya",
                "required_participant_ids": ["harry", "maya"],
                "resource_conditions": ["planning_only", "budget_usd=0"],
                "open_assumptions": ["water access remains unresolved"],
            },
        )
        first_id = first["proposal"]["id"]
        second_id = second["proposal"]["id"]
        assert first_id != second_id
        assert second["proposal"]["exact_terms"].startswith("Maya proposes")
        assert second["proposal"]["open_assumptions"] == [
            "water access remains unresolved"
        ]

        first_decision = post(
            client,
            f"/supernet/interface/commitments/{first_id}/decisions",
            {
                "participant_id": "harry",
                "authored_by": "harry",
                "decision": "ACCEPT",
                "exact_text": "I accept only the first proposal's scoped terms.",
                "authorship_role": "HUMAN",
            },
        )
        second_decision = post(
            client,
            f"/supernet/interface/commitments/{second_id}/decisions",
            {
                "participant_id": "maya",
                "authored_by": "maya",
                "decision": "REJECT",
                "exact_text": "I reject only the alternative proposal's terms.",
                "authorship_role": "HUMAN",
            },
        )

        first_surface = client.get(
            "/supernet/interface",
            params={"focus_event_id": first["proposal"]["proposal_event_id"]},
        ).json()["visual_closure"]["coordination"]
        second_surface = client.get(
            "/supernet/interface",
            params={"focus_event_id": second["proposal"]["proposal_event_id"]},
        ).json()["visual_closure"]["coordination"]
        assert first_surface["active_proposal"]["id"] == first_id
        assert second_surface["active_proposal"]["id"] == second_id
        person_resense = client.post(
            f"/supernet/events/{seeds['person']}/sense"
        )
        assert person_resense.status_code == 200, person_resense.text
        person_surface = person_resense.json()["visual_closure"]["coordination"]
        assert person_surface["active_proposal"]["id"] == first_id

        first_event_ids = {
            event_id
            for contributor in first_surface["mutual_authorship"]["contributors"]
            if contributor["role"] == "HUMAN"
            for event_id in contributor["event_ids"]
        }
        second_event_ids = {
            event_id
            for contributor in second_surface["mutual_authorship"]["contributors"]
            if contributor["role"] == "HUMAN"
            for event_id in contributor["event_ids"]
        }
        assert first_decision["decision_event_id"] in first_event_ids
        assert second_decision["decision_event_id"] not in first_event_ids
        assert second_decision["decision_event_id"] in second_event_ids
        assert first_decision["decision_event_id"] not in second_event_ids


def _demote_latest_visual_to_pre_nrrf837(
    app: Any,
    event_id: str,
    *,
    suffix: str,
    keep_nrrf837: bool = False,
) -> str:
    store = app.state.runtime.supernet_store
    row = store._conn.execute(  # noqa: SLF001 - migration-path fixture
        """SELECT id,receipt FROM supernet_visual_closure_receipts
        WHERE source_event_id=? ORDER BY seq DESC LIMIT 1""",
        (event_id,),
    ).fetchone()
    assert row is not None
    payload = json.loads(str(row["receipt"]))
    coordination = payload.get("coordination") or {}
    if not keep_nrrf837:
        coordination.pop("nrrf837_continuum", None)
        coordination.pop("continuum", None)
    payload["coordination"] = coordination
    payload.pop("translational_truth_axiometry", None)
    payload.pop("interface_natural_form", None)
    with store._lock:  # noqa: SLF001 - migration-path fixture
        store._conn.execute(  # noqa: SLF001 - migration-path fixture
            """UPDATE supernet_visual_closure_receipts
            SET input_signature=?,receipt=? WHERE id=?""",
            (
                f"pre-nrrf837:{event_id}:{suffix}",
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
                str(row["id"]),
            ),
        )
        store._conn.commit()  # noqa: SLF001 - migration-path fixture
    return str(row["id"])


def test_pre_nrrf837_latest_visual_is_lazily_upgraded_without_rewriting_history(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        first = create_intent(client)
        first_event_id = first["event_id"]
        historical_id = _demote_latest_visual_to_pre_nrrf837(
            app, first_event_id, suffix="event-route"
        )

        event_visual = client.get(
            f"/supernet/events/{first_event_id}/visual-closure"
        )
        assert event_visual.status_code == 200, event_visual.text
        upgraded = event_visual.json()
        assert upgraded["id"] != historical_id
        assert upgraded["coordination"]["nrrf837_continuum"]["schema"] == (
            "closure.supernet/nrrf837-continuum-v1"
        )
        historical = client.get(
            f"/supernet/visual-closure/receipts/{historical_id}"
        ).json()
        assert "nrrf837_continuum" not in historical["coordination"]

        second = create_intent(client)
        second_event_id = second["event_id"]
        second_historical_id = _demote_latest_visual_to_pre_nrrf837(
            app, second_event_id, suffix="primary-route"
        )
        primary = client.get(
            "/supernet/interface", params={"focus_event_id": second_event_id}
        )
        assert primary.status_code == 200, primary.text
        primary_payload = primary.json()
        assert primary_payload["visual_receipt_upgraded_to"] == (
            "closure.supernet/nrrf837-continuum-v1"
        )
        assert primary_payload["visual_closure"]["id"] != second_historical_id
        assert primary_payload["visual_closure"]["coordination"][
            "nrrf837_continuum"
        ]["schema"] == "closure.supernet/nrrf837-continuum-v1"

        third = create_intent(client)
        third_event_id = third["event_id"]
        same_schema_historical_id = _demote_latest_visual_to_pre_nrrf837(
            app,
            third_event_id,
            suffix="same-nrrf837-without-axiometry",
            keep_nrrf837=True,
        )
        same_schema_upgrade = client.get(
            f"/supernet/events/{third_event_id}/visual-closure"
        )
        assert same_schema_upgrade.status_code == 200, same_schema_upgrade.text
        same_schema_payload = same_schema_upgrade.json()
        assert same_schema_payload["id"] != same_schema_historical_id
        assert same_schema_payload["translational_truth_axiometry"]["schema"] == (
            "closure.supernet/translational-truth-axiometry-v2"
        )
        assert same_schema_payload["interface_natural_form"][
            "render_state_factorized"
        ] is True


def test_pre_nrrf837_proposal_replay_reuses_only_the_same_full_proposal(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        seeds = seed_coordination_field(client)
        intent = create_intent(client)
        payload = {
            "intent_event_id": intent["event_id"],
            "target_event_ids": [seeds["person"]],
            "title": "Legacy-compatible garden proposal",
            "exact_terms": "Harry and Maya may inspect one garden path together.",
            "proposed_by": "harry",
            "perspective_id": "harry",
            "required_participant_ids": ["harry", "maya"],
            "resource_conditions": ["inspection_only"],
            "open_assumptions": ["future consent remains open"],
        }
        created = post(client, "/supernet/interface/commitments", payload)
        proposal_id = created["proposal"]["id"]
        proposal_event_id = created["proposal"]["proposal_event_id"]
        stale_detail_id = _demote_latest_visual_to_pre_nrrf837(
            app, proposal_event_id, suffix="commitment-detail"
        )
        detail_response = client.get(
            f"/supernet/interface/commitments/{proposal_id}"
        )
        assert detail_response.status_code == 200, detail_response.text
        detail = detail_response.json()
        assert detail["coordination"]["nrrf837_continuum"]["schema"] == (
            "closure.supernet/nrrf837-continuum-v1"
        )
        assert app.state.runtime.supernet_store.latest_visual_closure_receipt(
            proposal_event_id
        )["id"] != stale_detail_id
        _demote_latest_visual_to_pre_nrrf837(
            app, proposal_event_id, suffix="idempotent-post"
        )
        legacy_signature = hashlib.sha256(
            "\x1f".join(
                [
                    intent["event_id"],
                    seeds["person"],
                    "harry",
                    payload["exact_terms"],
                ]
            ).encode("utf-8")
        ).hexdigest()
        store = app.state.runtime.supernet_store
        with store._lock:  # noqa: SLF001 - migration-path fixture
            store._conn.execute(  # noqa: SLF001 - migration-path fixture
                """UPDATE supernet_commitment_proposals SET external_key=?
                WHERE id=?""",
                (f"coordination-proposal:{legacy_signature}", proposal_id),
            )
            store._conn.commit()  # noqa: SLF001 - migration-path fixture

        before = len(store.list_commitment_proposals())
        replay = post(client, "/supernet/interface/commitments", payload)
        assert replay["proposal"]["id"] == proposal_id
        assert replay["coordination"]["nrrf837_continuum"]["schema"] == (
            "closure.supernet/nrrf837-continuum-v1"
        )
        assert len(store.list_commitment_proposals()) == before

        distinct_payload = {**payload, "title": "A genuinely different title"}
        distinct = post(
            client, "/supernet/interface/commitments", distinct_payload
        )
        assert distinct["proposal"]["id"] != proposal_id
        assert len(store.list_commitment_proposals()) == before + 1


def test_proposal_key_preserves_named_list_boundaries(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        seeds = seed_coordination_field(client)
        intent = create_intent(client)
        common = {
            "intent_event_id": intent["event_id"],
            "target_event_ids": [seeds["person"]],
            "title": "Boundary-safe proposal",
            "exact_terms": "Inspect one garden path without implied commitment.",
            "proposed_by": "harry",
            "perspective_id": "harry",
        }
        first = post(
            client,
            "/supernet/interface/commitments",
            {
                **common,
                "required_participant_ids": ["harry", "maya"],
                "resource_conditions": ["z-condition"],
            },
        )
        second = post(
            client,
            "/supernet/interface/commitments",
            {
                **common,
                "required_participant_ids": ["harry"],
                "resource_conditions": ["maya", "z-condition"],
            },
        )
        assert first["proposal"]["id"] != second["proposal"]["id"]
        assert first["proposal"]["required_participant_ids"] == ["harry", "maya"]
        assert second["proposal"]["required_participant_ids"] == ["harry"]

        perspective_a = post(
            client,
            "/supernet/interface/commitments",
            {
                **common,
                "perspective_id": "harry",
                "metadata": {"revision": 1},
                "required_participant_ids": ["harry"],
                "resource_conditions": ["perspective-scope"],
            },
        )
        perspective_b = post(
            client,
            "/supernet/interface/commitments",
            {
                **common,
                "perspective_id": "maya",
                "metadata": {"revision": 2},
                "required_participant_ids": ["harry"],
                "resource_conditions": ["perspective-scope"],
            },
        )
        assert perspective_a["proposal"]["id"] != perspective_b["proposal"]["id"]

        explicit_key_payload = {
            **common,
            "external_key": "client-proposal-key:boundary-test",
            "perspective_id": "harry",
            "metadata": {"revision": 1},
            "required_participant_ids": ["harry"],
            "resource_conditions": ["first-scope"],
        }
        post(client, "/supernet/interface/commitments", explicit_key_payload)
        participants_before_conflict = len(
            app.state.runtime.living_store.list_participants(limit=20_000)
        )
        collision = client.post(
            "/supernet/interface/commitments",
            json={
                **explicit_key_payload,
                "perspective_id": "maya",
                "metadata": {"revision": 2},
                "required_participant_ids": ["harry", "ghost-handle"],
            },
        )
        assert collision.status_code == 400
        assert "already bound to different" in collision.json()["detail"]
        assert len(
            app.state.runtime.living_store.list_participants(limit=20_000)
        ) == participants_before_conflict

        explicit_namespace_payload = {
            **common,
            "required_participant_ids": ["harry"],
            "resource_conditions": ["explicit-namespace"],
        }
        explicit_one = post(
            client,
            "/supernet/interface/commitments",
            {
                **explicit_namespace_payload,
                "external_key": "client-proposal-key:one",
            },
        )
        explicit_two = post(
            client,
            "/supernet/interface/commitments",
            {
                **explicit_namespace_payload,
                "external_key": "client-proposal-key:two",
            },
        )
        assert explicit_one["proposal"]["id"] != explicit_two["proposal"]["id"]
        assert explicit_one["proposal"]["action_id"] != explicit_two["proposal"][
            "action_id"
        ]
        assert explicit_one["proposal"]["external_key"] == (
            "client-proposal-key:one"
        )
        assert explicit_two["proposal"]["external_key"] == (
            "client-proposal-key:two"
        )


def test_concurrent_same_proposal_creates_one_action_and_one_proposal(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        seeds = seed_coordination_field(client)
        intent = create_intent(client)
        payload = {
            "intent_event_id": intent["event_id"],
            "target_event_ids": [seeds["person"]],
            "title": "Concurrent idempotency proposal",
            "exact_terms": "Create exactly one action for this exact request.",
            "proposed_by": "harry",
            "perspective_id": "harry",
            "required_participant_ids": ["harry", "maya"],
            "resource_conditions": ["one-action-only"],
            "metadata": {"race_fixture": True},
        }
        runtime = app.state.runtime
        action_count_before = len(runtime.living_store.list_actions(limit=20_000))
        proposal_count_before = len(
            runtime.supernet_store.list_commitment_proposals(limit=20_000)
        )
        original_create_action = runtime.living.create_action
        create_action_calls = 0

        async def slowed_create_action(data: Any) -> dict[str, Any]:
            nonlocal create_action_calls
            create_action_calls += 1
            await asyncio.sleep(0.05)
            return await original_create_action(data)

        runtime.living.create_action = slowed_create_action

        async def race() -> list[httpx.Response]:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as async_client:
                return list(
                    await asyncio.gather(
                        async_client.post(
                            "/supernet/interface/commitments", json=payload
                        ),
                        async_client.post(
                            "/supernet/interface/commitments", json=payload
                        ),
                    )
                )

        try:
            responses = asyncio.run(race())
        finally:
            runtime.living.create_action = original_create_action

        assert all(response.status_code == 200 for response in responses)
        bodies = [response.json() for response in responses]
        proposal_ids = {body["proposal"]["id"] for body in bodies}
        assert len(proposal_ids) == 1
        proposal_action_ids = {body["proposal"]["action_id"] for body in bodies}
        assert len(proposal_action_ids) == 1
        assert create_action_calls == 1
        assert len(runtime.living_store.list_actions(limit=20_000)) == (
            action_count_before + 1
        )
        assert len(
            runtime.supernet_store.list_commitment_proposals(limit=20_000)
        ) == proposal_count_before + 1
        for body in bodies:
            if body.get("action") is not None:
                assert body["action"]["id"] == body["proposal"]["action_id"]
