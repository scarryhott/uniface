from __future__ import annotations

import uuid
from typing import Any, TYPE_CHECKING

from .handed_actions import HandedActionMixin
from .handed_core import evaluate_system, stable, unique
from .handed_models import Hand, HandedLifeSystemCreate
from .handed_store import HandedLifeStore, utcnow
from .models import EvidenceStatus, Verdict
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


class HandedLifeManager(HandedActionMixin):
    """Finite NRRF800/802 chart downstream of the NRRF805 life primitive."""

    def __init__(self, runtime: "ClosureSupernetRuntime", store: HandedLifeStore):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_readings": ["NRRF799", "NRRF800", "NRRF802", "NRRF805"],
            "canonical_runtime_operation": "integrate",
            "ball": "ZMod 4 finite chart",
            "ball_sheaves": 4,
            "ball_step": "phase + 1 mod 4",
            "ball_step_order_exact": 4,
            "hair": "Closure ballStep finite chart",
            "hair_sheaves": 1,
            "hair_reading_universal_for_ball_step_invariants": True,
            "hand": [Hand.LEFT.value, Hand.RIGHT.value],
            "ball_return": "same chart hand, phase + 1",
            "hair_return": "inverse chart hand, phase - 1",
            "self_limit": "chart hand inversion at fixed phase",
            "self_limit_order_exact": 2,
            "left_handed_chart_gate": True,
            "left_handed_potential_gate_foundational": False,
            "human_relation_chart_available": True,
            "common_shift_observed": False,
            "closure_defined_once": True,
            "hair_is_closure_ball_step": True,
            "hand_is_closure_ball_return": True,
            "phase_is_closure_self_limit": True,
            "unified_cardinalities": {"hair": 1, "hand": 2, "phase": 4},
            "closure2_life_subsingleton": True,
            "finite_chart_only": True,
            "foundational_life_primitive": False,
            "temporal_role_assigned_from_hand": False,
            "potential_actual_requires_translational_truth": True,
            "internal_external_prior_to_translational_truth": False,
            "global_hair_zero_not_hair_cardinality_one": True,
            "local_ball_infinity_not_ball_cardinality_four": True,
            "parallel_closure_runtime_created": False,
            "biological_chirality_claimed": False,
            "biological_life_claimed": False,
            "human_law_claimed": False,
            "runtime_is_formal_proof": False,
            "truth_issued": False,
        }

    def _source_context(
        self, source_event_id: str | None, source_ids: list[str]
    ) -> tuple[list[str], list[str]]:
        exact_sources = list(source_ids)
        parents: list[str] = []
        if source_event_id is not None:
            event = self.runtime.supernet_store.get_event(source_event_id)
            exact_sources.extend(event["exact_source_ids"])
            parents.append(source_event_id)
        return unique(exact_sources), parents

    async def create_system(self, data: HandedLifeSystemCreate) -> dict[str, Any]:
        system_id = str(uuid.uuid4())
        evaluation = evaluate_system(data)
        source_ids, parents = self._source_context(data.source_event_id, data.source_ids)
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=stable(
                    {
                        "NRRF799": "natural translational completion from local ball step",
                        "NRRF800": "four-ball one-hair handed temporal chart",
                        "NRRF802": "hair hand and phase as instances of one closure construction",
                        "NRRF805_scope": "finite chart only after the Turing Being translational relation",
                        "name": data.name,
                        "initial": evaluation["initial_state"],
                        "ball": evaluation["ball_carrier"],
                        "hair_classes": evaluation["hair_classes"],
                        "foundation_status": evaluation["foundation_status"],
                        "unified_cardinalities": evaluation["unified_cardinalities"],
                        "left_gate_trace": evaluation["left_handed_gate_trace"],
                    }
                ),
                authored_by=data.authored_by,
                form_label="handed finite reaction chart",
                language_label="NRRF799/800/802 finite chart under NRRF805 scope",
                source_id="handed-life-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "generate one finite hair class from the four-phase ball step",
                    "apply chart ball and inverse-hair returns",
                    "derive chart hand and phase through one closure kernel",
                    "retain finite completion lineage",
                ],
                constraints=[
                    "finite ZMod 4 / two-hand executable chart",
                    "not the foundational Turing Being life carrier",
                    "left and right do not preassign potential or actual",
                    "internal and external require prior translational truth",
                    "global hair zero is not hair cardinality one",
                    "local ball infinity is not ball cardinality four",
                    "no biological interpretation inferred",
                    "no universal human law inferred",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF799",
                    "NRRF800",
                    "NRRF802",
                    "NRRF805 downstream chart",
                    "Closure step",
                    "ballReturn",
                    "hairReturn",
                    "four-sheaf ball one-sheaf hair",
                ],
                causal_predecessor_ids=parents,
                parent_event_ids=parents,
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="handed",
                external_key=f"handed:system:{system_id}",
                metadata={
                    **data.metadata,
                    "system_id": system_id,
                    "formal_readings": ["NRRF799", "NRRF800", "NRRF802", "NRRF805"],
                    "evaluation": evaluation,
                    "source_ids": source_ids,
                    "closure_defined_once": True,
                    "foundation_status": evaluation["foundation_status"],
                    "finite_ball_hair_foundational": False,
                    "temporal_role_assigned_from_hand": False,
                    "parallel_closure_runtime_created": False,
                    "runtime_is_formal_proof": False,
                    "truth_issued": False,
                },
            )
        )
        stored = self.store.create_system(
            {
                "id": system_id,
                "occurrence_id": receipt["occurrence_ids"][0],
                "integration_event_id": receipt["event_id"],
                "name": data.name,
                "authored_by": data.authored_by,
                "initial_hand": data.initial_hand.value,
                "initial_ball_phase": data.initial_ball_phase,
                "source_event_id": data.source_event_id,
                "perspective_id": data.perspective_id,
                "problem_id": data.problem_id,
                "source_ids": source_ids,
                "evaluation": evaluation,
                "metadata": {
                    **data.metadata,
                    "closure_defined_once": True,
                    "formal_readings": ["NRRF799", "NRRF800", "NRRF802", "NRRF805"],
                    "foundation_status": evaluation["foundation_status"],
                    "finite_ball_hair_foundational": False,
                    "temporal_role_assigned_from_hand": False,
                    "canonical_biological_interpretation": None,
                    "truth_issued": False,
                },
                "created_at": utcnow(),
            }
        )
        self.runtime.supernet_integrator.determine(
            receipt["event_id"],
            actor_id=data.authored_by,
            rigidity_scope=[
                "four finite ball phases",
                "one finite hair class",
                "chart return equations",
                "one closure kernel for chart hair hand and phase",
            ],
            rigidity_receipt={
                "ball_card": 4,
                "ball_step_order_exact": 4,
                "hair_card": 1,
                "completion_generated_from_local_ball_step": True,
                "every_hair_identification_has_finite_ball_path": evaluation[
                    "completion_every_identification_has_finite_path"
                ],
                "self_limit_order_exact": 2,
                "left_handed_chart_complete": evaluation["left_handed_gate_complete"],
                "closure_defined_once": evaluation["closure_defined_once"],
                "hair_isClosure": evaluation["hair_isClosure"],
                "hand_isClosure": evaluation["hand_isClosure"],
                "phase_isClosure": evaluation["phase_isClosure"],
                "closure2_life_subsingleton": evaluation[
                    "closure2_life_subsingleton"
                ],
                "foundation_status": evaluation["foundation_status"],
                "finite_ball_hair_foundational": False,
                "potential_actual_selected": False,
                "biological_interpretation_selected": False,
                "truth_issued": False,
            },
            determined_form={
                "ball_chart": [0, 1, 2, 3],
                "hair_chart_class": "hair:unit",
                "hand_chart": [Hand.LEFT.value, Hand.RIGHT.value],
                "ball_return": "same chart hand / phase + 1 mod 4",
                "hair_return": "inverse chart hand / phase - 1 mod 4",
                "self_limit": "chart hand inversion / fixed phase",
                "temporal_role": None,
                "internal": None,
                "external": None,
                "foundation_status": evaluation["foundation_status"],
                "unified_cardinalities": evaluation["unified_cardinalities"],
                "canonical_biological_interpretation": None,
            },
            unitary_path_partition={
                "ball_cycle": [0, 1, 2, 3, 0],
                "hair_completion_classes": 1,
                "hand_completion_classes": 2,
                "phase_completion_classes": 4,
                "joint_chart_completion_classes": 1,
                "left_gate_trace": evaluation["left_handed_gate_trace"],
                "local_chart_halt": "four-step finite return",
                "global_continuation": "requires a completed Turing Being reaction return",
            },
            reason=(
                "The finite chart is rigid under its submitted return equations; "
                "it does not determine foundational life roles before translational truth"
            ),
        )
        self.runtime.supernet_integrator.transition(
            receipt["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The finite handed chart returns without becoming the life foundation",
                actor_id=data.authored_by,
                returned_resource_ids=[system_id],
                successor_potential=[
                    {
                        "kind": "finite handed chart continuation",
                        "system_id": system_id,
                        "next": "bind to a completed Turing Being life event",
                        "hair_chart_class": "hair:unit",
                        "closure_kernel": "NRRF802",
                    }
                ],
                metadata={
                    "truth_issued": False,
                    "foundation_status": evaluation["foundation_status"],
                    "finite_ball_hair_foundational": False,
                    "parallel_closure_runtime_created": False,
                    "biological_life_claimed": False,
                    "human_law_claimed": False,
                },
            ),
        )
        return self.store.get_system(stored["id"])

    def projection(self) -> dict[str, Any]:
        systems = self.store.list_systems(limit=20_000)
        records = self.store.list_records(limit=20_000)
        projection = {
            "generated_at": utcnow(),
            "systems": systems,
            "records": records,
            "stats": self.store.stats(),
            "source_reverse_index": {
                **{
                    f"handed-system:{item['id']}": list(item["source_ids"])
                    for item in systems
                },
                **{
                    f"handed-record:{item['id']}": list(item["source_ids"])
                    for item in records
                },
            },
            "formal_readings": ["NRRF799", "NRRF800", "NRRF802", "NRRF805"],
            "canonical_runtime_operation": "integrate",
            "ball_sheaves": 4,
            "hair_sheaves": 1,
            "closure_defined_once": True,
            "hair_hand_phase_are_instances": True,
            "unified_cardinalities": {"hair": 1, "hand": 2, "phase": 4},
            "closure2_life_subsingleton": True,
            "finite_chart_only": True,
            "foundational_life_primitive": False,
            "temporal_role_assigned_from_hand": False,
            "potential_actual_requires_translational_truth": True,
            "global_hair_zero_not_hair_cardinality_one": True,
            "local_ball_infinity_not_ball_cardinality_four": True,
            "parallel_closure_runtime_created": False,
            "biological_claimed": False,
            "human_law_claimed": False,
            "truth_issued": False,
        }
        self.store.set_state("handed_life_field_projection", projection)
        return projection
