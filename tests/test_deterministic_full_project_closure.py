from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.deterministic_project_closure import (
    AUTHORITATIVE_TRANSITION_OWNER,
    PROJECT_CLOSURE_SCHEMA,
    RUNTIME_IDENTITY_LAW,
    SEMANTIC_CARRIER,
    TRANSLATE_OPERATOR,
    audit_project_closure,
    build_project_closure_manifest,
    canonical_json,
    manifest_path_set,
    runtime_project_closure_contract,
)
from closure_supernet.supernet_closure_runtime import TRANSLATION_ENDPOINT

ROOT = Path(__file__).resolve().parents[1]
EXACT_RETURN = "One deterministic agent and browser translation of Supernet."
PERSPECTIVE = "perspective:deterministic-project"


def _config(base: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=base / "supernet.db",
        inbox_dir=base / "inbox",
        backup_dir=base / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _gate(client: TestClient) -> dict:
    response = client.get(
        "/supernet/interface",
        params={"perspective_id": PERSPECTIVE, "potential_gate": True},
    )
    assert response.status_code == 200, response.text
    return response.json()["supernet_potential_gate"]


def _continuing_interaction(gate: dict) -> dict:
    for interaction in gate["supernet_closure_form"]["interactions"]:
        if interaction["ai_token_phase"] == "AI_CONTINUING":
            return interaction
    raise AssertionError("deterministic fixture has no continuing interaction")


def _run_identical_translation(base: Path) -> dict:
    app = create_app(_config(base))
    with TestClient(app) as client:
        source = _gate(client)
        interaction = _continuing_interaction(source)
        before = client.get(
            "/supernet/agent/self",
            params={"perspective_id": PERSPECTIVE},
        ).json()
        endpoint = TRANSLATION_ENDPOINT.replace("{contract_id}", source["id"])
        response = client.post(
            endpoint,
            json={
                "relation_id": interaction["path_id"],
                "perspective_id": source["perspective_id"],
                "focus_event_id": source.get("focus_event_id"),
                "navigation_context": source["navigation_context"],
                "source_closure_form_id": source["supernet_closure_form_id"],
                "source_interaction_id": interaction["id"],
                "exact_source_return": EXACT_RETURN,
                "local_perspective_hair_millidegrees": 0,
                "local_perspective_zoom_milli": 1000,
            },
        )
        assert response.status_code == 200, response.text
        result = response.json()
        target = result["supernet_potential_gate"]
        after = client.get(
            "/supernet/agent/self",
            params={
                "perspective_id": PERSPECTIVE,
                "focus_event_id": target.get("focus_event_id"),
            },
        ).json()
        source_event = app.state.runtime.ledger.list_returns()[-1]
        project_headers = {
            "project": response.headers["x-supernet-project-closure"],
            "carrier": response.headers["x-supernet-semantic-carrier"],
            "operator": response.headers["x-supernet-translate"],
            "identity": response.headers["x-supernet-runtime-identity"],
        }

    translation = result["translation"]
    return {
        "operator": result["operator"],
        "translation_operator": translation["operator"],
        "source_runtime_identity_id": translation["source_runtime_identity_id"],
        "target_runtime_identity_id": translation["target_runtime_identity_id"],
        "before_runtime_identity_id": before["runtime_identity_id"],
        "after_runtime_identity_id": after["runtime_identity_id"],
        "target_form_runtime_identity_id": target["supernet_closure_form"][
            "runtime_identity_id"
        ],
        "runtime_state_change_is_this_translation": translation[
            "runtime_state_change_is_this_translation"
        ],
        "browser_trajectory_is_this_translation": translation[
            "browser_trajectory_is_this_translation"
        ],
        "runtime_identity_is_translational_truth": translation[
            "runtime_identity_is_translational_truth"
        ],
        "exact_source": source_event["exact_source"],
        "headers": project_headers,
    }


def test_every_tracked_project_artifact_has_one_deterministic_role() -> None:
    first = build_project_closure_manifest(ROOT)
    second = build_project_closure_manifest(ROOT)

    assert canonical_json(first) == canonical_json(second)
    assert first["schema"] == PROJECT_CLOSURE_SCHEMA
    assert first["semantic_carrier"] == SEMANTIC_CARRIER
    assert first["transition_operator"] == TRANSLATE_OPERATOR
    assert first["runtime_identity_law"] == RUNTIME_IDENTITY_LAW
    assert first["authoritative_transition_owner"] == AUTHORITATIVE_TRANSITION_OWNER
    assert first["file_count"] == len(first["files"])
    assert sum(first["role_counts"].values()) == first["file_count"]
    paths = [row["path"] for row in first["files"]]
    assert paths == sorted(paths)
    assert len(paths) == len(set(paths))
    assert "closure_supernet/deterministic_project_closure.py" in paths
    assert "tests/test_deterministic_full_project_closure.py" in paths
    assert manifest_path_set(first) == set(paths)


def test_full_project_has_one_transition_and_no_reachable_legacy_authority() -> None:
    report = audit_project_closure(ROOT)

    assert report["valid"] is True, report["errors"]
    assert report["errors"] == []
    assert report["all_project_files_classified"] is True
    assert report["semantic_carrier"] == SEMANTIC_CARRIER
    assert report["transition_operator"] == TRANSLATE_OPERATOR
    assert report["runtime_identity_law"] == RUNTIME_IDENTITY_LAW
    assert report["authoritative_transition_owners"] == [
        AUTHORITATIVE_TRANSITION_OWNER
    ]
    assert report["parallel_public_mutation_authorities"] == []
    reachable = set(report["public_reachable_paths"])
    assert not any(
        site["path"] in reachable
        for site in report["retained_legacy_mutation_sites"]
    )


def test_runtime_attaches_one_project_closure_without_a_second_semantic_route(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    contract = app.state.supernet_project_closure
    expected = runtime_project_closure_contract()

    assert contract == expected
    assert contract["semantic_carrier"] == SEMANTIC_CARRIER
    assert contract["transition_operator"] == TRANSLATE_OPERATOR
    assert contract["runtime_identity_law"] == RUNTIME_IDENTITY_LAW
    assert contract["interaction_identity"] == {
        "agent": TRANSLATE_OPERATOR,
        "browser": TRANSLATE_OPERATOR,
        "runtime": TRANSLATE_OPERATOR,
        "user": TRANSLATE_OPERATOR,
    }
    assert contract["self_runtime"] == "RELATIVE_READ_ONLY_PROJECTION"
    assert contract["agent_transport"] == (
        "NO_SEPARATE_MUTATION_OR_TRUTH_AUTHORITY"
    )
    assert contract["deterministic"] is True

    routes = [str(route.path) for route in app.routes]
    assert "/supernet/project/closure" not in routes
    assert "/supernet/interface" in routes
    assert "/supernet/agent/capabilities" in routes
    assert "/supernet/agent/self" in routes
    assert "/mcp" in routes

    with TestClient(app) as client:
        response = client.get("/supernet/interface/capabilities")
        assert response.status_code == 200
        assert response.headers["x-supernet-project-closure"] == contract["id"]
        assert response.headers["x-supernet-semantic-carrier"] == SEMANTIC_CARRIER
        assert response.headers["x-supernet-translate"] == TRANSLATE_OPERATOR
        assert response.headers["x-supernet-runtime-identity"] == RUNTIME_IDENTITY_LAW


def test_identical_inputs_replay_the_same_translational_truth_identity(
    tmp_path: Path,
) -> None:
    first = _run_identical_translation(tmp_path / "first")
    second = _run_identical_translation(tmp_path / "second")

    assert canonical_json(first) == canonical_json(second)
    assert first["operator"] == TRANSLATE_OPERATOR
    assert first["translation_operator"] == TRANSLATE_OPERATOR
    assert first["source_runtime_identity_id"] == first["before_runtime_identity_id"]
    assert first["target_runtime_identity_id"] == first["after_runtime_identity_id"]
    assert first["target_runtime_identity_id"] == first[
        "target_form_runtime_identity_id"
    ]
    assert first["runtime_state_change_is_this_translation"] is True
    assert first["browser_trajectory_is_this_translation"] is True
    assert first["runtime_identity_is_translational_truth"] is True
    assert first["exact_source"] == EXACT_RETURN
    assert first["headers"] == {
        "project": runtime_project_closure_contract()["id"],
        "carrier": SEMANTIC_CARRIER,
        "operator": TRANSLATE_OPERATOR,
        "identity": RUNTIME_IDENTITY_LAW,
    }
