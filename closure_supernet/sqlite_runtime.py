from __future__ import annotations

import os
import re
import sqlite3
from typing import Any


_ORIGINAL_CONNECT = sqlite3.connect
_INSTALLED = False
_ALLOWED_JOURNAL_MODES = {"DELETE", "TRUNCATE", "PERSIST", "MEMORY", "WAL", "OFF"}
_ALLOWED_SYNCHRONOUS_MODES = {"OFF", "NORMAL", "FULL", "EXTRA"}
_JOURNAL_ASSIGNMENT = re.compile(r"^PRAGMA\s+JOURNAL_MODE\s*=\s*([A-Z]+)\s*;?$", re.I)


def configured_journal_mode() -> str:
    """Return the journal mode used by every Closure Supernet connection.

    Production defaults to the rollback journal because the database lives on a
    mounted Railway volume. This keeps every committed transaction in the main
    database file rather than relying on WAL sidecars surviving a container
    handoff. Development and tests retain WAL unless explicitly overridden.
    """

    configured = os.getenv("CLOSURE_SQLITE_JOURNAL_MODE")
    if configured:
        mode = configured.strip().upper()
    else:
        environment = os.getenv("CLOSURE_ENVIRONMENT", "development").strip().lower()
        mode = "DELETE" if environment == "production" else "WAL"
    if mode not in _ALLOWED_JOURNAL_MODES:
        raise ValueError(
            "CLOSURE_SQLITE_JOURNAL_MODE must be one of "
            + ", ".join(sorted(_ALLOWED_JOURNAL_MODES))
        )
    return mode


def configured_synchronous_mode() -> str:
    configured = os.getenv("CLOSURE_SQLITE_SYNCHRONOUS")
    if configured:
        mode = configured.strip().upper()
    else:
        environment = os.getenv("CLOSURE_ENVIRONMENT", "development").strip().lower()
        mode = "FULL" if environment == "production" else "NORMAL"
    if mode not in _ALLOWED_SYNCHRONOUS_MODES:
        raise ValueError(
            "CLOSURE_SQLITE_SYNCHRONOUS must be one of "
            + ", ".join(sorted(_ALLOWED_SYNCHRONOUS_MODES))
        )
    return mode


def configured_busy_timeout_ms() -> int:
    value = int(os.getenv("CLOSURE_SQLITE_BUSY_TIMEOUT_MS", "10000"))
    if value < 1:
        raise ValueError("CLOSURE_SQLITE_BUSY_TIMEOUT_MS must be positive")
    return value


def _rewrite_pragma(sql: str) -> str:
    match = _JOURNAL_ASSIGNMENT.match(sql.strip())
    if match and match.group(1).upper() == "WAL":
        return f"PRAGMA journal_mode={configured_journal_mode()}"
    return sql


class ClosureSQLiteConnection(sqlite3.Connection):
    """Connection that enforces one storage contract across every store lens."""

    def execute(self, sql: str, parameters: Any = (), /):  # type: ignore[override]
        return super().execute(_rewrite_pragma(sql), parameters)

    def executemany(self, sql: str, seq_of_parameters: Any, /):  # type: ignore[override]
        return super().executemany(_rewrite_pragma(sql), seq_of_parameters)

    def commit(self) -> None:  # type: ignore[override]
        super().commit()
        if configured_journal_mode() == "WAL":
            try:
                super().execute("PRAGMA wal_checkpoint(PASSIVE)")
            except sqlite3.Error:
                # Another connection can legitimately hold a read transaction.
                # The committed WAL remains valid and will be checkpointed later.
                pass

    def close(self) -> None:  # type: ignore[override]
        if configured_journal_mode() == "WAL":
            try:
                super().execute("PRAGMA wal_checkpoint(TRUNCATE)")
            except sqlite3.Error:
                pass
        super().close()


def configure_connection(connection: sqlite3.Connection) -> sqlite3.Connection:
    connection.execute(f"PRAGMA busy_timeout={configured_busy_timeout_ms()}")
    actual = connection.execute(
        f"PRAGMA journal_mode={configured_journal_mode()}"
    ).fetchone()
    actual_mode = "" if actual is None else str(actual[0]).upper()
    expected = configured_journal_mode()
    if actual_mode != expected:
        raise RuntimeError(
            f"SQLite journal mode mismatch: expected {expected}, got {actual_mode or 'unknown'}"
        )
    connection.execute(f"PRAGMA synchronous={configured_synchronous_mode()}")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def _connect(*args: Any, **kwargs: Any) -> sqlite3.Connection:
    kwargs.setdefault("factory", ClosureSQLiteConnection)
    connection = _ORIGINAL_CONNECT(*args, **kwargs)
    return configure_connection(connection)


def install_sqlite_runtime() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    sqlite3.connect = _connect  # type: ignore[assignment]


def storage_contract() -> dict[str, Any]:
    return {
        "journal_mode": configured_journal_mode(),
        "synchronous": configured_synchronous_mode(),
        "busy_timeout_ms": configured_busy_timeout_ms(),
        "production_main_file_commits": configured_journal_mode() != "WAL",
    }


install_sqlite_runtime()
