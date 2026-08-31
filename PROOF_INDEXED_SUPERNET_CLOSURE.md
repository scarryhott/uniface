# Proof-indexed Supernet closure

The complete Supernet is closed as a versioned natural-form atlas, not as one privileged ball diagram and not as an exhaustive text archive.

```text
Supernet = CloseAtlas(
  known/versioned natural forms,
  formal Lean witnesses,
  source-preserving returned translations,
  OPEN relations
)
```

The closure certificate is `closure_supernet/supernet_closure_certificate.py`.

## Closure criterion

`supernet_closed` is true exactly when the runtime can establish all of the following from its own receipts:

1. the versioned atlas is valid;
2. every known natural form and family in the retained atlas is still present;
3. the complete historical hair lineage remains versioned rather than overwritten;
4. the closure ball is one chart, never the master container;
5. visual resemblance and shared names cannot author equality;
6. every asserted non-identity atlas equality has a source-preserving returned witness;
7. every unwitnessed relation remains OPEN and cannot execute as equality;
8. every runtime state belongs to its derived atlas chart;
9. the formal Lean proof index resolves against the same atlas and contains the required closure modules;
10. proof bundles do not silently identify the forms they mention;
11. the compatible UI glue is derivable from the atlas;
12. when a UI receipt is supplied, it carries that exact atlas and exact glue;
13. when an interaction receipt is supplied, it carries that exact atlas and passes translational-continuity audit;
14. the archive audit is not a semantic authority.

This deliberately separates closure from terminal resolution:

```text
supernet_closed = true
open_relations_are_part_of_closure = true
existence_closed = false
dialectic_continuation_status = OPEN
```

A new unresolved relation therefore does not reopen the architecture. It extends the closed atlas with an OPEN boundary that can only become WITNESSED by a valid return.

## Natural-form authority

Known natural forms are retained by `natural_form_atlas.py`. A historical form does not need executable rendering to continue to exist in Supernet. It does need a stable versioned chart identity.

No later use of `hair`, `ball`, `seam`, `mirror`, `triangle`, `maze`, or another repeated name is allowed to erase an older semantic version.

## Lean authority

`formal_proof_index.py` indexes the existing machine-checked formal corpus against the atlas. The current core includes the formal chart/naturality/dialogue/UI line through NRRF858/859/862/866/872 and supporting domain modules such as NRRF849, NRRF861, NRRF865 and NRRF870.

The Python runtime does **not** claim to re-prove Lean and does not claim to inspect formal source files that are not mounted into the runtime:

```text
lean_source_verified_by_runtime = false
runtime_reproves_lean = false
```

The proof index therefore certifies which formal theorem families constrain which natural-form charts. It does not turn co-occurrence in a theorem into cross-form equality.

## Runtime equality authority

Current non-identity atlas equality remains stricter:

```text
WITNESSED(F_i -> F_j)
iff
  source_return_ids are present
  AND source_preserved
  AND closure_commutes
  AND return_preserved
```

Otherwise the relation is OPEN.

Formal theorems may prove chart invariants, naturality, projections, or equivalences, but they never authorize a visual/name-based collapse in the runtime atlas.

## UI closure

Every UI contract is sealed with:

```text
natural_form_atlas
formal_proof_index
glued_ui_subatlas
supernet_closure_certificate
```

The browser independently checks their content hashes and refuses to render unless the final certificate says `supernet_closed = true`.

The UI may itself still be at `OPEN_SOURCE_BOUNDARY`: architecture closure and local relation resolution are different statements.

## Archive audit

`closure-supernet-audit` remains available for exact historical-forensics work. It is diagnostic only:

```text
archive_audit_required_for_supernet_closure = false
archive_audit_is_diagnostic_only = true
```

This prevents inability to mount one historical export from becoming an artificial semantic dependency of the live network.
