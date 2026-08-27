# Handed Life, Ball Return, Hair Potential Gate — NRRF800 in Supernet

Closure Supernet 2.9 integrates the executable reading of
`NRRF800HandedLifeBallReturnHairPotentialGateFourSheafOneSheafTemporalClosure`
as one lens of the canonical `SupernetIntegrator` and as a concrete finite
instance of the NRRF799 generative-completion layer.

## Typed source data

The runtime admits only the finite chart defined by the module summary:

```text
Ball = ZMod 4
Hand = LEFT | RIGHT
ballStep(b) = b + 1 mod 4
ballReturn(h,b) = (h,b+1)
hairReturn(h,b) = (inverse(h),b-1)
```

The hair is not another phase. It is the natural completion of the ball under
its own local step. The four ball presentations form one generated completion
class, and every equality in that class retains a finite ball-step path.

## Four ball sheaves, one hair sheaf

The executable completion uses presentations `0,1,2,3` and the four local
steps around the cycle. It checks:

```text
ball cardinality = 4
ball-step order exactly = 4
no iterate below four is identity
completion classes = 1
all completion identifications have finite local lineage
completion is idempotent
```

The constant hair reading factors through that one class. The general
universality theorem remains in Lean; the runtime records a finite concrete
instance and does not replace the proof.

## Hand gate and self limit

Repeated ball returns never change the hand. Repeated hair returns invert the
hand exactly on odd iterates. The self-limit motion is the composite:

```text
selfLimit = hairReturn after ballReturn
```

so it preserves ball phase, inverts the hand, and has order exactly two.

Starting from the left-handed potential state, four inverse-hair returns visit
all four ball phases once, alternate `POTENTIAL` and `ACTUAL`, return to the
initial life state after four, and remain in the same hair class throughout.

## Naturality

For transparency, the finite runtime enumerates every bijection of the
four-phase ball and checks which commute with `ballStep`. Exactly four commute,
and all four are translations of the ball. This is an executable witness of the
module's finite naturality statement, not a substitute for the general proof.

## Human-relation chart

A submitted relation between participants `u` and `v` is read from the relative
integer separation:

```text
separation = standing(v) - standing(u)
ball phase = separation mod 4
hair = hair:unit
```

Positive separation is read `LEFT`, negative separation `RIGHT`. At equal
standing the caller supplies an explicit gate orientation; the reverse direction
uses its inverse. The runtime checks:

```text
common shifts change no relation reading
reverse directions carry inverse hands
reverse phases add to zero mod 4
both directions remain in the same hair
four units of changed separation are invisible to the ball phase
```

When before and after standings are submitted, the runtime classifies the exact
finite transition as `BALL_RETURN`, `HAIR_RETURN`, or `OPEN_OTHER`. It never
silently forces an unmatched interaction into one of the formal motions.

The explicit gate orientation is chart data, not a canonical human ranking.

## Supernet semantics

Each system, motion trace, and human-relation reading enters through:

```text
exact source
→ SupernetIntegrator.integrate
→ relation sensing
→ finite NRRF800 determination
→ OPEN return
→ successor potential
→ reopening
```

Determination records:

```text
truth_issued = false
canonical_biological_interpretation = null
biological_chirality_claimed = false
biological_life_claimed = false
human_law_claimed = false
```

The words hand, life, potential, actual, ball and hair name the constructions of
the formal chart. The runtime makes no claim about biological chirality,
biological life, or universal human behavior.

## API

```text
GET  /handed-life
GET  /network/handed-life/capabilities

POST /network/handed-life/systems
POST /supernet/events/{event_id}/handed-life
GET  /network/handed-life/systems
GET  /network/handed-life/systems/{id}

POST /network/handed-life/traces
POST /network/handed-life/human-relations
GET  /network/handed-life/records
GET  /network/handed-life/records/{id}

GET  /network/handed-life/field
GET  /supernet/project?lens=handed
```

## Exact boundary

The Python layer validates finite submitted states, steps and relations. It does
not machine-check the Lean theorem, infer a physical law, select a canonical
meaning of handedness, or turn a local determination into `TRUE`.
