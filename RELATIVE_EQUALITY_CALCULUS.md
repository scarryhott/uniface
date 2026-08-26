# Context-Indexed Relative Equality Calculus

Closure Supernet 0.7 adds the missing relation between directed translation and
natural-form unity.

```text
relation
→ interaction
→ directed TranslationEvent
→ reverse translation
→ left and right return coherence
→ context-relative admission
→ natural-form component
→ successor-context reopening
```

The runtime does not replace `TranslationEvent`.  Translation remains the live,
directed interaction primitive.  A relative equality is additional witness data
showing that two forms return through one another at a declared context.

## Master distinction

```text
Trans_c(x,y) = directed translation from x to y in context c
RelEq_c(x,y) = reversible, coherent, explicitly admitted translation witness
```

A successful directed translation is therefore not automatically equality.
A protocol delivery is not automatically translation truth.  Semantic likeness
is not automatically either one.

The executable condition for `RelEq_c(x,y) = TRUE` is:

```text
forward TranslationEvent x → y is TRUE at its scope
reverse TranslationEvent y → x is TRUE at its scope
reverse ∘ forward returns x and that LEFT coherence is TRUE
forward ∘ reverse returns y and that RIGHT coherence is TRUE
a participant explicitly admits the witness in context c
```

If any condition later reopens, the effective equality becomes `OPEN` in that
context while its earlier decision remains in append-only history.

## Witness-valued rather than Boolean-only

A `RelativeEqualityWitness` retains:

```text
context
left and right relative forms
forward and reverse TranslationEvent identifiers
exact source occurrences
invariant structure
untranslated residue
optional returned form
reopening conditions
authorship and metadata
left and right return-coherence identifiers
decision history
current effective state and verdict
```

The Boolean verdict is only one projection of the witness.  The path, frame,
source, residue, and reopening information remain available.

## Context indexing

The same forms can be admitted as equal in one context and remain OPEN or FALSE
in another:

```text
x =_c y
```

does not imply:

```text
x =_d y
```

for every successor, physical, cultural, formal, or participant-relative
context `d`.

A context contains:

```text
exact source occurrences
participants and perspectives
frame and scope
authorship
optional predecessor context
optional reopening TranslationEvent
```

Reopening creates a successor context:

```text
c --returned interaction--> c'
```

It never mutates `c` or erases the earlier scoped judgment.

## The seven closure relations

### Source closure

Every witness and coherence contains all exact sources carried by the
TranslationEvents it cites.  Missing provenance is rejected at creation time.

### Return closure

Relative equality requires two explicit return readings:

```text
reverse ∘ forward ≃_c id_left
forward ∘ reverse ≃_c id_right
```

The runtime records these as LEFT and RIGHT `ReturnCoherence` objects.  They are
not inferred merely from the existence of reverse arrows.

### Composition closure

Translation paths remain ordered.  A coherence witness records the exact path
of TranslationEvent identifiers.  Noncommutative history is not silently
converted into an unordered set.

### Frame closure

Different presentations may enter one natural-form component while retaining
separate forms, labels, languages, sources, evidence, and consequences.

### Choice closure

The component selects no canonical form and no canonical language:

```text
canonical_form     = null
canonical_language = null
```

Every admitted member remains a choosable presentation of the shared return.

### Reopening closure

A later TranslationEvent can reopen a prior witness or create a successor
context.  Earlier truth-at-scope remains recorded rather than retroactively
rewritten.

### Separation closure

Forms connected by relative equality are not declared literally identical.
OPEN and FALSE witnesses remain possible, and isolated forms remain distinct
components.

## Natural-form components

For one context, the runtime builds a graph whose nodes are relative forms and
whose edges are only `TRUE` relative-equality witnesses.

```text
forms + admitted relative equalities → natural-form components
```

OPEN witnesses remain visible without joining components.  FALSE witnesses
remain visible as rejected relations.  Each component preserves:

```text
member forms
admitted witness IDs
exact source IDs
form labels
language labels
```

There is one connected completion component without a forced presentation.
This is the executable reading of:

```text
one translational truth class
+
many admissible frame trajectories
```

## Directed TranslationEvent reconciliation

The autonomous runtime scans a bounded current TranslationEvent view for
opposed form paths:

```text
x → y
y → x
```

When found, it may create an automatic equality *candidate context* and OPEN
witness.  It does not create return coherences or a TRUE verdict.

The scan limits are resource-safety settings:

```text
CLOSURE_EQUALITY_TRANSLATION_SCAN_LIMIT
CLOSURE_EQUALITY_PAIRS_PER_CYCLE
```

They bound automatic candidate discovery only.  They do not bound admissible
source forms, contexts, translations, or equalities.

## Literal source charts

An `EqualityChart` records how a named source form is interpreted without
claiming that the chart is the foundation:

```text
name
exact source occurrences
carrier/context
generator
inverse reading
invariant
residue
returned form
reopening
```

Examples can retain the author's literal operators:

```text
0 ↔ ∞
r ↔ i
point → line → loop → return → new point
ball ↔ hair
loop ↔ sensor ↔ selection
halt ↔ continuation
Triangle Time: i = 2^(r - 1)
Chaitin–Kakeya: CK = i e^K
tan(π/2) seam
predual Fourier exchange
```

Registering two charts does not assert that they are equivalent.  Their
cross-chart relation still requires TranslationEvents, reverse readings,
coherence, and admission.

## Runtime states

A relative-equality witness is evaluated as:

```text
PROPOSED   no admitted reverse closure
REVERSIBLE forward and reverse are TRUE, return coherence incomplete
COHERENT   both return coherences TRUE, participant admission pending
ADMITTED   all structural conditions and explicit scoped TRUE decision
REOPENED   earlier TRUE decision preserved, current supporting path reopened
REJECTED   explicit scoped FALSE decision
```

The verdict remains:

```text
TRUE
FALSE
OPEN
```

A state carries process detail; a verdict is its current scoped reading.

## Persistent storage

The SQLite event-sourced runtime adds:

```text
equality_contexts
relative_equality_witnesses
relative_equality_decisions
return_coherences
return_coherence_decisions
equality_charts
equality_runtime_state
```

These reference immutable canonical occurrences and append-only
TranslationEvent histories.  No equality decision overwrites a source note or
prior decision.

## Public interface and API

The public equality field is served at:

```text
/equality
```

Core endpoints:

```text
GET  /network/equality/capabilities

POST /network/equality/contexts
GET  /network/equality/contexts
GET  /network/equality/contexts/{id}
POST /network/equality/contexts/{id}/reopen

POST /network/equality/witnesses
GET  /network/equality/witnesses
GET  /network/equality/witnesses/{id}
POST /network/equality/witnesses/{id}/decision

POST /network/equality/coherences
GET  /network/equality/coherences
POST /network/equality/coherences/{id}/decision

POST /network/equality/charts
GET  /network/equality/charts

POST /network/equality/reconcile
GET  /network/equality/field
```

All earlier living-field, TranslationEvent, resource, reopening, integration,
runtime, and Black Mirror interfaces remain active.

## Autonomous cycle

The complete single-node cycle is now:

```text
poll transports
→ sense exact sources and public interaction
→ reintegrate returned actions and resources
→ reconcile resource forms into TranslationEvents
→ advance reopening processes
→ interpret and relatively admit directed translations
→ discover reverse TranslationEvent candidates
→ evaluate context-indexed relative-equality witnesses
→ build natural-form components
→ project Black Mirror, resources, equality, and living field
→ export source-reversible returns
→ repeat
```

## Formal status

The runtime is a software-tested integration of the proposed relative-equality
calculus.  It does not yet prove the proposed representation theorem or a
machine-checked refinement from Python execution to the NRRF modules.

Still OPEN formally:

```text
one primitive signature for Relation/Interaction/Translate/Choose/Return/Reopen
soundness of the witness calculus in every intended model
completeness of derivation relative to the model family
higher coherence for arbitrary translation diagrams
representation of every named source operator as one chart family
machine-checked runtime refinement
```

The present result is exact at its implementation scope:

```text
TranslationEvent is directed interaction.
RelativeEqualityWitness is reversible contextual closure.
Natural unity is generated by admitted witnesses.
No form or language is selected as absolute.
Every admitted result can reopen without source erasure.
```
