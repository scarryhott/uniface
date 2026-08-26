# Closure Supernet Autonomous Living Runtime

The repository contains an executable, persistent, public living-network runtime for the Uniface Closure Supernet.

## Active cycle

```text
poll digital transports
→ sense exact local and public occurrences
→ reintegrate returned collective-action consequences
→ reintegrate returned resource forms
→ advance admissible reopening processes
→ propose candidate relations
→ build source-reversible interpretation witnesses
→ apply constitutional admission rules
→ apply participant decisions
→ audit affected perspectives
→ integrate the current live resource stage
→ project Black Mirror and the living field
→ export source-reversible returns
→ reopen
→ repeat
```

Autonomy is bounded. The runtime never:

- mutates an original occurrence;
- silently normalizes notation;
- upgrades semantic likeness or protocol delivery into truth;
- forces resources into a finite ontology;
- selects one external language as canonical;
- treats public popularity, money, rank, or model confidence as moral authority;
- omits affected perspectives while claiming collective completion;
- activates destructive external actions;
- assumes the whole field is Turing complete;
- treats a local halt, settlement, finite-scope residue, or return as terminal closure;
- turns formal similarity into physical or moral fact.

## Source note on `0` and `∞`

The source notes identify `0` and `∞` as reciprocal poles. They are not the axiometry by themselves. The wider axiometry is the configured network connecting the poles with `r/i`, Triangle Time, Chaitin–Kakeya, the `tan(π/2)` seam, predual Fourier, four-i, ball–hair, loop–sensor–selection, and metavectorization.

## Agent ecology

- **InboxSensorAgent** — senses exact local `.md`, `.txt`, and `.jsonl` occurrences.
- **UnderstandingAgent** — proposes literal, operator-path, inverse-path, and semantic candidate relations.
- **InterpretationAgent** — records preservation, transformation, omission, frame, scope, affected perspectives, reverse path, and reopening.
- **AdmissionAgent** — applies the active source-preserving constitutional rule.
- **MoralAuditAgent** — blocks completeness when affected perspectives are omitted.
- **ReopeningAgent** — turns incomplete admissions into explicit OPEN seams.
- **RuleReviewAgent** — proposes versioned rule revisions from repeated seams.
- **ProjectionAgent** — builds the current source-reversible Black Mirror topology.
- **DigitalIntegrationManager** — imports and exports digital sources without granting remote systems admission authority.
- **LivingNetworkManager** — persists participants, perspectives, problems, interactions-as-solutions, actions, returns, and problem reintegration.
- **IteratedReopeningManager** — advances admissible reopening families and dependency-sensitive closed residues.
- **LiveResourceProtocolManager** — persists open resource forms, active engagements, returned resources, OPEN reintegration translations, protocol receipts, natural components, and live stages.

Neither reintegration agent declares a return to be the final solution. Each creates a source-reversible OPEN relation and exposes it for interpretation and participant-relative admission.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
closure-supernet serve
```

Open:

- public living field: `http://localhost:8000/`
- live resource continuum: `http://localhost:8000/resources`
- iterated reopening field: `http://localhost:8000/reopening`
- autonomous runtime console: `http://localhost:8000/runtime`
- API documentation: `http://localhost:8000/docs`
- health: `http://localhost:8000/health`

## Persistent storage

The SQLite runtime is event-sourced and includes the canonical relation engine:

```text
occurrences
candidate_relations
interpretations
admissions
open_seams
rules
runtime_state
events
integrations
integration_receipts
integration_runs
```

The living public field adds participant, perspective, problem, interaction,
action, return and reintegration tables. Iterated reopening adds families,
variants, ordered readings, order assessments, processes, residue rounds and
moral connections.

The resource continuum adds:

```text
resource_forms
resource_engagements
resource_translations
resource_translation_decisions
resource_returns
resource_reintegrations
resource_protocol_receipts
resource_live_stages
resource_state
```

Exact text remains in immutable `occurrences`. State changes and relations are additional records rather than replacements.

## Public relative forms

```text
Problem       = exact source + at least one real situation + remaining discretion
Note          = immutable occurrence + self-interaction / loop step
Solution      = receipt constituted by an interaction
Action        = exact collective intent + participants + affected perspectives + OPEN assumptions
Return        = exact consequence returned by action
Resource      = exact occurrence + open author-selected form/language labels
Engagement    = active resource interaction preserving transformation history
Translation   = frame-to-frame witness whose protocol and truth verdicts remain separate
ResourceReturn= a new resource form linked to its source and queued for reintegration
LiveStage     = complete current-field coverage + delivery history + order-independent limit signature
```

No quantity or quality score is stored as the foundational social value. No resource label or language is treated as complete identity.

## Public APIs

The public living API remains available under `/network/*`. Iterated reopening is under `/network/reopening/*`. The resource continuum provides:

```text
GET  /network/resources/capabilities
POST /network/resources
GET  /network/resources
POST /network/resource-engagements
GET  /network/resource-engagements
POST /network/resource-translations
GET  /network/resource-translations
POST /network/resource-translations/{id}/decision
POST /network/resource-returns
GET  /network/resource-returns
GET  /network/resource-reintegrations
POST /network/resource-reintegrate
POST /network/resource-protocol-receipts
GET  /network/resource-protocol-receipts
POST /network/resource-live/integrate
GET  /network/resource-live/stages
GET  /network/resource-field
```

## Protocol/truth boundary

A transport receipt can report success or failure. It cannot directly set a resource translation to TRUE or FALSE. Natural components are generated only from current participant-relative TRUE translation decisions.

The runtime preserves delivery order in every stage while computing the live limit signature from sorted exact resource occurrences and admitted translation pairs. The current signature is compared to a full current-batch recomputation without stopping the network.

See [`LIVE_RESOURCE_PROTOCOL.md`](LIVE_RESOURCE_PROTOCOL.md).

## Digital integrations

Supported connectors:

```text
WEBHOOK_IN
WEBHOOK_OUT
GITHUB_REPOSITORY
HTTP_JSON_FEED
```

External assertions enter as immutable sources, not truth claims. Outbound returns include Black Mirror, living-field statistics, iterated reopening, resource-stage state, and reverse source indexes.

See [`DIGITAL_SUPERNET_INTEGRATIONS.md`](DIGITAL_SUPERNET_INTEGRATIONS.md).

## Security and progress boundary

Implemented now:

- single-node durable storage;
- persistent participants and perspectives;
- public problem/action/return interface;
- open-form resources and active engagements;
- autonomous problem and resource reintegration;
- iterated reopening and dependency-order readings;
- protocol/truth separation;
- live-stage and batch-signature checking;
- exact source immutability;
- append-only state and decision history;
- digital transports, API, dashboards, tests, and Docker support.

Not yet claimed:

- production cryptographic participant authentication;
- encrypted private/community scopes;
- public cloud deployment;
- replicated multi-node storage and federation;
- genuine partially ordered concurrent event structures;
- signed commitments and resource receipts;
- machine-checked refinement from Python execution to NRRF764–769;
- empirical proof of conscious-cultural or moral outcomes.

These remain explicit next closure levels rather than hidden behind a terminal-completion claim.
