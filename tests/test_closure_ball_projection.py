from __future__ import annotations

from copy import deepcopy

from closure_supernet.closure_ball_projection import (
    PROTOCOL,
    derive_closure_ball_projection,
    validate_closure_ball_projection,
)


def sample_contract(*, status: str = "WITNESSED") -> dict:
    states = [
        {
            "id": "state:a",
            "event_id": "event:a",
            "natural_form_id": "form:ab",
            "display_fibre_id": "display:alice:a",
            "source_return_ids": ["return:a"],
            "source_trace": "A proposal",
        },
        {
            "id": "state:b",
            "event_id": "event:b",
            "natural_form_id": "form:ab",
            "display_fibre_id": "display:alice:b",
            "source_return_ids": ["return:b"],
            "source_trace": "A translated return",
        },
        {
            "id": "state:c",
            "event_id": "event:c",
            "natural_form_id": "form:c",
            "display_fibre_id": "display:alice:c",
            "source_return_ids": ["return:c"],
            "source_trace": "An unresolved consequence",
        },
    ]
    return {
        "id": "contract:1",
        "status": status,
        "perspective_id": "alice",
        "focus_event_id": "event:b",
        "closure_derivation_id": "truth:1",
        "visual_closure_id": "visual:1",
        "interactive_translation_id": "translation:1",
        "field_event_seq": 3,
        "source_return_ids": ["return:a", "return:b", "return:c"],
        "closure_naturality_equations": {
            "id": "equations:1",
            "checks": {"distinctions_only_grow_with_arena": True},
        },
        "perspective_closure": {
            "active_perspective_id": "alice",
            "readings": {
                "alice": {
                    "state:a": "display:alice:a",
                    "state:b": "display:alice:b",
                    "state:c": "display:alice:c",
                },
                "bob": {
                    "state:a": "display:bob:a",
                    "state:b": "display:bob:b",
                    "state:c": "display:bob:c",
                },
            },
            "kernel": [["state:a", "state:b"], ["state:c"]],
            "kernels": {
                "alice": [["state:a", "state:b"], ["state:c"]],
                "bob": [["state:a", "state:b"], ["state:c"]],
            },
            "translations": [
                {
                    "id": "perspective:alice-bob",
                    "source_perspective_id": "alice",
                    "target_perspective_id": "bob",
                    "witnessed": True,
                    "source_return_ids": ["return:a", "return:b", "return:c"],
                }
            ],
        },
        "projection": {
            "active_perspective_id": "alice",
            "states": states,
            "equality_fibres": [
                {
                    "id": "form:ab",
                    "member_state_ids": ["state:a", "state:b"],
                    "display_fibre_ids": ["display:alice:a", "display:alice:b"],
                    "source_return_ids": ["return:a", "return:b"],
                    "derivation": {"source_return_ids": ["return:a", "return:b"]},
                },
                {
                    "id": "form:c",
                    "member_state_ids": ["state:c"],
                    "display_fibre_ids": ["display:alice:c"],
                    "source_return_ids": ["return:c"],
                    "derivation": {"source_return_ids": ["return:c"]},
                },
            ],
            "translations": [
                {
                    "id": "relation:ab",
                    "source_state_id": "state:a",
                    "target_state_id": "state:b",
                    "relation_status": "WITNESSED",
                    "executes_as_equality": True,
                    "same_display_fibre": True,
                    "derivation": {"source_return_ids": ["return:a", "return:b"]},
                },
                {
                    "id": "relation:bc",
                    "source_state_id": "state:b",
                    "target_state_id": "state:c",
                    "relation_status": "OPEN",
                    "executes_as_equality": False,
                    "same_display_fibre": False,
                    "derivation": {"source_return_ids": ["return:b", "return:c"]},
                },
            ],
            "potentials": [
                {
                    "id": "potential:c",
                    "target_state_id": "state:c",
                    "shared_natural_form_id": "form:c",
                    "derivation": {"source_return_ids": ["return:c"]},
                }
            ],
        },
        "return_relation": {
            "id": "return-relation:1",
            "kind": "SOURCE_PRESERVING_TRANSLATIONAL_RETURN",
            "focus_state_id": "state:b",
            "parent_natural_form_id": "form:ab",
            "derivation": {"source_return_ids": ["return:a", "return:b"]},
        },
    }


def empty_contract() -> dict:
    return {
        "id": "contract:empty",
        "status": "OPEN_SOURCE_BOUNDARY",
        "perspective_id": "alice",
        "focus_event_id": None,
        "source_return_ids": [],
        "projection": {
            "states": [],
            "equality_fibres": [],
            "translations": [],
            "potentials": [],
        },
        "perspective_closure": {
            "readings": {"alice": {}},
            "kernel": [],
            "kernels": {"alice": []},
            "translations": [],
        },
        "closure_naturality_equations": {"id": "equations:empty"},
        "return_relation": {
            "id": "return-relation:empty",
            "kind": "SOURCE_PRESERVING_TRANSLATIONAL_RETURN",
            "focus_state_id": None,
            "derivation": {"source_return_ids": []},
        },
    }


def test_one_ball_derives_ui_hair_maze_ai_token_and_closure() -> None:
    ball = derive_closure_ball_projection(sample_contract())

    assert ball["protocol"] == PROTOCOL
    assert ball["natural_ui"]["closure_ball_id"] == ball["id"]
    assert ball["maze_partition"]["id"] == ball["natural_ui"]["maze_partition_id"]
    assert ball["hair"]["action_ids"] == ball["natural_ui"]["hair_action_ids"]
    assert ball["checks"]["equality_closure_preserved"] is True
    assert ball["equality"]["all_readings_factor_through_event_projection"] is True

    for event in ball["interaction_events"]:
        readings = event["readings"]
        assert readings["ui"] == readings["ai"] == readings["token"] == readings["closure"]
        assert readings["ui"]["underlying_path_id"] == event["underlying_path_id"]
        assert readings["ui"]["closure_ball_id"] == ball["id"]


def test_every_exposed_action_is_hair_and_has_one_equal_event() -> None:
    ball = derive_closure_ball_projection(sample_contract())
    action_ids = set(ball["hair"]["action_ids"])
    event_action_ids = {event["hair_action_id"] for event in ball["interaction_events"]}

    assert action_ids == event_action_ids
    assert ball["hair"]["arbitrary_application_commands"] == []
    assert {
        action["kind"] for action in ball["hair"]["actions"]
    } >= {
        "ENTER_CLOSURE_LOCALITY",
        "REBASE_PERSPECTIVE",
        "FOLLOW_WITNESSED_TRANSLATION",
        "FOLLOW_OPEN_SEAM",
        "EXTEND_SOURCE_PRESERVING_RETURN",
        "REPARAMETERIZE_PERSPECTIVE_HAIR",
    }


def test_open_seams_are_navigable_but_never_execute_as_equality() -> None:
    ball = derive_closure_ball_projection(sample_contract())
    open_events = [
        event
        for event in ball["interaction_events"]
        if event["event_projection"]["open_seam"] is True
    ]

    assert open_events
    assert all(
        event["event_projection"]["executes_as_equality"] is False
        for event in open_events
    )
    assert any(
        action["kind"] == "FOLLOW_OPEN_SEAM"
        for action in ball["hair"]["actions"]
    )


def test_witnessed_paths_have_zero_closure_defect_without_invented_value() -> None:
    ball = derive_closure_ball_projection(sample_contract())
    witnessed = [
        event["event_projection"]
        for event in ball["interaction_events"]
        if event["event_projection"]["executes_as_equality"] is True
    ]

    assert witnessed
    assert all(event["closure_defect"] == 0 for event in witnessed)
    assert all(event["numeric_curvature"] is None for event in witnessed)
    assert all(event["numeric_value_not_invented"] is True for event in witnessed)


def test_perspective_rebase_preserves_global_ball_but_changes_projection() -> None:
    alice_contract = sample_contract()
    bob_contract = deepcopy(alice_contract)
    bob_contract["id"] = "contract:2"
    bob_contract["perspective_id"] = "bob"
    bob_contract["perspective_closure"]["active_perspective_id"] = "bob"
    for row in bob_contract["projection"]["states"]:
        row["display_fibre_id"] = row["display_fibre_id"].replace("alice", "bob")
    for row in bob_contract["projection"]["equality_fibres"]:
        row["display_fibre_ids"] = [
            value.replace("alice", "bob") for value in row["display_fibre_ids"]
        ]

    alice = derive_closure_ball_projection(alice_contract)
    bob = derive_closure_ball_projection(bob_contract)

    assert alice["id"] == bob["id"]
    assert alice["projection_id"] != bob["projection_id"]
    assert alice["maze_partition"]["kernel"] == bob["maze_partition"]["kernel"]


def test_display_geometry_cannot_change_ball_equality() -> None:
    first_contract = sample_contract()
    second_contract = deepcopy(first_contract)
    second_contract["projection"]["visualization"] = {
        "relation_digest": "authored-scene",
        "fibre_primitives": [{"centre": [1, 2], "radius": 999}],
    }
    first = derive_closure_ball_projection(first_contract)
    second = derive_closure_ball_projection(second_contract)

    assert first["id"] == second["id"]
    assert first["maze_partition"]["kernel"] == second["maze_partition"]["kernel"]
    assert first["natural_ui"]["geometry"] == second["natural_ui"]["geometry"]


def test_empty_open_ball_exposes_only_return_and_hair_reparameterization() -> None:
    ball = derive_closure_ball_projection(empty_contract())
    kinds = {action["kind"] for action in ball["hair"]["actions"]}

    assert ball["carrier_state_ids"] == []
    assert ball["maze_partition"]["kernel"] == []
    assert kinds == {
        "EXTEND_SOURCE_PRESERVING_RETURN",
        "REPARAMETERIZE_PERSPECTIVE_HAIR",
    }
    assert ball["checks"]["equality_closure_preserved"] is True


def test_validator_rejects_forged_ai_or_token_reading() -> None:
    contract = sample_contract()
    ball = derive_closure_ball_projection(contract)
    forged = deepcopy(ball)
    forged["interaction_events"][0]["readings"]["ai"]["underlying_path_id"] = "forged"

    validation = validate_closure_ball_projection(contract, forged)
    assert validation["valid"] is False
    assert "closure-ball:not-exact-derivation" in validation["errors"]


def test_validator_accepts_exact_derivation() -> None:
    contract = sample_contract()
    ball = derive_closure_ball_projection(contract)
    assert validate_closure_ball_projection(contract, ball)["valid"] is True
