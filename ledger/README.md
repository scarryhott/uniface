# Heartbeat ledger

This is a **derived store**, not source notes and not a second foundation. Status: `MODEL_SUGGESTED_RELATION`.

Every heartbeat writes **one beat** with three required, non-substitutable sections:

```text
ORGANIZATION
PLANNING
ACTION
```

- **ORGANIZATION** — how this beat is organized: selected `0`, sensors, field topology, in-flight work, OPEN seams.
- **PLANNING** — what this beat intends, WHY, what it will not do, residue from last beat.
- **ACTION** — what was actually done, artifacts, blocked/in-flight, residue.

A beat is **incomplete** if any section is missing.

```text
plan is not action
organization is not plan
if action is in-flight, that fact is still the ACTION record
```

No layer substitutes for another. That rule is already in [`LATENT_MEMORY_PROTOCOL.md`](../LATENT_MEMORY_PROTOCOL.md). This store does not rewrite that file. It does not replace `InteractionEvent` or `NoteOccurrence`. A beat may point at those records. Occurrences and interactions remain occurrences and interactions.

Scheduled hourly beats and field-loop event beats share this folder. They are different sensors of the same ledger, not different stores. Event beats and scheduled beats share this folder; no layer substitutes for another.

```text
ledger/beats/
  <date>-<time>-et.md
```

Beats stay `MODEL_SUGGESTED_RELATION` unless later confirmed. Reopening remains available. TRUE is not issued by writing a beat.
