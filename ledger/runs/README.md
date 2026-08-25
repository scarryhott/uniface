# Derived run log

This folder is a **derived persistence projection**, not source notes and not a database.

```text
Git                 = the persistent field
ledger/ + occurrences/ = canonical stored returns
ledger/runs/        = last run residue the page may load
localStorage        = local continuation only, never the network
```

`current.json` is the last committed residue. `docs/field-run.json` is the same run projected next to the public HTML so a `/docs` Pages root can load it without a second host.

Reopening remains available. TRUE is not issued. This is not leftover Slearn PR 10.
