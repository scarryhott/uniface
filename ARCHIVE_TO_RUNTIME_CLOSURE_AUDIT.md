# Archive-to-runtime closure audit

Supernet retains a deterministic archive audit for the stronger historical-forensics question: whether every semantic condition in a supplied export has been individually classified. It is **diagnostic**, not the semantic authority that closes Supernet.

The authoritative Supernet closure is proof-indexed:

```text
known/versioned natural-form atlas
+ indexed Lean witnesses
+ source-preserving returned translations
+ preserved OPEN relations
+ UI = Glue(compatible sub-atlas)
```

The archive therefore cannot gate `supernet_closed`. It can only report additional historical coverage against exact supplied bytes.

## Audit distinction

The audit separates two archive-local claims:

```text
historical_inventory_closed
    every detected Supernet semantic condition in this supplied archive
    has a classification; OPEN is allowed and MISSING is not.

runtime_execution_closed
    every detected condition in this supplied archive is EXECUTABLE or
    WITNESSED; REGISTERED, OPEN, and MISSING block this stronger archive-local
    execution claim.
```

The five classifications are:

- `EXECUTABLE`: the condition maps to a current runtime invariant with named source symbols.
- `WITNESSED`: a cross-form condition is connected by a source-preserving returned atlas translation.
- `REGISTERED`: the historical natural form is retained in the versioned atlas but has no executable translation established by this audit.
- `OPEN`: the relation is explicitly unresolved, empirical/speculative, or lacks a returned cross-form witness.
- `MISSING`: a Supernet theory condition was detected but could not be mapped to either the atlas or an executable runtime capability.

`MISSING` is never silently converted to `OPEN`, and `REGISTERED` is never silently promoted to `EXECUTABLE`.

## Source integrity

The parser binds the receipt to the exact archive bytes with SHA-256 and checks both exported header totals: `Conversations with user messages` and `User messages`. A mismatch prevents that archive's inventory closure.

Conversation boundaries are recognized only when an exported `##` title is immediately followed by its `Conversation ID` line. Markdown headings inside user messages therefore remain source text rather than becoming false conversations.

## Equality closure

A sentence that names two natural forms and asserts a translation/equality relation is not admitted because the words resemble one another. It is `OPEN` unless the supplied versioned atlas contains a non-identity `WITNESSED` path whose relations each preserve `source_return_ids`, `source_preserved`, `closure_commutes`, and `return_preserved`.

Only then does the archive condition classify as `WITNESSED`.

## Runtime use

Run the complete archive receipt:

```bash
closure-supernet-audit user_inputs_only.md --output archive_closure_audit.json
```

Print only its archive-local summary:

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

## Closure boundary

A File Library reference is not a runtime filesystem path, so the audit must not claim to have processed bytes it did not receive. That limitation affects only the archive-forensics receipt. It does **not** hold the Supernet semantic closure OPEN.

The runtime closure certificate explicitly requires:

```text
archive_audit_required_for_supernet_closure = false
archive_audit_is_diagnostic_only = true
```
