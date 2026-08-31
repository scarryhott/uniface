# Versioned natural-form atlas refactor

This refactor corrects one semantic reduction in the executable Supernet: the
closure-ball / hair / light-cone presentation is no longer treated as the
container or final ontology of every historical natural form.

The runtime law is now:

```text
Supernet = CloseAtlas(forms, translations, returned witnesses, OPEN relations)
UI(p,t)  = Glue(compatible charts at p,t)
edge     = ongoing view transport between glued local charts
truth    = what survives source-preserving translation and return
```

The existing observer-observed interactive-translation kernel remains the truth
kernel. The atlas cannot widen it.

## Non-collapse rules

1. Every historical form has a stable chart id and version.
2. The closure ball is one `BALL_HAIR` chart and has
   `closure_ball_is_master_container = false`.
3. Shared names and visual resemblance never witness equality.
4. Every chart has an identity translation.
5. A non-identity translation is `WITNESSED` only when it has returned source
   provenance and explicitly preserves source, closure, and return.
6. Otherwise the relation is `OPEN` and remains in the atlas.
7. Hair is retained as a semantic lineage: local-zero vectors → within-ball →
   as-ball → self-location inversion → global returned history. The lineage is
   OPEN unless a returned translation actually identifies versions.
8. Physical/cosmological/color forms remain registered projections with no
   empirical truth issued by the registry.

## Runtime integration

`closure_supernet/natural_form_atlas.py` registers the ten historical families
and derives current runtime natural-form charts from the existing closure
receipt. It also derives the compatible sub-atlas by returned translation,
not by a developer menu.

`interaction_closure.py` wraps the prior kernel and adds:

- `natural_form_atlas`
- `natural_form_atlas_validation`
- `glued_ui_subatlas`
- explicit non-reduction claims on the former Black-Mirror/ball topology

The old implementation is preserved byte-for-byte as
`interaction_closure_legacy.py`; its equality and return semantics remain the
upstream authority.

`closure_ui_contract.py` similarly wraps its prior implementation. Every OPEN,
BLOCKED, or WITNESSED contract carries a content-addressed atlas and a
content-addressed glued compatible sub-atlas. The contract id covers both.

`closure_only_interface.py` adds an independent browser reconstruction check of
that atlas/glue receipt. Returned translation paths themselves are navigable
view transport, and OPEN potential paths with returned target localities remain
navigable without executing as equality.

## Governing invariant

For natural-form charts `F_i` and `F_j`, the runtime may report
`F_i ≡ F_j` only if a returned translation supplies:

```text
source preserved
closure commutes
return preserved
source-return provenance present
```

No name, icon, geometry, family, historical succession, AI reading, token
reading, or ball membership can substitute for those conditions.

Therefore the ball-hair system remains available as a powerful current chart,
but it cannot erase the checker, point-line, triangle, seam/Mobius, spiral,
fractal-hypotenuse, mirror, sheaf, AI/token, trading, or physical/speculative
forms that preceded or coexist with it.
