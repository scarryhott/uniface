from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Awaitable, Callable

from .living_models import (
    ActionReturnCreate,
    ActionState,
    ActionStateChange,
    CollectiveActionCreate,
    InteractionCreate,
    InteractionKind,
    NoteCreate,
    ParticipantCreate,
    PerspectiveCreate,
    ProblemCreate,
    ProblemState,
    ProblemStateChange,
    ReintegrationDecisionCreate,
    ReintegrationStatus,
)
from .living_store import LivingNetworkStore
from .models import OccurrenceCreate, RelationType, Verdict
from .store import EventStore


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


class LivingNetworkManager:
    """Public relative forms and agentic closure-learning reintegration.

    The manager never converts an external or public contribution directly into
    global truth. It preserves exact authorship, constitutes every solution as
    an interaction, and returns consequences to the originating problem as an
    OPEN reintegration proposal unless an author or later witness confirms it.
    """

    agent_name = "living-reintegration-agent"

    def __init__(
        self,
        event_store: EventStore,
        living_store: LivingNetworkStore,
        ingest: Callable[[OccurrenceCreate], Awaitable[dict[str, Any]]],
    ):
        self.event_store = event_store
        self.store = living_store
        self.ingest = ingest

    def capabilities(self) -> dict[str, Any]:
        return {
            "protocol": "closure.supernet/living-v1",
            "forms": [
                "participant",
                "perspective",
                "real_problem",
                "note_as_loop_step",
                "interaction_as_solution",
                "collective_action",
                "returned_consequence",
                "agentic_reintegration",
            ],
            "source_immutable": True,
            "relations_reopenable": True,
            "quantity_ranking_foundational": False,
            "turing_complete_assumed": False,
            "automatic_global_truth": False,
            "authentication_status": "development identity records; production cryptographic authentication remains a deployment layer",
        }

    def create_participant(self, data: ParticipantCreate) -> dict[str, Any]:
        participant = self.store.create_participant(data)
        self.event_store.append_event(
            "LIVING_PARTICIPANT_CREATED",
            "participant",
            participant["id"],
            {"display_name": participant["display_name"]},
        )
        return participant

    def create_perspective(self, data: PerspectiveCreate) -> dict[str, Any]:
        perspective = self.store.create_perspective(data)
        self.event_store.append_event(
            "LIVING_PERSPECTIVE_CREATED",
            "perspective",
            perspective["id"],
            {
                "participant_id": perspective["participant_id"],
                "visibility": perspective["visibility"],
                "parent_perspective_id": perspective["parent_perspective_id"],
            },
        )
        return perspective

    async def create_problem(self, data: ProblemCreate) -> dict[str, Any]:
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=data.exact_text,
                source_id=f"living-participant:{data.created_by}",
                source_context=f"Real problem: {data.title}",
                metadata={
                    **data.metadata,
                    "living_form": "PROBLEM",
                    "title": data.title,
                    "situations": data.situations,
                    "created_by": data.created_by,
                    "perspective_id": (
                        data.metadata.get("supernet_perspective_handle")
                        or data.perspective_id
                    ),
                    "visibility": str(data.visibility),
                    "affected_perspectives": data.affected_perspectives,
                    "language_label": data.language_label,
                    "problem_is_not_empty": True,
                },
            )
        )
        problem = self.store.create_problem(data, occurrence["id"])
        self.event_store.append_event(
            "LIVING_PROBLEM_CREATED",
            "problem",
            problem["id"],
            {
                "occurrence_id": occurrence["id"],
                "created_by": data.created_by,
                "situations": data.situations,
                "state": problem["current_state"],
            },
        )
        return problem

    def transition_problem(self, problem_id: str, data: ProblemStateChange) -> dict[str, Any]:
        problem = self.store.transition_problem(problem_id, data.state, data.reason, data.actor_id)
        self.event_store.append_event(
            "LIVING_PROBLEM_STATE_CHANGED",
            "problem",
            problem_id,
            {"state": str(data.state), "reason": data.reason, "actor_id": data.actor_id},
        )
        return problem

    async def add_note(self, problem_id: str, data: NoteCreate) -> dict[str, Any]:
        problem = self.store.get_problem(problem_id)
        interaction_data = InteractionCreate(
            from_problem_id=problem_id,
            to_problem_id=problem_id,
            author_id=data.author_id,
            exact_text=data.exact_text,
            kind=InteractionKind.NOTE,
            source_perspective_id=data.perspective_id,
            target_perspective_id=data.perspective_id,
            affected_perspectives=data.affected_perspectives,
            preserves=["exact authored occurrence", "problem reality", "source reversibility"],
            transforms=["the problem field gains one loop step"],
            omits=[],
            visibility=data.visibility,
            metadata={**data.metadata, "note_is_loop_step": True},
        )
        interaction = await self.create_interaction(interaction_data)
        note = self.store.create_problem_note(problem_id, interaction["id"])
        self.event_store.append_event(
            "LIVING_PROBLEM_NOTE_ADDED",
            "problem_note",
            note["id"],
            {
                "problem_id": problem_id,
                "interaction_id": interaction["id"],
                "occurrence_id": interaction["occurrence_id"],
            },
        )
        return {**note, "interaction": interaction, "problem": problem}

    async def create_interaction(self, data: InteractionCreate) -> dict[str, Any]:
        target_problem_id = data.to_problem_id or data.from_problem_id
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=data.exact_text,
                source_id=f"living-participant:{data.author_id}",
                source_context=(
                    f"{data.kind} interaction: {data.from_problem_id} -> {target_problem_id}"
                ),
                metadata={
                    **data.metadata,
                    "living_form": "INTERACTION",
                    "interaction_kind": str(data.kind),
                    "from_problem_id": data.from_problem_id,
                    "to_problem_id": target_problem_id,
                    "author_id": data.author_id,
                    "source_perspective_id": data.source_perspective_id,
                    "target_perspective_id": data.target_perspective_id,
                    "affected_perspectives": data.affected_perspectives,
                    "preserves": data.preserves,
                    "transforms": data.transforms,
                    "omits": data.omits,
                    "solution_is_interaction": True,
                },
            )
        )
        interaction = self.store.create_interaction(data, occurrence["id"])
        problem = self.store.get_problem(data.from_problem_id)
        if problem["current_state"] == ProblemState.OPEN:
            self.store.transition_problem(
                data.from_problem_id,
                ProblemState.ACTIVE,
                "Interaction has begun transforming the problem's solution space",
                data.author_id,
            )
        self.event_store.append_event(
            "LIVING_INTERACTION_CREATED",
            "interaction",
            interaction["id"],
            {
                "occurrence_id": occurrence["id"],
                "from_problem_id": data.from_problem_id,
                "to_problem_id": target_problem_id,
                "solution_receipt_id": interaction["solution_receipt_id"],
                "kind": str(data.kind),
            },
        )
        self.event_store.append_event(
            "LIVING_SOLUTION_CONSTITUTED",
            "solution_receipt",
            interaction["solution_receipt_id"],
            {
                "interaction_id": interaction["id"],
                "problem_id": data.from_problem_id,
                "target_problem_id": target_problem_id,
                "verdict": str(Verdict.OPEN),
            },
        )
        return interaction

    async def create_action(self, data: CollectiveActionCreate) -> dict[str, Any]:
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=data.exact_intent,
                source_id=f"living-participant:{data.created_by}",
                source_context=f"Collective action: {data.title}",
                metadata={
                    **data.metadata,
                    "living_form": "COLLECTIVE_ACTION",
                    "problem_id": data.problem_id,
                    "title": data.title,
                    "created_by": data.created_by,
                    "participant_ids": data.participant_ids,
                    "affected_perspectives": data.affected_perspectives,
                    "open_assumptions": data.open_assumptions,
                    "collective_action_not_scalar_rank": True,
                },
            )
        )
        action = self.store.create_action(data, occurrence["id"])
        problem = self.store.get_problem(data.problem_id)
        if problem["current_state"] == ProblemState.OPEN:
            self.store.transition_problem(
                data.problem_id,
                ProblemState.ACTIVE,
                "A collective action has been proposed from the problem field",
                data.created_by,
            )
        self.event_store.append_event(
            "LIVING_COLLECTIVE_ACTION_CREATED",
            "collective_action",
            action["id"],
            {
                "problem_id": action["problem_id"],
                "occurrence_id": occurrence["id"],
                "participants": action["participant_ids"],
                "affected_perspectives": action["affected_perspectives"],
            },
        )
        return action

    def transition_action(self, action_id: str, data: ActionStateChange) -> dict[str, Any]:
        action = self.store.transition_action(action_id, data.state, data.reason, data.actor_id)
        self.event_store.append_event(
            "LIVING_ACTION_STATE_CHANGED",
            "collective_action",
            action_id,
            {"state": str(data.state), "reason": data.reason, "actor_id": data.actor_id},
        )
        return action

    async def add_action_return(
        self, action_id: str, data: ActionReturnCreate
    ) -> dict[str, Any]:
        action = self.store.get_action(action_id)
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=data.exact_text,
                source_id=f"living-participant:{data.authored_by}",
                source_location=data.source_location,
                source_context=f"Returned consequence of collective action: {action['title']}",
                evidence_status=data.evidence_status,
                metadata={
                    **data.metadata,
                    "living_form": "ACTION_RETURN",
                    "action_id": action_id,
                    "problem_id": action["problem_id"],
                    "authored_by": data.authored_by,
                    "affected_perspectives": data.affected_perspectives,
                    "return_is_not_terminal": True,
                },
            )
        )
        returned = self.store.create_action_return(
            action_id,
            occurrence["id"],
            data.authored_by,
            str(data.evidence_status),
            data.affected_perspectives,
            data.metadata,
        )
        self.store.transition_action(
            action_id,
            ActionState.RETURNED,
            "A consequence has returned and must be reintegrated rather than treated as terminal",
            data.authored_by,
        )
        self.store.transition_problem(
            action["problem_id"],
            ProblemState.RETURNED,
            "Collective action returned a consequence to the real problem",
            data.authored_by,
        )
        self.event_store.append_event(
            "LIVING_ACTION_RETURNED",
            "action_return",
            returned["id"],
            {
                "action_id": action_id,
                "problem_id": action["problem_id"],
                "occurrence_id": occurrence["id"],
                "affected_perspectives": data.affected_perspectives,
            },
        )
        return returned

    def reintegrate(self) -> int:
        created = 0
        for returned in self.store.list_action_returns(limit=100_000):
            if self.store.reintegration_exists_for_return(returned["id"]):
                continue
            action = self.store.get_action(returned["action_id"])
            problem = self.store.get_problem(action["problem_id"])
            source_occurrence_id = returned["occurrence_id"]
            target_occurrence_id = problem["occurrence_id"]
            candidate, _was_created = self.event_store.create_candidate_relation(
                source_occurrence_id,
                target_occurrence_id,
                str(RelationType.MORAL_CONSEQUENCE),
                0.86,
                (
                    "A returned consequence is reintegrated with the real problem that generated "
                    "the collective action; relation remains OPEN until interpreted and admitted"
                ),
                proposed_by=self.agent_name,
            )
            action_affected = set(action["affected_perspectives"])
            return_affected = set(returned["affected_perspectives"])
            affected = sorted(action_affected | return_affected)
            missing = sorted(action_affected - return_affected)
            open_questions = [
                "Does the returned consequence settle any discretion, or does it reopen the problem in a new form?",
                "Which interpretations of the return should be admitted by participants rather than autonomously asserted?",
            ]
            if missing:
                open_questions.append(
                    "Returned consequence omitted previously affected perspectives: " + ", ".join(missing)
                )
            if not affected:
                open_questions.append(
                    "No affected perspective was named; moral completeness cannot be claimed"
                )
            proposal = self.store.create_reintegration_proposal(
                problem_id=problem["id"],
                action_id=action["id"],
                return_id=returned["id"],
                source_occurrence_id=source_occurrence_id,
                target_occurrence_id=target_occurrence_id,
                candidate_relation_id=candidate["id"],
                proposal_text=(
                    f"Reintegrate the returned consequence of '{action['title']}' into "
                    f"the living problem '{problem['title']}' without erasing either source"
                ),
                preserved=[
                    "exact problem occurrence",
                    "exact returned consequence",
                    "action intent",
                    "authorship",
                    "source-reversible relation",
                ],
                changed=[
                    "the problem field now contains the consequences of collective action",
                    "future interpretation and action may be conditioned by the return",
                ],
                open_questions=open_questions,
                affected_perspectives=affected,
                generated_by=self.agent_name,
            )
            self.store.transition_problem(
                problem["id"],
                ProblemState.REOPENED,
                "Agentic reintegration returned action consequences as new problem potential",
                returned["authored_by"],
            )
            self.store.transition_action(
                action["id"],
                ActionState.REOPENED,
                "The returned consequence has re-entered the living field",
                returned["authored_by"],
            )
            if missing or not affected:
                reason = (
                    "Returned consequence cannot claim collective completion because affected "
                    "perspectives are missing or unnamed"
                )
                self.event_store.create_open_seam(
                    source_occurrence_id,
                    target_occurrence_id,
                    reason,
                    metadata={
                        "living_reintegration_id": proposal["id"],
                        "missing_perspectives": missing,
                        "affected_perspectives": affected,
                    },
                )
            self.event_store.append_event(
                "LIVING_REINTEGRATION_PROPOSED",
                "reintegration_proposal",
                proposal["id"],
                {
                    "problem_id": problem["id"],
                    "action_id": action["id"],
                    "return_id": returned["id"],
                    "candidate_relation_id": candidate["id"],
                    "status": str(ReintegrationStatus.OPEN),
                },
            )
            created += 1
        return created

    def decide_reintegration(
        self, proposal_id: str, data: ReintegrationDecisionCreate
    ) -> dict[str, Any]:
        proposal = self.store.decide_reintegration(
            proposal_id, data.status, data.reason, data.author_id
        )
        self.event_store.append_event(
            "LIVING_REINTEGRATION_DECIDED",
            "reintegration_proposal",
            proposal_id,
            {
                "status": str(data.status),
                "reason": data.reason,
                "author_id": data.author_id,
                "candidate_relation_id": proposal["candidate_relation_id"],
            },
        )
        return proposal

    def apply_reintegration_decisions(self) -> int:
        interpretations = self.event_store.list_interpretations(limit=100_000)
        by_candidate: dict[str, list[dict[str, Any]]] = {}
        for interpretation in interpretations:
            by_candidate.setdefault(interpretation["candidate_relation_id"], []).append(interpretation)
        created = 0
        for proposal in self.store.list_reintegration_proposals(limit=100_000):
            status = ReintegrationStatus(proposal["current_status"])
            if status == ReintegrationStatus.OPEN:
                continue
            verdict = Verdict.TRUE if status == ReintegrationStatus.AUTHOR_CONFIRMED else Verdict.FALSE
            for interpretation in by_candidate.get(proposal["candidate_relation_id"], []):
                rule_version = f"living-reintegration:{proposal['id']}:{status}"
                _admission, was_created = self.event_store.create_admission(
                    interpretation["id"],
                    verdict,
                    {
                        "AUTHOR_DECISION": True,
                        "SOURCE_REVERSIBLE": True,
                        "AFFECTED_PERSPECTIVES_RETAINED": bool(
                            proposal["affected_perspectives"]
                        ),
                        "REOPENING_AVAILABLE": True,
                    },
                    proposal["current_reason"] or "Living-network reintegration decision",
                    rule_version,
                    f"living-participant:{proposal['id']}",
                )
                created += int(was_created)
        return created

    def problem_view(self, problem_id: str, black_mirror: dict[str, Any]) -> dict[str, Any]:
        problem = self.store.get_problem(problem_id)
        interactions = self.store.list_interactions(problem_id=problem_id)
        actions = [
            item for item in self.store.list_actions(limit=100_000) if item["problem_id"] == problem_id
        ]
        action_ids = {item["id"] for item in actions}
        returns = [
            item
            for item in self.store.list_action_returns(limit=100_000)
            if item["action_id"] in action_ids
        ]
        reintegration = [
            item
            for item in self.store.list_reintegration_proposals(limit=100_000)
            if item["problem_id"] == problem_id
        ]
        source_ids = [problem["occurrence_id"]]
        source_ids.extend(item["occurrence_id"] for item in interactions)
        source_ids.extend(item["occurrence_id"] for item in actions)
        source_ids.extend(item["occurrence_id"] for item in returns)
        return {
            "problem": problem,
            "interactions": interactions,
            "solutions": [
                self.store.get_solution_receipt_by_interaction(item["id"])
                for item in interactions
            ],
            "actions": actions,
            "returns": returns,
            "reintegration": reintegration,
            "black_mirror": black_mirror,
            "source_occurrence_ids": sorted(set(source_ids)),
            "nonterminal": True,
        }

    def field_projection(self, black_mirror: dict[str, Any]) -> dict[str, Any]:
        participants = self.store.list_participants(limit=100_000)
        perspectives = self.store.list_perspectives(limit=100_000)
        problems = self.store.list_problems(limit=100_000)
        interactions = self.store.list_interactions(limit=100_000)
        actions = self.store.list_actions(limit=100_000)
        returns = self.store.list_action_returns(limit=100_000)
        reintegration = self.store.list_reintegration_proposals(limit=100_000)
        reverse: dict[str, list[str]] = {}
        for problem in problems:
            reverse[f"problem:{problem['id']}"] = [problem["occurrence_id"]]
        for interaction in interactions:
            reverse[f"interaction:{interaction['id']}"] = [interaction["occurrence_id"]]
        for action in actions:
            reverse[f"action:{action['id']}"] = [action["occurrence_id"]]
        for returned in returns:
            reverse[f"return:{returned['id']}"] = [returned["occurrence_id"]]
        stats = self.store.stats()
        stats.update(
            {
                "open_reintegration": sum(
                    1
                    for item in reintegration
                    if item["current_status"] == ReintegrationStatus.OPEN
                ),
                "locally_settled_problems": sum(
                    1 for item in problems if item["current_state"] == ProblemState.LOCALLY_SETTLED
                ),
                "quantity_quality_rankings": 0,
                "nonterminal": True,
                "turing_complete_assumed": False,
            }
        )
        return {
            "generated_at": utcnow(),
            "participants": participants,
            "perspectives": perspectives,
            "problems": problems,
            "interactions": interactions,
            "actions": actions,
            "returns": returns,
            "reintegration": reintegration,
            "black_mirror": black_mirror,
            "stats": stats,
            "source_reverse_index": reverse,
        }
