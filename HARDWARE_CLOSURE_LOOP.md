# Black Mirror Hardware Closure Loop

Closure Supernet 0.9 adds the active cyber-physical path requested by the
notebook architecture without turning the network into a hardware command bus.

```text
exact network sources
→ participant + agent interaction
→ selected metavector
→ temporary device-relative constraint
→ deterministic device-twin verification
→ scoped participant admission
→ operator execution
→ sensor return
→ OPEN TranslationEvent reintegration
→ successor network potential
```

## Natural-form mapping

The implementation keeps the source vocabulary visible:

```text
point        one source occurrence, control event, or sensor return
line / r     an extended source-to-device trajectory
loop / i     recurrence, orientation, phase, and feedback
ball         the currently bounded device-state potential
hair         still-open perturbation and control directions
0 ↔ ∞        reciprocal local-reading / open-path poles
metavector   the temporary selected control orientation
ellipse      the first deterministic Black Mirror device twin
sensor       the returned reading
selection    the bounded constraint proposal
closure      source-reversible return and reopening, not terminal actuation
```

These are explicit software readings. The device twin does not establish that
any notebook equation is already a physical law.

## Safety boundary

The repository ships only:

```text
SIMULATED_OPTICAL_ELLIPSE
SIMULATED_SENSOR_LOOP
```

It does not enable direct drivers for nuclear or fusion equipment, quantum
control hardware, high-energy or unsafe laser systems, voltage, cryogenic,
magnetic, plasma, radiation, pressure, or other hazardous apparatus.

The capability endpoint reports:

```text
direct_physical_actuation = false
high_energy_actuation     = false
nuclear_actuation         = false
quantum_actuation         = false
simulation_only           = true
```

A later physical adapter must remain a separately reviewed, capability-bounded
implementation. Naming a device, changing an environment variable, or receiving
a protocol message cannot enable physical actuation.

## Temporary global constraint

A `HardwareConstraint` is global only relative to the selected active network
loop. It is never an external permanent rule.

It contains exact source occurrences, source TranslationEvents and interactions,
human and agent participants, affected perspectives, a selected metavector,
bounded control values, expected return, duration, expiry, simulation receipt,
participant decisions, and its canonical TranslationEvent.

The default synthesizer creates a deterministic bounded vector from the exact
source text. This is a replaceable software chart, not the source-level
metavector definition. The exact texts and IDs remain present so participants
can inspect or replace the selection.

## Admission path

A proposal cannot execute directly.

```text
PROPOSED / OPEN
→ safe device-twin run
→ SIMULATED / OPEN
→ required distinct participant approvals
→ ADMITTED / TRUE at temporary device scope
→ operator execution
→ EXECUTED / TRUE with return receipt
```

A rejection becomes `REJECTED / FALSE`. An unused proposal becomes
`EXPIRED / OPEN` and its canonical TranslationEvent reopens.

## Device twin

The optical ellipse twin accepts bounded channels:

```text
phase_x
phase_y
polarization
intensity
```

It returns a deterministic sensor vector and metrics:

```text
return_intensity
phase_return
polarization_return
path_invariant
return_fidelity
stability
symmetry
path_return
```

The equations are deliberately simple and reproducible. They support end-to-end
software verification of source → selection → return. They are not represented
as a radiation-transport, Maxwell, quantum-optical, fusion, or gravitational
simulation.

## Physical-style return

Execution occurs only against the safe twin and produces:

```text
HardwareActuationReceipt
HardwareReturn
immutable SIMULATION_SOURCE occurrence
```

The return is translated back into the living field:

```text
hardware constraint
→ BLACK_MIRROR_HARDWARE_RETURN
→ simulated sensor return
→ OPEN successor potential
```

The reintegration explicitly records:

```text
SIMULATED_UNDER_ASSUMPTIONS
physical_law_claimed = false
physical_device_actuated = false
```

## Persistent storage

The event-sourced database adds:

```text
hardware_devices
hardware_constraints
hardware_constraint_states
hardware_constraint_decisions
hardware_twin_runs
hardware_actuations
hardware_returns
hardware_runtime_state
```

Original device descriptions, constraint intents, and sensor returns remain in
the canonical `occurrences` table. Hardware state changes append records rather
than rewriting their source.

## API and interface

Public interface:

```text
/hardware
```

Member network routes:

```text
GET  /network/hardware/capabilities
GET  /network/hardware/devices
POST /network/hardware/constraints/synthesize
GET  /network/hardware/constraints
GET  /network/hardware/constraints/{id}
POST /network/hardware/constraints/{id}/simulate
POST /network/hardware/constraints/{id}/decision
GET  /network/hardware/twin-runs
GET  /network/hardware/actuations
GET  /network/hardware/returns
GET  /network/hardware/field
```

Operator routes:

```text
POST /admin/hardware/devices
POST /admin/hardware/constraints/{id}/execute
POST /admin/hardware/reintegrate
```

The production middleware already protects `/admin` with the operator role.

## Autonomous cycle

The hardware layer adds only bounded maintenance to the active loop:

```text
expire unused temporary constraints
→ reintegrate pending twin returns
→ run the existing living Supernet cycle
→ update Black Mirror and living-field hardware projections
```

It never synthesizes or executes a device constraint automatically by default.

## First end-to-end scenario

The tests implement:

```text
two human participants
+ one AI participant
+ one exact Black Mirror source note
+ one simulated optical ellipse
+ one source-derived metavector
+ two independent approvals
+ one operator-executed twin return
+ one OPEN reintegration TranslationEvent
```

This is the repository-level cyber-physical closure loop. A real tabletop
optical adapter can later replace the twin only after its physical safety and
instrument protocol are separately defined and reviewed.
