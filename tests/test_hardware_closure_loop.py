"""Hardware closure loop chart tests.

FIRST TEST: two simulated humans + one autonomous AI + one simulated optical
ellipse + one bounded collective constraint + one physical-style return +
one reopened network cycle.

Refused actuation: no admission; expired; revoked; undefined form; raw AI alone.

This is a digital chart, not Closure. TRUE is not issued.
Live two-person Uniface E2E is not claimed.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from closure_supernet.api_hardware import HardwareLoopAPI
from closure_supernet.constraint_synthesis import SynthesisRefused
from closure_supernet.device_twin import OPTICAL_RHO_D, optical_rho_d
from closure_supernet.hardware_models import (
    ActuationDecision,
    AdmissionKind,
    ConstraintAdmission,
    DeviceKind,
    DeviceStatus,
    FormStatus,
    FrozenClock,
    ProposalOrigin,
    Refusal,
    natural_form,
)
from closure_supernet.hardware_web import render_html, render_json


def test_hardware_closure_loop_two_humans_ai_optical_ellipse():
    """FIRST TEST — full simulated hardware loop, then a reopened cycle."""
    clock = FrozenClock(datetime(2026, 8, 26, 12, 32, tzinfo=timezone.utc))
    api = HardwareLoopAPI(clock=clock)
    out = api.run_first_device_loop()

    device = out["device"]
    assert device.kind == DeviceKind.SIMULATED_OPTICAL_ELLIPSE
    assert device.simulated
    assert device.real_laser is False
    assert device.real_slm is False
    assert device.real_quantum_controller is False
    assert device.real_voltage is False
    assert device.real_magnet is False
    assert device.real_cryo is False
    assert device.real_fusion is False

    humans = [p for p in api.store.participants.values() if p.kind == "human"]
    agents = [p for p in api.store.participants.values() if p.kind == "autonomous_ai"]
    assert len(humans) == 2
    assert len(agents) == 1

    ix_a, ix_b, ix_ai, ix_sense = out["interactions"]
    assert ix_a.origin == ProposalOrigin.HUMAN
    assert ix_b.origin == ProposalOrigin.HUMAN
    assert ix_ai.origin == ProposalOrigin.AUTONOMOUS_AI
    assert ix_sense.origin == ProposalOrigin.SENSOR

    constraint = out["constraint"]
    assert constraint is not None
    assert constraint.temporary
    assert constraint.device_relative
    assert constraint.bounded
    assert constraint.source_reversible
    assert constraint.time_limited
    assert constraint.revocable
    assert constraint.causally_ordered
    assert constraint.device_id == device.device_id
    assert "path" in constraint.G_t
    assert "phase" in constraint.G_t
    assert "bounded_optical_envelope" in constraint.G_t

    envelope = out["envelope"]
    assert envelope is not None
    assert envelope.command == "u_t=SafetyEnvelope_D(G_t)"
    assert envelope.device_id == device.device_id
    assert envelope.source_interaction_ids
    assert set(envelope.participant_ids) == {"human-a", "human-b"}
    assert "ai-1" in envelope.agent_ids
    assert envelope.selected_metavector.phase is not None
    assert envelope.mapped_control_variables
    assert envelope.min_values
    assert envelope.max_values
    assert envelope.duration.total_seconds() > 0
    assert envelope.expires_at > clock.now()
    assert set(envelope.required_approvals) <= set(envelope.approvals)
    assert envelope.safety_policy_version
    assert envelope.simulation_result is not None and envelope.simulation_result.passed
    assert envelope.rollback_neutral_state

    admission = out["admission"]
    assert isinstance(admission, ConstraintAdmission)
    assert admission.kind == AdmissionKind.HARDWARE_ACTUATION
    assert admission.envelope_id == envelope.envelope_id

    receipt = out["receipt"]
    assert receipt.decision == ActuationDecision.ACTUATED
    assert receipt.refused_reason is None
    assert receipt.simulated
    assert receipt.applied_controls
    assert envelope.envelope_id
    assert api.store.envelopes[envelope.envelope_id].actuation_receipt_id == receipt.receipt_id

    phys = out["physical_return"]
    assert phys is not None
    assert phys.simulated
    assert phys.source_reversible
    assert phys.reintegrates_to_network
    assert phys.sensor_readings

    reopened = out["reopening"]
    assert reopened is not None
    assert reopened.next_interaction_id
    assert reopened.cycle_index == 1
    assert reopened.next_interaction_id in api.store.interactions
    assert reopened.return_id == phys.return_id

    # Interpretation admission is not actuation authorization.
    interp_prop = api.propose_from(
        [ix_a], origin=ProposalOrigin.HUMAN, author_id="human-a"
    )
    interp = api.admit_as_network_interpretation(interp_prop, timedelta(minutes=5))
    assert interp.kind == AdmissionKind.NETWORK_INTERPRETATION
    blocked = api.actuate(admission_id=interp.admission_id)
    assert blocked.decision == ActuationDecision.REFUSED
    assert blocked.refused_reason == Refusal.NETWORK_INTERPRETATION_IS_NOT_ACTUATION


def test_refused_no_admission_no_actuate():
    api = HardwareLoopAPI()
    api.register_first_device()
    api.add_human("human-a")
    ix = api.human_interact("human-a", ("r",), {"path": 0.2})
    prop = api.propose_from([ix], origin=ProposalOrigin.HUMAN, author_id="human-a")
    receipt = api.actuate(admission_id=None, proposal_id=prop.proposal_id)
    assert receipt.decision == ActuationDecision.REFUSED
    assert receipt.refused_reason == Refusal.NO_ADMISSION
    assert receipt.applied_controls == {}


def test_refused_expired_no_actuate():
    clock = FrozenClock(datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc))
    api = HardwareLoopAPI(clock=clock)
    api.register_first_device()
    api.add_human("human-a")
    api.add_human("human-b")
    api.add_autonomous_ai("ai-1")
    ixs = [
        api.human_interact("human-a", ("r",), {"path": 0.2}),
        api.human_interact("human-b", ("i",), {"phase": 0.1}),
        api.ai_interact("ai-1", ("ball",), {"bounded_optical_envelope": 0.3}),
    ]
    constraint, envelope, admission, receipt = api.synthesize_admit_actuate(
        ixs, approvals=("human-a", "human-b"), duration=timedelta(minutes=1), origin_author="human-a"
    )
    assert receipt.decision == ActuationDecision.ACTUATED
    assert admission is not None
    clock.advance(timedelta(minutes=2))
    expired = api.actuate(admission_id=admission.admission_id)
    assert expired.decision == ActuationDecision.REFUSED
    assert expired.refused_reason == Refusal.EXPIRED
    assert expired.applied_controls == {}


def test_refused_revoked_no_actuate():
    api = HardwareLoopAPI()
    api.register_first_device()
    api.add_human("human-a")
    api.add_human("human-b")
    api.add_autonomous_ai("ai-1")
    ixs = [
        api.human_interact("human-a", ("ellipse",), {"mirror_geometry": 0.4}),
        api.human_interact("human-b", ("metavector",), {"intensity": 0.2, "phase": 0.1, "orientation": 0.0}),
        api.ai_interact("ai-1", ("hair",), {"perturbation_directions": 0.1}),
    ]
    _c, _e, admission, first = api.synthesize_admit_actuate(
        ixs, approvals=("human-a", "human-b"), duration=timedelta(minutes=5), origin_author="human-a"
    )
    assert first.decision == ActuationDecision.ACTUATED
    assert admission is not None
    api.revoke(admission.admission_id)
    again = api.actuate(admission_id=admission.admission_id)
    assert again.decision == ActuationDecision.REFUSED
    assert again.refused_reason == Refusal.REVOKED
    assert again.applied_controls == {}


def test_refused_undefined_form_no_actuate():
    api = HardwareLoopAPI()
    api.register_first_device()
    api.add_human("human-a")
    api.add_human("human-b")
    device = api.twin.device
    image = optical_rho_d(natural_form("voltage"), device)
    assert image.status == FormStatus.OPEN
    assert image.actuatable is False
    assert "voltage" not in OPTICAL_RHO_D

    ixs = [
        api.human_interact("human-a", ("voltage",), {"voltage": 12.0}),
        api.human_interact("human-b", ("money",), {"money": 1.0}),
    ]
    _c, _e, _a, receipt = api.synthesize_admit_actuate(
        ixs, approvals=("human-a", "human-b"), duration=timedelta(minutes=5), origin_author="human-a"
    )
    assert receipt.decision == ActuationDecision.REFUSED
    assert receipt.refused_reason == Refusal.UNDEFINED_FORM
    assert receipt.applied_controls == {}


def test_refused_raw_ai_proposal_alone_no_actuate():
    api = HardwareLoopAPI()
    api.register_first_device()
    api.add_autonomous_ai("ai-1")
    prop = api.propose_raw_ai("ai-1", ("metavector",), {"phase": 0.9, "intensity": 0.9, "orientation": 0.0})
    assert prop.raw_ai_output is True
    receipt = api.actuate(admission_id=None, proposal_id=prop.proposal_id)
    assert receipt.decision == ActuationDecision.REFUSED
    assert receipt.refused_reason == Refusal.RAW_AI_PROPOSAL_ALONE
    assert receipt.applied_controls == {}

    # Synthesis of AI-only interactions also refuses; must not reach a device.
    ix = api.ai_interact("ai-1", ("metavector",), {"phase": 0.2}, raw=True)
    try:
        api.synthesize([ix], timedelta(minutes=5))
        raised = False
    except SynthesisRefused as exc:
        raised = True
        assert exc.reason == Refusal.RAW_AI_PROPOSAL_ALONE
    assert raised


def test_quantum_and_fusion_stubs_are_closed():
    api = HardwareLoopAPI()
    api.register_first_device()
    q = api.register_quantum_stub()
    f = api.register_fusion_stub()
    assert q.status == DeviceStatus.CLOSED
    assert q.institutional_review_only
    assert f.status == DeviceStatus.CLOSED
    assert f.institutional_review_only
    assert q.real_quantum_controller is False
    assert f.real_fusion is False


def test_hardware_web_chart_renders():
    api = HardwareLoopAPI()
    api.run_first_device_loop()
    html = render_html(api.store)
    assert "SafetyEnvelope_D" in html
    assert "not Closure" in html
    payload = render_json(api.store)
    assert "chart_not_closure" in payload
