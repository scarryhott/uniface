from __future__ import annotations

"""Trusted Alpaca source adapter for the current PR-104 closure runtime.

Alpaca supplies observer-relative events from one market through time.  This
module signs exact quote and fill returns with the configured Ed25519 adapter
key, retains each event once in a durable history, and passes only actual
buy-fill -> inventory -> actual sell-fill temporal returns to the existing full
closure-equation resolver.  A simultaneous bid/ask book is a local friction
projection and never a completed trading itinerary.

It is deliberately not a strategy or a second trading runtime.  It does not
choose an exit, hold duration, threshold, position size, or order.  Closure,
translational-truth partitioning, hair-fidelity horizon, relative-ball size,
atlas construction, and OPEN selection remain owned by
``interactive_translation_equations_current``.
"""

import argparse
import base64
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
from typing import Any, Callable, Mapping, Sequence

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .interactive_translation_equations_current import resolve_closure_equations
from .trading_source_return_truth import (
    PUBLIC_KEYS_ENV,
    encode_public_key,
    issue_trading_source_witness,
    private_key_from_base64,
)


PROTOCOL = "closure.supernet/alpaca-live-verified-source-adapter-v1"
EVENT_PROTOCOL = "closure.supernet/alpaca-temporal-source-event-v1"
PRIVATE_KEY_ENV = "CLOSURE_ALPACA_ADAPTER_PRIVATE_KEY"
AUTHORITY_ENV = "CLOSURE_ALPACA_ADAPTER_AUTHORITY"
HISTORY_PATH_ENV = "CLOSURE_ALPACA_HISTORY_PATH"
OBSERVER_ENV = "CLOSURE_ALPACA_OBSERVER_ID"
SYMBOLS_ENV = "CLOSURE_ALPACA_SYMBOLS"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()}"


def _decimal(value: Any) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"Alpaca supplied a non-decimal market coordinate: {value!r}") from exc
    if not result.is_finite() or result <= 0:
        raise ValueError(f"Alpaca supplied a non-positive market coordinate: {value!r}")
    return result


def _text(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _log(value: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = 48
        return +value.ln()


def _timestamp(value: Any) -> str:
    if value is None:
        return datetime.now(UTC).isoformat()
    if hasattr(value, "isoformat"):
        return str(value.isoformat())
    return str(value)


def _symbols(value: str | Sequence[str]) -> tuple[str, ...]:
    parts = value.split(",") if isinstance(value, str) else value
    result = tuple(dict.fromkeys(str(item).strip().upper() for item in parts if str(item).strip()))
    if not result:
        raise ValueError("At least one Alpaca symbol is required")
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
            history_path=Path(os.environ.get(HISTORY_PATH_ENV, "runtime_data/alpaca_closure_history.db")),
            api_key=api_key,
            api_secret=api_secret,
            private_key=private_key_from_base64(private_value),
            top_levels=max(1, int(os.environ.get("CLOSURE_ALPACA_TOP_LEVELS", "5"))),
            paper=os.environ.get("CLOSURE_ALPACA_PAPER", "true").strip().lower()
            not in {"0", "false", "no"},
        )


class AlpacaClosureHistory:
    """Persistent, replay-safe returned-source history for the pure resolver."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS alpaca_frames (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    observed_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS alpaca_returns (
                    authority_id TEXT NOT NULL,
                    source_event_id TEXT NOT NULL,
                    frame_seq INTEGER NOT NULL REFERENCES alpaca_frames(seq),
                    row_json TEXT NOT NULL,
                    PRIMARY KEY (authority_id, source_event_id)
                );
                CREATE INDEX IF NOT EXISTS idx_alpaca_returns_frame
                    ON alpaca_returns(frame_seq);
                CREATE TABLE IF NOT EXISTS alpaca_source_events (
                    authority_id TEXT NOT NULL,
                    source_event_id TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    event_kind TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    PRIMARY KEY (authority_id, source_event_id)
                );
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    @staticmethod
    def _coordinates(row: Mapping[str, Any]) -> tuple[str, str]:
        witness = row.get("source_witness")
        body = witness.get("body") if isinstance(witness, Mapping) else None
        if not isinstance(body, Mapping):
            raise ValueError("Alpaca history accepts only signed source returns")
        authority = str(body.get("authority_id") or "")
        event_id = str(body.get("source_event_id") or "")
        if not authority or not event_id:
            raise ValueError("Signed Alpaca return lacks authority or source-event identity")
        return authority, event_id

    def append_frame(self, rows: Sequence[Mapping[str, Any]], *, observed_at: str) -> dict[str, Any]:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            cursor = db.execute("INSERT INTO alpaca_frames(observed_at) VALUES (?)", (observed_at,))
            frame_seq = int(cursor.lastrowid)
            inserted = 0
            replayed = 0
            for raw in rows:
                row = dict(raw)
                authority, event_id = self._coordinates(row)
                result = db.execute(
                    """INSERT OR IGNORE INTO alpaca_returns
                       (authority_id, source_event_id, frame_seq, row_json)
                       VALUES (?, ?, ?, ?)""",
                    (authority, event_id, frame_seq, _stable(row)),
                )
                if result.rowcount:
                    inserted += 1
                else:
                    replayed += 1
            if inserted == 0:
                db.execute("DELETE FROM alpaca_frames WHERE seq = ?", (frame_seq,))
                frame_seq = 0
            db.commit()
        return {
            "frame_added": inserted > 0,
            "frame_seq": frame_seq or None,
            "inserted_return_count": inserted,
            "replayed_return_count": replayed,
            "persistent_replay_protection": True,
        }

    def history(self) -> list[list[dict[str, Any]]]:
        with self._connect() as db:
            rows = db.execute(
                """SELECT frame_seq, row_json FROM alpaca_returns
                   ORDER BY frame_seq, authority_id, source_event_id"""
            ).fetchall()
        frames: list[list[dict[str, Any]]] = []
        current_seq: int | None = None
        current: list[dict[str, Any]] = []
        for frame_seq, row_json in rows:
            if current_seq is not None and int(frame_seq) != current_seq:
                frames.append(current)
                current = []
            current_seq = int(frame_seq)
            current.append(json.loads(str(row_json)))
        if current:
            frames.append(current)
        return frames

    def append_source_events(
        self,
        events: Sequence[Mapping[str, Any]],
        *,
        observed_at: str,
    ) -> dict[str, int]:
        inserted = 0
        replayed = 0
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            for event in events:
                body = dict(event.get("body") or {})
                authority = str(body.get("authority_id") or "")
                event_id = str(body.get("source_event_id") or "")
                kind = str(body.get("event_kind") or "")
                if not authority or not event_id or not kind:
                    raise ValueError("Signed Alpaca source event lacks canonical coordinates")
                result = db.execute(
                    """INSERT OR IGNORE INTO alpaca_source_events
                       (authority_id, source_event_id, observed_at, event_kind, event_json)
                       VALUES (?, ?, ?, ?, ?)""",
                    (authority, event_id, observed_at, kind, _stable(dict(event))),
                )
                if result.rowcount:
                    inserted += 1
                else:
                    replayed += 1
            db.commit()
        return {
            "inserted_source_event_count": inserted,
            "replayed_source_event_count": replayed,
        }

    def counts(self) -> dict[str, int]:
        with self._connect() as db:
            frame_count = int(db.execute("SELECT COUNT(*) FROM alpaca_frames").fetchone()[0])
            return_count = int(db.execute("SELECT COUNT(*) FROM alpaca_returns").fetchone()[0])
            source_event_count = int(
                db.execute("SELECT COUNT(*) FROM alpaca_source_events").fetchone()[0]
            )
        return {
            "frame_count": frame_count,
            "return_count": return_count,
            "source_event_count": source_event_count,
        }


class AlpacaLiveClosureAdapter:
    def __init__(
        self,
        config: AlpacaLiveConfig,
        *,
        data_client: Any | None = None,
        trading_client: Any | None = None,
        request_factory: Callable[[Sequence[str]], Any] | None = None,
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
                raise RuntimeError("Install the Alpaca extra: pip install 'closure-supernet[alpaca]'") from exc
            data_client = CryptoHistoricalDataClient(config.api_key, config.api_secret)
        self.data_client = data_client
        if trading_client is None:
            try:
                from alpaca.trading.client import TradingClient
            except ImportError as exc:
                raise RuntimeError("Install the Alpaca extra: pip install 'closure-supernet[alpaca]'") from exc
            trading_client = TradingClient(
                config.api_key,
                config.api_secret,
                paper=config.paper,
            )
        self.trading_client = trading_client
        if request_factory is None:
            try:
                from alpaca.data.requests import CryptoLatestOrderbookRequest
            except ImportError as exc:
                raise RuntimeError("Install the Alpaca extra: pip install 'closure-supernet[alpaca]'") from exc
            request_factory = lambda symbols: CryptoLatestOrderbookRequest(symbol_or_symbols=list(symbols))
        self.request_factory = request_factory
        if orders_request_factory is None:
            try:
                from alpaca.trading.enums import QueryOrderStatus
                from alpaca.trading.requests import GetOrdersRequest
            except ImportError as exc:
                raise RuntimeError("Install the Alpaca extra: pip install 'closure-supernet[alpaca]'") from exc
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
            raise RuntimeError(f"{PUBLIC_KEYS_ENV} must be a JSON authority-to-key mapping") from exc
        expected = encode_public_key(self.config.private_key.public_key())
        if not isinstance(trusted, Mapping) or trusted.get(self.config.authority_id) != expected:
            raise RuntimeError("The Alpaca adapter public key is not the configured closure trust root")

    def _source_event_witness(self, *, event_kind: str, event: Mapping[str, Any]) -> dict[str, Any]:
        body = {
            "protocol": EVENT_PROTOCOL,
            "authority_id": self.config.authority_id,
            "observer_id": self.config.observer_id,
            "source_event_id": _digest("alpaca-source-event", event),
            "event_kind": event_kind,
            "source_event": dict(event),
        }
        return {
            "protocol": EVENT_PROTOCOL,
            "authority_id": self.config.authority_id,
            "body": body,
            "signature": base64.b64encode(
                self.config.private_key.sign(_stable(body).encode("utf-8"))
            ).decode("ascii"),
        }

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

    def _book_source_event(
        self,
        symbol: str,
        book: Any,
    ) -> tuple[dict[str, Any], dict[str, Any]] | None:
        bids = list(book.bids[: self.config.top_levels])
        asks = list(book.asks[: self.config.top_levels])
        if not bids or not asks:
            return None
        bid = _decimal(bids[0].price)
        ask = _decimal(asks[0].price)
        timestamp = _timestamp(getattr(book, "timestamp", None))
        exact_event = {
            "venue": "alpaca",
            "market": "crypto",
            "symbol": symbol,
            "timestamp": timestamp,
            "bids": [
                {"price": _text(_decimal(level.price)), "size": _text(_decimal(level.size))}
                for level in bids
            ],
            "asks": [
                {"price": _text(_decimal(level.price)), "size": _text(_decimal(level.size))}
                for level in asks
            ],
        }
        witness = self._source_event_witness(
            event_kind="CRYPTO_ORDERBOOK",
            event=exact_event,
        )
        projection = {
            "kind": "CURRENT_SPREAD_FRICTION_PROJECTION",
            "status": "WITNESSED",
            "source_event_id": witness["body"]["source_event_id"],
            "symbol": symbol,
            "timestamp": timestamp,
            "best_bid": _text(bid),
            "best_ask": _text(ask),
            "log_spread_curvature": _text(_log(ask) - _log(bid)),
            "instantaneous_spread_is_completed_trade": False,
            "authors_closed_itinerary": False,
            "semantic_authority": False,
        }
        return witness, projection

    def _orders(self, symbol: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        request = self.orders_request_factory(symbol)
        raw_orders = self.trading_client.get_orders(filter=request)
        source_orders: list[dict[str, Any]] = []
        rows: list[dict[str, Any]] = []
        normalized_symbol = symbol.replace("/", "").upper()
        for raw in raw_orders:
            order = self._model_dict(raw)
            order_symbol = str(order.get("symbol") or "").replace("/", "").upper()
            if order_symbol != normalized_symbol:
                continue
            source_orders.append(order)
            try:
                qty = _decimal(order.get("filled_qty")) if order.get("filled_qty") else None
                price = _decimal(order.get("filled_avg_price")) if order.get("filled_avg_price") else None
            except ValueError:
                # OPEN, canceled, and rejected orders commonly report a literal
                # zero filled quantity. They are source events, not fill returns.
                continue
            if qty is None or price is None:
                continue
            side = str(order.get("side") or "").lower().split(".")[-1]
            if side not in {"buy", "sell"}:
                continue
            rows.append({**order, "_filled_qty": qty, "_filled_price": price, "_side": side})
        rows.sort(
            key=lambda row: (
                str(row.get("filled_at") or row.get("updated_at") or row.get("submitted_at") or ""),
                str(row.get("id") or ""),
            )
        )
        return source_orders, rows

    def _fill_frames(
        self,
        symbol: str,
        orders: Sequence[Mapping[str, Any]],
    ) -> tuple[list[list[dict[str, Any]]], dict[str, Any]]:
        base, quote = symbol.split("/", 1)
        lots: list[dict[str, Any]] = []
        frames: list[list[dict[str, Any]]] = []
        unmatched_sell = Decimal("0")
        for order in orders:
            qty = _decimal(order["_filled_qty"])
            if order["_side"] == "buy":
                lots.append({"order": dict(order), "remaining": qty})
                continue
            sell_remaining = qty
            allocation_index = 0
            for lot in lots:
                if sell_remaining <= 0:
                    break
                available = Decimal(str(lot["remaining"]))
                if available <= 0:
                    continue
                allocated = min(available, sell_remaining)
                lot["remaining"] = available - allocated
                sell_remaining -= allocated
                buy = dict(lot["order"])
                sell = dict(order)
                allocation = {
                    "symbol": symbol,
                    "buy_order": {k: v for k, v in buy.items() if not k.startswith("_")},
                    "sell_order": {k: v for k, v in sell.items() if not k.startswith("_")},
                    "allocated_base_quantity": _text(allocated),
                    "allocation_index": allocation_index,
                    "inventory_method": "FIFO_RETURNED_FILL_ALLOCATION",
                }
                allocation_index += 1
                lot_id = _digest("alpaca-temporal-lot", allocation)
                inventory = f"{base}:INVENTORY:{lot_id}"
                committed = f"{quote}:COMMITTED:{lot_id}"
                legs = (
                    ("BUY_FILL", committed, inventory, _log(_decimal(buy["_filled_price"])), buy),
                    ("SELL_FILL", inventory, committed, -_log(_decimal(sell["_filled_price"])), sell),
                )
                frame: list[dict[str, Any]] = []
                for leg_kind, source, target, value, venue_order in legs:
                    source_event = {
                        "allocation": allocation,
                        "leg_kind": leg_kind,
                        "venue_order": {k: v for k, v in venue_order.items() if not k.startswith("_")},
                    }
                    source_event_id = _digest("alpaca-fill-return", source_event)
                    price = _decimal(venue_order["_filled_price"])
                    row: dict[str, Any] = {
                        "source": source,
                        "target": target,
                        "value": _text(value),
                        "timestamp": venue_order.get("filled_at"),
                        "authenticated": True,
                        "cost_complete": False,
                        "relative_size": _text(allocated * price),
                        "relative_size_unit": f"{quote}-notional",
                        "venue": "alpaca",
                        "venue_event_kind": leg_kind,
                        "venue_symbol": symbol,
                        "exact_source_event": source_event,
                        "exact_source_event_digest": source_event_id,
                        "fees_returned": False,
                        "automatic_order_submission": False,
                    }
                    row["source_witness"] = issue_trading_source_witness(
                        private_key=self.config.private_key,
                        authority_id=self.config.authority_id,
                        observer_id=self.config.observer_id,
                        source_event_id=source_event_id,
                        source_stream=f"alpaca:trading:fills:{symbol}",
                        row=row,
                    )
                    frame.append(row)
                frames.append(frame)
            unmatched_sell += sell_remaining

        open_qty = sum((Decimal(str(lot["remaining"])) for lot in lots), Decimal("0"))
        return frames, {
            "completed_temporal_return_count": len(frames),
            "open_inventory_base_quantity": _text(open_qty),
            "unmatched_sell_base_quantity": _text(unmatched_sell),
            "inventory_status": "OPEN" if open_qty or unmatched_sell else "WITNESSED",
            "inventory_method": "FIFO_RETURNED_FILL_ALLOCATION",
            "fill_fees_returned": False,
        }

    def receive_frame(
        self,
    ) -> tuple[list[list[dict[str, Any]]], list[dict[str, Any]], dict[str, Any]]:
        request = self.request_factory(self.config.symbols)
        books = self.data_client.get_crypto_latest_orderbook(request)
        symbol = self.config.symbols[0]
        book = books.get(symbol) if isinstance(books, Mapping) else None
        if book is None:
            try:
                book = books[symbol]
            except (KeyError, TypeError):
                book = None
        source_events: list[dict[str, Any]] = []
        spread_projection: dict[str, Any] | None = None
        if book is not None:
            translated = self._book_source_event(symbol, book)
            if translated is not None:
                event, spread_projection = translated
                source_events.append(event)
        source_orders, filled_orders = self._orders(symbol)
        for event in source_orders:
            source_events.append(self._source_event_witness(event_kind="ORDER_STATE", event=event))
        frames, inventory = self._fill_frames(symbol, filled_orders)
        observed_at = datetime.now(UTC).isoformat()
        return frames, source_events, {
            "received_at": observed_at,
            "configured_symbol": symbol,
            "missing_quote": book is None,
            "received_source_event_count": len(source_events),
            "received_relation_frame_count": len(frames),
            "received_return_count": sum(len(frame) for frame in frames),
            "spread_projection": spread_projection,
            "inventory_projection": inventory,
            "actual_alpaca_objects_translated": bool(source_events),
            "adapter_authors_closure": False,
            "quote_authors_completed_trade": False,
            "instantaneous_ask_bid_cycle_present": False,
            "multi_asset_cycle_present": False,
        }

    def resolve_once(self) -> dict[str, Any]:
        frames, source_events, receive_audit = self.receive_frame()
        event_audit = self.history.append_source_events(
            source_events,
            observed_at=receive_audit["received_at"],
        )
        frame_audits = [
            self.history.append_frame(frame, observed_at=receive_audit["received_at"])
            for frame in frames
        ]
        append_audit = {
            "inserted_return_count": sum(
                int(audit["inserted_return_count"]) for audit in frame_audits
            ),
            "replayed_return_count": sum(
                int(audit["replayed_return_count"]) for audit in frame_audits
            ),
            "inserted_relation_frame_count": sum(
                1 for audit in frame_audits if audit["frame_added"]
            ),
            "persistent_replay_protection": True,
        }
        history = self.history.history()
        receipt = resolve_closure_equations(
            {
                "trading": {
                    "observer_id": self.config.observer_id,
                    "source_truth_mode": "VERIFIED",
                    "sensor_history": history,
                }
            }
        )
        trading = dict(receipt.get("trading") or {})
        trading["alpaca_live_adapter"] = {
            "protocol": PROTOCOL,
            **receive_audit,
            **event_audit,
            **append_audit,
            **self.history.counts(),
            "source_event_id_is_exact_event_digest": True,
            "quote_is_friction_projection_only": True,
            "closed_relation_requires_returned_buy_and_sell_fills": True,
            "relation_values_are_temporal_fill_log_coordinates": True,
            "profitable_curvature_sign": "K<0",
            "natural_profit_definition": "Pi_nat=-K",
            "fixed_trade_kind_present": False,
            "fixed_horizon_present": False,
            "external_position_size_present": False,
            "fill_fee_return_missing": True,
            "automatic_order_submission": False,
        }
        receipt["trading"] = trading
        return receipt


def compact_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    trading = dict(receipt.get("trading") or {})
    partition = dict(trading.get("translational_truth_partition") or {})
    atlas = dict(trading.get("current_closure_relative_atlas") or {})
    boundary = dict(trading.get("open_boundary_natural_selection") or {})
    return {
        "protocol": PROTOCOL,
        "status": trading.get("status"),
        "natural_form_count": trading.get("witnessed_natural_form_count"),
        "current_profit_truth_witnessed": trading.get("current_profit_truth_witnessed"),
        "translational_truth_class_count": partition.get("class_count"),
        "relative_atlas_form_count": atlas.get("form_count"),
        "open_boundary_interaction_count": boundary.get("boundary_interaction_count"),
        "selected_interactions": trading.get("selected_interactions", []),
        "learning_interactions": trading.get("learning_interactions", []),
        "source_truth_audit": trading.get("source_truth_audit"),
        "alpaca_live_adapter": trading.get("alpaca_live_adapter"),
        "automatic_order_submission": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Alpaca as a trusted live source for PR-104 closure")
    parser.add_argument("--loop", action="store_true", help="continue receiving live source frames")
    parser.add_argument("--interval", type=float, default=15.0, help="seconds between source frames")
    parser.add_argument("--iterations", type=int, default=0, help="stop after N loop iterations; 0 is unbounded")
    parser.add_argument("--full", action="store_true", help="print the full closure-equation receipt")
    args = parser.parse_args()

    adapter = AlpacaLiveClosureAdapter(AlpacaLiveConfig.from_env())
    iteration = 0
    while True:
        receipt = adapter.resolve_once()
        print(json.dumps(receipt if args.full else compact_receipt(receipt), indent=2, default=str))
        iteration += 1
        if not args.loop or (args.iterations and iteration >= args.iterations):
            return
        time.sleep(max(0.1, args.interval))


__all__ = [
    "AlpacaClosureHistory",
    "AlpacaLiveClosureAdapter",
    "AlpacaLiveConfig",
    "PROTOCOL",
    "compact_receipt",
    "main",
]


if __name__ == "__main__":
    main()
