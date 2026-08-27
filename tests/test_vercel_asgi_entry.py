from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_inversion import create_app
from closure_supernet.config import RuntimeConfig


ROOT = Path(__file__).resolve().parents[1]
DOCS_INDEX = ROOT / "docs" / "index.html"
VERCEL_JSON = ROOT / "vercel.json"
ASGI_ENTRY = ROOT / "asgi.py"


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "vercel.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def test_root_vercel_json_selects_fastapi_asgi_not_docs_static() -> None:
    assert VERCEL_JSON.is_file()
    payload = json.loads(VERCEL_JSON.read_text(encoding="utf-8"))
    assert payload.get("framework") == "fastapi"
    functions = payload.get("functions") or {}
    assert "asgi.py" in functions
    exclude = functions["asgi.py"].get("excludeFiles", "")
    assert "docs/**" in exclude
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'entrypoint = "asgi:app"' in pyproject


def test_asgi_entry_reexports_existing_inversion_app() -> None:
    source = ASGI_ENTRY.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "closure_supernet.api_inversion"
    ]
    assert imports, "ASGI entry must import the existing FastAPI app"
    names = {alias.name for node in imports for alias in node.names}
    assert "app" in names
    assert "FastAPI(" not in source
    assert "docs/index.html" not in source


def test_serve_equivalent_root_is_integrator_field_not_docs_loop_face(
    tmp_path: Path,
) -> None:
    leftover = DOCS_INDEX.read_text(encoding="utf-8")
    assert "data-projection=\"face\"" in leftover

    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        root = client.get("/")
        supernet = client.get("/supernet")
        field = client.get("/supernet/field")
        self_limit = client.get("/self-limit")

    assert root.status_code == 200
    assert "text/html" in root.headers.get("content-type", "")
    assert "One continuous integrator" in root.text
    assert "data-projection=\"face\"" not in root.text
    assert "notes as undetermined Sense" not in root.text

    assert supernet.status_code == 200
    assert supernet.text == root.text

    assert field.status_code == 200
    payload = field.json()
    assert payload["canonical_runtime_operation"] == "integrate"
    assert payload["subsystems_are_lenses"] is True
    assert payload["truth_issued_by_determination"] is False

    assert self_limit.status_code == 200
    assert "One inversion" in self_limit.text
    assert self_limit.text != root.text


def test_asgi_module_serves_integrator_in_isolated_process(tmp_path: Path) -> None:
    db = tmp_path / "isolated.db"
    inbox = tmp_path / "inbox"
    backups = tmp_path / "backups"
    script = """
import os, sys
os.environ["CLOSURE_DB_PATH"] = {db!r}
os.environ["CLOSURE_INBOX_DIR"] = {inbox!r}
os.environ["CLOSURE_BACKUP_DIR"] = {backups!r}
os.environ["CLOSURE_AUTONOMY_ENABLED"] = "false"
os.environ["CLOSURE_TRUSTED_HOSTS"] = "testserver,localhost,127.0.0.1"
sys.path.insert(0, {root!r})
import asgi
from fastapi.testclient import TestClient
with TestClient(asgi.app) as client:
    root = client.get("/")
    field = client.get("/supernet/field")
    assert root.status_code == 200
    assert "One continuous integrator" in root.text
    assert "data-projection=\\"face\\"" not in root.text
    payload = field.json()
    assert payload["canonical_runtime_operation"] == "integrate"
    assert payload["truth_issued_by_determination"] is False
print("ok")
""".format(db=str(db), inbox=str(inbox), backups=str(backups), root=str(ROOT))
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
