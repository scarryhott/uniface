# Closure Supernet Production Integration

This layer makes the existing living network operate as a real public service.
It does **not** add another proof object and it does not move the foundation away
from interaction.

```text
public participant or agent
→ authenticated session
→ source-preserving network action
→ persistent TranslationEvent / resource / problem state
→ autonomous reintegration
→ realtime event return
→ later interaction
```

## What production means here

The production boundary supplies operational conditions around the existing
Supernet:

- durable single-node SQLite state mounted on persistent storage;
- authenticated browser and API sessions;
- member and operator roles;
- participant-bound authorship checks on write payloads;
- public-read / authenticated-write policy;
- protected runtime, rule, integration, and backup operations;
- authenticated WebSocket event access;
- request IDs, security headers, trusted hosts, CORS, body limits, and rate limits;
- liveness and readiness probes;
- consistent SQLite snapshots and retention;
- separate `web`, `worker`, or combined `all` service roles;
- Railway and Docker production manifests.

It does not redefine Closure. Authentication proves who submitted an action; it
does not make the action true. A deployment transports and persists the living
field; it does not become the field's canonical language.

## Production modes

### Development

```text
CLOSURE_ENVIRONMENT=development
CLOSURE_AUTH_MODE=open
```

This preserves the current local workflow.

### Invite-key production

```text
CLOSURE_ENVIRONMENT=production
CLOSURE_AUTH_MODE=api_key
CLOSURE_SESSION_SECRET=<random secret>
CLOSURE_AUTH_API_KEYS_JSON={...}
```

Example key map:

```json
{
  "replace-with-random-operator-key": {
    "subject": "network-operator",
    "role": "operator",
    "scopes": ["*"]
  },
  "replace-with-random-member-key": {
    "subject": "participant-account",
    "role": "member",
    "participant_id": "persistent-participant-id"
  }
}
```

Secrets belong only in deployment environment variables. They are never stored
in the repository or the runtime database.

### External JWT production

Use an OpenID/JWT provider through either a JWKS endpoint or a shared verification
secret:

```text
CLOSURE_AUTH_MODE=jwt
CLOSURE_AUTH_JWKS_URL=https://issuer.example/.well-known/jwks.json
CLOSURE_AUTH_ISSUER=https://issuer.example/
CLOSURE_AUTH_AUDIENCE=closure-supernet
CLOSURE_AUTH_JWT_ALGORITHMS=RS256
CLOSURE_SESSION_SECRET=<separate random browser-session secret>
```

`hybrid` accepts both invite keys and verified external JWTs.

Expected claims:

```text
sub              persistent account subject
role             member or operator
participant_id   optional living-network participant binding
scopes           optional list or space-separated string
```

## Browser session

Open:

```text
/production
```

An invite key is exchanged for a short-lived, signed, HTTP-only session cookie.
The existing living, translation, resource, reopening, and equality pages then
use that same-origin cookie automatically.

The key is not written to local storage.

## Authorization boundary

Anonymous access is configurable. Recommended public production defaults:

```text
CLOSURE_ALLOW_ANONYMOUS_READ=true
CLOSURE_ALLOW_ANONYMOUS_WRITE=false
CLOSURE_ALLOW_SELF_REGISTRATION=false
```

All mutating requests require at least `member`. These operations require
`operator`:

```text
/runtime
/bootstrap
/rules
/integrations
/admin
```

Inbound integration webhooks remain outside API-key auth because they already
use their connector-specific HMAC verification.

For non-operator members, common authorship fields such as `created_by`,
`author_id`, `authored_by`, `actor_id`, and `decided_by` must match the
participant bound to the authenticated principal.

## Public-only first production

The initial production release is deliberately a **public network**. Until
row-level visibility and encrypted group storage are implemented, set:

```text
CLOSURE_PUBLIC_ONLY_MODE=true
```

The write boundary rejects `PRIVATE`, `SHARED`, and `COMMUNITY` content rather
than accepting it and accidentally exposing it through an unfiltered read API.
This is a safety constraint, not a claim that the final Supernet should lack
private or community scopes.

## Web and worker roles

```text
CLOSURE_SERVICE_ROLE=all
```

runs the public API and autonomous reintegration loop in one process. This is the
supported SQLite deployment shape.

```text
CLOSURE_SERVICE_ROLE=web
```

disables the background loop in the HTTP service.

```bash
closure-supernet worker
```

runs only the autonomous loop. Split web/worker deployment requires a shared
storage backend with valid multi-process semantics; do not point independent
containers at unrelated SQLite files and call them one network.

## Health

```text
GET /livez   process is alive
GET /readyz  auth and storage configuration are operational
```

`/readyz` returns `503` when production authentication has no configured key,
JWT verifier, or browser-session secret; when development mode remains enabled;
or when the persistent database directory is unwritable.

## Backups

Operator API:

```text
POST /admin/backups
GET  /admin/backups
```

CLI:

```bash
closure-supernet backup --label before-upgrade
closure-supernet backup-list
```

Snapshots use SQLite's online backup API and include a JSON manifest. Retention
is controlled by:

```text
CLOSURE_BACKUP_DIR=/data/backups
CLOSURE_BACKUP_KEEP=30
```

A platform-level volume snapshot remains recommended in addition to application
snapshots.

## Docker

```bash
cp .env.production.example .env.production
# edit all secrets and host/origin values
docker compose -f docker-compose.production.yml up --build
```

Mount `/data` to persistent storage. The canonical database path is
`/data/closure_supernet.db`.

## Railway

The repository includes `railway.toml` and a Dockerfile healthcheck. Required
service variables include:

```text
CLOSURE_ENVIRONMENT=production
CLOSURE_PUBLIC_DEVELOPMENT_MODE=false
CLOSURE_AUTH_MODE=api_key or jwt
CLOSURE_SESSION_SECRET=<secret>
CLOSURE_AUTH_API_KEYS_JSON=<secret JSON>   # api_key/hybrid only
CLOSURE_TRUSTED_HOSTS=<generated-domain>,localhost
CLOSURE_CORS_ORIGINS=https://<generated-domain>
CLOSURE_DB_PATH=/data/closure_supernet.db
CLOSURE_BACKUP_DIR=/data/backups
```

Attach a persistent volume at `/data` before treating the service as durable.
The Railway healthcheck uses `/readyz`; deployment should remain unhealthy until
a real auth configuration and writable volume are present.

## Operational scope

This completes the first production envelope for a public, active, single-node
Supernet. It does not yet claim:

- encrypted private/community scopes;
- password reset, email verification, or social login UI;
- multi-region replication;
- multi-node causal event consensus;
- PostgreSQL-backed horizontal scale;
- signed human identity as a metaphysical identity proof;
- production moderation policy on behalf of the network.

Those are later production integrations. The current service is operationally
real without pretending that deployment terminates the living network.
