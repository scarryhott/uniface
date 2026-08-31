# Interactive translation of closure equations: NRRF866 runtime

Supernet 3.22 makes the finite NRRF866 relation part of every closure UI
contract. It is not a label attached after rendering. The observer–observed
interaction is still the semantic primitive; the runtime first derives its
translation witness and only then derives a `closure_naturality_equations`
object from the resulting chart family.

There is no new production API. The existing contract and its one
source-preserving return remain the only public interaction surface.

## Executable finite interpretation

For the runtime carrier:

```text
chart        = one explicit perspective reading
hair         = faithful display relabelling between readings
natural form = canonical section of the common reading kernel
pull         = restriction along a nested arena inclusion
closure fibre = equality of natural forms
```

The derivation proceeds only from contract operands:

```text
observer–observed interaction
→ interactive translation witness
→ perspective readings
→ faithful hair equations and connected translation class
→ common reading kernel
→ canonical natural-form section
→ exact pull square at each continuation prefix
→ monotone distinction growth
→ saturation at the full reachable carrier
```

Each pull stage identifies the exact prior states equal to the newly reached
state. It content-addresses those prior fibres independently in every
translated reading and in the canonical section. Equality of the digests—not
merely equality of fibre sizes—witnesses that the naturality square commutes.
The stage's distinction count is the number of previously reached states that
the new state separates. It can stay fixed or grow, never shrink. Full reach
must recover the complete closure partition.

The equation object also checks that the active chart is exactly the displayed
projection and that faithful hair witnesses connect the whole finite chart
family. Thus the runtime statement “closure fibres are translation classes”
is not inferred from coincident block sizes or trusted status flags.

## Independent acceptance

Python derives and seals the equation object while building the contract. The
contract audit rederives it exactly. The browser then independently rebuilds:

- chart kernels and their canonical section;
- every supplied hair relabelling;
- the translation-witness graph;
- every restricted-arena pull square;
- distinction growth and full-reach saturation; and
- the equation object's content ID.

Only after those equations match does the browser verify projective geometry
and the outer contract ID. A local return commitment binds both the latent
contract ID and its exact `closure_naturality_equations.id`. The server checks
both before appending an occurrence or integration event, and the durable
receipt retains the equation-system ID.

## Relation to NRRF865

The broad NRRF865 resolver remains an opt-in research adapter for reopening,
rule-chart, trading, resource, and legacy-runtime investigations. It is not
mounted in production. NRRF866 is an internal pure derivation inside the one
production UI contract, not a parallel truth runtime or mutation route.

## Honest boundary

This is a finite executable interpretation of the formal relation. It does
not re-prove Lean, validate the Lean source at runtime, establish a physical
cosmology, infer consciousness, or issue truth:

```text
formal_source_verified_by_runtime = false
runtime_reproves_lean = false
universe_growth_is_relational_arena_growth = true
physical_cosmology_claimed = false
truth_issued = false
```

NRRF866 proves its general statements inside the formal chart/hair/arena
model. The runtime checks the corresponding finite quotient for the
interactive carrier it has actually received.
