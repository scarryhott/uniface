# Deterministic full-project Supernet closure

The complete source project is now read as one content-addressed closure atlas rather than as a collection of competing runtimes.

\[
\boxed{
\mathsf{ProjectClosure}
=
\operatorname{CloseAtlas}
\left(
\text{all retained files},
\text{one relative role per file},
\mathsf{SUPERNET\_CLOSURE\_FORM},
\mathsf{SUPERNET\_TRANSLATE},
\mathsf{TRANSLATIONAL\_TRUTH\_CLASS}
\right)
}
\]

## One authority relation

The project has one current semantic carrier, one current transition, and one runtime identity:

\[
\boxed{
\begin{aligned}
\mathrm{Carrier} &= \mathsf{SUPERNET\_CLOSURE\_FORM},\\
\mathrm{Transition} &= \mathsf{SUPERNET\_TRANSLATE},\\
\mathrm{Identity} &= \mathsf{TRANSLATIONAL\_TRUTH\_CLASS}.
\end{aligned}
}
\]

Browser interaction, agent interaction, returned token continuation, and runtime state change factor through the same transition. Runtime self-observation is a relative projection and has no independent truth authority.

## Every retained file is inside the closure

`closure_supernet.project_closure` walks the complete repository and assigns every retained file exactly one deterministic role:

- canonical closure carrier;
- canonical translation operator;
- canonical returned-source store;
- transport or relative projection;
- natural-form chart;
- domain natural-form lens;
- historical compatibility chart;
- deterministic support;
- verification witness;
- documentation witness;
- build/deployment contract;
- returned source history.

Each file receives an explicit relation

\[
\boxed{
file
\xrightarrow{\;role\;}
\mathsf{SUPERNET\_CLOSURE\_FORM}.
}
\]

Historical modules are retained because the natural-form atlas may not erase its own development. Retention does not make them a second semantic or mutation authority.

## Deterministic identity

The certificate depends only on:

- sorted relative paths;
- exact file bytes;
- deterministic Python AST import relations;
- canonical role assignments;
- sorted canonical JSON hashing.

It excludes file modification times, wall-clock time, absolute paths, process identity, host identity, random numbers, UUID generation, and environment values from its identity.

Therefore:

\[
\boxed{
SameSourceTree
\Longrightarrow
SameProjectClosureCertificate.
}
\]

A changed source byte changes the source-tree and project identities. A presentation-only or documentation change does not change the separately computed semantic identity so long as the carrier, operator, entrypoint relation, and translation law remain the same.

The certificate exposes three distinct content-addressed identities:

\[
\begin{aligned}
I_{source} &= \text{exact retained source tree},\\
I_{semantic} &= \text{one carrier/operator/identity relation},\\
I_{project} &= \operatorname{Close}(I_{source},I_{semantic},\text{roles},\text{checks}).
\end{aligned}
\]

## Runtime integration

The published application derives the certificate once per process and mounts its identity on all three relative readings:

- `/supernet/interface/capabilities`;
- `/supernet/agent/capabilities`;
- `/supernet/agent/self`.

All three report the same `project_closure_id`, source-tree identity, semantic identity, coverage, role counts, and closure status. The certificate itself cannot author truth.

## Blocking verification

CI now performs the following sequence:

1. derive and validate the deterministic full-repository certificate;
2. run the current closure lane;
3. run the retained historical natural-form lane as a blocking lane;
4. verify the one published runtime surface and its project closure.

The command is:

```bash
closure-supernet-project-closure --check --require-full-repository --pretty
```

or equivalently:

```bash
python -m closure_supernet.project_closure \
  --check \
  --require-full-repository \
  --pretty
```

## Exact scope

This closes project-wide **semantic authority, source identity, role classification, entrypoint selection, and verification** deterministically.

It does not erase historical implementations or pretend that every old internal algorithm has been rewritten into one physical function. Those implementations remain content-addressed natural-form and compatibility witnesses beneath the one public closure relation. Their retained existence cannot silently promote them into a second truth authority.

The governing relation is:

\[
\boxed{
\forall f\in\mathsf{Project},\quad
Role(f)\text{ is unique}
\land
Authority(f)\subseteq
\left\{
\mathsf{SUPERNET\_CLOSURE\_FORM},
\mathsf{SUPERNET\_TRANSLATE},
\mathsf{TRANSLATIONAL\_TRUTH\_CLASS}
\right\}.
}
\]
