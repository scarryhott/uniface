from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERCEL_JSON = ROOT / "vercel.json"
ASGI_ENTRY = ROOT / "asgi.py"


def test_vercel_selects_the_projection_only_asgi_entry() -> None:
    payload = json.loads(VERCEL_JSON.read_text(encoding="utf-8"))
    assert payload.get("framework") == "fastapi"
    assert "asgi.py" in (payload.get("functions") or {})
    source = ASGI_ENTRY.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {
        node.module for node in tree.body if isinstance(node, ast.ImportFrom)
    }
    assert "closure_supernet.api_agent" in imported_modules
    assert "closure_supernet.api_inversion" not in imported_modules
    assert 'CLOSURE_ENVIRONMENT", "production"' in source
    assert 'CLOSURE_PROJECTION_ONLY_MODE", "true"' in source


def test_vercel_asgi_executes_one_projection_and_one_return(tmp_path: Path) -> None:
    script = """
import os, sys
os.environ["CLOSURE_DB_PATH"] = {db!r}
os.environ["CLOSURE_INBOX_DIR"] = {inbox!r}
os.environ["CLOSURE_BACKUP_DIR"] = {backups!r}
os.environ["CLOSURE_AUTONOMY_ENABLED"] = "false"
os.environ["CLOSURE_TRUSTED_HOSTS"] = "testserver,localhost,127.0.0.1"
sys.path.insert(0, {root!r})
import asgi
for forbidden in (
    "closure_supernet.api_natural_interface",
    "closure_supernet.agent_mcp",
    "closure_supernet.coordination",
    "closure_supernet.complete_interface_models",
    "closure_supernet.runtime",
):
    assert forbidden not in sys.modules, forbidden
from fastapi.testclient import TestClient
from closure_supernet.minimal_projection_runtime import derive_local_projection_commitment
with TestClient(asgi.app) as client:
    root = client.get("/")
    initial = client.get("/supernet/interface", params={{"perspective_id": "p"}}).json()["closure_ui_contract"]
    result = client.post(
        f"/supernet/interface/projections/{{initial['id']}}/return",
        json={{
            "return_relation_id": initial["return_relation"]["id"],
            "perspective_id": "p",
            "focus_event_id": None,
            "exact_source_return": "One exact visual return.",
            "closure_equation_system_id": initial["closure_naturality_equations"]["id"],
            "local_projection_commitment": derive_local_projection_commitment(
                initial,
                return_relation_id=initial["return_relation"]["id"],
                perspective_id="p",
                focus_event_id=None,
                exact_source_return="One exact visual return.",
            ),
        }},
    )
    assert root.status_code == 200
    assert '<main id="translational-mirror"></main>' in root.text
    assert result.status_code == 200, result.text
    assert result.json()["closure_ui_contract"]["status"] == "WITNESSED"
    assert client.get("/trading").status_code == 404
    assert client.get("/mcp").status_code == 404
print("ok")
""".format(
        db=str(tmp_path / "isolated.db"),
        inbox=str(tmp_path / "inbox"),
        backups=str(tmp_path / "backups"),
        root=str(ROOT),
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "ok" in result.stdout
