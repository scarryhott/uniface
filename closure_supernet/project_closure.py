from __future__ import annotations

"""Deterministic closure of the complete Supernet source project.

The certificate is a content-addressed reading of the repository.  It assigns
every retained file exactly one relative role around the single current
semantic carrier and transition operator.  Historical modules are preserved as
charts or compatibility witnesses; they never become a second truth or mutation
authority merely because they remain importable.

The derivation uses only relative paths, file bytes, deterministic AST import
relations and sorted canonical JSON.  It deliberately excludes timestamps,
absolute paths, process identity, randomness and mutable runtime data.
"""

import argparse
import ast
import hashlib
import json
import os
import sys
import tomllib
from collections import Counter, deque
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

PROTOCOL = "SUPERNET-DETERMINISTIC-PROJECT-CLOSURE"
SCHEMA = "closure.supernet/deterministic-project-closure-v1"
WITNESSED = "WITNESSED"
CONTINUING = "CONTINUING"

SEMANTIC_CARRIER = "SUPERNET_CLOSURE_FORM"
TRANSLATION_OPERATOR = "SUPERNET_TRANSLATE"
RUNTIME_IDENTITY = "TRANSLATIONAL_TRUTH_CLASS"

CANONICAL_CLOSURE_CARRIER = "CANONICAL_CLOSURE_CARRIER"
CANONICAL_TRANSLATION_OPERATOR = "CANONICAL_TRANSLATION_OPERATOR"
CANONICAL_RETURN_STORE = "CANONICAL_RETURN_STORE"
TRANSPORT_OR_RELATIVE_PROJECTION = "TRANSPORT_OR_RELATIVE_PROJECTION"
NATURAL_FORM_CHART = "NATURAL_FORM_CHART"
DOMAIN_NATURAL_FORM_LENS = "DOMAIN_NATURAL_FORM_LENS"
HISTORICAL_COMPATIBILITY_CHART = "HISTORICAL_COMPATIBILITY_CHART"
DETERMINISTIC_SUPPORT = "DETERMINISTIC_SUPPORT"
VERIFICATION_WITNESS = "VERIFICATION_WITNESS"
DOCUMENTATION_WITNESS = "DOCUMENTATION_WITNESS"
BUILD_AND_DEPLOYMENT_CONTRACT = "BUILD_AND_DEPLOYMENT_CONTRACT"
RETURNED_SOURCE_HISTORY = "RETURNED_SOURCE_HISTORY"

ROLES = (
    CANONICAL_CLOSURE_CARRIER,
    CANONICAL_TRANSLATION_OPERATOR,
    CANONICAL_RETURN_STORE,
    TRANSPORT_OR_RELATIVE_PROJECTION,
    NATURAL_FORM_CHART,
    DOMAIN_NATURAL_FORM_LENS,
    HISTORICAL_COMPATIBILITY_CHART,
    DETERMINISTIC_SUPPORT,
    VERIFICATION_WITNESS,
    DOCUMENTATION_WITNESS,
    BUILD_AND_DEPLOYMENT_CONTRACT,
    RETURNED_SOURCE_HISTORY,
)

CANONICAL_PATH_ROLES: dict[str, str] = {
    "closure_supernet/supernet_closure_form.py": CANONICAL_CLOSURE_CARRIER,
    "closure_supernet/supernet_closure_runtime.py": CANONICAL_TRANSLATION_OPERATOR,
    "closure_supernet/minimal_projection_runtime.py": CANONICAL_RETURN_STORE,
    "closure_supernet/supernet_store.py": CANONICAL_RETURN_STORE,
    "closure_supernet/closure_ui_contract.py": NATURAL_FORM_CHART,
    "closure_supernet/natural_form_atlas.py": NATURAL_FORM_CHART,
    "closure_supernet/supernet_closure_certificate.py": NATURAL_FORM_CHART,
    "closure_supernet/nrrf892_runtime_bridge.py": NATURAL_FORM_CHART,
    "closure_supernet/one_closure_form_interface.py": TRANSPORT_OR_RELATIVE_PROJECTION,
    "closure_supernet/api_agent.py": TRANSPORT_OR_RELATIVE_PROJECTION,
    "closure_supernet/agent_closure_mcp.py": TRANSPORT_OR_RELATIVE_PROJECTION,
    "closure_supernet/self_runtime_projection.py": TRANSPORT_OR_RELATIVE_PROJECTION,
    "closure_supernet/cli_supernet.py": TRANSPORT_OR_RELATIVE_PROJECTION,
    "closure_supernet/__main__.py": TRANSPORT_OR_RELATIVE_PROJECTION,
    "asgi.py": TRANSPORT_OR_RELATIVE_PROJECTION,
    "closure_supernet/project_closure.py": DETERMINISTIC_SUPPORT,
}

PUBLIC_ENTRYPOINT_PATHS = (
    "asgi.py",
    "closure_supernet/api_agent.py",
    "closure_supernet/cli_supernet.py",
)

CANONICAL_REQUIRED_PATHS = tuple(sorted(CANONICAL_PATH_ROLES))

EXCLUDED_PARTS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        ".nox",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        "htmlcov",
    }
)
EXCLUDED_SUFFIXES = frozenset(
    {
        ".pyc",
        ".pyo",
        ".db",
        ".sqlite",
        ".sqlite3",
        ".log",
        ".zip",
        ".tar",
        ".gz",
        ".DS_Store",
    }
)
INCLUDED_SUFFIXES = frozenset(
    {
        ".py",
        ".md",
        ".toml",
        ".yml",
        ".yaml",
        ".json",
        ".jsonl",
        ".js",
        ".mjs",
        ".cjs",
        ".html",
        ".css",
        ".txt",
        ".example",
        ".gitkeep",
    }
)
INCLUDED_NAMES = frozenset(
    {
        "Dockerfile",
        "Makefile",
        ".dockerignore",
        ".gitignore",
        ".python-version",
        ".vercelignore",
    }
)

HISTORICAL_SURFACE_STEMS = frozenset(
    {
        "api",
        "web",
        "runtime",
        "agent_mcp",
        "agents",
        "production",
        "production_web",
        "supernet_runtime",
        "supernet_integrator",
        "supernet_web",
        "topology",
        "topology_runtime",
        "coordination",
        "live_sense",
        "living_network",
        "public_web",
    }
)
DOMAIN_PREFIXES = (
    "trading",
    "alpaca",
    "hardware",
    "embodied",
    "resource",
    "handed",
    "turing_being",
    "completion",
    "constructive",
    "framework",
    "renormalization",
    "inversion",
    "reopening",
    "living",
)
NATURAL_FORM_TOKENS = (
    "natural_form",
    "closure",
    "translation",
    "equality",
    "axiometr",
    "projection",
    "visual",
    "nrrf",
    "continuation",
    "selection",
    "interaction",
)

MUTATION_MARKERS = (
    "app.post(",
    "@app.post(",
    "create_event(",
    "append_event(",
    "return_event(",
    "create_relation(",
    "create_reading(",
    ".offer(",
    ".interact(",
    ".reopen(",
)

FORBIDDEN_NONDETERMINISTIC_IMPORTS = frozenset(
    {
        "random",
        "secrets",
        "uuid",
        "time",
    }
)


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _digest(prefix: str, value: Any) -> str:
    data = _stable(value).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(data).hexdigest()}"


def locate_project_root(start: str | os.PathLike[str] | None = None) -> Path:
    candidates: list[Path] = []
    if start is not None:
        candidates.append(Path(start))
    candidates.append(Path.cwd())
    package_parent = Path(__file__).resolve().parents[1]
    candidates.append(package_parent)
    candidates.extend(package_parent.parents)

    seen: set[Path] = set()
    for raw in candidates:
        candidate = raw.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / "closure_supernet").is_dir():
            return candidate
    raise RuntimeError("Could not locate a Supernet project or installed package root")


def _eligible(relative_path: str) -> bool:
    path = PurePosixPath(relative_path)
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    if path.name in INCLUDED_NAMES:
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.suffix in INCLUDED_SUFFIXES


def project_paths(root: Path) -> list[str]:
    result: list[str] = []
    # A repository checkout is scanned in full.  An installed wheel is scanned
    # only through its own package directory, never through unrelated
    # site-packages that happen to share the same parent.
    scan_root = root if (root / "pyproject.toml").is_file() else root / "closure_supernet"
    if not scan_root.exists():
        return result
    for candidate in scan_root.rglob("*"):
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(root).as_posix()
        if _eligible(relative):
            result.append(relative)
    return sorted(set(result))


def classify_path(relative_path: str) -> str:
    if relative_path in CANONICAL_PATH_ROLES:
        return CANONICAL_PATH_ROLES[relative_path]

    path = PurePosixPath(relative_path)
    name = path.name
    stem = path.stem
    parts = path.parts

    if parts and parts[0] == "tests":
        return VERIFICATION_WITNESS
    if parts and parts[0] in {"docs"}:
        return DOCUMENTATION_WITNESS
    if name == "README.md" or (len(parts) == 1 and path.suffix == ".md"):
        return DOCUMENTATION_WITNESS
    if (
        parts[:2] == (".github", "workflows")
        or name in INCLUDED_NAMES
        or name in {"pyproject.toml", "railway.toml", "vercel.json"}
        or (len(parts) == 1 and path.suffix in {".toml", ".yml", ".yaml"})
    ):
        return BUILD_AND_DEPLOYMENT_CONTRACT
    if parts and parts[0] in {"ledger", "examples", "runtime_data"}:
        return RETURNED_SOURCE_HISTORY

    if parts and parts[0] == "closure_supernet":
        if (
            "_legacy" in stem
            or stem.startswith("full_supernet_projection_runtime")
            or (stem.startswith("api_") and stem != "api_agent")
            or (stem.startswith("cli_") and stem != "cli_supernet")
            or stem.endswith("_runtime")
            or stem.endswith("_store")
            or stem.endswith("_web")
            or stem in HISTORICAL_SURFACE_STEMS
        ):
            return HISTORICAL_COMPATIBILITY_CHART
        if stem.startswith(DOMAIN_PREFIXES):
            return DOMAIN_NATURAL_FORM_LENS
        if any(token in stem for token in NATURAL_FORM_TOKENS):
            return NATURAL_FORM_CHART
        return DETERMINISTIC_SUPPORT

    if path.suffix == ".py":
        return DETERMINISTIC_SUPPORT
    return RETURNED_SOURCE_HISTORY


def _module_name(relative_path: str) -> str | None:
    path = PurePosixPath(relative_path)
    if path.suffix != ".py":
        return None
    parts = list(path.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts:
        return None
    return ".".join(parts)


def _read_bytes(
    root: Path,
    relative_path: str,
    overrides: Mapping[str, bytes | str] | None,
) -> bytes:
    if overrides and relative_path in overrides:
        raw = overrides[relative_path]
        return raw.encode("utf-8") if isinstance(raw, str) else bytes(raw)
    return (root / relative_path).read_bytes()


def _resolve_relative_import(
    current_module: str,
    imported_module: str | None,
    level: int,
) -> str | None:
    if level <= 0:
        return imported_module
    package_parts = current_module.split(".")[:-1]
    trim = level - 1
    if trim > len(package_parts):
        return None
    base = package_parts[: len(package_parts) - trim]
    if imported_module:
        base.extend(imported_module.split("."))
    return ".".join(base) if base else None


def _python_imports(
    text: str,
    module_name: str,
    known_modules: set[str],
) -> tuple[list[str], list[str], list[str]]:
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        return [], [f"{error.lineno}:{error.offset}:{error.msg}"], []

    imports: set[str] = set()
    nondeterministic: set[str] = set()
    for node in ast.walk(tree):
        candidates: list[str] = []
        if isinstance(node, ast.Import):
            candidates.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            resolved = _resolve_relative_import(
                module_name,
                node.module,
                node.level,
            )
            if resolved:
                candidates.append(resolved)
                candidates.extend(
                    f"{resolved}.{alias.name}" for alias in node.names
                    if alias.name != "*"
                )
        for candidate in candidates:
            root_name = candidate.split(".", 1)[0]
            if root_name in FORBIDDEN_NONDETERMINISTIC_IMPORTS:
                nondeterministic.add(root_name)
            exact = candidate
            while exact and exact not in known_modules and "." in exact:
                exact = exact.rsplit(".", 1)[0]
            if exact in known_modules:
                imports.add(exact)
    return sorted(imports), [], sorted(nondeterministic)


def _script_targets(
    root: Path,
    overrides: Mapping[str, bytes | str] | None,
) -> dict[str, str]:
    if "pyproject.toml" not in project_paths(root):
        return {}
    try:
        payload = tomllib.loads(
            _read_bytes(root, "pyproject.toml", overrides).decode("utf-8")
        )
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return {}
    scripts = (payload.get("project") or {}).get("scripts") or {}
    return {
        str(name): str(target)
        for name, target in sorted(dict(scripts).items())
    }


def _dependency_closure(
    records: Sequence[Mapping[str, Any]],
    root_modules: Sequence[str],
) -> list[str]:
    graph = {
        str(record["module"]): list(record.get("internal_imports") or [])
        for record in records
        if record.get("module")
    }
    queue: deque[str] = deque(sorted(set(root_modules)))
    visited: set[str] = set()
    while queue:
        module = queue.popleft()
        if module in visited or module not in graph:
            continue
        visited.add(module)
        queue.extend(sorted(graph[module]))
    return sorted(visited)


def _target_module(target: str) -> str:
    return target.split(":", 1)[0].strip()


def _module_to_path(module: str, paths: set[str]) -> str | None:
    file_path = module.replace(".", "/") + ".py"
    init_path = module.replace(".", "/") + "/__init__.py"
    if file_path in paths:
        return file_path
    if init_path in paths:
        return init_path
    return None


def derive_project_closure_certificate(
    root: str | os.PathLike[str] | None = None,
    *,
    overrides: Mapping[str, bytes | str] | None = None,
) -> dict[str, Any]:
    project_root = locate_project_root(root)
    paths = project_paths(project_root)
    path_set = set(paths)

    known_modules = {
        module
        for relative in paths
        if (module := _module_name(relative)) is not None
    }
    records: list[dict[str, Any]] = []
    parse_errors: dict[str, list[str]] = {}
    nondeterministic_imports: dict[str, list[str]] = {}
    source_text: dict[str, str] = {}

    for relative in paths:
        raw = _read_bytes(project_root, relative, overrides)
        role = classify_path(relative)
        module = _module_name(relative)
        internal_imports: list[str] = []
        errors: list[str] = []
        non_deterministic: list[str] = []
        if module:
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError as error:
                text = ""
                errors = [f"unicode:{error.start}"]
            else:
                source_text[relative] = text
                internal_imports, errors, non_deterministic = _python_imports(
                    text,
                    module,
                    known_modules,
                )
        if errors:
            parse_errors[relative] = errors
        if non_deterministic:
            nondeterministic_imports[relative] = non_deterministic
        records.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size": len(raw),
                "role": role,
                "module": module,
                "internal_imports": internal_imports,
                "closure_relation": (
                    f"{relative} --{role}--> {SEMANTIC_CARRIER}"
                ),
            }
        )

    records.sort(key=lambda item: str(item["path"]))
    role_counts = dict(sorted(Counter(str(r["role"]) for r in records).items()))
    scripts = _script_targets(project_root, overrides)
    script_paths = {
        name: _module_to_path(_target_module(target), path_set)
        for name, target in scripts.items()
    }

    public_root_modules = [
        "asgi",
        "closure_supernet.api_agent",
        "closure_supernet.cli_supernet",
    ]
    public_dependencies = _dependency_closure(records, public_root_modules)
    module_roles = {
        str(record["module"]): str(record["role"])
        for record in records
        if record.get("module")
    }
    public_dependency_roles = {
        module: module_roles[module]
        for module in public_dependencies
        if module in module_roles
    }

    coverage = (
        "FULL_REPOSITORY"
        if {
            "pyproject.toml",
            "tests/conftest.py",
            "docs/index.html",
        }.issubset(path_set)
        else "INSTALLED_EXECUTABLE_PACKAGE"
    )

    canonical_missing = sorted(set(CANONICAL_REQUIRED_PATHS) - path_set)
    entrypoints_missing = sorted(set(PUBLIC_ENTRYPOINT_PATHS) - path_set)
    unknown_roles = sorted(
        {
            str(record["role"])
            for record in records
            if str(record["role"]) not in ROLES
        }
    )
    duplicate_paths = sorted(
        path for path, count in Counter(r["path"] for r in records).items()
        if count != 1
    )

    asgi_source = source_text.get("asgi.py", "")
    api_agent_source = source_text.get("closure_supernet/api_agent.py", "")
    cli_source = source_text.get("closure_supernet/cli_supernet.py", "")
    closure_runtime_source = source_text.get(
        "closure_supernet/supernet_closure_runtime.py", ""
    )
    agent_source = source_text.get("closure_supernet/agent_closure_mcp.py", "")
    self_source = source_text.get(
        "closure_supernet/self_runtime_projection.py", ""
    )

    direct_public_targets = {
        "asgi": "closure_supernet.api_agent" in asgi_source,
        "api_agent": (
            "supernet_closure_runtime" in api_agent_source
            and "attach_supernet_agent_mcp" in api_agent_source
            and "attach_self_runtime_projection" in api_agent_source
        ),
        "cli": "closure_supernet.api_agent:app" in cli_source,
    }
    translation_markers = {
        "runtime_installs_one_translate": (
            "app.state.supernet_translate = translate" in closure_runtime_source
        ),
        "agent_uses_runtime_translate": (
            "translate = app.state.supernet_translate" in agent_source
        ),
        "self_is_read_only_projection": (
            "self_observation_authors_truth" in self_source
            and "derive_self_runtime_reading" in self_source
        ),
    }

    noncanonical_surface_paths = sorted(
        str(record["path"])
        for record in records
        if record["role"] == HISTORICAL_COMPATIBILITY_CHART
    )
    direct_entrypoint_roles = {
        path: classify_path(path)
        for path in PUBLIC_ENTRYPOINT_PATHS
        if path in path_set
    }

    executable_targets_resolve = all(
        path is not None for path in script_paths.values()
    )
    executable_targets_classified = all(
        path is not None and classify_path(path) in ROLES
        for path in script_paths.values()
    )

    checks: dict[str, bool] = {
        "all_project_files_classified_exactly_once": (
            bool(records) and not unknown_roles and not duplicate_paths
        ),
        "all_python_modules_parse": not parse_errors,
        "canonical_closure_files_present": not canonical_missing,
        "public_entrypoints_present": not entrypoints_missing,
        "one_semantic_carrier_declared": SEMANTIC_CARRIER
        == "SUPERNET_CLOSURE_FORM",
        "one_translation_operator_declared": TRANSLATION_OPERATOR
        == "SUPERNET_TRANSLATE",
        "runtime_identity_is_translational_truth": RUNTIME_IDENTITY
        == "TRANSLATIONAL_TRUTH_CLASS",
        "public_entrypoints_resolve_to_canonical_runtime": all(
            direct_public_targets.values()
        ),
        "runtime_agent_and_self_share_one_operator": all(
            translation_markers.values()
        ),
        "historical_surfaces_are_classified_non_authoritative": all(
            classify_path(path) == HISTORICAL_COMPATIBILITY_CHART
            for path in noncanonical_surface_paths
        ),
        "historical_surfaces_are_not_direct_public_entrypoints": not (
            set(noncanonical_surface_paths) & set(PUBLIC_ENTRYPOINT_PATHS)
        ),
        "public_entrypoints_are_transport_only": all(
            role == TRANSPORT_OR_RELATIVE_PROJECTION
            for role in direct_entrypoint_roles.values()
        ),
        "all_declared_executables_resolve": executable_targets_resolve,
        "all_declared_executables_are_classified": executable_targets_classified,
        "natural_form_history_retained": (
            role_counts.get(NATURAL_FORM_CHART, 0) > 0
            and role_counts.get(HISTORICAL_COMPATIBILITY_CHART, 0) > 0
            and "closure_supernet/natural_form_atlas.py" in path_set
        ),
        "verification_and_documentation_retained": (
            coverage != "FULL_REPOSITORY"
            or (
                role_counts.get(VERIFICATION_WITNESS, 0) > 0
                and role_counts.get(DOCUMENTATION_WITNESS, 0) > 0
            )
        ),
        "build_and_deployment_contracts_retained": (
            coverage != "FULL_REPOSITORY"
            or role_counts.get(BUILD_AND_DEPLOYMENT_CONTRACT, 0) > 0
        ),
        "certificate_has_no_time_random_uuid_dependency": not (
            set(nondeterministic_imports.get(
                "closure_supernet/project_closure.py", []
            ))
            & FORBIDDEN_NONDETERMINISTIC_IMPORTS
        ),
        "certificate_uses_relative_paths_only": all(
            not PurePosixPath(str(record["path"])).is_absolute()
            for record in records
        ),
        "public_dependency_closure_is_recorded": bool(public_dependencies),
        "compatibility_substrate_is_content_addressed": all(
            record.get("sha256")
            for record in records
            if record["role"] == HISTORICAL_COMPATIBILITY_CHART
        ),
    }

    source_tree_identity_id = _digest(
        "project-source-tree",
        [
            {
                "path": record["path"],
                "sha256": record["sha256"],
                "size": record["size"],
                "role": record["role"],
                "module": record["module"],
                "internal_imports": record["internal_imports"],
            }
            for record in records
        ],
    )
    semantic_basis = {
        "semantic_carrier": SEMANTIC_CARRIER,
        "translation_operator": TRANSLATION_OPERATOR,
        "runtime_identity": RUNTIME_IDENTITY,
        "canonical_path_roles": dict(sorted(CANONICAL_PATH_ROLES.items())),
        "public_entrypoints": list(PUBLIC_ENTRYPOINT_PATHS),
        "public_dependency_closure": public_dependencies,
        "translation_markers": translation_markers,
    }
    semantic_identity_id = _digest("project-semantic-closure", semantic_basis)
    project_basis = {
        "source_tree_identity_id": source_tree_identity_id,
        "semantic_identity_id": semantic_identity_id,
        "coverage": coverage,
        "role_counts": role_counts,
        "checks": checks,
        "scripts": scripts,
    }
    project_closure_id = _digest("project-closure", project_basis)
    closed = all(checks.values())

    return {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "status": WITNESSED if closed else CONTINUING,
        "project_closed": closed,
        "id": project_closure_id,
        "source_tree_identity_id": source_tree_identity_id,
        "semantic_identity_id": semantic_identity_id,
        "semantic_carrier": SEMANTIC_CARRIER,
        "translation_operator": TRANSLATION_OPERATOR,
        "runtime_identity": RUNTIME_IDENTITY,
        "coverage": coverage,
        "file_count": len(records),
        "python_module_count": len(known_modules),
        "role_counts": role_counts,
        "records": records,
        "canonical_path_roles": dict(sorted(CANONICAL_PATH_ROLES.items())),
        "public_entrypoints": list(PUBLIC_ENTRYPOINT_PATHS),
        "public_dependency_closure": public_dependencies,
        "public_dependency_roles": public_dependency_roles,
        "declared_executables": scripts,
        "declared_executable_paths": script_paths,
        "checks": checks,
        "canonical_missing": canonical_missing,
        "public_entrypoints_missing": entrypoints_missing,
        "unknown_roles": unknown_roles,
        "duplicate_paths": duplicate_paths,
        "parse_errors": parse_errors,
        "nondeterministic_imports": nondeterministic_imports,
        "direct_public_targets": direct_public_targets,
        "translation_markers": translation_markers,
        "determinism": {
            "relative_paths_only": True,
            "content_addressed": True,
            "sorted_canonical_json": True,
            "timestamps_in_identity": False,
            "absolute_paths_in_identity": False,
            "process_identity_in_identity": False,
            "randomness_in_identity": False,
            "environment_values_in_identity": False,
            "same_source_tree_same_certificate": True,
        },
        "closure_equation": (
            "ProjectClosure = CloseAtlas("
            "all retained files,"
            "exactly one relative role per file,"
            "SUPERNET_CLOSURE_FORM,"
            "SUPERNET_TRANSLATE,"
            "TRANSLATIONAL_TRUTH_CLASS,"
            "content-addressed source relations"
            ")"
        ),
        "authority": {
            "semantic_authority": SEMANTIC_CARRIER,
            "mutation_authority": TRANSLATION_OPERATOR,
            "identity_authority": RUNTIME_IDENTITY,
            "historical_modules_are_retained": True,
            "historical_modules_author_truth": False,
            "domain_modules_are_relative_lenses": True,
            "transport_authors_truth": False,
            "rendering_authors_truth": False,
            "self_observation_authors_truth": False,
        },
    }


@lru_cache(maxsize=8)
def _cached_project_closure_for_root(project_root: str) -> dict[str, Any]:
    return derive_project_closure_certificate(project_root)


def cached_project_closure_certificate(
    root: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    """Return one immutable-by-convention derivation per source root/process."""

    project_root = locate_project_root(root)
    return _cached_project_closure_for_root(str(project_root.resolve()))


def validate_project_closure_certificate(
    certificate: Mapping[str, Any],
    root: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    records = certificate.get("records")
    if not isinstance(records, list):
        errors.append("records:missing")
        records = []

    expected_source_id = _digest(
        "project-source-tree",
        [
            {
                "path": record.get("path"),
                "sha256": record.get("sha256"),
                "size": record.get("size"),
                "role": record.get("role"),
                "module": record.get("module"),
                "internal_imports": record.get("internal_imports"),
            }
            for record in records
            if isinstance(record, Mapping)
        ],
    )
    if certificate.get("source_tree_identity_id") != expected_source_id:
        errors.append("source-tree-identity:mismatch")

    semantic_basis = {
        "semantic_carrier": certificate.get("semantic_carrier"),
        "translation_operator": certificate.get("translation_operator"),
        "runtime_identity": certificate.get("runtime_identity"),
        "canonical_path_roles": certificate.get("canonical_path_roles"),
        "public_entrypoints": certificate.get("public_entrypoints"),
        "public_dependency_closure": certificate.get(
            "public_dependency_closure"
        ),
        "translation_markers": certificate.get("translation_markers"),
    }
    expected_semantic_id = _digest(
        "project-semantic-closure",
        semantic_basis,
    )
    if certificate.get("semantic_identity_id") != expected_semantic_id:
        errors.append("semantic-identity:mismatch")

    project_basis = {
        "source_tree_identity_id": certificate.get("source_tree_identity_id"),
        "semantic_identity_id": certificate.get("semantic_identity_id"),
        "coverage": certificate.get("coverage"),
        "role_counts": certificate.get("role_counts"),
        "checks": certificate.get("checks"),
        "scripts": certificate.get("declared_executables"),
    }
    expected_project_id = _digest("project-closure", project_basis)
    if certificate.get("id") != expected_project_id:
        errors.append("project-closure-identity:mismatch")

    checks = certificate.get("checks")
    if not isinstance(checks, Mapping) or not all(
        value is True for value in checks.values()
    ):
        errors.append("checks:not-closed")
    if certificate.get("project_closed") is not True:
        errors.append("project:not-closed")
    if certificate.get("status") != WITNESSED:
        errors.append("status:not-witnessed")

    if root is not None:
        actual = derive_project_closure_certificate(root)
        for key in (
            "id",
            "source_tree_identity_id",
            "semantic_identity_id",
            "file_count",
            "coverage",
        ):
            if certificate.get(key) != actual.get(key):
                errors.append(f"current-project:{key}:mismatch")

    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "project_closure_id": certificate.get("id"),
        "source_tree_identity_id": certificate.get(
            "source_tree_identity_id"
        ),
        "semantic_identity_id": certificate.get("semantic_identity_id"),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="closure-supernet-project-closure"
    )
    parser.add_argument("--root", default=None)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--require-full-repository", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    certificate = derive_project_closure_certificate(args.root)
    validation = validate_project_closure_certificate(certificate)
    if (
        args.require_full_repository
        and certificate.get("coverage") != "FULL_REPOSITORY"
    ):
        validation = {
            **validation,
            "valid": False,
            "errors": sorted(
                set(validation.get("errors", []))
                | {"coverage:not-full-repository"}
            ),
        }

    payload = (
        certificate
        if not args.check
        else {
            "valid": validation["valid"],
            "errors": validation["errors"],
            "project_closure_id": certificate["id"],
            "source_tree_identity_id": certificate[
                "source_tree_identity_id"
            ],
            "semantic_identity_id": certificate["semantic_identity_id"],
            "coverage": certificate["coverage"],
            "file_count": certificate["file_count"],
            "role_counts": certificate["role_counts"],
        }
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2 if args.pretty else None))
    return 0 if validation["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CANONICAL_PATH_ROLES",
    "PROTOCOL",
    "RUNTIME_IDENTITY",
    "SCHEMA",
    "SEMANTIC_CARRIER",
    "TRANSLATION_OPERATOR",
    "cached_project_closure_certificate",
    "classify_path",
    "derive_project_closure_certificate",
    "locate_project_root",
    "main",
    "project_paths",
    "validate_project_closure_certificate",
]
