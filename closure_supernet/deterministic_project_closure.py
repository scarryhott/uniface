from __future__ import annotations

"""Deterministic project-wide closure for Supernet.

The current project has one semantic carrier, one transition operator, and one
runtime-identity law. Every other executable component is either a projection or
transport of that law, or retained historical evidence which is mechanically
prevented from becoming a published authority.

Two related closures are exposed:

* ``runtime_project_closure_contract`` is the small invariant attached to the
  live application. It is independent of clocks, process identifiers, random
  values, absolute paths, and file-system iteration order.
* ``build_project_closure_manifest`` and ``audit_project_closure`` inventory and
  verify every tracked project artifact in deterministic lexical order. This is
  the blocking project boundary preventing a second mutation, identity, or
  truth authority from re-entering Supernet.
"""

import argparse
import ast
import hashlib
import json
import subprocess
from collections import deque
from pathlib import Path
from typing import Any, Mapping, Sequence

from .supernet_closure_form import TRANSLATE_OPERATOR

PROJECT_CLOSURE_SCHEMA = "closure.supernet/deterministic-project-closure-v1"
PROJECT_CLOSURE_PROTOCOL = "DETERMINISTIC_TRANSLATIONAL_TRUTH_RUNTIME"
SEMANTIC_CARRIER = "SUPERNET_CLOSURE_FORM"
RUNTIME_IDENTITY_LAW = "TRANSLATIONAL_TRUTH_CLASS"
PUBLIC_ENTRY_MODULE = "closure_supernet.api_agent"
AUTHORITATIVE_TRANSITION_OWNER = "closure_supernet/supernet_closure_runtime.py"

TRANSPORT_MODULE_PATHS = (
    "asgi.py",
    "closure_supernet/api_agent.py",
    "closure_supernet/agent_closure_mcp.py",
    "closure_supernet/self_runtime_projection.py",
)

# Historical manager-composition agent calls may remain as versioned evidence,
# but no module reachable from the published entrypoint may invoke them as a
# current mutation authority.
LEGACY_AGENT_MUTATION_PATTERNS = (
    "runtime.live_sense.offer",
    "runtime.live_sense.interact",
    "runtime.topology.create_relation",
    "runtime.selection.create_reading",
    "runtime.topology.return_event",
    "runtime.topology.reopen",
    "runtime.topology.create_collective_trace",
)

MUTATING_HTTP_DECORATORS = frozenset({"post", "put", "patch", "delete"})
EXCLUDED_DIRECTORY_NAMES = frozenset(
    {
        ".git",
        ".lake",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "lake-packages",
        "node_modules",
    }
)


def canonical_json(value: Any) -> str:
    """The sole JSON normalization for deterministic project receipts."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def content_id(prefix: str, value: Any, *, length: int = 24) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return f"{prefix}:{digest[:length]}"


def find_project_root(start: str | Path | None = None) -> Path:
    candidate = Path(start).resolve() if start is not None else Path(__file__).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for root in (candidate, *candidate.parents):
        if (root / "pyproject.toml").is_file() and (root / "closure_supernet").is_dir():
            return root
    # Installed wheels use only the runtime law. This deterministic fallback is
    # still useful when a caller explicitly asks for the installed package
    # inventory rather than a checkout-wide manifest.
    return Path(__file__).resolve().parent.parent


def _git_tracked_paths(root: Path) -> list[Path] | None:
    if not (root / ".git").exists():
        return None
    process = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=False,
        capture_output=True,
    )
    if process.returncode != 0:
        return None
    paths: list[Path] = []
    for raw in process.stdout.split(b"\0"):
        if not raw:
            continue
        try:
            relative = Path(raw.decode("utf-8"))
        except UnicodeDecodeError:
            continue
        path = root / relative
        if path.is_file():
            paths.append(path)
    return sorted(paths, key=lambda item: item.relative_to(root).as_posix())


def iter_project_files(root: str | Path | None = None) -> tuple[Path, ...]:
    project_root = find_project_root(root)
    tracked = _git_tracked_paths(project_root)
    if tracked is not None:
        return tuple(tracked)

    paths: list[Path] = []
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(project_root)
        if any(part in EXCLUDED_DIRECTORY_NAMES for part in relative.parts):
            continue
        paths.append(path)
    return tuple(sorted(paths, key=lambda item: item.relative_to(project_root).as_posix()))


def _role_for_path(relative: str) -> str:
    path = Path(relative)
    if relative == AUTHORITATIVE_TRANSITION_OWNER:
        return "AUTHORITATIVE_TRANSITION"
    if relative in TRANSPORT_MODULE_PATHS:
        return "TRANSPORT_OR_PROJECTION"
    if path.suffix == ".lean":
        return "FORMAL_PROOF"
    if path.parts and path.parts[0] == "tests":
        return "VERIFICATION"
    if len(path.parts) >= 2 and path.parts[:2] == (".github", "workflows"):
        return "DETERMINISTIC_ENFORCEMENT"
    if path.parts and path.parts[0] == "closure_supernet":
        return "RETAINED_RUNTIME_OR_NATURAL_FORM"
    if path.suffix.lower() in {".md", ".rst", ".txt"}:
        return "DOCUMENTATION"
    if relative in {"Dockerfile", "pyproject.toml", "railway.toml", "vercel.json"}:
        return "DEPLOYMENT_INFRASTRUCTURE"
    return "PROJECT_ARTIFACT"


def build_project_closure_manifest(root: str | Path | None = None) -> dict[str, Any]:
    project_root = find_project_root(root)
    records: list[dict[str, Any]] = []
    role_counts: dict[str, int] = {}
    for path in iter_project_files(project_root):
        relative = path.relative_to(project_root).as_posix()
        role = _role_for_path(relative)
        role_counts[role] = role_counts.get(role, 0) + 1
        data = path.read_bytes()
        records.append(
            {
                "path": relative,
                "role": role,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )

    core = {
        "schema": PROJECT_CLOSURE_SCHEMA,
        "protocol": PROJECT_CLOSURE_PROTOCOL,
        "semantic_carrier": SEMANTIC_CARRIER,
        "transition_operator": TRANSLATE_OPERATOR,
        "runtime_identity_law": RUNTIME_IDENTITY_LAW,
        "authoritative_transition_owner": AUTHORITATIVE_TRANSITION_OWNER,
        "file_count": len(records),
        "role_counts": dict(sorted(role_counts.items())),
        "files": records,
    }
    return {"id": content_id("supernet-project-closure", core), **core}


def manifest_path_set(manifest: Mapping[str, Any]) -> set[str]:
    return {
        str(record.get("path"))
        for record in manifest.get("files", [])
        if isinstance(record, Mapping)
    }


def _module_name(relative: str) -> str | None:
    path = Path(relative)
    if path.suffix != ".py":
        return None
    if relative == "asgi.py":
        return "asgi"
    if not path.parts or path.parts[0] != "closure_supernet":
        return None
    parts = list(path.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _python_sources(project_root: Path) -> tuple[dict[str, str], dict[str, str]]:
    by_path: dict[str, str] = {}
    module_to_path: dict[str, str] = {}
    for path in iter_project_files(project_root):
        relative = path.relative_to(project_root).as_posix()
        module = _module_name(relative)
        if module is None:
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        by_path[relative] = source
        module_to_path[module] = relative
    return by_path, module_to_path


def _module_package(module: str, relative: str) -> str:
    if Path(relative).name == "__init__.py":
        return module
    return module.rpartition(".")[0]


def _resolve_imports(
    module: str,
    relative: str,
    tree: ast.AST,
    known_modules: set[str],
) -> set[str]:
    result: set[str] = set()
    package = _module_package(module, relative)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                candidate = alias.name
                while candidate:
                    if candidate in known_modules:
                        result.add(candidate)
                        break
                    candidate = candidate.rpartition(".")[0]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package.split(".") if package else []
                ascend = max(node.level - 1, 0)
                if ascend:
                    base = base[:-ascend] if ascend <= len(base) else []
                if node.module:
                    base.extend(node.module.split("."))
                parent = ".".join(part for part in base if part)
            else:
                parent = node.module or ""
            if parent in known_modules:
                result.add(parent)
            for alias in node.names:
                candidate = ".".join(part for part in (parent, alias.name) if part)
                if candidate in known_modules:
                    result.add(candidate)
    return result


def _public_import_closure(
    sources: Mapping[str, str],
    module_to_path: Mapping[str, str],
) -> tuple[set[str], list[str]]:
    known = set(module_to_path)
    parsed: dict[str, ast.AST] = {}
    errors: list[str] = []
    for module, relative in module_to_path.items():
        try:
            parsed[module] = ast.parse(sources[relative], filename=relative)
        except SyntaxError as exc:
            errors.append(f"python-syntax:{relative}:{exc.lineno}:{exc.msg}")

    roots = [
        name
        for name in ("closure_supernet", PUBLIC_ENTRY_MODULE, "asgi")
        if name in known
    ]
    reachable: set[str] = set()
    queue: deque[str] = deque(sorted(roots))
    while queue:
        module = queue.popleft()
        if module in reachable or module not in parsed:
            continue
        reachable.add(module)
        relative = module_to_path[module]
        imported = _resolve_imports(module, relative, parsed[module], known)
        for candidate in sorted(imported - reachable):
            queue.append(candidate)
    return reachable, errors


def _decorator_name(node: ast.expr) -> str:
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _mutating_http_functions(tree: ast.AST) -> list[str]:
    functions: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(
            _decorator_name(decorator) in MUTATING_HTTP_DECORATORS
            for decorator in node.decorator_list
        ):
            functions.append(node.name)
    return sorted(functions)


def runtime_project_closure_contract() -> dict[str, Any]:
    core = {
        "schema": PROJECT_CLOSURE_SCHEMA,
        "protocol": PROJECT_CLOSURE_PROTOCOL,
        "semantic_carrier": SEMANTIC_CARRIER,
        "transition_operator": TRANSLATE_OPERATOR,
        "runtime_identity_law": RUNTIME_IDENTITY_LAW,
        "interaction_identity": {
            "agent": TRANSLATE_OPERATOR,
            "browser": TRANSLATE_OPERATOR,
            "runtime": TRANSLATE_OPERATOR,
            "user": TRANSLATE_OPERATOR,
        },
        "self_runtime": "RELATIVE_READ_ONLY_PROJECTION",
        "agent_transport": "NO_SEPARATE_MUTATION_OR_TRUTH_AUTHORITY",
        "deterministic": True,
        "clock_authors_identity": False,
        "filesystem_order_authors_identity": False,
        "process_authors_identity": False,
        "randomness_authors_identity": False,
    }
    return {"id": content_id("supernet-runtime-project-closure", core), **core}


def audit_project_closure(root: str | Path | None = None) -> dict[str, Any]:
    project_root = find_project_root(root)
    manifest = build_project_closure_manifest(project_root)
    sources, module_to_path = _python_sources(project_root)
    reachable_modules, errors = _public_import_closure(sources, module_to_path)
    reachable_paths = {
        module_to_path[module]
        for module in reachable_modules
        if module in module_to_path
    }

    owners = sorted(
        relative
        for relative, source in sources.items()
        if "app.state.supernet_translate" in source
        and any(
            marker in source
            for marker in (
                "app.state.supernet_translate =",
                "setattr(app.state, \"supernet_translate\"",
                "setattr(app.state, 'supernet_translate'",
            )
        )
    )
    if owners != [AUTHORITATIVE_TRANSITION_OWNER]:
        errors.append(
            "transition-owner:expected-one:"
            f"{AUTHORITATIVE_TRANSITION_OWNER}:found={','.join(owners) or 'none'}"
        )

    legacy_sites: list[dict[str, str]] = []
    for relative, source in sorted(sources.items()):
        for pattern in LEGACY_AGENT_MUTATION_PATTERNS:
            if pattern not in source:
                continue
            legacy_sites.append({"path": relative, "pattern": pattern})
            if relative in reachable_paths:
                errors.append(f"legacy-mutation-publicly-reachable:{relative}:{pattern}")

    # Route definitions inside retained substrate modules are recorded, because
    # the final app may wrap or replace them. A route becomes a second authority
    # only when it appears in a public transport/entry module instead of the one
    # transition owner. Dynamic runtime tests separately verify that the final
    # published POST transition produces the SUPERNET_TRANSLATE receipt.
    public_mutating_routes: list[dict[str, Any]] = []
    parallel_public_authorities: list[dict[str, Any]] = []
    transport_or_entry = set(TRANSPORT_MODULE_PATHS) | {
        "closure_supernet/api_agent.py"
    }
    for relative in sorted(reachable_paths):
        source = sources.get(relative)
        if source is None:
            continue
        try:
            tree = ast.parse(source, filename=relative)
        except SyntaxError:
            continue
        functions = _mutating_http_functions(tree)
        if not functions:
            continue
        row = {"path": relative, "functions": functions}
        public_mutating_routes.append(row)
        if relative in transport_or_entry and relative != AUTHORITATIVE_TRANSITION_OWNER:
            parallel_public_authorities.append(row)
            errors.append(
                "parallel-public-transport-mutation-authority:"
                f"{relative}:{','.join(functions)}"
            )

    api_source = sources.get("closure_supernet/api_agent.py", "")
    for required in (
        "attach_supernet_agent_mcp",
        "attach_self_runtime_projection",
        "attach_deterministic_project_closure",
        "_create_closure_app",
    ):
        if required not in api_source:
            errors.append(f"public-entry-missing-project-closure:{required}")

    agent_source = sources.get("closure_supernet/agent_closure_mcp.py", "")
    if "app.state.supernet_translate" not in agent_source:
        errors.append("agent-transport-does-not-use-supernet-translate")
    for pattern in LEGACY_AGENT_MUTATION_PATTERNS:
        if pattern in agent_source:
            errors.append(f"agent-transport-retains-parallel-mutation:{pattern}")

    self_source = sources.get("closure_supernet/self_runtime_projection.py", "")
    if any(f"@app.{verb}" in self_source for verb in MUTATING_HTTP_DECORATORS):
        errors.append("self-runtime-has-mutating-http-route")
    if '"self_observation_authors_truth": False' not in self_source:
        errors.append("self-runtime-missing-no-truth-authority-witness")

    central_source = sources.get(AUTHORITATIVE_TRANSITION_OWNER, "")
    if "TRANSLATE_OPERATOR" not in central_source:
        errors.append("authoritative-runtime-missing-translate-operator")

    paths = manifest_path_set(manifest)
    for relative in TRANSPORT_MODULE_PATHS:
        if relative not in paths:
            errors.append(f"missing-transport-module:{relative}")

    runtime_contract = runtime_project_closure_contract()
    error_set = sorted(set(errors))
    warnings = sorted(
        {
            "retained-legacy-mutation-is-nonauthoritative:"
            f"{item['path']}:{item['pattern']}"
            for item in legacy_sites
            if item["path"] not in reachable_paths
        }
    )
    core = {
        "schema": PROJECT_CLOSURE_SCHEMA,
        "manifest_id": manifest["id"],
        "runtime_contract_id": runtime_contract["id"],
        "valid": not error_set,
        "errors": error_set,
        "warnings": warnings,
        "semantic_carrier": SEMANTIC_CARRIER,
        "transition_operator": TRANSLATE_OPERATOR,
        "runtime_identity_law": RUNTIME_IDENTITY_LAW,
        "authoritative_transition_owners": owners,
        "public_reachable_modules": sorted(reachable_modules),
        "public_reachable_paths": sorted(reachable_paths),
        "public_mutating_route_definitions": public_mutating_routes,
        "parallel_public_mutation_authorities": parallel_public_authorities,
        "retained_legacy_mutation_sites": legacy_sites,
        "all_project_files_classified": sum(manifest["role_counts"].values())
        == manifest["file_count"],
        "file_count": manifest["file_count"],
        "role_counts": manifest["role_counts"],
    }
    return {"id": content_id("supernet-project-closure-audit", core), **core}


def attach_deterministic_project_closure(app: Any) -> Any:
    """Attach the project law without adding a second semantic route."""

    if getattr(app.state, "deterministic_project_closure_attached", False):
        return app
    contract = runtime_project_closure_contract()
    app.state.deterministic_project_closure_attached = True
    app.state.supernet_project_closure = contract

    @app.middleware("http")
    async def deterministic_project_closure_headers(request: Any, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers.setdefault("x-supernet-project-closure", contract["id"])
        response.headers.setdefault("x-supernet-semantic-carrier", SEMANTIC_CARRIER)
        response.headers.setdefault("x-supernet-translate", TRANSLATE_OPERATOR)
        response.headers.setdefault("x-supernet-runtime-identity", RUNTIME_IDENTITY_LAW)
        return response

    return app


def _summary(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": report["id"],
        "valid": report["valid"],
        "manifest_id": report["manifest_id"],
        "runtime_contract_id": report["runtime_contract_id"],
        "semantic_carrier": report["semantic_carrier"],
        "transition_operator": report["transition_operator"],
        "runtime_identity_law": report["runtime_identity_law"],
        "authoritative_transition_owners": report["authoritative_transition_owners"],
        "parallel_public_mutation_authorities": report[
            "parallel_public_mutation_authorities"
        ],
        "file_count": report["file_count"],
        "role_counts": report["role_counts"],
        "errors": report["errors"],
        "warning_count": len(report["warnings"]),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify the deterministic full-project Supernet closure"
    )
    parser.add_argument("--root", default=None)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args(argv)
    report = audit_project_closure(args.root)
    print(canonical_json(report if args.full else _summary(report)))
    return 0 if report["valid"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "AUTHORITATIVE_TRANSITION_OWNER",
    "PROJECT_CLOSURE_PROTOCOL",
    "PROJECT_CLOSURE_SCHEMA",
    "PUBLIC_ENTRY_MODULE",
    "RUNTIME_IDENTITY_LAW",
    "SEMANTIC_CARRIER",
    "TRANSLATE_OPERATOR",
    "attach_deterministic_project_closure",
    "audit_project_closure",
    "build_project_closure_manifest",
    "canonical_json",
    "content_id",
    "find_project_root",
    "iter_project_files",
    "main",
    "manifest_path_set",
    "runtime_project_closure_contract",
]
