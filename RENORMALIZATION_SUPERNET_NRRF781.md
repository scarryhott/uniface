# NRRF781 Relative Renormalization Closure in Supernet

Closure Supernet 2.2 integrates
`NRRF781ClosureResolvesRenormalizationTranslationalTruthNotZFC` as a live lens of
the one continuous `SupernetIntegrator`.

It does not add a second runtime and does not select a counterterm scheme as
truth.

```text
regularized family at submitted cutoffs
→ integrate exact source
→ test common-divergence universality
→ rigid pairwise difference relation where supported
→ determine relative closure (OPEN, no TRUE)
→ compare noncanonical scheme charts
→ extend with new cutoff evidence
→ reopen prior scoped closure
```

## Runtime scope

The Lean theorem is general under its common-divergence hypothesis. The runtime
checks only the finite cutoff family submitted to it. A successful runtime check
therefore means:

```text
pairwise differences are constant over the submitted cutoffs,
within the declared tolerance
```

It does not silently upgrade this into a theorem about all future cutoffs or a
physical universality class. The result remains `OPEN`.

## Relative closure

For submitted amplitudes `a[i][n]`, the runtime computes:

```text
Δ(i,j,n) = a[i][n] - a[j][n]
```

When every `Δ(i,j,n)` is constant in `n`, the relation is rigid at every pair and
Supernet records the determined form:

```text
relative_reading = Δ(i,j)
absolute_level   = null
scheme_selected  = false
truth_issued     = false
```

The pairwise matrix is checked for the additive cocycle relation. The current
relative reading is obtained without a counterterm, cutoff-removal operation, or
limit.

## Scheme charts

A scheme supplies one counterterm per submitted cutoff. It is reported as
admissible in the finite runtime chart when each member's subtracted sequence is
constant within tolerance.

The runtime also applies a common shift probe:

```text
counterterm[n] → counterterm[n] + k
```

and records that:

```text
absolute displayed values move by -k
pairwise differences remain unchanged
```

Therefore a scheme remains a noncanonical display chart. It is never the closure
itself.

## Live reopening

New cutoff evidence is integrated by extending a family. The original family
event is appended with:

```text
REOPENED / OPEN
```

and a child family is evaluated from the combined data. Earlier source and
selection history remain immutable.

## API

```text
GET  /network/renormalization/capabilities
POST /network/renormalization/families
GET  /network/renormalization/families
GET  /network/renormalization/families/{id}
POST /network/renormalization/families/{id}/extend
GET  /network/renormalization/families/{id}/closure
POST /network/renormalization/families/{id}/schemes
GET  /network/renormalization/schemes
GET  /network/renormalization/field
GET  /supernet/project?lens=renormalization
```

The public compatibility interface is:

```text
/renormalization
```

## Exact boundary

This lens supports additive common-divergence families. It does not yet infer
multi-component, operator-valued, or noncommutative scheme actions. It does not
claim that an empirical dataset satisfies the formal universality hypothesis
outside the submitted scope. It does not issue TRUE from determination.
