# Latent Memory and Rule-Transformation Protocol

## Purpose

Uniface stores and operates notes in a latent relational space without replacing their source notation. The canonical memory object is the exact occurrence, not its embedding.

## 1. Canonical occurrence

```text
NoteOccurrence
  id
  source_id
  exact_text
  exact_symbols
  images_or_drawings
  date
  source_location
  surrounding_context
  author_status
  checksum
```

Original occurrences are immutable. Corrections and rewrites are new occurrences with explicit relations to the original.

## 2. Relational state

```text
RelationRecord
  source_occurrence
  target_occurrence
  relation_type
  ordered_operator_path
  preserved_structure
  transformed_structure
  omitted_or_hidden_structure
  proposed_by
  confirmed_by
  status
  evidence_refs
  rule_version
```

Recommended relation types:

```text
SAME_LITERAL_EQUATION
NOTATIONAL_VARIANT
SAME_OPERATOR_PATH
INVERSE_PATH
FRAME_TRANSLATION
REFINEMENT
COARSENING
PRECURSOR
LATER_READING
FORMALIZES
SIMULATES
CONTRADICTS
PHYSICAL_ANALOGY
SOCIOECONOMIC_ANALOGY
MORAL_CONSEQUENCE
OPEN_RELATION
```

## 3. Hybrid latent space

The system combines:

```text
literal source archive
+ semantic embeddings
+ axiometric operator graph
+ temporal interaction graph
+ formal proof graph
+ simulation/evidence graph
+ cultural-moral consequence graph
```

No layer substitutes for another.

- Embeddings retrieve possible semantic neighbors.
- Operator paths compare intended operations.
- Proof links scope machine-checked readings.
- Evidence links distinguish simulation from observation.
- Cultural-moral links preserve affected perspectives and consequences.

## 4. Interaction event

```text
InteractionEvent
  user_input
  retrieved_sources
  assistant_operation
  proposed_relations
  generated_artifacts
  returned_interpretation
  user_response
  accepted_changes
  rejected_changes
  open_changes
```

An interaction may update the explicit memory graph, but it does not alter an original note.

## 5. Admissibility test

A proposed transformation passes only when:

```text
SOURCE_REVERSIBLE
SYMBOL_PRESERVING
OPERATOR_PATH_EXPLICIT
VARIANTS_NOT_SILENTLY_NORMALIZED
STATUS_EXPLICIT
AFFECTED_PERSPECTIVES_RETAINED
FORMAL_SCOPE_EXPLICIT
EMPIRICAL_SCOPE_EXPLICIT
REOPENING_AVAILABLE
```

Failure of any required condition keeps the transformation OPEN or rejects it.

## 6. Rule transformation

```text
RuleVersion
  rule_id
  exact_rule_text
  parent_version
  reason_for_change
  source_interactions
  consequences
  compatibility_notes
  active_from
```

A rule change never silently rewrites historical outputs. Every output retains the rule version that generated it.

Typical reasons for revision:

- closure was assumed too early;
- return was treated terminally;
- a Turing chart was promoted to foundation;
- a local language was treated as universal;
- a contradiction was hidden;
- a projection deleted morally relevant perspectives;
- formal proof was overstated as physical evidence.

## 7. Retrieval and return

Every generated relation must provide a reverse path:

```text
current projection
→ supporting relation records
→ exact source occurrences
→ operator paths
→ formal/simulation/evidence witnesses
→ unresolved alternatives
```

A Black Mirror node without this source-reversible path is not admissible as a global interface object.

## 8. Assistant behavior

The assistant should:

1. retrieve the literal occurrence before normalizing it;
2. use the author’s source symbols in the primary explanation;
3. label classical notation as a derived chart;
4. distinguish memory retrieval from inference;
5. preserve notational conflicts;
6. expose the path behind a proposed unity;
7. record what a projection deletes;
8. preserve OPEN where evidence or translation is incomplete;
9. return transformed rules or notes as new versions;
10. allow every provisional return to reopen.

## 9. Memory qualification

“Shaping latent memory” means shaping the explicit relational context through which future interactions are interpreted: saved notes, typed links, summaries, theorem maps, and project artifacts. It does not imply private online retraining of model weights after each conversation.

## 10. Minimal implementation stores

```text
occurrences/
relations/
operator-paths/
interactions/
rule-versions/
formal-witnesses/
simulations/
evidence/
projections/
open-seams/
```

The system may use a vector database, graph database, object store, and theorem index, but the literal source archive remains canonical.
