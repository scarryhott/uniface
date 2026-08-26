from __future__ import annotations

import json
import uuid
from decimal import Decimal
from itertools import product
from typing import Any, TYPE_CHECKING

from .models import EvidenceStatus, Verdict
from .renormalization_models import (
    RegularizedFamilyCreate,
    RegularizedFamilyExtend,
    RenormalizationFieldProjection,
    RenormalizationSchemeCreate,
    SchemeEvaluation,
    UniversalityEvaluation,
)
from .renormalization_store import RenormalizationStore, utcnow
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


def _d(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _s(value: Decimal) -> str:
    return format(value, "f")


def _within(left: Decimal, right: Decimal, tolerance: Decimal) -> bool:
    return abs(left - right) <= tolerance


def _string_members(members: dict[str, list[Decimal]]) -> dict[str, list[str]]:
    return {name: [_s(value) for value in values] for name, values in members.items()}


class RenormalizationManager:
    """NRRF781 as a live relational-closure lens of the one Supernet.

    The runtime checks the supplied finite cutoff family. It never upgrades that
    finite check into an unscoped theorem about all cutoffs. A determined
    relative closure remains OPEN; absolute level and scheme choice remain
    explicitly undetermined.
    """

    def __init__(self, runtime: "ClosureSupernetRuntime", store: RenormalizationStore):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_reading": "NRRF781",
            "canonical_runtime_operation": "integrate",
            "adapter_label": "renormalization",
            "common_divergence_hypothesis_load_bearing": True,
            "relative_closure_scheme_free": True,
            "relative_closure_limit_free": True,
            "absolute_level_determined": False,
            "scheme_is_closure": False,
            "selector_relation_first": True,
            "determination_issues_truth": False,
            "finite_runtime_observation_scope": True,
            "extensions_reopen_prior_closure": True,
            "automatic_global_truth": False,
        }

    def _validate_source_ids(self, source_ids: list[str]) -> None:
        for source_id in source_ids:
            self.runtime.store.get_occurrence(source_id)

    @staticmethod
    def evaluate_family(data: RegularizedFamilyCreate) -> UniversalityEvaluation:
        names = sorted(data.members)
        tolerance = _d(data.tolerance)
        reference = names[0]
        reference_values = data.members[reference]
        cutoff_count = len(reference_values)

        pairwise: dict[str, dict[str, str]] = {name: {} for name in names}
        drifts: dict[str, dict[str, str]] = {name: {} for name in names}
        obstructions: list[dict[str, Any]] = []
        maximum_drift = Decimal("0")

        for left, right in product(names, repeat=2):
            base = data.members[left][0] - data.members[right][0]
            local_max = Decimal("0")
            failing: list[dict[str, str]] = []
            for index in range(cutoff_count):
                current = data.members[left][index] - data.members[right][index]
                drift = abs(current - base)
                local_max = max(local_max, drift)
                maximum_drift = max(maximum_drift, drift)
                if drift > tolerance:
                    failing.append(
                        {
                            "cutoff": data.cutoff_labels[index],
                            "difference": _s(current),
                            "expected": _s(base),
                            "drift": _s(drift),
                        }
                    )
            pairwise[left][right] = _s(base)
            drifts[left][right] = _s(local_max)
            if failing:
                obstructions.append(
                    {
                        "left": left,
                        "right": right,
                        "maximum_drift": _s(local_max),
                        "failures": failing,
                    }
                )

        universal = not obstructions
        cocycle = True
        for left, middle, right in product(names, repeat=3):
            lhs = _d(pairwise[left][middle]) + _d(pairwise[middle][right])
            rhs = _d(pairwise[left][right])
            if not _within(lhs, rhs, tolerance):
                cocycle = False
                break

        relative_chart = {
            name: _s(data.members[name][0] - reference_values[0]) for name in names
        }
        return UniversalityEvaluation(
            member_names=names,
            cutoff_labels=list(data.cutoff_labels),
            common_divergence_universal=universal,
            relative_closure_determined=universal,
            cutoff_independent=universal,
            scheme_free=universal,
            limit_free=universal,
            selector_rigid=universal,
            determination_issues_truth=False,
            absolute_level_determined=False,
            finite_observation_scope=True,
            reference_member=reference,
            common_component_chart=[_s(value) for value in reference_values],
            relative_member_chart=relative_chart,
            pairwise_differences=pairwise,
            pairwise_max_drift=drifts,
            maximum_drift=_s(maximum_drift),
            cocycle_consistent=cocycle,
            greatest_scheme_invariant_content=universal and cocycle,
            obstructions=obstructions,
        )

    async def create_family(self, data: RegularizedFamilyCreate) -> dict[str, Any]:
        return await self._create_family(data, parent_family_id=None, parent_event_ids=[])

    async def _create_family(
        self,
        data: RegularizedFamilyCreate,
        *,
        parent_family_id: str | None,
        parent_event_ids: list[str],
    ) -> dict[str, Any]:
        self._validate_source_ids(data.universality_source_ids)
        family_id = str(uuid.uuid4())
        evaluation = self.evaluate_family(data)
        members = _string_members(data.members)
        exact_payload = {
            "family": data.name,
            "cutoffs": data.cutoff_labels,
            "members": members,
            "tolerance": _s(data.tolerance),
            "parent_family_id": parent_family_id,
        }
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=(
                    "NRRF781 regularized family: "
                    + json.dumps(exact_payload, ensure_ascii=False, sort_keys=True)
                ),
                authored_by=data.authored_by,
                form_label="regularized family",
                language_label="NRRF781 translational relative closure",
                source_id="renormalization-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "pairwise relative reading",
                    "cutoff-drift comparison",
                    "scheme chart comparison",
                ],
                constraints=[
                    "common divergent component is load-bearing",
                    "runtime witness is scoped to submitted cutoffs",
                    "absolute level remains undetermined",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF781",
                    "common divergence",
                    "relative closure",
                    "scheme-invariant difference",
                    "translational truth not absolute normalization",
                ],
                parent_event_ids=parent_event_ids,
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.SIMULATED_UNDER_ASSUMPTIONS,
                adapter_label="renormalization",
                external_key=data.external_key or f"renormalization:family:{family_id}",
                metadata={
                    **data.metadata,
                    "renormalization_family_id": family_id,
                    "parent_family_id": parent_family_id,
                    "members": members,
                    "cutoff_labels": data.cutoff_labels,
                    "tolerance": _s(data.tolerance),
                    "universality_source_ids": data.universality_source_ids,
                    "universality": evaluation.model_dump(mode="json"),
                    "finite_observation_scope": True,
                    "absolute_level_determined": False,
                    "scheme_selected_as_truth": False,
                },
            )
        )
        event_id = receipt["event_id"]

        if evaluation.relative_closure_determined:
            pair_scope = [
                f"difference:{left}:{right}"
                for left in evaluation.member_names
                for right in evaluation.member_names
            ]
            self.runtime.supernet_integrator.determine(
                event_id,
                actor_id=data.authored_by,
                rigidity_scope=pair_scope,
                rigidity_receipt={
                    "relation": "a_i(n) - a_j(n) is constant across the submitted cutoffs",
                    "common_divergence_universal": True,
                    "pairwise_admissible_values": evaluation.pairwise_differences,
                    "each_pair_unique": True,
                    "cutoff_labels": data.cutoff_labels,
                    "tolerance": _s(data.tolerance),
                    "finite_observation_scope": True,
                    "universality_source_ids": data.universality_source_ids,
                },
                determined_form={
                    "relative_reading": evaluation.pairwise_differences,
                    "absolute_level": None,
                    "scheme_selected": False,
                    "reference_chart": {
                        "reference_member": evaluation.reference_member,
                        "relative_values": evaluation.relative_member_chart,
                        "noncanonical": True,
                    },
                },
                unitary_path_partition={
                    "path": [
                        "regularized family",
                        "pairwise difference",
                        "relative closure",
                        "scheme chart",
                        "reopening",
                    ],
                    "partition": {
                        "scheme_orbit": "absolute assignments under a common additive shift",
                        "invariant": "pairwise differences",
                        "dropped": "common additive absolute level",
                    },
                },
                reason=(
                    "The submitted common-divergence relation is rigid and leaves "
                    "one pairwise relative closure standing"
                ),
            )
            return_reason = (
                "Relative closure returned without counterterm, cutoff removal, "
                "limit, absolute normalization, or truth verdict"
            )
            successor = [
                {
                    "form_type": "relative-renormalization-closure",
                    "form_id": family_id,
                    "pairwise_differences": evaluation.pairwise_differences,
                    "absolute_level": None,
                    "scheme_required": False,
                }
            ]
            status = "RELATIVE_CLOSURE_DETERMINED"
        else:
            return_reason = (
                "The submitted family does not yet support one common-divergence "
                "closure; the obstruction remains OPEN"
            )
            successor = [
                {
                    "form_type": "renormalization-universality-obstruction",
                    "form_id": family_id,
                    "obstructions": evaluation.obstructions,
                    "reopening_required": True,
                }
            ]
            status = "OPEN_UNIVERSALITY"

        self.runtime.supernet_integrator.transition(
            event_id,
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason=return_reason,
                actor_id=data.authored_by,
                returned_resource_ids=[family_id],
                successor_potential=successor,
                metadata={
                    "nrrf781": True,
                    "relative_closure_determined": evaluation.relative_closure_determined,
                    "absolute_level_determined": False,
                    "scheme_selected_as_truth": False,
                    "limit_required_for_relative_closure": False,
                    "truth_issued": False,
                    "finite_observation_scope": True,
                },
            ),
        )

        row = {
            "id": family_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": event_id,
            "parent_family_id": parent_family_id,
            "name": data.name,
            "authored_by": data.authored_by,
            "perspective_id": data.perspective_id,
            "problem_id": data.problem_id,
            "cutoff_labels": data.cutoff_labels,
            "members": members,
            "tolerance": _s(data.tolerance),
            "universality_source_ids": data.universality_source_ids,
            "universality": evaluation.model_dump(mode="json"),
            "status": status,
            "metadata": {
                **data.metadata,
                "truth_issued": False,
                "scheme_is_closure": False,
                "absolute_level_determined": False,
            },
            "created_at": utcnow(),
        }
        result = self.store.create_family(row)
        self.projection()
        return result

    async def extend_family(
        self, family_id: str, data: RegularizedFamilyExtend
    ) -> dict[str, Any]:
        parent = self.store.get_family(family_id)
        parent_names = set(parent["members"])
        if set(data.members) != parent_names:
            raise ValueError("an extension must provide exactly the existing family members")
        overlap = set(parent["cutoff_labels"]) & set(data.cutoff_labels)
        if overlap:
            raise ValueError(f"extension cutoff labels already exist: {sorted(overlap)}")
        self._validate_source_ids(data.universality_source_ids)

        self.runtime.supernet_integrator.transition(
            parent["integration_event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.REOPENED,
                verdict=Verdict.OPEN,
                reason="New cutoff evidence reopens the prior scoped relative closure",
                actor_id=data.authored_by,
                successor_potential=[
                    {
                        "form_type": "extended-regularized-family",
                        "parent_family_id": family_id,
                        "new_cutoffs": data.cutoff_labels,
                    }
                ],
                metadata={
                    "nrrf781": True,
                    "reopened_by_new_cutoff_evidence": True,
                    "truth_issued": False,
                },
            ),
        )

        combined_members: dict[str, list[Decimal]] = {}
        for name in sorted(parent_names):
            combined_members[name] = [
                *[_d(value) for value in parent["members"][name]],
                *data.members[name],
            ]
        combined_sources = list(
            dict.fromkeys(
                [*parent["universality_source_ids"], *data.universality_source_ids]
            )
        )
        child = RegularizedFamilyCreate(
            name=f"{parent['name']} — extended",
            authored_by=data.authored_by,
            members=combined_members,
            cutoff_labels=[*parent["cutoff_labels"], *data.cutoff_labels],
            tolerance=_d(parent["tolerance"]),
            perspective_id=parent.get("perspective_id"),
            problem_id=parent.get("problem_id"),
            universality_source_ids=combined_sources,
            metadata={
                **parent.get("metadata", {}),
                **data.metadata,
                "extended_from": family_id,
            },
            external_key=data.external_key,
        )
        return await self._create_family(
            child,
            parent_family_id=family_id,
            parent_event_ids=[parent["integration_event_id"]],
        )

    @staticmethod
    def evaluate_scheme(
        family: dict[str, Any], data: RenormalizationSchemeCreate
    ) -> SchemeEvaluation:
        cutoff_labels = family["cutoff_labels"]
        if len(data.counterterm) != len(cutoff_labels):
            raise ValueError("counterterm length must match the family cutoff count")
        tolerance = _d(family["tolerance"])
        members = {
            name: [_d(value) for value in values]
            for name, values in family["members"].items()
        }
        names = sorted(members)
        sequences: dict[str, list[Decimal]] = {
            name: [value - data.counterterm[index] for index, value in enumerate(values)]
            for name, values in members.items()
        }
        maximum_drift = Decimal("0")
        admissible = True
        for values in sequences.values():
            base = values[0]
            for value in values:
                drift = abs(value - base)
                maximum_drift = max(maximum_drift, drift)
                if drift > tolerance:
                    admissible = False
        renormalized_values = {name: values[0] for name, values in sequences.items()}
        relative: dict[str, dict[str, str]] = {name: {} for name in names}
        for left, right in product(names, repeat=2):
            relative[left][right] = _s(
                renormalized_values[left] - renormalized_values[right]
            )

        closure = family["universality"]["pairwise_differences"]
        matches = bool(family["universality"]["relative_closure_determined"])
        if matches:
            for left, right in product(names, repeat=2):
                if not _within(
                    _d(relative[left][right]), _d(closure[left][right]), tolerance
                ):
                    matches = False
                    break

        shifted_counterterm = [value + data.shift_probe for value in data.counterterm]
        shifted_values = {
            name: renormalized_values[name] - data.shift_probe for name in names
        }
        shift_moves = bool(
            data.shift_probe != 0
            and any(shifted_values[name] != renormalized_values[name] for name in names)
        )
        shift_preserves = True
        for left, right in product(names, repeat=2):
            before = renormalized_values[left] - renormalized_values[right]
            after = shifted_values[left] - shifted_values[right]
            if not _within(before, after, tolerance):
                shift_preserves = False
                break

        return SchemeEvaluation(
            admissible_scheme=admissible,
            counterterm=[_s(value) for value in data.counterterm],
            renormalized_sequences={
                name: [_s(value) for value in values] for name, values in sequences.items()
            },
            renormalized_values={name: _s(value) for name, value in renormalized_values.items()},
            maximum_residual_drift=_s(maximum_drift),
            relative_differences=relative,
            matches_relative_closure=matches,
            shift_probe=_s(data.shift_probe),
            shifted_counterterm=[_s(value) for value in shifted_counterterm],
            shifted_renormalized_values={
                name: _s(value) for name, value in shifted_values.items()
            },
            shift_moves_absolute_values=shift_moves,
            shift_preserves_relative_closure=shift_preserves,
        )

    async def create_scheme(
        self, family_id: str, data: RenormalizationSchemeCreate
    ) -> dict[str, Any]:
        family = self.store.get_family(family_id)
        self._validate_source_ids(data.scheme_source_ids)
        scheme_id = str(uuid.uuid4())
        evaluation = self.evaluate_scheme(family, data)
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=(
                    f"NRRF781 scheme chart {data.name} for family {family_id}: "
                    f"counterterm={evaluation.counterterm}; shift_probe={evaluation.shift_probe}; "
                    f"admissible={evaluation.admissible_scheme}."
                ),
                authored_by=data.authored_by,
                form_label="renormalization scheme chart",
                language_label="noncanonical absolute normalization chart",
                source_id="renormalization-supernet",
                parent_event_ids=[family["integration_event_id"]],
                capabilities=[
                    "counterterm chart",
                    "absolute-value display",
                    "relative-closure comparison",
                ],
                constraints=[
                    "scheme is not closure",
                    "common shift changes absolute values",
                    "scheme does not issue truth",
                ],
                relation_hints=[
                    "NRRF781",
                    "renormalization scheme ambiguity",
                    "difference scheme independent",
                ],
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.SIMULATED_UNDER_ASSUMPTIONS,
                adapter_label="renormalization",
                external_key=data.external_key or f"renormalization:scheme:{scheme_id}",
                metadata={
                    **data.metadata,
                    "renormalization_scheme_id": scheme_id,
                    "family_id": family_id,
                    "evaluation": evaluation.model_dump(mode="json"),
                    "scheme_source_ids": data.scheme_source_ids,
                    "scheme_is_closure": False,
                    "absolute_chart_noncanonical": True,
                },
            )
        )
        self.runtime.supernet_integrator.transition(
            receipt["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason=(
                    "The scheme chart returned absolute values while preserving "
                    "the relative closure; no scheme was selected as truth"
                ),
                actor_id=data.authored_by,
                returned_resource_ids=[scheme_id],
                successor_potential=[
                    {
                        "form_type": "renormalization-scheme-chart",
                        "form_id": scheme_id,
                        "family_id": family_id,
                        "matches_relative_closure": evaluation.matches_relative_closure,
                        "scheme_is_closure": False,
                    }
                ],
                metadata={
                    "nrrf781": True,
                    "scheme_is_closure": False,
                    "shift_moves_absolute_values": evaluation.shift_moves_absolute_values,
                    "shift_preserves_relative_closure": evaluation.shift_preserves_relative_closure,
                    "truth_issued": False,
                },
            ),
        )
        row = {
            "id": scheme_id,
            "family_id": family_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "scheme_source_ids": data.scheme_source_ids,
            "evaluation": evaluation.model_dump(mode="json"),
            "metadata": {**data.metadata, "truth_issued": False},
            "created_at": utcnow(),
        }
        result = self.store.create_scheme(row)
        self.projection()
        return result

    def closure(self, family_id: str) -> dict[str, Any]:
        family = self.store.get_family(family_id)
        return {
            "family_id": family_id,
            "status": family["status"],
            "relative_closure": family["universality"]["pairwise_differences"],
            "relative_closure_determined": family["universality"][
                "relative_closure_determined"
            ],
            "absolute_level": None,
            "scheme_selected": False,
            "limit_required": False,
            "cutoff_independent": family["universality"]["cutoff_independent"],
            "cocycle_consistent": family["universality"]["cocycle_consistent"],
            "greatest_scheme_invariant_content": family["universality"][
                "greatest_scheme_invariant_content"
            ],
            "obstructions": family["universality"]["obstructions"],
            "finite_observation_scope": True,
            "truth_issued": False,
            "source_reverse_index": {
                f"renormalization:family:{family_id}": [
                    family["occurrence_id"],
                    *family["universality_source_ids"],
                ]
            },
        }

    def projection(self) -> dict[str, Any]:
        families = self.store.list_families(limit=10_000)
        schemes = self.store.list_schemes(limit=10_000)
        source_reverse_index: dict[str, list[str]] = {}
        for family in families:
            source_reverse_index[f"renormalization:family:{family['id']}"] = list(
                dict.fromkeys(
                    [family["occurrence_id"], *family["universality_source_ids"]]
                )
            )
        for scheme in schemes:
            source_reverse_index[f"renormalization:scheme:{scheme['id']}"] = list(
                dict.fromkeys([scheme["occurrence_id"], *scheme["scheme_source_ids"]])
            )
        projection = RenormalizationFieldProjection(
            generated_at=utcnow(),
            families=families,
            schemes=schemes,
            stats={
                **self.store.stats(),
                "finite_observation_scope": True,
                "absolute_level_determined": False,
                "scheme_is_closure": False,
            },
            source_reverse_index=source_reverse_index,
        ).model_dump(mode="json")
        self.store.set_state("renormalization_field_projection", projection)
        return projection
