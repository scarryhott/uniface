from __future__ import annotations

import json
import shutil
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.closure_only_interface import CLOSURE_ONLY_SUPERNET_HTML
from closure_supernet.closure_ui_contract import (
    PROTOCOL,
    RETURN_ENDPOINT_TEMPLATE,
    SCHEMA,
    _digest,
    _stable,
    validate_ui_contract,
)
from closure_supernet.config import RuntimeConfig
from closure_supernet.minimal_projection_runtime import (
    derive_local_projection_commitment,
)


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "browser-contract.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def actual_open_and_witnessed_contracts(
    tmp_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        opened = client.get(
            "/supernet/interface",
            params={"perspective_id": "perspective:browser-check"},
        ).json()["closure_ui_contract"]
        exact_source = "An exact source returned through the browser."
        response = client.post(
            RETURN_ENDPOINT_TEMPLATE.format(contract_id=opened["id"]),
            json={
                "return_relation_id": opened["return_relation"]["id"],
                "perspective_id": opened["perspective_id"],
                "focus_event_id": opened["focus_event_id"],
                "exact_source_return": exact_source,
                "closure_equation_system_id": opened[
                    "closure_naturality_equations"
                ]["id"],
                "local_projection_commitment": derive_local_projection_commitment(
                    opened,
                    return_relation_id=opened["return_relation"]["id"],
                    perspective_id=opened["perspective_id"],
                    focus_event_id=opened["focus_event_id"],
                    exact_source_return=exact_source,
                ),
                "source_stream": "browser-contract-test",
            },
        )
        assert response.status_code == 200, response.text
        committed = response.json()["closure_ui_contract"]
        translated_response = client.get(
            "/supernet/interface",
            params={
                "perspective_id": "perspective:browser-check-translated",
                "focus_event_id": committed["focus_event_id"],
            },
        )
        assert translated_response.status_code == 200, translated_response.text
        witnessed = translated_response.json()["closure_ui_contract"]
    return opened, witnessed


def javascript_function(start: str, end: str) -> str:
    source = CLOSURE_ONLY_SUPERNET_HTML
    start_index = source.index(start)
    end_index = source.index(end, start_index)
    return source[start_index:end_index].strip()


def browser_contract_checks(
    node: str,
    contracts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    functions = "\n\n".join(
        [
            javascript_function(
                "  function asText(value) {",
                "  function unique(values) {",
            ),
            javascript_function(
                "  function unique(values) {",
                "  function sameMembers(left, right) {",
            ),
            javascript_function(
                "  function sameMembers(left, right) {",
                "  function stable(value) {",
            ),
            javascript_function(
                "  function stable(value) {",
                "  async function contractIdMatchesContent(contract) {",
            ),
            javascript_function(
                "  async function contractIdMatchesContent(contract) {",
                "  function derivationMatches(contract, derivation, allowOpen = false) {",
            ),
            javascript_function(
                "  function derivationMatches(contract, derivation, allowOpen = false) {",
                "  function validate(contract) {",
            ),
            javascript_function(
                "  function validate(contract) {",
                "  function sourceBlock(svg, x, y, width, height, text, className) {",
            ),
        ]
    )
    script = f"""
const crypto = require("node:crypto").webcrypto;
const schema = {json.dumps(SCHEMA)};
const protocol = {json.dumps(PROTOCOL)};
const statuses = new Set([
  "OPEN_SOURCE_BOUNDARY",
  "OPEN_TRUTH_CONSTRAINT",
  "WITNESSED",
]);
const locallyDerivedVisualizations = new WeakMap();
{functions}

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => input += chunk);
process.stdin.on("end", async () => {{
  const contracts = JSON.parse(input);
  const results = [];
  for (const contract of contracts) {{
    const body = Object.create(null);
    for (const [key, value] of Object.entries(contract)) {{
      if (key !== "id") body[key] = value;
    }}
    results.push({{
      canonical: stable(body),
      id_matches: await contractIdMatchesContent(contract),
      equations_match: await closureNaturalityEquationsMatch(contract),
      visualization_matches: await visualizationMatches(contract),
      boundary_and_structure_valid: validate(contract),
    }});
  }}
  process.stdout.write(JSON.stringify(results));
}});
"""
    checked = subprocess.run(
        [node, "--check", "-"],
        input=script,
        capture_output=True,
        text=True,
        check=False,
    )
    assert checked.returncode == 0, checked.stderr or checked.stdout
    result = subprocess.run(
        [node, "-e", script],
        input=json.dumps(contracts, ensure_ascii=False),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    return json.loads(result.stdout)


def reseal_content_id(contract: dict[str, Any]) -> dict[str, Any]:
    resealed = deepcopy(contract)
    body = {key: value for key, value in resealed.items() if key != "id"}
    resealed["id"] = _digest("translational-visualization", body)
    return resealed


def test_browser_sha256_matches_python_and_both_rejection_gates(
    tmp_path: Path,
) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required to execute the published browser verifier")

    opened, witnessed = actual_open_and_witnessed_contracts(tmp_path)
    assert opened["status"] == "OPEN_SOURCE_BOUNDARY"
    assert witnessed["status"] == "WITNESSED"
    assert validate_ui_contract(opened)["valid"] is True
    assert validate_ui_contract(witnessed)["valid"] is True

    content_tamper = deepcopy(witnessed)
    content_tamper["projection"]["states"][0]["source_trace"] = (
        "A client-authored substitute with the server content ID left unchanged."
    )

    boundary_tamper = deepcopy(witnessed)
    boundary_tamper["closure_process"]["boundary"][
        "external_resource_admitted"
    ] = True
    boundary_tamper = reseal_content_id(boundary_tamper)

    contracts = [opened, witnessed, content_tamper, boundary_tamper]
    results = browser_contract_checks(node, contracts)

    for contract, result in zip(contracts, results, strict=True):
        body = {key: value for key, value in contract.items() if key != "id"}
        assert result["canonical"] == _stable(body)

    assert results[0]["id_matches"] is True
    assert results[0]["equations_match"] is True
    assert results[0]["boundary_and_structure_valid"] is True
    assert results[1]["id_matches"] is True
    assert results[1]["equations_match"] is True
    assert results[1]["visualization_matches"] is True
    assert results[1]["boundary_and_structure_valid"] is True

    # The substitute source is structurally plausible.  Only recomputing the
    # content-addressed contract ID prevents it becoming a client-local truth.
    assert results[2]["boundary_and_structure_valid"] is True
    assert results[2]["id_matches"] is False
    assert validate_ui_contract(content_tamper)["valid"] is False

    # Conversely, a malicious client can recompute an untrusted content ID,
    # but it still cannot cross the external-effect/consciousness boundary.
    assert results[3]["id_matches"] is True
    assert results[3]["boundary_and_structure_valid"] is False
    assert validate_ui_contract(boundary_tamper)["valid"] is False

    assert "if (!validate(contract)" in CLOSURE_ONLY_SUPERNET_HTML
    assert "!await closureNaturalityEquationsMatch(contract)" in (
        CLOSURE_ONLY_SUPERNET_HTML
    )
    assert "!await visualizationMatches(contract)" in CLOSURE_ONLY_SUPERNET_HTML
    assert "!await contractIdMatchesContent(contract)" in CLOSURE_ONLY_SUPERNET_HTML
    assert '"data-local-modification": "UNCOMMITTED_CLOSURE_POTENTIAL"' in (
        CLOSURE_ONLY_SUPERNET_HTML
    )
    assert '"data-local-perspective-hair": localHairMillidegrees' in (
        CLOSURE_ONLY_SUPERNET_HTML
    )
    assert 'await digest("local-projection"' in CLOSURE_ONLY_SUPERNET_HTML
    assert "committed.closure_rederived !== true" in CLOSURE_ONLY_SUPERNET_HTML


def test_browser_rederives_exact_naturality_equations_before_rendering(
    tmp_path: Path,
) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required to execute the published browser verifier")

    _, witnessed = actual_open_and_witnessed_contracts(tmp_path)
    tampered = deepcopy(witnessed)
    tampered["closure_naturality_equations"]["finite_instance"][
        "pull_growth_stages"
    ][0]["naturality_square_commutes"] = False
    tampered["closure_naturality_equations"]["checks"][
        "all_pull_naturality_squares_commute"
    ] = False
    tampered = reseal_content_id(tampered)

    [result] = browser_contract_checks(node, [tampered])
    assert result["id_matches"] is True
    assert result["equations_match"] is False
    assert validate_ui_contract(tampered)["valid"] is False


def test_browser_rederives_exact_geometry_before_rendering(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required to execute the published browser verifier")

    _, witnessed = actual_open_and_witnessed_contracts(tmp_path)
    tampered = deepcopy(witnessed)
    tampered["projection"]["visualization"]["fibre_primitives"][0]["centre"][0] += 1
    tampered = reseal_content_id(tampered)

    [result] = browser_contract_checks(node, [tampered])
    assert result["id_matches"] is True
    assert result["boundary_and_structure_valid"] is True
    assert result["visualization_matches"] is False
    assert validate_ui_contract(tampered)["valid"] is False
    assert "const visualization = locallyDerivedVisualizations.get(active)" in (
        CLOSURE_ONLY_SUPERNET_HTML
    )


def test_browser_canonical_json_matches_python_for_unicode_and_proto(
    tmp_path: Path,
) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required to execute the published browser verifier")

    _, witnessed = actual_open_and_witnessed_contracts(tmp_path)
    adversarial = deepcopy(witnessed)
    adversarial["\ue000"] = {"position": "private-use-code-point"}
    adversarial["\U00010000"] = {"position": "supplementary-code-point"}
    adversarial["__proto__"] = {"must_remain_own_content": True}
    adversarial = reseal_content_id(adversarial)

    assert validate_ui_contract(adversarial)["valid"] is True
    [result] = browser_contract_checks(node, [adversarial])
    body = {key: value for key, value in adversarial.items() if key != "id"}
    assert result["canonical"] == _stable(body)
    assert result["id_matches"] is True
    assert result["boundary_and_structure_valid"] is True
    assert '"__proto__":{"must_remain_own_content":true}' in result["canonical"]
    assert result["canonical"].index('"\ue000"') < result["canonical"].index(
        '"\U00010000"'
    )


def test_browser_recomputes_perspective_closure_and_same_origin_endpoint(
    tmp_path: Path,
) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required to execute the published browser verifier")

    _, witnessed = actual_open_and_witnessed_contracts(tmp_path)
    closure = witnessed["perspective_closure"]
    assert len(closure["readings"]) == 2
    assert len(closure["translations"]) == 1

    forged_mapping = deepcopy(witnessed)
    mapping = forged_mapping["perspective_closure"]["translations"][0][
        "display_translation"
    ]
    source_display = next(iter(mapping))
    mapping[source_display] = f"{mapping[source_display]}:forged"

    missing_carrier = deepcopy(witnessed)
    inactive_perspective = next(
        perspective
        for perspective in missing_carrier["perspective_closure"]["readings"]
        if perspective != missing_carrier["perspective_id"]
    )
    inactive_reading = missing_carrier["perspective_closure"]["readings"][
        inactive_perspective
    ]
    inactive_reading.pop(next(iter(inactive_reading)))

    forged_kernel = deepcopy(witnessed)
    forged_kernel["perspective_closure"]["kernel"] = [["state:not-in-carrier"]]

    disconnected = deepcopy(witnessed)
    disconnected["perspective_closure"]["translations"] = []

    forged_provenance = deepcopy(witnessed)
    forged_provenance["perspective_closure"]["translations"][0][
        "source_return_ids"
    ] = ["return:not-in-contract"]

    forged_endpoint = deepcopy(witnessed)
    forged_endpoint["execution"]["endpoint_template"] = (
        "https://attacker.invalid/supernet/{contract_id}/return"
    )

    forged_process = deepcopy(witnessed)
    forged_process["closure_process"]["relative_proofs"][
        "runtime_additive_content_verified"
    ] = True

    forged_lineage = deepcopy(witnessed)
    forged_lineage["continuation_lineage_ids"] = []

    adversarial = [
        reseal_content_id(contract)
        for contract in (
            forged_mapping,
            missing_carrier,
            forged_kernel,
            disconnected,
            forged_provenance,
            forged_endpoint,
            forged_process,
            forged_lineage,
        )
    ]
    results = browser_contract_checks(node, adversarial)
    assert all(result["id_matches"] is True for result in results)
    assert all(result["boundary_and_structure_valid"] is False for result in results)
    assert all(validate_ui_contract(contract)["valid"] is False for contract in adversarial)


def test_return_navigation_commits_only_after_successor_verification() -> None:
    source = javascript_function(
        "  async function returnSource() {",
        '  sensor.addEventListener("input", () => {',
    )
    verification = source.index("if (!await verifyContract(next)) return;")
    draft_commit = source.index("if (draft === exactSourceReturn)")
    navigation_commit = source.index("history.replaceState(null, \"\", current);")
    render_commit = source.index("render(next);")
    assert verification < draft_commit < navigation_commit < render_commit
    assert (
        "`/supernet/interface/projections/${encodeURIComponent(submittedContract.id)}/return`"
        in source
    )
    assert "active.execution.endpoint_template" not in source
    assert "active !== submittedContract" in source


def test_malformed_continuation_metadata_is_rejected_without_raising(
    tmp_path: Path,
) -> None:
    _, witnessed = actual_open_and_witnessed_contracts(tmp_path)
    malformed = deepcopy(witnessed)
    malformed["continuation_index"] = "not-an-integer"
    malformed["continuation_lineage_ids"] = 42

    validation = validate_ui_contract(malformed)
    assert validation["valid"] is False
    assert "continuation:index" in validation["errors"]
    assert "continuation:lineage-shape" in validation["errors"]
