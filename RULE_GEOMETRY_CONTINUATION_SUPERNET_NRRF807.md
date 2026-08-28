# Rule, Geometry, and Natural Continuation — NRRF807 in Supernet

Closure Supernet 3.2 integrates the executable reading of
`NRRF807RuleGeometryEqualRelationNaturalContinuation` as a lens over the same
append-only event field, Turing Being lineage, and NRRF799 completion engine.
It does not introduce an independent rule engine or geometry engine.

## One translation, two readings

For a submitted finite total translation `step : X → X` and origin `x`, the
runtime stores the unique continuation prefix

```text
continuation(x,n) = step^[n](x)
```

and derives two relations from it:

```text
RuleRel step x y  ⇔  ∃ n, y = step^[n](x)
GeomRel step x y  ⇔  cl step x = cl step y
                    ⇔  ∃ m n, step^[m](x) = step^[n](y)
```

The rule receipt keeps the directed iterate number and exact unfolded path. The
geometry receipt keeps the closure class and two continuation paths meeting at
one value.

## Non-collapse boundary

The runtime checks, on the submitted finite chart:

```text
RuleRel ⊆ GeomRel
GeomRel = EqvGen RuleRel
RuleRel = GeomRel ⇔ RuleRel is symmetric
```

A geometry witness never manufactures a forward rule witness. Two points may
share a closure because their continuations meet even when neither is reachable
from the other in the requested direction.

This preserves the distinction between:

- shared closure and directed causal lineage;
- common geometry and authorship;
- meeting in a generated equality and consenting to a forward action;
- an available reverse path and a merely symmetrized fold.

## Finite exact instances

### Four-phase ball

```text
0 → 1 → 2 → 3 → 0
```

The translation is finite and injective, every orbit is periodic, and every
backward displacement is representable by enough forward steps. The runtime
therefore verifies `rule_eq_geometry = true`.

### Two sources meeting at one return

```text
a → b ← c
    ↺
```

`a` and `c` share the geometry because both continuations reach `b`. The rule
from `a` to `c` is absent. The geometry witness retains `(m,n)=(1,1)` and does
not invent a directed path.

## Infinite theorem-level instances

The formal module also proves:

```text
(ℕ,succ): RuleRel = ≤, while GeomRel is one folded point
x ↦ x + π on ℝ: geometry relates 0 and -π, rule does not go backward
```

The live runtime records these as symbolic theorem-level examples. It does not
claim to exhaust an infinite carrier by finite execution.

## Turing Being integration

A continuation may cite a Turing Being life event. The event must already carry
an admitted source-preserving action–reaction return with completed
translational truth. Only then may the supplied real-world translation step be
projected as a rule/geometry continuation.

```text
global hair 0 executor
→ local ball ∞ reactor
→ returned global hair 0+
→ translational truth
→ natural continuation
→ rule and geometry lenses
→ OPEN next stage
```

Returned global hair `0+` is therefore read as the next indexed stage of the
same continuation, not as a second independent loop.

NRRF807 does not choose which real-world step is admissible. For an unlinked
formal finite chart, step admissibility remains `OPEN`.

## Translation morphisms

A map between two stored systems is accepted only when it intertwines the
translations:

```text
f(step₁(x)) = step₂(f(x))
```

The runtime then verifies:

```text
morphism_rule
morphism_geom
continuation_natural
map_mk_commutes
```

The same map carries directed rule witnesses, geometry classes, and every
checked continuation stage.

## Persistence

The lens adds materialized tables in the same SQLite database:

```text
natural_continuation_systems
natural_continuation_maps
natural_continuation_state
```

Each system references its canonical NRRF799 completion system and its canonical
Supernet integration event. These tables do not advance an independent field.

## API

```text
GET  /continuation
GET  /network/continuations/capabilities
GET  /network/continuations/field

POST /network/continuations/systems
POST /network/turing-being/life-events/{id}/continuation
GET  /network/continuations/systems
GET  /network/continuations/systems/{id}
GET  /network/continuations/systems/{id}/continuation
GET  /network/continuations/systems/{id}/rule
GET  /network/continuations/systems/{id}/geometry

POST /network/continuations/maps
GET  /network/continuations/maps
GET  /network/continuations/maps/{id}
```

The Supernet lens is:

```text
/supernet/project?lens=continuation
```

## Scope

The Lean module proves the general results. The Python layer evaluates finite
submitted carriers and preserves exact witnesses. It does not select the
translation step, infer physical law, collapse geometry into causality, choose a
canonical representative, or issue `TRUE` merely because a relation was
computed. Every determination remains `OPEN`.
