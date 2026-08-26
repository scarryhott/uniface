from __future__ import annotations

from typing import Any

from .models import EvidenceStatus, Verdict
from .resource_protocol import LiveResourceProtocolManager
from .resource_store import ResourceStore
from .runtime import ClosureSupernetRuntime
from .translation_models import (
    RelativeFormRef,
    TranslationEventCreate,
    TranslationKind,
    TranslationRole,
    TranslationState,
    TranslationStateCreate,
)


_PATCHED = False


def _form(resource: dict[str, Any], role: TranslationRole) -> RelativeFormRef:
    return RelativeFormRef(
        form_type="resource",
        form_id=resource["id"],
        occurrence_id=resource["occurrence_id"],
        role=role,
        label=resource["form_label"],
        metadata={
            "language_label": resource["language_label"],
            "capabilities": resource["capabilities"],
            "constraints": resource["constraints"],
            "resource_form_is_open": True,
        },
    )


def install_resource_runtime() -> None:
    """Layer the resource continuum onto the canonical TranslationEvent field."""

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_init = ClosureSupernetRuntime.__init__
    original_cycle = ClosureSupernetRuntime.cycle
    original_status = ClosureSupernetRuntime.status
    original_black_mirror = ClosureSupernetRuntime.black_mirror
    original_close = ClosureSupernetRuntime.close

    def init(self: ClosureSupernetRuntime, config=None) -> None:
        original_init(self, config)
        self.resource_store = ResourceStore(self.config.database_path)
        self.resource_protocol = LiveResourceProtocolManager(
            self.config,
            self.store,
            self.living_store,
            self.resource_store,
            self.ingest,
        )

        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            resources = self.resource_protocol.projection()
            projection["live_resource_protocol"] = {
                "stats": resources["stats"],
                "source_reverse_index": resources["source_reverse_index"],
                "current_stage": resources["current_stage"],
                "protocol_is_translational_truth": False,
                "canonical_language": None,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

        living_projection = self.living.field_projection

        def combined_living_projection(black_mirror: dict[str, Any]) -> dict[str, Any]:
            projection = living_projection(black_mirror)
            resources = self.resource_protocol.projection()
            projection["live_resource_protocol"] = resources
            projection["stats"].update(
                {
                    "resources": resources["stats"]["resources"],
                    "resource_engagements": resources["stats"]["engagements"],
                    "resource_translations": resources["stats"]["translations"],
                    "resource_returns": resources["stats"]["returns"],
                    "resource_natural_components": resources["stats"][
                        "natural_components"
                    ],
                    "resource_protocol_is_truth": False,
                    "finite_resource_registry": False,
                    "canonical_resource_language": None,
                }
            )
            projection["source_reverse_index"].update(
                resources["source_reverse_index"]
            )
            return projection

        self.living.field_projection = combined_living_projection

    def reconcile_resource_translations(self: ClosureSupernetRuntime) -> int:
        changed = 0
        desired_state = {
            str(Verdict.OPEN): TranslationState.INTERPRETED,
            str(Verdict.TRUE): TranslationState.ADMITTED,
            str(Verdict.FALSE): TranslationState.REJECTED,
        }
        for item in self.resource_store.list_translations(limit=100_000):
            external_key = f"resource_translation:{item['id']}"
            canonical = self.translation_store.get_by_external_key(external_key)
            source = self.resource_store.get_resource(item["source_resource_id"])
            target = self.resource_store.get_resource(item["target_resource_id"])
            if canonical is None:
                kind = (
                    TranslationKind.LANGUAGE_TRANSLATION
                    if item["source_language"] != item["target_language"]
                    else TranslationKind.FRAME_TRANSLATION
                )
                canonical = self.translation.create(
                    TranslationEventCreate(
                        kind=kind,
                        exact_source_ids=[
                            source["occurrence_id"],
                            target["occurrence_id"],
                            item["occurrence_id"],
                        ],
                        source_forms=[_form(source, TranslationRole.SOURCE)],
                        target_forms=[_form(target, TranslationRole.TARGET)],
                        participant_ids=[item["authored_by"]],
                        participating_perspective_ids=[
                            value
                            for value in (
                                source["perspective_id"],
                                target["perspective_id"],
                            )
                            if value
                        ],
                        relation_type=item["relation_label"][:200],
                        preserves=item["preserved"],
                        transforms=item["transformed"],
                        untranslated=item["omitted"],
                        affected_perspectives=item["affected_perspectives"],
                        frame_and_scope=(
                            f"{item['source_frame']} -> {item['target_frame']}"
                        ),
                        admission_scope=item["current_scope"],
                        successor_potential=[
                            _form(target, TranslationRole.SUCCESSOR_POTENTIAL)
                        ],
                        evidence_status=EvidenceStatus.INTERPRETED_RELATION,
                        generated_by=item["authored_by"],
                        external_key=external_key,
                        transport={
                            "transport_label": item["transport_label"],
                            "protocol_verdict": item["protocol_verdict"],
                            "protocol_verdict_is_not_truth": True,
                        },
                        metadata={
                            "resource_translation_id": item["id"],
                            "faithfulness": item["faithfulness"],
                            "resource_forms_open": True,
                            "canonical_language_selected": False,
                        },
                    )
                )
                changed += 1
            state = desired_state[item["current_verdict"]]
            if (
                canonical["current_verdict"] != item["current_verdict"]
                or canonical["current_state"] != str(state)
            ):
                canonical = self.translation.transition(
                    canonical["id"],
                    TranslationStateCreate(
                        state=state,
                        verdict=Verdict(item["current_verdict"]),
                        reason=item["current_reason"],
                        actor_id=item["decided_by"],
                        metadata={
                            "resource_translation_id": item["id"],
                            "scope": item["current_scope"],
                            "protocol_verdict": item["protocol_verdict"],
                            "protocol_verdict_is_not_truth": True,
                        },
                    ),
                )
                changed += 1
        return changed

    async def cycle(self: ClosureSupernetRuntime):
        resource_reintegrations = 0
        if self.config.resource_protocol_enabled:
            resource_reintegrations = (
                await self.resource_protocol.reintegrate_pending(
                    self.config.resource_reintegrations_per_cycle
                )
            )
            self.reconcile_resource_translations()
            _stage, stage_created = self.resource_protocol.integrate_live_stage(
                trigger="autonomous-pre-cycle"
            )
        else:
            stage_created = False

        result = await original_cycle(self)
        resources = self.resource_protocol.projection()
        result.resource_reintegrations = resource_reintegrations
        result.resource_stages = int(stage_created)
        result.resources = int(resources["stats"]["resources"])
        result.resource_engagements = int(resources["stats"]["engagements"])
        result.resource_translations = int(resources["stats"]["translations"])
        result.resource_returns = int(resources["stats"]["returns"])
        result.resource_pending_reintegrations = int(
            resources["stats"]["pending_reintegrations"]
        )
        result.resource_natural_components = int(
            resources["stats"]["natural_components"]
        )
        self.store.set_state("last_cycle", result.model_dump(mode="json"))
        return result

    def status(self: ClosureSupernetRuntime):
        base = original_status(self).model_dump(mode="python")
        stats = self.resource_store.stats()
        projection = self.resource_protocol.projection()
        base.update(
            {
                "resources": stats["resources"],
                "resource_engagements": stats["engagements"],
                "resource_translations": stats["translations"],
                "resource_returns": stats["returns"],
                "resource_pending_reintegrations": stats[
                    "pending_reintegrations"
                ],
                "resource_stages": stats["stages"],
                "resource_natural_components": projection["stats"][
                    "natural_components"
                ],
                "resource_protocol_enabled": self.config.resource_protocol_enabled,
            }
        )
        return type(original_status(self))(**base)

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "live_resource_protocol" not in projection:
            resources = self.resource_protocol.projection()
            projection["live_resource_protocol"] = {
                "stats": resources["stats"],
                "source_reverse_index": resources["source_reverse_index"],
                "current_stage": resources["current_stage"],
                "protocol_is_translational_truth": False,
                "canonical_language": None,
            }
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "resource_store"):
            self.resource_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.reconcile_resource_translations = (
        reconcile_resource_translations
    )
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.close = close


install_resource_runtime()
