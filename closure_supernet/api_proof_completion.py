from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_continuation as base_api
from .config import RuntimeConfig
from .proof_completion_models import (
    AdmissionCreate,
    BalanceCreate,
    DerivationCreate,
    ProofFieldProjection,
    ProofReceipt,
    ProofSystem,
    ProofSystemCreate,
)
from .proof_completion_web import PROOF_COMPLETION_HTML


def attach_proof_completion_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "proof_completion_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.proof_completion_routes_attached = True
    app.version = "3.3.0"
    app.description += (
        "; NRRF811 adds proof-bearing depth beneath completion: finite Deriv data "
        "abstracts to proposition-level Admits, reciprocal proof gives Balance, "
        "the balance quotient is the meta abstraction object, and every visible "
        "completion remains reversible to concrete proof witnesses"
    )

    @app.get(
        "/proof-completion",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    async def proof_completion_interface() -> str:
        return PROOF_COMPLETION_HTML

    @app.get("/network/proofs/capabilities")
    async def proof_completion_capabilities() -> dict[str, Any]:
        return runtime.proof_completion.capabilities()

    @app.post("/network/proofs/systems", response_model=ProofSystem)
    async def create_proof_system(data: ProofSystemCreate) -> ProofSystem:
        try:
            return ProofSystem.model_validate(
                await runtime.proof_completion.create_system(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/proofs/systems", response_model=list[ProofSystem])
    async def list_proof_systems(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[ProofSystem]:
        return [
            ProofSystem.model_validate(item)
            for item in runtime.proof_completion_store.list_systems(limit)
        ]

    @app.get("/network/proofs/systems/{system_id}", response_model=ProofSystem)
    async def get_proof_system(system_id: str) -> ProofSystem:
        try:
            return ProofSystem.model_validate(
                runtime.proof_completion_store.get_system(system_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/network/proofs/systems/{system_id}/derivation")
    async def derivation_witness(
        system_id: str,
        source: Annotated[str, Query(min_length=1)],
        target: Annotated[str, Query(min_length=1)],
    ) -> dict[str, Any]:
        try:
            return runtime.proof_completion.derivation_witness(
                system_id, source, target
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/proofs/systems/{system_id}/derivations",
        response_model=ProofReceipt,
    )
    async def create_derivation(
        system_id: str, data: DerivationCreate
    ) -> ProofReceipt:
        try:
            return ProofReceipt.model_validate(
                await runtime.proof_completion.create_derivation(system_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/proofs/systems/{system_id}/admission")
    async def admission_witness(
        system_id: str,
        seeds: Annotated[list[str], Query(min_length=1)],
    ) -> dict[str, Any]:
        try:
            return runtime.proof_completion.admission_witness(system_id, seeds)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/proofs/systems/{system_id}/admissions",
        response_model=ProofReceipt,
    )
    async def create_admission(
        system_id: str, data: AdmissionCreate
    ) -> ProofReceipt:
        try:
            return ProofReceipt.model_validate(
                await runtime.proof_completion.create_admission(system_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/proofs/systems/{system_id}/balance")
    async def balance_witness(
        system_id: str,
        left: Annotated[str, Query(min_length=1)],
        right: Annotated[str, Query(min_length=1)],
    ) -> dict[str, Any]:
        try:
            return runtime.proof_completion.balance_witness(
                system_id, left, right
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/proofs/systems/{system_id}/balances",
        response_model=ProofReceipt,
    )
    async def create_balance(
        system_id: str, data: BalanceCreate
    ) -> ProofReceipt:
        try:
            return ProofReceipt.model_validate(
                await runtime.proof_completion.create_balance(system_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/proofs/receipts", response_model=list[ProofReceipt])
    async def list_proof_receipts(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
        system_id: str | None = None,
        kind: str | None = None,
    ) -> list[ProofReceipt]:
        return [
            ProofReceipt.model_validate(item)
            for item in runtime.proof_completion_store.list_receipts(
                limit, system_id=system_id, kind=kind
            )
        ]

    @app.get("/network/proofs/receipts/{receipt_id}", response_model=ProofReceipt)
    async def get_proof_receipt(receipt_id: str) -> ProofReceipt:
        try:
            return ProofReceipt.model_validate(
                runtime.proof_completion_store.get_receipt(receipt_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/network/proofs/canonical-qg")
    async def canonical_qg() -> dict[str, Any]:
        return runtime.proof_completion.projection()["canonical_qg"]

    @app.post(
        "/network/turing-being/life-events/{life_event_id}/proof-completion",
        response_model=ProofSystem,
    )
    async def prove_turing_being_life(
        life_event_id: str,
        authored_by: str = "participant",
    ) -> ProofSystem:
        try:
            return ProofSystem.model_validate(
                await runtime.proof_completion.create_from_turing_being(
                    life_event_id, authored_by=authored_by
                )
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/proofs/field",
        response_model=ProofFieldProjection,
    )
    async def proof_completion_field() -> ProofFieldProjection:
        return ProofFieldProjection.model_validate(
            runtime.proof_completion_field()
        )

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_proof_completion_routes(base_api.create_app(config))


app = attach_proof_completion_routes(base_api.app)
