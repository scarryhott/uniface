from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_supernet as base_api
from .config import RuntimeConfig
from .trading_models import (
    ClassicalTransaction,
    ClassicalTransactionCreate,
    ExecutionSelection,
    ExecutionSelectionCreate,
    NumeraireEvaluation,
    NumeraireEvaluationCreate,
    PnLEvaluation,
    PnLEvaluationCreate,
    PriceShiftEvaluation,
    PriceShiftEvaluationCreate,
    TradingCircuitEvaluation,
    TradingCircuitEvaluationCreate,
    TradingFieldProjection,
    TradingSystemEvaluation,
    TradingSystemEvaluationCreate,
)
from .trading_web import TRADING_HTML


def attach_trading_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "trading_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.trading_routes_attached = True
    app.version = "2.1.0"
    app.description += (
        "; NRRF780 classical trading is a simulation-only lens of the one "
        "SupernetIntegrator, with six-layer transactions, local-price/inf-cost "
        "evaluation, rigid quote execution, price holonomy, and time P&L"
    )

    @app.get("/trading", response_class=HTMLResponse, include_in_schema=False)
    async def trading_interface() -> str:
        return TRADING_HTML

    @app.get("/network/trading/capabilities")
    async def trading_capabilities() -> dict[str, Any]:
        return runtime.trading.capabilities()

    @app.post("/network/trading/selector", response_model=ExecutionSelection)
    async def execution_selector(data: ExecutionSelectionCreate) -> ExecutionSelection:
        try:
            return runtime.trading.execution_selection(data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/network/trading/transactions", response_model=ClassicalTransaction)
    async def create_transaction(data: ClassicalTransactionCreate) -> ClassicalTransaction:
        if not runtime.config.trading_enabled:
            raise HTTPException(status_code=503, detail="trading lens is disabled")
        try:
            return ClassicalTransaction.model_validate(await runtime.trading.create_transaction(data))
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/trading/transactions", response_model=list[ClassicalTransaction])
    async def list_transactions(
        symbol: str | None = None,
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[ClassicalTransaction]:
        return [
            ClassicalTransaction.model_validate(item)
            for item in runtime.trading_store.list_transactions(limit=limit, symbol=symbol)
        ]

    @app.post("/network/trading/systems", response_model=TradingSystemEvaluation)
    async def evaluate_system(data: TradingSystemEvaluationCreate) -> TradingSystemEvaluation:
        try:
            return TradingSystemEvaluation.model_validate(await runtime.trading.evaluate_system(data))
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/trading/systems", response_model=list[TradingSystemEvaluation])
    async def list_systems(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[TradingSystemEvaluation]:
        return [TradingSystemEvaluation.model_validate(item) for item in runtime.trading_store.list_systems(limit)]

    @app.post("/network/trading/invariance/shift", response_model=PriceShiftEvaluation)
    async def evaluate_shift(data: PriceShiftEvaluationCreate) -> PriceShiftEvaluation:
        try:
            return PriceShiftEvaluation.model_validate(await runtime.trading.evaluate_shift(data))
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/network/trading/invariance/numeraire", response_model=NumeraireEvaluation)
    async def evaluate_numeraire(data: NumeraireEvaluationCreate) -> NumeraireEvaluation:
        try:
            return NumeraireEvaluation.model_validate(await runtime.trading.evaluate_numeraire(data))
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/network/trading/circuits", response_model=TradingCircuitEvaluation)
    async def evaluate_circuit(data: TradingCircuitEvaluationCreate) -> TradingCircuitEvaluation:
        try:
            return TradingCircuitEvaluation.model_validate(await runtime.trading.evaluate_circuit(data))
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/trading/circuits", response_model=list[TradingCircuitEvaluation])
    async def list_circuits(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[TradingCircuitEvaluation]:
        return [TradingCircuitEvaluation.model_validate(item) for item in runtime.trading_store.list_circuits(limit)]

    @app.post("/network/trading/pnl", response_model=PnLEvaluation)
    async def evaluate_pnl(data: PnLEvaluationCreate) -> PnLEvaluation:
        try:
            return PnLEvaluation.model_validate(await runtime.trading.evaluate_pnl(data))
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/trading/pnl", response_model=list[PnLEvaluation])
    async def list_pnl(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[PnLEvaluation]:
        return [PnLEvaluation.model_validate(item) for item in runtime.trading_store.list_pnl(limit)]

    @app.get("/network/trading/field", response_model=TradingFieldProjection)
    async def trading_field() -> TradingFieldProjection:
        return TradingFieldProjection.model_validate(runtime.trading_field())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_trading_routes(base_api.create_app(config))


app = attach_trading_routes(base_api.app)
