from __future__ import annotations

from copy import deepcopy
from typing import Any

from closure_supernet.nrrf837_continuum import (
    append_local,
    build_continuum_receipt,
    canonical_hash,
    canonical_json,
    compose_pointwise,
    unity_form,
)


def community_garden_inputs(
    *,
    selector_version: str = "berkeley-garden-unity-v1",
    selector_source: str = "Berkeley garden participants",
    proposal: dict[str, Any] | None = None,
) -> dict[str, Any]:
    intent = {
        "id": "event-intent-harry",
        "event_id": "event-intent-harry",
        "exact_text": "I want to start a community garden.",
        "authored_by": "harry",
        "perspective_id": "harry",
        "exact_source_ids": ["source-harry-thought-1"],
        "source_occurrence_ids": ["source-harry-thought-1"],
        "metadata": {"authorship_role": "HUMAN"},
    }
    field_events = [
        {
            "id": "event-person-maya",
            "exact_text": (
                "Maya wants to help start a Berkeley community garden and can "
                "share composting experience on weekends."
            ),
            "authored_by": "maya",
            "perspective_id": "maya",
            "exact_source_ids": ["source-maya-profile-1"],
            "metadata": {
                "authorship_role": "HUMAN",
                "coordination_kind": "PERSON",
            },
        },
        {
            "id": "event-project-river-street",
            "exact_text": (
                "River Street Garden has six open beds and seeks weekend "
                "organizers; water access remains unresolved."
            ),
            "authored_by": "river-street-steward",
            "perspective_id": "river-street-steward",
            "exact_source_ids": ["source-river-street-project-1"],
            "metadata": {
                "authorship_role": "HUMAN",
                "coordination_kind": "PROJECT",
            },
        },
        {
            "id": "event-resource-agreement-template",
            "exact_text": (
                "Editable community-garden agreement template; it is not "
                "binding and requires each participant's acceptance."
            ),
            "authored_by": "proposal-library",
            "perspective_id": "proposal-library",
            "exact_source_ids": ["source-garden-template-1"],
            "metadata": {
                "authorship_role": "HUMAN",
                "coordination_kind": "RESOURCE",
            },
        },
    ]
    paths = [
        {
            "id": "path-person-maya",
            "target_event_id": "event-person-maya",
            "kind": "PERSON",
            "score": 0.91,
            "natural_form_id": "garden-collaboration",
            "why": {
                "matched_features": ["community garden", "Berkeley", "weekends"],
                "source_event_ids": ["event-intent-harry", "event-person-maya"],
            },
        },
        {
            "id": "path-project-river-street",
            "target_event_id": "event-project-river-street",
            "kind": "PROJECT",
            "score": 0.86,
            "natural_form_id": "garden-collaboration",
            "why": {
                "matched_features": ["community garden", "Berkeley", "organizers"],
                "source_event_ids": [
                    "event-intent-harry",
                    "event-project-river-street",
                ],
            },
        },
        {
            "id": "path-resource-agreement-template",
            "target_event_id": "event-resource-agreement-template",
            "kind": "RESOURCE",
            "score": 0.78,
            "natural_form_id": "garden-collaboration",
            "why": {
                "matched_features": ["community garden", "agreement", "consent"],
                "source_event_ids": [
                    "event-intent-harry",
                    "event-resource-agreement-template",
                ],
            },
        },
    ]
    active_proposal = proposal or {
        "id": "proposal-river-street",
        "status": "PROPOSED",
        "proposed_by": "harry",
        "required_participant_ids": ["harry", "maya"],
        "target_event_ids": [
            "event-person-maya",
            "event-project-river-street",
            "event-resource-agreement-template",
        ],
        "resource_conditions": [
            "tools_only",
            "budget_usd<=25",
            "requires both participant acceptances",
        ],
        "decisions": [],
        "binding": False,
        "truth_issued": False,
    }
    return {
        "local_event": intent,
        "intent": intent,
        "field_events": field_events,
        "paths": paths,
        "active_proposal": active_proposal,
        "living_return": None,
        "operator": {
            "natural_form": "AGREE",
            "selector_version": selector_version,
            "selector_source": selector_source,
        },
        "enabled_forms": ["DISCOVER", "CONNECT", "AGREE"],
        "freedom_actions": ["inspect", "message", "ask", "decline", "revise"],
        "closure_level_id": "garden-collaboration",
        "contributors": [
            {
                "role": "HUMAN",
                "actor_id": "harry",
                "source_event_ids": ["event-intent-harry"],
                "natural_form_id": "garden-collaboration",
            },
            {
                "role": "AI",
                "actor_id": "coordination-ai",
                "source_event_ids": [
                    "path-person-maya",
                    "path-project-river-street",
                ],
                "natural_form_id": "garden-collaboration",
            },
            {
                "role": "TOKEN",
                "actor_id": "proposal-river-street",
                "source_event_ids": ["proposal-river-street"],
                "natural_form_id": "garden-collaboration",
            },
            {
                "role": "LIVING_SYSTEM",
                "actor_id": "river-street-garden",
                "source_event_ids": ["event-project-river-street"],
                "natural_form_id": "garden-collaboration",
            },
        ],
        "token_status": {
            "status": "PROPOSED",
            "gated_forms": ["ACT", "RETURN"],
            "interactions_gated": False,
        },
    }


def test_nrrf837_computes_monoid_homomorphism_and_selector_laws() -> None:
    identity: list[str] = []
    thought = ["local:intent"]
    coordination = ["local:ask", "local:propose"]
    return_word = ["local:return"]
    atom_map = {
        "local:intent": "global:garden",
        "local:ask": "global:garden",
        "local:propose": "global:agreement",
        "local:return": "global:living-return",
    }

    assert append_local(identity, thought) == thought
    assert append_local(thought, identity) == thought
    assert append_local(append_local(thought, coordination), return_word) == (
        append_local(thought, append_local(coordination, return_word))
    )
    assert compose_pointwise(identity, atom_map) == identity
    assert compose_pointwise(append_local(thought, coordination), atom_map) == (
        append_local(
            compose_pointwise(thought, atom_map),
            compose_pointwise(coordination, atom_map),
        )
    )

    # Canonical composition is source-order independent for object keys, while
    # the chosen unity presentation is deliberately selector-version dependent.
    assert canonical_json({"b": 2, "a": 1}) == canonical_json({"a": 1, "b": 2})
    assert canonical_hash({"b": 2, "a": 1}) == canonical_hash({"a": 1, "b": 2})
    assert unity_form(
        "global:garden", selector_version="garden-unity-v1"
    ) != unity_form("global:garden", selector_version="garden-unity-v2")


def test_nrrf837_receipt_computes_continuum_laws_and_preserves_provenance() -> None:
    inputs = community_garden_inputs()
    receipt = build_continuum_receipt(**inputs)

    assert receipt["protocol"] == "NRRF837"
    assert receipt["receipt_id"] == canonical_hash(
        {key: value for key, value in receipt.items() if key != "receipt_id"}
    )

    assert receipt["local_monoid"]["associative"] is True
    assert receipt["local_monoid"]["identity_verified"] is True
    assert receipt["compose"]["identity_preserved"] is True
    assert receipt["compose"]["concatenation_preserved"] is True
    assert receipt["compose"]["homomorphism_verified"] is True

    modality = receipt["modality"]
    assert modality["first_application"] == modality["second_application"]
    assert modality["presentation"]["id"] == modality["first_application"][0]
    assert modality["form"]["derived_within_closure"] is True
    assert modality["defines_closure"] is False
    assert modality["idempotent"] is True
    assert modality["fixed_point"] is True
    assert modality["fixed_points_equal_unity"] is True
    assert modality["fixed_points_equal_unity_scope"] == (
        "declared finite generator/unity domain only"
    )
    assert set(modality["declared_fixed_point_ids"]) == set(
        modality["declared_unity_ids"]
    )

    selector = receipt["unity_selector"]
    assert selector["global_states_in_bijection_with_selected_forms"] is True
    assert len(selector["declared_global_states"]) == len(
        selector["declared_unity"]
    )
    assert {
        tuple(item["global_word"]): item["id"]
        for item in selector["declared_unity"]
    }.keys() == {tuple(item) for item in selector["declared_global_states"]}

    freedom = receipt["freedom_fibre"]
    assert freedom["nonempty"] is True
    assert len(freedom["unity_witnesses"]) == 1
    assert freedom["exactly_one_unity_witness"] is True
    assert modality["fixed_point_witnesses"] == freedom["unity_witnesses"]
    assert freedom["canonical_unity_witness_id"] == modality["form"]["id"]
    assert len(freedom["local_presentations"]) > len(freedom["unity_witnesses"])
    assert set(freedom["local_actions"]) == set(inputs["freedom_actions"])

    # Equality of translated content identifies a contribution in the closure,
    # not the executor, AI, token, or living-system actor that authored it.
    authorship = receipt["authorship"]
    assert authorship["source_identities_preserved"] is False
    assert {"coordination-ai", "proposal-river-street"} <= set(
        authorship["missing_source_identity_actor_ids"]
    )
    assert authorship["equal_global_content_identifies_actors"] is False
    assert {item["authorship_role"] for item in authorship["contributors"]} == {
        "HUMAN",
        "AI",
        "TOKEN",
        "LIVING_SYSTEM",
    }
    assert {
        "harry",
        "coordination-ai",
        "proposal-river-street",
        "river-street-garden",
    } <= {item["actor_id"] for item in authorship["contributors"]}
    assert all(
        item["record_kind"] == "CONTRIBUTOR_AUTHORSHIP"
        for item in authorship["contributor_records"]
    )
    assert any(
        item["equality_status"] == "OPEN"
        for item in authorship["contributor_records"]
    )
    assert all(
        item["authored_form_claim_is_truth_witness"] is False
        for item in authorship["contributor_records"]
    )
    assert authorship["mutual_authorship_redundancy_applicable"] is False
    assert authorship["mutual_authorship_redundancy_premise"] == {
        "relevant_contributor_count": 4,
        "all_contributors_witnessed": False,
        "same_witnessed_global_reading": False,
        "same_witnessed_natural_form": False,
        "premise_injected": False,
    }
    assert any(
        len(group["actor_ids"]) > 1 and group["actors_identified"] is False
        for group in authorship["equal_content_groups"]
    )


def test_nrrf837_separates_suggestion_ranking_gates_and_commitment() -> None:
    inputs = community_garden_inputs()
    receipt = build_continuum_receipt(**inputs)

    suggestions = receipt["suggestions"]
    equivalence = suggestions["equivalence"]
    assert equivalence["relation"] == "form(compose(x)) = form(compose(y))"
    assert equivalence["reflexive"] is True
    assert equivalence["symmetric"] is True
    assert equivalence["transitive"] is True
    assert equivalence["verified"] is True
    ranked = suggestions["contextual_ranked_edges"]
    assert [edge["score"] for edge in ranked] == sorted(
        (path["score"] for path in inputs["paths"]), reverse=True
    )
    assert suggestions["ranking_is_contextual_not_equivalence"] is True
    assert suggestions["global_optimum_claimed"] is False
    # Contextual similarity does not manufacture formal equality.  These
    # source events carry distinct content and no shared authored equality key.
    assert all(edge["formal_status"] == "OPEN" for edge in ranked)
    assert all(edge["shared_natural_form"] is False for edge in ranked)
    assert suggestions["formally_witnessed_edge_ids"] == []
    assert set(suggestions["form_equality_open_edge_ids"]) == {
        path["id"] for path in inputs["paths"]
    }

    gates = receipt["gates"]
    assert gates["token"]["gates_forms"] is True
    assert set(gates["token"]["gated_forms"]) == {"ACT", "RETURN"}
    assert gates["token"]["gates_ordinary_interactions"] is False
    assert gates["token"]["blind_to_ordinary_interaction"] is True
    assert gates["ai"]["mediates_suggestions"] is True
    assert set(gates["ai"]["admitted_interactions"]) == {
        path["target_event_id"] for path in inputs["paths"]
    }
    assert gates["ai"]["controls_form_admission"] is False
    assert gates["ai"]["blind_to_form_admission"] is True
    assert gates["ai"]["can_consent"] is False
    assert gates["ai"]["can_bind"] is False
    assert gates["joint_product"]["product_witness"]
    assert gates["joint_product"]["relation_equals_cartesian_product"] is True
    assert gates["joint_product"]["independent_coordinates"] is True

    commitment = receipt["commitment_relation"]
    assert commitment["correlated"] is True
    assert commitment["separate_from_product_gates"] is True
    assert commitment["non_product_realisable_by_independent_gates"] is False

    one_tap = receipt["one_tap"]
    assert one_tap["nonbinding_proposal"] is True
    settlement = one_tap["settlement"]
    assert settlement["required_participant_ids"] == ["harry", "maya"]
    assert settlement["human_acceptances"] == []
    assert settlement["all_required_humans_accepted"] is False
    assert settlement["requires_independent_human_acceptance"] is True
    assert settlement["settled"] is False


def test_nrrf837_path_form_equality_requires_actual_compose_equality() -> None:
    inputs = community_garden_inputs()
    inputs["intent"]["global_content_id"] = "authored-form-A"
    inputs["local_event"] = inputs["intent"]
    inputs["field_events"][0]["global_content_id"] = "authored-form-B"
    inputs["field_events"][1]["global_content_id"] = "authored-form-A"

    receipt = build_continuum_receipt(**inputs)
    edges = {
        item["target_event_id"]: item
        for item in receipt["suggestions"]["contextual_ranked_edges"]
    }

    unequal = edges["event-person-maya"]
    assert unequal["formal_status"] == "OPEN"
    assert unequal["shared_natural_form"] is False
    assert unequal["natural_form_id"] is None
    assert unequal["source_natural_form_id"] != unequal["target_natural_form_id"]

    authored_same = edges["event-project-river-street"]
    assert authored_same["formal_status"] == "OPEN"
    assert authored_same["shared_natural_form"] is False
    assert authored_same["natural_form_id"] is None
    assert authored_same["source_natural_form_id"] != authored_same[
        "target_natural_form_id"
    ]


def test_authored_form_id_cannot_collapse_truth_derived_global_kernel() -> None:
    inputs = community_garden_inputs()
    inputs["intent"]["natural_form_id"] = "authored-same"
    inputs["field_events"][0]["natural_form_id"] = "authored-same"
    inputs["local_event"] = inputs["intent"]

    receipt = build_continuum_receipt(**inputs)
    kernel = receipt["global_equality_kernel"]
    assert kernel["authored_ids_define_equality"] is False
    assert kernel["presentation_metadata_defines_equality"] is False
    classes = [set(item["members"]) for item in kernel["classes"]]
    assert not any(
        {"event-intent-harry", "event-person-maya"} <= members
        for members in classes
    )


def test_nrrf837_missing_blank_path_references_remain_distinct_and_open() -> None:
    inputs = community_garden_inputs()
    inputs["paths"] = [
        {
            "id": "missing-path-a",
            "target_event_id": "missing-event-a",
            "score": 0.9,
            "why": {"source_event_id": "event-intent-harry"},
        },
        {
            "id": "missing-path-b",
            "target_event_id": "missing-event-b",
            "score": 0.8,
            "why": {"source_event_id": "event-intent-harry"},
        },
    ]
    receipt = build_continuum_receipt(**inputs)
    edges = receipt["suggestions"]["contextual_ranked_edges"]
    assert [edge["formal_status"] for edge in edges] == ["OPEN", "OPEN"]
    assert all(edge["shared_natural_form"] is False for edge in edges)
    assert all(edge["target_natural_form_id"] is None for edge in edges)
    atom_map = receipt["compose"]["atom_map"]
    assert atom_map["missing-event-a"] != atom_map["missing-event-b"]
    unknown_records = {
        item["source_event_ids"][0]: item
        for item in receipt["authorship"]["event_authorship_records"]
        if item["source_event_ids"][0] in {"missing-event-a", "missing-event-b"}
    }
    assert set(unknown_records) == {"missing-event-a", "missing-event-b"}
    for record in unknown_records.values():
        assert record["equality_status"] == "OPEN"
        assert record["equality_basis"] == "UNRESOLVED_TRANSLATIONAL_TRUTH"
        assert record["global_word"] is None
        assert record["global_content_id"] is None
        assert record["global_state_id"] is None
        assert record["selected_natural_form_id"] is None


def test_nrrf837_global_state_is_focus_and_ranking_independent_but_phase_sensitive() -> None:
    inputs = community_garden_inputs()
    intent_focus = build_continuum_receipt(**inputs)

    target_inputs = deepcopy(inputs)
    target_inputs["local_event"] = target_inputs["field_events"][0]
    target_focus = build_continuum_receipt(**target_inputs)
    assert target_focus["local_event_id"] != intent_focus["local_event_id"]
    assert target_focus["global_content_id"] == intent_focus["global_content_id"]
    assert target_focus["global_state_id"] == intent_focus["global_state_id"]
    assert target_focus["selected_natural_form_id"] != intent_focus[
        "selected_natural_form_id"
    ]
    assert target_focus["modality"]["input"] == intent_focus["modality"]["input"]

    reranked_inputs = deepcopy(inputs)
    reranked_inputs["paths"][0]["score"] = 0.01
    reranked_inputs["paths"][1]["score"] = 0.99
    reranked = build_continuum_receipt(**reranked_inputs)
    assert reranked["global_state_id"] == intent_focus["global_state_id"]
    assert (
        reranked["selected_natural_form_id"]
        == intent_focus["selected_natural_form_id"]
    )

    next_phase_inputs = deepcopy(inputs)
    next_phase_inputs["operator"]["natural_form"] = "ACT"
    next_phase = build_continuum_receipt(**next_phase_inputs)
    assert next_phase["global_content_id"] == intent_focus["global_content_id"]
    assert next_phase["global_state_id"] != intent_focus["global_state_id"]
    assert next_phase["selected_natural_form_id"] == intent_focus[
        "selected_natural_form_id"
    ]

    other_level_inputs = deepcopy(inputs)
    other_level_inputs["closure_level_id"] = "different-local-nrrf825-level"
    other_level = build_continuum_receipt(**other_level_inputs)
    assert other_level["global_state_id"] == intent_focus["global_state_id"]
    assert (
        other_level["selected_natural_form_id"]
        == intent_focus["selected_natural_form_id"]
    )


def test_nrrf837_public_author_and_internal_actor_remain_distinct_and_sourced() -> None:
    inputs = community_garden_inputs()
    inputs["field_events"][0]["authored_by"] = "participant-uuid-maya"
    inputs["field_events"][0]["metadata"].update(
        {
            "authored_handle": "maya",
            "created_by": "participant-uuid-maya",
        }
    )
    receipt = build_continuum_receipt(**inputs)
    maya = next(
        item
        for item in receipt["authorship"]["event_authorship_records"]
        if item["source_event_ids"] == ["event-person-maya"]
    )
    assert maya["actor_id"] == "maya"
    assert maya["internal_actor_id"] == "participant-uuid-maya"
    assert maya["source_identity_status"] == "WITNESSED"
    assert receipt["authorship"]["source_identities_preserved"] is False
    assert "coordination-ai" in receipt["authorship"][
        "missing_source_identity_actor_ids"
    ]

    missing_inputs = deepcopy(inputs)
    missing_inputs["contributors"].append(
        {
            "role": "AI",
            "actor_id": "unsourced-ai",
            "source_event_ids": [],
        }
    )
    missing = build_continuum_receipt(**missing_inputs)
    assert missing["authorship"]["source_identities_preserved"] is False
    assert "unsourced-ai" in missing["authorship"][
        "missing_source_identity_actor_ids"
    ]


def test_nrrf837_equal_content_preserves_same_handle_distinct_internal_actors() -> None:
    inputs = community_garden_inputs()
    for event, internal_actor_id in zip(
        inputs["field_events"][:2],
        ["participant-uuid-one", "participant-uuid-two"],
        strict=True,
    ):
        event["global_content_id"] = "shared-authored-reading"
        event["metadata"].update(
            {
                "authored_handle": "shared-steward",
                "created_by": internal_actor_id,
            }
        )

    authorship = build_continuum_receipt(**inputs)["authorship"]
    expected_identities = {
        ("shared-steward", "participant-uuid-one"),
        ("shared-steward", "participant-uuid-two"),
    }
    records = [
        item
        for item in authorship["event_authorship_records"]
        if (item["actor_id"], item["internal_actor_id"]) in expected_identities
    ]
    assert {
        (item["actor_id"], item["internal_actor_id"]) for item in records
    } == expected_identities
    assert all(
        item["equality_basis"]
        == "NRRF840_VIS_CLOSURE_TRANSLATIONAL_TRUTHS"
        for item in records
    )
    assert len({item["selected_natural_form_id"] for item in records}) == 2
    assert authorship["equal_global_content_identifies_actors"] is False


def test_nrrf837_contributor_redundancy_requires_witnessed_equal_readings() -> None:
    equal_receipt = build_continuum_receipt(**community_garden_inputs())
    equal_authorship = equal_receipt["authorship"]
    assert equal_authorship["mutual_authorship_redundancy_applicable"] is False
    assert all(
        item["mutual_authorship_redundancy_applicable"] is False
        for item in equal_authorship["contributor_records"]
    )

    mismatched_inputs = community_garden_inputs()
    mismatched_inputs["contributors"][1]["natural_form_id"] = (
        "different-authored-form"
    )
    mismatched = build_continuum_receipt(**mismatched_inputs)["authorship"]
    assert mismatched["mutual_authorship_redundancy_applicable"] is False
    ai_record = next(
        item
        for item in mismatched["contributor_records"]
        if item["actor_id"] == "coordination-ai"
    )
    assert ai_record["authored_form_claim_is_truth_witness"] is False

    unknown_inputs = community_garden_inputs()
    unknown = unknown_inputs["contributors"][1]
    unknown.pop("natural_form_id")
    unknown["source_event_ids"] = ["unresolved-ai-path"]
    unknown_receipt = build_continuum_receipt(**unknown_inputs)["authorship"]
    unknown_record = next(
        item
        for item in unknown_receipt["contributor_records"]
        if item["actor_id"] == "coordination-ai"
    )
    assert unknown_record["equality_status"] == "OPEN"
    assert unknown_record["equality_basis"] == "UNRESOLVED_TRANSLATIONAL_TRUTH"
    assert unknown_record["global_content_id"] is None
    assert unknown_record["selected_natural_form_id"] is None
    assert unknown_record["unresolved_source_event_ids"] == [
        "unresolved-ai-path"
    ]
    assert unknown_receipt["mutual_authorship_redundancy_applicable"] is False
    assert unknown_receipt["mutual_authorship_redundancy_premise"][
        "all_contributors_witnessed"
    ] is False

    resolved_inputs = community_garden_inputs()
    resolved = resolved_inputs["contributors"][0]
    resolved.pop("natural_form_id")
    resolved["source_event_ids"] = ["event-intent-harry"]
    resolved_record = next(
        item
        for item in build_continuum_receipt(**resolved_inputs)["authorship"][
            "contributor_records"
        ]
        if item["actor_id"] == "harry"
    )
    assert resolved_record["equality_status"] == "WITNESSED"
    assert resolved_record["equality_basis"] == (
        "NRRF840_VIS_CLOSURE_TRANSLATIONAL_TRUTHS"
    )


def test_nrrf837_ai_acceptance_cannot_settle_but_independent_humans_can() -> None:
    proposal = community_garden_inputs()["active_proposal"]
    proposal["status"] = "ACCEPTED"
    proposal["decisions"] = [
        {
            "participant_id": "harry",
            "decision": "ACCEPT",
            "authorship_role": "HUMAN",
            "decision_event_id": "decision-harry",
        },
        {
            "participant_id": "maya",
            "decision": "ACCEPT",
            "authorship_role": "AI",
            "decision_event_id": "decision-ai-for-maya",
        },
    ]
    ai_receipt = build_continuum_receipt(
        **community_garden_inputs(proposal=proposal)
    )
    ai_settlement = ai_receipt["one_tap"]["settlement"]
    assert ai_receipt["gates"]["ai"]["can_consent"] is False
    assert [
        item["participant_id"] for item in ai_settlement["human_acceptances"]
    ] == ["harry"]
    assert ai_settlement["all_required_humans_accepted"] is False
    assert ai_settlement["settled"] is False

    human_proposal = deepcopy(proposal)
    human_proposal["decisions"][1]["authorship_role"] = "HUMAN"
    human_proposal["decisions"][1]["decision_event_id"] = "decision-maya"
    human_receipt = build_continuum_receipt(
        **community_garden_inputs(proposal=human_proposal)
    )
    human_settlement = human_receipt["one_tap"]["settlement"]
    assert {
        item["participant_id"] for item in human_settlement["human_acceptances"]
    } == {"harry", "maya"}
    assert human_settlement["all_required_humans_accepted"] is True
    assert human_settlement["settled"] is True
    assert human_receipt["one_tap"]["nonbinding_proposal"] is True


def test_nrrf837_unity_is_versioned_extra_data_and_issues_no_truth_or_value() -> None:
    v1 = build_continuum_receipt(
        **community_garden_inputs(
            selector_version="berkeley-garden-unity-v1",
            selector_source="participants adopted garden policy v1",
        )
    )
    v2 = build_continuum_receipt(
        **community_garden_inputs(
            selector_version="berkeley-garden-unity-v2",
            selector_source="participants adopted garden policy v2",
        )
    )

    selector = v1["unity_selector"]
    assert selector["version"] == "berkeley-garden-unity-v1"
    assert selector["source"] == "participants adopted garden policy v1"
    assert selector["network_derived"] is False
    assert selector["extra_data"] is True
    alternative = selector["alternative_selector_witness"]
    assert alternative["same_local_and_global_monoids"] is True
    assert alternative["same_compose"] is True
    assert alternative["same_global_word"] is True
    assert alternative["distinct"] is True
    assert alternative["alternative_is_not_active_unity"] is True
    assert v2["unity_selector"]["version"] == "berkeley-garden-unity-v2"
    assert v1["global_monoid"] == v2["global_monoid"]
    assert v1["global_equality_kernel"] == v2["global_equality_kernel"]
    assert v1["selected_natural_form_id"] == v2["selected_natural_form_id"]
    assert v1["modality"]["form"] == v2["modality"]["form"]
    assert v1["modality"]["presentation"] != v2["modality"]["presentation"]

    for receipt in (v1, v2):
        claims = receipt["claims"]
        assert claims["truth_issued"] is False
        assert claims["economic_claim_made"] is False
        assert claims["value_claim_made"] is False
        assert claims["optimality_claim_made"] is False
REMOTE_NRRF837_REFERENCE_TESTS = r'''
from closure_supernet.nrrf837 import (
    attach_continuum_to_visual_receipt,
    derive_continuum_receipt,
)


def continuum_fixture():
    events = [
        {
            "id": "event-a",
            "seq": 1,
            "exact_source_ids": ["a"],
            "authored_by": "maya",
            "current_stage": "SOURCE_PRESERVED",
            "metadata": {"nrrf837_unity": True},
        },
        {
            "id": "event-b",
            "seq": 2,
            "exact_source_ids": ["b"],
            "authored_by": "harry",
            "current_stage": "SOURCE_PRESERVED",
            "metadata": {},
        },
        {
            "id": "event-c",
            "seq": 3,
            "exact_source_ids": ["c"],
            "authored_by": "other",
            "current_stage": "SOURCE_PRESERVED",
            "metadata": {},
        },
        {
            "id": "event-proposal",
            "seq": 4,
            "exact_source_ids": ["p"],
            "authored_by": "harry",
            "current_stage": "COMMITTED",
            "metadata": {},
        },
    ]
    occurrences = [
        {"id": "a", "exact_text": "canonical garden collaboration"},
        {"id": "b", "exact_text": "I want to start a garden"},
        {"id": "c", "exact_text": "unrelated project"},
        {"id": "p", "exact_text": "garden agreement"},
    ]
    level = {
        "level_id": "level-1",
        "truth_closes_level_alone": {
            "natural_forms": [
                {
                    "natural_form": "L/0",
                    "members": ["a", "b"],
                    "representative_is_not_privileged": True,
                },
                {
                    "natural_form": "L/1",
                    "members": ["c"],
                    "representative_is_not_privileged": True,
                },
                {
                    "natural_form": "L/2",
                    "members": ["p"],
                    "representative_is_not_privileged": True,
                },
            ]
        },
    }
    coordination = {
        "intent_event_id": "event-b",
        "intent": {"event_id": "event-b"},
        "paths": [
            {
                "id": "path-a",
                "target_event_id": "event-a",
                "why": {},
            },
            {
                "id": "path-c",
                "target_event_id": "event-c",
                "why": {},
            },
        ],
        "active_proposal": {
            "proposal_event_id": "event-proposal",
            "target_event_ids": ["event-a"],
            "required_participant_ids": ["harry", "maya"],
            "resource_conditions": ["budget<=25"],
            "exact_terms": "two hours and tools",
            "status": "ACCEPTED",
        },
        "natural_form_operator": {
            "enabled_forms": [
                "DISCOVER",
                "CONNECT",
                "AGREE",
                "COMMIT",
                "ACT",
                "RETURN",
            ],
            "local_open": ["inspect", "message", "revise"],
        },
        "token_gate": {
            "gated_forms": ["ACT", "RETURN"],
            "currency_issued": False,
        },
        "mutual_authorship": {
            "contributors": [
                {
                    "role": "HUMAN",
                    "event_ids": ["event-b"],
                    "source_event_ids": ["event-b"],
                    "source_reverse_path": ["b"],
                },
                {
                    "role": "AI",
                    "event_ids": ["event-a"],
                    "source_event_ids": ["event-a"],
                    "source_reverse_path": ["a"],
                },
                {
                    "role": "LIVING",
                    "event_ids": ["event-a"],
                    "source_event_ids": ["event-a"],
                    "source_reverse_path": ["a"],
                },
            ]
        },
    }
    return events, occurrences, level, coordination


def test_active_continuum_audits_modality_unity_and_freedom():
    events, occurrences, level, coordination = continuum_fixture()
    receipt = derive_continuum_receipt(
        event=events[1],
        field_events=events,
        field_occurrences=occurrences,
        relation_receipts=[],
        closure_level=level,
        coordination=coordination,
    )

    structure = receipt["structure"]
    compose = structure["compose"]["active_generator_map"]
    form = structure["form"]["active_map"]
    modality = structure["modality"]["active_map"]

    assert compose["a"] == compose["b"]
    assert form[compose["a"]] == "a"
    assert modality["a"] == "a"
    assert modality["b"] == "a"
    assert modality[modality["b"]] == modality["b"]
    assert structure["unity"]["selected_local_ids"] == ["a", "c", "p"]
    assert receipt["active_form"]["freedom_range_size"] == 2
    assert receipt["audits"]["all_active_finite_audits_pass"] is True
    assert receipt["audits"]["non_vacuous_multi_point_freedom_range"] is True


def test_suggestions_distinguish_shared_form_from_open_ai_candidate():
    events, occurrences, level, coordination = continuum_fixture()
    receipt = derive_continuum_receipt(
        event=events[1],
        field_events=events,
        field_occurrences=occurrences,
        relation_receipts=[],
        closure_level=level,
        coordination=coordination,
    )

    by_id = {path["id"]: path for path in coordination["paths"]}
    assert by_id["path-a"]["natural_form_suggestion"] is True
    assert (
        by_id["path-a"]["why"]["nrrf837"]["suggestion_relation"]
        == "SAME_NATURAL_FORM"
    )
    assert by_id["path-c"]["natural_form_suggestion"] is False
    assert (
        by_id["path-c"]["why"]["nrrf837"]["suggestion_relation"]
        == "OPEN_AI_CANDIDATE"
    )
    assert receipt["suggestion_relation"]["natural_form_path_ids"] == ["path-a"]
    assert receipt["suggestion_relation"]["open_ai_candidate_path_ids"] == ["path-c"]


def test_authorship_identity_requires_both_presentations_to_be_natural_forms():
    events, occurrences, level, coordination = continuum_fixture()
    receipt = derive_continuum_receipt(
        event=events[1],
        field_events=events,
        field_occurrences=occurrences,
        relation_receipts=[],
        closure_level=level,
        coordination=coordination,
    )

    authorship = receipt["authorship"]
    assert any(
        {pair["left_role"], pair["right_role"]} == {"HUMAN", "AI"}
        for pair in authorship["same_global_noncanonical_pairs"]
    )
    assert any(
        {pair["left_role"], pair["right_role"]} == {"AI", "LIVING"}
        for pair in authorship["redundant_natural_form_pairs"]
    )
    assert authorship["converse_without_natural_form_rejected"] is True
    assert authorship["human_ai_living_roles_collapsed"] is False


def test_independent_gates_expose_non_product_commitment_constraints():
    events, occurrences, level, coordination = continuum_fixture()
    receipt = derive_continuum_receipt(
        event=events[1],
        field_events=events,
        field_occurrences=occurrences,
        relation_receipts=[],
        closure_level=level,
        coordination=coordination,
    )

    gates = receipt["gates"]
    assert gates["independent_joint_gate"]["shape"] == "PRODUCT"
    assert gates["independent_joint_gate"]["admitted_pair_count"] == 12
    assert gates["non_product_gate_not_realisable_by_independent_pair"] is True
    assert gates["relational_policy_layer_required"] is True
    assert gates["relational_policy_layer_present"] is True
    assert gates["ordinary_interaction_remains_open"] is True


def test_visual_receipt_is_enriched_without_issuing_truth():
    events, occurrences, level, coordination = continuum_fixture()
    visual = {
        "protocol": "closure.supernet/visual-translational-closure-v1",
        "coordination": coordination,
        "operational_closure": {},
        "truth_issued": False,
    }
    enriched = attach_continuum_to_visual_receipt(
        visual,
        event=events[1],
        field_events=events,
        field_occurrences=occurrences,
        relation_receipts=[],
        closure_level=level,
    )

    continuum = enriched["coordination"]["continuum"]
    assert continuum["protocol"].endswith("nrrf837-continuum-v1")
    assert enriched["nrrf837_continuum"]["continuum_id"] == continuum["continuum_id"]
    assert enriched["operational_closure"]["nrrf837_continuum_derived"] is True
    assert enriched["truth_issued"] is False
'''
