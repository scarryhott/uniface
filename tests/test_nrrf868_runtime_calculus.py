from closure_supernet.interactive_derivation_calculus import (
    OPEN_STATUS,
    REFUTED_STATUS,
    WITNESSED_STATUS,
    classify_returned_relation,
    normalize_translation_history,
)
from closure_supernet.interactive_translation_relation import derive_feedback_translation


def test_positive_truth_is_one_translation_certificate():
    receipt = derive_feedback_translation(
        observer_id="o",
        returned_feedback=[
            {"observed_id": "a", "source_ids": ["sa"], "payload": 1},
            {"observed_id": "b", "source_ids": ["sb"], "payload": 2},
        ],
        returned_interactions=[
            {"id": "r", "source": "a", "target": "b", "source_ids": ["rr"], "returned": True}
        ],
    )
    row = receipt["interactions"][0]
    assert row["interaction_status"] == WITNESSED_STATUS
    assert row["translation_witness"]["kind"] == "TRANSLATION_WITNESS"
    assert row["translation_witness"]["one_step_normal_form"] is True
    assert row["derivation_history_is_semantic"] is False
    assert receipt["derivation_normal_form"] == "ONE_TRANSLATION"


def test_negative_truth_requires_explicit_returned_loop():
    receipt = derive_feedback_translation(
        observer_id="o",
        returned_feedback=[
            {"observed_id": "a", "source_ids": ["sa"], "payload": 1},
            {"observed_id": "b", "source_ids": ["sb"], "payload": 2},
        ],
        returned_interactions=[{
            "id": "r",
            "source": "a",
            "target": "b",
            "source_ids": ["rr"],
            "returned": True,
            "loop_refutation": {"closed": True, "left_cost": 1.0, "right_cost": 2.0},
        }],
    )
    row = receipt["interactions"][0]
    assert row["interaction_status"] == REFUTED_STATUS
    assert row["translation_relation_witnessed"] is False
    assert row["loop_refutation"]["kind"] == "LOOP_REFUTATION"
    assert receipt["translation_partition"] == [["a"], ["b"]]
    assert receipt["refuted_pairs"] == [["a", "b"]]


def test_absence_of_either_certificate_is_open_not_false():
    result = classify_returned_relation(
        observer_id="o",
        source_id="a",
        target_id="b",
        relation_id="proposal",
        source_return_ids=[],
        endpoints_source_preserved=True,
        returned=False,
    )
    assert result["status"] == OPEN_STATUS
    assert result["derivable"] is None
    assert result["closure_equal"] is None


def test_derivation_history_normalizes_to_one_step():
    first = classify_returned_relation(
        observer_id="o", source_id="a", target_id="b", relation_id="ab",
        source_return_ids=["r1"], endpoints_source_preserved=True, returned=True,
    )["translation_witness"]
    second = classify_returned_relation(
        observer_id="o", source_id="b", target_id="c", relation_id="bc",
        source_return_ids=["r2"], endpoints_source_preserved=True, returned=True,
    )["translation_witness"]
    normalized = normalize_translation_history([first, second])
    assert normalized["source_id"] == "a"
    assert normalized["target_id"] == "c"
    assert normalized["one_step_normal_form"] is True
    assert normalized["normalized_from_steps"] == 2
    assert normalized["derivation_depth_semantic"] is False
