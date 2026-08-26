"""Hardware closure chart for Uniface.

Digital chart of a hardware loop, not Closure. Notebook operators are
proposed device-relative realizations, not established physical identities.
TRUE is not issued.
"""

from .hardware_models import (
    ActuationDecision,
    ActuationReceipt,
    ActuatorChannel,
    AdmissionKind,
    ConstraintAdmission,
    ConstraintProposal,
    Device,
    DeviceKind,
    DeviceStatus,
    FormStatus,
    PhysicalReturn,
    Refusal,
    SafetyEnvelope,
    SensorChannel,
    VerificationRun,
)
from .api_hardware import HardwareLoopAPI

__all__ = [
    "ActuationDecision",
    "ActuationReceipt",
    "ActuatorChannel",
    "AdmissionKind",
    "ConstraintAdmission",
    "ConstraintProposal",
    "Device",
    "DeviceKind",
    "DeviceStatus",
    "FormStatus",
    "HardwareLoopAPI",
    "PhysicalReturn",
    "Refusal",
    "SafetyEnvelope",
    "SensorChannel",
    "VerificationRun",
]

CHART_NOT_CLOSURE = True
TRUE_ISSUED = False
