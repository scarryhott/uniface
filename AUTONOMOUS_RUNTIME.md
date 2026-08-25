# Closure Supernet Autonomous Runtime

This repository now contains an executable runtime for the Uniface Closure Supernet.

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

## Agents

- **InboxSensorAgent** — watches the inbox for exact `.md`, `.txt`, and `.jsonl` occurrences.
- **UnderstandingAgent** — proposes literal, operator-path, inverse-path, and semantic candidate relations.
- **InterpretationAgent** — records preservation, transformation, omission, frame, scope, affected perspectives, reverse path, and reopening.
- **AdmissionAgent** — applies the active source-preserving constitutional rule.
- **MoralAuditAgent** — blocks global completeness when affected perspectives are omitted.
- **ReopeningAgent** — turns incomplete admissions into explicit OPEN seams.
- **ProjectionAgent** — generates the current Black Mirror topology with reverse source indexes.
- **RuleReviewAgent** — notices repeated seams and proposes versioned rule revisions without rewriting history.

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
```

Original occurrences have no update endpoint. Revised notes are new occurrences linked by typed relations. Rules are versioned; historical outputs retain the rule version that generated them.

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
WS   /ws/events
```

## Black Mirror projection

TRUE admissions form provisional classes. OPEN admissions remain visible as edges and seams. FALSE admissions remain contradictions. Every displayed class contains a reverse index to its exact source occurrences.

The projection is nonterminal: its OPEN seams and returned classes become inputs to subsequent autonomous cycles.
