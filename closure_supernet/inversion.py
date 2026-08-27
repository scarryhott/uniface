from __future__ import annotations

import json
import math
import uuid
from decimal import Decimal
from typing import Any, TYPE_CHECKING

from .inversion_models import (
    DemonConstructionCreate,
    EntanglementConstructionCreate,
    HairConstructionKind,
    InversionFieldProjection,
    LocalRelationCreate,
    LocalRelationEvaluation,
    SingularityConstructionCreate,
    SuperpositionConstructionCreate,
)
from .inversion_store import InversionStore, utcnow
from .models import EvidenceStatus, Verdict
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


D = Decimal
ZERO = D(0)
ONE = D(1)
TWO = D(2)
THREE = D(3)


def _dstr(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _matrix_strings(matrix: list[list[Decimal]]) -> list[list[str]]:
    return [[_dstr(value) for value in row] for row in matrix]


def _vector_strings(vector: list[Decimal]) -> list[str]:
    return [_dstr(value) for value in vector]


def _zero_matrix() -> list[list[Decimal]]:
    return [[ZERO for _ in range(3)] for _ in range(3)]


def _identity() -> list[list[Decimal]]:
    return [[ONE if row == col else ZERO for col in range(3)] for row in range(3)]


def _transpose(matrix: list[list[Decimal]]) -> list[list[Decimal]]:
    return [[matrix[col][row] for col in range(3)] for row in range(3)]


def _add(left: list[list[Decimal]], right: list[list[Decimal]]) -> list[list[Decimal]]:
    return [[left[row][col] + right[row][col] for col in range(3)] for row in range(3)]


def _sub(left: list[list[Decimal]], right: list[list[Decimal]]) -> list[list[Decimal]]:
    return [[left[row][col] - right[row][col] for col in range(3)] for row in range(3)]


def _scale(value: Decimal, matrix: list[list[Decimal]]) -> list[list[Decimal]]:
    return [[value * entry for entry in row] for row in matrix]


def _neg(matrix: list[list[Decimal]]) -> list[list[Decimal]]:
    return _scale(-ONE, matrix)


def _matmul(left: list[list[Decimal]], right: list[list[Decimal]]) -> list[list[Decimal]]:
    return [
        [
            sum((left[row][inner] * right[inner][col] for inner in range(3)), ZERO)
            for col in range(3)
        ]
        for row in range(3)
    ]


def _trace(matrix: list[list[Decimal]]) -> Decimal:
    return sum((matrix[index][index] for index in range(3)), ZERO)


def _frob_sq(matrix: list[list[Decimal]]) -> Decimal:
    return sum((entry * entry for row in matrix for entry in row), ZERO)


def _vector_add(left: list[Decimal], right: list[Decimal]) -> list[Decimal]:
    return [left[index] + right[index] for index in range(3)]


def _vector_scale(value: Decimal, vector: list[Decimal]) -> list[Decimal]:
    return [value * entry for entry in vector]


def _cross(left: list[Decimal], right: list[Decimal]) -> list[Decimal]:
    return [
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    ]


def _axial(vector: list[Decimal]) -> list[list[Decimal]]:
    x, y, z = vector
    return [
        [ZERO, -z, y],
        [z, ZERO, -x],
        [-y, x, ZERO],
    ]


def _hair_vector(hair_part: list[list[Decimal]]) -> list[Decimal]:
    return [hair_part[2][1], hair_part[0][2], hair_part[1][0]]


def _close(left: Decimal, right: Decimal, tolerance: Decimal) -> bool:
    return abs(left - right) <= tolerance


def _vector_close(left: list[Decimal], right: list[Decimal], tolerance: Decimal) -> bool:
    return all(_close(left[index], right[index], tolerance) for index in range(3))


def _matrix_close(
    left: list[list[Decimal]], right: list[list[Decimal]], tolerance: Decimal
) -> bool:
    return all(
        _close(left[row][col], right[row][col], tolerance)
        for row in range(3)
        for col in range(3)
    )


def _matrix_zero(matrix: list[list[Decimal]], tolerance: Decimal) -> bool:
    return _matrix_close(matrix, _zero_matrix(), tolerance)


def _vector_zero(vector: list[Decimal], tolerance: Decimal) -> bool:
    return _vector_close(vector, [ZERO, ZERO, ZERO], tolerance)


def _sum_matrices(matrices: list[list[list[Decimal]]]) -> list[list[Decimal]]:
    result = _zero_matrix()
    for matrix in matrices:
        result = _add(result, matrix)
    return result


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in values if str(item)))


class InversionSelfLimitManager:
    """Representation-free executable chart of NRRF795/796.

    The Lean modules carry the uniqueness theorems. This manager validates finite
    submitted matrices and records their source-reversible derived readings.
    """

    def __init__(self, runtime: "ClosureSupernetRuntime", store: InversionStore):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_readings": ["NRRF795", "NRRF796"],
            "canonical_runtime_operation": "integrate",
            "adapter_label": "inversion",
            "representation_required": False,
            "prediction_representation_independent_under_formal_conditions": True,
            "return_inversion": "-transpose",
            "return_inversion_forced_under_declared_conditions": True,
            "scale_reading": "divergence/trace",
            "hair_reading": "normalized inverse axial vector of the skew sector",
            "coordinate_curl_chart_available": True,
            "neutral_residue": "symmetric traceless sector",
            "self_limit_chart": "Frobenius-squared orthogonal decomposition",
            "one_hair_reading_under_declared_conditions": True,
            "phenomena_are_scoped_constructions": True,
            "physical_law_claimed": False,
            "runtime_is_formal_proof": False,
            "determination_issues_truth": False,
        }

    @staticmethod
    def evaluate_relation(
        matrix: list[list[Decimal]], tolerance: Decimal
    ) -> LocalRelationEvaluation:
        transpose = _transpose(matrix)
        return_inversion = _neg(transpose)
        return_inversion_twice = _neg(_transpose(return_inversion))

        return_symmetric = _scale(ONE / TWO, _add(matrix, transpose))
        hair_part = _scale(ONE / TWO, _sub(matrix, transpose))
        divergence = _trace(matrix)
        scale_part = _scale(divergence / THREE, _identity())
        neutral_part = _sub(return_symmetric, scale_part)
        reconstruction = _add(_add(scale_part, hair_part), neutral_part)

        normalized_hair = _hair_vector(hair_part)
        coordinate_curl = _vector_scale(TWO, normalized_hair)
        axial_reconstruction = _axial(normalized_hair)

        total_content = _frob_sq(matrix)
        scale_content = _frob_sq(scale_part)
        hair_content = _frob_sq(hair_part)
        neutral_content = _frob_sq(neutral_part)
        self_limit_sum = scale_content + hair_content + neutral_content

        neutral_zero = _matrix_zero(neutral_part, tolerance)
        scale_zero = _matrix_zero(scale_part, tolerance)
        hair_zero = _matrix_zero(hair_part, tolerance)
        pure_scale = hair_zero and neutral_zero
        pure_hair = scale_zero and neutral_zero
        scale_saturation = _close(total_content, scale_content, tolerance) and pure_scale
        hair_saturation = _close(total_content, hair_content, tolerance) and pure_hair
        joint_saturation = _close(total_content, scale_content + hair_content, tolerance)

        return LocalRelationEvaluation(
            relation=_matrix_strings(matrix),
            return_inversion=_matrix_strings(return_inversion),
            return_inversion_involutive=_matrix_close(
                return_inversion_twice, matrix, tolerance
            ),
            return_symmetric_part=_matrix_strings(return_symmetric),
            hair_part=_matrix_strings(hair_part),
            scale_part=_matrix_strings(scale_part),
            neutral_part=_matrix_strings(neutral_part),
            reconstruction=_matrix_strings(reconstruction),
            reconstruction_exact=_matrix_close(reconstruction, matrix, tolerance),
            divergence=_dstr(divergence),
            normalized_hair=_vector_strings(normalized_hair),
            coordinate_curl=_vector_strings(coordinate_curl),
            axial_reconstruction_exact=_matrix_close(
                axial_reconstruction, hair_part, tolerance
            ),
            divergence_reversed_by_inversion=_close(
                _trace(return_inversion), -divergence, tolerance
            ),
            hair_preserved_by_inversion=_vector_close(
                _hair_vector(_scale(ONE / TWO, _sub(return_inversion, _transpose(return_inversion)))),
                normalized_hair,
                tolerance,
            ),
            hair_sector_fixed=_matrix_close(
                _neg(_transpose(hair_part)), hair_part, tolerance
            ),
            return_symmetric_sector_anti_fixed=_matrix_close(
                _neg(_transpose(return_symmetric)), _neg(return_symmetric), tolerance
            ),
            neutral_sector_anti_fixed=_matrix_close(
                _neg(_transpose(neutral_part)), _neg(neutral_part), tolerance
            ),
            total_content=_dstr(total_content),
            scale_content=_dstr(scale_content),
            hair_content=_dstr(hair_content),
            neutral_content=_dstr(neutral_content),
            self_limit_sum=_dstr(self_limit_sum),
            self_limit_exact=_close(total_content, self_limit_sum, tolerance),
            self_limit_inversion_invariant=_close(
                _frob_sq(return_inversion), total_content, tolerance
            ),
            divergence_within_self_limit=scale_content <= total_content + tolerance,
            hair_within_self_limit=hair_content <= total_content + tolerance,
            scale_saturation=scale_saturation,
            hair_saturation=hair_saturation,
            joint_readings_saturate=joint_saturation,
            joint_saturation_iff_neutral_zero=joint_saturation == neutral_zero,
            pure_scale=pure_scale,
            pure_hair=pure_hair,
            neutral_zero=neutral_zero,
            neutral_nonzero=not neutral_zero,
        )

    def _source_context(
        self, source_event_id: str | None, source_ids: list[str]
    ) -> tuple[list[str], list[str]]:
        exact_sources = list(source_ids)
        parents: list[str] = []
        if source_event_id is not None:
            event = self.runtime.supernet_store.get_event(source_event_id)
            exact_sources.extend(event["exact_source_ids"])
            parents.append(source_event_id)
        return _unique(exact_sources), parents

    async def create_relation(self, data: LocalRelationCreate) -> dict[str, Any]:
        relation_id = str(uuid.uuid4())
        evaluation = self.evaluate_relation(data.matrix, data.tolerance)
        source_ids, parents = self._source_context(data.source_event_id, data.source_ids)
        exact_text = json.dumps(
            {
                "NRRF796": "self-limit inversion equality one hair closure ball",
                "name": data.name,
                "matrix": _matrix_strings(data.matrix),
                "return_inversion": evaluation.return_inversion,
                "divergence": evaluation.divergence,
                "normalized_hair": evaluation.normalized_hair,
                "neutral_part": evaluation.neutral_part,
                "self_limit": evaluation.self_limit_sum,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="representation-free self-limit inversion relation",
                language_label="NRRF795/796 finite local-relation chart",
                source_id="inversion-self-limit-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "derive -transpose return inversion",
                    "derive scale hair neutral decomposition",
                    "check exact self-limit content",
                    "retain one normalized hair channel",
                ],
                constraints=[
                    "finite 3x3 real-matrix runtime chart",
                    "Frobenius-squared content is an executable chart",
                    "physical realization remains OPEN",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF795",
                    "NRRF796",
                    "return inversion",
                    "self limit",
                    "one hair",
                    "ball hair neutral",
                ],
                causal_predecessor_ids=parents,
                parent_event_ids=parents,
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="inversion",
                external_key=data.external_key or f"inversion:relation:{relation_id}",
                metadata={
                    **data.metadata,
                    "relation_id": relation_id,
                    "formal_readings": ["NRRF795", "NRRF796"],
                    "evaluation": evaluation.model_dump(mode="json"),
                    "source_ids": source_ids,
                    "representation_required": False,
                    "physical_law_claimed": False,
                    "runtime_is_formal_proof": False,
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
            "source_event_id": data.source_event_id,
            "perspective_id": data.perspective_id,
            "problem_id": data.problem_id,
            "payload": {
                "matrix": _matrix_strings(data.matrix),
                "tolerance": _dstr(data.tolerance),
            },
            "evaluation": evaluation.model_dump(mode="json"),
            "source_ids": source_ids,
            "metadata": {
                **data.metadata,
                "representation_required": False,
                "physical_law_claimed": False,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        stored = self.store.create_relation(row)
        self.runtime.supernet_integrator.determine(
            receipt["event_id"],
            actor_id=data.authored_by,
            rigidity_scope=[
                "return inversion",
                "scale reading",
                "hair reading",
                "neutral residue",
                "self-limit content",
            ],
            rigidity_receipt={
                "return_inversion_forced_under_declared_conditions": True,
                "unique_hair_reading_under_declared_conditions": True,
                "reconstruction_exact": evaluation.reconstruction_exact,
                "self_limit_exact": evaluation.self_limit_exact,
                "prior_reading_complete": True,
                "forced_isolation": False,
                "representation_used": False,
                "runtime_is_formal_proof": False,
            },
            determined_form={
                "relation_id": relation_id,
                "return_inversion": evaluation.return_inversion,
                "scale_part": evaluation.scale_part,
                "hair_part": evaluation.hair_part,
                "neutral_part": evaluation.neutral_part,
                "normalized_hair": evaluation.normalized_hair,
                "self_limit": evaluation.self_limit_sum,
                "canonical_representation": None,
                "canonical_presentation": None,
            },
            unitary_path_partition={
                "path": [
                    "relation",
                    "-transpose return",
                    "scale/hair/neutral sectors",
                    "self-limit equality",
                    "returned successor potential",
                ],
                "partition": {
                    "anti-fixed": ["scale", "neutral"],
                    "fixed": ["hair"],
                },
            },
            reason=(
                "The submitted relation has one return inversion and one exact "
                "scale/hair/neutral self-limit reading in this finite chart"
            ),
        )
        self.runtime.supernet_integrator.transition(
            receipt["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason=(
                    "The representation-free decomposition returns as successor "
                    "potential without making a physical-law or truth claim"
                ),
                actor_id=data.authored_by,
                returned_resource_ids=[relation_id],
                successor_potential=[
                    {
                        "form_type": "self-limit-inversion-relation",
                        "relation_id": relation_id,
                        "neutral_nonzero": evaluation.neutral_nonzero,
                        "physical_realization": "OPEN",
                    }
                ],
                metadata={
                    "nrrf795": True,
                    "nrrf796": True,
                    "representation_required": False,
                    "physical_law_claimed": False,
                    "truth_issued": False,
                },
            ),
        )
        self.projection()
        return self.store.get_relation(stored["id"])

    @staticmethod
    def evaluate_entanglement(data: EntanglementConstructionCreate) -> dict[str, Any]:
        left = _axial(data.left_hair)
        right = _axial(data.right_hair)
        commutator = _sub(_matmul(left, right), _matmul(right, left))
        reverse = _sub(_matmul(right, left), _matmul(left, right))
        expected = _axial(_cross(data.left_hair, data.right_hair))
        relation = InversionSelfLimitManager.evaluate_relation(commutator, data.tolerance)
        commutes = _matrix_zero(commutator, data.tolerance)
        return {
            "left_hair": _vector_strings(data.left_hair),
            "right_hair": _vector_strings(data.right_hair),
            "order_defect": _matrix_strings(commutator),
            "order_defect_hair": relation.normalized_hair,
            "order_defect_equals_axial_cross": _matrix_close(
                commutator, expected, data.tolerance
            ),
            "source_free": _close(_trace(commutator), ZERO, data.tolerance),
            "pure_hair": relation.pure_hair,
            "antisymmetric_in_pair": _matrix_close(
                reverse, _neg(commutator), data.tolerance
            ),
            "commutes": commutes,
            "zero_exactly_when_commuting_for_axial_inputs": (
                _matrix_zero(commutator, data.tolerance) == commutes
            ),
            "genuinely_nonzero": not commutes,
            "construction_scope": "order defect of two submitted axial translations",
            "physical_entanglement_claimed": False,
            "truth_issued": False,
        }

    @staticmethod
    def evaluate_superposition(data: SuperpositionConstructionCreate) -> dict[str, Any]:
        total = _sum_matrices(data.summands)
        summand_evaluations = [
            InversionSelfLimitManager.evaluate_relation(matrix, data.tolerance)
            for matrix in data.summands
        ]
        total_evaluation = InversionSelfLimitManager.evaluate_relation(
            total, data.tolerance
        )
        summed_hair = [ZERO, ZERO, ZERO]
        for evaluation in summand_evaluations:
            summed_hair = _vector_add(
                summed_hair,
                [D(value) for value in evaluation.normalized_hair],
            )
        total_hair = [D(value) for value in total_evaluation.normalized_hair]
        some_input_hair = any(
            not _vector_zero([D(value) for value in item.normalized_hair], data.tolerance)
            for item in summand_evaluations
        )
        destructive = _vector_zero(total_hair, data.tolerance) and some_input_hair
        total_nonzero = not _matrix_zero(total, data.tolerance)
        return {
            "summands": [_matrix_strings(matrix) for matrix in data.summands],
            "sum": _matrix_strings(total),
            "summand_hairs": [item.normalized_hair for item in summand_evaluations],
            "summed_hair": _vector_strings(summed_hair),
            "sum_hair": total_evaluation.normalized_hair,
            "hair_linearity": _vector_close(summed_hair, total_hair, data.tolerance),
            "destructive_hair_interference": destructive,
            "neutral_residue_nonzero": total_evaluation.neutral_nonzero,
            "reading_cancellation_not_state_annihilation": destructive and total_nonzero,
            "sum_relation": total_evaluation.model_dump(mode="json"),
            "construction_scope": "linearity of the one submitted matrix hair chart",
            "physical_superposition_claimed": False,
            "truth_issued": False,
        }

    @staticmethod
    def evaluate_singularity(data: SingularityConstructionCreate) -> dict[str, Any]:
        angle = float(data.angle_radians)
        cosine = math.cos(angle)
        if not data.at_seam and abs(cosine) <= float(data.tolerance):
            raise ValueError(
                "angle lies at the ratio seam; set at_seam=true to use the seam-field construction"
            )
        if data.at_seam:
            ratio: Decimal | None = None
            hair = [ZERO, ZERO, ZERO]
        else:
            ratio = D(str(math.tan(angle)))
            hair = _vector_scale(ratio, data.direction)
        matrix = _axial(hair)
        cross_with_direction = _cross(hair, data.direction)
        return {
            "direction": _vector_strings(data.direction),
            "angle_radians": _dstr(data.angle_radians),
            "at_seam": data.at_seam,
            "tangent_ratio": None if ratio is None else _dstr(ratio),
            "hair": _vector_strings(hair),
            "hair_matrix": _matrix_strings(matrix),
            "one_hair_direction": _vector_zero(cross_with_direction, data.tolerance),
            "ratio_reading_empty_at_seam": data.at_seam,
            "seam_field_hair_extinguished": data.at_seam and _vector_zero(hair, data.tolerance),
            "seam_symbol_required_to_complete_ratio_reading": data.at_seam,
            "seam_chart_value_is_not_a_finite_ratio_solution": data.at_seam,
            "single_sample_does_not_prove_unbounded_approach": True,
            "construction_scope": "one tangent-multiple hair direction with a separately typed seam field",
            "physical_singularity_claimed": False,
            "truth_issued": False,
        }

    @staticmethod
    def evaluate_demon(data: DemonConstructionCreate) -> dict[str, Any]:
        source = InversionSelfLimitManager.evaluate_relation(
            data.neutral_input, data.tolerance
        )
        output = InversionSelfLimitManager.evaluate_relation(
            data.submitted_output, data.tolerance
        )
        input_is_neutral = (
            source.neutral_nonzero or source.neutral_zero
        ) and source.divergence == "0" and all(
            value == "0" for value in source.normalized_hair
        ) and _matrix_close(
            data.neutral_input,
            [[D(value) for value in row] for row in source.neutral_part],
            data.tolerance,
        )
        hair_preserved = source.normalized_hair == output.normalized_hair
        source_preserved = _close(
            D(source.divergence), D(output.divergence), data.tolerance
        )
        output_is_neutral = output.divergence == "0" and all(
            value == "0" for value in output.normalized_hair
        ) and _matrix_close(
            data.submitted_output,
            [[D(value) for value in row] for row in output.neutral_part],
            data.tolerance,
        )
        premises_hold = input_is_neutral and hair_preserved and source_preserved
        no_gain = output_is_neutral and output.divergence == "0"
        return {
            "neutral_input": _matrix_strings(data.neutral_input),
            "submitted_output": _matrix_strings(data.submitted_output),
            "input_is_neutral": input_is_neutral,
            "hair_preserved_on_submitted_witness": hair_preserved,
            "source_preserved_on_submitted_witness": source_preserved,
            "premises_hold_on_submitted_witness": premises_hold,
            "output_is_neutral": output_is_neutral,
            "source_gain_zero": no_gain,
            "conditional_no_gain_holds": (not premises_hold) or no_gain,
            "construction_scope": "one submitted input/output witness, not a universal linear-operator proof",
            "physical_thermodynamic_claimed": False,
            "truth_issued": False,
        }

    async def _create_construction(
        self,
        *,
        kind: HairConstructionKind,
        name: str,
        authored_by: str,
        source_event_id: str | None,
        source_ids: list[str],
        payload: dict[str, Any],
        evaluation: dict[str, Any],
        metadata: dict[str, Any],
        external_key: str | None,
    ) -> dict[str, Any]:
        construction_id = str(uuid.uuid4())
        exact_sources, parents = self._source_context(source_event_id, source_ids)
        exact_text = json.dumps(
            {
                "NRRF796": kind.value,
                "name": name,
                "payload": payload,
                "evaluation": evaluation,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=authored_by,
                form_label=f"one-hair construction: {kind.value}",
                language_label="NRRF796 scoped construction",
                source_id="inversion-self-limit-supernet",
                capabilities=["read construction through one normalized hair channel"],
                constraints=[
                    "construction name is definition-scoped",
                    "no external physical claim is issued",
                    "physical realization remains OPEN",
                ],
                relation_hints=["NRRF796", "one hair", kind.value],
                causal_predecessor_ids=parents,
                parent_event_ids=parents,
                affected_perspectives=[authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="inversion",
                external_key=external_key or f"inversion:construction:{construction_id}",
                metadata={
                    **metadata,
                    "construction_id": construction_id,
                    "construction_kind": kind.value,
                    "formal_reading": "NRRF796",
                    "evaluation": evaluation,
                    "source_ids": exact_sources,
                    "physical_law_claimed": False,
                    "runtime_is_formal_proof": False,
                    "truth_issued": False,
                },
            )
        )
        row = {
            "id": construction_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "kind": kind.value,
            "name": name,
            "authored_by": authored_by,
            "source_event_id": source_event_id,
            "payload": payload,
            "evaluation": evaluation,
            "source_ids": exact_sources,
            "metadata": {
                **metadata,
                "physical_law_claimed": False,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        stored = self.store.create_construction(row)
        self.runtime.supernet_integrator.determine(
            receipt["event_id"],
            actor_id=authored_by,
            rigidity_scope=[kind.value, "construction definition"],
            rigidity_receipt={
                "construction_definition_complete": True,
                "one_hair_channel": True,
                "physical_realization_open": True,
                "forced_isolation": False,
            },
            determined_form={
                "construction_id": construction_id,
                "construction_kind": kind.value,
                "evaluation": evaluation,
                "canonical_physical_interpretation": None,
                "canonical_presentation": None,
            },
            unitary_path_partition={
                "path": ["source construction", "one hair reading", "scoped result", "reopening"],
                "partition": [kind.value, "physical realization OPEN"],
            },
            reason=(
                "The named construction has one result under its submitted definition; "
                "no external physical interpretation is selected"
            ),
        )
        self.runtime.supernet_integrator.transition(
            receipt["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The scoped hair construction returns without issuing physical or universal truth",
                actor_id=authored_by,
                returned_resource_ids=[construction_id],
                successor_potential=[
                    {
                        "form_type": "one-hair-construction",
                        "construction_id": construction_id,
                        "kind": kind.value,
                        "physical_realization": "OPEN",
                    }
                ],
                metadata={
                    "nrrf796": True,
                    "physical_law_claimed": False,
                    "truth_issued": False,
                },
            ),
        )
        self.projection()
        return self.store.get_construction(stored["id"])

    async def create_entanglement(
        self, data: EntanglementConstructionCreate
    ) -> dict[str, Any]:
        return await self._create_construction(
            kind=HairConstructionKind.ENTANGLEMENT_ORDER_DEFECT,
            name=data.name,
            authored_by=data.authored_by,
            source_event_id=data.source_event_id,
            source_ids=data.source_ids,
            payload={
                "left_hair": _vector_strings(data.left_hair),
                "right_hair": _vector_strings(data.right_hair),
                "tolerance": _dstr(data.tolerance),
            },
            evaluation=self.evaluate_entanglement(data),
            metadata=data.metadata,
            external_key=data.external_key,
        )

    async def create_superposition(
        self, data: SuperpositionConstructionCreate
    ) -> dict[str, Any]:
        return await self._create_construction(
            kind=HairConstructionKind.SUPERPOSITION_HAIR_SUM,
            name=data.name,
            authored_by=data.authored_by,
            source_event_id=data.source_event_id,
            source_ids=data.source_ids,
            payload={
                "summands": [_matrix_strings(matrix) for matrix in data.summands],
                "tolerance": _dstr(data.tolerance),
            },
            evaluation=self.evaluate_superposition(data),
            metadata=data.metadata,
            external_key=data.external_key,
        )

    async def create_singularity(
        self, data: SingularityConstructionCreate
    ) -> dict[str, Any]:
        return await self._create_construction(
            kind=HairConstructionKind.SINGULARITY_SEAM_HAIR,
            name=data.name,
            authored_by=data.authored_by,
            source_event_id=data.source_event_id,
            source_ids=data.source_ids,
            payload={
                "direction": _vector_strings(data.direction),
                "angle_radians": _dstr(data.angle_radians),
                "at_seam": data.at_seam,
                "tolerance": _dstr(data.tolerance),
            },
            evaluation=self.evaluate_singularity(data),
            metadata=data.metadata,
            external_key=data.external_key,
        )

    async def create_demon(self, data: DemonConstructionCreate) -> dict[str, Any]:
        return await self._create_construction(
            kind=HairConstructionKind.DEMON_NEUTRAL_NO_GAIN,
            name=data.name,
            authored_by=data.authored_by,
            source_event_id=data.source_event_id,
            source_ids=data.source_ids,
            payload={
                "neutral_input": _matrix_strings(data.neutral_input),
                "submitted_output": _matrix_strings(data.submitted_output),
                "tolerance": _dstr(data.tolerance),
            },
            evaluation=self.evaluate_demon(data),
            metadata=data.metadata,
            external_key=data.external_key,
        )

    def projection(self) -> dict[str, Any]:
        relations = self.store.list_relations()
        constructions = self.store.list_constructions()
        source_reverse_index: dict[str, list[str]] = {}
        for item in relations:
            source_reverse_index[f"inversion:relation:{item['id']}"] = _unique(
                [item["occurrence_id"], *item["source_ids"]]
            )
        for item in constructions:
            source_reverse_index[f"inversion:construction:{item['id']}"] = _unique(
                [item["occurrence_id"], *item["source_ids"]]
            )
        projection = InversionFieldProjection(
            generated_at=utcnow(),
            relations=relations,
            constructions=constructions,
            stats=self.store.stats(),
            source_reverse_index=source_reverse_index,
        ).model_dump(mode="json")
        self.store.set_state("inversion_field_projection", projection)
        return projection
