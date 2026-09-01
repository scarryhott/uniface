from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.full_supernet_potential_gate import (
    validate_full_supernet_gate_contract,
)


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "full-gate-contract.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def test_gate_rejects_truth_reduction_and_navigation_truth_drift(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        full = client.get(
            "/supernet/potential-gate",
            params={"perspective_id": "perspective:guard"},
        ).json()["supernet_potential_gate"]

    reduced = deepcopy(full)
    reduced["relative_natural_form_potential_gate"][
        "supernet_is_not_isolated_equality_condition"
    ] = False
    assert validate_full_supernet_gate_contract(reduced)["valid"] is False

    drift = deepcopy(full)
    drift["navigation_context"]["truth_invariant_id"] = "forged"
    assert validate_full_supernet_gate_contract(drift)["valid"] is False


def test_every_gate_path_is_truth_inert_until_return(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        full = client.get(
            "/supernet/potential-gate",
            params={"perspective_id": "perspective:path-guard"},
        ).json()["supernet_potential_gate"]

    gate = full["relative_natural_form_potential_gate"]
    assert gate["paths"]
    assert all(path["navigation_changes_truth"] is False for path in gate["paths"])
    assert all(
        path["selection_executes_as_equality"] is False for path in gate["paths"]
    )
    assert all(
        path["return_required_to_refine_truth"] is True for path in gate["paths"]
    )
