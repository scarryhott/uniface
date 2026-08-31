# Archive-to-runtime closure audit

Supernet now has a deterministic audit surface for the stronger claim that the historical ontology has been preserved rather than merely summarized.

## Closure distinction

The audit separates two claims:

```text
historical_inventory_closed
    every detected Supernet semantic condition has a classification;
    OPEN is allowed and MISSING is not.

runtime_execution_closed
    every detected condition is EXECUTABLE or WITNESSED;
    REGISTERED, OPEN, and MISSING block this stronger claim.
```

The five classifications are:

- `EXECUTABLE`: the condition maps to a current runtime invariant with named source symbols.
- `WITNESSED`: a cross-form condition is connected by a source-preserving returned atlas translation.
- `REGISTERED`: the historical natural form is retained in the versioned atlas but has no executable translation established by this audit.
- `OPEN`: the relation is explicitly unresolved, empirical/speculative, or lacks a returned cross-form witness.
- `MISSING`: a Supernet theory condition was detected but could not be mapped to either the atlas or an executable runtime capability.

`MISSING` is never silently converted to `OPEN`, and `REGISTERED` is never silently promoted to `EXECUTABLE`.

## Source integrity

The parser binds the receipt to the exact archive bytes with SHA-256 and checks both exported header totals: `Conversations with user messages` and `User messages`. A mismatch prevents historical inventory closure.

Conversation boundaries are recognized only when an exported `##` title is immediately followed by its `Conversation ID` line. Markdown headings inside user messages therefore remain source text rather than becoming false conversations.

## Equality closure

A sentence that names two natural forms and asserts a translation/equality relation is not admitted because the words resemble one another. It is `OPEN` unless the supplied versioned atlas contains a non-identity `WITNESSED` path whose relations each preserve `source_return_ids`, `source_preserved`, `closure_commutes`, and `return_preserved`.

Only then does the archive condition classify as `WITNESSED`.

## Runtime use

Run the complete receipt:

```bash
closure-supernet-audit user_inputs_only.md --output archive_closure_audit.json
```

Print only its closure summary:

```bash
closure-supernet-audit user_inputs_only.md --summary
```

Supply a current atlas receipt when cross-form returned translations should be checked:

```bash
closure-supernet-audit user_inputs_only.md \
  --atlas-json current_natural_form_atlas.json \
  --output archive_closure_audit.json
```

The audit is deterministic text/registry matching. It does not use embeddings or a semantic-similarity model to manufacture historical equality.

## Current archive boundary

The historical File Library contains a `user_inputs_only.md` export whose header states 42,683 user messages. A File Library reference is not a runtime filesystem path, so the repository must not claim that the full archive has already passed merely because it can be searched interactively. Until the exact archive bytes are supplied to `closure-supernet-audit`, the global `every historical condition is running` claim remains OPEN.
