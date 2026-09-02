# Deterministic Supernet Project Closure

The full repository is one versioned natural-form atlas, but it has exactly one executable semantic authority:

\[
\Gamma_{n+1}=\operatorname{SUPERNET\_TRANSLATE}(\Gamma_n,\delta_n).
\]

The closure relation is:

\[
\boxed{
\operatorname{RuntimeTransition}
=
\operatorname{BrowserInteraction}
=
\operatorname{AgentInteraction}
=
\operatorname{SUPERNET\_TRANSLATE}
}
\]

and runtime identity is:

\[
\boxed{
\operatorname{Id}_{Runtime}(x)
=[x]_{\operatorname{TranslationalTruth}}.
}
\]

## Deterministic law

For one initial returned history and one ordered sequence of exact source-preserving interactions,

\[
(C_0,\delta_0,\ldots,\delta_n)
=
(C'_0,\delta'_0,\ldots,\delta'_n)
\Longrightarrow
(Id_n,Receipt_n)=(Id'_n,Receipt'_n).
\]

Semantic time is returned-event order. Wall clocks, latency, process scheduling diagnostics and renderer timing remain provenance only and cannot author runtime identity.

Every interaction is reduced under one serial kernel. Its semantic intent and result receive content-addressed identities. Replaying the same semantic intent may change transport metadata such as `replayed`, but cannot change the translational-truth result or deterministic receipt.

## Full-project relation

No historical module or natural form is deleted. Every tracked file participates in the deterministic project closure digest and is classified as one of:

- authoritative closure runtime;
- sealed compatibility chart;
- formal natural form;
- closure witness test;
- historical/explanatory atlas;
- build/source support.

Compatibility charts may be executed for historical comparison, but they do not author current truth or mutation. The import closure rooted at `closure_supernet.api_agent` is the only published semantic authority.

## Enforcement

`closure-supernet-determinism-audit --root .` deterministically:

1. hashes every Git-tracked project file in lexical order;
2. derives the authoritative Python import closure;
3. rejects imports of sealed legacy runtimes into the published authority;
4. requires the deterministic kernel to be attached before browser, agent or self-runtime transports;
5. requires agent mutation to use `app.state.supernet_translate` and forbids the older Sense/topology/selection mutation entrypoints;
6. requires self-runtime to remain a read-only relative projection;
7. requires one published mutating HTTP relation;
8. rejects entropy or wall-clock calls inside the deterministic kernel.

The audit is a blocking CI gate. Dynamic tests additionally run the same ordered return history in two fresh runtimes and require identical translational-truth identities and deterministic receipts.

Thus the executable project relation is:

\[
\boxed{
\text{full project}
=
\text{one deterministic closure reducer}
+
\text{all other code as source-preserving lenses or retained charts}.
}
\]
