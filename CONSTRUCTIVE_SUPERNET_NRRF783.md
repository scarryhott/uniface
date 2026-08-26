# NRRF783 Constructive Axiometric Forms in Supernet

Closure Supernet 2.3 integrates the constructive formal reading from:

```text
NRRF783AxiometricFormsUnifiedWithoutClassical
NRRF783TranslationalTruthFormsWithoutClassical
```

as an explicit-witness lens of the one continuous `SupernetIntegrator`.

The Lean development proves the theorems and audits their axioms. The Python
runtime does not replace that proof. It executes finite witness data and records
exactly which constructive structure was supplied.

## Axiometric form

A runtime form contains:

```text
source carrier A
presentation carrier B
encode : A → B
evaluate : B → A
```

The section/encoding is part of the submitted datum. The runtime never starts
from a bare surjectivity claim and then chooses a section.

It checks:

```text
U1: evaluate(encode(a)) = a
```

and constructs:

```text
hold(b) = encode(evaluate(b))
```

Then it checks the derived holding equation:

```text
U2: hold(hold(b)) = hold(b)
```

Closing is read through the explicit defect:

```text
defect = { b | hold(b) ≠ b }
U3      = defect is empty
```

The materialized evaluation also reports the familiar readings:

```text
encode injective
evaluate surjective
encode surjective
evaluate injective
fixed presentations
```

A U1-valid form enters the canonical Supernet history with a rigidity receipt and
a `DETERMINED / OPEN` state. The result then returns as successor potential. No
truth verdict is inferred.

## Form from an idempotent translation

Given an explicit total translation:

```text
hold : B → B
```

the runtime checks idempotence and constructs:

```text
A        = fixed points of hold
encode   = inclusion of fixed points
evaluate = hold
```

No representative is selected from an existence proposition. The fixed data are
computed directly from the submitted translation.

## Translational truth

A constructive translational closure supplies:

```text
finite commutative group G
sites I
base site i₀ ∈ I
levels : I → G
```

The group operation, identity, inverses, associativity, and commutativity are
checked exhaustively over the submitted finite table.

The base site is explicit input. The runtime does not use a hidden nonempty-index
choice to manufacture one.

It computes:

```text
relative(i,j) = -levels(i) + levels(j)
```

and verifies the cocycle equation:

```text
relative(i,j) + relative(j,k) = relative(i,k)
```

The absolute level chart remains noncanonical.

## Constructive bridge form

The common-shift orbit is presented as a closing axiometric form:

```text
source carrier       = group shifts
presentation carrier = shifted level charts
encode               = shift ↦ chart
evaluate             = chart ↦ shift
```

Because the base site was supplied, the shift reading is computable. The bridge
form satisfies U1 and U3 in the finite runtime chart.

## Chart comparison and overlap

For a second submitted level chart, the runtime derives the candidate common
shift from the base site and checks it at every site.

When it succeeds:

```text
one unique common shift exists
relative potentials agree
the charts present one closure orbit
```

This is the executable witness form of overlap forcing equality. The runtime does
not claim a global `equal or disjoint` dichotomy without a witness.

## Supernet states

Every form and translational closure enters through:

```python
await runtime.integrate_resource(
    ResourceEnvelope(..., adapter_label="constructive")
)
```

Records carry:

```text
section_carried_as_data = true
base_site_supplied = true
site_chosen_by_runtime = false
classical_choice_required = false
excluded_middle_required = false
runtime_is_formal_proof = false
truth_issued = false
```

The first four fields describe the execution contract. The fifth-to-last
distinction is important: machine-checked absence of classical principles belongs
to the Lean audit, not to a claim inferred from running Python.

## API

```text
GET  /network/constructive/capabilities

POST /network/constructive/forms
POST /network/constructive/forms/from-idempotent
GET  /network/constructive/forms
GET  /network/constructive/forms/{id}

POST /network/constructive/translations
GET  /network/constructive/translations
GET  /network/constructive/translations/{id}
POST /network/constructive/translations/{id}/compare

GET  /network/constructive/comparisons
GET  /network/constructive/field
GET  /supernet/project?lens=constructive
```

The compatibility interface is:

```text
/constructive
```

## Exact boundary

This layer uses finite, explicitly enumerated carriers and groups so the witness
checks are executable. It does not claim to replace arbitrary Lean types,
quotients, higher coherences, or the axiom audit. It does not issue TRUE from a
valid form and does not turn a chosen display chart into an absolute language.

The live relation is:

```text
explicit relation
→ explicit witness
→ determined form
→ relative return
→ successor potential
```
