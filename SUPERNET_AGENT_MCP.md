# Closure Supernet agent MCP

This is a continuation of the completed Supernet software, not a new semantic foundation.

An external ChatGPT/Codex-style agent can participate in the same live field through the Streamable HTTP MCP endpoint:

```text
https://uniface-supernet-production.up.railway.app/mcp
```

The MCP server is mounted inside the same FastAPI process and shares the same `ClosureSupernetRuntime`, database, production security middleware, live Sense pipeline, TranslationField, NRRF790 selection audit, topology return/reopening operations, and Black Mirror projection.

## Agent relation

```text
agent observes field
→ agent offers/interacts with exact source
→ existing live Sense runs
→ interpretation/admission/TranslationField
→ natural selection or OPEN branching
→ agent may relate/refine/return/reopen/collect
→ successor event is re-sensed
```

The agent is a participant. It has no truth privilege, no admin privilege, and no independent closure semantics. Agent mutations remain additive and nonterminal.

## Tools

- `supernet_observe` — read recent events and the perspective-relative natural Black Mirror receipt.
- `supernet_offer` — add an exact source or interact with a parent event; immediately run live Sense. An optional eight-sheaf placement uses the same canonical occurrence.
- `supernet_relate` — propose an explicit directed or reciprocal relation between existing events. Geometry never manufactures direction.
- `supernet_refine` — select one currently admissible Sense relation. If alternatives remain, the existing NRRF790 machinery records forced isolation rather than natural selection.
- `supernet_return` — return a result/consequence as a new successor event and re-sense it.
- `supernet_reopen` — reopen a prior event without erasing its history and re-sense the field.
- `supernet_collective` — join two or more event trajectories into a new source-preserving collective continuation and re-sense it.

The regular capability boundary is:

```text
GET /supernet/agent/capabilities
```

## Non-collapse contract

```text
same runtime = true
source preserving = true
OPEN remains OPEN
background autonomy required = false
admin privilege = false
truth privilege = false
canonical language = none
canonical pixel layout = none
return is nonterminal
reopening remains available
```

Production authentication and rate limiting wrap `/mcp` through the existing outer FastAPI middleware. The MCP layer does not add a bypass around Supernet authorization.

## Connecting an agent

Use the public `/mcp` URL as a remote Streamable HTTP MCP server in a compatible ChatGPT/Codex developer connection. Once connected, the agent can call the tools above as an ordinary Supernet participant.

Creating this endpoint does not automatically inject the tool into an already-running ChatGPT conversation. The client must connect the remote MCP server first; after that, tool calls enter the same deployed Supernet field.
