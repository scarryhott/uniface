from __future__ import annotations

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
