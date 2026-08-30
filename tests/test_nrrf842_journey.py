from __future__ import annotations

from copy import deepcopy

from closure_supernet.nrrf842_journey import derive_nrrf842_journey_receipt


def event(
    event_id: str,
    *,
    parent_ids: list[str] | None = None,
    perspective_id: str | None = "harry",
    role: str = "HUMAN",
    seq: int = 1,
) -> dict:
    return {
        "id": event_id,
        "seq": seq,
        "parent_event_ids": parent_ids or [],
        "current_stage": "SOURCE_PRESERVED",
        "current_verdict": "OPEN",
        "authored_by": perspective_id or "source",
        "perspective_id": perspective_id,
        "form_label": "thought",
        "exact_source_ids": [f"occurrence-{event_id}"],
        "created_at": f"2026-08-30T00:00:0{seq}Z",
        "metadata": {"authorship_role": role},
    }


def coordination(
    phase: str = "DISCOVER",
    *,
    required: list[str] | None = None,
    accepted: list[str] | None = None,
) -> dict:
    required = required or []
    accepted = accepted or []
    proposal = (
        {
            "id": "proposal-1",
            "required_participant_ids": required,
            "decision_history": [
                {
                    "participant_id": participant,
                    "decision": "ACCEPT",
                    "authorship_role": "HUMAN",
                }
                for participant in accepted
            ],
        }
        if required
        else None
    )
    return {
        "paths": [
            {
                "id": "path-garden",
                "target_event_id": "project-garden",
                "kind": "PROJECT",
                "label": "River Street garden",
                "why": {
                    "shared_natural_form_id": "natural-form:garden",
                    "formal_suggestion_status": "WITNESSED",
                },
            },
            {
                "id": "path-open",
                "target_event_id": "resource-tools",
                "kind": "RESOURCE",
                "label": "Tool library",
                "why": {"formal_suggestion_status": "OPEN"},
            },
        ],
        "active_proposal": proposal,
        "natural_form_operator": {"natural_form": phase},
        "continuum": {
            "selected_natural_form_id": "natural-form:garden",
            "modality": {"operator": phase},
            "one_tap": {
                "settlement": {
                    "required_participant_ids": required,
                    "human_acceptances": [
                        {
                            "participant_id": participant,
                            "authorship_role": "HUMAN",
                        }
                        for participant in accepted
                    ],
                }
            },
        },
    }


def derive(
    focus: dict,
    events: list[dict],
    *,
    current_coordination: dict | None = None,
) -> dict:
    return derive_nrrf842_journey_receipt(
        focus_event=focus,
        field_events=events,
        perspective_visual_mirror={"id": "mirror-1"},
        visual_truth_closure={"id": "vis-closure-1"},
        natural_forms=[
            {"natural_form": "natural-form:garden", "members": ["a", "b"]}
        ],
        coordination=current_coordination or coordination(),
    )


def test_closed_state_does_not_erase_or_identify_two_journeys() -> None:
    root_a = event("root-a", seq=1)
    focus_a = event("focus-a", parent_ids=["root-a"], seq=2)
    root_b = event("root-b", seq=1)
    focus_b = event("focus-b", parent_ids=["root-b"], seq=2)

    first = derive(focus_a, [root_a, focus_a, root_b, focus_b])
    second = derive(focus_b, [root_a, focus_a, root_b, focus_b])

    assert first["closed_state"]["id"] == second["closed_state"]["id"]
    assert first["journey"]["id"] != second["journey"]["id"]
    assert [item["event_id"] for item in first["journey"]["steps"]] == [
        "root-a",
        "focus-a",
    ]
    separation = first["state_journey_separation"]
    assert separation["closure_is_journey"] is False
    assert separation["same_closed_state_identifies_histories"] is False
    assert separation["closure_state_local"] is True
    assert separation["closed_state_can_continue"] is True


def test_necessary_conditions_are_recorded_without_becoming_sufficient() -> None:
    focus = event("focus")
    receipt = derive(focus, [focus])

    necessary = receipt["necessary_conditions"]
    assert necessary["known_conditions_present"] is True
    assert necessary["necessary_not_sufficient"] is True
    assert necessary["conditions_are_sufficient"] is False
    assert necessary["complete_living_system_claimed"] is False


def test_perspective_is_a_living_choice_and_never_ai_choice_for_a_person() -> None:
    human = event("human", perspective_id="garden-view")
    human_receipt = derive(human, [human])
    choice = human_receipt["chosen_perspective"]
    assert choice["chosen"] is True
    assert choice["choice_source"] == "EVENT_PERSPECTIVE"
    assert choice["no_fixed_perspective_is_universal"] is True
    assert choice["not_choosing_is_a_cap_not_a_contradiction"] is True

    ai = event("ai", perspective_id="suggested-view", role="AI")
    ai_choice = derive(ai, [ai])["chosen_perspective"]
    assert ai_choice["chosen"] is False
    assert ai_choice["status"] == "OPEN"
    assert ai_choice["ai_may_suggest_not_choose_for_a_living_author"] is True


def test_unity_gates_only_shared_ascent_and_never_people_or_interaction() -> None:
    focus = event("focus")
    partial = derive(
        focus,
        [focus],
        current_coordination=coordination(
            "COMMIT", required=["harry", "maya"], accepted=["harry"]
        ),
    )["unity_gate"]
    assert partial["transition_status"] == "OPEN"
    assert partial["scope"] == "SHARED_TRAJECTORY_NOT_PERSON"
    assert partial["community"][
        "one_unresolved_member_keeps_shared_ascent_open"
    ] is True
    assert partial["ordinary_interaction_open"] is True
    assert partial["interactions_gated"] is False
    assert partial["person_ranked"] is False
    assert partial["human_worth_scored"] is False

    complete_coordination = coordination(
        "COMMIT", required=["harry", "maya"], accepted=["harry", "maya"]
    )
    complete = derive(
        focus, [focus], current_coordination=complete_coordination
    )["unity_gate"]
    assert complete["transition_status"] == "SATISFIED"
    assert complete["unity_reached"] is True
    assert complete["unity_not_sufficient_for_ascent"] is True
    assert complete["transition_authorized_by_this_gate"] is False


def test_truth_curved_light_cone_is_semantic_and_preserves_open_paths() -> None:
    focus = event("focus")
    cone = derive(focus, [focus])["truth_curved_light_cone"]

    assert cone["kind"] == "SEMANTIC_TRUTH_CURVATURE_NOT_PHYSICAL_SPACETIME"
    assert cone["physical_light_cone_claimed"] is False
    assert cone["origin"]["visual_mirror_id"] == "mirror-1"
    assert cone["path_count"] == 2
    assert cone["witnessed_truth_constraint_count"] == 1
    assert cone["open_path_count"] == 1
    assert all(path["local_freedom_preserved"] for path in cone["paths"])
    assert cone["natural_language"]["thought_derivation"] == (
        "THOUGHT_IS_CLOSURE_OF_METAPHOR_INTO_RELATIONS"
    )


def test_receipt_is_deterministic() -> None:
    focus = event("focus")
    first = derive(focus, [focus])
    second = derive(deepcopy(focus), [deepcopy(focus)])
    assert first == second
