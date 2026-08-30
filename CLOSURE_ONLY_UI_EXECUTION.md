# Closure-Only Supernet UI Execution

## Runtime identity

~~~text
authored perspective boundary
→ interaction-time Sense
→ NRRF843 active perspective reading
→ translational truth and NRRF840 closure
→ interaction closure
→ complete perspective-interaction UI contract
→ generic transport interpreter
→ server-revalidated interaction return
→ successor contract
~~~

The interface is not a fixed map populated by a closure receipt. The receipt
derives the complete visible interface and the browser translates that
contract into DOM/SVG primitives.

## Contract states

**OPEN_SOURCE_BOUNDARY** derives the first input from the requested
perspective. It admits only **OFFER_SOURCE** and claims no truth or natural
form.

**WITNESSED** requires the NRRF843 mirror, located truth constraint, NRRF840
closure, interaction closure, active perspective reading, natural forms,
source-return provenance, and matching identifiers. Its scene and operations
are closure-internal.

**OPEN_TRUTH_CONSTRAINT** is fail-closed. It has an invisible root, no actions,
and no semantic fallback.

## Whole-interface invariant

The validator checks:

1. one reachable scene tree with unique node, field, control, and action IDs;
2. only allowlisted transport primitives and safe text tags;
3. exact closure, UI, interaction, perspective, natural-form, and source-return
   provenance on every scene node, topology record, visual form, and action;
4. topology positions and relations derived from the active NRRF843 display
   fibres, with OPEN relations unable to execute as equality;
5. controls = action bindings = execution allowlist;
6. field references resolve to declared controls and required fields are a
   subset of each action schema;
7. action bindings contain only allowlisted operations—never an endpoint,
   method, URL, or client-resolved payload;
8. no hardcoded visible instances and no semantic fallback;
9. a content-addressed contract ID matching the complete validated body.

## Execution boundary

The browser submits only the chosen action, its raw declared fields, and the
perspective/focus coordinates already authored by the displayed contract:

~~~json
{
  "action_id": "continue-local-interaction",
  "perspective_id": "harry",
  "focus_event_id": "event-content-address",
  "values": {
    "author": "harry",
    "perspective": "harry",
    "coordination_kind": "intent",
    "location": "Berkeley, California",
    "thought": "Invite neighbors to plan the first meeting."
  }
}
~~~

to:

~~~text
POST /supernet/interface/contracts/{contract_id}/execute
~~~

These coordinates identify the persisted perspective projection; they do not
select a route or define any semantics. Before Sense or any other mutation, the
server compares the submitted content address, authored focus, canonical
perspective, authenticated participant, and exact field-event revision with
the persisted contract. A mismatch returns **409 STALE_CONTRACT** without
creating a field stage. A fresh GET re-derives the requested perspective's
complete interface natural form and successor contract. Only after the
nonmutating checks and exact field-schema validation does the executor dispatch
one of:

- **OFFER_SOURCE**
- **CONTINUE_INTERACTION**
- **PROPOSE_AGREEMENT**
- **DECIDE_AGREEMENT**
- **RETURN_AGREEMENT**

Agreement proposals remain nonbinding. Each required human authors their own
accept/reject/withdraw return. The living action return is unavailable until
the existing consent gate reports acceptance.

An execution fingerprint is claimed in persistent storage before dispatch. An
exact retry returns the stored response with `replayed: true`; a changed retry
is rejected, and an interrupted claim remains sealed rather than risking a
duplicate interaction.

Perspective projection rebuilds the whole `interface_natural_form`, including
its render state, quotient state, closure projection, factorization witness,
and content address. It never patches another perspective's certified form.

Compatibility endpoints still exist for API clients, so closure-only execution
is a property of the primary website path rather than every legacy server API.
Those endpoints are not encoded in the website program and cannot be selected
by a browser-carried contract.
