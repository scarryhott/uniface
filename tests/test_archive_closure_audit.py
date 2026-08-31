from closure_supernet.archive_closure_audit import (
    EXECUTABLE,
    MISSING,
    OPEN,
    REGISTERED,
    WITNESSED,
    audit_archive,
    classify_condition,
    parse_archive,
    validate_archive_audit,
)
from closure_supernet.natural_form_atlas import derive_versioned_natural_form_atlas


def archive(*messages: str, declared_messages: int | None = None) -> str:
    count = len(messages) if declared_messages is None else declared_messages
    rendered = [
        "# User inputs only",
        "",
        "Extracted from 1 conversation files.",
        "",
        "- Conversations with user messages: 1",
        f"- User messages: {count}",
        "- Empty/non-text user messages skipped: 0",
        "",
        "---",
        "",
        "## Theory",
        "",
        "_Conversation ID: `conversation-1`_",
        "",
    ]
    for index, message in enumerate(messages, 1):
        rendered.extend(
            [
                f"### Message {index} — 2026-08-31 00:0{index}:00 UTC",
                "",
                message,
                "",
            ]
        )
    return "\n".join(rendered)


def witnessed_atlas():
    return derive_versioned_natural_form_atlas(
        truth_derivation={},
        interactive_translation={},
        active_perspective_id=None,
        active_reading={},
        additional_translation_sources=(
            {
                "atlas_translations": [
                    {
                        "source_chart_id": "nf:triangle-time:v1",
                        "target_chart_id": "nf:checker-grid:v1",
                        "source_return_ids": ["return:triangle-checker"],
                        "returned": True,
                        "source_preserved": True,
                        "closure_commutes": True,
                        "return_preserved": True,
                        "return_witness_id": "witness:triangle-checker",
                    }
                ]
            },
        ),
    )


def test_parser_counts_only_exported_conversation_headers():
    source = archive(
        "Closure remains relational.\n\n## This heading is inside the message, not a new conversation.",
        "The fractal hypotenuse remains a natural form.",
    )
    parsed = parse_archive(source)
    assert parsed["declared_user_message_count"] == 2
    assert parsed["declared_conversation_count"] == 1
    assert parsed["parsed_conversation_count"] == 1
    assert len(parsed["messages"]) == 2
    assert "inside the message" in parsed["messages"][0]["text"]


def test_registered_executable_open_and_missing_are_not_collapsed():
    receipt = audit_archive(
        archive(
            "The fractal hypotenuse remains a natural form.",
            "Observer-observed interactive translation derives the current closure relation.",
            "Triangle time translates to checker grid.",
            "Closure phoenix tensor equals aurora tensor.",
        ),
        archive_name="fixture.md",
    )
    statuses = [condition["status"] for condition in receipt["conditions"]]
    assert REGISTERED in statuses
    assert EXECUTABLE in statuses
    assert OPEN in statuses
    assert MISSING in statuses
    assert receipt["historical_inventory_closed"] is False
    assert receipt["runtime_execution_closed"] is False
    assert validate_archive_audit(receipt)["valid"] is True


def test_cross_form_relation_requires_returned_atlas_translation():
    statement = "Triangle time translates to checker grid."
    assert classify_condition(text=statement)["status"] == OPEN
    classified = classify_condition(text=statement, atlas=witnessed_atlas())
    assert classified["status"] == WITNESSED
    assert classified["basis"] == "SOURCE_PRESERVING_RETURNED_ATLAS_TRANSLATION"


def test_registered_chart_is_not_silently_called_executable():
    classified = classify_condition(
        text="The fractal hypotenuse remains a natural form of closure."
    )
    assert classified["status"] == REGISTERED
    assert "nf:fractal-hypotenuse:v1" in classified["chart_ids"]


def test_runtime_capability_can_close_a_complete_fixture():
    receipt = audit_archive(
        archive("Observer-observed interactive translation derives the relation."),
        archive_name="executable.md",
    )
    assert receipt["source_count_matches_declared_archive"] is True
    assert receipt["classification_counts"][EXECUTABLE] >= 1
    assert receipt["classification_counts"][MISSING] == 0
    assert receipt["classification_counts"][OPEN] == 0
    assert receipt["classification_counts"][REGISTERED] == 0
    assert receipt["historical_inventory_closed"] is True
    assert receipt["runtime_execution_closed"] is True


def test_source_count_mismatch_prevents_inventory_closure():
    receipt = audit_archive(
        archive(
            "Observer-observed interactive translation derives the relation.",
            declared_messages=2,
        )
    )
    assert receipt["source_count_matches_declared_archive"] is False
    assert receipt["historical_inventory_closed"] is False
    assert receipt["runtime_execution_closed"] is False
