from closure_supernet.interactive_translation_relation import derive_relative_interactions


def test_interaction_is_primitive_and_closure_equations_are_derived():
    result = derive_relative_interactions(
        observer_id="p",
        projection_reading={"a": "x", "b": "x", "c": "y"},
        form_by_member={"a": "nf1", "b": "nf1", "c": "nf2"},
        visual_nodes=[
            {"id": "ea", "occurrence_id": "a"},
            {"id": "eb", "occurrence_id": "b"},
            {"id": "ec", "occurrence_id": "c"},
        ],
        visual_edges=[
            {"id": "ab", "source": "ea", "target": "eb"},
            {"id": "ac", "source": "ea", "target": "ec"},
        ],
        truth_members={"a", "b", "c"},
    )
    assert result["observer_observed_relation_is_primitive"] is True
    assert result["observation_equality_is_primitive"] is False
    assert result["return_is_primitive"] is False
    assert result["closure_equations_derived"] is True
    ab = next(row for row in result["interactions"] if row["id"] == "ab")
    assert ab["translation_relation_witnessed"] is True
    assert ab["closure_preserved_after_translation"] is True
    assert "ac" in result["open_visual_edge_ids"]
    assert result["raw_visual_adjacency_authors_truth"] is False


def test_return_is_witness_not_fixed_semantics():
    result = derive_relative_interactions(
        observer_id="p",
        projection_reading={"a": "x", "b": "x"},
        form_by_member={"a": "nf", "b": "nf"},
        visual_nodes=[
            {"id": "ea", "occurrence_id": "a"},
            {"id": "eb", "occurrence_id": "b"},
        ],
        visual_edges=[{"id": "ab", "source": "ea", "target": "eb"}],
        truth_members={"a", "b"},
    )
    relation = result["interactions"][0]
    assert relation["return_witness_id"]
    assert relation["return_is_semantic_primitive"] is False
    assert relation["return_is_interaction_witness"] is True
    assert relation["fixed_return_required"] is False
    assert relation["continuation_status"] == "OPEN"


def test_missing_observer_leaves_translation_open():
    result = derive_relative_interactions(
        observer_id=None,
        projection_reading={"a": "x", "b": "x"},
        form_by_member={"a": "nf", "b": "nf"},
        visual_nodes=[
            {"id": "ea", "occurrence_id": "a"},
            {"id": "eb", "occurrence_id": "b"},
        ],
        visual_edges=[{"id": "ab", "source": "ea", "target": "eb"}],
        truth_members={"a", "b"},
    )
    assert result["translation_reading_total"] is False
    assert result["closure_equations_derived"] is False
    assert result["interactions"][0]["interaction_status"] == "OPEN"


def test_display_relabeling_preserves_derived_closure_partition():
    common = dict(
        observer_id="p",
        form_by_member={"a": "nf1", "b": "nf1", "c": "nf2"},
        visual_nodes=[
            {"id": "ea", "occurrence_id": "a"},
            {"id": "eb", "occurrence_id": "b"},
            {"id": "ec", "occurrence_id": "c"},
        ],
        visual_edges=[{"id": "ab", "source": "ea", "target": "eb"}],
        truth_members={"a", "b", "c"},
    )
    first = derive_relative_interactions(
        projection_reading={"a": "display-1", "b": "display-1", "c": "display-2"},
        **common,
    )
    second = derive_relative_interactions(
        projection_reading={"a": "other", "b": "other", "c": "else"},
        **common,
    )
    assert first["translation_partition"] == second["translation_partition"]
    assert first["closure_equations_derived"] is True
    assert second["closure_equations_derived"] is True
