# Closure Supernet Autonomous Living Translation Runtime

The repository contains an executable, persistent, public living runtime for the Uniface Closure Supernet.

Closure is not identified with its HTTP, WebSocket, webhook, GitHub, JSON or database protocols. Those are transport charts. The canonical live primitive is a source-reversible `TranslationEvent`.

## Active cycle

```text
poll digital transports
→ sense exact local and public occurrences
→ reintegrate returned collective-action consequences
→ advance admissible reopening families
→ propose candidate relations
→ build source-reversible interpretation witnesses
→ apply relative constitutional admission
→ reconcile derived forms into Translation Events
→ return solutions, residues, consequences, and projections
→ produce successor potential
→ reopen
→ repeat
```

Autonomy is bounded. The runtime never:

- mutates an original occurrence or prior translation state;
- silently normalizes notation;
- upgrades semantic likeness or protocol delivery into truth;
- treats public popularity, money, rank or model confidence as moral authority;
- omits affected perspectives while claiming collective completion;
- activates destructive external actions;
- assumes the whole field is Turing complete;
- treats a local halt, finite stabilization, settlement or return as terminal closure;
- turns formal similarity into physical or moral fact.

## Source note on `0` and `∞`

The source notes identify `0` and `∞` as reciprocal poles. They are not the axiometry by themselves. The wider axiometry is the configured network connecting the poles with `r/i`, Triangle Time, Chaitin–Kakeya, the `tan(π/2)` seam, predual Fourier, four-i, ball–hair, loop–sensor–selection, and metavectorization.

## Live translation field

Each translation records:

```text
exact source occurrences
source and target relative forms
participant and perspective traces
what is preserved
what is transformed
what remains untranslated
frame and admission scope
affected perspectives
predecessor translations
returned form
successor potential
reopening conditions
```

Its state history is append-only:

```text
PROPOSED
INTERPRETED
ADMITTED
RETURNED
REOPENED
REJECTED
```

Candidate relations, interpretations, admissions, notes, problem interactions, solutions, collective actions, returned consequences, order assessments and residue rounds are reconciled into this field. See [`TRANSLATIONAL_TRUTH_RUNTIME.md`](TRANSLATIONAL_TRUTH_RUNTIME.md).

## Agent ecology

- **InboxSensorAgent** — senses exact local `.md`, `.txt`, and `.jsonl` occurrences.
- **UnderstandingAgent** — proposes literal, operator-path, inverse-path, and semantic candidate relations.
- **InterpretationAgent** — records preservation, transformation, omission, frame, scope, affected perspectives, reverse path, and reopening.
- **AdmissionAgent** — applies the active source-preserving constitutional rule.
- **MoralAuditAgent** — blocks completeness when affected perspectives are omitted.
- **ReopeningAgent** — turns incomplete admissions into explicit OPEN seams.
- **RuleReviewAgent** — proposes versioned rule revisions from repeated seams.
- **ProjectionAgent** — builds the current source-reversible Black Mirror topology.
- **DigitalIntegrationManager** — transports digital sources and returns without granting remote systems admission authority.
- **LivingNetworkManager** — persists participants, perspectives, real problems, notes, interactions-as-solutions, collective actions, returns, and reintegration proposals.
- **IteratedReopeningManager** — computes explicit reopening families, dependency-order effects, finite residues, and residue-relative moral connections.
- **TranslationFieldManager** — reconciles all of those relative forms into the canonical live translation field and preserves their nonterminal history.

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
- live translation field: `http://localhost:8000/translation`
- iterated reopening field: `http://localhost:8000/reopening`
- autonomous runtime console: `http://localhost:8000/runtime`
- API documentation: `http://localhost:8000/docs`
- health: `http://localhost:8000/health`

## Persistent storage

The SQLite runtime is event-sourced and includes:

```text
occurrences
candidate_relations
interpretations
admissions
open_seams
rules
runtime_state
events

translation_events
translation_states
translation_runtime_state

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

reopening_families
reopening_variants
ordered_readings
order_assessments
reopening_processes
residue_rounds
residue_moral_connections
reopening_state

integrations
integration_receipts
integration_runs
```

Exact text remains in immutable `occurrences`. Translation, problem, action, residue, and reintegration changes append records rather than replacing prior states.

## Relative forms

```text
Problem       = exact source + real situations + remaining discretion
Note          = immutable occurrence + self-interaction / loop step
Solution      = returned form constituted by an interaction
Action        = exact collective intent + participants + affected perspectives
Return        = exact consequence translated back into the problem
Reopening     = alternate translation family whose shared residue becomes new potential
Black Mirror  = current nonterminal topology returned by the translation field
```

No quantity or quality score is stored as the foundational social value.

## Translation API

```text
GET  /network/translations/capabilities
POST /network/translations
GET  /network/translations
POST /network/translations/compose
POST /network/translations/reconcile
GET  /network/translations/field
GET  /network/translations/{id}
POST /network/translations/{id}/state
```

The public living, reopening, source, rule, integration, runtime, projection and WebSocket APIs remain available as derived or transport views.

## Transport integrations

Supported transports:

```text
WEBHOOK_IN
WEBHOOK_OUT
GITHUB_REPOSITORY
HTTP_JSON_FEED
```

External assertions enter as immutable sources, not truth claims. Outbound returns include source reverse indexes and explicitly declare that protocol is transport-only.

## Security and progress boundary

Implemented now:

- single-node durable source and translation storage;
- persistent participant and perspective records;
- public problem/action/return interface;
- autonomous reintegration and iterated reopening;
- append-only translation state history;
- transport-neutral connectors, APIs, live views, tests, and Docker support.

Not yet claimed:

- production cryptographic participant authentication;
- encrypted private/community scopes;
- public cloud deployment;
- replicated multi-node storage and federation;
- signed commitments and action receipts;
- machine-checked refinement from Python execution to NRRF761–768;
- empirical proof of conscious-cultural or moral outcomes.

These remain explicit next closure levels rather than hidden behind a terminal-completion claim.
