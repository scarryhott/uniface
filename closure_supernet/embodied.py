from __future__ import annotations

import json
import uuid
from typing import Any, TYPE_CHECKING

from .embodied_models import (
    ALL_SHEAVES,
    GLOBAL_HAIR_SHEAVES,
    LOCAL_BALL_SHEAVES,
    EmbodiedFieldCreate,
    EmbodiedFieldEvaluation,
    EmbodiedFieldProjection,
    EmbodiedLoopSensorCreate,
    EmbodiedLoopSensorEvaluation,
    EmbodiedRelationCreate,
    EmbodiedRelationEvaluation,
    EmbodiedSectionCreate,
    SheafKind,
)
from .embodied_store import EmbodiedStore, utcnow
from .models import EvidenceStatus, Verdict
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


class EmbodiedSupernetManager:
    """One embodied eight-sheaf lens over the canonical Supernet integrator.

    "Memetic love" is represented operationally as a non-scalar conjunction of
    source preservation, reciprocal translation, consent, affected-perspective
    inclusion, retained residue, and reopening. It is not a physical force,
    emotion classifier, or score of human worth.
    """

    def __init__(self, runtime: "ClosureSupernetRuntime", store: EmbodiedStore):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "canonical_runtime_operation": "integrate",
            "adapter_label": "embodied",
            "eight_sheaf_supernet": True,
            "sheaves": [item.value for item in ALL_SHEAVES],
            "local_ball_sheaves": [item.value for item in LOCAL_BALL_SHEAVES],
            "global_hair_sheaves": [item.value for item in GLOBAL_HAIR_SHEAVES],
            "local_ball_is_embodied_human_interaction": True,
            "global_hair_is_open_potential": True,
            "memetic_love_is_reciprocal_translation": True,
            "syntropic_attractor_is_non_scalar": True,
            "resource_metrics_are_downstream": True,
            "unknown_hypotheses_remain_open": True,
            "physical_force_claimed": False,
            "emotion_inferred": False,
            "human_worth_scored": False,
            "single_sensor_complete": False,
            "runtime_is_formal_proof": False,
            "determination_issues_truth": False,
        }

    async def create_section(self, data: EmbodiedSectionCreate) -> dict[str, Any]:
        section_id = str(uuid.uuid4())
        metadata = dict(data.metadata)
        if data.sheaf == SheafKind.UNKNOWN_UAP_HYPOTHESIS:
            metadata.update(
                {
                    "hypothesis_status": "OPEN",
                    "alien_claim_verified": False,
                    "anomaly_is_not_explanation": True,
                    "truth_issued": False,
                }
            )
        exact_text = json.dumps(
            {
                "embodied_eight_sheaf": data.sheaf.value,
                "name": data.name,
                "exact_text": data.exact_text,
                "participants": data.participants,
                "perspective_ids": data.perspective_ids,
                "consent_scope": data.consent_scope,
                "hypothesis_status": metadata.get("hypothesis_status"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label=f"embodied sheaf section: {data.sheaf.value}",
                language_label="eight-sheaf translational chart",
                source_id="embodied-supernet",
                problem_id=data.problem_id,
                perspective_id=data.perspective_ids[0] if data.perspective_ids else None,
                capabilities=[
                    *data.capabilities,
                    "source-preserving sheaf participation",
                    "return into one Supernet field",
                ],
                constraints=[
                    *data.constraints,
                    "no hidden emotion inference",
                    "no human-worth score",
                    "unknown hypotheses remain OPEN",
                ],
                relation_hints=[
                    "eight sheaf",
                    data.sheaf.value,
                    "local ball" if data.sheaf in LOCAL_BALL_SHEAVES else "global hair",
                ],
                affected_perspectives=data.perspective_ids,
                evidence_status=data.evidence_status,
                adapter_label="embodied",
                external_key=data.external_key or f"embodied:section:{section_id}",
                metadata={
                    **metadata,
                    "embodied_section_id": section_id,
                    "sheaf": data.sheaf.value,
                    "participants": data.participants,
                    "consent_scope": data.consent_scope,
                    "source_ids": data.source_ids,
                    "physical_force_claimed": False,
                    "emotion_inferred": False,
                    "human_worth_scored": False,
                    "truth_issued": False,
                },
            )
        )
        row = {
            "id": section_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "sheaf": data.sheaf.value,
            "payload": {
                "exact_text": data.exact_text,
                "participants": data.participants,
                "perspective_ids": data.perspective_ids,
                "problem_id": data.problem_id,
                "consent_scope": data.consent_scope,
                "capabilities": data.capabilities,
                "constraints": data.constraints,
                "evidence_status": str(data.evidence_status),
            },
            "source_ids": data.source_ids,
            "metadata": {
                **metadata,
                "physical_force_claimed": False,
                "emotion_inferred": False,
                "human_worth_scored": False,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        stored = self.store.create_section(row)
        self.runtime.supernet_integrator.transition(
            receipt["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RELATION_SENSED,
                verdict=Verdict.OPEN,
                reason="The exact sheaf section entered the embodied field and remains available for explicit translation",
                actor_id=data.authored_by,
                successor_potential=[
                    {
                        "form_type": "embodied-sheaf-section",
                        "section_id": section_id,
                        "sheaf": data.sheaf.value,
                        "hypothesis_status": metadata.get("hypothesis_status"),
                    }
                ],
                metadata={
                    "eight_sheaf_supernet": True,
                    "unknown_hypotheses_remain_open": True,
                    "truth_issued": False,
                },
            ),
        )
        self.projection()
        return self.store.get_section(stored["id"])

    @staticmethod
    def evaluate_relation(
        data: EmbodiedRelationCreate,
        left: dict[str, Any],
        right: dict[str, Any],
    ) -> EmbodiedRelationEvaluation:
        expected_perspectives = set(left.get("perspective_ids", [])) | set(
            right.get("perspective_ids", [])
        )
        expected_participants = set(left.get("participants", [])) | set(
            right.get("participants", [])
        )
        preserve_set = set(data.preserves)
        source_preserved = {
            data.left_section_id,
            data.right_section_id,
        }.issubset(preserve_set)
        reciprocal = bool(data.forward_translation) and bool(data.reverse_translation)
        perspectives_included = expected_perspectives.issubset(
            set(data.affected_perspectives)
        )
        consent_scoped = not expected_participants or expected_participants.issubset(
            set(data.consented_participant_ids)
        )
        reopenable = bool(data.reopening_conditions)
        residue_retained = bool(data.untranslated_residue) or bool(
            data.metadata.get("no_untranslated_residue") is True
        )
        unknown_sections = [
            section
            for section in (left, right)
            if section["sheaf"] == SheafKind.UNKNOWN_UAP_HYPOTHESIS.value
        ]
        unknown_open = all(
            section.get("metadata", {}).get("hypothesis_status") == "OPEN"
            and section.get("metadata", {}).get("alien_claim_verified") is False
            for section in unknown_sections
        )
        love_admissible = all(
            (
                source_preserved,
                reciprocal,
                perspectives_included,
                consent_scoped,
                reopenable,
                residue_retained,
                unknown_open,
            )
        )
        return EmbodiedRelationEvaluation(
            source_preserved=source_preserved,
            reciprocal_return=reciprocal,
            affected_perspectives_included=perspectives_included,
            consent_scoped=consent_scoped,
            reopenable=reopenable,
            residue_retained=residue_retained,
            unknown_hypotheses_open=unknown_open,
            love_admissible=love_admissible,
        )

    async def create_relation(self, data: EmbodiedRelationCreate) -> dict[str, Any]:
        left = self.store.get_section(data.left_section_id)
        right = self.store.get_section(data.right_section_id)
        relation_id = str(uuid.uuid4())
        evaluation = self.evaluate_relation(data, left, right)
        exact_text = json.dumps(
            {
                "embodied_relation": data.name,
                "left": data.left_section_id,
                "right": data.right_section_id,
                "forward": data.forward_translation,
                "reverse": data.reverse_translation,
                "preserves": data.preserves,
                "transforms": data.transforms,
                "untranslated_residue": data.untranslated_residue,
                "evaluation": evaluation.model_dump(mode="json"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        affected = list(
            dict.fromkeys(
                [
                    *left.get("perspective_ids", []),
                    *right.get("perspective_ids", []),
                    *data.affected_perspectives,
                ]
            )
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="embodied reciprocal translation",
                language_label="memetic-love closure profile",
                source_id="embodied-supernet",
                problem_id=left.get("problem_id") or right.get("problem_id"),
                perspective_id=affected[0] if affected else None,
                capabilities=[
                    "forward and reverse translation",
                    "source-preserving reciprocal return",
                    "reopening",
                ],
                constraints=[
                    "memetic love is not a physical force",
                    "no emotion inference",
                    "resource metrics are downstream",
                ],
                relation_hints=[
                    "ball hair equivalence",
                    "reciprocal translation",
                    "memetic love",
                ],
                parent_event_ids=[
                    left["integration_event_id"],
                    right["integration_event_id"],
                ],
                affected_perspectives=affected,
                evidence_status=EvidenceStatus.INTERPRETED_RELATION,
                adapter_label="embodied",
                external_key=data.external_key or f"embodied:relation:{relation_id}",
                metadata={
                    **data.metadata,
                    "embodied_relation_id": relation_id,
                    "evaluation": evaluation.model_dump(mode="json"),
                    "source_ids": data.source_ids,
                    "physical_force_claimed": False,
                    "emotion_inferred": False,
                    "human_worth_scored": False,
                    "truth_issued": False,
                },
            )
        )
        row = {
            "id": relation_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "left_section_id": data.left_section_id,
            "right_section_id": data.right_section_id,
            "payload": {
                "forward_translation": data.forward_translation,
                "reverse_translation": data.reverse_translation,
                "preserves": data.preserves,
                "transforms": data.transforms,
                "untranslated_residue": data.untranslated_residue,
                "affected_perspectives": data.affected_perspectives,
                "consented_participant_ids": data.consented_participant_ids,
                "reopening_conditions": data.reopening_conditions,
            },
            "evaluation": evaluation.model_dump(mode="json"),
            "source_ids": data.source_ids,
            "metadata": {
                **data.metadata,
                "physical_force_claimed": False,
                "emotion_inferred": False,
                "human_worth_scored": False,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        stored = self.store.create_relation(row)
        if evaluation.love_admissible:
            self.runtime.supernet_integrator.determine(
                receipt["event_id"],
                actor_id=data.authored_by,
                rigidity_scope=["reciprocal-translation", relation_id],
                rigidity_receipt={
                    "source_preserved": True,
                    "reciprocal_return": True,
                    "affected_perspectives_included": True,
                    "consent_scoped": True,
                    "reopenable": True,
                    "residue_retained": True,
                    "unknown_hypotheses_open": True,
                },
                determined_form={
                    "relation_id": relation_id,
                    "left_section_id": data.left_section_id,
                    "right_section_id": data.right_section_id,
                    "love_admissible": True,
                    "canonical_presentation": None,
                },
                unitary_path_partition={
                    "path": [
                        data.left_section_id,
                        "forward translation",
                        data.right_section_id,
                        "reverse return",
                        data.left_section_id,
                    ],
                    "partition": {
                        "preserved": data.preserves,
                        "transformed": data.transforms,
                        "open_residue": data.untranslated_residue,
                    },
                },
                reason="The explicit reciprocal relation preserves sources, perspectives, consent, residue, and reopening",
            )
            self.runtime.supernet_integrator.transition(
                receipt["event_id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RETURNED,
                    verdict=Verdict.OPEN,
                    reason="The reciprocal relation returned without becoming a force, score, or truth verdict",
                    actor_id=data.authored_by,
                    returned_resource_ids=[relation_id],
                    successor_potential=[
                        {
                            "form_type": "embodied-reciprocal-relation",
                            "relation_id": relation_id,
                            "reopening_conditions": data.reopening_conditions,
                        }
                    ],
                    metadata={
                        "memetic_love_is_reciprocal_translation": True,
                        "physical_force_claimed": False,
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
                    reason="The relation remains OPEN because one or more reciprocal-admissibility witnesses are missing",
                    actor_id=data.authored_by,
                    successor_potential=[
                        {
                            "form_type": "open-embodied-relation",
                            "relation_id": relation_id,
                            "evaluation": evaluation.model_dump(mode="json"),
                        }
                    ],
                    metadata={
                        "memetic_love_is_reciprocal_translation": True,
                        "truth_issued": False,
                    },
                ),
            )
        self.projection()
        return self.store.get_relation(stored["id"])

    @staticmethod
    def _components(
        section_ids: list[str], relations: list[dict[str, Any]]
    ) -> list[list[str]]:
        adjacency = {section_id: set() for section_id in section_ids}
        for relation in relations:
            if not relation["evaluation"]["love_admissible"]:
                continue
            left = relation["left_section_id"]
            right = relation["right_section_id"]
            adjacency[left].add(right)
            adjacency[right].add(left)
        remaining = set(section_ids)
        components: list[list[str]] = []
        while remaining:
            seed = next(item for item in section_ids if item in remaining)
            stack = [seed]
            component: list[str] = []
            while stack:
                current = stack.pop()
                if current not in remaining:
                    continue
                remaining.remove(current)
                component.append(current)
                stack.extend(sorted(adjacency[current], reverse=True))
            components.append([item for item in section_ids if item in component])
        return components

    @classmethod
    def evaluate_field(
        cls,
        sections: list[dict[str, Any]],
        relations: list[dict[str, Any]],
    ) -> EmbodiedFieldEvaluation:
        coverage: dict[str, list[str]] = {item.value: [] for item in ALL_SHEAVES}
        by_id = {section["id"]: section for section in sections}
        for section in sections:
            coverage[section["sheaf"]].append(section["id"])
        missing = [item for item in ALL_SHEAVES if not coverage[item.value]]
        local_ball = [
            section["id"]
            for section in sections
            if section["sheaf"] in {item.value for item in LOCAL_BALL_SHEAVES}
        ]
        global_hair = [
            section["id"]
            for section in sections
            if section["sheaf"] in {item.value for item in GLOBAL_HAIR_SHEAVES}
        ]
        local_complete = all(coverage[item.value] for item in LOCAL_BALL_SHEAVES)
        global_complete = all(coverage[item.value] for item in GLOBAL_HAIR_SHEAVES)
        all_eight = local_complete and global_complete
        components = cls._components([section["id"] for section in sections], relations)
        relation_by_component: dict[int, list[dict[str, Any]]] = {}
        profiles: dict[str, list[str]] = {}
        local_values = {item.value for item in LOCAL_BALL_SHEAVES}
        global_values = {item.value for item in GLOBAL_HAIR_SHEAVES}
        for component_id, component in enumerate(components):
            component_set = set(component)
            component_relations = [
                relation
                for relation in relations
                if relation["left_section_id"] in component_set
                and relation["right_section_id"] in component_set
            ]
            relation_by_component[component_id] = component_relations
            properties = {"source_reverse_indexed", "resource_metrics_downstream"}
            if component_relations and all(
                relation["evaluation"]["source_preserved"]
                for relation in component_relations
            ):
                properties.add("source_preserving")
            if component_relations and all(
                relation["evaluation"]["reciprocal_return"]
                for relation in component_relations
            ):
                properties.add("reciprocal_return")
            if component_relations and all(
                relation["evaluation"]["affected_perspectives_included"]
                for relation in component_relations
            ):
                properties.add("affected_perspectives_included")
            if component_relations and all(
                relation["evaluation"]["consent_scoped"]
                for relation in component_relations
            ):
                properties.add("consent_scoped")
            if component_relations and all(
                relation["evaluation"]["reopenable"]
                for relation in component_relations
            ):
                properties.add("reopenable")
            if component_relations and all(
                relation["evaluation"]["residue_retained"]
                for relation in component_relations
            ):
                properties.add("residue_retained")
            component_sheaves = {by_id[item]["sheaf"] for item in component}
            if local_values.issubset(component_sheaves):
                properties.add("local_ball_complete")
            if global_values.issubset(component_sheaves):
                properties.add("global_hair_complete")
            if {item.value for item in ALL_SHEAVES}.issubset(component_sheaves):
                properties.add("all_eight_sheaves")
            cross_relation = any(
                (
                    by_id[relation["left_section_id"]]["sheaf"] in local_values
                    and by_id[relation["right_section_id"]]["sheaf"] in global_values
                )
                or (
                    by_id[relation["right_section_id"]]["sheaf"] in local_values
                    and by_id[relation["left_section_id"]]["sheaf"] in global_values
                )
                for relation in component_relations
                if relation["evaluation"]["love_admissible"]
            )
            if cross_relation:
                properties.add("ball_hair_connected")
            unknowns = [
                by_id[item]
                for item in component
                if by_id[item]["sheaf"] == SheafKind.UNKNOWN_UAP_HYPOTHESIS.value
            ]
            if all(
                section.get("metadata", {}).get("hypothesis_status") == "OPEN"
                for section in unknowns
            ):
                properties.add("unknown_hypotheses_open")
            profiles[str(component_id)] = sorted(properties)

        profile_sets = {
            component_id: set(properties)
            for component_id, properties in profiles.items()
        }
        maximal: list[int] = []
        for component_id, properties in profile_sets.items():
            dominated = any(
                properties < other_properties
                for other_id, other_properties in profile_sets.items()
                if other_id != component_id
            )
            if not dominated:
                maximal.append(int(component_id))
        unique = (
            len(maximal) == 1
            and "all_eight_sheaves" in profile_sets[str(maximal[0])]
            and "ball_hair_connected" in profile_sets[str(maximal[0])]
            and "reciprocal_return" in profile_sets[str(maximal[0])]
            and "consent_scoped" in profile_sets[str(maximal[0])]
            and "reopenable" in profile_sets[str(maximal[0])]
        )
        selected_id = maximal[0] if unique else None
        selected = components[selected_id] if selected_id is not None else None
        field_connected = len(components) == 1
        ball_hair_connected = any(
            "ball_hair_connected" in set(properties)
            for properties in profiles.values()
        )
        unknown_open = all(
            section.get("metadata", {}).get("hypothesis_status") == "OPEN"
            for section in sections
            if section["sheaf"] == SheafKind.UNKNOWN_UAP_HYPOTHESIS.value
        )
        return EmbodiedFieldEvaluation(
            sheaf_coverage=coverage,
            missing_sheaves=missing,
            local_ball_section_ids=local_ball,
            global_hair_section_ids=global_hair,
            local_ball_complete=local_complete,
            global_hair_complete=global_complete,
            all_eight_sheaves_present=all_eight,
            reciprocal_components=components,
            component_profiles=profiles,
            maximal_component_ids=maximal,
            unique_natural_component=unique,
            selected_component_id=selected_id,
            selected_component=selected,
            field_connected=field_connected,
            ball_hair_connected=ball_hair_connected,
            unknown_hypotheses_open=unknown_open,
        )

    async def create_field(self, data: EmbodiedFieldCreate) -> dict[str, Any]:
        sections = [self.store.get_section(item_id) for item_id in data.section_ids]
        section_set = set(data.section_ids)
        relations = [self.store.get_relation(item_id) for item_id in data.relation_ids]
        if any(
            relation["left_section_id"] not in section_set
            or relation["right_section_id"] not in section_set
            for relation in relations
        ):
            raise ValueError("every relation endpoint must be included in section_ids")
        field_id = str(uuid.uuid4())
        evaluation = self.evaluate_field(sections, relations)
        exact_text = json.dumps(
            {
                "embodied_eight_sheaf_field": data.name,
                "section_ids": data.section_ids,
                "relation_ids": data.relation_ids,
                "local_ball": evaluation.local_ball_section_ids,
                "global_hair": evaluation.global_hair_section_ids,
                "evaluation": evaluation.model_dump(mode="json"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        parent_events = [
            *[section["integration_event_id"] for section in sections],
            *[relation["integration_event_id"] for relation in relations],
        ]
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="embodied eight-sheaf Supernet field",
                language_label="local ball / global hair relational chart",
                source_id="embodied-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "eight-sheaf gluing",
                    "local embodied ball",
                    "globally open hair",
                    "non-scalar natural component",
                ],
                constraints=[
                    "resource metrics remain downstream",
                    "unknown hypotheses remain OPEN",
                    "no physical-force claim",
                    "no emotion or human-worth scoring",
                ],
                relation_hints=[
                    "eight sheaf tensor",
                    "ball hair equivalence",
                    "syntropic attractor",
                    "human interaction network",
                ],
                parent_event_ids=list(dict.fromkeys(parent_events)),
                affected_perspectives=[
                    item
                    for section in sections
                    for item in section.get("perspective_ids", [])
                ],
                evidence_status=EvidenceStatus.INTERPRETED_RELATION,
                adapter_label="embodied",
                external_key=data.external_key or f"embodied:field:{field_id}",
                metadata={
                    **data.metadata,
                    "embodied_field_id": field_id,
                    "evaluation": evaluation.model_dump(mode="json"),
                    "implementation_metrics": data.implementation_metrics,
                    "resource_metrics_are_downstream": True,
                    "syntropic_attractor_is_non_scalar": True,
                    "truth_issued": False,
                },
            )
        )
        row = {
            "id": field_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "payload": {
                "section_ids": data.section_ids,
                "relation_ids": data.relation_ids,
                "perspective_id": data.perspective_id,
                "problem_id": data.problem_id,
                "implementation_metrics": data.implementation_metrics,
            },
            "evaluation": evaluation.model_dump(mode="json"),
            "source_ids": data.source_ids,
            "metadata": {
                **data.metadata,
                "resource_metrics_are_downstream": True,
                "physical_force_claimed": False,
                "emotion_inferred": False,
                "human_worth_scored": False,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        stored = self.store.create_field(row)
        if evaluation.unique_natural_component:
            self.runtime.supernet_integrator.determine(
                receipt["event_id"],
                actor_id=data.authored_by,
                rigidity_scope=["eight-sheaf-natural-component", field_id],
                rigidity_receipt={
                    "all_eight_sheaves_present": True,
                    "ball_hair_connected": True,
                    "reciprocal_return": True,
                    "consent_scoped": True,
                    "reopenable": True,
                    "resource_metric_used_as_foundation": False,
                },
                determined_form={
                    "field_id": field_id,
                    "selected_component_id": evaluation.selected_component_id,
                    "selected_component": evaluation.selected_component,
                    "local_ball": evaluation.local_ball_section_ids,
                    "global_hair": evaluation.global_hair_section_ids,
                    "canonical_presentation": None,
                },
                unitary_path_partition={
                    "path": [
                        "point occurrence",
                        "line translation",
                        "reciprocal loop",
                        "local ball return",
                        "global hair reopening",
                    ],
                    "partition": {
                        "local_ball": evaluation.local_ball_section_ids,
                        "global_hair": evaluation.global_hair_section_ids,
                        "components": evaluation.reciprocal_components,
                    },
                },
                reason="One non-dominated reciprocal component carries all eight sheaves and connects the embodied ball to open global hair",
            )
            self.runtime.supernet_integrator.transition(
                receipt["event_id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RETURNED,
                    verdict=Verdict.OPEN,
                    reason="The embodied ball returned as one current-field form while the global hair remains open",
                    actor_id=data.authored_by,
                    returned_resource_ids=[field_id],
                    successor_potential=[
                        {
                            "form_type": "embodied-eight-sheaf-field",
                            "field_id": field_id,
                            "local_ball": evaluation.local_ball_section_ids,
                            "global_hair": evaluation.global_hair_section_ids,
                            "global_hair_open": True,
                        }
                    ],
                    metadata={
                        "eight_sheaf_supernet": True,
                        "syntropic_attractor_is_non_scalar": True,
                        "resource_metrics_are_downstream": True,
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
                    reason="The embodied field remains OPEN because the eight sheaves do not yet form one unique reciprocal component",
                    actor_id=data.authored_by,
                    successor_potential=[
                        {
                            "form_type": "open-embodied-field",
                            "field_id": field_id,
                            "missing_sheaves": [item.value for item in evaluation.missing_sheaves],
                            "maximal_component_ids": evaluation.maximal_component_ids,
                        }
                    ],
                    metadata={
                        "eight_sheaf_supernet": True,
                        "resource_metrics_are_downstream": True,
                        "truth_issued": False,
                    },
                ),
            )
        self.projection()
        return self.store.get_field(stored["id"])

    @staticmethod
    def evaluate_sensor(
        data: EmbodiedLoopSensorCreate,
        field: dict[str, Any],
    ) -> EmbodiedLoopSensorEvaluation:
        field_sections = set(field["section_ids"])
        visible = set(data.visible_section_ids)
        returned = set(data.returned_section_ids)
        sensor_in_field = data.sensor_section_id in field_sections
        visible_valid = visible.issubset(field_sections)
        returned_valid = returned.issubset(field_sections)
        local_ball = set(field["evaluation"]["local_ball_section_ids"])
        global_hair = set(field["evaluation"]["global_hair_section_ids"])
        local_read = [item for item in data.visible_section_ids if item in local_ball]
        hair_read = [item for item in data.returned_section_ids if item in global_hair]
        if not hair_read:
            hair_read = [
                item
                for item in field["evaluation"]["global_hair_section_ids"]
                if item not in visible
            ]
        coverage = visible | returned
        return EmbodiedLoopSensorEvaluation(
            sensor_in_field=sensor_in_field,
            visible_sections_valid=visible_valid,
            returned_sections_valid=returned_valid,
            local_ball_read=local_read,
            global_hair_read=hair_read,
            local_halt_reading=bool(local_read),
            global_continuation_reading=bool(global_hair),
            current_field_coverage_complete=coverage == field_sections,
        )

    async def create_sensor_read(
        self, data: EmbodiedLoopSensorCreate
    ) -> dict[str, Any]:
        field = self.store.get_field(data.field_id)
        self.store.get_section(data.sensor_section_id)
        evaluation = self.evaluate_sensor(data, field)
        if not (
            evaluation.sensor_in_field
            and evaluation.visible_sections_valid
            and evaluation.returned_sections_valid
        ):
            raise ValueError("sensor and all visible/returned sections must belong to the field")
        read_id = str(uuid.uuid4())
        exact_text = json.dumps(
            {
                "embodied_loop_sensor": data.name,
                "field_id": data.field_id,
                "sensor_section_id": data.sensor_section_id,
                "resolution": data.resolution,
                "visible": data.visible_section_ids,
                "returned": data.returned_section_ids,
                "evaluation": evaluation.model_dump(mode="json"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="embodied loop-sensor reading",
                language_label="local halt / global continuation chart",
                source_id="embodied-supernet",
                problem_id=field.get("problem_id"),
                capabilities=[
                    "background-independent relational reading",
                    "local ball return",
                    "global hair continuation",
                ],
                constraints=[
                    "single sensor is never the complete Supernet",
                    "absolute origin is not observed",
                    "unknown hypotheses receive no truth verdict",
                ],
                relation_hints=[
                    "loop sensor",
                    "ball hair",
                    "halting continuation",
                    "partial computational completion",
                ],
                parent_event_ids=[field["integration_event_id"]],
                affected_perspectives=[],
                evidence_status=EvidenceStatus.INTERPRETED_RELATION,
                adapter_label="embodied",
                external_key=data.external_key or f"embodied:sensor:{read_id}",
                metadata={
                    **data.metadata,
                    "embodied_sensor_read_id": read_id,
                    "evaluation": evaluation.model_dump(mode="json"),
                    "single_sensor_complete": False,
                    "absolute_origin_observed": False,
                    "truth_issued": False,
                },
            )
        )
        row = {
            "id": read_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "field_id": data.field_id,
            "sensor_section_id": data.sensor_section_id,
            "payload": {
                "resolution": data.resolution,
                "visible_section_ids": data.visible_section_ids,
                "returned_section_ids": data.returned_section_ids,
            },
            "evaluation": evaluation.model_dump(mode="json"),
            "source_ids": data.source_ids,
            "metadata": {
                **data.metadata,
                "single_sensor_complete": False,
                "absolute_origin_observed": False,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        stored = self.store.create_sensor_read(row)
        self.runtime.supernet_integrator.determine(
            receipt["event_id"],
            actor_id=data.authored_by,
            rigidity_scope=["sensor-reading", read_id, f"resolution:{data.resolution}"],
            rigidity_receipt={
                "sensor_in_field": True,
                "visible_sections_valid": True,
                "returned_sections_valid": True,
                "absolute_origin_observed": False,
            },
            determined_form={
                "sensor_read_id": read_id,
                "local_ball_read": evaluation.local_ball_read,
                "global_hair_read": evaluation.global_hair_read,
                "local_halt_reading": evaluation.local_halt_reading,
                "global_continuation_reading": evaluation.global_continuation_reading,
                "single_sensor_complete": False,
            },
            unitary_path_partition={
                "path": [
                    "sensor section",
                    "visible local ball",
                    "returned global hair",
                    "reintegrated successor potential",
                ],
                "partition": {
                    "visible": data.visible_section_ids,
                    "returned": data.returned_section_ids,
                    "unread": [
                        item
                        for item in field["section_ids"]
                        if item not in set(data.visible_section_ids)
                        | set(data.returned_section_ids)
                    ],
                },
            },
            reason="The loop sensor determines one relational reading without observing an absolute origin or completing the whole Supernet",
        )
        self.runtime.supernet_integrator.transition(
            receipt["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The sensor return becomes successor potential; the local halt and global continuation remain two readings of one loop",
                actor_id=data.authored_by,
                returned_resource_ids=[read_id],
                successor_potential=[
                    {
                        "form_type": "embodied-loop-sensor-return",
                        "sensor_read_id": read_id,
                        "field_id": data.field_id,
                        "global_hair_read": evaluation.global_hair_read,
                        "reintegrate": True,
                    }
                ],
                metadata={
                    "single_sensor_complete": False,
                    "global_continuation_reading": True,
                    "truth_issued": False,
                },
            ),
        )
        self.projection()
        return self.store.get_sensor_read(stored["id"])

    def projection(self) -> dict[str, Any]:
        sections = self.store.list_sections()
        relations = self.store.list_relations()
        fields = self.store.list_fields()
        reads = self.store.list_sensor_reads()
        reverse: dict[str, list[str]] = {}
        for item in [*sections, *relations, *fields, *reads]:
            event_id = item["integration_event_id"]
            for source_id in [item["occurrence_id"], *item.get("source_ids", [])]:
                reverse.setdefault(source_id, []).append(event_id)
        projection = EmbodiedFieldProjection(
            generated_at=utcnow(),
            sections=sections,
            relations=relations,
            fields=fields,
            sensor_reads=reads,
            stats=self.store.stats(),
            source_reverse_index={
                key: list(dict.fromkeys(values)) for key, values in reverse.items()
            },
        ).model_dump(mode="json")
        self.store.set_state("embodied_field_projection", projection)
        return projection
