"""In-memory causally ordered store for the hardware chart."""

from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timedelta
from typing import Any

from .hardware_models import (
    ActuationReceipt,
    ConstraintAdmission,
    ConstraintProposal,
    Device,
    Interaction,
    NetworkReopening,
    Participant,
    PhysicalReturn,
    SafetyEnvelope,
    TemporaryGlobalConstraint,
    VerificationRun,
)


class HardwareStore:
    def __init__(self) -> None:
        self._seq = 0
        self.devices: dict[str, Device] = {}
        self.participants: dict[str, Participant] = {}
        self.interactions: dict[str, Interaction] = {}
        self.proposals: dict[str, ConstraintProposal] = {}
        self.constraints: dict[str, TemporaryGlobalConstraint] = {}
        self.envelopes: dict[str, SafetyEnvelope] = {}
        self.admissions: dict[str, ConstraintAdmission] = {}
        self.receipts: dict[str, ActuationReceipt] = {}
        self.returns: dict[str, PhysicalReturn] = {}
        self.verifications: dict[str, VerificationRun] = {}
        self.reopenings: dict[str, NetworkReopening] = {}

    def next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def put_device(self, device: Device) -> Device:
        self.devices[device.device_id] = device
        return device

    def put_participant(self, participant: Participant) -> Participant:
        self.participants[participant.participant_id] = participant
        return participant

    def put_interaction(self, item: Interaction) -> Interaction:
        self.interactions[item.interaction_id] = item
        return item

    def put_proposal(self, item: ConstraintProposal) -> ConstraintProposal:
        self.proposals[item.proposal_id] = item
        return item

    def put_constraint(self, item: TemporaryGlobalConstraint) -> TemporaryGlobalConstraint:
        self.constraints[item.constraint_id] = item
        return item

    def put_envelope(self, item: SafetyEnvelope) -> SafetyEnvelope:
        self.envelopes[item.envelope_id] = item
        return item

    def put_admission(self, item: ConstraintAdmission) -> ConstraintAdmission:
        self.admissions[item.admission_id] = item
        return item

    def put_receipt(self, item: ActuationReceipt) -> ActuationReceipt:
        self.receipts[item.receipt_id] = item
        return item

    def put_return(self, item: PhysicalReturn) -> PhysicalReturn:
        self.returns[item.return_id] = item
        return item

    def put_verification(self, item: VerificationRun) -> VerificationRun:
        self.verifications[item.run_id] = item
        return item

    def put_reopening(self, item: NetworkReopening) -> NetworkReopening:
        self.reopenings[item.reopening_id] = item
        return item

    def replace_envelope(self, envelope_id: str, **changes: Any) -> SafetyEnvelope:
        current = self.envelopes[envelope_id]
        updated = replace(current, **changes)
        self.envelopes[envelope_id] = updated
        return updated

    def replace_admission(self, admission_id: str, **changes: Any) -> ConstraintAdmission:
        current = self.admissions[admission_id]
        updated = replace(current, **changes)
        self.admissions[admission_id] = updated
        return updated

    def snapshot(self) -> dict[str, Any]:
        def conv(obj: Any) -> Any:
            if obj is None or isinstance(obj, (str, int, float, bool)):
                return obj
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, timedelta):
                return obj.total_seconds()
            if isinstance(obj, dict):
                return {str(k): conv(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [conv(x) for x in obj]
            if hasattr(obj, "value"):
                try:
                    return obj.value
                except Exception:
                    pass
            if hasattr(obj, "__dataclass_fields__"):
                return {k: conv(v) for k, v in asdict(obj).items()}
            return str(obj)

        return {
            "chart_not_closure": True,
            "TRUE_issued": False,
            "devices": {k: conv(v) for k, v in self.devices.items()},
            "participants": {k: conv(v) for k, v in self.participants.items()},
            "interactions": {k: conv(v) for k, v in self.interactions.items()},
            "constraints": {k: conv(v) for k, v in self.constraints.items()},
            "envelopes": {k: conv(v) for k, v in self.envelopes.items()},
            "admissions": {k: conv(v) for k, v in self.admissions.items()},
            "receipts": {k: conv(v) for k, v in self.receipts.items()},
            "returns": {k: conv(v) for k, v in self.returns.items()},
            "reopenings": {k: conv(v) for k, v in self.reopenings.items()},
            "sequence": self._seq,
        }
