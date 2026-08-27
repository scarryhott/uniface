from __future__ import annotations

import json
import uuid
from typing import Any, TYPE_CHECKING

from .constructive import ConstructiveClosureManager
from .framework_models import (
    FrameworkClassification,
    FrameworkFieldProjection,
    NaturalSelectionArenaCreate,
    NaturalSelectionEvaluation,
    TranslationalTruthEvaluation,
    TranslationalTruthFrameworkCreate,
    TruthSelectionBridgeCreate,
)
from .framework_store import FrameworkStore, utcnow
from .models import EvidenceStatus, Verdict
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


class TranslationalFrameworkManager:
    """One live NRRF784/785 lens over the canonical Supernet integrator."""

    def __init__(self, runtime: "ClosureSupernetRuntime", store: FrameworkStore):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_readings": ["NRRF784", "NRRF785"],
            "canonical_runtime_operation": "integrate",
            "adapter_label": "framework",
            "level_natural_selection": True,
            "selector_fixed_under_shift": True,
            "selector_factors_through_orbits": True,
            "resource_metrics_are_downstream": True,
            "translational_truth_unique_on_orbits": True,
            "classical_and_contextual_share_truth": True,
            "classical_is_total_global_section": True,
            "contextual_is_global_section_obstruction": True,
            "local_fragments_are_noncontextual": True,
            "global_assignment_required_for_truth": False,
            "classical_choice_required": False,
            "excluded_middle_required": False,
            "runtime_is_formal_proof": False,
            "determination_issues_truth": False,
        }

    @staticmethod
    def _validate_group(group: Any) -> dict[str, Any]:
        return ConstructiveClosureManager._validate_group(group)

    @staticmethod
    def _validate_action(
        group: dict[str, Any], carrier: list[str], action: dict[str, dict[str, str]]
    ) -> bool:
        elements = group["elements"]
        add = group["addition"]
        zero = group["zero"]
        carrier_set = set(carrier)
        if set(action) != set(elements):
            return False
        for level in elements:
            row = action[level]
            if set(row) != carrier_set or set(row.values()) != carrier_set:
                return False
        if any(action[zero][item] != item for item in carrier):
            return False
        for left in elements:
            for right in elements:
                composed = add[left][right]
                for item in carrier:
                    if action[composed][item] != action[left][action[right][item]]:
                        return False
        return True

    @staticmethod
    def _orbits(
        group: dict[str, Any], carrier: list[str], action: dict[str, dict[str, str]]
    ) -> tuple[list[list[str]], dict[str, int]]:
        remaining = set(carrier)
        orbits: list[list[str]] = []
        orbit_of: dict[str, int] = {}
        while remaining:
            seed = next(item for item in carrier if item in remaining)
            orbit = sorted(
                {action[level][seed] for level in group["elements"]},
                key=carrier.index,
            )
            orbit_id = len(orbits)
            orbits.append(orbit)
            for item in orbit:
                orbit_of[item] = orbit_id
                remaining.discard(item)
        return orbits, orbit_of

    @classmethod
    def evaluate_arena(cls, data: NaturalSelectionArenaCreate) -> NaturalSelectionEvaluation:
        group = cls._validate_group(data.group)
        action_valid = cls._validate_action(group, data.forms, data.action)
        if not action_valid:
            raise ValueError("submitted level action does not satisfy the group-action laws")
        orbits, orbit_of = cls._orbits(group, data.forms, data.action)
        natural = all(
            data.selected[data.action[level][form]] == data.selected[form]
            for level in group["elements"]
            for form in data.forms
        )
        orbit_verdicts: dict[str, bool | None] = {}
        selected_orbits: list[int] = []
        for orbit_id, orbit in enumerate(orbits):
            values = {data.selected[form] for form in orbit}
            verdict = next(iter(values)) if len(values) == 1 else None
            orbit_verdicts[str(orbit_id)] = verdict
            if verdict is True:
                selected_orbits.append(orbit_id)

        metric_present = data.resource_metric is not None
        metric_natural: bool | None = None
        metric_invariant: bool | None = None
        metric_selected: list[str] = []
        metric_constant: bool | None = None
        flip_witnesses: list[dict[str, Any]] = []
        if data.resource_metric is not None:
            metric = data.resource_metric
            minimum = min(metric.values())
            metric_selected = [form for form in data.forms if metric[form] == minimum]
            selected_set = set(metric_selected)
            metric_natural = all(
                (data.action[level][form] in selected_set) == (form in selected_set)
                for level in group["elements"]
                for form in data.forms
            )
            metric_invariant = all(
                metric[data.action[level][form]] == metric[form]
                for level in group["elements"]
                for form in data.forms
            )
            metric_constant = all(
                len({metric[item] for item in orbits[orbit_of[form]]}) == 1
                for form in metric_selected
            )
            for level in group["elements"]:
                shifted_selected = {data.action[level][form] for form in metric_selected}
                if shifted_selected != selected_set:
                    flip_witnesses.append(
                        {
                            "level": level,
                            "selected_before": metric_selected,
                            "selected_after": [form for form in data.forms if form in shifted_selected],
                        }
                    )

        return NaturalSelectionEvaluation(
            group_valid=True,
            action_valid=True,
            natural=natural,
            selector_fixed_under_shift=natural,
            factors_through_orbits=natural,
            orbits=orbits,
            orbit_of=orbit_of,
            orbit_verdicts=orbit_verdicts,
            selected_orbit_ids=selected_orbits,
            unique_selected_orbit=natural and len(selected_orbits) == 1,
            resource_metric_present=metric_present,
            resource_metric_selector_natural=metric_natural,
            resource_metric_level_invariant=metric_invariant,
            metric_selected_forms=metric_selected,
            metric_selected_orbit_cost_constant=metric_constant,
            metric_flip_witnesses=flip_witnesses,
        )

    async def create_arena(self, data: NaturalSelectionArenaCreate) -> dict[str, Any]:
        arena_id = str(uuid.uuid4())
        evaluation = self.evaluate_arena(data)
        exact_text = json.dumps(
            {
                "NRRF784": "conscious selective naturality",
                "name": data.name,
                "forms": data.forms,
                "group": data.group.model_dump(mode="json"),
                "action": data.action,
                "selected": data.selected,
                "resource_metric": None if data.resource_metric is None else {key: str(value) for key, value in data.resource_metric.items()},
                "natural": evaluation.natural,
                "orbits": evaluation.orbits,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="level-natural selection arena",
                language_label="NRRF784 orbit selector chart",
                source_id="framework-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=["selector fixed under level shifts", "orbit quotient factorization", "resource metric bias detection"],
                constraints=["resource metric is not foundational selection", "selected presentation is not canonical", "determination does not issue TRUE"],
                relation_hints=["NRRF784", "naturality", "level orbit", "selector"],
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="framework",
                external_key=data.external_key or f"framework:arena:{arena_id}",
                metadata={
                    **data.metadata,
                    "arena_id": arena_id,
                    "formal_reading": "NRRF784",
                    "evaluation": evaluation.model_dump(mode="json"),
                    "resource_metric_foundational_selector": False,
                    "classical_choice_required": False,
                    "truth_issued": False,
                },
            )
        )
        row = {
            "id": arena_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "perspective_id": data.perspective_id,
            "problem_id": data.problem_id,
            "payload": {
                "forms": data.forms,
                "group": data.group.model_dump(mode="json"),
                "action": data.action,
                "selected": data.selected,
                "resource_metric": None if data.resource_metric is None else {key: str(value) for key, value in data.resource_metric.items()},
            },
            "evaluation": evaluation.model_dump(mode="json"),
            "source_ids": data.source_ids,
            "metadata": {**data.metadata, "resource_metric_foundational_selector": False, "truth_issued": False},
            "created_at": utcnow(),
        }
        stored = self.store.create_arena(row)
        if evaluation.unique_selected_orbit:
            orbit_id = evaluation.selected_orbit_ids[0]
            selected_orbit = evaluation.orbits[orbit_id]
            self.runtime.supernet_integrator.determine(
                receipt["event_id"],
                actor_id=data.authored_by,
                rigidity_scope=["level-orbit", str(orbit_id)],
                rigidity_receipt={"selector_natural": True, "factors_through_orbits": True, "unique_selected_orbit": True, "resource_metric_used_as_foundation": False},
                determined_form={"selected_orbit_id": orbit_id, "selected_orbit": selected_orbit, "canonical_presentation": None},
                unitary_path_partition={"path": ["level shift", "orbit", "natural verdict"], "partition": evaluation.orbits},
                reason="A level-natural selector leaves exactly one translation orbit selected",
            )
            self.runtime.supernet_integrator.transition(
                receipt["event_id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RETURNED,
                    verdict=Verdict.OPEN,
                    reason="The selected natural orbit returned without canonizing a presentation or issuing TRUE",
                    actor_id=data.authored_by,
                    returned_resource_ids=[arena_id],
                    successor_potential=[{"form_type": "natural-selection-orbit", "arena_id": arena_id, "selected_orbit": selected_orbit, "canonical_presentation": None}],
                    metadata={"nrrf784": True, "resource_metric_foundational_selector": False, "truth_issued": False},
                ),
            )
        else:
            self.runtime.supernet_integrator.transition(
                receipt["event_id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RELATION_SENSED,
                    verdict=Verdict.OPEN,
                    reason="The selector is level-dependent or does not rigidly select one orbit; selection remains OPEN",
                    actor_id=data.authored_by,
                    successor_potential=[{"form_type": "open-natural-selection", "arena_id": arena_id, "natural": evaluation.natural, "selected_orbit_ids": evaluation.selected_orbit_ids}],
                    metadata={"nrrf784": True, "resource_metric_foundational_selector": False, "truth_issued": False},
                ),
            )
        self.projection()
        return self.store.get_arena(stored["id"])

    @classmethod
    def evaluate_framework(cls, data: TranslationalTruthFrameworkCreate) -> TranslationalTruthEvaluation:
        group = cls._validate_group(data.group)
        frame_action_valid = cls._validate_action(group, data.frames, data.frame_action)
        observable_action_valid = cls._validate_action(group, data.observables, data.observable_action)
        if not frame_action_valid or not observable_action_valid:
            raise ValueError("submitted frame/observable action is not a group action")

        invariance_failures: list[dict[str, Any]] = []
        for level in group["elements"]:
            for frame in data.frames:
                for observable in data.observables:
                    shifted_frame = data.frame_action[level][frame]
                    shifted_observable = data.observable_action[level][observable]
                    left = data.verdicts[frame][observable]
                    right = data.verdicts[shifted_frame][shifted_observable]
                    if left != right:
                        invariance_failures.append({"level": level, "frame": frame, "observable": observable, "shifted_frame": shifted_frame, "shifted_observable": shifted_observable, "verdict": left, "shifted_verdict": right})
        invariant = not invariance_failures

        presentations = [f"{frame}::{observable}" for frame in data.frames for observable in data.observables]
        presentation_action = {
            level: {
                f"{frame}::{observable}": f"{data.frame_action[level][frame]}::{data.observable_action[level][observable]}"
                for frame in data.frames
                for observable in data.observables
            }
            for level in group["elements"]
        }
        orbits, orbit_of = cls._orbits(group, presentations, presentation_action)
        orbit_truth: dict[str, str | None] = {}
        for orbit_id, orbit in enumerate(orbits):
            values = {data.verdicts[presentation.split("::", 1)[0]][presentation.split("::", 1)[1]] for presentation in orbit}
            orbit_truth[str(orbit_id)] = next(iter(values)) if len(values) == 1 else None

        frame_assignments = {
            frame: {
                observable: data.verdicts[frame][observable] if data.verdicts[frame][observable] is not None else data.default_value
                for observable in data.observables
            }
            for frame in data.frames
        }
        total = all(data.verdicts[frame][observable] is not None for frame in data.frames for observable in data.observables)
        obstructions: list[dict[str, Any]] = []
        assignment: dict[str, str] = {}
        for observable in data.observables:
            defined = {data.verdicts[frame][observable] for frame in data.frames if data.verdicts[frame][observable] is not None}
            if len(defined) > 1:
                obstructions.append({"observable": observable, "frame_verdicts": {frame: data.verdicts[frame][observable] for frame in data.frames if data.verdicts[frame][observable] is not None}})
            assignment[observable] = next(iter(defined)) if len(defined) == 1 else data.default_value
        noncontextual = not obstructions
        global_assignment = assignment if noncontextual else None
        classical = invariant and total and noncontextual
        contextual = invariant and not noncontextual
        frame_free_total = total and all(len({data.verdicts[frame][observable] for frame in data.frames}) == 1 for observable in data.observables)
        invariant_assignment = bool(global_assignment) and all(
            global_assignment[data.observable_action[level][observable]] == global_assignment[observable]
            for level in group["elements"]
            for observable in data.observables
        )
        if not invariant:
            classification = FrameworkClassification.OPEN_TRANSLATIONAL_LAW
        elif classical:
            classification = FrameworkClassification.CLASSICAL
        elif noncontextual:
            classification = FrameworkClassification.NONCONTEXTUAL_PARTIAL
        else:
            classification = FrameworkClassification.CONTEXTUAL

        return TranslationalTruthEvaluation(
            group_valid=True,
            frame_action_valid=True,
            observable_action_valid=True,
            joint_translation_invariant=invariant,
            invariance_failures=invariance_failures,
            presentation_orbits=orbits,
            presentation_orbit_of=orbit_of,
            orbit_truth=orbit_truth,
            truth_unique=invariant,
            fragment_noncontextual=True,
            frame_assignments=frame_assignments,
            total=total,
            noncontextual=noncontextual,
            classical=classical,
            contextual=contextual,
            frame_free_total=frame_free_total,
            invariant_global_assignment=invariant_assignment,
            global_assignment=global_assignment,
            contextual_obstructions=obstructions,
            classification=classification,
            natural_orbit_truth=invariant,
        )

    async def create_framework(self, data: TranslationalTruthFrameworkCreate) -> dict[str, Any]:
        framework_id = str(uuid.uuid4())
        evaluation = self.evaluate_framework(data)
        exact_text = json.dumps(
            {
                "NRRF785": "quantum/classical translational truth framework",
                "name": data.name,
                "observables": data.observables,
                "frames": data.frames,
                "values": data.values,
                "group": data.group.model_dump(mode="json"),
                "frame_action": data.frame_action,
                "observable_action": data.observable_action,
                "verdicts": data.verdicts,
                "orbit_truth": evaluation.orbit_truth,
                "classification": evaluation.classification,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="translational truth framework",
                language_label="NRRF785 frame-observable orbit chart",
                source_id="framework-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=["unique truth on frame-observable orbits", "frame-local classical fragments", "global-section/contextuality classification"],
                constraints=["contextual does not mean truthless", "global assignment is not the truth object", "abstract framework is not a physical quantum claim"],
                relation_hints=["NRRF785", "translational truth", "classical section", "contextual obstruction"],
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="framework",
                external_key=data.external_key or f"framework:truth:{framework_id}",
                metadata={
                    **data.metadata,
                    "framework_id": framework_id,
                    "formal_reading": "NRRF785",
                    "evaluation": evaluation.model_dump(mode="json"),
                    "global_assignment_required_for_truth": False,
                    "truth_issued": False,
                },
            )
        )
        row = {
            "id": framework_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "perspective_id": data.perspective_id,
            "problem_id": data.problem_id,
            "payload": {"observables": data.observables, "frames": data.frames, "values": data.values, "default_value": data.default_value, "group": data.group.model_dump(mode="json"), "frame_action": data.frame_action, "observable_action": data.observable_action, "verdicts": data.verdicts},
            "evaluation": evaluation.model_dump(mode="json"),
            "source_ids": data.source_ids,
            "metadata": {**data.metadata, "global_assignment_required_for_truth": False, "truth_issued": False},
            "created_at": utcnow(),
        }
        stored = self.store.create_framework(row)
        if evaluation.joint_translation_invariant:
            self.runtime.supernet_integrator.determine(
                receipt["event_id"],
                actor_id=data.authored_by,
                rigidity_scope=["presentation-orbits", *evaluation.orbit_truth.keys()],
                rigidity_receipt={"joint_translation_invariant": True, "truth_unique_on_orbits": True, "global_assignment_required": False},
                determined_form={"orbit_truth": evaluation.orbit_truth, "classification": str(evaluation.classification), "global_assignment": evaluation.global_assignment, "contextual_obstructions": evaluation.contextual_obstructions},
                unitary_path_partition={"path": ["frame", "observable", "joint level shift", "orbit truth"], "partition": evaluation.presentation_orbits},
                reason="Joint frame-observable translation leaves one partial truth function on presentation orbits",
            )
            self.runtime.supernet_integrator.transition(
                receipt["event_id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RETURNED,
                    verdict=Verdict.OPEN,
                    reason="Translational truth returned with a classical section, partial section, or contextual obstruction; no framework-wide TRUE was issued",
                    actor_id=data.authored_by,
                    returned_resource_ids=[framework_id],
                    successor_potential=[{"form_type": "translational-truth-framework", "framework_id": framework_id, "classification": str(evaluation.classification), "orbit_truth": evaluation.orbit_truth, "global_assignment": evaluation.global_assignment}],
                    metadata={"nrrf785": True, "contextual_truth_retained": evaluation.contextual, "global_assignment_required_for_truth": False, "truth_issued": False},
                ),
            )
        else:
            self.runtime.supernet_integrator.transition(
                receipt["event_id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RELATION_SENSED,
                    verdict=Verdict.OPEN,
                    reason="The joint translation law fails, so orbit truth remains OPEN",
                    actor_id=data.authored_by,
                    successor_potential=[{"form_type": "open-translational-framework", "framework_id": framework_id, "invariance_failures": evaluation.invariance_failures}],
                    metadata={"nrrf785": True, "truth_issued": False},
                ),
            )
        self.projection()
        return self.store.get_framework(stored["id"])

    async def create_bridge(self, data: TruthSelectionBridgeCreate) -> dict[str, Any]:
        arena = self.store.get_arena(data.arena_id)
        framework = self.store.get_framework(data.framework_id)
        if set(data.form_to_presentation) != set(arena["forms"]):
            raise ValueError("form_to_presentation must cover every arena form")
        for form, presentation in data.form_to_presentation.items():
            if presentation.frame not in framework["frames"]:
                raise ValueError(f"mapped frame for {form} is not in the framework")
            if presentation.observable not in framework["observables"]:
                raise ValueError(f"mapped observable for {form} is not in the framework")

        failures: list[dict[str, Any]] = []
        mapping = {form: f"{presentation.frame}::{presentation.observable}" for form, presentation in data.form_to_presentation.items()}
        group_elements = arena["group"]["elements"]
        if group_elements != framework["group"]["elements"]:
            failures.append({"reason": "level groups use different ordered carriers"})
        else:
            for level in group_elements:
                for form in arena["forms"]:
                    source = data.form_to_presentation[form]
                    shifted_form = arena["action"][level][form]
                    expected = f"{framework['frame_action'][level][source.frame]}::{framework['observable_action'][level][source.observable]}"
                    observed = mapping[shifted_form]
                    if observed != expected:
                        failures.append({"level": level, "form": form, "shifted_form": shifted_form, "expected_presentation": expected, "observed_presentation": observed})
        equivariant = not failures
        selected_framework_orbits: list[int] = []
        for orbit_id in arena["evaluation"]["selected_orbit_ids"]:
            for form in arena["evaluation"]["orbits"][orbit_id]:
                presentation_key = mapping[form]
                target_orbit = framework["evaluation"]["presentation_orbit_of"][presentation_key]
                if target_orbit not in selected_framework_orbits:
                    selected_framework_orbits.append(target_orbit)
        selected_truth = {str(orbit_id): framework["evaluation"]["orbit_truth"][str(orbit_id)] for orbit_id in selected_framework_orbits}
        natural_selector = bool(arena["evaluation"]["natural"])
        framework_truth = bool(framework["evaluation"]["joint_translation_invariant"])
        unified = equivariant and natural_selector and framework_truth
        bridge_id = str(uuid.uuid4())
        exact_text = json.dumps(
            {
                "NRRF784_NRRF785": "natural selection of translational truth",
                "name": data.name,
                "arena_id": data.arena_id,
                "framework_id": data.framework_id,
                "form_to_presentation": {form: presentation.model_dump(mode="json") for form, presentation in data.form_to_presentation.items()},
                "equivariant": equivariant,
                "selected_orbit_truth": selected_truth,
                "framework_classification": framework["evaluation"]["classification"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="natural translational truth bridge",
                language_label="NRRF784 ↔ NRRF785 equivariant orbit chart",
                source_id="framework-supernet",
                capabilities=["equivariant transport of natural selection", "selection of orbit truth without global section"],
                constraints=["resource metrics remain downstream", "contextual obstruction does not erase truth", "no canonical presentation is selected"],
                relation_hints=["NRRF784", "NRRF785", "orbit truth", "naturality"],
                causal_predecessor_ids=[arena["integration_event_id"], framework["integration_event_id"]],
                parent_event_ids=[arena["integration_event_id"], framework["integration_event_id"]],
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="framework",
                external_key=data.external_key or f"framework:bridge:{bridge_id}",
                metadata={**data.metadata, "bridge_id": bridge_id, "equivariant": equivariant, "unified": unified, "resource_metric_foundational_selector": False, "global_assignment_required_for_truth": False, "truth_issued": False},
            )
        )
        row = {
            "id": bridge_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "arena_id": data.arena_id,
            "framework_id": data.framework_id,
            "payload": {
                "form_to_presentation": {form: presentation.model_dump(mode="json") for form, presentation in data.form_to_presentation.items()},
                "equivariant": equivariant,
                "equivariance_failures": failures,
                "natural_selector": natural_selector,
                "framework_translational_truth": framework_truth,
                "selected_framework_orbit_ids": selected_framework_orbits,
                "selected_orbit_truth": selected_truth,
                "unified": unified,
                "framework_classification": framework["evaluation"]["classification"],
                "global_assignment_required_for_truth": False,
                "resource_metric_foundational_selector": False,
                "canonical_presentation": None,
                "truth_issued": False,
            },
            "source_ids": data.source_ids,
            "metadata": data.metadata,
            "created_at": utcnow(),
        }
        stored = self.store.create_bridge(row)
        if unified:
            self.runtime.supernet_integrator.determine(
                receipt["event_id"],
                actor_id=data.authored_by,
                rigidity_scope=["selected-translational-orbits", *map(str, selected_framework_orbits)],
                rigidity_receipt={"selector_natural": True, "bridge_equivariant": True, "framework_truth_unique": True, "global_assignment_required": False},
                determined_form={"selected_orbit_truth": selected_truth, "framework_classification": framework["evaluation"]["classification"], "canonical_presentation": None},
                unitary_path_partition={"path": ["natural selector", "equivariant map", "orbit truth"], "partition": framework["evaluation"]["presentation_orbits"]},
                reason="Level-natural selection transports equivariantly into the shared translational truth object",
            )
            self.runtime.supernet_integrator.transition(
                receipt["event_id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RETURNED,
                    verdict=Verdict.OPEN,
                    reason="Selected orbit truth returned independently of whether a classical global section exists",
                    actor_id=data.authored_by,
                    returned_resource_ids=[bridge_id],
                    successor_potential=[{"form_type": "natural-translational-truth", "bridge_id": bridge_id, "selected_orbit_truth": selected_truth, "classification": framework["evaluation"]["classification"]}],
                    metadata={"nrrf784": True, "nrrf785": True, "global_assignment_required_for_truth": False, "resource_metric_foundational_selector": False, "truth_issued": False},
                ),
            )
        else:
            self.runtime.supernet_integrator.transition(
                receipt["event_id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RELATION_SENSED,
                    verdict=Verdict.OPEN,
                    reason="The selector/framework bridge is not yet equivariant and natural, so reunification remains OPEN",
                    actor_id=data.authored_by,
                    successor_potential=[{"form_type": "open-truth-selection-bridge", "bridge_id": bridge_id, "equivariance_failures": failures}],
                    metadata={"nrrf784": True, "nrrf785": True, "truth_issued": False},
                ),
            )
        self.projection()
        return self.store.get_bridge(stored["id"])

    def projection(self) -> dict[str, Any]:
        arenas = self.store.list_arenas()
        frameworks = self.store.list_frameworks()
        bridges = self.store.list_bridges()
        reverse: dict[str, list[str]] = {}
        for item in [*arenas, *frameworks, *bridges]:
            for source_id in item.get("source_ids", []):
                reverse.setdefault(source_id, []).append(item["integration_event_id"])
            reverse.setdefault(item["occurrence_id"], []).append(item["integration_event_id"])
        projection = FrameworkFieldProjection(
            generated_at=utcnow(),
            arenas=arenas,
            frameworks=frameworks,
            bridges=bridges,
            stats=self.store.stats(),
            source_reverse_index={key: list(dict.fromkeys(values)) for key, values in reverse.items()},
        ).model_dump(mode="json")
        self.store.set_state("framework_field_projection", projection)
        return projection
