from __future__ import annotations

"""Trusted live Alpaca source for single-market temporal closure trading.

This module has no trading-closure law.  It only receives actual venue events,
signs them, persists them once, and hands the returned event history to
``trading_temporal_market_closure``.

A quote book is a local friction/depth observation.  A market trade is a market
observation.  An order state is an interaction return.  A fill state is an
execution return.  None of those is paired with another event by this adapter;
the closure runtime alone determines when temporal inventory has returned.
"""

import argparse
import base64
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
from typing import Any, Callable, Mapping, Sequence

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .trading_source_return_truth import (
    PUBLIC_KEYS_ENV,
    encode_public_key,
    private_key_from_base64,
)
from .trading_temporal_market_closure import (
    ALPACA_EVENT_PROTOCOL,
    resolve_single_market_temporal_closure,
)


PROTOCOL = "closure.supernet/alpaca-live-temporal-source-adapter-v2"
EVENT_PROTOCOL = ALPACA_EVENT_PROTOCOL
PRIVATE_KEY_ENV = "CLOSURE_ALPACA_ADAPTER_PRIVATE_KEY"
AUTHORITY_ENV = "CLOSURE_ALPACA_ADAPTER_AUTHORITY"
HISTORY_PATH_ENV = "CLOSURE_ALPACA_HISTORY_PATH"
OBSERVER_ENV = "CLOSURE_ALPACA_OBSERVER_ID"
SYMBOLS_ENV = "CLOSURE_ALPACA_SYMBOLS"


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()}"


def _decimal(value: Any) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"Alpaca supplied a non-decimal coordinate: {value!r}") from exc
    if not result.is_finite():
        raise ValueError(f"Alpaca supplied a non-finite coordinate: {value!r}")
    return result


def _positive(value: Any) -> Decimal:
    result = _decimal(value)
    if result <= 0:
        raise ValueError(f"Alpaca supplied a non-positive coordinate: {value!r}")
    return result


def _text(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _timestamp(value: Any) -> str:
    if value is None:
        return datetime.now(UTC).isoformat()
    if hasattr(value, "isoformat"):
        return str(value.isoformat())
    return str(value)


def _symbols(value: str | Sequence[str]) -> tuple[str, ...]:
    parts = value.split(",") if isinstance(value, str) else value
    result = tuple(
        dict.fromkeys(
            str(item).strip().upper()
            for item in parts
            if str(item).strip()
        )
    )
    if not result:
        raise ValueError("Exactly one Alpaca crypto symbol is required")
    for symbol in result:
        if symbol.count("/") != 1:
            raise ValueError(f"Alpaca crypto symbol must be BASE/QUOTE: {symbol}")
    return result


@dataclass(frozen=True)
class AlpacaLiveConfig:
    observer_id: str
    authority_id: str
    symbols: tuple[str, ...]
    history_path: Path
    api_key: str
    api_secret: str
    private_key: Ed25519PrivateKey
    top_levels: int = 5
    paper: bool = True

    @classmethod
    def from_env(cls) -> "AlpacaLiveConfig":
        private_value = os.environ.get(PRIVATE_KEY_ENV, "").strip()
        if not private_value:
            raise RuntimeError(f"{PRIVATE_KEY_ENV} is required by the trusted Alpaca adapter")
        api_key = os.environ.get("APCA_API_KEY_ID", "").strip()
        api_secret = os.environ.get("APCA_API_SECRET_KEY", "").strip()
        if not api_key or not api_secret:
            raise RuntimeError("APCA_API_KEY_ID and APCA_API_SECRET_KEY are required")
        observer_id = os.environ.get(OBSERVER_ENV, "alpaca:paper:market").strip()
        authority_id = os.environ.get(AUTHORITY_ENV, "alpaca-paper-adapter-v1").strip()
        if not observer_id or not authority_id:
            raise RuntimeError(f"{OBSERVER_ENV} and {AUTHORITY_ENV} must be non-empty")
        symbols = _symbols(os.environ.get(SYMBOLS_ENV, "BTC/USD"))
        if len(symbols) != 1:
            raise RuntimeError(
                "Closure trading has one empirical market arena; configure exactly one Alpaca symbol"
            )
        return cls(
            observer_id=observer_id,
            authority_id=authority_id,
            symbols=symbols,
            history_path=Path(
                os.environ.get(
                    HISTORY_PATH_ENV,
                    "runtime_data/alpaca_closure_history.db",
                )
            ),
            api_key=api_key,
            api_secret=api_secret,
            private_key=private_key_from_base64(private_value),
            top_levels=max(1, int(os.environ.get("CLOSURE_ALPACA_TOP_LEVELS", "5"))),
            paper=os.environ.get("CLOSURE_ALPACA_PAPER", "true").strip().lower()
            not in {"0", "false", "no"},
        )


class AlpacaClosureHistory:
    """Durable exact source-event history; replay changes no temporal truth."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS alpaca_source_events (
                    authority_id TEXT NOT NULL,
                    source_event_id TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    event_kind TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    PRIMARY KEY (authority_id, source_event_id)
                );
                CREATE INDEX IF NOT EXISTS idx_alpaca_source_events_observed
                    ON alpaca_source_events(observed_at);
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        return connection

    @staticmethod
    def _coordinates(event: Mapping[str, Any]) -> tuple[str, str, str]:
        body_raw = event.get("body")
        body = body_raw if isinstance(body_raw, Mapping) else {}
        authority = str(body.get("authority_id") or "")
        event_id = str(body.get("source_event_id") or "")
        kind = str(body.get("event_kind") or "")
        if not authority or not event_id or not kind:
            raise ValueError("Signed Alpaca source event lacks canonical coordinates")
        return authority, event_id, kind

    def append_source_events(
        self,
        events: Sequence[Mapping[str, Any]],
        *,
        observed_at: str,
    ) -> dict[str, int | bool]:
        inserted = 0
        replayed = 0
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            for raw in events:
                event = dict(raw)
                authority, event_id, kind = self._coordinates(event)
                result = db.execute(
                    """INSERT OR IGNORE INTO alpaca_source_events
                       (authority_id, source_event_id, observed_at, event_kind, event_json)
                       VALUES (?, ?, ?, ?, ?)""",
                    (authority, event_id, observed_at, kind, _stable(event)),
                )
                if result.rowcount:
                    inserted += 1
                else:
                    replayed += 1
            db.commit()
        return {
            "inserted_source_event_count": inserted,
            "replayed_source_event_count": replayed,
            "history_changed": inserted > 0,
            "persistent_replay_protection": True,
        }

    def source_events(self) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                """SELECT event_json
                   FROM alpaca_source_events
                   ORDER BY observed_at, rowid"""
            ).fetchall()
        return [json.loads(str(row[0])) for row in rows]

    def counts(self) -> dict[str, int]:
        with self._connect() as db:
            source_event_count = int(
                db.execute("SELECT COUNT(*) FROM alpaca_source_events").fetchone()[0]
            )
        return {"source_event_count": source_event_count}


class AlpacaLiveClosureAdapter:
    def __init__(
        self,
        config: AlpacaLiveConfig,
        *,
        data_client: Any | None = None,
        trading_client: Any | None = None,
        orderbook_request_factory: Callable[[Sequence[str]], Any] | None = None,
        trade_request_factory: Callable[[Sequence[str]], Any] | None = None,
        orders_request_factory: Callable[[str], Any] | None = None,
    ):
        self.config = config
        if len(config.symbols) != 1:
            raise ValueError(
                "Closure trading observes one market through time; multiple symbols are not one arena"
            )
        self.history = AlpacaClosureHistory(config.history_path)
        self._assert_trusted_public_key()

        if data_client is None:
            try:
                from alpaca.data.historical import CryptoHistoricalDataClient
            except ImportError as exc:
                raise RuntimeError(
                    "Install the Alpaca extra: pip install 'closure-supernet[alpaca]'"
                ) from exc
            data_client = CryptoHistoricalDataClient(config.api_key, config.api_secret)
        self.data_client = data_client

        if trading_client is None:
            try:
                from alpaca.trading.client import TradingClient
            except ImportError as exc:
                raise RuntimeError(
                    "Install the Alpaca extra: pip install 'closure-supernet[alpaca]'"
                ) from exc
            trading_client = TradingClient(
                config.api_key,
                config.api_secret,
                paper=config.paper,
            )
        self.trading_client = trading_client

        if orderbook_request_factory is None:
            try:
                from alpaca.data.requests import CryptoLatestOrderbookRequest
            except ImportError as exc:
                raise RuntimeError(
                    "Install the Alpaca extra: pip install 'closure-supernet[alpaca]'"
                ) from exc
            orderbook_request_factory = lambda symbols: CryptoLatestOrderbookRequest(
                symbol_or_symbols=list(symbols)
            )
        self.orderbook_request_factory = orderbook_request_factory

        if trade_request_factory is None:
            try:
                from alpaca.data.requests import CryptoLatestTradeRequest
            except ImportError as exc:
                raise RuntimeError(
                    "Install the Alpaca extra: pip install 'closure-supernet[alpaca]'"
                ) from exc
            trade_request_factory = lambda symbols: CryptoLatestTradeRequest(
                symbol_or_symbols=list(symbols)
            )
        self.trade_request_factory = trade_request_factory

        if orders_request_factory is None:
            try:
                from alpaca.trading.enums import QueryOrderStatus
                from alpaca.trading.requests import GetOrdersRequest
            except ImportError as exc:
                raise RuntimeError(
                    "Install the Alpaca extra: pip install 'closure-supernet[alpaca]'"
                ) from exc
            orders_request_factory = lambda symbol: GetOrdersRequest(
                status=QueryOrderStatus.ALL,
                symbols=[symbol],
                limit=500,
            )
        self.orders_request_factory = orders_request_factory

    def _assert_trusted_public_key(self) -> None:
        raw = os.environ.get(PUBLIC_KEYS_ENV, "").strip()
        if not raw:
            raise RuntimeError(f"{PUBLIC_KEYS_ENV} must trust the configured Alpaca adapter")
        try:
            trusted = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"{PUBLIC_KEYS_ENV} must be a JSON authority-to-key mapping"
            ) from exc
        expected = encode_public_key(self.config.private_key.public_key())
        if not isinstance(trusted, Mapping) or trusted.get(self.config.authority_id) != expected:
            raise RuntimeError(
                "The Alpaca adapter public key is not the configured closure trust root"
            )

    @staticmethod
    def _model_dict(value: Any) -> dict[str, Any]:
        if hasattr(value, "model_dump"):
            return dict(value.model_dump(mode="json"))
        if isinstance(value, Mapping):
            return dict(value)
        return {
            key: raw
            for key, raw in vars(value).items()
            if not key.startswith("_")
        }

    def _source_event_witness(
        self,
        *,
        event_kind: str,
        event: Mapping[str, Any],
    ) -> dict[str, Any]:
        source_event = dict(event)
        source_event_id = _digest(
            "alpaca-source-event",
            {"event_kind": event_kind, "source_event": source_event},
        )
        body = {
            "protocol": EVENT_PROTOCOL,
            "authority_id": self.config.authority_id,
            "observer_id": self.config.observer_id,
            "source_event_id": source_event_id,
            "event_kind": event_kind,
            "source_event": source_event,
        }
        return {
            "protocol": EVENT_PROTOCOL,
            "authority_id": self.config.authority_id,
            "body": body,
            "signature": base64.b64encode(
                self.config.private_key.sign(_stable(body).encode("utf-8"))
            ).decode("ascii"),
        }

    def _book_event(self, symbol: str, book: Any) -> dict[str, Any] | None:
        bids = list(book.bids[: self.config.top_levels])
        asks = list(book.asks[: self.config.top_levels])
        if not bids or not asks:
            return None
        event = {
            "venue": "alpaca",
            "market": "crypto",
            "symbol": symbol,
            "timestamp": _timestamp(getattr(book, "timestamp", None)),
            "bids": [
                {"price": _text(_positive(level.price)), "size": _text(_positive(level.size))}
                for level in bids
            ],
            "asks": [
                {"price": _text(_positive(level.price)), "size": _text(_positive(level.size))}
                for level in asks
            ],
        }
        return self._source_event_witness(event_kind="CRYPTO_ORDERBOOK", event=event)

    def _market_trade_event(self, symbol: str, trade: Any) -> dict[str, Any] | None:
        if trade is None:
            return None
        event = self._model_dict(trade)
        event.setdefault("symbol", symbol)
        event.setdefault("venue", "alpaca")
        event.setdefault("market", "crypto")
        return self._source_event_witness(event_kind="MARKET_TRADE", event=event)

    def _order_events(self, symbol: str) -> list[dict[str, Any]]:
        request = self.orders_request_factory(symbol)
        raw_orders = self.trading_client.get_orders(filter=request)
        normalized_symbol = symbol.replace("/", "").upper()
        events: list[dict[str, Any]] = []
        for raw in raw_orders:
            order = self._model_dict(raw)
            order_symbol = str(order.get("symbol") or "").replace("/", "").upper()
            if order_symbol != normalized_symbol:
                continue
            events.append(self._source_event_witness(event_kind="ORDER_STATE", event=order))
            try:
                filled_qty = _decimal(order.get("filled_qty") or "0")
                filled_price = _decimal(order.get("filled_avg_price") or "0")
            except ValueError:
                filled_qty = Decimal("0")
                filled_price = Decimal("0")
            if filled_qty > 0 and filled_price > 0:
                events.append(self._source_event_witness(event_kind="FILL_STATE", event=order))
        return events

    @staticmethod
    def _lookup(result: Any, symbol: str) -> Any | None:
        if isinstance(result, Mapping):
            return result.get(symbol)
        try:
            return result[symbol]
        except (KeyError, TypeError):
            return None

    def receive_events(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        symbol = self.config.symbols[0]
        events: list[dict[str, Any]] = []

        book_result = self.data_client.get_crypto_latest_orderbook(
            self.orderbook_request_factory(self.config.symbols)
        )
        book = self._lookup(book_result, symbol)
        book_event = self._book_event(symbol, book) if book is not None else None
        if book_event is not None:
            events.append(book_event)

        latest_trade = None
        trade_method = getattr(self.data_client, "get_crypto_latest_trade", None)
        if callable(trade_method):
            trade_result = trade_method(self.trade_request_factory(self.config.symbols))
            latest_trade = self._lookup(trade_result, symbol)
            trade_event = self._market_trade_event(symbol, latest_trade)
            if trade_event is not None:
                events.append(trade_event)

        order_events = self._order_events(symbol)
        events.extend(order_events)
        observed_at = datetime.now(UTC).isoformat()
        return events, {
            "received_at": observed_at,
            "configured_symbol": symbol,
            "missing_quote": book is None,
            "missing_market_trade": latest_trade is None,
            "received_source_event_count": len(events),
            "received_order_or_fill_event_count": len(order_events),
            "actual_alpaca_objects_translated": bool(events),
            "adapter_authors_relation_frames": False,
            "adapter_authors_closure": False,
            "quote_authors_completed_trade": False,
            "instantaneous_ask_bid_cycle_present": False,
            "successor_bid_exit_rule_present": False,
            "fifo_fill_pairing_present": False,
            "multi_asset_cycle_present": False,
            "automatic_order_submission": False,
        }

    def resolve_once(self) -> dict[str, Any]:
        events, receive_audit = self.receive_events()
        append_audit = self.history.append_source_events(
            events,
            observed_at=receive_audit["received_at"],
        )
        source_history = self.history.source_events()
        trading = resolve_single_market_temporal_closure(
            observer_id=self.config.observer_id,
            symbol=self.config.symbols[0],
            source_events=source_history,
        )
        trading["alpaca_live_adapter"] = {
            "protocol": PROTOCOL,
            **receive_audit,
            **append_audit,
            **self.history.counts(),
            "source_event_id_is_exact_signed_event_digest": True,
            "source_events_are_quote_trade_order_fill_returns": True,
            "quote_is_friction_projection_only": True,
            "closure_derivation_module": "trading_temporal_market_closure",
            "closed_relation_requires_temporal_inventory_return": True,
            "relation_value_is_returned_quote_cashflow_cost": True,
            "profitable_curvature_sign": "K<0",
            "natural_profit_definition": "Pi_nat=-K",
            "fixed_trade_kind_present": False,
            "fixed_horizon_present": False,
            "external_position_size_present": False,
            "automatic_order_submission": False,
        }
        return {
            "protocol": PROTOCOL,
            "status": trading.get("status"),
            "trading": trading,
        }


def compact_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    trading = dict(receipt.get("trading") or {})
    partition = dict(trading.get("translational_truth_partition") or {})
    atlas = dict(trading.get("current_closure_relative_atlas") or {})
    boundary = dict(trading.get("open_boundary_natural_selection") or {})
    return {
        "protocol": PROTOCOL,
        "status": trading.get("status"),
        "symbol": trading.get("symbol"),
        "temporal_closure_count": trading.get("temporal_closure_count"),
        "natural_form_count": trading.get("witnessed_natural_form_count"),
        "current_profit_truth_witnessed": trading.get("current_profit_truth_witnessed"),
        "current_net_profit_truth_witnessed": trading.get(
            "current_net_profit_truth_witnessed"
        ),
        "translational_truth_class_count": partition.get("class_count"),
        "relative_atlas_truth_class_count": atlas.get("truth_class_count"),
        "open_boundary_interaction_count": boundary.get("boundary_interaction_count"),
        "selected_interactions": trading.get("selected_interactions", []),
        "learning_interactions": trading.get("learning_interactions", []),
        "source_truth_audit": trading.get("source_truth_audit"),
        "temporal_closure_audit": trading.get("temporal_closure_audit"),
        "alpaca_live_adapter": trading.get("alpaca_live_adapter"),
        "automatic_order_submission": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Alpaca as a signed source for single-market temporal closure"
    )
    parser.add_argument("--loop", action="store_true", help="continue receiving live source events")
    parser.add_argument("--interval", type=float, default=15.0, help="seconds between source polls")
    parser.add_argument("--iterations", type=int, default=0, help="stop after N loop iterations; 0 is unbounded")
    parser.add_argument("--full", action="store_true", help="print the full temporal closure receipt")
    args = parser.parse_args()

    adapter = AlpacaLiveClosureAdapter(AlpacaLiveConfig.from_env())
    iteration = 0
    while True:
        receipt = adapter.resolve_once()
        print(
            json.dumps(
                receipt if args.full else compact_receipt(receipt),
                indent=2,
                default=str,
            )
        )
        iteration += 1
        if not args.loop or (args.iterations and iteration >= args.iterations):
            return
        time.sleep(max(0.1, args.interval))


__all__ = [
    "AlpacaClosureHistory",
    "AlpacaLiveClosureAdapter",
    "AlpacaLiveConfig",
    "EVENT_PROTOCOL",
    "PROTOCOL",
    "compact_receipt",
    "main",
]


if __name__ == "__main__":
    main()
