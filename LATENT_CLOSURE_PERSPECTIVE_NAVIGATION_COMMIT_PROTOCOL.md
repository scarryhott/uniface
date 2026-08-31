# Latent closure perspective navigation and commit protocol

Supernet 3.21 treats the verified closure relation as the browser's latent
state. The SVG is only its current projection. It is not a second model and
does not own independent semantics.

The executable state is:

```text
L = verified latent closure
P = mutable local perspective hair and focus
M = uncommitted local modification
screen = project(L, P, M)
```

Dragging the field changes only the local perspective hair. Selecting a fibre
navigates to its closure focus. Typing constructs a dashed local potential
derived from the exact draft; it does not mutate the durable closure or claim
truth. Double-clicking returns the local hair to its normalised reading.

Enter computes a content commitment over the active contract, return relation,
perspective, focus, exact source, local hair and equality kernel. The server
reconstructs that commitment from its current closure before it appends an
event. A forged or stale local commitment is rejected without creating a
return. The successor is then rederived, audited, content-addressed and sent
back with a receipt for the committed local projection. The browser adopts it
only after independently verifying both the receipt and successor geometry.

Local hair is retained as provenance but never defines equality. Thus users
may navigate and modify the interface perspectivally without being allowed to
rewrite the translational kernel by moving its presentation.

This protocol establishes local staging and closure-governed commit. Durable
continuity across infrastructure replacement still requires a persistent
volume mounted at `/data` in the Railway service.
