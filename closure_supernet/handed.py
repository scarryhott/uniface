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
    """Finite executable NRRF799/800 chart inside the one Supernet runtime."""

    def __init__(self, runtime: "ClosureSupernetRuntime", store: HandedLifeStore):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_readings": ["NRRF799", "NRRF800"],
            "canonical_runtime_operation": "integrate",
            "ball": "ZMod 4",
            "ball_sheaves": 4,
            "ball_step": "phase + 1 mod 4",
            "ball_step_order_exact": 4,
            "hair": "natural completion of the ball step",
            "hair_sheaves": 1,
            "hair_reading_universal_for_ball_step_invariants": True,
            "hand": [Hand.LEFT.value, Hand.RIGHT.value],
            "ball_return": "same hand, phase + 1",
            "hair_return": "inverse hand, phase - 1",
            "self_limit": "hairReturn after ballReturn = hand inversion at fixed phase",
            "self_limit_order_exact": 2,
            "left_handed_potential_gate": True,
            "human_relation_mapping": True,
            "common_shift_observed": False,
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
                        "NRRF800": "handed life ball return hair potential gate temporal closure",
                        "name": data.name,
                        "initial": evaluation["initial_state"],
                        "ball": evaluation["ball_carrier"],
                        "hair_classes": evaluation["hair_classes"],
                        "left_gate_trace": evaluation["left_handed_gate_trace"],
                    }
                ),
                authored_by=data.authored_by,
                form_label="handed life temporal closure",
                language_label="NRRF799/800 four-ball one-hair chart",
                source_id="handed-life-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "generate one hair from the four-phase ball step",
                    "apply ball and inverse-hair returns",
                    "derive the self-limit hand inversion",
                    "retain finite completion lineage",
                ],
                constraints=[
                    "finite ZMod 4 / two-hand executable chart",
                    "no biological interpretation inferred",
                    "no universal human law inferred",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF799",
                    "NRRF800",
                    "ballReturn",
                    "hairReturn",
                    "left-handed potential gate",
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
                    "formal_readings": ["NRRF799", "NRRF800"],
                    "evaluation": evaluation,
                    "source_ids": source_ids,
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
                "four ball phases",
                "one generated hair class",
                "ball/hair return equations",
                "self-limit hand inversion",
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
                "left_handed_gate_complete": evaluation["left_handed_gate_complete"],
                "biological_interpretation_selected": False,
                "truth_issued": False,
            },
            determined_form={
                "ball_sheaves": [0, 1, 2, 3],
                "hair_class": "hair:unit",
                "hand": [Hand.LEFT.value, Hand.RIGHT.value],
                "ball_return": "same hand / phase + 1 mod 4",
                "hair_return": "inverse hand / phase - 1 mod 4",
                "self_limit": "hand inversion / fixed ball phase",
                "canonical_biological_interpretation": None,
            },
            unitary_path_partition={
                "ball_cycle": [0, 1, 2, 3, 0],
                "hair_completion_classes": 1,
                "left_gate_trace": evaluation["left_handed_gate_trace"],
                "local_halt": "four-step ball return",
                "global_continuation": "same hair reopened through next state",
            },
            reason=(
                "The four-phase ball step generates one hair class and the stated "
                "return equations determine the handed temporal trace"
            ),
        )
        self.runtime.supernet_integrator.transition(
            receipt["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The handed-life chart returns as reopenable successor potential",
                actor_id=data.authored_by,
                returned_resource_ids=[system_id],
                successor_potential=[
                    {
                        "kind": "handed-life continuation",
                        "system_id": system_id,
                        "next": "ballReturn or hairReturn",
                        "hair_class": "hair:unit",
                    }
                ],
                metadata={
                    "truth_issued": False,
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
            "formal_readings": ["NRRF799", "NRRF800"],
            "canonical_runtime_operation": "integrate",
            "ball_sheaves": 4,
            "hair_sheaves": 1,
            "biological_claimed": False,
            "human_law_claimed": False,
            "truth_issued": False,
        }
        self.store.set_state("handed_life_field_projection", projection)
        return projection
