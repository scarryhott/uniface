# Occurrence: Note relative persist

This file is an **interaction/interpretation return**. It names the 18:34 ET difference that the Note operator now writes a lineage receipt on uniface-relative, the same store as Problem/Inter. It is not a rewrite of FOUNDATION, not two-person E2E complete, not Rate My Face, and not a claim that the framework is achieved.

```text
status              = MODEL_SUGGESTED_RELATION
relation_type       = LATER_READING
author_status       = OPEN
reopening           = available
not                 = FOUNDATION
not                 = LATENT_MEMORY_PROTOCOL
not                 = leftover Slearn PR 10
not                 = Rate My Face / rmf_* tables
not                 = two-person+agent E2E complete
not                 = invented NRRF764/765 Lean
not                 = a new SQL kind / RLS policy
```

Provenance: 1634 residue (Note stayed a local returned reading) closed as persist on beat 2026-08-25-1834-et.

## Canonical occurrence fields

```text
NoteOccurrence
  id                 occ-2026-08-25-note-relative-persist
  source_id          beat-2026-08-25-1834-et
  exact_text         Note writes a lineage receipt on uniface-relative.
                     Table kind stays relative_interaction.
                     payload.inter / ui_kind names returned_note.
                     The note text is the returned note, not a rule.
  date               2026-08-25
  source_location    https://uniface-tawny.vercel.app (not the field)
  author_status      MODEL_SUGGESTED_RELATION; TRUE not issued
```

## The reading (assistant interpretation, labeled)

1634 smoked one-agent reconstruction on LIVE https://uniface-tawny.vercel.app (lineage `87ed6a81-20c7-4319-9015-291e6797e18f`) and found Note local-only. 1834 wired `showReturnedNote()` to `writeRelativeInteraction('returned_note')`. `PERSIST_KINDS` now includes `returned_note`. Table `kind` remains `relative_interaction` (existing RLS: anon insert/select that kind only). Reconstruction walks receipts for the last `returned_note` and restores that Note after reload/`?lineage=`.

One-agent persist smoke (not two-person E2E): lineage `b5b17022-80f3-4d7f-87b9-e211767ab716`, receipt `b1a0b1f8-198a-4c3e-8778-448b4d05c561`, row `41254dc5-4a8b-4cf4-be9b-7d6b43f33763`. Insert HTTP 201 with publishable key; GET restored `payload.inter=returned_note` and the returned note text.

## OPEN seams

```text
two-person + agent E2E OPEN (not fake-complete)
admitted prefix not reconstructed from receipts
GitHub Pages still OPEN
NRRF764 / NRRF765 still not on public slearn main
NRRF657_on_slearn OPEN (PR 12 unmerged)
TRUE not issued
framework not achieved
```

TRUE is not issued. Reopening remains available.
