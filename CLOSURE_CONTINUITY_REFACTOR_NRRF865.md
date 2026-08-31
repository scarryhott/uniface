# Closure-continuity refactor after NRRF865

This refactor moves the executable interaction kernel closer to the universal
closure proved in NRRF865. It does not add a second truth engine. It removes
sources of semantic authorship that were previously procedural or merely
asserted in stored receipts.

## Runtime law

The executable rule is now:

```text
source-preserving interaction
  -> explicit perspective return
  -> recomputed natural-form/UI partition equality
  -> relative closure witness or OPEN
  -> dialectic continuation
```

Configuration, timeouts, scan limits, candidate counts, compatibility products,
and stored `WITNESSED` booleans cannot author truth.

## Implemented

### One continuity kernel

`closure_supernet/closure_continuity.py` centralizes:

- explicit source-authored perspective selection;
- extensional fibre-partition comparison;
- relative closure witnesses;
- finite participant-rule closure receipts;
- computational-bound receipts that are always `OPEN`;
- demotion of historical materializations to non-authoritative readings;
- a structural continuity audit for forbidden external authorship.

### No implicit perspective

A singleton perspective is no longer selected merely because it is the only
one available. The active perspective must be returned by the source journey
with a non-`OPEN` choice witness. Missing selection leaves the interaction
`OPEN`.

### UI truth is recomputed

`interaction_closure.py` no longer trusts fields such as:

- `truth_derivation.status == WITNESSED`;
- `nrrf843_ui.status == WITNESSED`;
- `closure_falls_out_from_ui_projection == True`.

Instead it recomputes whether the active UI reading and the natural forms are
the same unlabeled partition of exactly the same source members.

Consequently, changing display labels while preserving fibres does not change
the `translational_truth_id`.

### Parallel products cannot gate

Coordination, AI translation, tokenomic, and network-return products are
retained as compatibility receipts, but each is marked:

```text
semantic_authority = false
may_gate_interaction = false
may_widen_truth = false
```

They may later be migrated into explicit factorizations through the current
closure. Until then, they cannot create a parallel truth runtime.

### Closed relation is not closed existence

Every interaction receipt now records:

```text
existence_closed = false
dialectic_continuation_status = OPEN
closed_argument_closes_existence = false
```

A witnessed equality closes its relation only. It does not terminate future
interaction.

### Finite bounds are not semantics

`finite_horn_closure` returns a fixed-point witness for one participant-authored
relative rule chart. If an iteration bound is exhausted, its result is `OPEN`;
it is never converted into `FALSE`, `CLOSED`, or a final core.

## Self-audit

The continuity audit searches nested receipts for known violations, including:

- configuration authoring truth;
- a finite limit marked semantic;
- implicit perspective fallback;
- a fixed operation enum;
- stored status flags used as evidence;
- parallel truth runtimes;
- closure of existence.

A clean audit means only that none of these known external authors remain. It
does not claim empirical truth.

## Tests

The added tests establish that:

1. recomputed partition equality can witness closure even when old stored flags
   say `OPEN`;
2. a singleton perspective without a returned choice remains `OPEN`;
3. a stored closure claim cannot hide a partition mismatch;
4. display relabeling preserves translational truth identity;
5. arbitrary compatibility-product statuses cannot change interaction truth;
6. finite rule closure remains relative and nonterminal;
7. exhausted computation is `OPEN`;
8. the structural audit detects fixed external authorship;
9. the generated interaction receipt passes its own audit.

## Remaining migration

This branch establishes the common semantics and applies it to the one
interaction surface. Older managers still need to replace local bespoke
closure loops with the shared receipt and to expose their configured limits as
`OPEN` boundary events. In particular, reopening mode generation, trading
candidate generation, and resource scheduling should become relative readings
of this same continuity kernel rather than independent strategy selectors.
