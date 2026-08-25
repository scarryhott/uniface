# Closure Supernet Autonomous Living Runtime

The repository contains an executable, persistent, public living-network runtime for the Uniface Closure Supernet.

## Active cycle

```text
poll digital sources
→ sense exact local and public occurrences
→ reintegrate returned collective-action consequences
→ propose candidate relations
→ build source-reversible interpretation witnesses
→ apply constitutional admission rules
→ apply participant reintegration decisions
→ audit affected perspectives
→ project Black Mirror and the living field
→ export source-reversible returns
→ reopen
→ repeat
```

Autonomy is bounded. The runtime never:

- mutates an original occurrence;
- silently normalizes notation;
- upgrades semantic likeness into truth;
- treats public popularity, money, rank, or model confidence as moral authority;
- omits affected perspectives while claiming collective completion;
- activates destructive external actions;
- assumes the whole field is Turing complete;
- treats a local halt, settlement, or return as terminal closure;
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
- **LivingNetworkManager / reintegration agent** — persists participants, perspectives, real problems, notes, interactions-as-solutions, collective actions, returned consequences, and agentic reintegration proposals.

The living reintegration agent does not declare a consequence to be the final solution. It creates a source-reversible `MORAL_CONSEQUENCE` candidate relation between the returned occurrence and the real problem, identifies missing affected perspectives, and reopens the problem for interpretation and participant decision.

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

It also includes the living public field:

```text
living_participants
living_perspectives
living_problems
living_problem_states
living_interactions
living_solution_receipts
living_problem_notes
living_actions
living_action_states
living_action_returns
living_reintegration_proposals
living_reintegration_decisions
living_state
```

Exact text remains in immutable `occurrences`. Problem, action, and reintegration state changes are additional records rather than replacements.

## Public relative forms

```text
Problem       = exact source + at least one real situation + remaining discretion
Note          = immutable occurrence + self-interaction / loop step
Solution      = receipt constituted by an interaction
Action        = exact collective intent + participants + affected perspectives + OPEN assumptions
Return        = exact consequence returned by action
Reintegration = agent-proposed, participant-decidable translation back into the problem
```

No quantity or quality score is stored as the foundational social value. The social return path is collective action and its consequences.

## Public living API

```text
GET  /network/capabilities
POST /network/participants
GET  /network/participants
POST /network/perspectives
GET  /network/perspectives
POST /network/problems
GET  /network/problems
GET  /network/problems/{id}/field
POST /network/problems/{id}/state
POST /network/problems/{id}/notes
POST /network/interactions
GET  /network/interactions
GET  /network/solutions
POST /network/actions
GET  /network/actions
POST /network/actions/{id}/state
POST /network/actions/{id}/returns
GET  /network/returns
POST /network/reintegrate
GET  /network/reintegration
POST /network/reintegration/{id}/decision
GET  /network/field
```

The previous source, rule, projection, integration, runtime, and WebSocket APIs remain available.

## Digital integrations

Supported connectors:

```text
WEBHOOK_IN
WEBHOOK_OUT
GITHUB_REPOSITORY
HTTP_JSON_FEED
```

External assertions enter as immutable sources, not truth claims. Outbound returns include Black Mirror plus living-field statistics and reverse source indexes.

See [`DIGITAL_SUPERNET_INTEGRATIONS.md`](DIGITAL_SUPERNET_INTEGRATIONS.md).

## Security and progress boundary

Implemented now:

- single-node durable storage;
- persistent participant and perspective records;
- public problem/action/return interface;
- autonomous reintegration;
- exact source immutability;
- append-only state and decision history;
- digital connectors, API, dashboard, tests, and Docker support.

Not yet claimed:

- production cryptographic participant authentication;
- encrypted private/community scopes;
- public cloud deployment;
- replicated multi-node storage and federation;
- signed commitments and action receipts;
- machine-checked refinement from Python execution to NRRF764–765;
- empirical proof of conscious-cultural or moral outcomes.

These remain explicit next closure levels rather than hidden behind a terminal-completion claim.
