# Closure Supernet Autonomous Runtime

This repository contains an executable runtime for the Uniface Closure Supernet.

## What autonomous means

The process runs continuously without requiring a person to manually advance every stage:

```text
sense exact occurrences
→ propose candidate relations
→ build source-reversible interpretation witnesses
→ apply constitutional admission rules
→ project the current Black Mirror topology
→ reopen incomplete relations
→ inspect repeated seams and propose rule revisions
→ repeat
```

Autonomy is bounded. The runtime never:

- mutates an original occurrence;
- silently normalizes notation;
- upgrades semantic likeness into truth;
- activates destructive external actions;
- assumes the whole field is Turing complete;
- treats a local halt or return as terminal closure;
- turns formal similarity into physical or moral fact.

The runtime may autonomously create candidate relations, interpretations, OPEN seams, projections, and proposed rule versions. The conservative default auto-admits only exact source-preserving duplicates. Stronger unifications remain OPEN until author confirmation, formal proof, or evidence is attached.

## Source note on `0` and `∞`

The source notes identify `0` and `∞` as reciprocal poles. They are not called axiometries by themselves. The broader axiometry is the configured network of operations relating the poles to `r/i`, Triangle Time, Chaitin–Kakeya, seams, paths, returns, sensor–selection, and reopening.

The runtime keeps the compatibility key `ZERO_INFINITY`, but its source role is `reciprocal poles`.

## Agents

- **InboxSensorAgent** — watches the inbox for exact `.md`, `.txt`, and `.jsonl` occurrences.
- **UnderstandingAgent** — proposes literal, operator-path, inverse-path, and semantic candidate relations.
- **InterpretationAgent** — records preservation, transformation, omission, frame, scope, affected perspectives, reverse path, and reopening.
- **AdmissionAgent** — applies the active source-preserving constitutional rule.
- **MoralAuditAgent** — blocks global completeness when affected perspectives are omitted.
- **ReopeningAgent** — turns incomplete admissions into explicit OPEN seams.
- **ProjectionAgent** — generates the current Black Mirror topology with reverse source indexes.
- **RuleReviewAgent** — notices repeated seams and proposes versioned rule revisions without rewriting history.
- **DigitalIntegrationManager** — polls configured digital sources, records receipts and cursors, imports exact occurrences, and exports event/projection returns without granting remote systems authority over admission.

An optional OpenAI-compatible provider can refine interpretation witnesses. It remains a derived chart and is subject to the same admission policy.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
closure-supernet serve
```

Open:

- dashboard: `http://localhost:8000/`
- API documentation: `http://localhost:8000/docs`
- health: `http://localhost:8000/health`

For a repository bootstrap:

```bash
closure-supernet bootstrap .
closure-supernet run --cycles 5
```

## Inbox operation

Drop source files into `runtime_data/inbox/`. Every autonomous cycle scans the directory. A source location plus checksum prevents repeated ingestion while the original file remains untouched.

## Optional interpretation model

```bash
export CLOSURE_LLM_MODE=compatible
export CLOSURE_LLM_API_KEY=...
export CLOSURE_LLM_BASE_URL=https://api.openai.com/v1
export CLOSURE_LLM_MODEL=gpt-5-mini
```

Without a model key the runtime remains operational using deterministic, source-preserving interpretation witnesses.

## Storage

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
integrations
integration_receipts
integration_runs
```

Original occurrences have no update endpoint. Revised notes are new occurrences linked by typed relations. Rules are versioned; historical outputs retain the rule version that generated them. Integration records persist configurations, cursor state, environment-variable names for secrets, idempotent delivery receipts, and run history. Secret values are not stored.

## Digital integrations

Supported connectors:

```text
WEBHOOK_IN
WEBHOOK_OUT
GITHUB_REPOSITORY
HTTP_JSON_FEED
```

The connector cycle is:

```text
poll enabled pull sources
→ import immutable exact occurrences
→ run local understanding and admission
→ build Black Mirror projection
→ export new events and the source-reversible projection
→ advance connector cursors
→ reopen
```

External assertions enter as sources, not truth claims. An external system cannot self-certify a relation as locally TRUE.

Register a GitHub source:

```bash
closure-supernet integration-add \
  --name notes-repository \
  --kind GITHUB_REPOSITORY \
  --secret-env GITHUB_TOKEN \
  --config '{"repository":"owner/repo","ref":"main","include":["**/*.md","**/*.lean"]}'

closure-supernet integration-poll
```

See [`DIGITAL_SUPERNET_INTEGRATIONS.md`](DIGITAL_SUPERNET_INTEGRATIONS.md) for the protocol, signing, provenance, cursor, API, and security details.

## API

```text
POST /occurrences
GET  /occurrences
GET  /candidate-relations
GET  /interpretations
GET  /admissions
POST /interpretations/{id}/author-decision
GET  /open-seams
GET  /projection
GET  /events
POST /runtime/cycle
POST /runtime/start
POST /runtime/stop
GET  /runtime/status
POST /rules
POST /rules/{id}/activate
GET  /integrations/capabilities
POST /integrations
GET  /integrations
GET  /integrations/runs
GET  /integrations/{id}
POST /integrations/{id}/enable
POST /integrations/{id}/disable
POST /integrations/{id}/poll
POST /integrations/{id}/webhook
WS   /ws/events
```

## Black Mirror projection

TRUE admissions form provisional classes. OPEN admissions remain visible as edges and seams. FALSE admissions remain contradictions. Every displayed class contains a reverse index to its exact source occurrences.

Outbound connectors export this reverse index with the projection. The projection is nonterminal: its OPEN seams and returned classes become inputs to subsequent autonomous cycles.

## Security boundary

- Connector secrets are environment references, never stored values.
- Webhooks support HMAC-SHA256 over the exact request body.
- URLs cannot contain credentials.
- Literal private and loopback destinations are blocked by default.
- Redirects are not followed.
- Production deployment must also enforce DNS and network egress policy.
- Imported text is preserved as source and is not executed.
- Transport success is not translational truth.
