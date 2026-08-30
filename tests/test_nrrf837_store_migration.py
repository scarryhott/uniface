from __future__ import annotations

import sqlite3
from pathlib import Path

from closure_supernet.supernet_store import SupernetIntegrationStore


def test_pre_nrrf837_proposal_table_gains_exact_continuum_fields(
    tmp_path: Path,
) -> None:
    database = tmp_path / "pre-nrrf837.db"
    connection = sqlite3.connect(database)
    connection.execute(
        """
        CREATE TABLE supernet_commitment_proposals (
            id TEXT PRIMARY KEY,
            proposal_event_id TEXT NOT NULL UNIQUE,
            intent_event_id TEXT NOT NULL,
            action_id TEXT,
            target_event_ids TEXT NOT NULL,
            required_participant_ids TEXT NOT NULL,
            resource_conditions TEXT NOT NULL,
            external_key TEXT UNIQUE,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()

    store = SupernetIntegrationStore(database)
    try:
        columns = {
            str(row["name"]): row
            for row in store._conn.execute(  # noqa: SLF001 - migration contract
                "PRAGMA table_info(supernet_commitment_proposals)"
            ).fetchall()
        }
        assert {"title", "proposed_by", "exact_terms", "open_assumptions"} <= set(
            columns
        )
        assert "unity_selector_version" in columns
        assert columns["exact_terms"]["dflt_value"] == "''"
        assert columns["open_assumptions"]["dflt_value"] == "'[]'"
    finally:
        store.close()


def test_nrrf837_exact_terms_and_unity_policy_survive_restart(
    tmp_path: Path,
) -> None:
    database = tmp_path / "nrrf837-persistence.db"
    store = SupernetIntegrationStore(database)
    intent, _ = store.create_event(
        {"authored_by": "harry", "form_label": "intent"}
    )
    target, _ = store.create_event(
        {"authored_by": "maya", "form_label": "project"}
    )
    proposal_event, _ = store.create_event(
        {"authored_by": "harry", "form_label": "agreement"}
    )
    proposal, created = store.create_commitment_proposal(
        {
            "proposal_event_id": proposal_event["id"],
            "intent_event_id": intent["id"],
            "target_event_ids": [target["id"]],
            "required_participant_ids": ["harry", "maya"],
            "resource_conditions": ["budget_usd<=25"],
            "title": "Persistent garden terms",
            "proposed_by": "harry",
            "exact_terms": "Harry and Maya each retain independent consent.",
            "open_assumptions": ["water access remains unresolved"],
            "unity_selector_version": "nrrf837-unity-selector/v1",
        }
    )
    assert created is True
    store.close()

    reopened = SupernetIntegrationStore(database)
    try:
        persisted = reopened.get_commitment_proposal(proposal["id"])
        assert persisted["title"] == "Persistent garden terms"
        assert persisted["proposed_by"] == "harry"
        assert persisted["exact_terms"] == (
            "Harry and Maya each retain independent consent."
        )
        assert persisted["open_assumptions"] == [
            "water access remains unresolved"
        ]
        assert persisted["unity_selector_version"] == (
            "nrrf837-unity-selector/v1"
        )
    finally:
        reopened.close()
