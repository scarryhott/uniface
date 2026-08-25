# Digital Supernet Integrations

## Source correction: `0` and `∞` are reciprocal poles

In the literal notes, `0` and `∞` are poles. Their reciprocal relation is one
operation in the wider axiometric network; the poles are not themselves
renamed as “the axiometry.”

The runtime retains the compatibility index `ZERO_INFINITY`, but its source
role is now explicitly:

```text
reciprocal poles
```

The broader operator field also retains `r/i`, Triangle Time, the implicit
shell return, Chaitin–Kakeya, the `tan(π/2)` seam, predual Fourier, four-i,
ball–hair, loop–sensor–selection, and metavectorization.

## Integration principle

A digital application, repository, feed, model, ledger, or remote node is not
an external closure authority.

```text
external source
→ immutable local occurrence
→ candidate relation
→ interpretation witness
→ local configured admission
→ provisional projection
→ reopening
```

An imported assertion is stored as a source occurrence with provenance. It is
not silently promoted to TRUE. Delivery success proves only that bytes crossed
an interface.

## Supported connector kinds

### `WEBHOOK_IN`

Accepts signed or explicitly unsigned development envelopes at:

```text
POST /integrations/{integration_id}/webhook
```

When `secret_env` is configured, the sender signs the raw request body:

```text
X-Closure-Signature: sha256=<HMAC-SHA256>
```

The registry stores only the environment-variable name. It never stores the
secret value.

### `WEBHOOK_OUT`

Exports new event batches together with the current Black Mirror projection
and reverse source index. Connector-generated delivery events are consumed by
the cursor but are not echoed back indefinitely.

The outbound envelope includes:

```text
protocol version
integration identity
new events
current projection
source reverse index
nonterminal=true
turing_complete_assumed=false
```

### `GITHUB_REPOSITORY`

Polls a GitHub repository tree and imports matching UTF-8 blobs as exact source
occurrences. Provenance retains:

```text
repository
ref
tree SHA
blob SHA
path
source URI
```

Default source patterns include Markdown, text, and Lean files. Truncated tree
responses are rejected rather than silently treated as complete.

### `HTTP_JSON_FEED`

Polls an HTTP JSON or JSONL/NDJSON source. It supports:

```text
ETag / If-None-Match
Last-Modified / If-Modified-Since
idempotent external IDs
optional environment-backed authorization
```

The feed returns either a list or:

```json
{
  "items": [
    {
      "external_id": "note-1",
      "exact_text": "ball ↔ hair",
      "source_id": "external-notes",
      "source_location": "https://example.test/notes/1",
      "source_context": "optional",
      "metadata": {}
    }
  ]
}
```

## Closure envelope v1

The inbound protocol is:

```text
closure.supernet/v1
```

Example:

```json
{
  "version": "closure.supernet/v1",
  "items": [
    {
      "external_id": "source-42",
      "exact_text": "0 ↔ ∞ are reciprocal poles",
      "source_id": "notebook",
      "source_location": "external://notebook/42",
      "metadata": {
        "author": "source author"
      }
    }
  ],
  "metadata": {
    "batch": "optional"
  }
}
```

Every item receives an idempotent receipt scoped to its integration and
transport direction. Repeated delivery does not create repeated occurrences.

## Runtime cycle

The autonomous cycle is now:

```text
poll enabled pull integrations
→ sense local inbox
→ propose relations
→ interpret
→ apply admission policy
→ reopen OPEN relations
→ audit affected perspectives
→ review repeated seams
→ project Black Mirror
→ push enabled outbound integrations
→ repeat
```

A connector error is recorded as an integration run and runtime event. It does
not terminate the active Supernet loop.

## API

```text
GET  /integrations/capabilities
POST /integrations
GET  /integrations
GET  /integrations/runs
GET  /integrations/{id}
POST /integrations/{id}/enable
POST /integrations/{id}/disable
POST /integrations/{id}/poll
POST /integrations/{id}/webhook
```

## CLI

Register and poll a GitHub source:

```bash
closure-supernet integration-add \
  --name notebook-repository \
  --kind GITHUB_REPOSITORY \
  --secret-env GITHUB_TOKEN \
  --config '{"repository":"owner/repo","ref":"main","include":["**/*.md","**/*.lean"]}'

closure-supernet integration-list
closure-supernet integration-poll
```

Register an outbound return channel:

```bash
closure-supernet integration-add \
  --name black-mirror-return \
  --kind WEBHOOK_OUT \
  --secret-env CLOSURE_OUTBOUND_SECRET \
  --config '{"url":"https://receiver.example/closure"}'
```

## Security and non-collapse boundaries

- Secrets are environment references, not database fields.
- URLs may not contain credentials.
- Literal localhost and private IP destinations are blocked by default.
- Redirects are not followed.
- Private-network integrations require explicit opt-in.
- Production deployments should also enforce DNS and network egress policy to
  prevent rebinding and indirect private-network access.
- Remote text is preserved as source; it is not executed.
- Remote metadata cannot self-certify formal, physical, social, or moral truth.
- A remote relation must pass local interpretation and admission.
- Every projection retains a reverse index to its exact local source
  occurrences.

## Status

Implemented now:

- persistent connector registry;
- enable/disable state;
- persistent pull/push cursors;
- idempotent receipts;
- signed inbound and outbound webhooks;
- GitHub source polling;
- HTTP JSON/JSONL polling;
- event and projection export;
- API, CLI, dashboard and test coverage.

Not configured by the repository itself:

- production credentials;
- cloud deployment;
- authenticated public peer discovery;
- encrypted application-level payloads beyond HTTPS;
- distributed consensus;
- automatic authority over external systems.

These remain deployment choices or later integrations. None becomes the
foundational conscious-cultural Supernetwork merely by being connected.
