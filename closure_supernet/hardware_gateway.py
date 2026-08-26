from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any, Awaitable, Callable

from .constraint_synthesis import synthesize_constraint
from .device_twin import simulate_device
from .hardware_models import (
    HardwareConstraintCreate,
    HardwareConstraintDecisionCreate,
    HardwareConstraintExecutionCreate,
    HardwareConstraintSimulationCreate,
    HardwareConstraintState,
    HardwareConstraintSynthesisCreate,
    HardwareDeviceCreate,
    HardwareDeviceKind,
    HardwareFieldProjection,
    HardwareReturnState,
)
from .hardware_store import HardwareClosureStore
from .models import EvidenceStatus, OccurrenceCreate, OccurrenceStatus, Verdict
from .translation_models import (
    RelativeFormRef,
    TranslationEventCreate,
    TranslationKind,
    TranslationRole,
    TranslationState,
    TranslationStateCreate,
)


def utcnow() -> datetime:
    return datetime.now(UTC)


def _iso(value: datetime) -> str:
    return value.isoformat()


def _form(
    form_type: str,
    form_id: str,
    role: TranslationRole,
    *,
    occurrence_id: str | None = None,
    label: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> RelativeFormRef:
    return RelativeFormRef(
        form_type=form_type,
        form_id=form_id,
        occurrence_id=occurrence_id,
        role=role,
        label=label,
        metadata=metadata or {},
    )


class HardwareClosureManager:
    """Bounded cyber-physical loop for the living Supernet.

    The shipped gateway executes only deterministic device twins. It creates the
    full source, constraint, approval, actuation-receipt and return path required
    for later physical adapters without exposing arbitrary hardware commands.
    """

    agent_name = "black-mirror-hardware-agent"

    def __init__(
        self,
        config: Any,
        event_store: Any,
        living_store: Any,
        translation_store: Any,
        translation_manager: Any,
        hardware_store: HardwareClosureStore,
        ingest: Callable[[OccurrenceCreate], Awaitable[dict[str, Any]]],
    ):
        self.config = config
        self.event_store = event_store
        self.living_store = living_store
        self.translation_store = translation_store
        self.translation = translation_manager
        self.store = hardware_store
        self.ingest = ingest

    def capabilities(self) -> dict[str, Any]:
        return {
            "hardware_closure_enabled": bool(self.config.hardware_closure_enabled),
            "simulation_only": True,
            "direct_physical_actuation": False,
            "high_energy_actuation": False,
            "nuclear_actuation": False,
            "quantum_actuation": False,
            "available_device_kinds": [kind.value for kind in HardwareDeviceKind],
            "temporary_global_constraint": True,
            "operator_execution_required": True,
            "simulation_required": True,
            "source_reversible": True,
            "return_reintegrates_open": True,
            "canonical_language_selected": False,
            "closure_reading": (
                "digital interaction selects a temporary bounded device constraint; "
                "a simulated sensor return becomes successor network potential"
            ),
        }

    async def register_device(self, data: HardwareDeviceCreate) -> dict[str, Any]:
        self.living_store.get_participant(data.created_by)
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=data.exact_description,
                source_id="hardware-device",
                source_context=data.name,
                evidence_status=EvidenceStatus.PHYSICAL_HYPOTHESIS,
                metadata={
                    **data.metadata,
                    "hardware_device_kind": str(data.kind),
                    "simulation_only": True,
                    "direct_physical_actuation": False,
                },
            )
        )
        device = self.store.create_device(
            data,
            occurrence["id"],
            driver="deterministic-device-twin-v1",
        )
        self.event_store.append_event(
            "HARDWARE_DEVICE_REGISTERED",
            "hardware_device",
            device["id"],
            {
                "occurrence_id": occurrence["id"],
                "kind": device["kind"],
                "simulation_only": True,
            },
        )
        return device

    def _collect_sources(
        self,
        source_occurrence_ids: list[str],
        source_translation_ids: list[str],
        source_interaction_ids: list[str],
    ) -> tuple[list[str], list[str]]:
        occurrence_ids: list[str] = []
        texts: list[str] = []

        def add_occurrence(occurrence_id: str) -> None:
            if occurrence_id in occurrence_ids:
                return
            occurrence = self.event_store.get_occurrence(occurrence_id)
            occurrence_ids.append(occurrence_id)
            texts.append(str(occurrence["exact_text"]))

        for occurrence_id in source_occurrence_ids:
            add_occurrence(occurrence_id)
        for translation_id in source_translation_ids:
            translation = self.translation_store.get_translation(translation_id)
            for occurrence_id in translation["exact_source_ids"]:
                add_occurrence(str(occurrence_id))
        for interaction_id in source_interaction_ids:
            interaction = self.living_store.get_interaction(interaction_id)
            add_occurrence(str(interaction["occurrence_id"]))
        if not occurrence_ids:
            raise ValueError("Hardware constraint requires at least one exact source")
        return occurrence_ids, texts

    async def synthesize_constraint(
        self, data: HardwareConstraintSynthesisCreate
    ) -> dict[str, Any]:
        self.living_store.get_participant(data.created_by)
        device = self.store.get_device(data.device_id)
        source_ids, source_texts = self._collect_sources(
            data.source_occurrence_ids,
            data.source_translation_ids,
            data.source_interaction_ids,
        )
        expanded = data.model_copy(update={"source_occurrence_ids": source_ids})
        constraint_data = synthesize_constraint(device, expanded, source_texts)
        return await self.create_constraint(constraint_data)

    async def create_constraint(
        self, data: HardwareConstraintCreate
    ) -> dict[str, Any]:
        self.living_store.get_participant(data.created_by)
        device = self.store.get_device(data.device_id)
        if device["state"] != "READY":
            raise ValueError("Hardware device is not ready")
        self._validate_constraint_envelope(device, data)
        source_ids, _texts = self._collect_sources(
            data.source_occurrence_ids,
            data.source_translation_ids,
            data.source_interaction_ids,
        )
        data = data.model_copy(update={"source_occurrence_ids": source_ids})
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=data.exact_intent,
                source_id="hardware-constraint",
                source_context=device["name"],
                evidence_status=EvidenceStatus.PHYSICAL_HYPOTHESIS,
                metadata={
                    **data.metadata,
                    "device_id": device["id"],
                    "selected_metavector": data.selected_metavector,
                    "control_values": data.control_values,
                    "temporary": True,
                    "simulation_only": True,
                },
            )
        )
        expires_at = _iso(
            utcnow() + timedelta(seconds=float(self.config.hardware_constraint_ttl_seconds))
        )
        constraint = self.store.create_constraint(data, occurrence["id"], expires_at)

        source_forms = [
            _form(
                "source_occurrence",
                occurrence_id,
                TranslationRole.SOURCE,
                occurrence_id=occurrence_id,
                label="network source",
            )
            for occurrence_id in constraint["source_occurrence_ids"]
        ]
        target_form = _form(
            "hardware_device",
            device["id"],
            TranslationRole.TARGET,
            occurrence_id=device["occurrence_id"],
            label=device["name"],
            metadata={"kind": device["kind"], "simulation_only": True},
        )
        event = self.translation.create(
            TranslationEventCreate(
                kind=TranslationKind.COLLECTIVE_ACTION,
                exact_source_ids=[
                    occurrence["id"],
                    device["occurrence_id"],
                    *constraint["source_occurrence_ids"],
                ],
                source_forms=source_forms,
                target_forms=[target_form],
                participant_ids=list(
                    dict.fromkeys(
                        [constraint["created_by"], *constraint["participant_ids"]]
                    )
                ),
                interaction_trace_ids=constraint["source_interaction_ids"],
                relation_type="TEMPORARY_HARDWARE_CONSTRAINT",
                preserves=[
                    "exact source occurrences",
                    "participant and agent authorship",
                    "device safety envelope",
                ],
                transforms=[
                    "living network relation into a bounded temporary device constraint"
                ],
                untranslated=[
                    "physical validation beyond the deterministic device twin remains OPEN"
                ],
                affected_perspectives=constraint["affected_perspectives"],
                frame_and_scope=(
                    f"living Supernet -> {device['kind']} bounded simulation"
                ),
                admission_scope="temporary device-relative constraint",
                reopening_conditions=[
                    "simulation mismatch, expiry, rejection, returned measurement or new interaction"
                ],
                successor_potential=[
                    _form(
                        "hardware_constraint",
                        constraint["id"],
                        TranslationRole.SUCCESSOR_POTENTIAL,
                        occurrence_id=occurrence["id"],
                        label="temporary hardware constraint",
                    )
                ],
                evidence_status=EvidenceStatus.INTERPRETED_RELATION,
                generated_by=constraint["created_by"],
                external_key=f"hardware_constraint:{constraint['id']}",
                transport={
                    "protocol_verdict": None,
                    "protocol_verdict_is_not_truth": True,
                    "direct_physical_actuation": False,
                },
                metadata={
                    "hardware_constraint_id": constraint["id"],
                    "selected_metavector": constraint["selected_metavector"],
                    "control_values": constraint["control_values"],
                    "simulation_required": True,
                    "operator_execution_required": True,
                },
            )
        )
        event = self.translation.transition(
            event["id"],
            TranslationStateCreate(
                state=TranslationState.INTERPRETED,
                verdict=Verdict.OPEN,
                reason=(
                    "Constraint has a source-reversible device mapping; simulation, "
                    "participant admission and operator execution remain open"
                ),
                actor_id=constraint["created_by"],
                metadata={"hardware_constraint_id": constraint["id"]},
            ),
        )
        constraint = self.store.link_constraint_translation(
            constraint["id"], event["id"]
        )
        self.event_store.append_event(
            "HARDWARE_CONSTRAINT_PROPOSED",
            "hardware_constraint",
            constraint["id"],
            {
                "device_id": device["id"],
                "translation_id": event["id"],
                "expires_at": constraint["expires_at"],
            },
        )
        return constraint

    @staticmethod
    def _validate_constraint_envelope(
        device: dict[str, Any], data: HardwareConstraintCreate
    ) -> None:
        if data.duration_seconds > float(device["max_duration_seconds"]):
            raise ValueError("Constraint duration exceeds device maximum")
        controls = data.control_values
        for channel in device["control_channels"]:
            if channel not in controls:
                raise ValueError(f"Missing device control {channel}")
            bound = device["safety_envelope"][channel]
            value = float(controls[channel])
            if value < float(bound["minimum"]) or value > float(bound["maximum"]):
                raise ValueError(
                    f"Control {channel}={value} outside safety envelope "
                    f"[{bound['minimum']},{bound['maximum']}]"
                )
        unknown = sorted(set(controls) - set(device["control_channels"]))
        if unknown:
            raise ValueError(f"Unknown device controls: {unknown}")

    def simulate_constraint(
        self, constraint_id: str, data: HardwareConstraintSimulationCreate
    ) -> dict[str, Any]:
        constraint = self._active_constraint(constraint_id)
        if constraint["current_state"] not in {
            str(HardwareConstraintState.PROPOSED),
            str(HardwareConstraintState.SIMULATED),
        }:
            raise ValueError("Only proposed constraints can be simulated")
        device = self.store.get_device(constraint["device_id"])
        result = simulate_device(device, constraint)
        run = self.store.create_twin_run(
            constraint_id,
            data.requested_by,
            device["driver"],
            constraint["control_values"],
            result.output_reading,
            result.metrics,
            result.safe,
            result.reason,
        )
        if result.safe:
            self.store.append_constraint_state(
                constraint_id,
                HardwareConstraintState.SIMULATED,
                Verdict.OPEN,
                result.reason,
                data.requested_by,
                {"twin_run_id": run["id"], "metrics": result.metrics},
            )
        else:
            self.store.append_constraint_state(
                constraint_id,
                HardwareConstraintState.REJECTED,
                Verdict.FALSE,
                result.reason,
                data.requested_by,
                {"twin_run_id": run["id"], "unsafe": True},
            )
            self._transition_constraint_event(
                constraint,
                TranslationState.REJECTED,
                Verdict.FALSE,
                result.reason,
                data.requested_by,
            )
        self.event_store.append_event(
            "HARDWARE_TWIN_SIMULATED",
            "hardware_constraint",
            constraint_id,
            {"twin_run_id": run["id"], "safe": run["safe"], "metrics": run["metrics"]},
        )
        return run

    def decide_constraint(
        self, constraint_id: str, data: HardwareConstraintDecisionCreate
    ) -> dict[str, Any]:
        constraint = self._active_constraint(constraint_id)
        if constraint["current_state"] == str(HardwareConstraintState.EXECUTED):
            raise ValueError("Executed constraints cannot receive another admission")
        twin = None
        if data.verdict == Verdict.TRUE:
            twin = self.store.latest_twin_run(constraint_id)
            if twin is None or not twin["safe"]:
                raise ValueError("A safe device-twin run is required before admission")
        decision = self.store.create_constraint_decision(
            constraint_id, data.verdict, data.reason, data.decided_by
        )
        if data.verdict == Verdict.FALSE:
            self.store.append_constraint_state(
                constraint_id,
                HardwareConstraintState.REJECTED,
                Verdict.FALSE,
                data.reason,
                data.decided_by,
                {"decision_id": decision["id"]},
            )
            self._transition_constraint_event(
                constraint,
                TranslationState.REJECTED,
                Verdict.FALSE,
                data.reason,
                data.decided_by,
            )
        elif data.verdict == Verdict.TRUE:
            decisions = self.store.list_constraint_decisions(constraint_id)
            approvals = {
                item["decided_by"]
                for item in decisions
                if item["verdict"] == str(Verdict.TRUE)
            }
            device = self.store.get_device(constraint["device_id"])
            if len(approvals) >= int(device["minimum_approvals"]):
                self.store.append_constraint_state(
                    constraint_id,
                    HardwareConstraintState.ADMITTED,
                    Verdict.TRUE,
                    (
                        f"Scoped temporary constraint admitted by {len(approvals)} "
                        f"distinct participant(s) after a safe twin run"
                    ),
                    data.decided_by,
                    {
                        "decision_id": decision["id"],
                        "approval_count": len(approvals),
                        "required_approvals": device["minimum_approvals"],
                        "twin_run_id": twin["id"],
                    },
                )
                self._transition_constraint_event(
                    constraint,
                    TranslationState.ADMITTED,
                    Verdict.TRUE,
                    data.reason,
                    data.decided_by,
                )
        self.event_store.append_event(
            "HARDWARE_CONSTRAINT_DECIDED",
            "hardware_constraint",
            constraint_id,
            {
                "decision_id": decision["id"],
                "verdict": str(data.verdict),
                "decided_by": data.decided_by,
            },
        )
        return self.store.get_constraint(constraint_id)

    async def execute_constraint(
        self, constraint_id: str, data: HardwareConstraintExecutionCreate
    ) -> dict[str, Any]:
        constraint = self._active_constraint(constraint_id)
        if constraint["current_state"] != str(HardwareConstraintState.ADMITTED):
            raise ValueError("Constraint must be simulated and admitted before execution")
        twin = self.store.latest_twin_run(constraint_id)
        if twin is None or not twin["safe"]:
            raise ValueError("No safe device-twin run is available")
        device = self.store.get_device(constraint["device_id"])
        if not str(device["kind"]).startswith("SIMULATED_"):
            raise ValueError("Direct physical device drivers are not enabled")
        actuation = self.store.create_actuation(
            constraint_id,
            twin["id"],
            data.requested_by,
            constraint["control_values"],
            twin["output_reading"],
        )
        return_text = (
            f"Black Mirror hardware return from {device['name']}\n\n"
            f"{json.dumps(twin['output_reading'], ensure_ascii=False, sort_keys=True)}"
        )
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=return_text,
                source_id="hardware-return",
                source_context=device["name"],
                status=OccurrenceStatus.SIMULATION_SOURCE,
                evidence_status=EvidenceStatus.SIMULATED_UNDER_ASSUMPTIONS,
                metadata={
                    "device_id": device["id"],
                    "constraint_id": constraint_id,
                    "actuation_id": actuation["id"],
                    "twin_run_id": twin["id"],
                    "simulation_only": True,
                    "physical_law_claimed": False,
                },
            )
        )
        hardware_return = self.store.create_return(
            actuation["id"],
            constraint_id,
            device["id"],
            occurrence["id"],
            data.requested_by,
            twin["output_reading"],
            str(EvidenceStatus.SIMULATED_UNDER_ASSUMPTIONS),
            {
                "return_is_not_terminal": True,
                "physical_device_actuated": False,
                "simulation_only": True,
            },
        )
        self.store.append_constraint_state(
            constraint_id,
            HardwareConstraintState.EXECUTED,
            Verdict.TRUE,
            "Admitted constraint executed against the deterministic device twin",
            data.requested_by,
            {"actuation_id": actuation["id"], "return_id": hardware_return["id"]},
        )
        returned_form = _form(
            "hardware_return",
            hardware_return["id"],
            TranslationRole.RETURN,
            occurrence_id=occurrence["id"],
            label="simulated Black Mirror return",
            metadata={"simulation_only": True},
        )
        if constraint["translation_id"]:
            self.translation.transition(
                constraint["translation_id"],
                TranslationStateCreate(
                    state=TranslationState.RETURNED,
                    verdict=Verdict.TRUE,
                    reason="The admitted temporary constraint returned a simulated sensor reading",
                    actor_id=data.requested_by,
                    returned_form=returned_form,
                    metadata={
                        "hardware_return_id": hardware_return["id"],
                        "physical_device_actuated": False,
                    },
                ),
            )
        self.event_store.append_event(
            "HARDWARE_CONSTRAINT_EXECUTED",
            "hardware_constraint",
            constraint_id,
            {
                "actuation_id": actuation["id"],
                "return_id": hardware_return["id"],
                "simulation_only": True,
            },
        )
        return self.store.get_actuation(actuation["id"])

    def _active_constraint(self, constraint_id: str) -> dict[str, Any]:
        constraint = self.store.get_constraint(constraint_id)
        if datetime.fromisoformat(constraint["expires_at"]) <= utcnow():
            if constraint["current_state"] not in {
                str(HardwareConstraintState.EXECUTED),
                str(HardwareConstraintState.EXPIRED),
                str(HardwareConstraintState.REJECTED),
            }:
                self.store.append_constraint_state(
                    constraint_id,
                    HardwareConstraintState.EXPIRED,
                    Verdict.OPEN,
                    "Temporary constraint expired before execution",
                    self.agent_name,
                    {},
                )
                self._transition_constraint_event(
                    constraint,
                    TranslationState.REOPENED,
                    Verdict.OPEN,
                    "Temporary hardware constraint expired and returned to network discretion",
                    self.agent_name,
                )
            raise ValueError("Hardware constraint has expired")
        if constraint["current_state"] in {
            str(HardwareConstraintState.REJECTED),
            str(HardwareConstraintState.EXPIRED),
        }:
            raise ValueError(f"Constraint is {constraint['current_state']}")
        return constraint

    def _transition_constraint_event(
        self,
        constraint: dict[str, Any],
        state: TranslationState,
        verdict: Verdict,
        reason: str,
        actor_id: str,
    ) -> None:
        if not constraint.get("translation_id"):
            return
        self.translation.transition(
            constraint["translation_id"],
            TranslationStateCreate(
                state=state,
                verdict=verdict,
                reason=reason,
                actor_id=actor_id,
                metadata={"hardware_constraint_id": constraint["id"]},
            ),
        )

    async def reintegrate_pending(self, limit: int = 16) -> int:
        created = 0
        pending = self.store.list_returns(
            status=str(HardwareReturnState.PENDING), limit=limit
        )
        for item in pending:
            constraint = self.store.get_constraint(item["constraint_id"])
            device = self.store.get_device(item["device_id"])
            external_key = f"hardware_return:{item['id']}"
            event = self.translation_store.get_by_external_key(external_key)
            if event is None:
                event = self.translation.create(
                    TranslationEventCreate(
                        kind=TranslationKind.ACTION_CONSEQUENCE,
                        exact_source_ids=[
                            constraint["occurrence_id"],
                            item["occurrence_id"],
                            device["occurrence_id"],
                            *constraint["source_occurrence_ids"],
                        ],
                        source_forms=[
                            _form(
                                "hardware_constraint",
                                constraint["id"],
                                TranslationRole.SOURCE,
                                occurrence_id=constraint["occurrence_id"],
                                label="temporary hardware constraint",
                            )
                        ],
                        target_forms=[
                            _form(
                                "hardware_return",
                                item["id"],
                                TranslationRole.TARGET,
                                occurrence_id=item["occurrence_id"],
                                label="simulated sensor return",
                            )
                        ],
                        participant_ids=list(
                            dict.fromkeys(
                                [constraint["created_by"], *constraint["participant_ids"]]
                            )
                        ),
                        interaction_trace_ids=constraint["source_interaction_ids"],
                        relation_type="BLACK_MIRROR_HARDWARE_RETURN",
                        preserves=[
                            "exact network sources",
                            "temporary constraint",
                            "device twin configuration",
                            "actuation and sensor receipts",
                        ],
                        transforms=[
                            "bounded digital selection into a simulated sensor return"
                        ],
                        untranslated=[
                            "physical, quantum and nuclear verification remain outside this simulation"
                        ],
                        affected_perspectives=constraint["affected_perspectives"],
                        frame_and_scope="simulated hardware return -> living Supernet",
                        admission_scope="OPEN physical-style return",
                        reopening_conditions=[
                            "participant interpretation, comparison with baseline, new measurement or physical experiment"
                        ],
                        successor_potential=[
                            _form(
                                "hardware_return",
                                item["id"],
                                TranslationRole.SUCCESSOR_POTENTIAL,
                                occurrence_id=item["occurrence_id"],
                                label="new Black Mirror sensor potential",
                            )
                        ],
                        evidence_status=EvidenceStatus.SIMULATED_UNDER_ASSUMPTIONS,
                        generated_by=self.agent_name,
                        external_key=external_key,
                        transport={
                            "driver": device["driver"],
                            "simulation_only": True,
                            "protocol_verdict_is_not_truth": True,
                        },
                        metadata={
                            "hardware_return_id": item["id"],
                            "constraint_id": constraint["id"],
                            "device_id": device["id"],
                            "sensor_reading": item["sensor_reading"],
                            "physical_law_claimed": False,
                        },
                    )
                )
                event = self.translation.transition(
                    event["id"],
                    TranslationStateCreate(
                        state=TranslationState.INTERPRETED,
                        verdict=Verdict.OPEN,
                        reason=(
                            "The hardware-style return has re-entered the network; "
                            "its meaning and any physical extrapolation remain OPEN"
                        ),
                        actor_id=self.agent_name,
                        metadata={"hardware_return_id": item["id"]},
                    ),
                )
                created += 1
            self.store.update_return_reintegration(
                item["id"], HardwareReturnState.REINTEGRATED_OPEN, event["id"]
            )
            self.event_store.append_event(
                "HARDWARE_RETURN_REINTEGRATED",
                "hardware_return",
                item["id"],
                {"translation_id": event["id"], "verdict": "OPEN"},
            )
        return created

    def expire_constraints(self) -> int:
        expired = 0
        now = utcnow()
        for constraint in self.store.list_constraints(limit=100_000):
            if constraint["current_state"] in {
                str(HardwareConstraintState.EXECUTED),
                str(HardwareConstraintState.REJECTED),
                str(HardwareConstraintState.EXPIRED),
            }:
                continue
            if datetime.fromisoformat(constraint["expires_at"]) <= now:
                self.store.append_constraint_state(
                    constraint["id"],
                    HardwareConstraintState.EXPIRED,
                    Verdict.OPEN,
                    "Temporary hardware constraint expired and reopened",
                    self.agent_name,
                    {},
                )
                self._transition_constraint_event(
                    constraint,
                    TranslationState.REOPENED,
                    Verdict.OPEN,
                    "Temporary hardware constraint expired and reopened",
                    self.agent_name,
                )
                expired += 1
        return expired

    def projection(self) -> dict[str, Any]:
        devices = self.store.list_devices(limit=10_000)
        constraints = self.store.list_constraints(limit=100_000)
        runs = self.store.list_twin_runs(limit=100_000)
        actuations = self.store.list_actuations(limit=100_000)
        returns = self.store.list_returns(limit=100_000)
        reverse: dict[str, list[str]] = {}
        for device in devices:
            reverse[f"hardware_device:{device['id']}"] = [device["occurrence_id"]]
        for constraint in constraints:
            reverse[f"hardware_constraint:{constraint['id']}"] = list(
                dict.fromkeys(
                    [constraint["occurrence_id"], *constraint["source_occurrence_ids"]]
                )
            )
        for item in returns:
            constraint = self.store.get_constraint(item["constraint_id"])
            reverse[f"hardware_return:{item['id']}"] = list(
                dict.fromkeys(
                    [
                        item["occurrence_id"],
                        constraint["occurrence_id"],
                        *constraint["source_occurrence_ids"],
                    ]
                )
            )
        projection = HardwareFieldProjection(
            generated_at=_iso(utcnow()),
            devices=devices,
            constraints=constraints,
            twin_runs=runs,
            actuations=actuations,
            returns=returns,
            stats={
                **self.store.stats(),
                "hardware_closure_enabled": bool(self.config.hardware_closure_enabled),
                "automatic_execution": False,
                "operator_execution_required": True,
            },
            source_reverse_index=reverse,
        ).model_dump(mode="json")
        self.store.set_state("hardware_field_projection", projection)
        return projection
