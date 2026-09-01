from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
import json
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from closure_supernet.alpaca_live_closure import (
    AlpacaLiveClosureAdapter,
    AlpacaLiveConfig,
    compact_receipt,
)
from closure_supernet.trading_source_return_truth import (
    PUBLIC_KEYS_ENV,
    encode_public_key,
)


class FakeDataClient:
    def __init__(self, books, trades=None):
        self.books = books
        self.trades = trades or {}

    def get_crypto_latest_orderbook(self, request):
        return self.books

    def get_crypto_latest_trade(self, request):
        return self.trades


class FakeTradingClient:
    def __init__(self, orders=()):
        self.orders = list(orders)

    def get_orders(self, *, filter):
        return self.orders


def level(price: str, size: str):
    return SimpleNamespace(price=Decimal(price), size=Decimal(size))


def book(*, bid: str = "100", ask: str = "101", seconds: int = 0):
    return SimpleNamespace(
        timestamp=datetime(2026, 9, 1, 12, 0, tzinfo=UTC)
        + timedelta(seconds=seconds),
        bids=[level(bid, "2")],
        asks=[level(ask, "3")],
    )


def market_trade(*, price: str = "100.5", size: str = "0.1", seconds: int = 1):
    return SimpleNamespace(
        symbol="BTC/USD",
        price=price,
        size=size,
        timestamp=datetime(2026, 9, 1, 12, 0, tzinfo=UTC)
        + timedelta(seconds=seconds),
    )


def fill(
    order_id: str,
    side: str,
    price: str,
    qty: str,
    *,
    seconds: int,
    fee: str | None = None,
):
    timestamp = datetime(2026, 9, 1, 12, 0, tzinfo=UTC) + timedelta(seconds=seconds)
    body = {
        "id": order_id,
        "symbol": "BTC/USD",
        "side": side,
        "status": "filled",
        "filled_qty": qty,
        "filled_avg_price": price,
        "filled_at": timestamp,
        "updated_at": timestamp,
        "submitted_at": timestamp - timedelta(seconds=2),
    }
    if fee is not None:
        body["fee_amount"] = fee
        body["fee_currency"] = "USD"
    return SimpleNamespace(**body)


def configured_adapter(
    tmp_path,
    monkeypatch,
    *,
    orders=(),
    symbols=("BTC/USD",),
    trade=True,
):
    private = Ed25519PrivateKey.generate()
    authority = "alpaca-test-adapter"
    monkeypatch.setenv(
        PUBLIC_KEYS_ENV,
        json.dumps({authority: encode_public_key(private.public_key())}),
    )
    config = AlpacaLiveConfig(
        observer_id="alpaca:test:observer",
        authority_id=authority,
        symbols=symbols,
        history_path=tmp_path / "alpaca.db",
        api_key="paper-key",
        api_secret="paper-secret",
        private_key=private,
    )
    trades = {"BTC/USD": market_trade()} if trade else {}
    return AlpacaLiveClosureAdapter(
        config,
        data_client=FakeDataClient({"BTC/USD": book()}, trades),
        trading_client=FakeTradingClient(orders),
        orderbook_request_factory=lambda requested: tuple(requested),
        trade_request_factory=lambda requested: tuple(requested),
        orders_request_factory=lambda symbol: symbol,
    )


def test_quote_and_market_trade_are_signed_context_not_completed_trade(
    tmp_path, monkeypatch
):
    adapter = configured_adapter(tmp_path, monkeypatch)
    events, audit = adapter.receive_events()

    assert {event["body"]["event_kind"] for event in events} == {
        "CRYPTO_ORDERBOOK",
        "MARKET_TRADE",
    }
    assert audit["quote_authors_completed_trade"] is False
    assert audit["instantaneous_ask_bid_cycle_present"] is False
    assert audit["successor_bid_exit_rule_present"] is False
    assert audit["fifo_fill_pairing_present"] is False

    trading = adapter.resolve_once()["trading"]
    assert trading["status"] == "OPEN"
    assert trading["natural_forms"] == []
    assert trading["temporal_closure_count"] == 0
    assert Decimal(trading["quote_projections"][-1]["log_spread_curvature"]) > 0
    assert trading["quote_projections"][-1]["authors_temporal_closure"] is False


def test_buy_fill_remains_open_until_relative_inventory_returns(tmp_path, monkeypatch):
    adapter = configured_adapter(
        tmp_path,
        monkeypatch,
        orders=[fill("buy-1", "buy", "100", "0.2", seconds=5)],
    )
    trading = adapter.resolve_once()["trading"]

    assert trading["status"] == "OPEN"
    assert trading["natural_forms"] == []
    assert trading["temporal_closure_count"] == 0
    assert trading["temporal_closure_audit"]["current_relative_inventory"] == "0.2"
    assert trading["temporal_closure_audit"]["current_inventory_status"] == "OPEN"


def test_partial_sell_does_not_fake_a_closed_lot(tmp_path, monkeypatch):
    adapter = configured_adapter(
        tmp_path,
        monkeypatch,
        orders=[
            fill("buy-1", "buy", "100", "0.2", seconds=5),
            fill("sell-1", "sell", "102", "0.1", seconds=20),
        ],
    )
    trading = adapter.resolve_once()["trading"]

    assert trading["temporal_closure_count"] == 0
    assert trading["temporal_closure_audit"]["current_relative_inventory"] == "0.1"
    assert trading["fill_derivation_audit"]["fifo_matching_used"] is False
    assert trading["fill_derivation_audit"]["cost_basis_selector_present"] is False


def test_multi_fill_path_closes_when_inventory_state_returns(tmp_path, monkeypatch):
    adapter = configured_adapter(
        tmp_path,
        monkeypatch,
        orders=[
            fill("buy-1", "buy", "100", "0.1", seconds=5),
            fill("buy-2", "buy", "110", "0.1", seconds=10),
            fill("sell-1", "sell", "120", "0.2", seconds=30),
        ],
    )
    trading = adapter.resolve_once()["trading"]
    temporal = trading["current_temporal_closure"]
    form = trading["natural_forms"][0]

    assert trading["status"] == "WITNESSED"
    assert trading["temporal_closure_count"] == 1
    assert temporal["path_fill_count"] == 3
    assert temporal["inventory_return_exact"] is True
    assert temporal["fifo_matching_used"] is False
    assert temporal["gross_profit_quote"] == "3"
    assert temporal["net_profit_status"] == "OPEN"
    assert form["unitary_curvature"] == "-3"
    assert form["natural_profit"] == "3"
    assert form["orientation"] == "PROFITABLE"
    assert form["trade_projection"]["execution_return_status"] == "OPEN"
    assert trading["current_net_profit_truth_witnessed"] is False


def test_returned_quote_fees_make_net_profit_a_witness(tmp_path, monkeypatch):
    adapter = configured_adapter(
        tmp_path,
        monkeypatch,
        orders=[
            fill("buy-1", "buy", "100", "0.2", seconds=5, fee="0.01"),
            fill("sell-1", "sell", "102", "0.2", seconds=25, fee="0.01"),
        ],
    )
    trading = adapter.resolve_once()["trading"]
    temporal = trading["current_temporal_closure"]

    assert temporal["cost_complete"] is True
    assert temporal["gross_profit_quote"] == "0.4"
    assert temporal["fee_quote"] == "0.02"
    assert temporal["net_profit_quote"] == "0.38"
    assert temporal["net_profit_status"] == "WITNESSED"
    assert trading["current_net_profit_truth_witnessed"] is True
    assert trading["natural_forms"][0]["natural_profit"] == "0.38"
    assert trading["natural_forms"][0]["trade_projection"]["execution_return_status"] == "WITNESSED"


def test_temporal_relation_uses_returned_cashflow_not_log_spread(tmp_path, monkeypatch):
    adapter = configured_adapter(
        tmp_path,
        monkeypatch,
        orders=[
            fill("buy-1", "buy", "100", "0.2", seconds=5),
            fill("sell-1", "sell", "102", "0.2", seconds=25),
        ],
    )
    trading = adapter.resolve_once()["trading"]

    assert trading["natural_forms"][0]["natural_profit"] == "0.4"
    assert trading["instantaneous_ask_bid_cycle_authors_trade"] is False
    assert trading["successor_bid_authors_exit"] is False
    assert trading["empirical_arena_is_one_market_through_time"] is True


def test_source_event_replay_does_not_increase_temporal_history(tmp_path, monkeypatch):
    adapter = configured_adapter(
        tmp_path,
        monkeypatch,
        orders=[
            fill("buy-1", "buy", "100", "0.2", seconds=5),
            fill("sell-1", "sell", "102", "0.2", seconds=25),
        ],
    )
    first = adapter.resolve_once()["trading"]
    second = adapter.resolve_once()["trading"]

    first_audit = first["alpaca_live_adapter"]
    second_audit = second["alpaca_live_adapter"]
    assert first_audit["history_changed"] is True
    assert second_audit["history_changed"] is False
    assert second_audit["replayed_source_event_count"] > 0
    assert first["temporal_closure_count"] == second["temporal_closure_count"] == 1
    assert first["fill_derivation_audit"]["fill_increment_count"] == 2
    assert second["fill_derivation_audit"]["fill_increment_count"] == 2


def test_multi_asset_configuration_is_rejected(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="one market"):
        configured_adapter(
            tmp_path,
            monkeypatch,
            symbols=("BTC/USD", "ETH/USD"),
        )


def test_compact_receipt_preserves_temporal_closure_without_strategy_fields(
    tmp_path, monkeypatch
):
    compact = compact_receipt(
        configured_adapter(tmp_path, monkeypatch).resolve_once()
    )
    assert compact["status"] == "OPEN"
    assert compact["temporal_closure_count"] == 0
    assert compact["automatic_order_submission"] is False
    assert "hold_seconds" not in compact
    assert "notional_usd" not in compact
