from __future__ import annotations

"""Project-wide determinism and semantic-authority audit for Supernet.

The full repository is retained as the versioned natural-form atlas, while one
import closure rooted at ``closure_supernet.api_agent`` is the executable
semantic authority.  Historical modules remain available as compatibility
charts, but cannot create another runtime identity or mutation operator.

The audit is deterministic: it reads Git-tracked bytes in lexical order,
constructs a project Merkle-style closure, derives the authoritative import
closure, and checks that browser, agent and self-runtime all factor through the
single ``SUPERNET_TRANSLATE`` kernel.
"""

import argparse
import ast
import hashlib
import importlib.util
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .deterministic_translation_kernel import (
    DETERMINISTIC_TRANSLATION_PROTOCOL,
    canonical_json,
    content_id,
)
from .supernet_closure_form import TRANSLATE_OPERATOR

PROJECT_CLOSURE_PROTOCOL = "closure.supernet/deterministic-full-project-v1"
SEMANTIC_ENTRYPOINT = "closure_supernet.api_agent"

SEALED_COMPATIBILITY_MODULES = {
    "closure_supernet.agent_mcp",
    "closure_supernet.api_inversion",
    "closure_supernet.api_natural_interface",
    "closure_supernet.complete_interface_models",
    "closure_supernet.coordination",
    "closure_supernet.runtime",
}

LEGACY_AGENT_MUTATION_MARKERS = (
    ".live_sense.offer(",
    ".live_sense.interact(",
    ".topology.create_relation(",
    ".selection.create_reading(",
    ".topology.return_event(",
    ".topology.reopen(",
    ".topology.create_collective_trace(",
)

FORBIDDEN_KERNEL_ENTROPY_CALLS = {
    "datetime.now",
    "datetime.utcnow",
    "os.urandom",
    "random.random",
    "random.randrange",
    "random.randint",
    "secrets.token_bytes",
    "secrets.token_hex",
    "time.time",
    "time.time_ns",
    "uuid.uuid1",
    "uuid.uuid4",
}

EXCLUDED_PARTS = {
    ".git",
    ".lake",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}


@dataclass(frozen=True)
class ProjectFile:
    path: str
    sha256: str
    size: int
    role: str


def _git_files(root: Path) -> list[Path]:
    try:
        raw = subprocess.check_output(
            ["git", "-C", str(root), "ls-files", "-z"],
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return sorted(
            path
            for path in root.rglob("*")
            if path.is_file()
            and not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
        )
    result: list[Path] = []
    for item in raw.decode("utf-8").split("\0"):
        if not item:
            continue
        path = root / item
        if path.is_file() and not any(
            part in EXCLUDED_PARTS for part in Path(item).parts
        ):
            result.append(path)
    return sorted(result)


def _python_modules(root: Path) -> dict[str, Path]:
    package = root / "closure_supernet"
    result: dict[str, Path] = {}
    if not package.exists():
        return result
    for path in sorted(package.rglob("*.py")):
        relative = path.relative_to(root).with_suffix("")
        parts = list(relative.parts)
        if parts[-1] == "__init__":
            parts.pop()
        result[".".join(parts)] = path
    return result


def _resolve_imports(module: str, path: Path, known: set[str]) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return set()
    package = module.rpartition(".")[0]
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name in known:
                    found.add(name)
                else:
                    # Importing a child through its package still makes the
                    # nearest known module part of the closure.
                    candidates = [item for item in known if name.startswith(item + ".")]
                    found.update(candidates)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                relative = "." * node.level + (node.module or "")
                try:
                    base = importlib.util.resolve_name(relative, package)
                except (ImportError, ValueError):
                    continue
            else:
                base = node.module or ""
            if base in known:
                found.add(base)
            for alias in node.names:
                candidate = f"{base}.{alias.name}" if base else alias.name
                if candidate in known:
                    found.add(candidate)
    return found


def authoritative_import_closure(root: Path) -> list[str]:
    modules = _python_modules(root)
    if SEMANTIC_ENTRYPOINT not in modules:
        return []
    closed: set[str] = set()
    frontier = [SEMANTIC_ENTRYPOINT]
    while frontier:
        module = frontier.pop()
        if module in closed:
            continue
        closed.add(module)
        for dependency in sorted(
            _resolve_imports(module, modules[module], set(modules))
        ):
            if dependency not in closed:
                frontier.append(dependency)
    return sorted(closed)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _entropy_calls(path: Path) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    rows: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name in FORBIDDEN_KERNEL_ENTROPY_CALLS:
            rows.append({"call": name, "line": getattr(node, "lineno", None)})
    return rows


def _mutating_routes(path: Path) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    rows: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            method = _call_name(decorator.func).rsplit(".", 1)[-1]
            if method not in {"post", "put", "patch", "delete"}:
                continue
            path_value: str | None = None
            if decorator.args:
                argument = decorator.args[0]
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                    path_value = argument.value
                elif isinstance(argument, ast.Name):
                    path_value = argument.id
            rows.append(
                {
                    "method": method.upper(),
                    "path": path_value,
                    "function": node.name,
                    "line": node.lineno,
                }
            )
    return rows


def _role(relative: Path, authoritative_paths: set[str]) -> str:
    value = relative.as_posix()
    module = ""
    if relative.suffix == ".py" and relative.parts[:1] == ("closure_supernet",):
        parts = list(relative.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        module = ".".join(parts)
    if module and module in authoritative_paths:
        return "AUTHORITATIVE_CLOSURE_RUNTIME"
    if module:
        return "SEALED_COMPATIBILITY_CHART"
    if relative.parts[:1] == ("tests",):
        return "CLOSURE_WITNESS_TEST"
    if relative.suffix == ".lean":
        return "FORMAL_NATURAL_FORM"
    if relative.suffix.lower() in {".md", ".txt"}:
        return "HISTORICAL_OR_EXPLANATORY_ATLAS"
    return "BUILD_OR_SOURCE_SUPPORT"


def project_files(root: Path, authoritative: Iterable[str]) -> list[ProjectFile]:
    authoritative_set = set(authoritative)
    rows: list[ProjectFile] = []
    for path in _git_files(root):
        relative = path.relative_to(root)
        data = path.read_bytes()
        rows.append(
            ProjectFile(
                path=relative.as_posix(),
                sha256=hashlib.sha256(data).hexdigest(),
                size=len(data),
                role=_role(relative, authoritative_set),
            )
        )
    return rows


def audit_project(root: Path | str) -> dict[str, Any]:
    root = Path(root).resolve()
    authoritative = authoritative_import_closure(root)
    modules = _python_modules(root)
    authoritative_files = [modules[name] for name in authoritative if name in modules]
    errors: list[str] = []

    if not authoritative:
        errors.append("semantic-entrypoint-not-found")
    sealed_imports = sorted(set(authoritative) & SEALED_COMPATIBILITY_MODULES)
    if sealed_imports:
        errors.append("sealed-compatibility-imported-by-runtime")

    api_agent = root / "closure_supernet" / "api_agent.py"
    api_text = api_agent.read_text(encoding="utf-8") if api_agent.exists() else ""
    attachment_order = [
        api_text.find("attach_deterministic_translation_kernel"),
        api_text.find("attach_supernet_agent_mcp"),
        api_text.find("attach_self_runtime_projection"),
    ]
    deterministic_attached = (
        all(index >= 0 for index in attachment_order)
        and attachment_order == sorted(attachment_order)
    )
    if not deterministic_attached:
        errors.append("deterministic-kernel-not-first-runtime-attachment")

    agent_path = root / "closure_supernet" / "agent_closure_mcp.py"
    agent_text = agent_path.read_text(encoding="utf-8") if agent_path.exists() else ""
    legacy_agent_markers = sorted(
        marker for marker in LEGACY_AGENT_MUTATION_MARKERS if marker in agent_text
    )
    agent_uses_one_translate = (
        "app.state.supernet_translate" in agent_text
        and not legacy_agent_markers
    )
    if not agent_uses_one_translate:
        errors.append("agent-has-separate-mutation-authority")

    self_path = root / "closure_supernet" / "self_runtime_projection.py"
    self_text = self_path.read_text(encoding="utf-8") if self_path.exists() else ""
    self_is_read_only = (
        '@app.get("/supernet/agent/self")' in self_text
        and "app.state.supernet_translate(" not in self_text
        and "self_observation_authors_truth\": False" in self_text
    )
    if not self_is_read_only:
        errors.append("self-runtime-is-not-read-only-projection")

    routes: list[dict[str, Any]] = []
    for path in authoritative_files:
        relative = path.relative_to(root).as_posix()
        for row in _mutating_routes(path):
            routes.append({"file": relative, **row})
    allowed_paths = {
        "TRANSLATION_ENDPOINT",
        "/supernet/interface/projections/{contract_id}/return",
    }
    unexpected_routes = [row for row in routes if row["path"] not in allowed_paths]
    translate_routes = [row for row in routes if row["path"] in allowed_paths]
    if unexpected_routes:
        errors.append("additional-authoritative-http-mutation-route")
    if len(translate_routes) != 1:
        errors.append("authoritative-translate-route-count-not-one")

    kernel_path = root / "closure_supernet" / "deterministic_translation_kernel.py"
    entropy = _entropy_calls(kernel_path) if kernel_path.exists() else []
    if entropy:
        errors.append("deterministic-kernel-uses-entropy-or-wall-clock")

    files = project_files(root, authoritative)
    if not files:
        errors.append("project-has-no-accounted-files")
    project_rows = [
        {
            "path": row.path,
            "sha256": row.sha256,
            "size": row.size,
            "role": row.role,
        }
        for row in files
    ]
    role_counts: dict[str, int] = {}
    for row in files:
        role_counts[row.role] = role_counts.get(row.role, 0) + 1

    project_closure_id = content_id(
        "supernet-project-closure",
        {
            "protocol": PROJECT_CLOSURE_PROTOCOL,
            "semantic_entrypoint": SEMANTIC_ENTRYPOINT,
            "translation_protocol": DETERMINISTIC_TRANSLATION_PROTOCOL,
            "translation_operator": TRANSLATE_OPERATOR,
            "files": project_rows,
        },
    )
    authority_closure_id = content_id(
        "supernet-authority-closure",
        {
            "protocol": PROJECT_CLOSURE_PROTOCOL,
            "semantic_entrypoint": SEMANTIC_ENTRYPOINT,
            "authoritative_modules": authoritative,
            "mutating_routes": routes,
        },
    )

    return {
        "protocol": PROJECT_CLOSURE_PROTOCOL,
        "valid": not errors,
        "errors": errors,
        "project_closure_id": project_closure_id,
        "authority_closure_id": authority_closure_id,
        "semantic_entrypoint": SEMANTIC_ENTRYPOINT,
        "translation_operator": TRANSLATE_OPERATOR,
        "translation_protocol": DETERMINISTIC_TRANSLATION_PROTOCOL,
        "runtime_identity": "TRANSLATIONAL_TRUTH_CLASS",
        "semantic_time": "RETURNED_EVENT_ORDER",
        "wall_clock_authors_identity": False,
        "all_project_files_accounted_for": bool(files),
        "project_file_count": len(files),
        "role_counts": dict(sorted(role_counts.items())),
        "authoritative_modules": authoritative,
        "sealed_compatibility_modules_imported": sealed_imports,
        "one_authoritative_mutation_route": len(translate_routes) == 1
        and not unexpected_routes,
        "authoritative_mutation_routes": routes,
        "unexpected_authoritative_mutation_routes": unexpected_routes,
        "deterministic_kernel_attached_before_transports": deterministic_attached,
        "agent_uses_same_translation": agent_uses_one_translate,
        "legacy_agent_mutation_markers": legacy_agent_markers,
        "self_runtime_is_read_only_projection": self_is_read_only,
        "kernel_entropy_calls": entropy,
        "compatibility_charts_author_truth": False,
        "truth_issued": False,
    }


def assert_project_closed(report: dict[str, Any]) -> None:
    if report.get("valid"):
        return
    raise RuntimeError(
        "Deterministic Supernet project closure failed: "
        + ", ".join(report.get("errors") or ["unknown"])
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    report = audit_project(args.root)
    print(canonical_json(report))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROJECT_CLOSURE_PROTOCOL",
    "SEMANTIC_ENTRYPOINT",
    "assert_project_closed",
    "audit_project",
    "authoritative_import_closure",
    "main",
    "project_files",
]
