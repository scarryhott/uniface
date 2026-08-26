# Unified Supernet Runtime

Closure Supernet 1.0 replaces parallel semantic runtimes with one append-only
integration operation:

```text
(current Supernet field, offered or returned relative form)
→ integration receipt
→ successor Supernet field
```

The implementation identity is:

```text
Supernet runtime = continuous integration of every offered and returned form
```

The living network, TranslationEvents, relative equality, resources, reopening,
collective action, agents, Black Mirror and bounded hardware loop remain useful
code modules and API views. They are now **lenses** over one canonical field
rather than separate foundations.

## Canonical operation

```python
await runtime.integrate_resource(ResourceEnvelope(...))
```

Every integration:

1. preserves the exact source occurrence;
2. creates one immutable `SupernetIntegrationEvent`;
3. senses literal symbols, operator paths and participant relation hints;
4. keeps the event `OPEN` unless an explicit scoped admission changes it;
5. determines a natural form only when an explicit rigidity receipt is attached;
6. does not issue `TRUE` merely because determination completed;
7. commits one replayable successor field stage;
8. exposes every specialized representation as a projection lens.

The canonical guarantee is:

```text
No subsystem advances the Supernet field directly.
Only SupernetIntegrator.commit_stage creates a successor field stage.
```

Compatibility stores may still append their own materialized records. Their
sources and canonical `TranslationEvent` relations are reconciled into the next
Supernet stage.

## Open resource envelope

There is no closed resource enum and no selected universal language.

```text
ResourceEnvelope
  exact_text
  authored_by
  form_label
  language_label
  perspective / problem / action references
  capabilities
  constraints
  relation_hints
  causal predecessors
  affected perspectives
  evidence status
  adapter label
```

A note, problem, proof, simulation, learning path, service, AI proposal,
collective action, token projection, sensor reading or a form not yet named can
all enter through this envelope.

## One integration event

```text
SupernetIntegrationEvent
  exact source IDs
  authorship and perspective
  open form and language labels
  capabilities and constraints
  sensed relation hints
  causal and interaction predecessors
  affected perspectives
  evidence status
  append-only state history
```

States are:

```text
SOURCE_PRESERVED
RELATION_SENSED
ADMITTED
DETERMINED
RETURNED
REOPENED
REJECTED
```

`DETERMINED` requires both:

```text
rigidity_receipt
and determined_form
```

and is forced to retain:

```text
verdict = OPEN
truth_issued = false
```

A later explicit admission may issue a scoped verdict. Determination itself does
not.

## Replayable stages

Each committed `UnifiedFieldStage` records:

```text
ordered event history
history signature
order-independent current limit signature
OPEN / admitted / determined / returned / reopened counts
source reverse index
lens counts
previous stage
trigger event
```

The current field is reconstructible from the append-only integration events and
states. Restart does not require treating a materialized projection as the
source of truth.

## Lenses

The primary field supports these views:

```text
all
source
problem
resource
translation
selector
reopening
action
hardware
equality
agent
```

A lens filters or renders the field. It does not create another field.

The former pages remain available for diagnostics:

```text
/translation
/resources
/reopening
/equality
/hardware
/runtime
```

The primary surface is now:

```text
/
/supernet
```

## API

```text
GET  /supernet/capabilities
POST /supernet/integrate
POST /supernet/events/{id}/interact
GET  /supernet/events
GET  /supernet/events/{id}
GET  /supernet/stages
GET  /supernet/field
GET  /supernet/project?lens=<lens>
WS   /supernet/stream

POST /admin/supernet/events/{id}/state
POST /admin/supernet/reconcile
POST /admin/supernet/stage
```

Production authorization still protects mutating member and operator routes.
Transport, authentication and storage certify delivery and authorship; they do
not create translational truth.

## Hardware

The hardware gateway is a lens and adapter:

```text
integrated network sources
→ explicit rigidity receipt at safe control scope
→ determined natural form
→ bounded simulated device adapter
→ sensor return resource
→ integrate
```

The repository still permits only deterministic device twins. The unified
integrator does not enable direct physical, high-energy, nuclear, quantum,
laser, voltage, magnetic, cryogenic or plasma actuation.

## Runtime cycle

```text
reconcile pre-existing exact sources
→ run bounded living/resource/reopening/equality/hardware adapters
→ reconcile all new exact sources and TranslationEvents
→ commit exactly one cycle field stage
→ project every lens from that stage
→ repeat
```

Individual sources may commit immediate stages as they arrive. A cycle stage
then closes the current batch without replacing those historical transitions.

## Scope

This implements the requested single-node semantic unification:

```text
continuous integrator = runtime center
specialized subsystems = adapters and lenses
exact sources = immutable
field stages = append-only and replayable
natural-form determination = rigidity-dependent
TRUE = never issued by determination alone
return = successor potential, not terminal output
```

It does not yet provide a distributed causal event log, multi-node consensus,
encrypted community scopes, or direct physical hardware drivers. Those are
future adapters to the same integration operation rather than new runtimes.
