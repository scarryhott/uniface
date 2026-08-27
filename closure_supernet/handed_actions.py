from __future__ import annotations

import uuid
from typing import Any, Callable

from .handed_core import (
    ball_return,
    hair_return,
    iterate,
    self_limit,
    stable,
    state,
    unique,
)
from .handed_models import (
    Hand,
    HandedMotionCreate,
    HandedRecordKind,
    HumanRelationCreate,
    MotionKind,
)
from .handed_store import utcnow
from .models import EvidenceStatus, Verdict
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope


class HandedActionMixin:
    runtime: Any
    store: Any

    async def create_motion(self, data: HandedMotionCreate) -> dict[str, Any]:
        system = self.store.get_system(data.system_id)
        start = state(
            data.start_hand or Hand(system["initial_hand"]),
            system["initial_ball_phase"]
            if data.start_ball_phase is None
            else data.start_ball_phase,
        )
        step_map: dict[MotionKind, Callable[[dict[str, Any]], dict[str, Any]]] = {
            MotionKind.BALL_RETURN: ball_return,
            MotionKind.HAIR_RETURN: hair_return,
            MotionKind.SELF_LIMIT: self_limit,
        }
        trace = iterate(start, step_map[data.motion], data.steps)
        end = {key: value for key, value in trace[-1].items() if key != "index"}
        source_ids, parents = self._source_context(data.source_event_id, data.source_ids)
        source_ids = unique(source_ids + system["source_ids"])
        parents.append(system["integration_event_id"])
        record_id = str(uuid.uuid4())
        evaluation = {
            "motion": data.motion.value,
            "steps": data.steps,
            "start": start,
            "end": end,
            "trace": trace,
            "same_hair_throughout": len({item["hair_class"] for item in trace}) == 1,
            "ball_return_hand_preserved": data.motion != MotionKind.BALL_RETURN
            or all(item["hand"] == start["hand"] for item in trace),
            "hair_gate_iff_odd": data.motion != MotionKind.HAIR_RETURN
            or ((end["hand"] != start["hand"]) == (data.steps % 2 == 1)),
            "self_limit_fixed_ball_phase": data.motion != MotionKind.SELF_LIMIT
            or end["ball_phase"] == start["ball_phase"],
            "self_limit_gate_iff_odd": data.motion != MotionKind.SELF_LIMIT
            or ((end["hand"] != start["hand"]) == (data.steps % 2 == 1)),
            "closed_full_state": end == start,
            "transition_class": data.motion.value,
            "truth_issued": False,
        }
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=stable(
                    {
                        "NRRF800": "handed-life motion trace",
                        "system_id": data.system_id,
                        "motion": data.motion.value,
                        "trace": trace,
                    }
                ),
                authored_by=data.authored_by,
                form_label="handed life motion trace",
                language_label="NRRF800 return trace",
                source_id="handed-life-supernet",
                capabilities=["apply exact handed-life return"],
                constraints=["finite submitted trace", "truth is not issued"],
                relation_hints=["NRRF800", data.motion.value],
                causal_predecessor_ids=unique(parents),
                parent_event_ids=unique(parents),
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="handed",
                external_key=f"handed:record:{record_id}",
                metadata={
                    **data.metadata,
                    "record_id": record_id,
                    "system_id": data.system_id,
                    "evaluation": evaluation,
                    "truth_issued": False,
                },
            )
        )
        stored = self.store.create_record(
            {
                "id": record_id,
                "occurrence_id": receipt["occurrence_ids"][0],
                "integration_event_id": receipt["event_id"],
                "kind": HandedRecordKind.MOTION_TRACE.value,
                "system_id": data.system_id,
                "name": f"{system['name']} — {data.motion.value}",
                "authored_by": data.authored_by,
                "source_event_id": data.source_event_id,
                "payload": data.model_dump(mode="json"),
                "evaluation": evaluation,
                "source_ids": source_ids,
                "metadata": data.metadata,
                "created_at": utcnow(),
            }
        )
        self._determine_record(receipt["event_id"], data.authored_by, record_id, evaluation)
        return stored

    @staticmethod
    def _relation_state(
        source_standing: int,
        target_standing: int,
        gate_hand: Hand,
    ) -> tuple[int, dict[str, Any]]:
        separation = int(target_standing) - int(source_standing)
        hand = Hand.LEFT if separation > 0 else Hand.RIGHT if separation < 0 else gate_hand
        return separation, state(hand, separation % 4)

    async def create_human_relation(self, data: HumanRelationCreate) -> dict[str, Any]:
        record_id = str(uuid.uuid4())
        separation, forward = self._relation_state(
            data.source_standing, data.target_standing, data.gate_hand
        )
        reverse_separation, reverse = self._relation_state(
            data.target_standing, data.source_standing, data.gate_hand.inverse
        )
        shifted_separation, shifted = self._relation_state(
            data.source_standing + data.common_shift,
            data.target_standing + data.common_shift,
            data.gate_hand,
        )
        four_separation = separation + 4
        _, four_state = self._relation_state(0, four_separation, data.gate_hand)
        after: dict[str, Any] | None = None
        transition_class = "OPEN_OTHER"
        if data.after_source_standing is not None and data.after_target_standing is not None:
            after_separation, after_state = self._relation_state(
                data.after_source_standing, data.after_target_standing, data.gate_hand
            )
            after = {
                "source_standing": data.after_source_standing,
                "target_standing": data.after_target_standing,
                "separation": after_separation,
                "state": after_state,
            }
            if after_state == ball_return(forward):
                transition_class = MotionKind.BALL_RETURN.value
            elif after_state == hair_return(forward):
                transition_class = MotionKind.HAIR_RETURN.value
        evaluation = {
            "source_participant": data.source_participant,
            "target_participant": data.target_participant,
            "source_standing": data.source_standing,
            "target_standing": data.target_standing,
            "separation": separation,
            "forward_state": forward,
            "reverse_separation": reverse_separation,
            "reverse_state": reverse,
            "nothing_absolute_read": True,
            "common_shift": data.common_shift,
            "shifted_separation": shifted_separation,
            "shifted_state": shifted,
            "common_shift_invariant": shifted_separation == separation and shifted == forward,
            "reverse_hands_are_inverse": reverse["hand"]
            == Hand(forward["hand"]).inverse.value,
            "reverse_ball_phases_are_inverse": (
                int(forward["ball_phase"]) + int(reverse["ball_phase"])
            )
            % 4
            == 0,
            "same_hair_both_directions": reverse["hair_class"] == forward["hair_class"],
            "after": after,
            "transition_class": transition_class,
            "one_act_away_from_gate_is_ball_return": separation != 0
            and transition_class == MotionKind.BALL_RETURN.value,
            "one_act_at_gate_is_hair_return": separation == 0
            and transition_class == MotionKind.HAIR_RETURN.value,
            "four_act_separation": four_separation,
            "four_act_state": four_state,
            "four_acts_ball_blind": four_state["ball_phase"] == forward["ball_phase"],
            "four_acts_relation_changed_by_four": four_separation - separation == 4,
            "every_human_relation_same_hair_in_chart": True,
            "gate_orientation_explicit_data": data.gate_hand.value,
            "human_law_claimed": False,
            "truth_issued": False,
        }
        source_ids, parents = self._source_context(data.source_event_id, data.source_ids)
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=stable(
                    {
                        "NRRF800": "human relation handed-life reading",
                        "name": data.name,
                        "participants": [data.source_participant, data.target_participant],
                        "standings": [data.source_standing, data.target_standing],
                        "evaluation": evaluation,
                    }
                ),
                authored_by=data.authored_by,
                form_label="handed human relation reading",
                language_label="NRRF800 submitted relation chart",
                source_id="handed-life-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "read relative hand, ball phase and hair",
                    "classify submitted before/after relation return",
                    "check common-shift invariance",
                ],
                constraints=[
                    "submitted integer standings only",
                    "equal-standing orientation is explicit chart data",
                    "no human law inferred",
                    "truth is not issued",
                ],
                relation_hints=["NRRF800", "human relation", transition_class],
                causal_predecessor_ids=parents,
                parent_event_ids=parents,
                affected_perspectives=[data.source_participant, data.target_participant],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="handed",
                external_key=f"handed:record:{record_id}",
                metadata={
                    **data.metadata,
                    "record_id": record_id,
                    "evaluation": evaluation,
                    "human_law_claimed": False,
                    "truth_issued": False,
                },
            )
        )
        stored = self.store.create_record(
            {
                "id": record_id,
                "occurrence_id": receipt["occurrence_ids"][0],
                "integration_event_id": receipt["event_id"],
                "kind": HandedRecordKind.HUMAN_RELATION.value,
                "system_id": None,
                "name": data.name,
                "authored_by": data.authored_by,
                "source_event_id": data.source_event_id,
                "payload": data.model_dump(mode="json"),
                "evaluation": evaluation,
                "source_ids": source_ids,
                "metadata": data.metadata,
                "created_at": utcnow(),
            }
        )
        self._determine_record(receipt["event_id"], data.authored_by, record_id, evaluation)
        return stored

    def _determine_record(
        self, event_id: str, actor_id: str, record_id: str, evaluation: dict[str, Any]
    ) -> None:
        self.runtime.supernet_integrator.determine(
            event_id,
            actor_id=actor_id,
            rigidity_scope=["submitted NRRF800 finite chart"],
            rigidity_receipt={
                "record_id": record_id,
                "relation_reading_deterministic_on_submitted_data": True,
                "physical_or_biological_interpretation_selected": False,
                "truth_issued": False,
            },
            determined_form={
                "record_id": record_id,
                "transition_class": evaluation.get("transition_class"),
                "hair_class": "hair:unit",
                "canonical_human_interpretation": None,
            },
            unitary_path_partition={
                "ball": "four phases",
                "hair": "one completion class",
                "return": evaluation.get("transition_class"),
            },
            reason="The submitted finite relation uniquely determines its handed-life reading",
        )
        self.runtime.supernet_integrator.transition(
            event_id,
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The handed-life reading returns while interpretation remains reopenable",
                actor_id=actor_id,
                returned_resource_ids=[record_id],
                successor_potential=[
                    {
                        "kind": "handed-life reopening",
                        "record_id": record_id,
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
