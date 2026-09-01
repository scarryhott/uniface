from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
import json
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from closure_supernet.alpaca_live_closure import AlpacaLiveClosureAdapter, AlpacaLiveConfig, compact_receipt
from closure_supernet.trading_source_return_truth import PUBLIC_KEYS_ENV, encode_public_key


class FakeDataClient:
    def __init__(self, books): self.books = books
    def get_crypto_latest_orderbook(self, request): return self.books


class FakeTradingClient:
    def __init__(self, orders=()): self.orders = list(orders)
    def get_orders(self, *, filter): return self.orders


def level(price: str, size: str):
    return SimpleNamespace(price=Decimal(price), size=Decimal(size))


def book(*, bid: str = "100", ask: str = "101"):
    return SimpleNamespace(
        timestamp=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        bids=[level(bid, "2")],
        asks=[level(ask, "3")],
    )


def fill(order_id: str, side: str, price: str, qty: str, *, seconds: int):
    timestamp = datetime(2026, 9, 1, 12, 0, tzinfo=UTC) + timedelta(seconds=seconds)
    return SimpleNamespace(
        id=order_id, symbol="BTC/USD", side=side, status="filled",
        filled_qty=qty, filled_avg_price=price, filled_at=timestamp,
        updated_at=timestamp, submitted_at=timestamp,
    )


def configured_adapter(tmp_path, monkeypatch, *, orders=(), symbols=("BTC/USD",)):
    private = Ed25519PrivateKey.generate()
    authority = "alpaca-test-adapter"
    monkeypatch.setenv(PUBLIC_KEYS_ENV, json.dumps({authority: encode_public_key(private.public_key())}))
    config = AlpacaLiveConfig(
        observer_id="alpaca:test:observer", authority_id=authority, symbols=symbols,
        history_path=tmp_path / "alpaca.db", api_key="paper-key", api_secret="paper-secret",
        private_key=private,
    )
    return AlpacaLiveClosureAdapter(
        config, data_client=FakeDataClient({"BTC/USD": book()}),
        trading_client=FakeTradingClient(orders), request_factory=lambda requested: tuple(requested),
        orders_request_factory=lambda symbol: symbol,
    )


def test_quote_is_signed_friction_projection_not_completed_trade(tmp_path, monkeypatch):
    adapter = configured_adapter(tmp_path, monkeypatch)
    frames, events, audit = adapter.receive_frame()

    assert frames == []
    assert len(events) == 1
    assert events[0]["body"]["event_kind"] == "CRYPTO_ORDERBOOK"
    assert Decimal(audit["spread_projection"]["log_spread_curvature"]) > 0
    assert audit["quote_authors_completed_trade"] is False
    assert audit["instantaneous_ask_bid_cycle_present"] is False
    assert audit["multi_asset_cycle_present"] is False

    trading = adapter.resolve_once()["trading"]
    assert trading["status"] == "OPEN"
    assert trading["natural_forms"] == []


def test_buy_fill_remains_open_inventory_until_actual_sell_return(tmp_path, monkeypatch):
    adapter = configured_adapter(
        tmp_path, monkeypatch,
        orders=[fill("buy-1", "buy", "100", "0.2", seconds=0)],
    )
    receipt = adapter.resolve_once()["trading"]
    audit = receipt["alpaca_live_adapter"]

    assert receipt["status"] == "OPEN"
    assert receipt["natural_forms"] == []
    assert audit["inventory_projection"]["inventory_status"] == "OPEN"
    assert audit["inventory_projection"]["open_inventory_base_quantity"] == "0.2"
    assert audit["received_relation_frame_count"] == 0


def test_actual_fill_return_closes_single_market_temporal_itinerary(tmp_path, monkeypatch):
    adapter = configured_adapter(
        tmp_path, monkeypatch,
        orders=[
            fill("buy-1", "buy", "100", "0.2", seconds=0),
            fill("sell-1", "sell", "102", "0.2", seconds=20),
        ],
    )
    trading = adapter.resolve_once()["trading"]
    form = trading["natural_forms"][0]

    assert trading["status"] == "WITNESSED"
    assert form["orientation"] == "PROFITABLE"
    assert Decimal(form["unitary_curvature"]) < 0
    assert Decimal(form["natural_profit"]) > 0
    assert form["timing"]["duration_seconds"] == "20.0"
    assert form["timing"]["fixed_horizon"] is None
    assert form["trade_projection"]["execution_return_status"] == "OPEN"
    assert trading["alpaca_live_adapter"]["fill_fee_return_missing"] is True
    assert trading["alpaca_live_adapter"]["automatic_order_submission"] is False


def test_fill_relation_replay_is_persistent_across_resolutions(tmp_path, monkeypatch):
    adapter = configured_adapter(
        tmp_path, monkeypatch,
        orders=[
            fill("buy-1", "buy", "100", "0.2", seconds=0),
            fill("sell-1", "sell", "102", "0.2", seconds=20),
        ],
    )
    first = adapter.resolve_once()["trading"]["alpaca_live_adapter"]
    second = adapter.resolve_once()["trading"]["alpaca_live_adapter"]

    assert first["inserted_return_count"] == 2
    assert first["frame_count"] == 1
    assert second["inserted_return_count"] == 0
    assert second["replayed_return_count"] == 2
    assert second["frame_count"] == 1
    assert second["return_count"] == 2


def test_multi_asset_configuration_is_rejected(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="one market"):
        configured_adapter(tmp_path, monkeypatch, symbols=("BTC/USD", "ETH/USD"))


def test_compact_receipt_preserves_closure_without_strategy_fields(tmp_path, monkeypatch):
    compact = compact_receipt(configured_adapter(tmp_path, monkeypatch).resolve_once())
    assert compact["status"] == "OPEN"
    assert compact["automatic_order_submission"] is False
    assert "hold_seconds" not in compact
    assert "notional_usd" not in compact
