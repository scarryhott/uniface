from __future__ import annotations

import json
import uuid
from typing import Any, TYPE_CHECKING

from .constructive_models import (
    AxiometricFormCreate,
    AxiometricFormEvaluation,
    ConstructiveFieldProjection,
    FiniteCommutativeGroupCreate,
    IdempotentTranslationCreate,
    TranslationChartCompareCreate,
    TranslationalClosureCreate,
    TranslationalClosureEvaluation,
)
from .constructive_store import ConstructiveStore, utcnow
from .models import EvidenceStatus, Verdict
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


class ConstructiveClosureManager:
    """Executable explicit-witness reading of NRRF783.

    The Lean modules establish the constructive theorems. This manager does not
    re-prove them: it requires the finite runtime witnesses as data, validates
    them directly, and sends every result through the one Supernet integrator.
    """

    def __init__(self, runtime: "ClosureSupernetRuntime", store: ConstructiveStore):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_reading": "NRRF783",
            "canonical_runtime_operation": "integrate",
            "adapter_label": "constructive",
            "explicit_witnesses": True,
            "section_carried_as_data": True,
            "u1_single_postulate": True,
            "u2_derived": True,
            "u3_defect_reading": True,
            "form_from_idempotent": True,
            "base_site_supplied_as_data": True,
            "relative_potential_complete": True,
            "overlap_witness_forces_closure_equality": True,
            "classical_choice_required": False,
            "excluded_middle_required": False,
            "runtime_is_formal_proof": False,
            "determination_issues_truth": False,
            "canonical_language": None,
        }

    @staticmethod
    def evaluate_form(data: AxiometricFormCreate) -> AxiometricFormEvaluation:
        u1_failures: list[dict[str, str]] = []
        for source in data.source_carrier:
            encoded = data.encode[source]
            returned = data.evaluate[encoded]
            if returned != source:
                u1_failures.append(
                    {
                        "source": source,
                        "encoded": encoded,
                        "returned": returned,
                    }
                )
        u1 = not u1_failures
        hold = {
            presentation: data.encode[data.evaluate[presentation]]
            for presentation in data.presentation_carrier
        }
        u2 = all(
            hold[hold[presentation]] == hold[presentation]
            for presentation in data.presentation_carrier
        )
        defect = [
            presentation
            for presentation in data.presentation_carrier
            if hold[presentation] != presentation
        ]
        u3 = not defect
        encode_injective = len(set(data.encode.values())) == len(data.source_carrier)
        evaluate_surjective = set(data.evaluate.values()) == set(data.source_carrier)
        encode_surjective = set(data.encode.values()) == set(data.presentation_carrier)
        evaluate_injective = len(set(data.evaluate.values())) == len(
            data.presentation_carrier
        )
        fixed = [
            presentation
            for presentation in data.presentation_carrier
            if hold[presentation] == presentation
        ]
        return AxiometricFormEvaluation(
            u1_return=u1,
            u1_failures=u1_failures,
            hold=hold,
            u2_hold_idempotent=u2,
            u2_derived_from_u1=u1 and u2,
            u3_closes=u3,
            defect=defect,
            defect_empty=not defect,
            defect_empty_iff_closes=(u3 == (not defect)),
            encode_injective=encode_injective,
            evaluate_surjective=evaluate_surjective,
            encode_surjective=encode_surjective,
            evaluate_injective=evaluate_injective,
            fixed_presentations=fixed,
            admissible_form=u1,
        )

    async def create_form(
        self,
        data: AxiometricFormCreate,
        *,
        origin: str = "EXPLICIT_AXIOMETRIC_FORM",
    ) -> dict[str, Any]:
        form_id = str(uuid.uuid4())
        evaluation = self.evaluate_form(data)
        exact_text = json.dumps(
            {
                "NRRF783": "axiometric form",
                "name": data.name,
                "source_carrier": data.source_carrier,
                "presentation_carrier": data.presentation_carrier,
                "encode": data.encode,
                "evaluate": data.evaluate,
                "U1": evaluation.u1_return,
                "U2": evaluation.u2_hold_idempotent,
                "U3": evaluation.u3_closes,
                "defect": evaluation.defect,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="constructive axiometric form",
                language_label="NRRF783 explicit witness chart",
                source_id="constructive-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "explicit encode/evaluate/return witnesses",
                    "U2 derivation from U1",
                    "U3 defect reading",
                    "choice-free finite execution chart",
                ],
                constraints=[
                    "runtime chart is not the Lean proof",
                    "determination does not issue TRUE",
                    "section is supplied as data",
                ],
                relation_hints=[
                    "NRRF783",
                    "U1 return",
                    "U2 hold",
                    "U3 closing",
                    "constructive closure form",
                ],
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="constructive",
                external_key=data.external_key or f"constructive:form:{form_id}",
                metadata={
                    **data.metadata,
                    "constructive_form_id": form_id,
                    "origin": origin,
                    "source_ids": data.source_ids,
                    "evaluation": evaluation.model_dump(mode="json"),
                    "section_carried_as_data": True,
                    "classical_choice_required": False,
                    "excluded_middle_required": False,
                    "runtime_is_formal_proof": False,
                    "truth_issued": False,
                },
            )
        )
        row = {
            "id": form_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": data.name,
            "origin": origin,
            "authored_by": data.authored_by,
            "perspective_id": data.perspective_id,
            "problem_id": data.problem_id,
            "source_carrier": data.source_carrier,
            "presentation_carrier": data.presentation_carrier,
            "encode": data.encode,
            "evaluate": data.evaluate,
            "evaluation": evaluation.model_dump(mode="json"),
            "source_ids": data.source_ids,
            "metadata": {
                **data.metadata,
                "section_carried_as_data": True,
                "classical_choice_required": False,
                "excluded_middle_required": False,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        stored = self.store.create_form(row)
        if evaluation.u1_return:
            self.runtime.supernet_integrator.determine(
                receipt["event_id"],
                actor_id=data.authored_by,
                rigidity_scope=["U1:return", *data.source_carrier],
                rigidity_receipt={
                    "U1_return": True,
                    "encode_is_section_data": True,
                    "source_fibres_inhabited_by": data.encode,
                    "choice_required": False,
                },
                determined_form={
                    "form_id": form_id,
                    "encode": data.encode,
                    "evaluate": data.evaluate,
                    "hold": evaluation.hold,
                    "closes": evaluation.u3_closes,
                    "defect": evaluation.defect,
                },
                unitary_path_partition={
                    "path": ["encode", "evaluate", "hold", "return"],
                    "partition": {
                        "fixed_presentations": evaluation.fixed_presentations,
                        "defect_presentations": evaluation.defect,
                    },
                },
                reason="The explicit return witness satisfies U1; U2 is derived and U3 is read by the defect",
            )
            self.runtime.supernet_integrator.transition(
                receipt["event_id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RETURNED,
                    verdict=Verdict.OPEN,
                    reason="Constructive closure-form evaluation returned without issuing TRUE",
                    actor_id=data.authored_by,
                    returned_resource_ids=[form_id],
                    successor_potential=[
                        {
                            "form_type": "constructive-form",
                            "form_id": form_id,
                            "u3_closes": evaluation.u3_closes,
                            "defect": evaluation.defect,
                        }
                    ],
                    metadata={
                        "nrrf783": True,
                        "u1_return": True,
                        "u2_derived": evaluation.u2_derived_from_u1,
                        "u3_closes": evaluation.u3_closes,
                        "classical_choice_required": False,
                        "excluded_middle_required": False,
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
                    reason="The submitted finite chart does not satisfy U1 and remains an OPEN form attempt",
                    actor_id=data.authored_by,
                    successor_potential=[
                        {
                            "form_type": "constructive-form-attempt",
                            "form_id": form_id,
                            "u1_failures": evaluation.u1_failures,
                        }
                    ],
                    metadata={
                        "nrrf783": True,
                        "admissible_form": False,
                        "classical_choice_required": False,
                        "truth_issued": False,
                    },
                ),
            )
        self.projection()
        return self.store.get_form(stored["id"])

    async def create_from_idempotent(
        self, data: IdempotentTranslationCreate
    ) -> dict[str, Any]:
        idempotent = all(
            data.translation[data.translation[item]] == data.translation[item]
            for item in data.carrier
        )
        if not idempotent:
            raise ValueError("translation must be idempotent to construct a form")
        fixed = [item for item in data.carrier if data.translation[item] == item]
        if not fixed:
            raise ValueError("an idempotent translation on a nonempty carrier must expose fixed data")
        form_data = AxiometricFormCreate(
            name=data.name,
            authored_by=data.authored_by,
            source_carrier=fixed,
            presentation_carrier=data.carrier,
            encode={item: item for item in fixed},
            evaluate=data.translation,
            perspective_id=data.perspective_id,
            problem_id=data.problem_id,
            source_ids=data.source_ids,
            metadata={
                **data.metadata,
                "idempotent_translation": data.translation,
                "fixed_points": fixed,
                "constructed_not_chosen": True,
            },
            external_key=data.external_key,
        )
        return await self.create_form(
            form_data, origin="IDEMPOTENT_TRANSLATION_CONSTRUCTED_FORM"
        )

    @staticmethod
    def _validate_group(group: FiniteCommutativeGroupCreate) -> dict[str, Any]:
        elements = group.elements
        element_set = set(elements)
        if group.zero not in element_set:
            raise ValueError("group zero must be an element")
        if set(group.addition) != element_set:
            raise ValueError("addition table must have one row for every element")
        if set(group.inverse) != element_set:
            raise ValueError("inverse table must cover every element")
        for left in elements:
            row = group.addition[left]
            if set(row) != element_set:
                raise ValueError(f"addition row {left} must cover every element")
            if any(value not in element_set for value in row.values()):
                raise ValueError(f"addition row {left} leaves the group")
        if any(value not in element_set for value in group.inverse.values()):
            raise ValueError("inverse values must lie in the group")
        for value in elements:
            if group.addition[group.zero][value] != value:
                raise ValueError("zero is not a left identity")
            if group.addition[value][group.zero] != value:
                raise ValueError("zero is not a right identity")
            inverse = group.inverse[value]
            if group.addition[value][inverse] != group.zero:
                raise ValueError("inverse table fails on the right")
            if group.addition[inverse][value] != group.zero:
                raise ValueError("inverse table fails on the left")
        for left in elements:
            for right in elements:
                if group.addition[left][right] != group.addition[right][left]:
                    raise ValueError("addition must be commutative")
                for third in elements:
                    lhs = group.addition[group.addition[left][right]][third]
                    rhs = group.addition[left][group.addition[right][third]]
                    if lhs != rhs:
                        raise ValueError("addition must be associative")
        return group.model_dump(mode="json")

    @staticmethod
    def _relative_potential(
        group: dict[str, Any], sites: list[str], levels: dict[str, str]
    ) -> dict[str, dict[str, str]]:
        add = group["addition"]
        inverse = group["inverse"]
        return {
            left: {
                right: add[inverse[levels[left]]][levels[right]]
                for right in sites
            }
            for left in sites
        }

    @staticmethod
    def _cocycle_consistent(
        group: dict[str, Any],
        sites: list[str],
        relative: dict[str, dict[str, str]],
    ) -> bool:
        add = group["addition"]
        zero = group["zero"]
        for left in sites:
            if relative[left][left] != zero:
                return False
            for middle in sites:
                for right in sites:
                    if add[relative[left][middle]][relative[middle][right]] != relative[left][right]:
                        return False
        return True

    async def create_translation(
        self, data: TranslationalClosureCreate
    ) -> dict[str, Any]:
        group = self._validate_group(data.group)
        element_set = set(group["elements"])
        if any(value not in element_set for value in data.levels.values()):
            raise ValueError("every site level must be a group element")
        closure_id = str(uuid.uuid4())
        closure_form_id = str(uuid.uuid4())
        relative = self._relative_potential(group, data.sites, data.levels)
        cocycle = self._cocycle_consistent(group, data.sites, relative)
        chart_tokens = {shift: f"chart:{shift}" for shift in group["elements"]}
        closure_form_data = AxiometricFormCreate(
            name=f"{data.name} closure form",
            authored_by=data.authored_by,
            source_carrier=list(group["elements"]),
            presentation_carrier=list(chart_tokens.values()),
            encode=chart_tokens,
            evaluate={token: shift for shift, token in chart_tokens.items()},
            perspective_id=data.perspective_id,
            problem_id=data.problem_id,
            source_ids=data.source_ids,
            metadata={
                "origin": "TRANSLATIONAL_TRUTH_BRIDGE",
                "base_site": data.base_site,
                "site_chosen_by_runtime": False,
            },
        )
        closure_form_evaluation = self.evaluate_form(closure_form_data)
        exact_text = json.dumps(
            {
                "NRRF783": "translational truth closure",
                "name": data.name,
                "group": group,
                "sites": data.sites,
                "base_site": data.base_site,
                "levels": data.levels,
                "relative_potential": relative,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="constructive translational closure",
                language_label="NRRF783 relative-potential chart",
                source_id="constructive-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "explicit finite commutative-group witnesses",
                    "relative-potential invariance",
                    "computable closure form from supplied base site",
                    "unique common-shift comparison",
                ],
                constraints=[
                    "base site is participant-supplied data",
                    "no canonical absolute level",
                    "runtime chart is not the Lean proof",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF783",
                    "translational truth",
                    "relative potential",
                    "closure form",
                    "common shift",
                ],
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="constructive",
                external_key=data.external_key
                or f"constructive:translation:{closure_id}",
                metadata={
                    **data.metadata,
                    "constructive_closure_id": closure_id,
                    "closure_form_id": closure_form_id,
                    "source_ids": data.source_ids,
                    "base_site_supplied": True,
                    "site_chosen_by_runtime": False,
                    "classical_choice_required": False,
                    "excluded_middle_required": False,
                    "truth_issued": False,
                },
            )
        )
        form_row = {
            "id": closure_form_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": closure_form_data.name,
            "origin": "TRANSLATIONAL_TRUTH_BRIDGE",
            "authored_by": data.authored_by,
            "perspective_id": data.perspective_id,
            "problem_id": data.problem_id,
            "source_carrier": closure_form_data.source_carrier,
            "presentation_carrier": closure_form_data.presentation_carrier,
            "encode": closure_form_data.encode,
            "evaluate": closure_form_data.evaluate,
            "evaluation": closure_form_evaluation.model_dump(mode="json"),
            "source_ids": data.source_ids,
            "metadata": {
                "constructive_closure_id": closure_id,
                "base_site": data.base_site,
                "choice_free_bridge": True,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        self.store.create_form(form_row)
        evaluation = TranslationalClosureEvaluation(
            group_valid=True,
            base_site_supplied=True,
            relative_potential=relative,
            cocycle_consistent=cocycle,
            common_shift_invariant=True,
            relative_potential_complete=True,
            closure_form_closes=closure_form_evaluation.u3_closes,
            closure_form_id=closure_form_id,
        )
        row = {
            "id": closure_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "perspective_id": data.perspective_id,
            "problem_id": data.problem_id,
            "group": group,
            "sites": data.sites,
            "base_site": data.base_site,
            "levels": data.levels,
            "source_ids": data.source_ids,
            "evaluation": evaluation.model_dump(mode="json"),
            "metadata": {
                **data.metadata,
                "canonical_absolute_level": None,
                "base_site_supplied": True,
                "site_chosen_by_runtime": False,
                "classical_choice_required": False,
                "excluded_middle_required": False,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        self.store.create_translation(row)
        self.runtime.supernet_integrator.determine(
            receipt["event_id"],
            actor_id=data.authored_by,
            rigidity_scope=[
                f"relative-potential:{left}:{right}"
                for left in data.sites
                for right in data.sites
            ],
            rigidity_receipt={
                "group_valid": True,
                "base_site": data.base_site,
                "base_site_supplied_as_data": True,
                "relative_potential_unique": True,
                "choice_required": False,
            },
            determined_form={
                "constructive_closure_id": closure_id,
                "relative_potential": relative,
                "canonical_absolute_level": None,
                "closure_form_id": closure_form_id,
            },
            unitary_path_partition={
                "path": ["level chart", "common shift", "relative potential", "closure form"],
                "partition": {
                    "one_closure_orbit": list(group["elements"]),
                    "invariant": "relative potential",
                    "presentation": "absolute level chart",
                },
            },
            reason="The supplied group and base site compute the complete relative-potential closure without choosing an absolute level",
        )
        self.runtime.supernet_integrator.transition(
            receipt["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="Constructive translational closure returned without issuing TRUE",
                actor_id=data.authored_by,
                returned_resource_ids=[closure_id, closure_form_id],
                successor_potential=[
                    {
                        "form_type": "constructive-translational-closure",
                        "form_id": closure_id,
                        "relative_potential": relative,
                        "canonical_absolute_level": None,
                    }
                ],
                metadata={
                    "nrrf783": True,
                    "base_site_supplied": True,
                    "relative_potential_complete": True,
                    "classical_choice_required": False,
                    "excluded_middle_required": False,
                    "truth_issued": False,
                },
            ),
        )
        self.projection()
        return self.store.get_translation(closure_id)

    async def compare_chart(
        self, closure_id: str, data: TranslationChartCompareCreate
    ) -> dict[str, Any]:
        closure = self.store.get_translation(closure_id)
        sites = list(closure["sites"])
        if set(data.levels) != set(sites):
            raise ValueError("comparison levels must be total exactly on closure sites")
        group = closure["group"]
        elements = set(group["elements"])
        if any(value not in elements for value in data.levels.values()):
            raise ValueError("comparison levels must lie in the closure group")
        base = closure["base_site"]
        first = closure["levels"]
        shift = group["addition"][group["inverse"][first[base]]][data.levels[base]]
        shifted = {
            site: group["addition"][first[site]][shift]
            for site in sites
        }
        differs_by_shift = shifted == data.levels
        first_relative = closure["evaluation"]["relative_potential"]
        second_relative = self._relative_potential(group, sites, data.levels)
        relative_equal = first_relative == second_relative
        closure_equal = differs_by_shift and relative_equal
        comparison_id = str(uuid.uuid4())
        exact_text = json.dumps(
            {
                "NRRF783": "translation-chart comparison",
                "closure_id": closure_id,
                "first_levels": first,
                "comparison_levels": data.levels,
                "derived_shift": shift,
                "closure_equal": closure_equal,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="constructive translation-chart comparison",
                language_label="NRRF783 shift witness",
                source_id="constructive-supernet",
                capabilities=[
                    "derive unique common shift from supplied base site",
                    "compare relative potentials",
                    "overlap witness forces closure equality",
                ],
                constraints=[
                    "no global equal-or-disjoint decision is inferred",
                    "comparison uses explicit chart data",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF783",
                    "shift uniqueness",
                    "relative potential completeness",
                    "overlap forces equality",
                ],
                parent_event_ids=[closure["integration_event_id"]],
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.INTERPRETED_RELATION,
                adapter_label="constructive",
                external_key=data.external_key
                or f"constructive:comparison:{comparison_id}",
                metadata={
                    **data.metadata,
                    "closure_id": closure_id,
                    "source_ids": data.source_ids,
                    "derived_shift": shift,
                    "classical_choice_required": False,
                    "excluded_middle_required": False,
                    "truth_issued": False,
                },
            )
        )
        row = {
            "id": comparison_id,
            "closure_id": closure_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "authored_by": data.authored_by,
            "comparison_levels": data.levels,
            "derived_shift": shift,
            "charts_differ_by_common_shift": differs_by_shift,
            "relative_potentials_equal": relative_equal,
            "closure_equal": closure_equal,
            "unique_shift": closure_equal,
            "overlap_forces_equality": closure_equal,
            "absolute_levels_noncanonical": True,
            "source_ids": data.source_ids,
            "metadata": {
                **data.metadata,
                "first_levels": first,
                "shifted_first_levels": shifted,
                "no_dichotomy_claimed": True,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        stored = self.store.create_comparison(row)
        self.runtime.supernet_integrator.transition(
            receipt["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason=(
                    "Explicit common-shift witness identifies one closure"
                    if closure_equal
                    else "The submitted charts do not share the derived closure witness"
                ),
                actor_id=data.authored_by,
                returned_resource_ids=[comparison_id],
                successor_potential=[
                    {
                        "form_type": "constructive-chart-comparison",
                        "form_id": comparison_id,
                        "closure_equal": closure_equal,
                        "derived_shift": shift,
                    }
                ],
                metadata={
                    "nrrf783": True,
                    "closure_equal": closure_equal,
                    "unique_shift": closure_equal,
                    "classical_choice_required": False,
                    "excluded_middle_required": False,
                    "truth_issued": False,
                },
            ),
        )
        self.projection()
        return stored

    def projection(self) -> dict[str, Any]:
        forms = self.store.list_forms(limit=10_000)
        translations = self.store.list_translations(limit=10_000)
        comparisons = self.store.list_comparisons(limit=10_000)
        stats = self.store.stats()
        source_reverse_index: dict[str, list[str]] = {}
        for form in forms:
            source_reverse_index[f"constructive-form:{form['id']}"] = list(
                dict.fromkeys([form["occurrence_id"], *form["source_ids"]])
            )
        for closure in translations:
            source_reverse_index[f"constructive-closure:{closure['id']}"] = list(
                dict.fromkeys([closure["occurrence_id"], *closure["source_ids"]])
            )
        for comparison in comparisons:
            source_reverse_index[
                f"constructive-comparison:{comparison['id']}"
            ] = list(
                dict.fromkeys(
                    [comparison["occurrence_id"], *comparison["source_ids"]]
                )
            )
        projection = ConstructiveFieldProjection(
            generated_at=utcnow(),
            forms=forms,
            translations=translations,
            comparisons=comparisons,
            stats=stats,
            source_reverse_index=source_reverse_index,
        ).model_dump(mode="json")
        self.store.set_state("constructive_field_projection", projection)
        return projection
