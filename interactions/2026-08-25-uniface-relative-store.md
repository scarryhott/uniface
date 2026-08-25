# Interaction: uniface-relative persist wired

This is an **InteractionEvent**. It is provenance for a stored return. It is not a source note and not a foundation document.

Returned occurrence: [`occurrences/2026-08-25-uniface-relative-store.md`](../occurrences/2026-08-25-uniface-relative-store.md).

Heartbeat 15:34 ET: Harry confirmed `$0/month` `uniface-relative`. Wire select/admit as relative interaction only. Do not overwrite beat 1434. Do not merge. Do not mix `rmf_*`.

```text
InteractionEvent
  id                    interaction-2026-08-25-uniface-relative-store
  date                  2026-08-25
  sensed                15:34 ET
  participants          Harry (scarryhott); this autonomous loop
```

## Event

```text
status                = MODEL_SUGGESTED_RELATION
project               = uniface-relative
project_id            = thpzzkaymledzcwsfqhn
table                 = public.uniface_relative_interaction
api                   = https://thpzzkaymledzcwsfqhn.supabase.co
not                   = the field
not                   = git closure
not                   = leftover Slearn PR 10
not                   = rmf_* / Rate My Face
not                   = a service-role key in the repo
```

## Accepted / rejected / open changes

```text
accepted   select/admit POST kind=relative_interaction to uniface-relative
accepted   GET recent rows as a visible relative-interaction field
rejected   client appends a ledger beat / FOUNDATION rewrite / rmf mix-in / service-role
open       service-role never in the client
open       later authenticated authors
open       NRRF764/765 not on slearn main
open       GitHub Pages
open       TRUE not issued
```
