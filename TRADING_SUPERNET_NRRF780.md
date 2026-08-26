# NRRF780 Classical Trading Lens in Closure Supernet

Closure Supernet 2.1 integrates the formal reading in
`NRRF780ClassicalTradingSystemLocalPricesInfCostsMultilayerValueFlow` as a
simulation-only lens of the one continuous `SupernetIntegrator`.

It does not add a second trading runtime and does not connect a brokerage or
submit market orders.

```text
six-layer transaction source
→ integrate
→ rigid quote-side execution relation where requested
→ natural-form fill determination (OPEN, no TRUE)
→ local-price / inf-cost evaluation
→ value-flow return
→ successor Supernet potential
```

## Six irredundant layers

A transaction retains:

```text
signed size · bid · ask · fill · mark · fee
```

The materialized transaction record includes a stable identity hash of all six
layers. It also includes a concrete drop-fill witness: the other five layers can
remain unchanged while the fill changes, so execution is not silently discarded.

## Local prices and inf cost

For signed size `q`:

```text
slippage = q × (fill − mark)
cost     = fee + slippage
cash     = −q × fill − fee
inventory value = q × mark
net flow = cash + inventory value
         = q × (mark − fill) − fee
         = −cost
```

The runtime records the exact identity residual `net + cost`. Cost is a derived
layer, so it does not replace bid, ask, fill, or mark. Absolute price level is not
recoverable from cost alone.

## Relative unity

The trading lens implements two explicit invariance analyses:

```text
uniform price shift:
  bid, ask, fill, mark ↦ each + k
  flow and cost unchanged

change of numéraire:
  bid, ask, fill, mark, fee ↦ λ × each
  flow and cost both scale by λ
  flow / cost unchanged when defined
```

These evaluations are returned as source-preserving OPEN Supernet events.

## Spread crossing

In `SELECTOR_QUOTE` mode, the relation is rigid:

```text
positive signed size (buy)  → fill = ask
negative signed size (sell) → fill = bid
```

The selected fill is recorded through the normal rigidity-receipt path of the
natural-form selector. Determination remains `OPEN` and records
`truth_issued=false`.

When mark is the midpoint, crossing cost is:

```text
fee + |size| × spread / 2
```

and the immediate marked value flow is its negative.

## Systems, circuits, and price holonomy

A system evaluation sums transaction cost and net flow and checks:

```text
system net = −system cost
```

A circuit evaluation accepts edge-local price moves and nonnegative charges:

```text
price holonomy = Σ local price move
total friction = Σ charge
circuit net     = price holonomy − total friction
```

If price holonomy is zero, the price field is exact for that circuit, a global
token reading is available, and the round trip returns exactly minus friction.
A profitable circuit necessarily has positive price holonomy exceeding friction
and is therefore nonexact in this chart.

## Time P&L

The constant-position evaluator records:

```text
P&L = position × (end mark − start mark) − accumulated cost
```

If the market returns to its starting mark, P&L is exactly minus accumulated
cost. Positive P&L is equivalent to the marked price move beating cost.

## One Supernet runtime

Every transaction and analysis enters through:

```python
await runtime.integrate_resource(ResourceEnvelope(..., adapter_label="trading"))
```

The trading tables are materialized views. The canonical field remains the
append-only Supernet integration history. The `trading` lens is available through:

```text
GET /supernet/project?lens=trading
```

## API

```text
GET  /network/trading/capabilities
POST /network/trading/selector
POST /network/trading/transactions
GET  /network/trading/transactions
POST /network/trading/systems
GET  /network/trading/systems
POST /network/trading/invariance/shift
POST /network/trading/invariance/numeraire
POST /network/trading/circuits
GET  /network/trading/circuits
POST /network/trading/pnl
GET  /network/trading/pnl
GET  /network/trading/field
```

The public compatibility interface is:

```text
/trading
```

## Operational boundary

This implementation is an evaluator and simulator. It has no brokerage
connector, exchange credential store, live market-data feed, order router, or
automatic order-submission endpoint. Nothing in the formal result or software
constitutes financial advice or a claim of profitable strategy performance.
