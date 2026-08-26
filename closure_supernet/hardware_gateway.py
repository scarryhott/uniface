"""Hardware Closure Gateway.

The only path from a collective constraint to a device command.

    admissible as a network interpretation  ≠  authorized as a hardware actuation

Hardware receives u_t = SafetyEnvelope_D(G_t).
Never raw AI output. Never undifferentiated public consensus.
"""

from __future__ import annotations

from datetime import datetime
from typing import Mapping

from .device_twin import NEUTRAL_STATE, SimulatedOpticalEllipseTwin, mapped_controls_for_forms
from .hardware_models import (
    ActuationDecision,
    ActuationReceipt,
    AdmissionKind,
    Clock,
    ConstraintAdmission,
    ConstraintProposal,
    Device,
    DeviceKind,
    DeviceStatus,
    HardwareSafetyPolicy,
    Interaction,
    PhysicalReturn,
    Refusal,
    SAFETY_POLICY_VERSION,
    SafetyEnvelope,
    TemporaryGlobalConstraint,
    UtcClock,
    VerificationRun,
    new_id,
)
from .hardware_store import HardwareStore
from .constraint_synthesis import selected_metavector


def wrap_safety_envelope(
    *,
    constraint: TemporaryGlobalConstraint,
    device: Device,
    approvals: tuple[str, ...],
    required_approvals: tuple[str, ...],
    simulation,
    sequence: int,
    now: datetime,
) -> SafetyEnvelope:
    """u_t = SafetyEnvelope_D(G_t)."""
    mins = {name: lo for name, (lo, _hi) in mapped_controls_for_forms((), device)[0].items()}
    # bounds from device channels
    mins = {c.control_variable: c.min_value for c in device.actuator_channels}
    maxs = {c.control_variable: c.max_value for c in device.actuator_channels}
    mapped = tuple(constraint.G_t.keys())
    return SafetyEnvelope(
        envelope_id=new_id("env"),
        device_id=device.device_id,
        source_interaction_ids=constraint.source_interaction_ids,
        participant_ids=constraint.participant_ids,
        agent_ids=constraint.agent_ids,
        selected_metavector=selected_metavector(constraint.G_t),
        mapped_control_variables=mapped,
        min_values={k: mins[k] for k in mapped if k in mins},
        max_values={k: maxs[k] for k in mapped if k in maxs},
        duration=constraint.duration,
        expires_at=constraint.expires_at,
        required_approvals=required_approvals,
        approvals=approvals,
        safety_policy_version=SAFETY_POLICY_VERSION,
        simulation_result=simulation,
        actuation_receipt_id=None,
        rollback_neutral_state=dict(NEUTRAL_STATE),
        constraint_id=constraint.constraint_id,
        revoked=False,
        causal_predecessor_ids=(constraint.constraint_id,),
        sequence=sequence,
        chart_not_closure=True,
        command="u_t=SafetyEnvelope_D(G_t)",
    )


class HardwareClosureGateway:
    def __init__(
        self,
        store: HardwareStore,
        twin: SimulatedOpticalEllipseTwin,
        policy: HardwareSafetyPolicy | None = None,
        clock: Clock | None = None,
    ) -> None:
        self.store = store
        self.twin = twin
        self.policy = policy or HardwareSafetyPolicy()
        self.clock = clock or UtcClock()

    def _refuse(
        self,
        reason: Refusal,
        *,
        device_id: str,
        envelope_id: str | None = None,
        admission_id: str | None = None,
        predecessors: tuple[str, ...] = (),
    ) -> ActuationReceipt:
        receipt = ActuationReceipt(
            receipt_id=new_id("refused"),
            envelope_id=envelope_id,
            device_id=device_id,
            decision=ActuationDecision.REFUSED,
            refused_reason=reason,
            applied_controls={},
            at=self.clock.now(),
            simulated=True,
            sequence=self.store.next_seq(),
            causal_predecessor_ids=predecessors,
            admission_id=admission_id,
            note=f"refused: {reason.value}; chart not Closure",
        )
        self.store.put_receipt(receipt)
        return receipt

    def admit_network_interpretation(
        self, proposal: ConstraintProposal, expires_at: datetime
    ) -> ConstraintAdmission:
        admission = ConstraintAdmission(
            admission_id=new_id("adm-interp"),
            proposal_id=proposal.proposal_id,
            kind=AdmissionKind.NETWORK_INTERPRETATION,
            envelope_id=None,
            admitted_at=self.clock.now(),
            expires_at=expires_at,
            revoked=False,
            causal_predecessor_ids=(proposal.proposal_id,),
            sequence=self.store.next_seq(),
            note="admissible as a network interpretation ≠ authorized as a hardware actuation",
        )
        self.store.put_admission(admission)
        return admission

    def admit_hardware_actuation(
        self, proposal: ConstraintProposal, envelope: SafetyEnvelope
    ) -> ConstraintAdmission | ActuationReceipt:
        reason = self._actuation_precheck(envelope, proposal=proposal)
        if reason is not None:
            return self._refuse(
                reason,
                device_id=envelope.device_id,
                envelope_id=envelope.envelope_id,
                predecessors=(envelope.envelope_id, proposal.proposal_id),
            )
        admission = ConstraintAdmission(
            admission_id=new_id("adm-act"),
            proposal_id=proposal.proposal_id,
            kind=AdmissionKind.HARDWARE_ACTUATION,
            envelope_id=envelope.envelope_id,
            admitted_at=self.clock.now(),
            expires_at=envelope.expires_at,
            revoked=False,
            causal_predecessor_ids=(proposal.proposal_id, envelope.envelope_id),
            sequence=self.store.next_seq(),
            note="authorized as a hardware actuation under SafetyEnvelope_D; not Closure",
        )
        self.store.put_admission(admission)
        return admission

    def _actuation_precheck(
        self,
        envelope: SafetyEnvelope,
        *,
        proposal: ConstraintProposal | None = None,
        admission: ConstraintAdmission | None = None,
    ) -> Refusal | None:
        device = self.store.devices.get(envelope.device_id)
        now = self.clock.now()
        if device is None:
            return Refusal.WRONG_DEVICE
        if device.status == DeviceStatus.CLOSED or device.institutional_review_only:
            return Refusal.DEVICE_CLOSED
        if device.kind != DeviceKind.SIMULATED_OPTICAL_ELLIPSE:
            return Refusal.DEVICE_CLOSED
        if (
            device.real_laser
            or device.real_slm
            or device.real_quantum_controller
            or device.real_voltage
            or device.real_magnet
            or device.real_cryo
            or device.real_fusion
        ):
            return Refusal.REAL_HARDWARE_FORBIDDEN
        if envelope.safety_policy_version != self.policy.version:
            return Refusal.WRONG_POLICY
        if envelope.revoked or (admission is not None and admission.revoked):
            return Refusal.REVOKED
        if now >= envelope.expires_at or (admission is not None and now >= admission.expires_at):
            return Refusal.EXPIRED
        if not envelope.mapped_control_variables:
            return Refusal.UNDEFINED_FORM
        required = set(envelope.required_approvals)
        got = set(envelope.approvals)
        if not required <= got:
            return Refusal.MISSING_APPROVALS
        human_approvals = [
            pid
            for pid in envelope.approvals
            if (p := self.store.participants.get(pid)) is not None and p.kind == "human"
        ]
        if len(human_approvals) < self.policy.min_human_approvals:
            return Refusal.MISSING_APPROVALS
        if proposal is not None:
            if proposal.raw_ai_output and not envelope.participant_ids:
                return Refusal.RAW_AI_OUTPUT_TO_HARDWARE
            if proposal.origin.value == "autonomous_ai" and not envelope.participant_ids:
                return Refusal.RAW_AI_PROPOSAL_ALONE
            if proposal.undifferentiated_public_consensus:
                return Refusal.PUBLIC_CONSENSUS
        if not envelope.participant_ids:
            return Refusal.RAW_AI_PROPOSAL_ALONE
        sim = envelope.simulation_result
        if self.policy.require_simulation_pass and (sim is None or not sim.passed):
            return Refusal.SIMULATION_FAILED
        constraint = self.store.constraints.get(envelope.constraint_id)
        if constraint is not None:
            if not (
                constraint.temporary
                and constraint.device_relative
                and constraint.bounded
                and constraint.source_reversible
                and constraint.time_limited
                and constraint.revocable
                and constraint.causally_ordered
            ):
                return Refusal.NOT_TEMPORARY
        return None

    def actuate(
        self,
        *,
        admission_id: str | None = None,
        proposal_id: str | None = None,
        envelope_id: str | None = None,
    ) -> ActuationReceipt:
        device_id = self.twin.device.device_id
        if admission_id is None:
            prop = self.store.proposals.get(proposal_id) if proposal_id else None
            if prop is not None and (prop.raw_ai_output or prop.origin.value == "autonomous_ai"):
                if not prop.source_interaction_ids:
                    return self._refuse(
                        Refusal.RAW_AI_PROPOSAL_ALONE,
                        device_id=prop.device_id,
                        predecessors=(prop.proposal_id,),
                    )
                # even with ids, a raw AI proposal without admission cannot actuate
                if prop.raw_ai_output and prop.origin.value == "autonomous_ai":
                    return self._refuse(
                        Refusal.RAW_AI_PROPOSAL_ALONE,
                        device_id=prop.device_id,
                        predecessors=(prop.proposal_id,),
                    )
            return self._refuse(
                Refusal.NO_ADMISSION,
                device_id=device_id,
                predecessors=tuple(x for x in (proposal_id, envelope_id) if x),
            )

        admission = self.store.admissions.get(admission_id)
        if admission is None:
            return self._refuse(Refusal.NO_ADMISSION, device_id=device_id)

        if admission.kind != AdmissionKind.HARDWARE_ACTUATION:
            return self._refuse(
                Refusal.NETWORK_INTERPRETATION_IS_NOT_ACTUATION,
                device_id=device_id,
                admission_id=admission.admission_id,
                predecessors=(admission.admission_id,),
            )

        if admission.envelope_id is None:
            return self._refuse(
                Refusal.MISSING_ENVELOPE,
                device_id=device_id,
                admission_id=admission.admission_id,
                predecessors=(admission.admission_id,),
            )

        envelope = self.store.envelopes.get(admission.envelope_id)
        if envelope is None:
            return self._refuse(
                Refusal.MISSING_ENVELOPE,
                device_id=device_id,
                admission_id=admission.admission_id,
                envelope_id=admission.envelope_id,
            )

        proposal = self.store.proposals.get(admission.proposal_id)
        reason = self._actuation_precheck(envelope, proposal=proposal, admission=admission)
        if reason is not None:
            return self._refuse(
                reason,
                device_id=envelope.device_id,
                envelope_id=envelope.envelope_id,
                admission_id=admission.admission_id,
                predecessors=(admission.admission_id, envelope.envelope_id),
            )

        # Hardware receives only the envelope command u_t, never G_t raw and never raw AI.
        constraint = self.store.constraints[envelope.constraint_id]
        bounded: dict[str, float] = {}
        for name, value in constraint.G_t.items():
            lo = envelope.min_values.get(name)
            hi = envelope.max_values.get(name)
            if lo is None or hi is None:
                continue
            if lo <= float(value) <= hi:
                bounded[name] = float(value)
        _ = envelope.command
        applied = self.twin.apply(bounded)
        receipt = ActuationReceipt(
            receipt_id=new_id("act"),
            envelope_id=envelope.envelope_id,
            device_id=envelope.device_id,
            decision=ActuationDecision.ACTUATED,
            refused_reason=None,
            applied_controls=applied,
            at=self.clock.now(),
            simulated=True,
            sequence=self.store.next_seq(),
            causal_predecessor_ids=(admission.admission_id, envelope.envelope_id),
            admission_id=admission.admission_id,
            note="actuated from SafetyEnvelope_D(G_t); simulated optical ellipse; not Closure",
        )
        self.store.put_receipt(receipt)
        self.store.replace_envelope(envelope.envelope_id, actuation_receipt_id=receipt.receipt_id)
        return receipt

    def record_physical_return(self, receipt: ActuationReceipt) -> PhysicalReturn:
        envelope = self.store.envelopes.get(receipt.envelope_id) if receipt.envelope_id else None
        source_ids = envelope.source_interaction_ids if envelope else ()
        phys = PhysicalReturn(
            return_id=new_id("ret"),
            receipt_id=receipt.receipt_id,
            device_id=receipt.device_id,
            sensor_readings=self.twin.sense(),
            source_reversible=True,
            reintegrates_to_network=True,
            source_interaction_ids=source_ids,
            at=self.clock.now(),
            simulated=True,
            sequence=self.store.next_seq(),
            causal_predecessor_ids=(receipt.receipt_id,),
        )
        self.store.put_return(phys)
        return phys

    def revoke(self, admission_id: str) -> ConstraintAdmission:
        admission = self.store.replace_admission(admission_id, revoked=True)
        if admission.envelope_id:
            self.store.replace_envelope(admission.envelope_id, revoked=True)
        return admission
