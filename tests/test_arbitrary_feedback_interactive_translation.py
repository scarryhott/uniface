from closure_supernet.interactive_translation_relation import derive_feedback_translation


def test_feedback_payload_cannot_author_equality():
    receipt = derive_feedback_translation(
        observer_id="observer",
        returned_feedback=[
            {"observed_id": "a", "source_ids": ["sa"], "payload": {"price": 1}},
            {"observed_id": "b", "source_ids": ["sb"], "payload": {"price": 1}},
        ],
        returned_interactions=[],
    )
    assert receipt["translation_partition"] == [["a"], ["b"]]
    assert receipt["observation_equality_is_primitive"] is False


def test_returned_interaction_derives_fibre_without_feature_or_horizon():
    receipt = derive_feedback_translation(
        observer_id="observer",
        returned_feedback=[
            {"observed_id": "a", "source_ids": ["sa"], "payload": {"anything": [1, 2, 3]}},
            {"observed_id": "b", "source_ids": ["sb"], "payload": {"different": True}},
        ],
        returned_interactions=[
            {"id": "r", "source": "a", "target": "b", "source_ids": ["r-source"], "returned": True}
        ],
    )
    assert receipt["translation_partition"] == [["a", "b"]]
    assert receipt["interactions"][0]["translation_relation_witnessed"] is True
    assert receipt["feature_selection_is_semantic"] is False
    assert receipt["horizon_selection_is_semantic"] is False
    assert receipt["strategy_selection_is_semantic"] is False


def test_unreturned_relation_stays_open():
    receipt = derive_feedback_translation(
        observer_id="observer",
        returned_feedback=[
            {"observed_id": "a", "source_ids": ["sa"], "payload": 1},
            {"observed_id": "b", "source_ids": ["sb"], "payload": 2},
        ],
        returned_interactions=[{"id": "proposal", "source": "a", "target": "b"}],
    )
    assert receipt["translation_partition"] == [["a"], ["b"]]
    assert receipt["interactions"][0]["interaction_status"] == "OPEN"


def test_missing_observer_never_witnesses_translation():
    receipt = derive_feedback_translation(
        observer_id=None,
        returned_feedback=[
            {"observed_id": "a", "source_ids": ["sa"], "payload": 1},
            {"observed_id": "b", "source_ids": ["sb"], "payload": 2},
        ],
        returned_interactions=[
            {"source": "a", "target": "b", "source_ids": ["r"], "returned": True}
        ],
    )
    assert receipt["translation_partition"] == [["a"], ["b"]]
    assert receipt["translation_reading_total"] is False


def test_arbitrary_feedback_shape_is_transport_only():
    receipt = derive_feedback_translation(
        observer_id="o",
        returned_feedback=[
            {"observed_id": "weather", "source_ids": ["sensor"], "payload": {"temp": 21.4}},
            {"observed_id": "market", "source_ids": ["feed"], "payload": {"bid": 10, "ask": 11}},
        ],
        returned_interactions=[
            {"source": "weather", "target": "market", "source_ids": ["human-return"], "returned": True}
        ],
    )
    assert receipt["translation_partition"] == [["market", "weather"]]
    assert receipt["fixed_return_required"] is False
