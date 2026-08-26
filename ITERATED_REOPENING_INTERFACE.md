# Iterated Reopening Interface

This document maps `NRRF768IteratedReopeningAdmissibleFamiliesDependencyOrder`
into the executable Closure Supernet living runtime.

## Integration status

The NRRF768 digital layer is merged into `main` as Closure Supernet runtime
version `0.4.0`. The public API, autonomous cycle, persistent reopening store,
dependency-order classifier, residue projection and residue-relative moral
connection are exercised by the repository test suite and CI.

The Lean module and the Python implementation have different statuses:

- NRRF768 is machine-checked under its stated formal reading.
- The runtime is a source-preserving, software-tested realization of selected
  interface commitments.
- No machine-checked refinement theorem from Python execution to Lean has yet
  been proved.

## Living cycle

```text
ordered assumptions
→ nonempty admissible reopening family
→ explicit closure of each reopening
→ remainingStar residue
→ next round's assumptions
→ further reopening
```

The runtime never exposes a global `FINAL_CORE` state. A finite executable
process may report:

```text
STABLE_AT_CURRENT_FINITE_SCOPE
```

That means only that the current finite occurrence universe, closure rules and
reopening generator produced no further change. New interactions, rules,
translations or source occurrences may create a later process that reopens it.

## Exact source objects

Every assumption, lesson and returned reading is represented by an immutable
canonical occurrence identifier. A reopening family and residue point back to
those occurrences through a source reverse index.

The runtime does not infer semantic closure from embeddings. Its executable
closure chart uses explicit participant-supplied finite implication rules:

```json
{
  "premise_occurrence_ids": ["a", "b"],
  "conclusion_occurrence_id": "lesson",
  "label": "optional source description"
}
```

The least finite saturation under those implications is a derived digital
chart. It is not claimed to be the only meaning of the source notes' closure.

## Reopening families

Supported generated families are:

```text
TRIVIAL
SINGLE_REMOVAL
JOINT_SUSPENSION
POWERSET
CUSTOM
```

`CUSTOM` accepts explicit held ordered occurrences, allowing suspensions,
translations and replacements that are not reducible to deleting one member.

For a nonempty family `F`, the runtime computes:

```text
remainingStar(F) = intersection of closure(T), for every T in F
```

It then checks that closing the residue again leaves it unchanged.

The executable `POWERSET` mode is bounded by
`CLOSURE_REOPENING_POWERSET_LIMIT`. That is a resource-safety limit, not a
foundational restriction on NRRF768's admissible families.

## Dependency order

An ordered reading records:

```text
exact reading occurrence
held occurrence sequence
dependency edges
declared meaning key
participant
problem
```

Two readings with the same held content are classified as:

```text
SAME_READING
CONTENT_PRESERVING
MEANING_CHANGING
```

A meaning-changing reorder creates an OPEN relation and OPEN seam. The runtime
therefore does not silently replace an ordered argument, historical sequence,
learning path or cultural reading with an unordered set.

## Iterated residue rounds

A reopening process carries:

```text
real problem
initial assumptions
family generator
explicit closure rules
maximum executable rounds
optional previous process
```

Each autonomous cycle advances at most the configured number of ACTIVE
processes by one round. A residue round records:

```text
input assumptions
reopening family
remainingStar
closedness witness result
strict reopening flag
previous round
```

The process states are:

```text
ACTIVE
STABLE_AT_CURRENT_FINITE_SCOPE
MAX_ROUNDS_REACHED
REOPENED
```

There is deliberately no terminal moral-core state.

## Moral connection on the residue

A moral connection compares two participant understandings against one residue
round. It holds when both understandings include the shared residue. Full
understandings need not be equal.

The projection preserves separately:

```text
shared residue
participant A plurality outside the residue
participant B plurality outside the residue
```

This operationalizes connection through what survives every currently
admissible reopening while preserving difference outside it.

## Runtime integration

The autonomous cycle now includes:

```text
sense digital and public interactions
→ reintegrate returned action consequences
→ advance active reopening processes
→ propose source relations
→ interpret and admit
→ preserve OPEN seams
→ build Black Mirror
→ build living field with iterated reopening projection
→ export source-reversible returns
→ repeat
```

The public interfaces are:

```text
/reopening
/network/reopening/capabilities
/network/reopening/families
/network/reopening/readings
/network/reopening/order-assessments
/network/reopening/processes
/network/reopening/rounds
/network/reopening/moral-connections
/network/reopening/field
```

## Non-collapse boundaries

The implementation does not:

- overwrite an assumption or lesson occurrence;
- treat order as presentation-only without evidence;
- auto-admit semantic similarity as identity;
- call finite stabilization final truth;
- require full agreement outside the residue;
- assume Turing completeness;
- rename `0` and `∞` as the entire axiometry;
- convert the runtime correspondence into a physical or moral law.

The living field remains:

```text
real problem
→ ordered assumptions
→ admissible reopening family
→ shared residue
→ residue-relative connection
→ collective interaction
→ returned consequence
→ new reopening process
```
