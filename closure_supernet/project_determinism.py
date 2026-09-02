from __future__ import annotations

"""Mount the deterministic full-project closure on the one published runtime."""

from typing import Any, Mapping

from fastapi import FastAPI

from .project_closure import (
    cached_project_closure_certificate,
    validate_project_closure_certificate,
)


def _route_endpoint(app: FastAPI, path: str, method: str) -> Any:
    for route in app.router.routes:
        methods = getattr(route, "methods", set()) or set()
        if getattr(route, "path", None) == path and method in methods:
            return route.endpoint
    raise RuntimeError(f"missing route: {method} {path}")


def _remove_route(app: FastAPI, path: str, method: str) -> None:
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if not (
            getattr(route, "path", None) == path
            and method in (getattr(route, "methods", set()) or set())
        )
    ]


def _public_fields(certificate: Mapping[str, Any]) -> dict[str, Any]:
    checks = certificate.get("checks") or {}
    return {
        "project_closure_id": certificate.get("id"),
        "project_source_tree_identity_id": certificate.get(
            "source_tree_identity_id"
        ),
        "project_semantic_identity_id": certificate.get(
            "semantic_identity_id"
        ),
        "project_closure_status": certificate.get("status"),
        "project_closed": certificate.get("project_closed") is True,
        "project_coverage": certificate.get("coverage"),
        "project_file_count": certificate.get("file_count"),
        "project_python_module_count": certificate.get(
            "python_module_count"
        ),
        "project_role_counts": dict(certificate.get("role_counts") or {}),
        "full_project_deterministic": True,
        "all_project_files_classified_exactly_once": checks.get(
            "all_project_files_classified_exactly_once"
        )
        is True,
        "all_public_mutations_factor_through_supernet_translate": checks.get(
            "runtime_agent_and_self_share_one_operator"
        )
        is True,
        "compatibility_modules_are_non_authoritative": (
            checks.get(
                "historical_surfaces_are_classified_non_authoritative"
            )
            is True
            and checks.get(
                "historical_surfaces_are_not_direct_public_entrypoints"
            )
            is True
        ),
        "same_source_tree_same_project_identity": True,
        "project_certificate_authors_truth": False,
    }


def attach_deterministic_project_closure(app: FastAPI) -> FastAPI:
    """Close every retained project file around the one runtime authority."""

    if getattr(app.state, "deterministic_project_closure_attached", False):
        return app

    certificate = cached_project_closure_certificate()
    validation = validate_project_closure_certificate(certificate)
    if validation.get("valid") is not True:
        raise RuntimeError(
            "Deterministic project closure failed: "
            + ", ".join(validation.get("errors") or ["unknown"])
        )

    app.state.deterministic_project_closure_attached = True
    app.state.supernet_project_closure = certificate
    app.state.supernet_project_closure_validation = validation
    fields = _public_fields(certificate)

    interface_capabilities = _route_endpoint(
        app,
        "/supernet/interface/capabilities",
        "GET",
    )
    _remove_route(app, "/supernet/interface/capabilities", "GET")

    @app.get("/supernet/interface/capabilities")
    async def project_closed_interface_capabilities() -> dict[str, Any]:
        base = dict(await interface_capabilities())
        base.update(fields)
        return base

    agent_capabilities = _route_endpoint(
        app,
        "/supernet/agent/capabilities",
        "GET",
    )
    _remove_route(app, "/supernet/agent/capabilities", "GET")

    @app.get("/supernet/agent/capabilities")
    async def project_closed_agent_capabilities() -> dict[str, Any]:
        base = dict(await agent_capabilities())
        base.update(fields)
        return base

    self_runtime = _route_endpoint(app, "/supernet/agent/self", "GET")
    _remove_route(app, "/supernet/agent/self", "GET")

    @app.get("/supernet/agent/self")
    async def project_closed_self_runtime(
        perspective_id: str = "runtime:self",
        focus_event_id: str | None = None,
    ) -> dict[str, Any]:
        base = dict(
            await self_runtime(
                perspective_id=perspective_id,
                focus_event_id=focus_event_id,
            )
        )
        base.update(fields)
        return base

    return app


__all__ = [
    "attach_deterministic_project_closure",
]
