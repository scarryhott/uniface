from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.full_supernet_potential_gate import (
    OPEN_RETURN_EXTENSION,
    PERSPECTIVE_TRANSPORT,
    validate_full_supernet_gate_contract,
)


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "full-gate.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _open_path(full: dict) -> dict:
    gate = full["relative_natural_form_potential_gate"]
    return next(
        path
        for path in gate["paths"]
        if path["status"] != "WITNESSED"
        and path["action"] == OPEN_RETURN_EXTENSION
    )


def _return(client: TestClient, full: dict, source: str) -> dict:
    path = _open_path(full)
    response = client.post(
        f"/supernet/potential-gates/{full['id']}/return",
        json={
            "relation_id": path["id"],
            "perspective_id": full["perspective_id"],
            "focus_event_id": full["focus_event_id"],
            "navigation_context": full["navigation_context"],
            "exact_source_return": source,
            "local_perspective_hair_millidegrees": 12000,
            "local_perspective_zoom_milli": 1400,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["returned"] is True
    return response.json()["supernet_potential_gate"]


def test_full_supernet_is_truth_plus_relative_natural_form_potential(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        response = client.get(
            "/supernet/potential-gate",
            params={"perspective_id": "perspective:origin"},
        )
    assert response.status_code == 200
    full = response.json()["supernet_potential_gate"]
    assert validate_full_supernet_gate_contract(full)["valid"] is True
    gate = full["relative_natural_form_potential_gate"]
    assert full["supernet_is_relative_natural_form_potential_gate"] is True
    assert full["equality_closure_is_not_the_whole_supernet"] is True
    assert gate["supernet_is_not_isolated_equality_condition"] is True
    assert gate["witnessed_truth_plus_open_potential"] is True
    assert gate["all_retained_families_are_local_potentials"] is True
    assert gate["navigation_relocalises_without_refining_truth"] is True
    assert gate["only_source_preserving_return_refines_truth"] is True
    assert gate["family_potentials"]
    assert gate["paths"]
    assert gate["maze_partition"]["paths_partitioned"] == len(gate["paths"])
    assert len(gate["unitary_curvature"]["path_curvatures"]) == len(
        gate["paths"]
    )
    assert all(
        item["ai_and_token_share_one_curvature_carrier"] is True
        for item in gate["unitary_curvature"]["path_curvatures"]
    )
    assert gate["hair"]["changes_truth"] is False
    assert gate["zoom"]["changes_truth"] is False
    solver = full["potential_gate_natural_form_solver"]
    assert solver["gate_id"] == gate["id"]
    assert solver["equality_is_one_local_constraint"] is True
    assert solver["open_potential_is_part_of_form"] is True
    assert solver["perspectival_path_is_part_of_form"] is True


def test_return_refines_truth_and_rederives_the_whole_gate(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        opened = client.get(
            "/supernet/potential-gate",
            params={"perspective_id": "perspective:return"},
        ).json()["supernet_potential_gate"]
        successor = _return(
            client,
            opened,
            "A returned source refines the closure and therefore the full potential gate.",
        )
    assert successor["id"] != opened["id"]
    assert successor["truth_invariant_id"] != opened["truth_invariant_id"]
    assert successor["relative_natural_form_potential_gate"]["id"] != opened[
        "relative_natural_form_potential_gate"
    ]["id"]
    assert successor["potential_gate_natural_form_solver"]["id"] != opened[
        "potential_gate_natural_form_solver"
    ]["id"]
    assert successor["navigation_context"]["depth"] == 0
    assert opened["navigation_context"]["id"] in successor[
        "navigation_context"
    ]["prior_navigation_context_ids"]
    assert validate_full_supernet_gate_contract(successor)["valid"] is True


def test_perspective_navigation_relocalises_one_unchanged_truth_gate(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        origin_a = client.get(
            "/supernet/potential-gate",
            params={"perspective_id": "perspective:a"},
        ).json()["supernet_potential_gate"]
        _return(client, origin_a, "Perspective A returns one exact relation.")

        origin_b = client.get(
            "/supernet/potential-gate",
            params={"perspective_id": "perspective:b"},
        ).json()["supernet_potential_gate"]
        _return(client, origin_b, "Perspective B returns another exact relation.")

        at_a = client.get(
            "/supernet/potential-gate",
            params={"perspective_id": "perspective:a"},
        ).json()["supernet_potential_gate"]
        transport = next(
            path
            for path in at_a["relative_natural_form_potential_gate"]["paths"]
            if path["action"] == PERSPECTIVE_TRANSPORT
            and path["target_perspective_id"] == "perspective:b"
        )
        response = client.post(
            f"/supernet/potential-gates/{at_a['id']}/navigate",
            json={
                "relation_id": transport["id"],
                "perspective_id": at_a["perspective_id"],
                "focus_event_id": at_a["focus_event_id"],
                "navigation_context": at_a["navigation_context"],
            },
        )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["navigated"] is True
    assert payload["truth_refined"] is False
    at_b = payload["supernet_potential_gate"]
    assert at_b["perspective_id"] == "perspective:b"
    assert at_b["truth_invariant_id"] == at_a["truth_invariant_id"]
    assert at_b["navigation_context"]["depth"] == (
        at_a["navigation_context"]["depth"] + 1
    )
    step = at_b["navigation_context"]["steps"][-1]
    assert step["source_perspective_id"] == "perspective:a"
    assert step["target_perspective_id"] == "perspective:b"
    assert step["truth_invariant_id"] == at_a["truth_invariant_id"]
    assert at_b["relative_natural_form_potential_gate"][
        "active_perspective_id"
    ] == "perspective:b"
    assert validate_full_supernet_gate_contract(at_b)["valid"] is True


def test_live_surface_navigates_the_gate_not_a_fixed_focus_graph(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/")
        capabilities = client.get("/supernet/interface/capabilities").json()
    assert page.status_code == 200
    html = page.text
    static_body = html.split("<body>", 1)[1].split("<script>", 1)[0].strip()
    assert static_body == '<main id="translational-mirror"></main>'
    assert "/supernet/potential-gate" in html
    assert "/supernet/potential-gates/" in html
    assert "PERSPECTIVE_TRANSPORT" in html
    assert "OPEN_RETURN_EXTENSION" in html
    assert "data-relative-natural-form-potential-gate" in html
    assert "data-equality-is-local-gate-constraint" in html
    assert "data-visible-equals-interaction" in html
    assert "loadContract(relation.target_state_id)" not in html
    assert capabilities["surface"] == "RELATIVE_NATURAL_FORM_POTENTIAL_GATE"
    assert capabilities["navigation_mutates_truth"] is False
    assert capabilities["return_may_refine_truth"] is True
    assert capabilities["equality_is_one_local_gate_constraint"] is True


def test_browser_rederives_and_accepts_the_full_potential_gate(
    tmp_path: Path,
) -> None:
    import json
    import shutil
    import subprocess

    node = shutil.which("node")
    if node is None:
        return
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/")
        full = client.get(
            "/supernet/potential-gate",
            params={"perspective_id": "perspective:browser-gate"},
        ).json()["supernet_potential_gate"]
    source = page.text
    script_source = source.split("<script>", 1)[1].split("</script>", 1)[0]
    syntax = subprocess.run(
        [node, "--check", "-"],
        input=script_source,
        text=True,
        capture_output=True,
        check=False,
    )
    assert syntax.returncode == 0, syntax.stderr or syntax.stdout
    start = script_source.index("function asText(v)")
    end = script_source.index("function phaseWeight", start)
    verifier = script_source[start:end]
    script = f'''\nconst crypto=require("node:crypto").webcrypto;\n{verifier}\nlet input="";process.stdin.setEncoding("utf8");process.stdin.on("data",c=>input+=c);process.stdin.on("end",async()=>{{const value=JSON.parse(input);process.stdout.write(JSON.stringify({{valid:await contractMatches(value)}}));}});\n'''
    result = subprocess.run(
        [node, "-e", script],
        input=json.dumps(full, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert json.loads(result.stdout) == {"valid": True}
