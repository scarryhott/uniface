"""Programmatic API for the hardware closure loop chart.

Not a live two-person Uniface E2E. Not Closure. TRUE not issued.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Iterable, Mapping, Sequence

from .constraint_synthesis import (
    SynthesisRefused,
    proposal_from_interactions,
    synthesize_temporary_constraint,
)
from .device_twin import (
    SimulatedOpticalEllipseTwin,
    fusion_adapter_stub,
    quantum_adapter_stub,
    register_simulated_optical_ellipse,
)
from .hardware_gateway import HardwareClosureGateway, wrap_safety_envelope
from .hardware_models import (
    ActuationReceipt,
    AdmissionKind,
    Clock,
    ConstraintAdmission,
    ConstraintProposal,
    Device,
    FrozenClock,
    HardwareSafetyPolicy,
    Interaction,
    NetworkReopening,
    Participant,
    PhysicalReturn,
    ProposalOrigin,
    Refusal,
    SAFETY_POLICY_VERSION,
    SafetyEnvelope,
    TemporaryGlobalConstraint,
    UtcClock,
    VerificationRun,
    natural_form,
    new_id,
)
from .hardware_store import HardwareStore


class HardwareLoopAPI:
    def __init__(self, clock: Clock | None = None, policy: HardwareSafetyPolicy | None = None) -> None:
        self.clock = clock or UtcClock()
        self.policy = policy or HardwareSafetyPolicy()
        self.store = HardwareStore()
        self.twin: SimulatedOpticalEllipseTwin | None = None
        self.gateway: HardwareClosureGateway | None = None

    def _gw(self) -> HardwareClosureGateway:
        if self.gateway is None:
            raise RuntimeError("register_first_device first")
        return self.gateway

    def register_first_device(self, device_id: str | None = None) -> Device:
        device = register_simulated_optical_ellipse(device_id)
        self.store.put_device(device)
        self.twin = SimulatedOpticalEllipseTwin(device)
        self.gateway = HardwareClosureGateway(self.store, self.twin, self.policy, self.clock)
        return device

    def register_quantum_stub(self) -> Device:
        return self.store.put_device(quantum_adapter_stub())

    def register_fusion_stub(self) -> Device:
        return self.store.put_device(fusion_adapter_stub())

    def add_human(self, participant_id: str, display: str | None = None) -> str:
        self.store.put_participant(Participant(participant_id=participant_id, kind="human", display=display or participant_id))
        return participant_id

    def add_autonomous_ai(self, agent_id: str, display: str | None = None) -> str:
        self.store.put_participant(Participant(participant_id=agent_id, kind="autonomous_ai", display=display or agent_id))
        return agent_id

    def _interact(
        self,
        *,
        origin: ProposalOrigin,
        actor_id: str,
        natural_forms: Sequence[str],
        controls: Mapping[str, float] | None,
        raw_ai_output: bool = False,
        undifferentiated_public_consensus: bool = False,
        predecessors: tuple[str, ...] = (),
    ) -> Interaction:
        device = self.twin.device if self.twin else next(iter(self.store.devices.values()))
        item = Interaction(
            interaction_id=new_id("ix"),
            origin=origin,
            actor_id=actor_id,
            device_id=device.device_id,
            natural_forms=tuple(natural_form(s) for s in natural_forms),
            requested_controls=dict(controls or {}),
            at=self.clock.now(),
            raw_ai_output=raw_ai_output,
            undifferentiated_public_consensus=undifferentiated_public_consensus,
            sequence=self.store.next_seq(),
            causal_predecessor_ids=predecessors,
        )
        self.store.put_interaction(item)
        return item

    def human_interact(
        self, participant_id: str, natural_forms: Sequence[str], controls: Mapping[str, float] | None = None
    ) -> Interaction:
        return self._interact(origin=ProposalOrigin.HUMAN, actor_id=participant_id, natural_forms=natural_forms, controls=controls)

    def ai_interact(
        self, agent_id: str, natural_forms: Sequence[str], controls: Mapping[str, float] | None = None, raw: bool = False
    ) -> Interaction:
        return self._interact(
            origin=ProposalOrigin.AUTONOMOUS_AI,
            actor_id=agent_id,
            natural_forms=natural_forms,
            controls=controls,
            raw_ai_output=raw,
        )

    def sensor_interact(self, device: Device | None = None) -> Interaction:
        twin = self.twin
        assert twin is not None
        readings = twin.sense()
        return self._interact(
            origin=ProposalOrigin.SENSOR,
            actor_id=twin.device.sensor_channels[0].channel_id,
            natural_forms=("ellipse",),
            controls={},
            predecessors=(),
        )

    def propose_from(
        self,
        interactions: Sequence[Interaction],
        *,
        origin: ProposalOrigin,
        author_id: str,
        raw_ai_output: bool = False,
        undifferentiated_public_consensus: bool = False,
    ) -> ConstraintProposal:
        device = self.twin.device  # type: ignore[union-attr]
        prop = proposal_from_interactions(
            origin=origin,
            author_id=author_id,
            device=device,
            interactions=interactions,
            now=self.clock.now(),
            sequence=self.store.next_seq(),
            raw_ai_output=raw_ai_output,
            undifferentiated_public_consensus=undifferentiated_public_consensus,
        )
        self.store.put_proposal(prop)
        return prop

    def propose_raw_ai(self, agent_id: str, natural_forms: Sequence[str], controls: Mapping[str, float]) -> ConstraintProposal:
        ix = self.ai_interact(agent_id, natural_forms, controls, raw=True)
        return self.propose_from([ix], origin=ProposalOrigin.AUTONOMOUS_AI, author_id=agent_id, raw_ai_output=True)

    def synthesize(
        self, interactions: Sequence[Interaction], duration: timedelta
    ) -> TemporaryGlobalConstraint:
        device = self.twin.device  # type: ignore[union-attr]
        constraint = synthesize_temporary_constraint(
            device=device,
            interactions=interactions,
            duration=duration,
            now=self.clock.now(),
            policy=self.policy,
            sequence=self.store.next_seq(),
            predecessor_ids=tuple(ix.interaction_id for ix in interactions),
        )
        self.store.put_constraint(constraint)
        return constraint

    def simulate_and_wrap(
        self,
        constraint: TemporaryGlobalConstraint,
        *,
        approvals: Sequence[str],
        required_approvals: Sequence[str] | None = None,
    ) -> tuple[SafetyEnvelope, VerificationRun]:
        assert self.twin is not None
        sim = self.twin.simulate(constraint.G_t, max_intensity=self.policy.max_intensity)
        required = tuple(required_approvals) if required_approvals is not None else tuple(approvals)
        envelope = wrap_safety_envelope(
            constraint=constraint,
            device=self.twin.device,
            approvals=tuple(approvals),
            required_approvals=required,
            simulation=sim,
            sequence=self.store.next_seq(),
            now=self.clock.now(),
        )
        self.store.put_envelope(envelope)
        verification = VerificationRun(
            run_id=sim.run_id,
            envelope_id=envelope.envelope_id,
            simulation=sim,
            policy_ok=sim.passed and sim.energy_bound_ok,
            rho_d_defined=bool(envelope.mapped_control_variables),
            at=self.clock.now(),
            sequence=self.store.next_seq(),
        )
        self.store.put_verification(verification)
        return envelope, verification

    def admit_as_network_interpretation(self, proposal: ConstraintProposal, duration: timedelta) -> ConstraintAdmission:
        expires = self.clock.now() + duration
        return self._gw().admit_network_interpretation(proposal, expires)

    def admit_for_actuation(self, proposal: ConstraintProposal, envelope: SafetyEnvelope) -> ConstraintAdmission | ActuationReceipt:
        return self._gw().admit_hardware_actuation(proposal, envelope)

    def actuate(self, admission_id: str | None = None, proposal_id: str | None = None) -> ActuationReceipt:
        return self._gw().actuate(admission_id=admission_id, proposal_id=proposal_id)

    def physical_return(self, receipt: ActuationReceipt) -> PhysicalReturn:
        return self._gw().record_physical_return(receipt)

    def reintegrate(self, phys: PhysicalReturn, cycle_index: int = 1) -> NetworkReopening:
        nxt = Interaction(
            interaction_id=new_id("ix-next"),
            origin=ProposalOrigin.COLLECTIVE,
            actor_id="network",
            device_id=phys.device_id,
            natural_forms=(),
            requested_controls={},
            at=self.clock.now(),
            sequence=self.store.next_seq(),
            causal_predecessor_ids=(phys.return_id,),
        )
        self.store.put_interaction(nxt)
        reopening = NetworkReopening(
            reopening_id=new_id("reopen"),
            return_id=phys.return_id,
            next_interaction_id=nxt.interaction_id,
            cycle_index=cycle_index,
            sequence=self.store.next_seq(),
            causal_predecessor_ids=(phys.return_id,),
        )
        self.store.put_reopening(reopening)
        return reopening

    def revoke(self, admission_id: str) -> ConstraintAdmission:
        return self._gw().revoke(admission_id)

    def synthesize_admit_actuate(
        self,
        interactions: Sequence[Interaction],
        *,
        approvals: Sequence[str],
        duration: timedelta,
        origin_author: str,
    ) -> tuple[TemporaryGlobalConstraint | None, SafetyEnvelope | None, ConstraintAdmission | None, ActuationReceipt]:
        """Collective path. Synthesis failures become refused receipts, not throws, for tests."""
        device_id = self.twin.device.device_id  # type: ignore[union-attr]
        try:
            constraint = self.synthesize(interactions, duration)
        except SynthesisRefused as exc:
            prop = self.propose_from(
                interactions,
                origin=ProposalOrigin.COLLECTIVE if len(interactions) > 1 else interactions[0].origin,
                author_id=origin_author,
                raw_ai_output=exc.reason == Refusal.RAW_AI_PROPOSAL_ALONE,
            )
            receipt = self.actuate(admission_id=None, proposal_id=prop.proposal_id)
            if receipt.refused_reason != exc.reason:
                # keep the more specific synthesis reason on a fresh refuse
                receipt = self._gw()._refuse(
                    exc.reason,
                    device_id=device_id,
                    predecessors=(prop.proposal_id,),
                )
            return None, None, None, receipt

        proposal = self.propose_from(
            interactions, origin=ProposalOrigin.COLLECTIVE, author_id=origin_author
        )
        envelope, _ver = self.simulate_and_wrap(constraint, approvals=approvals)
        admitted = self.admit_for_actuation(proposal, envelope)
        if isinstance(admitted, ActuationReceipt):
            return constraint, envelope, None, admitted
        receipt = self.actuate(admission_id=admitted.admission_id)
        return constraint, envelope, admitted, receipt

    def run_first_device_loop(
        self,
        *,
        human_a: str = "human-a",
        human_b: str = "human-b",
        ai_id: str = "ai-1",
        duration: timedelta | None = None,
    ) -> dict:
        """Two simulated humans + one autonomous AI + simulated optical ellipse.

        One bounded collective constraint + one physical-style return + one reopened cycle.
        """
        device = self.register_first_device()
        self.add_human(human_a)
        self.add_human(human_b)
        self.add_autonomous_ai(ai_id)
        dur = duration or timedelta(minutes=5)
        ix_a = self.human_interact(
            human_a,
            ("r", "ellipse"),
            {"path": 0.2, "gain": 0.1, "mirror_geometry": 0.4},
        )
        ix_b = self.human_interact(
            human_b,
            ("i", "metavector"),
            {"phase": 0.15, "intensity": 0.2, "orientation": 0.05},
        )
        ix_ai = self.ai_interact(ai_id, ("ball",), {"bounded_optical_envelope": 0.5})
        ix_sense = self.sensor_interact(device)
        constraint, envelope, admission, receipt = self.synthesize_admit_actuate(
            [ix_a, ix_b, ix_ai, ix_sense],
            approvals=(human_a, human_b),
            duration=dur,
            origin_author=human_a,
        )
        phys = None
        reopened = None
        if receipt.decision.value == "actuated":
            phys = self.physical_return(receipt)
            reopened = self.reintegrate(phys, cycle_index=1)
        return {
            "device": device,
            "interactions": (ix_a, ix_b, ix_ai, ix_sense),
            "constraint": constraint,
            "envelope": envelope,
            "admission": admission,
            "receipt": receipt,
            "physical_return": phys,
            "reopening": reopened,
        }
