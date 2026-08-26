"""Temporary Global Constraint Synthesizer.

human + AI + sensor interaction → G_t (temporary collective constraint).

Hardware never receives G_t raw. Hardware receives u_t = SafetyEnvelope_D(G_t).
Raw AI output alone is not a constraint. Undifferentiated public consensus is not a constraint.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Mapping, Sequence

from .device_twin import mapped_controls_for_forms
from .hardware_models import (
    Clock,
    ConstraintProposal,
    Device,
    HardwareSafetyPolicy,
    Interaction,
    Metavector,
    ProposalOrigin,
    Refusal,
    SAFETY_POLICY_VERSION,
    TemporaryGlobalConstraint,
    new_id,
)


class SynthesisRefused(Exception):
    def __init__(self, reason: Refusal, detail: str = "") -> None:
        self.reason = reason
        super().__init__(detail or reason.value)


def _forms_from(interactions: Sequence[Interaction]):
    forms = []
    for ix in interactions:
        forms.extend(ix.natural_forms)
    return tuple(forms)


def merge_requested_controls(interactions: Sequence[Interaction]) -> dict[str, float]:
    out: dict[str, float] = {}
    for ix in interactions:
        for k, v in ix.requested_controls.items():
            out[k] = float(v)
    return out


def synthesize_temporary_constraint(
    *,
    device: Device,
    interactions: Sequence[Interaction],
    duration: timedelta,
    now: datetime,
    policy: HardwareSafetyPolicy | None = None,
    sequence: int,
    predecessor_ids: tuple[str, ...] = (),
) -> TemporaryGlobalConstraint:
    """Build G_t. Does not authorize actuation."""
    policy = policy or HardwareSafetyPolicy()
    if not interactions:
        raise SynthesisRefused(Refusal.NO_ADMISSION, "no interactions")
    if any(ix.undifferentiated_public_consensus for ix in interactions):
        raise SynthesisRefused(Refusal.PUBLIC_CONSENSUS)
    origins = {ix.origin for ix in interactions}
    humans = tuple(dict.fromkeys(ix.actor_id for ix in interactions if ix.origin == ProposalOrigin.HUMAN))
    agents = tuple(dict.fromkeys(ix.actor_id for ix in interactions if ix.origin == ProposalOrigin.AUTONOMOUS_AI))
    if origins <= {ProposalOrigin.AUTONOMOUS_AI} or (not humans and agents):
        raise SynthesisRefused(Refusal.RAW_AI_PROPOSAL_ALONE)
    if any(ix.raw_ai_output and ix.origin == ProposalOrigin.AUTONOMOUS_AI for ix in interactions) and not humans:
        raise SynthesisRefused(Refusal.RAW_AI_PROPOSAL_ALONE)
    if len(humans) < policy.min_human_approvals:
        raise SynthesisRefused(Refusal.MISSING_APPROVALS, "collective constraint needs two humans")
    if duration.total_seconds() <= 0:
        raise SynthesisRefused(Refusal.NOT_TEMPORARY, "duration must be positive and finite")

    forms = _forms_from(interactions)
    defined, open_forms = mapped_controls_for_forms(forms, device)
    requested = merge_requested_controls(interactions)
    G_t: dict[str, float] = {}
    bounded = True
    for name, value in requested.items():
        if name not in defined:
            # stays OPEN: not copied into G_t, not rejected as a network reading
            continue
        lo, hi = defined[name]
        if value < lo or value > hi:
            bounded = False
            continue
        G_t[name] = value
    if not G_t:
        raise SynthesisRefused(Refusal.UNDEFINED_FORM, "no defined ρ_D image; forms stay OPEN")
    if not bounded:
        raise SynthesisRefused(Refusal.UNBOUNDED)

    expires = now + duration
    source_ids = tuple(ix.interaction_id for ix in interactions)
    return TemporaryGlobalConstraint(
        constraint_id=new_id("Gt"),
        device_id=device.device_id,
        G_t=G_t,
        source_interaction_ids=source_ids,
        participant_ids=humans,
        agent_ids=agents,
        expires_at=expires,
        duration=duration,
        temporary=True,
        device_relative=True,
        bounded=True,
        source_reversible=True,
        time_limited=True,
        revocable=True,
        causally_ordered=True,
        approved_under_safety_policy=False,  # approvals happen at envelope admission
        safety_policy_version=policy.version,
        sequence=sequence,
        causal_predecessor_ids=predecessor_ids or source_ids,
        open_unmapped_forms=open_forms,
    )


def proposal_from_interactions(
    *,
    origin: ProposalOrigin,
    author_id: str,
    device: Device,
    interactions: Sequence[Interaction],
    now: datetime,
    sequence: int,
    raw_ai_output: bool = False,
    undifferentiated_public_consensus: bool = False,
) -> ConstraintProposal:
    return ConstraintProposal(
        proposal_id=new_id("prop"),
        origin=origin,
        author_id=author_id,
        device_id=device.device_id,
        natural_forms=_forms_from(interactions),
        requested_controls=merge_requested_controls(interactions),
        source_interaction_ids=tuple(ix.interaction_id for ix in interactions),
        created_at=now,
        raw_ai_output=raw_ai_output,
        undifferentiated_public_consensus=undifferentiated_public_consensus,
        sequence=sequence,
        causal_predecessor_ids=tuple(ix.interaction_id for ix in interactions),
    )


def selected_metavector(G_t: Mapping[str, float]) -> Metavector:
    return Metavector(
        phase=G_t.get("phase"),
        intensity=G_t.get("intensity"),
        orientation=G_t.get("orientation"),
    )
