# Living Closure Supernet Interface

## Instantiated relation

The public interface now enacts the current NRRF764–765 reading:

```text
real problem
→ note / loop step
→ interaction / solution
→ collective action
→ returned consequence
→ agentic reintegration
→ reopened problem
```

This is not a post-and-ranking social feed. The interface stores exact authorship, relative perspectives, real situations, interactions, action commitments, returned consequences, and reopenable interpretations. Likes, follower totals, money, model confidence, and global quality scores are not foundational fields.

## Problems are real

A public `Problem` must contain:

```text
exact source occurrence
non-empty situations
creator
relative perspective (optional)
affected perspectives
visibility
append-only state history
```

An empty situation list is rejected. The initial state is `OPEN`: the problem presents something real while discretion remains.

Problem states are append-only:

```text
OPEN
ACTIVE
RETURNED
LOCALLY_SETTLED
REOPENED
```

A settled state is local and can reopen. State changes never rewrite the source problem.

## Notes are loop steps

A note attached to a problem is stored as:

```text
immutable occurrence
+ self-interaction of the problem
+ solution receipt
```

It is neither treated as an external rule that forces the field nor as a suggestion that leaves the field unchanged.

## Solutions are interactions

Every living-network interaction receives exactly one `SolutionReceipt`.

```text
solution receipt
  interaction_id
  source problem
  target problem
  OPEN / TRUE / FALSE at the current reading
  reason
```

The default is `OPEN`: the interaction constitutes a solution relation without autonomously claiming that all discretion has ended.

Interaction forms include:

```text
NOTE
QUESTION
INTERPRETATION
TRANSLATION
ACTION_PROPOSAL
RETURN
REINTERPRETATION
```

Each interaction records what it preserves, transforms, omits, which perspectives it affects, and which relative perspectives it translates between.

## Collective action

A collective action is not a popularity score. It contains:

```text
real problem
exact intent occurrence
participants
affected perspectives
open assumptions
append-only action state
returned consequences
```

Action states are:

```text
PROPOSED
COMMITTED
ACTIVE
RETURNED
REOPENED
```

The public interface makes collective action the social return path:

```text
shared interpretation
→ commitment
→ action
→ consequence
→ reintegration
```

## Agentic closure-learning reintegration

The living reintegration agent processes every returned consequence once. It:

1. preserves the exact problem and exact return occurrences;
2. creates a source-reversible `MORAL_CONSEQUENCE` candidate relation;
3. records what was preserved and what changed;
4. names OPEN questions rather than declaring terminal settlement;
5. checks whether affected perspectives were omitted;
6. creates an OPEN seam when moral completeness cannot be claimed;
7. reopens the problem and action;
8. lets the ordinary interpretation and admission agents process the relation;
9. applies later participant confirmation or rejection without deleting the prior OPEN admission.

The agent may change future attention and relation proposals. It may not overwrite sources, self-certify global truth, or erase dissenting and affected perspectives.

## Public interface

The public site at `/` supports:

- creating persistent participant records;
- opening real problems;
- adding notes as loop steps;
- creating interactions as solutions;
- proposing collective actions;
- returning consequences;
- inspecting living field state;
- viewing the current Black Mirror projection;
- confirming or rejecting reintegration proposals;
- reopening the field through each return.

The autonomous runtime console remains available at `/runtime`. OpenAPI documentation remains at `/docs`.

## Public API

```text
GET  /network/capabilities
POST /network/participants
GET  /network/participants
POST /network/perspectives
GET  /network/perspectives
POST /network/problems
GET  /network/problems
GET  /network/problems/{id}
GET  /network/problems/{id}/field
POST /network/problems/{id}/state
POST /network/problems/{id}/notes
POST /network/interactions
GET  /network/interactions
GET  /network/solutions
POST /network/actions
GET  /network/actions
POST /network/actions/{id}/state
POST /network/actions/{id}/returns
GET  /network/returns
POST /network/reintegrate
GET  /network/reintegration
POST /network/reintegration/{id}/decision
GET  /network/field
```

## Persistent storage

The existing event-sourced SQLite database now also contains:

```text
living_participants
living_perspectives
living_problems
living_problem_states
living_interactions
living_solution_receipts
living_problem_notes
living_actions
living_action_states
living_action_returns
living_reintegration_proposals
living_reintegration_decisions
living_state
```

Exact text still lives in the canonical immutable `occurrences` table. Living-network objects reference those occurrences. Interpretations and states may evolve through additional records; the source does not mutate.

## Translational truth of interaction

The public field does not equate interaction with popularity or agreement. A translation becomes active through the same source-preserving pipeline as the rest of Closure Supernet:

```text
exact occurrence
→ candidate relation
→ interpretation witness
→ configured admission
→ current projection
→ interaction and consequence
→ reintegration
→ reopening
```

`TRUE` remains a current admitted relation, not a terminal end. `FALSE` preserves contradiction. `OPEN` preserves coherent incompletion.

## Progress boundary

Implemented in version `0.3.0`:

- persistent public participant and perspective forms;
- real-problem validation and append-only state;
- note-as-loop-step persistence;
- interaction-as-solution receipts;
- collective actions and returned consequences;
- agentic reintegration into the canonical relation engine;
- affected-perspective OPEN seams;
- public web interface and living-field API;
- Black Mirror and source reverse indexes inside the living projection;
- autonomous-cycle integration and test coverage.

Not yet claimed complete:

- production cryptographic participant authentication;
- fine-grained private/community authorization and encryption;
- public cloud deployment;
- multi-node federation and peer discovery;
- replicated storage beyond the single SQLite node;
- community-specific admission constitutions;
- cryptographically signed collective commitments and action receipts;
- machine-checked refinement from the Python runtime to NRRF764–765;
- empirical validation that public use produces the intended conscious-cultural or moral outcomes.

These are the next closure levels. Their absence is explicit rather than hidden behind a claim of terminal completion.
