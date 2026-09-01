from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "equal-browser.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def test_equal_translation_browser_accepts_the_current_verified_contract(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required to execute the production browser verifier")

    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/")
        contract = client.get(
            "/supernet/interface",
            params={"perspective_id": "perspective:equal-browser"},
        ).json()["closure_ui_contract"]

    source = page.text
    start = source.index("  function asText(value) {")
    end = source.index("  function solvePoint(solution, point) {", start)
    verifier = source[start:end]
    script = f'''\nconst crypto = require("node:crypto").webcrypto;\n{verifier}\nlet input = "";\nprocess.stdin.setEncoding("utf8");\nprocess.stdin.on("data", chunk => input += chunk);\nprocess.stdin.on("end", async () => {{\n  const contract = JSON.parse(input);\n  process.stdout.write(JSON.stringify({{matches: await contractMatches(contract)}}));\n}});\n'''
    syntax = subprocess.run(
        [node, "--check", "-"],
        input=script,
        capture_output=True,
        text=True,
        check=False,
    )
    assert syntax.returncode == 0, syntax.stderr or syntax.stdout
    result = subprocess.run(
        [node, "-e", script],
        input=json.dumps(contract, ensure_ascii=False),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert json.loads(result.stdout) == {"matches": True}


def test_equal_translation_surface_has_no_hidden_interaction_geometry(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        html = client.get("/").text

    assert ".closure-relation" in html
    assert "pointer-events:stroke" in html
    assert '"data-visible-equals-interaction":"true"' in html
    assert '"data-same-object-visible-and-interactive":"true"' in html
    assert '"data-presentation-only":"false"' in html
    assert "natural-form-family-layer" not in html
