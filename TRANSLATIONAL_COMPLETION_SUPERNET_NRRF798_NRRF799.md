# Natural Translational Completion in Supernet

Closure Supernet 2.8 integrates the readings of
`NRRF798UnifyFullClosureThroughTranslationalTruth` and
`NRRF799NaturalTranslationalCompletionEquallyGlobalLocalGenerativeContinuity`
through the one canonical `SupernetIntegrator`.

## Runtime identity

The runtime starts from a bare submitted local step relation. It does not require
that relation to be reflexive, symmetric or transitive.

```text
admitted local step
→ symmetric finite reach
→ connected completion class
→ quotient map
→ locally invariant readings
→ global translational truths
→ OPEN return
→ later local step reopens the completion
```

Only steps explicitly marked `admitted_for_completion=true` generate the
completion. Directed occurrences that lack the required admission, consent or
source-preservation witnesses can remain in the event graph without becoming
closure identifications.

## Generative continuity

For a finite submitted graph, Supernet records the cumulative stages:

```text
Within 0
Within 1
...
Within n
```

where stage `n` contains every ordered pair joined by a path of at most `n`
admitted symmetric moves. The stages are monotone and the final stage is exactly
the generated completion. Every quotient equality has a concrete finite path
receipt; no global identification is created without local lineage.

The executable runtime is finite. The Lean theorem establishes the general
pointwise-finite result without requiring one uniform finite bound for an
arbitrary infinite carrier.

## Equally local and global

A submitted reading is checked twice:

```text
local invariant  = equal on every admitted generating step
global invariant = constant on every generated completion class
```

The runtime verifies that these conditions agree and, when they hold, constructs
the unique quotient-level factorization.

A reading additionally `decides_completion` when equal reading values occur
exactly on the same completion classes. In that case its range is an executable
presentation of the quotient, matching the generic reading theorem used by
NRRF798.

Predicate-valued readings are treated as translational truths. Supernet also
constructs one canonical class-indicator truth per completion class, which is
sufficient to separate any two distinct classes. This is the finite runtime
receipt for recovering the global closure from locally invariant truths.

## Completion closure

Pushing every admitted step through the quotient map yields equality of quotient
classes. Therefore the runtime records:

```text
pushed_step_generates_only_equality = true
completion_closed = true
completion_idempotent = true
```

This is closure relative to the current admitted step relation. A later local
translation can reopen the prior event, generate a child completion and merge
previously distinct classes while retaining the historical quotient.

## Functorial maps

A submitted map between two completion systems is accepted as
relation-preserving only when each admitted source step maps into one target
completion class. It then induces one quotient map and satisfies the runtime
`map_mk` commuting receipt. Identity maps and composed maps are retained with
explicit parent-map lineage.

## Persistence

The materialized lens adds:

```text
translational_completion_systems
translational_completion_maps
translational_completion_state
```

These tables are projections of the canonical append-only integration log. Each
system retains its exact source occurrence, parent completion, local steps,
finite paths, quotient classes, invariant readings, truths and reopening
history.

## API

```text
GET  /network/completion/capabilities
POST /network/completion/systems
POST /supernet/events/{event_id}/complete
POST /network/completion/systems/{id}/extend
GET  /network/completion/systems
GET  /network/completion/systems/{id}
GET  /network/completion/systems/{id}/witness?source=...&target=...

POST /network/completion/maps
POST /network/completion/maps/compose
GET  /network/completion/maps
GET  /network/completion/maps/{id}

GET  /network/completion/field
GET  /supernet/project?lens=completion
```

The compatibility interface is `/completion`.

## Exact boundary

The Python runtime computes a finite graph completion and executable receipts. It
is not the Lean proof or axiom audit. It does not infer that a one-way human
interaction is reciprocal, consented or equivalence-generating. It selects no
canonical representative and issues no automatic truth verdict.

```text
canonical_representative_selected = false
runtime_is_formal_proof = false
truth_issued = false
```
