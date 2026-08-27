# NRRF790 Selection Completeness in Supernet

Closure Supernet 2.6 integrates
`NRRF790CompleteNaturalSelectionIncompleteForcedIsolation` as an audit lens of
the one continuous `SupernetIntegrator`.

## Four live states

```text
EMPTY_TOTAL_ISOLATION
  No symbol is admitted. Nothing can be selected.

OPEN_BRANCHING
  Two or more symbols remain admitted. No natural selection exists.

NATURAL_SELECTION
  Exactly one symbol was already admitted. Selection reports the complete
  reading and removes nothing.

FORCED_ISOLATION
  Several symbols were admitted and an actor isolated one. The final singleton
  is complete, but the original reading was not.
```

## The temporal distinction

The same final singleton can have two different histories:

```text
complete reading → natural selection
branching reading → authored isolation → singleton completion
```

Supernet retains that lineage. A forced isolation records:

```text
selected symbol
removed admissible symbols
author and scope
strict strengthening
explicit transposition symmetry witness
source event and exact sources
reopening potential
```

The symmetry witness swaps the selected symbol with another originally admitted
symbol. It preserves the original reading, moves the selected symbol, and breaks
the isolated reading. This is the executable reason the selection was not
natural before isolation.

## Orbit order

NRRF784 remains upstream. Natural selection should normally be applied to
level-unified orbit symbols rather than raw presentations:

```text
raw presentations
→ level orbits
→ admissibility reading on orbits
→ NRRF790 completeness audit
→ optional explicit representative isolation
```

A unique natural orbit does not create a canonical representative inside that
orbit.

## Runtime semantics

All readings enter through `SupernetIntegrator.integrate`. Natural selections and
forced isolations may both produce a determined singleton, but their rigidity
receipts differ:

```text
NATURAL_SELECTION
  prior_reading_complete = true
  strict_strengthening = false
  removed_admissible_symbols = []

FORCED_ISOLATION
  prior_reading_complete = false
  strict_strengthening = true
  removed_admissible_symbols = [...]
  symmetry_witness = transposition(...)
```

Both remain `OPEN`; `truth_issued=false`.

## API

```text
GET  /network/selections/capabilities
POST /network/selections/readings
GET  /network/selections/readings
GET  /network/selections/readings/{id}
GET  /network/selections/field
POST /supernet/events/{event_id}/select
GET  /supernet/project?lens=selector
```

NRRF790 remains a derived chart inside `/field-run.json` (`nrrf790`). It is not a public audit page.

## Exact boundary

The Python layer checks finite submitted symbol fields. The Lean module carries
the general theorem and axiom audit. The runtime does not infer that a forced
isolation is morally wrong or operationally unnecessary. Safety, deadlines,
physical actuation, and explicit authorship can require isolation. The runtime
only prevents that intervention from being misreported as natural completion.

The central invariant is:

```text
Natural selection never removes an admissible alternative.
```
