from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utcstamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def create_backup(database_path: Path, backup_dir: Path, *, label: str = "manual") -> dict[str, Any]:
    database_path = Path(database_path)
    backup_dir = Path(backup_dir)
    if not database_path.exists():
        raise FileNotFoundError(f"Database not found: {database_path}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    safe_label = "".join(ch for ch in label if ch.isalnum() or ch in {"-", "_"}) or "backup"
    destination = backup_dir / f"closure-supernet-{utcstamp()}-{safe_label}.db"
    with sqlite3.connect(database_path) as source, sqlite3.connect(destination) as target:
        source.backup(target)
        target.execute("PRAGMA quick_check")
    manifest = {
        "database": str(database_path),
        "backup": str(destination),
        "bytes": destination.stat().st_size,
        "created_at": datetime.now(UTC).isoformat(),
        "label": safe_label,
    }
    destination.with_suffix(".json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return manifest


def list_backups(backup_dir: Path, *, limit: int = 100) -> list[dict[str, Any]]:
    backup_dir = Path(backup_dir)
    if not backup_dir.exists():
        return []
    result: list[dict[str, Any]] = []
    for path in sorted(backup_dir.glob("closure-supernet-*.db"), reverse=True)[:limit]:
        manifest_path = path.with_suffix(".json")
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                manifest = {}
        else:
            manifest = {}
        result.append(
            {
                "backup": str(path),
                "bytes": path.stat().st_size,
                "created_at": manifest.get("created_at"),
                "label": manifest.get("label"),
            }
        )
    return result


def prune_backups(backup_dir: Path, *, keep: int) -> int:
    backup_dir = Path(backup_dir)
    files = sorted(backup_dir.glob("closure-supernet-*.db"), reverse=True)
    removed = 0
    for path in files[max(0, keep):]:
        path.unlink(missing_ok=True)
        path.with_suffix(".json").unlink(missing_ok=True)
        removed += 1
    return removed
