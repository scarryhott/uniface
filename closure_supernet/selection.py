from __future__ import annotations

import json
import uuid
from typing import Any, TYPE_CHECKING

from .models import EvidenceStatus, Verdict
from .selection_models import (
    SelectionFieldProjection,
    SelectionReadingCreate,
    SelectionReadingEvaluation,
    SelectionReadingState,
)
from .selection_store import SelectionStore, utcnow
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


class SelectionAuditManager:
    """Executable NRRF790 reading over the canonical Supernet integrator."""

    def __init__(self, runtime: "ClosureSupernetRuntime", store: SelectionStore):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_reading": "NRRF790",
            "canonical_runtime_operation": "integrate",
            "complete_iff_natural_selection": True,
            "incomplete_admissible_choice_is_forced_isolation": True,
            "natural_selection_never_removes_admissible_alternative": True,
            "empty_reading_selects_nothing": True,
            "completing_an_incomplete_reading_is_isolation": True,
            "explicit_symmetry_witness_for_forced_isolation": True,
            "no_equivariant_selector_away_from_completeness": True,
            "selection_applies_after_level_orbit_unification": True,
            "canonical_presentation": None,
            "determination_issues_truth": False,
        }

    @staticmethod
    def evaluate(data: SelectionReadingCreate) -> SelectionReadingEvaluation:
        admissible = list(data.admissible_symbols)
        count = len(admissible)
        complete = count == 1
        empty = count == 0
        branching = count >= 2

        natural_symbol = admissible[0] if complete else None
        forced = branching and data.selected_symbol is not None
        isolated = data.selected_symbol if forced else None
        removed = [item for item in admissible if item != isolated] if forced else []

        if empty:
            state = SelectionReadingState.EMPTY_TOTAL_ISOLATION
        elif complete:
            state = SelectionReadingState.NATURAL_SELECTION
        elif forced:
            state = SelectionReadingState.FORCED_ISOLATION
        else:
            state = SelectionReadingState.OPEN_BRANCHING

        symmetry_witness: dict[str, Any] | None = None
        if forced and isolated is not None and removed:
            other = removed[0]
            symmetry_witness = {
                "kind": "transposition",
                "swaps": [isolated, other],
                "preserves_original_admissibility": True,
                "moves_selected_symbol": True,
                "breaks_isolated_reading": True,
            }

        return SelectionReadingEvaluation(
            state=state,
            complete=complete,
            incomplete=not complete,
            empty=empty,
            branching=branching,
            admissible_count=count,
            natural_selection=complete,
            natural_selection_symbol=natural_symbol,
            forced_isolation=forced,
            isolated_symbol=isolated,
            removed_admissible_symbols=removed,
            strict_strengthening=forced,
            symmetry_witness=symmetry_witness,
            selected_symbol_fixed_by_all_reading_symmetries=complete,
            completing_is_isolating=forced,
            natural_selection_iff_not_forced_isolation=True,
            no_natural_selector_away_from_completeness=branching,
            total_isolation_from_field=empty,
            selection_authority_required=forced,
        )

    async def create_reading(self, data: SelectionReadingCreate) -> dict[str, Any]:
        reading_id = str(uuid.uuid4())
        evaluation = self.evaluate(data)

        inherited_sources = list(data.source_ids)
        parent_event_ids: list[str] = []
        causal_predecessor_ids: list[str] = []
        if data.source_event_id is not None:
            source_event = self.runtime.supernet_store.get_event(data.source_event_id)
            inherited_sources.extend(source_event["exact_source_ids"])
            parent_event_ids.append(data.source_event_id)
            causal_predecessor_ids.append(data.source_event_id)
        inherited_sources = list(dict.fromkeys(inherited_sources))

        exact_text = json.dumps(
            {
                "NRRF790": "complete natural selection / incomplete forced isolation",
                "name": data.name,
                "field_symbols": data.field_symbols,
                "admissible_symbols": data.admissible_symbols,
                "selected_symbol": data.selected_symbol,
                "state": evaluation.state.value,
                "removed_admissible_symbols": evaluation.removed_admissible_symbols,
                "symmetry_witness": evaluation.symmetry_witness,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="selection completeness audit",
                language_label="NRRF790 admissibility reading",
                source_id="selection-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "distinguish natural completion from forced isolation",
                    "retain removed admissible alternatives",
                    "carry explicit symmetry witness",
                    "preserve selection authorship and scope",
                ],
                constraints=[
                    "natural selection requires a singleton reading",
                    "forced isolation is not foundational naturality",
                    "empty reading selects nothing",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF790",
                    evaluation.state.value,
                    "natural selection",
                    "forced isolation",
                ],
                causal_predecessor_ids=causal_predecessor_ids,
                parent_event_ids=parent_event_ids,
                affected_perspectives=[
                    item
                    for item in [data.perspective_id, data.authored_by]
                    if item is not None
                ],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="selector",
                external_key=data.external_key or f"selection:{reading_id}",
                metadata={
                    **data.metadata,
                    "selection_reading_id": reading_id,
                    "formal_reading": "NRRF790",
                    "selection_state": evaluation.state.value,
                    "selection_scope": data.selection_scope,
                    "evaluation": evaluation.model_dump(mode="json"),
                    "source_ids": inherited_sources,
                    "canonical_presentation": None,
                    "truth_issued": False,
                },
            )
        )

        row = {
            "id": reading_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "field_symbols": data.field_symbols,
            "admissible_symbols": data.admissible_symbols,
            "selected_symbol": data.selected_symbol,
            "source_event_id": data.source_event_id,
            "selection_scope": data.selection_scope,
            "perspective_id": data.perspective_id,
            "problem_id": data.problem_id,
            "evaluation": evaluation.model_dump(mode="json"),
            "source_ids": inherited_sources,
            "metadata": {
                **data.metadata,
                "canonical_presentation": None,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        stored = self.store.create_reading(row)

        if evaluation.state in {
            SelectionReadingState.NATURAL_SELECTION,
            SelectionReadingState.FORCED_ISOLATION,
        }:
            selected = (
                evaluation.natural_selection_symbol
                if evaluation.natural_selection
                else evaluation.isolated_symbol
            )
            self.runtime.supernet_integrator.determine(
                receipt["event_id"],
                actor_id=data.authored_by,
                rigidity_scope=[data.selection_scope, *data.field_symbols],
                rigidity_receipt={
                    "prior_reading_complete": evaluation.complete,
                    "prior_reading_branching": evaluation.branching,
                    "post_selection_reading_complete": True,
                    "determination_origin": evaluation.state.value,
                    "natural_selection": evaluation.natural_selection,
                    "forced_isolation": evaluation.forced_isolation,
                    "strict_strengthening": evaluation.strict_strengthening,
                    "removed_admissible_symbols": evaluation.removed_admissible_symbols,
                    "symmetry_witness": evaluation.symmetry_witness,
                },
                determined_form={
                    "selected_symbol": selected,
                    "selection_state": evaluation.state.value,
                    "original_admissible_symbols": data.admissible_symbols,
                    "removed_admissible_symbols": evaluation.removed_admissible_symbols,
                    "canonical_presentation": None,
                },
                unitary_path_partition={
                    "path": [
                        "admissibility reading",
                        evaluation.state.value,
                        "singleton completion",
                    ],
                    "partition": {
                        "retained": [] if selected is None else [selected],
                        "removed": evaluation.removed_admissible_symbols,
                    },
                    "symmetry_witness": evaluation.symmetry_witness,
                },
                reason=(
                    "The reading was already complete and therefore naturally selected"
                    if evaluation.natural_selection
                    else "An authored isolation completed a branching reading; the result is determined but not natural"
                ),
            )
            self.runtime.supernet_integrator.transition(
                receipt["event_id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RETURNED,
                    verdict=Verdict.OPEN,
                    reason=(
                        "The natural selection returns as successor potential"
                        if evaluation.natural_selection
                        else "The forced isolation returns with its removed alternatives and reopening lineage"
                    ),
                    actor_id=data.authored_by,
                    returned_resource_ids=[reading_id],
                    successor_potential=[
                        {
                            "form_type": "selection-reading",
                            "reading_id": reading_id,
                            "selection_state": evaluation.state.value,
                            "selected_symbol": selected,
                            "removed_admissible_symbols": evaluation.removed_admissible_symbols,
                            "reopenable": True,
                        }
                    ],
                    metadata={
                        "nrrf790": True,
                        "natural_selection": evaluation.natural_selection,
                        "forced_isolation": evaluation.forced_isolation,
                        "truth_issued": False,
                    },
                ),
            )
        else:
            self.runtime.supernet_integrator.transition(
                receipt["event_id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RELATION_SENSED,
                    verdict=Verdict.OPEN,
                    reason=(
                        "The reading is empty and selects nothing"
                        if evaluation.empty
                        else "Several symbols remain admissible; no natural selection exists"
                    ),
                    actor_id=data.authored_by,
                    successor_potential=[
                        {
                            "form_type": "selection-reading",
                            "reading_id": reading_id,
                            "selection_state": evaluation.state.value,
                            "admissible_symbols": data.admissible_symbols,
                        }
                    ],
                    metadata={
                        "nrrf790": True,
                        "natural_selection": False,
                        "forced_isolation": False,
                        "truth_issued": False,
                    },
                ),
            )

        self.projection()
        return self.store.get_reading(stored["id"])

    def projection(self) -> dict[str, Any]:
        readings = self.store.list_readings()
        source_reverse_index: dict[str, list[str]] = {}
        for reading in readings:
            source_reverse_index[f"selection:{reading['id']}"] = list(
                dict.fromkeys(
                    [reading["occurrence_id"], *reading.get("source_ids", [])]
                )
            )
        projection = SelectionFieldProjection(
            generated_at=utcnow(),
            readings=readings,
            stats=self.store.stats(),
            source_reverse_index=source_reverse_index,
        ).model_dump(mode="json")
        self.store.set_state("selection_field_projection", projection)
        return projection
