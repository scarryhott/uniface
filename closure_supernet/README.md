# closure_supernet — hardware layer (digital chart, not Closure)

Origin new-repo is blocked. This package lives in Uniface as a **separate Python package**, not as a rewrite of notes.

This is a **digital chart of a hardware loop**, not Closure. Notebook operators are proposed device-relative realizations, not established physical identities. TRUE is not issued. Live two-person Uniface E2E is not claimed.

## Loop (chart)

```text
human + AI + sensor interaction
→ temporary collective constraint G_t
→ u_t = SafetyEnvelope_D(G_t)
→ hardware action (simulated)
→ physical-style return
→ network reintegration
→ next interaction (reopened)
```

## Enforced in code

```text
admissible as a network interpretation
    ≠
authorized as a hardware actuation
```

- ρ_D : NaturalForm ⇁ DeviceConstraint (partial). Undefined forms stay **OPEN**: neither rejected nor allowed to actuate.
- Hardware receives **u_t = SafetyEnvelope_D(G_t)** only. Never raw AI output. Never undifferentiated public consensus.
- Constraints are temporary, device-relative, bounded, source-reversible, time-limited, revocable, causally ordered, and approved under a hardware safety policy.

## First device

**Simulated low-energy optical ellipse.** No real laser, SLM, quantum controller, voltage, magnet, cryo, or fusion.

Optical ρ_D is defined only for:

| Natural form | Device constraint |
|---|---|
| r | path / delay / gain / translation |
| i | phase / polarization |
| hair | perturbation directions |
| ball | bounded optical envelope |
| ellipse | mirror / phase-transfer geometry |
| metavector | phase / intensity / orientation |

Everything else stays OPEN.

Quantum and fusion adapters are **typed stubs marked CLOSED / institutional-review only**.

## Layout

- `hardware_models.py` — Device, SensorChannel, ActuatorChannel, SafetyEnvelope, ConstraintProposal, ConstraintAdmission, ActuationReceipt, PhysicalReturn, VerificationRun
- `hardware_store.py` — in-memory causally ordered store
- `hardware_gateway.py` — Hardware Closure Gateway (only path to actuation)
- `constraint_synthesis.py` — Temporary Global Constraint Synthesizer
- `device_twin.py` — simulated optical ellipse + CLOSED stubs
- `api_hardware.py` — programmatic loop API
- `hardware_web.py` — HTML/JSON chart of the store (not the field)

```bash
python3 -m pytest tests/test_hardware_closure_loop.py
```
