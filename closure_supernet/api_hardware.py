from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_production as base_api
from .config import RuntimeConfig
from .hardware_models import (
    HardwareActuationReceipt,
    HardwareConstraint,
    HardwareConstraintDecisionCreate,
    HardwareConstraintExecutionCreate,
    HardwareConstraintSimulationCreate,
    HardwareConstraintSynthesisCreate,
    HardwareDevice,
    HardwareDeviceCreate,
    HardwareFieldProjection,
    HardwareReturn,
    HardwareTwinRun,
)
from .hardware_web import HARDWARE_CLOSURE_HTML


def attach_hardware_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "hardware_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.hardware_routes_attached = True
    app.version = "0.9.0"
    app.description += (
        "; adds a bounded Black Mirror hardware closure loop with deterministic "
        "optical/sensor device twins, temporary network constraints, scoped "
        "admission, simulated actuation receipts, and OPEN physical-return reintegration"
    )

    @app.get("/hardware", response_class=HTMLResponse, include_in_schema=False)
    async def hardware_interface() -> str:
        return HARDWARE_CLOSURE_HTML

    @app.get("/network/hardware/capabilities")
    async def hardware_capabilities() -> dict[str, Any]:
        return runtime.hardware.capabilities()

    @app.get("/network/hardware/devices", response_model=list[HardwareDevice])
    async def list_hardware_devices(
        limit: Annotated[int, Query(ge=1, le=10_000)] = 1000,
    ) -> list[HardwareDevice]:
        return [
            HardwareDevice.model_validate(row)
            for row in runtime.hardware_store.list_devices(limit)
        ]

    @app.post("/admin/hardware/devices", response_model=HardwareDevice)
    async def register_hardware_device(data: HardwareDeviceCreate) -> HardwareDevice:
        try:
            return HardwareDevice.model_validate(await runtime.hardware.register_device(data))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/hardware/constraints/synthesize",
        response_model=HardwareConstraint,
    )
    async def synthesize_hardware_constraint(
        data: HardwareConstraintSynthesisCreate,
    ) -> HardwareConstraint:
        try:
            return HardwareConstraint.model_validate(
                await runtime.hardware.synthesize_constraint(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/hardware/constraints", response_model=list[HardwareConstraint])
    async def list_hardware_constraints(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[HardwareConstraint]:
        return [
            HardwareConstraint.model_validate(row)
            for row in runtime.hardware_store.list_constraints(limit)
        ]

    @app.get(
        "/network/hardware/constraints/{constraint_id}",
        response_model=HardwareConstraint,
    )
    async def get_hardware_constraint(constraint_id: str) -> HardwareConstraint:
        try:
            return HardwareConstraint.model_validate(
                runtime.hardware_store.get_constraint(constraint_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/hardware/constraints/{constraint_id}/simulate",
        response_model=HardwareTwinRun,
    )
    async def simulate_hardware_constraint(
        constraint_id: str, data: HardwareConstraintSimulationCreate
    ) -> HardwareTwinRun:
        try:
            return HardwareTwinRun.model_validate(
                runtime.hardware.simulate_constraint(constraint_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/hardware/constraints/{constraint_id}/decision",
        response_model=HardwareConstraint,
    )
    async def decide_hardware_constraint(
        constraint_id: str, data: HardwareConstraintDecisionCreate
    ) -> HardwareConstraint:
        try:
            return HardwareConstraint.model_validate(
                runtime.hardware.decide_constraint(constraint_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/admin/hardware/constraints/{constraint_id}/execute",
        response_model=HardwareActuationReceipt,
    )
    async def execute_hardware_constraint(
        constraint_id: str, data: HardwareConstraintExecutionCreate
    ) -> HardwareActuationReceipt:
        try:
            return HardwareActuationReceipt.model_validate(
                await runtime.hardware.execute_constraint(constraint_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/hardware/twin-runs", response_model=list[HardwareTwinRun])
    async def list_hardware_twin_runs(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[HardwareTwinRun]:
        return [
            HardwareTwinRun.model_validate(row)
            for row in runtime.hardware_store.list_twin_runs(limit)
        ]

    @app.get(
        "/network/hardware/actuations", response_model=list[HardwareActuationReceipt]
    )
    async def list_hardware_actuations(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[HardwareActuationReceipt]:
        return [
            HardwareActuationReceipt.model_validate(row)
            for row in runtime.hardware_store.list_actuations(limit)
        ]

    @app.get("/network/hardware/returns", response_model=list[HardwareReturn])
    async def list_hardware_returns(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[HardwareReturn]:
        return [
            HardwareReturn.model_validate(row)
            for row in runtime.hardware_store.list_returns(limit=limit)
        ]

    @app.post("/admin/hardware/reintegrate")
    async def reintegrate_hardware_returns() -> dict[str, Any]:
        reintegrated = await runtime.hardware.reintegrate_pending(
            runtime.config.hardware_reintegrations_per_cycle
        )
        projection = runtime.hardware.projection()
        runtime.projection.run()
        return {"reintegrated": reintegrated, "field": projection}

    @app.get("/network/hardware/field", response_model=HardwareFieldProjection)
    async def hardware_field() -> HardwareFieldProjection:
        return HardwareFieldProjection.model_validate(runtime.hardware_field())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_hardware_routes(base_api.create_app(config))


app = attach_hardware_routes(base_api.app)
