# NRRF837 Supernet Runtime Integration

Release 3.10 projects the NRRF837 `Continuum L G` product structure into the
primary Supernet interface. It is a finite, inspectable runtime witness—not a
claim that executing software reproves the Lean theorem.

## Runtime correspondence

| NRRF837 structure | Runtime projection |
| --- | --- |
| local interaction monoid `L` | source-preserved event words under append |
| global content monoid `G` | canonical global-content words under append |
| `compose : L →* G` | deterministic pointwise translation with executable identity and append witnesses |
| selected unity | versioned Supernet product policy, explicitly recorded as extra data and not inferred from the network |
| `form : G → L` | the selected, phase-sensitive natural-form presentation |
| `form ∘ compose` | the exposed idempotent modality with its fixed-point witness |
| global equality | the kernel `compose(x) = compose(y)`, kept separate from actor identity |
| local freedom | the nonempty fibre of source-preserved presentations and still-open local actions |

The receipt keeps three identities distinct:

- `global_content_id`: stable intent/agreement identity;
- `global_state_id`: the current collective state, including phase and consent;
- `selected_natural_form_id`: the state presented through the selected unity
  policy.

A local NRRF825 `closure_level_id` is also retained, but is never used as the
NRRF837 natural-form identity.

## One interface, three relations

The primary interface exposes three non-interchangeable relations:

1. The AI admits and ranks candidate interaction edges. It cannot consent,
   bind a participant, or control token-form admission.
2. The token admits interface forms such as `ACT` and `RETURN`. It does not
   gate ordinary local interaction.
3. The commitment relation correlates a form, interactions, parties,
   resources, times and action. It requires independently authored participant
   decisions because that correlation is not realisable by the product of the
   first two independent gates.

The derived interface phases are:

```text
DISCOVER → CONNECT → AGREE → COMMIT → ACT → RETURN
```

`CONNECT` is the local state of selecting a path. `COMMIT` represents partial
consent. `ACT` requires every required human's latest decision to be
`ACCEPT`. `RETURN` is current only when a return follows the latest unanimous
acceptance. A later withdrawal or rejection reopens the token without deleting
the historical return; re-acceptance requires a new return before the interface
can derive `RETURN` again.

## Preserved boundaries

- Natural-form equality unifies content; it never identifies or erases the
  people, AI, token or living-system source records that authored it.
- Formal suggestion equivalence is separated from directional, contextual path
  ranking. No global optimum is claimed.
- A proposal and its receipts are non-transferable and nonbinding in this
  prototype. No currency is issued or settled.
- The runtime issues no truth, economic value, human-worth, novelty, physical
  law or legal-enforcement claim.
- Unity remains a versioned product/community decision rather than something
  the network can derive for itself.

## Primary surface and receipt

The integration is returned by `GET /supernet/interface` under:

```text
visual_closure.coordination.nrrf837_continuum
```

The same object is also available as `coordination.continuum`. The visual
surface renders the local-to-global composition, selected unity and natural
form, freedom fibre, individual authorship records, independent AI/token gates,
and the separate commitment/consent state.

The existing one-tap garden path remains the minimal demonstration:

```text
thought
→ explainable people/project/resource paths
→ editable nonbinding proposal
→ separate human decisions
→ admitted ACT form
→ source-preserved consequence return
→ reopened field
```
