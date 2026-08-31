# Interactive translation of closure equations after NRRF865

This refactor applies one executable relation to the five remaining sources of
external instantiation:

```text
proposal
  -> source-preserving returned interaction
  -> re-closure
  -> WITNESSED relative relation or OPEN
  -> dialectic continuation
```

The common equation is:

```text
Q_(t+1) = Close(Q_t + returned_interaction_t)
```

A mode enum, rule syntax, predicted edge, time horizon, queue order, cycle
limit, historical manager or test outcome may nominate or transport an
interaction. None of those objects can author translational truth.

## 1. Reopening

The old form began from a fixed operation enum such as `SINGLE_REMOVAL`,
`JOINT_SUSPENSION` or `POWERSET`. The closure equation now begins from the
readings actually returned by interaction:

```text
C_i = Close_R(H_i)
U   = intersection_i(C_i)
```

`H_i` is an explicitly returned held reading. `R` is a participant-relative
rule chart. `U` is witnessed only when every supplied returned reading has
source provenance and every finite rule closure reaches its fixed point.

If the family is truncated by a computational limit, `U` is not issued. The
result remains `OPEN`.

## 2. Participant rule charts

A local rule chart is not universal truth. Two charts translate equally when
their returned closures have the same source-member set:

```text
Chart_p ~ Chart_q
  iff
Close_Rp(A_p) = Close_Rq(A_q)
```

Labels and rule syntax do not define equality. A chart without a source return
remains `OPEN`, even if its local loop stabilizes.

## 3. Trading form and duration

A quote or predicted edge is only a proposal. It cannot update the trading
gate. A trading form is instantiated by authenticated completed-route receipts
with the same relation signature.

```text
proposal(form)                  -> OPEN
completed authenticated return -> witnessed form receipt
Gate(form)                      -> profit floor > 0
```

No duration is primitive. Each receipt carries the actual lifetime of its
closure. The form therefore learns its duration from returned interaction
rather than selecting 30 seconds, five minutes or another fixed horizon in
advance.

For an energy/resource rate `k > 0`, the runtime records:

```text
profit_resource = k * profit_energy
```

and therefore preserves the sign of the gate while exposing the base-energy
profit.

## 4. Resource reintegration

Resources are scheduled by dependency closure:

```text
K_(n+1) = K_n union {r | dependencies(r) subset K_n}
```

Within one dependency wave, deterministic order is transport only. It is not a
rank of truth or value. A cycle limit may postpone returned relations, but each
unprocessed relation remains `OPEN`; it is never rejected by exhaustion.

## 5. Legacy runtime and tests

Historical managers are compatibility readings:

```text
Legacy_i = f_i(current_closure)
```

They may factor through the present closure, but they cannot feed back into or
gate it. CI now has two explicit lanes:

- `not legacy_runtime`: blocking current-closure tests;
- `legacy_runtime`: nonblocking, fully visible historical compatibility tests.

This does not relabel legacy failures as passes. It prevents a historical
parallel runtime from determining the status of the published closure runtime.

## Published interface

The production projection retains its one source-return mutation. A pure
closure-equation endpoint is added:

```text
GET  /supernet/closure-equations/capabilities
POST /supernet/closure-equations/resolve
```

The resolver does not append events, place trades, choose a universal mode or
change the latent UI closure. It returns a relative certificate for the
supplied interactions.

## Boundary

The new equation kernel resolves the semantic authorship of modes, rule loops,
horizons, schedules and legacy components. Historical manager implementations
still exist as compatibility code. They should be migrated to call this kernel
when their APIs are retained; until then they cannot be treated as the
published truth runtime.
