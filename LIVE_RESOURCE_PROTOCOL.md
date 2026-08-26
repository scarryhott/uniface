# Live Self-Reintegrating Resource Protocol

This layer instantiates resources as living relative forms of the Closure
Supernet.  It is a protocol for carrying interaction; it is not the closure and
it does not define translational truth.

```text
resource form
→ active engagement
→ returned resource form
→ OPEN translation witness
→ relative admission
→ natural component
→ further engagement
```

## Foundational boundary

The implementation follows the NRRF769 distinction:

```text
protocol = encoding, delivery, receipt, ordering and transport convention
truth    = admissible translation among readings
closure  = the invariant completion transported through those translations
```

A successful wire receipt can coexist with an OPEN or FALSE translation.  A
failed or absent protocol receipt does not make an otherwise admitted
translation false.  Protocol verdicts and truth verdicts are persisted in
separate records.

## No finite resource ontology

A resource uses author-selected open strings:

```text
form_label
language_label
capabilities
constraints
```

There is no `ResourceKind` enumeration and no registry that decides in advance
whether a lesson, proof, service, commitment, compute process, image, material,
story, action, physical result or future form may participate.

The exact source occurrence remains canonical.  Labels help participants read
and retrieve a resource but do not become its complete identity.

## No externally selected language

Every resource and translation may retain its own language or frame label.
The live projection deliberately returns:

```text
canonical_form     = null
canonical_language = null
```

A natural component lists every participating form and language.  It does not
select one as the language into which the others must collapse.

## Engagement and return

An engagement records:

```text
actor
exact occurrence
open engagement label
source resource
perspective and problem links
what is preserved
what is transformed
what is omitted
affected perspectives
```

An engagement never mutates the original resource.  A returned consequence is
created as another immutable resource with `parent_resource_id` pointing back
to its source.

The autonomous reintegration agent then creates an OPEN translation from the
source form to the returned form.  It preserves both exact occurrences and does
not claim that the return is already globally true or terminal.

## Natural unification

The runtime does not unify resources because they share a type label, language,
embedding neighborhood, owner, price or protocol endpoint.

It builds components only from translations whose latest participant-relative
verdict is `TRUE`:

```text
resources + admitted translations → natural components
```

`OPEN` translations remain visible edges.  `FALSE` translations remain visible
rejections.  Every component retains all member sources, form labels and
language labels.

This is the executable sense in which the continuum naturally unifies under
active engagement rather than being enforced by a finite schema.

## Live stages and the batch limit

Each live stage records:

```text
delivery order
all resources
all engagements
all translations
TRUE / OPEN / FALSE translation partitions
natural components
source reverse index
stage signature
order-independent limit signature
```

The stage signature preserves historical arrival order.  The limit signature
is computed from the set of exact resource occurrences and admitted translation
pairs after sorting, so reindexing delivery does not change it.

At every current stage, the runtime recomputes the same signature from the full
batch and reports:

```text
live_limit_matches_current_batch
```

This is a software invariant of the current implementation, not a replacement
for NRRF769's machine-checked theorem.

## Complete coverage without terminal completion

`complete_coverage` means every resource in the current executable field is
represented by the stage and has a reverse path to its exact occurrence.

It does **not** mean:

- every future resource has been anticipated;
- every translation has been settled;
- one language is complete;
- the network has reached a final moral core;
- the protocol is metaphysically complete.

The implementation is complete relative to its current admitted field and
nonterminal relative to future engagement.

## Persistent storage

The SQLite event-sourced runtime adds:

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

Original occurrences remain in the canonical `occurrences` table.  Every
resource table stores references and append-only relational history rather than
rewriting source text.

## Public interface and API

The public resource continuum is served at:

```text
/resources
```

Core endpoints:

```text
GET  /network/resources/capabilities
POST /network/resources
GET  /network/resources
GET  /network/resources/{id}

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

## Autonomous cycle

When enabled, each runtime cycle performs:

```text
poll transports
→ sense exact sources
→ reintegrate returned living actions
→ reintegrate returned resources
→ advance reopening processes
→ interpret and admit translations
→ integrate a live resource stage
→ project the living field
→ export source-reversible returns
→ repeat
```

## Status discipline

The implementation records distinct claims:

```text
PROTOCOL_DELIVERED
RESOURCE_AUTHORED
ENGAGEMENT_RECORDED
TRANSLATION_OPEN
TRANSLATION_TRUE_AT_SCOPE
TRANSLATION_FALSE_AT_SCOPE
RETURN_PENDING_REINTEGRATION
RETURN_REINTEGRATED_OPEN
LIVE_STAGE_COMPLETE_COVERAGE
```

None of those statuses silently becomes universal truth.

## Formal status

- NRRF769 is machine-checked under its formal reading.
- Closure Supernet 0.5 is a software-tested realization of selected live
  integration and protocol-separation commitments.
- The order-independent limit signature is an executable invariant.
- A machine-checked refinement theorem from the Python runtime to NRRF769
  remains OPEN.
- Typed heterogeneous frame translation, graded faithfulness laws and genuine
  concurrent event structures remain further formal and distributed-runtime
  work.
