# Representation-Free Self-Limit and Inversion in Supernet

Closure Supernet 2.7 integrates the readings of
`NRRF795NoRepresentationUniquePredictionClosureDerivationNaturalForms` and
`NRRF796SelfLimitInversionEqualityOneHairClosureBall` through the one canonical
`SupernetIntegrator`.

## One source relation

A submitted finite local relation is a real 3×3 matrix `A`. The source matrix is
preserved exactly. The runtime adds no carrier or faithful encoding before it
computes the closure readings.

```text
A
→ relInv(A) = -Aᵀ
→ symmetric / hair split
→ scale + neutral split of the symmetric sector
→ one normalized hair vector
→ exact self-limit content receipt
→ OPEN return and reopening
```

The Lean modules prove uniqueness relative to their stated closure conditions.
The Python layer checks one finite submitted matrix and records the resulting
witnesses; it is not a replacement for the proof or axiom audit.

## Inversion

The executable chart checks:

```text
relInv(relInv(A)) = A
divg(relInv(A)) = -divg(A)
hair(relInv(A)) = hair(A)
```

It derives:

```text
return-symmetric = (A + Aᵀ) / 2
hair part        = (A - Aᵀ) / 2
scale part       = trace(A)/3 · I
neutral part     = return-symmetric - scale part
```

The hair part is reconstructed from its inverse axial vector. For transparency,
the runtime also returns the coordinate-curl chart, which is twice that normalized
vector under the standard axial-matrix convention.

## Self-limit chart

The runtime uses the Frobenius-squared orthogonal decomposition:

```text
||A||² = ||scale||² + ||hair||² + ||neutral||²
```

This is an executable finite chart of the formal self-limit reading. It records:

```text
pure scale saturation
pure hair saturation
joint scale+hair saturation iff neutral = 0
invariance under -transpose
```

The implementation does not claim that this runtime norm is the only possible
physical measure of content.

## One hair, four scoped constructions

The runtime gives all four constructions the same normalized-hair operation while
preserving their distinct definitions and hypotheses.

### Entanglement order defect

Two submitted hair vectors are converted to axial translations. Their matrix
commutator is evaluated. In this axial-input chart it is pure hair, reverses sign
when the inputs are exchanged, and vanishes exactly when the two axial matrices
commute.

### Superposition

Submitted matrices are summed. The runtime checks linearity of the hair reading
and can record destructive hair cancellation with a nonzero neutral residue.
Reading cancellation is not treated as state annihilation.

### Singularity seam

Away from the seam, the hair is a tangent multiple of one supplied direction. At
the seam, the runtime uses a separately typed seam-field construction whose hair
is extinguished. It explicitly records that this zero is not a finite solution of
the empty ratio equation.

### Demon neutral no-gain

The endpoint checks one submitted neutral input/output witness. It verifies the
premises and conclusion for that witness only. It does not infer a universal
linear operator theorem or a physical thermodynamic law.

## Selection status

The mathematical readings are recorded as natural determinations under the
module's declared admissibility conditions:

```text
representation_used = false
forced_isolation = false
canonical_representation = null
canonical_physical_interpretation = null
```

A later selection among several experimental realizations must pass through the
NRRF790 selector audit and is a forced isolation unless the realization relation
itself becomes complete.

## API

```text
GET  /network/inversion/capabilities
POST /network/inversion/relations
POST /supernet/events/{event_id}/self-limit
GET  /network/inversion/relations
GET  /network/inversion/relations/{id}

POST /network/inversion/constructions/entanglement
POST /network/inversion/constructions/superposition
POST /network/inversion/constructions/singularity
POST /network/inversion/constructions/demon
GET  /network/inversion/constructions
GET  /network/inversion/constructions/{id}

GET  /network/inversion/field
GET  /supernet/project?lens=inversion
```

The compatibility UI is `/self-limit`.

## Exact boundary

This layer does not establish empirical quantum entanglement, physical
superposition, a spacetime singularity, Maxwell-demon thermodynamics, gravity,
or quantum gravity. The names refer to constructions defined by the formal module
and executable chart. Every returned event remains `OPEN`, `truth_issued=false`,
and `physical_law_claimed=false`.
