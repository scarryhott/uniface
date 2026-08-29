from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from closure_supernet.api_natural_interface import create_app
from closure_supernet.config import RuntimeConfig


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
    assert intent_event_id in why["source_event_ids"]
    assert path["target_event_id"] in why["source_event_ids"]


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
        assert proposal["required_participant_ids"] == ["harry", "maya"]
        assert proposal["decisions"] == []
        assert_proposal_is_nonbinding(proposal)

        proposed_coordination = created["coordination"]
        proposed_operator = proposed_coordination["natural_form_operator"]
        assert proposed_operator["natural_form"] == "AGREE"
        assert proposed_operator["token_gated_forms"] == ["ACT", "RETURN"]
        assert proposed_operator["interactions_gated"] is False
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

        mutual = returned_coordination["mutual_authorship"]
        assert {item["role"] for item in mutual["contributors"]} == {
            "HUMAN",
            "AI",
            "TOKEN",
            "LIVING",
        }
        assert mutual["canonical_author"] is None
        assert mutual["all_sources_preserved"] is True
        assert all(item["source_event_ids"] for item in mutual["contributors"])
        assert len({item["natural_form_id"] for item in mutual["contributors"]}) == 1

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

        persisted_response = client.get(
            f"/supernet/interface/commitments/{proposal_id}"
        )
        assert persisted_response.status_code == 200, persisted_response.text
        persisted = persisted_response.json()
        assert persisted["proposal"]["id"] == proposal_id
        assert persisted["proposal"]["status"] == "RETURNED"
        assert persisted["coordination"]["mutual_authorship"] == mutual
        assert persisted["truth_issued"] is False


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
