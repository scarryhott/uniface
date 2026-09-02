from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.config import RuntimeConfig
from closure_supernet.project_closure import (
    HISTORICAL_COMPATIBILITY_CHART,
    SEMANTIC_CARRIER,
    TRANSLATION_OPERATOR,
    TRANSPORT_OR_RELATIVE_PROJECTION,
    derive_project_closure_certificate,
    project_paths,
    validate_project_closure_certificate,
)

ROOT = Path(__file__).resolve().parents[1]


def test_complete_project_has_one_deterministic_closure_certificate() -> None:
    first = derive_project_closure_certificate(ROOT)
    second = derive_project_closure_certificate(ROOT)

    assert first == second
    assert first["coverage"] == "FULL_REPOSITORY"
    assert first["project_closed"] is True
    assert first["status"] == "WITNESSED"
    assert validate_project_closure_certificate(first, ROOT)["valid"] is True

    expected_paths = project_paths(ROOT)
    records = first["records"]
    assert [record["path"] for record in records] == expected_paths
    assert len(records) == len(set(expected_paths))
    assert all(record["role"] for record in records)
    assert all(
        record["closure_relation"].endswith(f"--> {SEMANTIC_CARRIER}")
        for record in records
    )
    assert all(not Path(record["path"]).is_absolute() for record in records)


def test_project_identity_changes_only_with_returned_source_bytes() -> None:
    base = derive_project_closure_certificate(ROOT)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changed = derive_project_closure_certificate(
        ROOT,
        overrides={"README.md": readme + "\nDeterministic test return.\n"},
    )

    assert changed["project_closed"] is True
    assert changed["source_tree_identity_id"] != base["source_tree_identity_id"]
    assert changed["id"] != base["id"]
    assert changed["semantic_identity_id"] == base["semantic_identity_id"]
    assert validate_project_closure_certificate(changed)["valid"] is True


def test_every_historical_runtime_is_retained_but_not_a_public_authority() -> None:
    certificate = derive_project_closure_certificate(ROOT)
    record_by_path = {
        record["path"]: record for record in certificate["records"]
    }

    for path in (
        "closure_supernet/api.py",
        "closure_supernet/agent_mcp.py",
        "closure_supernet/full_supernet_projection_runtime_v7.py",
        "closure_supernet/runtime.py",
        "closure_supernet/supernet_runtime.py",
    ):
        assert record_by_path[path]["role"] == HISTORICAL_COMPATIBILITY_CHART

    assert set(certificate["public_entrypoints"]).isdisjoint(
        {
            record["path"]
            for record in certificate["records"]
            if record["role"] == HISTORICAL_COMPATIBILITY_CHART
        }
    )
    assert all(
        record_by_path[path]["role"] == TRANSPORT_OR_RELATIVE_PROJECTION
        for path in certificate["public_entrypoints"]
    )
    assert certificate["authority"] == {
        "semantic_authority": "SUPERNET_CLOSURE_FORM",
        "mutation_authority": "SUPERNET_TRANSLATE",
        "identity_authority": "TRANSLATIONAL_TRUTH_CLASS",
        "historical_modules_are_retained": True,
        "historical_modules_author_truth": False,
        "domain_modules_are_relative_lenses": True,
        "transport_authors_truth": False,
        "rendering_authors_truth": False,
        "self_observation_authors_truth": False,
    }


def test_runtime_agent_browser_and_self_publish_same_project_closure(
    tmp_path: Path,
) -> None:
    from closure_supernet.api_agent import create_app

    app = create_app(
        RuntimeConfig(
            database_path=tmp_path / "project-closure.db",
            inbox_dir=tmp_path / "inbox",
            backup_dir=tmp_path / "backups",
            autonomy_enabled=False,
            environment="test",
            trusted_hosts=("testserver", "localhost", "127.0.0.1"),
        )
    )
    certificate = app.state.supernet_project_closure
    assert certificate["project_closed"] is True

    with TestClient(app) as client:
        interface = client.get("/supernet/interface/capabilities")
        agent = client.get("/supernet/agent/capabilities")
        self_reading = client.get(
            "/supernet/agent/self",
            params={"perspective_id": "project:self"},
        )

    assert interface.status_code == 200
    assert agent.status_code == 200
    assert self_reading.status_code == 200
    readings = (interface.json(), agent.json(), self_reading.json())
    for reading in readings:
        assert reading["project_closure_id"] == certificate["id"]
        assert (
            reading["project_source_tree_identity_id"]
            == certificate["source_tree_identity_id"]
        )
        assert (
            reading["project_semantic_identity_id"]
            == certificate["semantic_identity_id"]
        )
        assert reading["project_closure_status"] == "WITNESSED"
        assert reading["project_closed"] is True
        assert reading["full_project_deterministic"] is True
        assert reading["all_project_files_classified_exactly_once"] is True
        assert (
            reading["all_public_mutations_factor_through_supernet_translate"]
            is True
        )
        assert reading["compatibility_modules_are_non_authoritative"] is True
        assert reading["project_certificate_authors_truth"] is False

    assert interface.json()["translation_operator"] == TRANSLATION_OPERATOR
    assert agent.json()["translation_operator"] == TRANSLATION_OPERATOR
    assert self_reading.json()["translation_operator"] == TRANSLATION_OPERATOR


def test_project_certificate_contains_no_clock_random_or_host_identity() -> None:
    certificate = derive_project_closure_certificate(ROOT)
    determinism = certificate["determinism"]

    assert determinism == {
        "relative_paths_only": True,
        "content_addressed": True,
        "sorted_canonical_json": True,
        "timestamps_in_identity": False,
        "absolute_paths_in_identity": False,
        "process_identity_in_identity": False,
        "randomness_in_identity": False,
        "environment_values_in_identity": False,
        "same_source_tree_same_certificate": True,
    }
    serialized = str(
        {
            "id": certificate["id"],
            "source": certificate["source_tree_identity_id"],
            "semantic": certificate["semantic_identity_id"],
        }
    )
    assert str(ROOT.resolve()) not in serialized
