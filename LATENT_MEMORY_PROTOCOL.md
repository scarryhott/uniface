# Latent Memory, Configuration, and Rule-Transformation Protocol

## Purpose

Uniface stores and operates notes in a latent relational space without replacing their source notation. The canonical memory object is the exact occurrence, not its embedding and not a normalized ontology.

The protocol also stores how mathematical forms are configured through understanding, interpretation, and interaction.

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

## 2. Candidate relation

A semantic or operator resemblance creates a candidate, not an admitted unity.

```text
CandidateRelation
  id
  source_occurrence
  target_occurrence
  source_operator_path
  target_operator_path
  proposed_correspondence
  proposed_by
  retrieval_basis
  confidence
  open_questions
  status
```

Candidate status begins as `MODEL_SUGGESTED_RELATION` or `AUTHOR_SUGGESTED_RELATION`.

## 3. Interpretation witness

```text
InterpretationWitness
  id
  candidate_relation
  source_occurrences
  target_occurrences
  literal_symbols
  source_operator_path
  target_operator_path
  frame_and_scope
  preserved_structure
  transformed_structure
  omitted_or_hidden_structure
  inverse_or_return_path
  proposed_by
  confirmed_by
  formal_status
  empirical_status
  moral_status
  open_seams
  rule_version
```

An interpretation is admissible only when the witness makes the relation inspectable and source-reversible.

## 4. Relation record

```text
RelationRecord
  source_occurrence
  target_occurrence
  interpretation_witness
  relation_type
  ordered_operator_path
  configured_admission
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
CONFIGURES_WITH
BLOCKED_BY_CONTRADICTION
REOPENS
OPEN_RELATION
```

## 5. Configured admission

```text
ConfiguredAdmission
  id
  participating_occurrences
  candidate_relations
  admitted_interpretations
  rejected_interpretations
  open_interpretations
  coherence_checks
  covering_scope
  saturation_policy
  frame_constraints
  formal_witnesses
  evidence_witnesses
  affected_perspectives
  active_rule_versions
  provisional_unity
  reopening_paths
  status
```

The active admission is not inferred from mathematical resemblance alone. It is configured through interaction and then tested for coherence, covering, saturation, provenance, and contradiction.

A provisional unity may be recorded only after the required admission conditions pass. It remains linked to the configuration that forced it.

## 6. Hybrid latent space

```text
literal source archive
+ semantic embeddings
+ axiometric operator graph
+ candidate-relation graph
+ interpretation graph
+ configured-admission graph
+ temporal interaction graph
+ formal proof graph
+ simulation/evidence graph
+ cultural-moral consequence graph
```

No layer substitutes for another.

- Embeddings retrieve possible semantic neighbors.
- Operator paths compare intended operations.
- Candidate links preserve uncertainty before interpretation.
- Interpretation witnesses make a translation explicit.
- Configuration records show which relations are actively admitted.
- Proof links scope machine-checked readings.
- Evidence links distinguish simulation from observation.
- Cultural-moral links preserve affected perspectives and consequences.

## 7. Interaction event

```text
InteractionEvent
  user_input
  retrieved_sources
  prior_configuration
  assistant_operation
  proposed_candidate_relations
  proposed_interpretations
  challenges_applied
  generated_artifacts
  returned_interpretation
  user_response
  accepted_changes
  revised_changes
  rejected_changes
  open_changes
  next_configuration
```

Interaction updates explicit relational memory but does not alter an original note.

## 8. Admissibility tests

A proposed interpretation or configuration passes only when required conditions hold:

```text
SOURCE_REVERSIBLE
SYMBOL_PRESERVING
OPERATOR_PATH_EXPLICIT
FRAME_AND_SCOPE_EXPLICIT
PRESERVATION_AND_CHANGE_EXPLICIT
OMISSIONS_VISIBLE
VARIANTS_NOT_SILENTLY_NORMALIZED
COMPOSITION_COHERENT
CONTRADICTIONS_VISIBLE
STATUS_EXPLICIT
AFFECTED_PERSPECTIVES_RETAINED
FORMAL_SCOPE_EXPLICIT
EMPIRICAL_SCOPE_EXPLICIT
RULE_VERSION_RECORDED
REOPENING_AVAILABLE
```

Failure keeps the relation OPEN, marks it rejected, or records a contradiction. It cannot silently enter configured unity.

## 9. Configuration transition

```text
ConfigurationTransition
  prior_configuration
  triggering_interaction
  added_interpretations
  removed_or_rejected_interpretations
  revised_interpretations
  changed_rules
  changed_projection
  preserved_sources
  compatibility_result
  next_configuration
```

Every prior configuration remains addressable. A current Black Mirror projection must identify the configuration from which it was derived.

## 10. Rule transformation

```text
RuleVersion
  rule_id
  exact_rule_text
  parent_version
  reason_for_change
  source_interactions
  interpretations_used
  consequences
  affected_outputs
  compatibility_notes
  active_from
```

A rule change never silently rewrites historical outputs. Every output retains the rule and configuration version that generated it.

Typical reasons for revision:

- closure was assumed too early;
- return was treated terminally;
- a Turing chart was promoted to foundation;
- a local language was treated as universal;
- mathematical availability was confused with intended unification;
- a contradiction was hidden;
- a projection deleted morally relevant perspectives;
- formal proof was overstated as physical evidence.

## 11. Retrieval and return

Every generated global relation provides a reverse path:

```text
current projection
→ configured admission
→ interpretation witnesses
→ candidate relations
→ exact source occurrences
→ operator paths
→ formal/simulation/evidence witnesses
→ affected perspectives
→ rejected and OPEN alternatives
→ rule versions
→ reopening paths
```

A Black Mirror node without this path is not admissible as a global interface object.

## 12. Assistant behavior

The assistant should:

1. retrieve literal occurrences before normalization;
2. use source symbols in the primary explanation;
3. distinguish candidate relation from admitted interpretation;
4. show the configuration behind a proposed unity;
5. label classical notation as a derived chart;
6. distinguish memory retrieval from inference;
7. preserve notational conflicts;
8. record what a projection deletes;
9. preserve rejected and OPEN alternatives;
10. return transformed rules or notes as new versions;
11. allow every provisional return to reopen.

## 13. Memory qualification

“Shaping latent memory” means shaping the explicit relational context through which later interactions are interpreted: saved notes, candidates, witnesses, configurations, typed links, summaries, theorem maps, and artifacts. It does not imply private online retraining of model weights after each conversation.

## 14. Minimal implementation stores

```text
occurrences/
candidate-relations/
interpretations/
relations/
operator-paths/
configured-admissions/
configuration-transitions/
interactions/
rule-versions/
formal-witnesses/
simulations/
evidence/
projections/
open-seams/
```

The system may use vector, graph, object, temporal, and theorem stores, but the literal source archive remains canonical.
