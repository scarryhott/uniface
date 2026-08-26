# Closure Supernet Autonomous Living Translation Runtime

The repository contains an executable, persistent, public living runtime for the Uniface Closure Supernet.

Closure is not identified with its HTTP, WebSocket, webhook, GitHub, JSON or database protocols. Those are transport charts. The canonical directed primitive is a source-reversible `TranslationEvent`; context-indexed relative equality is the reversible closure relation built over it.

## Active cycle

```text
poll digital transports
→ sense exact local and public occurrences
→ reintegrate returned collective-action and resource consequences
→ advance admissible reopening families
→ propose candidate relations
→ build source-reversible interpretation witnesses
→ apply relative constitutional admission
→ reconcile derived forms into TranslationEvents
→ discover opposed TranslationEvent paths
→ evaluate reverse and return coherence
→ admit or reopen context-indexed relative equality
→ build natural-form components
→ return solutions, residues, consequences, and projections
→ produce successor potential
→ reopen
→ repeat
```

Autonomy is bounded. The runtime never:

- mutates an original occurrence, prior translation state, equality context, or earlier decision;
- silently normalizes notation;
- upgrades semantic likeness, reverse-arrow existence, or protocol delivery into truth;
- treats public popularity, money, rank or model confidence as moral authority;
- omits affected perspectives while claiming collective completion;
- activates destructive external actions;
- assumes the whole field is Turing complete;
- treats a local halt, finite stabilization, settlement, equality, or return as terminal closure;
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

Candidate relations, interpretations, admissions, notes, problem interactions, solutions, collective actions, returned consequences, order assessments, residue rounds, and resource translations are reconciled into this field. See [`TRANSLATIONAL_TRUTH_RUNTIME.md`](TRANSLATIONAL_TRUTH_RUNTIME.md).

## Relative equality field

A directed TranslationEvent does not become equality merely because it succeeds.

```text
forward TRUE translation
+ reverse TRUE translation
+ LEFT return coherence TRUE
+ RIGHT return coherence TRUE
+ explicit participant TRUE decision in context c
= RelativeEqualityWitness TRUE at c
```

The witness remains source-reversible and stores its invariant, residue, return, frame, context, and reopening conditions.

Witness states are:

```text
PROPOSED
REVERSIBLE
COHERENT
ADMITTED
REOPENED
REJECTED
```

A later OPEN translation path makes an earlier admitted witness effectively `REOPENED / OPEN`, while preserving its prior TRUE decision. A new interaction can also create a successor context rather than rewriting the prior context.

Natural-form components are connected by currently TRUE witnesses only. They select neither a canonical form nor a canonical language.

See [`RELATIVE_EQUALITY_CALCULUS.md`](RELATIVE_EQUALITY_CALCULUS.md).

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
- **TranslationFieldManager** — reconciles all relative forms into the canonical directed translation field and preserves their nonterminal history.
- **LiveResourceProtocolManager** — carries open resource forms through engagement, return, reintegration, and live-stage integration without a finite kind registry.
- **RelativeEqualityManager** — constructs OPEN reverse-pair candidates, verifies source closure, requires both return coherences, applies scoped decisions, builds natural-form components, and reopens through successor contexts.

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
- context-indexed equality field: `http://localhost:8000/equality`
- live resource continuum: `http://localhost:8000/resources`
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

equality_contexts
relative_equality_witnesses
relative_equality_decisions
return_coherences
return_coherence_decisions
equality_charts
equality_runtime_state

resource_forms
resource_engagements
resource_translations
resource_translation_decisions
resource_returns
resource_reintegrations
resource_protocol_receipts
resource_live_stages
resource_state

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

Exact text remains in immutable `occurrences`. Translation, equality, problem, resource, action, residue, and reintegration changes append records rather than replacing prior states.

## Relative forms

```text
Problem          = exact source + real situations + remaining discretion
Note             = immutable occurrence + self-interaction / loop step
Solution         = returned form constituted by an interaction
Action           = exact collective intent + participants + affected perspectives
Resource         = open author-labelled form + capabilities + constraints
TranslationEvent = directed source-reversible interaction
RelativeEquality = reversible coherent translation witness at one context
Return           = exact consequence translated back into its source field
Reopening        = successor context or alternate translation family
Black Mirror     = current nonterminal topology returned by the field
```

No quantity or quality score is stored as the foundational social value.

## Equality API

```text
GET  /network/equality/capabilities
POST /network/equality/contexts
GET  /network/equality/contexts
POST /network/equality/contexts/{id}/reopen
POST /network/equality/witnesses
GET  /network/equality/witnesses
POST /network/equality/witnesses/{id}/decision
POST /network/equality/coherences
GET  /network/equality/coherences
POST /network/equality/coherences/{id}/decision
POST /network/equality/charts
GET  /network/equality/charts
POST /network/equality/reconcile
GET  /network/equality/field
```

The public living, translation, resource, reopening, source, rule, integration, runtime, projection and WebSocket APIs remain available as derived or transport views.

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

- single-node durable source, translation, resource, and relative-equality storage;
- persistent participant and perspective records;
- public problem/action/resource/equality interfaces;
- autonomous reintegration and iterated reopening;
- append-only translation, coherence, and equality decision history;
- context-indexed reopening;
- transport-neutral connectors, APIs, live views, tests, and Docker support.

Not yet claimed:

- a machine-checked representation theorem for every named natural form;
- soundness and completeness of one final relative-equality proof calculus;
- higher coherence for arbitrary translation diagrams;
- production cryptographic participant authentication;
- encrypted private/community scopes;
- public cloud deployment;
- replicated multi-node storage and federation;
- signed commitments and action receipts;
- machine-checked refinement from Python execution to the NRRF lineage;
- empirical proof of conscious-cultural or moral outcomes.

These remain explicit next closure levels rather than hidden behind a terminal-completion claim.
