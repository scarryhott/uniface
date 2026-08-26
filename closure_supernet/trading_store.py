from __future__ import annotations

import json
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _loads(value: str | None, default: Any) -> Any:
    return default if value is None else json.loads(value)


class TradingStore:
    """Append-only materialized trading lens over the canonical Supernet log."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _init_schema(self) -> None:
        schema = """
        CREATE TABLE IF NOT EXISTS trading_transactions (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            signed_size TEXT NOT NULL,
            bid TEXT NOT NULL,
            ask TEXT NOT NULL,
            fill TEXT NOT NULL,
            mark TEXT NOT NULL,
            fee TEXT NOT NULL,
            execution_mode TEXT NOT NULL,
            currency TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            perspective_id TEXT,
            problem_id TEXT,
            evaluation TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_trading_transactions_symbol
          ON trading_transactions(symbol, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_trading_transactions_event
          ON trading_transactions(integration_event_id);

        CREATE TABLE IF NOT EXISTS trading_system_evaluations (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            transaction_ids TEXT NOT NULL,
            total_cost TEXT NOT NULL,
            total_net TEXT NOT NULL,
            identity_residual TEXT NOT NULL,
            sys_net_eq_neg_sys_cost INTEGER NOT NULL,
            all_costs_nonnegative INTEGER NOT NULL,
            any_cost_positive INTEGER NOT NULL,
            nonpositive_when_charged INTEGER NOT NULL,
            strictly_negative_once_charged INTEGER NOT NULL,
            flow_cost_ratio TEXT,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS trading_shift_evaluations (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            transaction_id TEXT NOT NULL REFERENCES trading_transactions(id),
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS trading_numeraire_evaluations (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            transaction_id TEXT NOT NULL REFERENCES trading_transactions(id),
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS trading_circuit_evaluations (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            payload TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS trading_pnl_evaluations (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            payload TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS trading_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_transaction(self, row: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._conn.execute(
                """INSERT INTO trading_transactions
                (id,occurrence_id,integration_event_id,symbol,signed_size,bid,ask,fill,mark,fee,
                 execution_mode,currency,authored_by,perspective_id,problem_id,evaluation,metadata,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["id"], row["occurrence_id"], row["integration_event_id"], row["symbol"],
                    row["signed_size"], row["bid"], row["ask"], row["fill"], row["mark"], row["fee"],
                    row["execution_mode"], row["currency"], row["authored_by"], row.get("perspective_id"),
                    row.get("problem_id"), _json(row["evaluation"]), _json(row.get("metadata", {})),
                    row.get("created_at", utcnow()),
                ),
            )
            self._conn.commit()
        return self.get_transaction(row["id"])

    def get_transaction(self, transaction_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM trading_transactions WHERE id=?", (transaction_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Trading transaction {transaction_id} not found")
        return self._decode_transaction(row)

    def list_transactions(self, limit: int = 10_000, symbol: str | None = None) -> list[dict[str, Any]]:
        if symbol is None:
            rows = self._conn.execute(
                "SELECT * FROM trading_transactions ORDER BY created_at DESC,id DESC LIMIT ?", (limit,)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM trading_transactions WHERE symbol=? ORDER BY created_at DESC,id DESC LIMIT ?",
                (symbol, limit),
            ).fetchall()
        return [self._decode_transaction(row) for row in rows]

    @staticmethod
    def _decode_transaction(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["evaluation"] = _loads(item["evaluation"], {})
        item["metadata"] = _loads(item["metadata"], {})
        return item

    def create_system(self, row: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._conn.execute(
                """INSERT INTO trading_system_evaluations
                (id,occurrence_id,integration_event_id,transaction_ids,total_cost,total_net,
                 identity_residual,sys_net_eq_neg_sys_cost,all_costs_nonnegative,any_cost_positive,
                 nonpositive_when_charged,strictly_negative_once_charged,flow_cost_ratio,metadata,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["id"], row["occurrence_id"], row["integration_event_id"],
                    _json(row["transaction_ids"]), row["total_cost"], row["total_net"],
                    row["identity_residual"], int(row["sys_net_eq_neg_sys_cost"]),
                    int(row["all_costs_nonnegative"]), int(row["any_cost_positive"]),
                    int(row["nonpositive_when_charged"]), int(row["strictly_negative_once_charged"]),
                    row.get("flow_cost_ratio"), _json(row.get("metadata", {})),
                    row.get("created_at", utcnow()),
                ),
            )
            self._conn.commit()
        return self.get_system(row["id"])

    def get_system(self, evaluation_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM trading_system_evaluations WHERE id=?", (evaluation_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Trading system evaluation {evaluation_id} not found")
        item = dict(row)
        item["transaction_ids"] = _loads(item["transaction_ids"], [])
        item["metadata"] = _loads(item["metadata"], {})
        for key in (
            "sys_net_eq_neg_sys_cost", "all_costs_nonnegative", "any_cost_positive",
            "nonpositive_when_charged", "strictly_negative_once_charged",
        ):
            item[key] = bool(item[key])
        return item

    def list_systems(self, limit: int = 10_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM trading_system_evaluations ORDER BY created_at DESC,id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [self.get_system(row["id"]) for row in rows]

    def _create_payload(self, table: str, row: dict[str, Any], *, has_symbol: bool = False) -> dict[str, Any]:
        columns = "id,occurrence_id,integration_event_id"
        values: list[Any] = [row["id"], row["occurrence_id"], row["integration_event_id"]]
        placeholders = "?,?,?"
        if "transaction_id" in row:
            columns += ",transaction_id"
            placeholders += ",?"
            values.append(row["transaction_id"])
        if has_symbol:
            columns += ",symbol"
            placeholders += ",?"
            values.append(row["symbol"])
        columns += ",payload"
        placeholders += ",?"
        values.append(_json(row))
        if has_symbol:
            columns += ",metadata"
            placeholders += ",?"
            values.append(_json(row.get("metadata", {})))
        columns += ",created_at"
        placeholders += ",?"
        values.append(row.get("created_at", utcnow()))
        with self._lock:
            self._conn.execute(
                f"INSERT INTO {table} ({columns}) VALUES({placeholders})", tuple(values)
            )
            self._conn.commit()
        return dict(row)

    def create_shift(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._create_payload("trading_shift_evaluations", row)

    def create_numeraire(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._create_payload("trading_numeraire_evaluations", row)

    def create_circuit(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._create_payload("trading_circuit_evaluations", row, has_symbol=True)

    def create_pnl(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._create_payload("trading_pnl_evaluations", row, has_symbol=True)

    def _list_payloads(self, table: str, limit: int) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            f"SELECT payload FROM {table} ORDER BY created_at DESC,id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [_loads(row["payload"], {}) for row in rows]

    def list_shifts(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return self._list_payloads("trading_shift_evaluations", limit)

    def list_numeraires(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return self._list_payloads("trading_numeraire_evaluations", limit)

    def list_circuits(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return self._list_payloads("trading_circuit_evaluations", limit)

    def list_pnl(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return self._list_payloads("trading_pnl_evaluations", limit)

    def stats(self) -> dict[str, int]:
        tables = {
            "transactions": "trading_transactions",
            "systems": "trading_system_evaluations",
            "shifts": "trading_shift_evaluations",
            "numeraires": "trading_numeraire_evaluations",
            "circuits": "trading_circuit_evaluations",
            "pnl": "trading_pnl_evaluations",
        }
        return {
            key: int(self._conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for key, table in tables.items()
        }

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO trading_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute("SELECT value FROM trading_state WHERE key=?", (key,)).fetchone()
        return default if row is None else _loads(row["value"], default)
