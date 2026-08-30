"""Closure-derived translational-truth axiometry.

This module deliberately starts with *visual existence*, not with a quotient,
selector, metric, topology, or externally chosen interface.  Relative truth is
first evaluated between things that visually exist.  Only witnessed truth is
promoted to an axiom.  The admitted axiometry derives a joint truth reading;
NRRF840 closure is then the preimage of the image of a seed under that reading,
and natural forms are precisely its saturated truth fibres.

The external renderer has one role: transporting an already-derived interface
natural form to pixels or another presentation medium.  It cannot witness
truth, add an axiom, identify two forms, or admit a natural form.
"""

from __future__ import annotations

import hashlib
import json
from collections import deque
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


PROTOCOL = "TRANSLATIONAL_TRUTH_AXIOMETRY"
SCHEMA = "closure.supernet/translational-truth-axiometry-v3"
NRRF840_MODULE = (
    "NRRF840ClosureDerivedFromTranslationalTruthAxiometryNotAnExternalLimit"
)
NRRF840_CRITERION = (
    "x in visClosure(vis, A) iff exists a in A, for every observer o, "
    "vis(o, x) = vis(o, a)"
)
JOINT_TRUTH_OBSERVER = "TRANSLATIONAL_TRUTH_JOINT_READING"


class TruthVerdict(str, Enum):
    """A relative truth reading before closure admission."""

    TRUE = "TRUE"
    FALSE = "FALSE"
    OPEN = "OPEN"


class WitnessStatus(str, Enum):
    """Whether a proposed relative translation has a truth witness."""

    WITNESSED = "WITNESSED"
    NOT_WITNESSED = "NOT_WITNESSED"


class WitnessKind(str, Enum):
    IDENTITY = "IDENTITY"
    RELATIVE_TRANSLATION = "RELATIVE_TRANSLATION"


class RendererRole(str, Enum):
    TRANSPORT_ONLY = "TRANSPORT_ONLY"


def _canonical(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {
            str(key): _canonical(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (set, frozenset)):
        items = [_canonical(item) for item in value]
        return sorted(items, key=lambda item: _canonical_json(item))
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    return str(value)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _canonical(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _stable_id(prefix: str, value: Any) -> str:
    digest = hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def _strict_bool(value: Any, *, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    raise TypeError(f"{field_name} must be a boolean, got {value!r}")


class FrozenMapping(Mapping[str, Any]):
    """Small recursively immutable mapping used by derived receipts."""

    __slots__ = ("_items", "_lookup")

    def __init__(self, value: Mapping[str, Any]) -> None:
        items = tuple(sorted(value.items(), key=lambda item: str(item[0])))
        self._items = items
        self._lookup = dict(items)

    def __getitem__(self, key: str) -> Any:
        return self._lookup[key]

    def __iter__(self):
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __deepcopy__(self, memo: dict[int, Any]) -> FrozenMapping:
        return self

    def __repr__(self) -> str:
        return f"FrozenMapping({dict(self._items)!r})"


def _freeze(value: Any) -> Any:
    if isinstance(value, FrozenMapping):
        return value
    if isinstance(value, Mapping):
        return FrozenMapping(
            {str(key): _freeze(item) for key, item in value.items()}
        )
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted((_freeze(item) for item in value), key=_canonical_json))
    return value


def _to_dict(value: Any) -> dict[str, Any]:
    """Serialize one public dataclass as plain JSON-compatible data."""

    return _canonical(asdict(value))


def _strings(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, Mapping):
        values: Iterable[Any] = value.values()
    else:
        try:
            values = iter(value)
        except TypeError:
            values = iter((value,))
    return tuple(dict.fromkeys(str(item) for item in values if str(item)))


def _verdict(value: Any) -> TruthVerdict:
    if isinstance(value, TruthVerdict):
        return value
    if value is True:
        return TruthVerdict.TRUE
    if value is False:
        return TruthVerdict.FALSE
    try:
        return TruthVerdict(str(value).upper())
    except ValueError as exc:
        raise ValueError(f"unsupported truth verdict: {value!r}") from exc


@dataclass(frozen=True)
class VisualForm:
    """One explicitly present form in visual existence."""

    id: str
    state: Mapping[str, Any] = field(default_factory=dict)
    existence_provenance: tuple[str, ...] = ()
    source_returns: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("a visual form requires a non-empty id")
        object.__setattr__(self, "state", _freeze(self.state))
        provenance = _strings(self.existence_provenance)
        if not provenance:
            provenance = (f"visual-existence:{self.id}",)
        object.__setattr__(self, "existence_provenance", provenance)
        source_returns = _strings(self.source_returns)
        if not source_returns:
            source_returns = provenance
        object.__setattr__(self, "source_returns", source_returns)

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class VisualExistence:
    forms: tuple[VisualForm, ...]

    @property
    def form_ids(self) -> tuple[str, ...]:
        return tuple(form.id for form in self.forms)

    def form(self, form_id: str) -> VisualForm:
        for item in self.forms:
            if item.id == form_id:
                return item
        raise KeyError(form_id)

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class ConditionWitness:
    """Explicit evidence for one conjunct of closure admission."""

    witnessed: bool
    provenance: tuple[str, ...] = ()
    basis: str = "EXPLICIT_WITNESS"

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "witnessed",
            _strict_bool(self.witnessed, field_name="condition witness"),
        )
        object.__setattr__(self, "provenance", _strings(self.provenance))


@dataclass(frozen=True)
class VisualEquation:
    """A deterministic visual equation connecting two existing forms."""

    id: str
    source: str
    target: str
    equation: str
    deterministic: bool = True
    source_returns: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id or not self.source or not self.target or not self.equation:
            raise ValueError("visual equation requires id, endpoints, and equation")
        object.__setattr__(
            self,
            "deterministic",
            _strict_bool(
                self.deterministic,
                field_name="visual equation deterministic",
            ),
        )
        object.__setattr__(self, "source_returns", _strings(self.source_returns))
        provenance = _strings(self.provenance)
        if not provenance:
            provenance = (f"visual-equation:{self.id}",)
        object.__setattr__(self, "provenance", provenance)

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class RelativeTruth:
    """A proposed truth of translation between two visually presented forms."""

    id: str
    source: str
    target: str
    verdict: TruthVerdict
    provenance: tuple[str, ...] = ()
    statement: str | None = None
    source_returns: tuple[str, ...] = ()
    visual_equation: VisualEquation | Mapping[str, Any] | None = None
    compatibility: ConditionWitness | Mapping[str, Any] | bool = False
    closure_explicit: ConditionWitness | Mapping[str, Any] | bool | None = None

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("relative truth requires a non-empty id")
        if not self.source or not self.target:
            raise ValueError("relative truth requires source and target ids")
        object.__setattr__(self, "verdict", _verdict(self.verdict))
        object.__setattr__(self, "source_returns", _strings(self.source_returns))
        provenance = _strings(self.provenance)
        if not provenance:
            provenance = (f"relative-truth:{self.id}",)
        object.__setattr__(self, "provenance", provenance)
        equation = _coerce_visual_equation(
            self.visual_equation,
            truth_id=self.id,
            source=self.source,
            target=self.target,
        )
        object.__setattr__(self, "visual_equation", equation)
        compatibility = _coerce_condition(
            self.compatibility,
            default_provenance=f"compatibility:{self.id}",
        )
        object.__setattr__(self, "compatibility", compatibility)
        equation_matches = bool(
            equation is not None
            and equation.deterministic
            and equation.source == self.source
            and equation.target == self.target
        )
        explicit_input = self.closure_explicit
        if explicit_input is None:
            closure_explicit = ConditionWitness(
                witnessed=equation_matches,
                provenance=(
                    (
                        f"closure-explicit-from-equation:{equation.id}",
                        *equation.provenance,
                    )
                    if equation_matches and equation is not None
                    else ()
                ),
                basis="DETERMINISTIC_VISUAL_EQUATION",
            )
        else:
            claimed_explicit = _coerce_condition(
                explicit_input,
                default_provenance=f"closure-explicit:{self.id}",
            )
            if claimed_explicit.witnessed and equation_matches and equation is not None:
                closure_explicit = ConditionWitness(
                    witnessed=True,
                    provenance=tuple(
                        dict.fromkeys(
                            (
                                *claimed_explicit.provenance,
                                equation.id,
                                *equation.provenance,
                            )
                        )
                    ),
                    basis=(
                        "EXPLICIT_WITNESS_AND_DETERMINISTIC_VISUAL_EQUATION"
                    ),
                )
            else:
                closure_explicit = ConditionWitness(
                    witnessed=False,
                    provenance=claimed_explicit.provenance,
                    basis=(
                        "REJECTED_WITHOUT_MATCHING_DETERMINISTIC_VISUAL_EQUATION"
                        if claimed_explicit.witnessed
                        else claimed_explicit.basis
                    ),
                )
        object.__setattr__(self, "closure_explicit", closure_explicit)

    @property
    def meets_visual_existence(self) -> bool:
        """The admission predicate: compatible AND closure-explicit."""

        return (
            self.compatibility.witnessed
            and self.has_valid_visual_equation
            and self.closure_explicit.witnessed
        )

    @property
    def has_valid_visual_equation(self) -> bool:
        equation = self.visual_equation
        return bool(
            equation is not None
            and equation.deterministic
            and equation.source == self.source
            and equation.target == self.target
        )

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class VisualMirrorConstraint:
    """One relation presented by the semantic UI as a truth constraint."""

    id: str
    truth_id: str
    source: str
    target: str
    verdict: TruthVerdict
    statement: str | None
    visual_equation_id: str | None
    endpoints_visually_exist: bool
    source_return_provenance: tuple[str, ...]
    presentation_status: str


@dataclass(frozen=True)
class PerspectiveVisualMirror:
    """The UI-semantic visualization in which truth is constrained.

    This is not the HTML/SVG renderer and not a post-closure dashboard.  It is
    the source-preserving perspectival projection of visual existence and its
    proposed translation equations.  Axiometry can only evaluate constraints
    presented here; without this mirror the Supernet truth relation is OPEN.
    """

    id: str
    form_ids: tuple[str, ...]
    perspective_ids: tuple[str, ...]
    projected_forms: Mapping[str, Mapping[str, Any]]
    constraints: tuple[VisualMirrorConstraint, ...]
    source_return_provenance: tuple[str, ...]
    semantic_observers: tuple[str, ...] = (
        "PERSPECTIVE_FORM",
        "RELATIVE_VISUAL_EQUATION",
    )
    role: str = "METAPHORICAL_FORM_TRANSLATION_AND_TRUTH_CONSTRAINT_SURFACE"
    static_external_network_map: bool = False
    essential_to_supernet_truth: bool = True
    metaphorical_forms_are_semantic: bool = True
    thought_derivation: str = "THOUGHT_IS_CLOSURE_OF_METAPHOR_INTO_RELATIONS"
    without_visualization_status: str = "OPEN"
    participates_in_closure: bool = True
    closes_and_reopens_through_returns: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "projected_forms", _freeze(self.projected_forms))

    def constraint_for(self, truth_id: str) -> VisualMirrorConstraint | None:
        for item in self.constraints:
            if item.truth_id == truth_id:
                return item
        return None

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class RelativeTruthEvaluation:
    truth_id: str
    source: str
    target: str
    verdict: TruthVerdict
    endpoints_exist: bool
    status: WitnessStatus
    reason: str
    witness_id: str | None
    compatible: bool
    closure_explicit: bool
    meets_visual_existence: bool
    closure_admitted: bool


@dataclass(frozen=True)
class TruthWitness:
    """An explicit witness that may generate an equality axiom."""

    id: str
    kind: WitnessKind
    source: str
    target: str
    truth_id: str
    truth_provenance: tuple[str, ...]
    existence_provenance: tuple[str, ...]
    source_return_provenance: tuple[str, ...]
    visual_equation_provenance: tuple[str, ...]
    compatibility_provenance: tuple[str, ...]
    closure_explicit_provenance: tuple[str, ...]
    visual_mirror_provenance: tuple[str, ...]


@dataclass(frozen=True)
class TranslationAxiom:
    """One visual translation axiom promoted from exactly one truth witness."""

    id: str
    source: str
    target: str
    witness_id: str
    truth_id: str
    truth_provenance: tuple[str, ...]
    existence_provenance: tuple[str, ...]
    source_return_provenance: tuple[str, ...]
    visual_equation_provenance: tuple[str, ...]
    compatibility_provenance: tuple[str, ...]
    closure_explicit_provenance: tuple[str, ...]
    visual_mirror_provenance: tuple[str, ...]


@dataclass(frozen=True)
class Axiometry:
    axioms: tuple[TranslationAxiom, ...]
    witness_ids: tuple[str, ...]

    def axiom(self, axiom_id: str) -> TranslationAxiom:
        for item in self.axioms:
            if item.id == axiom_id:
                return item
        raise KeyError(axiom_id)

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class ClosureMeeting:
    """The post-axiometry decision that one visual axiom generates closure."""

    id: str
    axiom_id: str
    witness_id: str
    truth_id: str
    visual_mirror_constraint_id: str
    source: str
    target: str
    compatible: bool
    closure_explicit: bool
    admitted: bool
    basis: str
    provenance: tuple[str, ...]


@dataclass(frozen=True)
class EquivalenceRelation:
    """A closure relation with a finite path back to witnessed axioms."""

    source: str
    target: str
    path: tuple[str, ...]
    axiom_ids: tuple[str, ...]
    witness_ids: tuple[str, ...]
    truth_ids: tuple[str, ...]
    closure_operations: tuple[str, ...]


@dataclass(frozen=True)
class EquivalenceClosure:
    classes: tuple[tuple[str, ...], ...]
    relations: tuple[EquivalenceRelation, ...]

    def relation(self, source: str, target: str) -> EquivalenceRelation | None:
        for item in self.relations:
            if item.source == source and item.target == target:
                return item
        return None


@dataclass(frozen=True)
class ObserverEquality:
    """One observer equation used by the NRRF840 closure criterion."""

    observer_id: str
    member_id: str
    source_form_id: str
    member_reading: str
    source_reading: str
    equal: bool
    provenance: tuple[str, ...]


@dataclass(frozen=True)
class VisClosureMembership:
    """Executable witness of ``x ∈ visClosure vis A`` for a singleton seed."""

    id: str
    member_id: str
    source_form_id: str
    source_return_provenance: tuple[str, ...]
    observer_equalities: tuple[ObserverEquality, ...]
    source_exists: bool = True
    source_in_seed: bool = True
    all_observers_equal: bool = True
    admitted: bool = True
    formal_criterion: str = NRRF840_CRITERION


@dataclass(frozen=True)
class VisClosureProperties:
    """The NRRF840 laws inherited from the preimage/image construction."""

    extensive: bool = True
    monotone: bool = True
    additive: bool = True
    idempotent: bool = True
    least_naturally_admitted_superset: bool = True
    naturally_admitted_closed_under_complement: bool = True
    naturally_admitted_closed_under_arbitrary_unions: bool = True
    naturally_admitted_closed_under_arbitrary_intersections: bool = True
    external_limit_used: bool = False
    unnatural_limit: bool = False


@dataclass(frozen=True)
class DerivedVisualClosure:
    """The finite executable form of NRRF840 ``visClosure``.

    Axiometry first derives one joint translational-truth reading for every
    visually existing form.  Closure is then computed *only* as
    ``preimage(image(A))`` under that reading.  The axiom graph is retained as
    provenance for the reading; it is no longer presented as the definition of
    closure.
    """

    id: str
    visual_mirror_id: str
    observer_ids: tuple[str, ...]
    joint_reading_by_form: Mapping[str, str]
    classes: tuple[tuple[str, ...], ...]
    singleton_closure: Mapping[str, tuple[str, ...]]
    memberships: tuple[VisClosureMembership, ...]
    properties: VisClosureProperties = VisClosureProperties()
    construction: str = "PREIMAGE_OF_IMAGE_OF_JOINT_TRANSLATIONAL_TRUTH_READING"
    formal_module: str = NRRF840_MODULE
    formal_theorems: tuple[str, ...] = (
        "visClosure_eq_reachOp_axiometry",
        "visClosure_eq_preimage_image",
        "visClosure_eq_truth_preimage_image",
        "naturallyAdmitted_iff_derivedTranslationalTruths",
        "isLeast_visClosure",
        "visClosure_not_unnaturalLimit",
    )
    formal_criterion: str = NRRF840_CRITERION
    natural_admission_criterion: str = (
        "form = preimage(image(form)); equivalently, form is a union of "
        "translational-truth fibres"
    )
    closure_matches_axiometry_truth_classes: bool = True
    correspondence_status: str = (
        "EXECUTABLE_RUNTIME_WITNESS_LINKED_TO_NRRF840; "
        "PYTHON_EXECUTION_DOES_NOT_REPROVE_THE_LEAN_THEOREMS"
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "joint_reading_by_form",
            _freeze(self.joint_reading_by_form),
        )
        object.__setattr__(
            self,
            "singleton_closure",
            _freeze(self.singleton_closure),
        )

    def close(self, seed_form_ids: Iterable[str]) -> tuple[str, ...]:
        """Return ``visClosure vis A`` by the exact NRRF840 criterion."""

        seeds = tuple(dict.fromkeys(str(item) for item in seed_form_ids))
        unknown = sorted(set(seeds) - set(self.joint_reading_by_form))
        if unknown:
            raise KeyError(
                "closure seed is outside visual existence: " + ", ".join(unknown)
            )
        seed_readings = {
            self.joint_reading_by_form[item]
            for item in seeds
        }
        return tuple(
            form_id
            for form_id in sorted(self.joint_reading_by_form)
            if self.joint_reading_by_form[form_id] in seed_readings
        )

    def is_naturally_admitted(self, form_ids: Iterable[str]) -> bool:
        """A form is admitted exactly when it is already truth-saturated."""

        members = tuple(sorted(dict.fromkeys(str(item) for item in form_ids)))
        return self.close(members) == members

    def membership(
        self,
        member_id: str,
        source_form_id: str,
    ) -> VisClosureMembership | None:
        for item in self.memberships:
            if (
                item.member_id == member_id
                and item.source_form_id == source_form_id
            ):
                return item
        return None

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class NaturalForm:
    """An equivalence class admitted only after translational-truth closure."""

    id: str
    members: tuple[str, ...]
    truth_provenance: tuple[str, ...]
    axiom_provenance: tuple[str, ...]
    witness_provenance: tuple[str, ...]
    relation_provenance: tuple[tuple[str, str], ...]
    existence_provenance: tuple[str, ...]
    source_return_provenance: tuple[str, ...]
    visual_equation_provenance: tuple[str, ...]
    compatibility_provenance: tuple[str, ...]
    closure_explicit_provenance: tuple[str, ...]
    visual_mirror_provenance: tuple[str, ...]
    factorization_provenance: tuple[str, ...]
    visual_closure_id: str
    vis_closure_membership_witness_ids: tuple[str, ...]
    formal_basis: str = NRRF840_MODULE
    admitted: bool = True
    admission_basis: str = "NRRF840_VIS_CLOSURE_TRANSLATIONAL_TRUTHS"
    derived_within_closure: bool = True

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class ExternalRendererContract:
    role: RendererRole = RendererRole.TRANSPORT_ONLY
    can_present: bool = True
    can_witness_truth: bool = False
    can_generate_axioms: bool = False
    can_admit_forms: bool = False
    can_change_closure: bool = False


EXTERNAL_RENDERER_CONTRACT = ExternalRendererContract()


@dataclass(frozen=True)
class InterfaceNaturalForm:
    """A closed UI reading of the whole derived quotient."""

    id: str
    closure_id: str
    natural_form_ids: tuple[str, ...]
    members: tuple[str, ...]
    render_states: tuple[Mapping[str, Any], ...]
    quotient_render_state: Mapping[str, Mapping[str, Any]]
    closure_projection: Mapping[str, Mapping[str, Any]]
    truth_provenance: tuple[str, ...]
    axiom_provenance: tuple[str, ...]
    witness_provenance: tuple[str, ...]
    factorization_provenance: tuple[str, ...]
    existence_provenance: tuple[str, ...]
    source_return_provenance: tuple[str, ...]
    visual_equation_provenance: tuple[str, ...]
    compatibility_provenance: tuple[str, ...]
    closure_explicit_provenance: tuple[str, ...]
    visual_mirror_provenance: tuple[str, ...]
    visual_mirror_id: str
    visual_closure_id: str
    vis_closure_membership_witness_ids: tuple[str, ...]
    formal_basis: str = NRRF840_MODULE
    formal_criterion: str = NRRF840_CRITERION
    mechanism_role: str = "VISUAL_TRUTH_CONSTRAINT_AND_CLOSURE_RETURN"
    essential_to_supernet_truth: bool = True
    metaphorical_forms_are_semantic: bool = True
    thought_derivation: str = "THOUGHT_IS_CLOSURE_OF_METAPHOR_INTO_RELATIONS"
    without_interface_status: str = "OPEN"
    static_external_network_map: bool = False
    closes_and_reopens_through_returns: bool = True
    closure_internal: bool = True
    admitted: bool = True
    admission_basis: str = "NRRF840_VIS_CLOSURE_TRANSLATIONAL_TRUTHS"
    renderer_contract: ExternalRendererContract = EXTERNAL_RENDERER_CONTRACT

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


@dataclass(frozen=True)
class ClosureDerivation:
    """All stages of visual-existence-to-natural-form derivation."""

    id: str
    visual_existence: VisualExistence
    perspective_visual_mirror: PerspectiveVisualMirror
    relative_truths: tuple[RelativeTruth, ...]
    truth_evaluations: tuple[RelativeTruthEvaluation, ...]
    witnesses: tuple[TruthWitness, ...]
    axiometry: Axiometry
    closure_meetings: tuple[ClosureMeeting, ...]
    visual_truth_closure: DerivedVisualClosure
    equivalence_closure: EquivalenceClosure
    natural_forms: tuple[NaturalForm, ...]
    protocol: str = PROTOCOL
    schema: str = SCHEMA

    def natural_form_for(self, member_id: str) -> NaturalForm:
        for item in self.natural_forms:
            if member_id in item.members:
                return item
        raise KeyError(member_id)

    def relation(self, source: str, target: str) -> EquivalenceRelation | None:
        return self.equivalence_closure.relation(source, target)

    def vis_closure(self, seed_form_ids: Iterable[str]) -> tuple[str, ...]:
        return self.visual_truth_closure.close(seed_form_ids)

    def is_naturally_admitted(self, form_ids: Iterable[str]) -> bool:
        return self.visual_truth_closure.is_naturally_admitted(form_ids)

    @property
    def admitted_axiom_ids(self) -> tuple[str, ...]:
        return tuple(
            meeting.axiom_id
            for meeting in self.closure_meetings
            if meeting.admitted
        )

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)


def _coerce_visual_form(value: VisualForm | Mapping[str, Any] | str) -> VisualForm:
    if isinstance(value, VisualForm):
        return value
    if isinstance(value, str):
        return VisualForm(id=value)
    form_id = value.get("id") or value.get("form_id") or value.get("node_id")
    if form_id is None:
        raise ValueError("visual form mapping requires id, form_id, or node_id")
    raw_state = value.get("state")
    if raw_state is None:
        raw_state = value.get("visual_state")
    state = dict(raw_state) if isinstance(raw_state, Mapping) else {}
    provenance = _strings(
        value.get("existence_provenance") or value.get("provenance")
    )
    return VisualForm(
        id=str(form_id),
        state=state,
        existence_provenance=provenance,
        source_returns=_strings(
            value.get("source_return_ids") or value.get("source_returns")
        ),
    )


def _coerce_condition(
    value: ConditionWitness | Mapping[str, Any] | bool | None,
    *,
    default_provenance: str,
) -> ConditionWitness:
    if value is None:
        return ConditionWitness(witnessed=False)
    if isinstance(value, ConditionWitness):
        if value.witnessed and not value.provenance:
            return ConditionWitness(
                witnessed=True,
                provenance=(default_provenance,),
                basis=value.basis,
            )
        return value
    if isinstance(value, Mapping):
        witnessed = _strict_bool(
            value.get("witnessed", value.get("value", False)),
            field_name="condition witness",
        )
        provenance = _strings(value.get("provenance") or value.get("source_ids"))
        if witnessed and not provenance:
            provenance = (default_provenance,)
        return ConditionWitness(
            witnessed=witnessed,
            provenance=provenance,
            basis=str(value.get("basis") or "EXPLICIT_WITNESS"),
        )
    witnessed = _strict_bool(value, field_name="condition witness")
    return ConditionWitness(
        witnessed=witnessed,
        provenance=(default_provenance,) if witnessed else (),
    )


def _coerce_visual_equation(
    value: VisualEquation | Mapping[str, Any] | str | None,
    *,
    truth_id: str,
    source: str,
    target: str,
) -> VisualEquation | None:
    if value is None:
        return None
    if isinstance(value, VisualEquation):
        return value
    if isinstance(value, str):
        if not value:
            return None
        return VisualEquation(
            id=_stable_id(
                "visual-equation",
                {"truth": truth_id, "source": source, "target": target, "equation": value},
            ),
            source=source,
            target=target,
            equation=value,
            deterministic=True,
        )
    equation_source = str(value.get("source") or source)
    equation_target = str(value.get("target") or target)
    expression = value.get("equation") or value.get("expression")
    if expression is None or not str(expression):
        raise ValueError("visual_equation mapping requires equation or expression")
    equation_id = value.get("id") or value.get("equation_id")
    if equation_id is None:
        equation_id = _stable_id(
            "visual-equation",
            {
                "truth": truth_id,
                "source": equation_source,
                "target": equation_target,
                "equation": expression,
            },
        )
    return VisualEquation(
        id=str(equation_id),
        source=equation_source,
        target=equation_target,
        equation=str(expression),
        deterministic=_strict_bool(
            value.get("deterministic", True),
            field_name="visual equation deterministic",
        ),
        source_returns=_strings(
            value.get("source_return_ids") or value.get("source_returns")
        ),
        provenance=_strings(value.get("provenance") or value.get("source_ids")),
    )


def _coerce_relative_truth(
    value: RelativeTruth | Mapping[str, Any],
) -> RelativeTruth:
    if isinstance(value, RelativeTruth):
        return value
    source = value.get("source") or value.get("left")
    target = value.get("target") or value.get("right")
    if source is None or target is None:
        raise ValueError("relative truth mapping requires source/target or left/right")
    verdict = _verdict(value.get("verdict", TruthVerdict.OPEN))
    truth_id = value.get("id") or value.get("truth_id")
    if truth_id is None:
        truth_id = _stable_id(
            "relative-truth",
            {"source": source, "target": target, "verdict": verdict.value},
        )
    return RelativeTruth(
        id=str(truth_id),
        source=str(source),
        target=str(target),
        verdict=verdict,
        provenance=_strings(value.get("provenance") or value.get("source_ids")),
        statement=(
            None if value.get("statement") is None else str(value.get("statement"))
        ),
        source_returns=_strings(
            value.get("source_return_ids") or value.get("source_returns")
        ),
        visual_equation=value.get("visual_equation"),
        compatibility=value.get("compatible", value.get("compatibility", False)),
        closure_explicit=value.get("closure_explicit"),
    )


def _derive_perspective_visual_mirror(
    existence: VisualExistence,
    truths: tuple[RelativeTruth, ...],
) -> PerspectiveVisualMirror:
    form_ids = set(existence.form_ids)
    perspective_ids = tuple(
        sorted(
            {
                str(form.state.get("perspective_id"))
                for form in existence.forms
                if form.state.get("perspective_id") not in {None, ""}
            }
        )
    )
    constraints: list[VisualMirrorConstraint] = []
    for truth in truths:
        equation = truth.visual_equation
        endpoints_exist = truth.source in form_ids and truth.target in form_ids
        constraint_id = _stable_id(
            "visual-mirror-constraint",
            {
                "truth": truth.id,
                "source": truth.source,
                "target": truth.target,
                "verdict": truth.verdict.value,
                "equation": equation.id if equation is not None else None,
            },
        )
        constraints.append(
            VisualMirrorConstraint(
                id=constraint_id,
                truth_id=truth.id,
                source=truth.source,
                target=truth.target,
                verdict=truth.verdict,
                statement=truth.statement,
                visual_equation_id=(
                    equation.id if equation is not None else None
                ),
                endpoints_visually_exist=endpoints_exist,
                source_return_provenance=tuple(
                    dict.fromkeys(
                        (
                            *truth.source_returns,
                            *(equation.source_returns if equation is not None else ()),
                        )
                    )
                ),
                presentation_status=(
                    "PRESENTED_TRUE_CONSTRAINT"
                    if truth.verdict is TruthVerdict.TRUE
                    else "PRESENTED_OPEN_POTENTIAL"
                    if truth.verdict is TruthVerdict.OPEN
                    else "PRESENTED_FALSE_CONSTRAINT"
                ),
            )
        )
    mirror_id = _stable_id(
        "perspective-visual-mirror",
        {
            "forms": sorted(existence.form_ids),
            "perspectives": perspective_ids,
            "projected_forms": {
                form.id: form.state for form in existence.forms
            },
            "constraints": [item.id for item in constraints],
        },
    )
    return PerspectiveVisualMirror(
        id=mirror_id,
        form_ids=tuple(sorted(existence.form_ids)),
        perspective_ids=perspective_ids,
        projected_forms={form.id: form.state for form in existence.forms},
        constraints=tuple(sorted(constraints, key=lambda item: item.id)),
        source_return_provenance=tuple(
            dict.fromkeys(
                source_return
                for form in existence.forms
                for source_return in form.source_returns
            )
        ),
    )


def _identity_witness(
    form: VisualForm,
    visual_mirror: PerspectiveVisualMirror,
) -> TruthWitness:
    truth_id = f"identity-truth:{form.id}"
    witness_id = _stable_id(
        "truth-witness",
        {"kind": WitnessKind.IDENTITY.value, "form": form.id},
    )
    return TruthWitness(
        id=witness_id,
        kind=WitnessKind.IDENTITY,
        source=form.id,
        target=form.id,
        truth_id=truth_id,
        truth_provenance=(truth_id,),
        existence_provenance=form.existence_provenance,
        source_return_provenance=form.source_returns,
        visual_equation_provenance=(f"visual-equation:identity:{form.id}",),
        compatibility_provenance=(f"compatibility:identity:{form.id}",),
        closure_explicit_provenance=(f"closure-explicit:identity:{form.id}",),
        visual_mirror_provenance=(
            visual_mirror.id,
            f"visual-mirror-identity:{form.id}",
        ),
    )


def _cross_witness(
    truth: RelativeTruth,
    source: VisualForm,
    target: VisualForm,
    visual_mirror: PerspectiveVisualMirror,
) -> TruthWitness:
    if truth.visual_equation is None:
        raise ValueError(
            "a cross-form truth witness requires a visual equation"
        )
    mirror_constraint = visual_mirror.constraint_for(truth.id)
    if mirror_constraint is None:
        raise ValueError(
            "a cross-form truth witness requires a visual-mirror constraint"
        )
    witness_id = _stable_id(
        "truth-witness",
        {
            "kind": WitnessKind.RELATIVE_TRANSLATION.value,
            "truth": truth.id,
            "source": truth.source,
            "target": truth.target,
        },
    )
    return TruthWitness(
        id=witness_id,
        kind=WitnessKind.RELATIVE_TRANSLATION,
        source=truth.source,
        target=truth.target,
        truth_id=truth.id,
        truth_provenance=truth.provenance,
        existence_provenance=tuple(
            dict.fromkeys(
                (*source.existence_provenance, *target.existence_provenance)
            )
        ),
        source_return_provenance=tuple(
            dict.fromkeys(
                (
                    *truth.source_returns,
                    *(truth.visual_equation.source_returns if truth.visual_equation else ()),
                )
                or (
                    *source.source_returns,
                    *target.source_returns,
                )
            )
        ),
        visual_equation_provenance=tuple(
            dict.fromkeys(
                (truth.visual_equation.id, *truth.visual_equation.provenance)
            )
        ),
        compatibility_provenance=truth.compatibility.provenance,
        closure_explicit_provenance=truth.closure_explicit.provenance,
        visual_mirror_provenance=(
            visual_mirror.id,
            mirror_constraint.id,
        ),
    )


def _promote_axiom(witness: TruthWitness) -> TranslationAxiom:
    axiom_id = _stable_id(
        "translation-axiom",
        {
            "source": witness.source,
            "target": witness.target,
            "witness": witness.id,
        },
    )
    return TranslationAxiom(
        id=axiom_id,
        source=witness.source,
        target=witness.target,
        witness_id=witness.id,
        truth_id=witness.truth_id,
        truth_provenance=witness.truth_provenance,
        existence_provenance=witness.existence_provenance,
        source_return_provenance=witness.source_return_provenance,
        visual_equation_provenance=witness.visual_equation_provenance,
        compatibility_provenance=witness.compatibility_provenance,
        closure_explicit_provenance=witness.closure_explicit_provenance,
        visual_mirror_provenance=witness.visual_mirror_provenance,
    )


def _derive_closure_meetings(
    axioms: tuple[TranslationAxiom, ...],
    witnesses: tuple[TruthWitness, ...],
    truths: tuple[RelativeTruth, ...],
    visual_mirror: PerspectiveVisualMirror,
) -> tuple[ClosureMeeting, ...]:
    witness_by_id = {witness.id: witness for witness in witnesses}
    truth_by_id = {truth.id: truth for truth in truths}
    meetings: list[ClosureMeeting] = []
    for axiom in axioms:
        witness = witness_by_id[axiom.witness_id]
        if witness.kind is WitnessKind.IDENTITY:
            mirror_constraint_id = f"visual-mirror-identity:{witness.source}"
            admitted = True
            compatible = True
            closure_explicit = True
            basis = "VISUAL_EXISTENCE_IDENTITY"
            provenance = tuple(
                dict.fromkeys(
                    (
                        *witness.existence_provenance,
                        *witness.closure_explicit_provenance,
                        *witness.visual_mirror_provenance,
                    )
                )
            )
        else:
            truth = truth_by_id[witness.truth_id]
            mirror_constraint = visual_mirror.constraint_for(truth.id)
            if mirror_constraint is None:  # pragma: no cover - constructor invariant
                raise RuntimeError("axiom lost its visual-mirror constraint")
            mirror_constraint_id = mirror_constraint.id
            compatible = truth.compatibility.witnessed
            closure_explicit = truth.closure_explicit.witnessed
            admitted = bool(
                compatible
                and truth.has_valid_visual_equation
                and closure_explicit
            )
            basis = truth.closure_explicit.basis
            provenance = tuple(
                dict.fromkeys(
                    (
                        *truth.provenance,
                        *truth.compatibility.provenance,
                        *truth.closure_explicit.provenance,
                        truth.visual_equation.id
                        if truth.visual_equation is not None
                        else "",
                        visual_mirror.id,
                        mirror_constraint.id,
                    )
                )
            )
        meeting_id = _stable_id(
            "closure-meeting",
            {
                "axiom": axiom.id,
                "admitted": admitted,
                "basis": basis,
            },
        )
        meetings.append(
            ClosureMeeting(
                id=meeting_id,
                axiom_id=axiom.id,
                witness_id=witness.id,
                truth_id=witness.truth_id,
                visual_mirror_constraint_id=mirror_constraint_id,
                source=axiom.source,
                target=axiom.target,
                compatible=compatible,
                closure_explicit=closure_explicit,
                admitted=admitted,
                basis=basis,
                provenance=tuple(item for item in provenance if item),
            )
        )
    return tuple(sorted(meetings, key=lambda item: item.id))


def _closure(
    form_ids: tuple[str, ...], axioms: tuple[TranslationAxiom, ...]
) -> EquivalenceClosure:
    adjacency: dict[str, list[tuple[str, TranslationAxiom]]] = {
        form_id: [] for form_id in form_ids
    }
    identity_axioms: dict[str, TranslationAxiom] = {}
    for axiom in axioms:
        if axiom.source == axiom.target:
            identity_axioms[axiom.source] = axiom
        else:
            adjacency[axiom.source].append((axiom.target, axiom))
            adjacency[axiom.target].append((axiom.source, axiom))
    for neighbours in adjacency.values():
        neighbours.sort(key=lambda item: (item[0], item[1].id))

    seen: set[str] = set()
    classes: list[tuple[str, ...]] = []
    for start in sorted(form_ids):
        if start in seen:
            continue
        queue = deque((start,))
        component: list[str] = []
        seen.add(start)
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbour, _ in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    queue.append(neighbour)
        classes.append(tuple(sorted(component)))

    relations: list[EquivalenceRelation] = []
    for component in classes:
        for source in component:
            for target in component:
                if source == target:
                    identity = identity_axioms[source]
                    relations.append(
                        EquivalenceRelation(
                            source=source,
                            target=target,
                            path=(source,),
                            axiom_ids=(identity.id,),
                            witness_ids=(identity.witness_id,),
                            truth_ids=(identity.truth_id,),
                            closure_operations=("REFLEXIVITY",),
                        )
                    )
                    continue

                queue = deque((source,))
                predecessor: dict[
                    str, tuple[str, TranslationAxiom] | None
                ] = {source: None}
                while queue and target not in predecessor:
                    current = queue.popleft()
                    for neighbour, edge_axiom in adjacency[current]:
                        if neighbour in predecessor:
                            continue
                        predecessor[neighbour] = (current, edge_axiom)
                        queue.append(neighbour)

                path_back = [target]
                edge_back: list[TranslationAxiom] = []
                cursor = target
                while cursor != source:
                    prior = predecessor[cursor]
                    if prior is None:  # pragma: no cover - impossible after component BFS
                        raise RuntimeError("closure component lost its finite witness")
                    cursor, edge_axiom = prior
                    path_back.append(cursor)
                    edge_back.append(edge_axiom)
                path = tuple(reversed(path_back))
                path_axioms = tuple(reversed(edge_back))
                operations = ["AXIOM_GENERATION"]
                if any(
                    axiom.source != path[index]
                    or axiom.target != path[index + 1]
                    for index, axiom in enumerate(path_axioms)
                ):
                    operations.append("SYMMETRY")
                if len(path_axioms) > 1:
                    operations.append("TRANSITIVITY")
                relations.append(
                    EquivalenceRelation(
                        source=source,
                        target=target,
                        path=path,
                        axiom_ids=tuple(item.id for item in path_axioms),
                        witness_ids=tuple(item.witness_id for item in path_axioms),
                        truth_ids=tuple(item.truth_id for item in path_axioms),
                        closure_operations=tuple(operations),
                    )
                )

    return EquivalenceClosure(classes=tuple(classes), relations=tuple(relations))


def _derive_visual_truth_closure(
    existence: VisualExistence,
    equivalence: EquivalenceClosure,
    visual_mirror: PerspectiveVisualMirror,
) -> DerivedVisualClosure:
    """Factor axiometry into a joint reading, then apply NRRF840 exactly."""

    class_by_form = {
        member: members
        for members in equivalence.classes
        for member in members
    }
    joint_reading_by_form = {
        member: _stable_id(
            "joint-translational-truth-reading",
            {"members": class_by_form[member]},
        )
        for member in sorted(existence.form_ids)
    }
    singleton_closure = {
        source: tuple(
            member
            for member in sorted(existence.form_ids)
            if joint_reading_by_form[member] == joint_reading_by_form[source]
        )
        for source in sorted(existence.form_ids)
    }
    memberships: list[VisClosureMembership] = []
    for source in sorted(existence.form_ids):
        source_form = existence.form(source)
        source_reading = joint_reading_by_form[source]
        for member in singleton_closure[source]:
            member_form = existence.form(member)
            relation = equivalence.relation(source, member)
            if relation is None:  # pragma: no cover - guarded by equal class
                raise RuntimeError(
                    "joint truth reading lacks its axiometry provenance"
                )
            equality_provenance = tuple(
                dict.fromkeys(
                    (
                        *source_form.source_returns,
                        *member_form.source_returns,
                        *relation.axiom_ids,
                        *relation.witness_ids,
                        *relation.truth_ids,
                    )
                )
            )
            observer_equality = ObserverEquality(
                observer_id=JOINT_TRUTH_OBSERVER,
                member_id=member,
                source_form_id=source,
                member_reading=joint_reading_by_form[member],
                source_reading=source_reading,
                equal=True,
                provenance=equality_provenance,
            )
            membership_id = _stable_id(
                "vis-closure-membership",
                {
                    "member": member,
                    "source": source,
                    "observer_equalities": (observer_equality,),
                },
            )
            memberships.append(
                VisClosureMembership(
                    id=membership_id,
                    member_id=member,
                    source_form_id=source,
                    source_return_provenance=tuple(
                        dict.fromkeys(
                            (
                                *source_form.source_returns,
                                *member_form.source_returns,
                            )
                        )
                    ),
                    observer_equalities=(observer_equality,),
                )
            )

    closure_id = _stable_id(
        "nrrf840-vis-closure",
        {
            "formal_module": NRRF840_MODULE,
            "visual_mirror": visual_mirror.id,
            "joint_reading_by_form": joint_reading_by_form,
            "singleton_closure": singleton_closure,
        },
    )
    result = DerivedVisualClosure(
        id=closure_id,
        visual_mirror_id=visual_mirror.id,
        observer_ids=(JOINT_TRUTH_OBSERVER,),
        joint_reading_by_form=joint_reading_by_form,
        classes=equivalence.classes,
        singleton_closure=singleton_closure,
        memberships=tuple(memberships),
    )
    # This assertion is the executable bridge: the retained axiom graph and
    # the NRRF840 preimage/image construction must select exactly the same
    # finite truth fibres.  Neither one is allowed to silently widen the other.
    derived_classes = tuple(
        dict.fromkeys(result.close((source,)) for source in sorted(existence.form_ids))
    )
    if derived_classes != equivalence.classes:
        raise RuntimeError(
            "NRRF840 visClosure disagrees with the derived axiometry truth classes"
        )
    return result


def _natural_forms(
    visual_closure: DerivedVisualClosure,
    equivalence: EquivalenceClosure,
    axioms: tuple[TranslationAxiom, ...],
) -> tuple[NaturalForm, ...]:
    forms: list[NaturalForm] = []
    for members in visual_closure.classes:
        member_set = set(members)
        class_axioms = tuple(
            axiom
            for axiom in axioms
            if axiom.source in member_set and axiom.target in member_set
        )
        truth_provenance = tuple(
            dict.fromkeys(
                item
                for axiom in class_axioms
                for item in (axiom.truth_id, *axiom.truth_provenance)
            )
        )
        natural_form_id = _stable_id("natural-form", {"members": members})

        def provenance(field_name: str) -> tuple[str, ...]:
            return tuple(
                dict.fromkeys(
                    item
                    for axiom in class_axioms
                    for item in getattr(axiom, field_name)
                )
            )

        forms.append(
            NaturalForm(
                id=natural_form_id,
                members=members,
                truth_provenance=truth_provenance,
                axiom_provenance=tuple(axiom.id for axiom in class_axioms),
                witness_provenance=tuple(
                    axiom.witness_id for axiom in class_axioms
                ),
                relation_provenance=tuple(
                    (relation.source, relation.target)
                    for relation in equivalence.relations
                    if relation.source in member_set
                    and relation.target in member_set
                ),
                existence_provenance=provenance(
                    "existence_provenance"
                ),
                source_return_provenance=provenance(
                    "source_return_provenance"
                ),
                visual_equation_provenance=provenance(
                    "visual_equation_provenance"
                ),
                compatibility_provenance=provenance(
                    "compatibility_provenance"
                ),
                closure_explicit_provenance=provenance(
                    "closure_explicit_provenance"
                ),
                visual_mirror_provenance=provenance(
                    "visual_mirror_provenance"
                ),
                factorization_provenance=(
                    f"factorization-witness:{natural_form_id}",
                ),
                visual_closure_id=visual_closure.id,
                vis_closure_membership_witness_ids=tuple(
                    membership.id
                    for membership in visual_closure.memberships
                    if membership.source_form_id in member_set
                    and membership.member_id in member_set
                ),
            )
        )
    return tuple(forms)


def derive_translational_truth_axiometry(
    visual_existence: Iterable[VisualForm | Mapping[str, Any] | str],
    relative_truths: Iterable[RelativeTruth | Mapping[str, Any]] = (),
) -> ClosureDerivation:
    """Derive natural forms through the complete closure relation.

    The stages are explicit in the result:

    ``visual existence -> witnessed relative truths -> visual axiometry ->
    closure-explicit meeting -> joint translational-truth reading -> NRRF840
    ``preimage(image(A))`` closure -> naturally admitted forms``.

    Every existing form receives an identity witness.  A non-identity proposal
    receives a truth witness exactly when both endpoints exist, its verdict is
    ``TRUE``, compatibility is witnessed, and a deterministic endpoint-matching
    visual equation exists.  Those witnesses first become visual axioms.  Only
    a later closure-explicit meeting admits an axiom as an equality generator.
    ``OPEN`` and ``FALSE`` proposals, merely similar presentations, and axioms
    whose meeting remains open cannot generate equality.
    """

    forms = tuple(_coerce_visual_form(value) for value in visual_existence)
    form_ids = tuple(form.id for form in forms)
    if len(form_ids) != len(set(form_ids)):
        raise ValueError("visual existence contains duplicate form ids")
    existence = VisualExistence(forms=forms)
    form_by_id = {form.id: form for form in forms}
    truths = tuple(_coerce_relative_truth(value) for value in relative_truths)
    truth_ids = tuple(truth.id for truth in truths)
    if len(truth_ids) != len(set(truth_ids)):
        raise ValueError("relative truths contain duplicate truth ids")
    visual_mirror = _derive_perspective_visual_mirror(existence, truths)

    witnesses: list[TruthWitness] = [
        _identity_witness(form, visual_mirror)
        for form in sorted(forms, key=lambda item: item.id)
    ]
    evaluations: list[RelativeTruthEvaluation] = []
    for truth in truths:
        endpoints_exist = (
            truth.source in form_by_id and truth.target in form_by_id
        )
        if truth.source == truth.target and truth.source in form_by_id:
            # Existence already supplies identity.  The proposal is not needed
            # to generate a second axiom and cannot revoke reflexivity.
            identity = next(
                witness
                for witness in witnesses
                if witness.kind is WitnessKind.IDENTITY
                and witness.source == truth.source
            )
            claim_is_true = truth.verdict is TruthVerdict.TRUE
            evaluations.append(
                RelativeTruthEvaluation(
                    truth_id=truth.id,
                    source=truth.source,
                    target=truth.target,
                    verdict=truth.verdict,
                    endpoints_exist=True,
                    status=(
                        WitnessStatus.WITNESSED
                        if claim_is_true
                        else WitnessStatus.NOT_WITNESSED
                    ),
                    reason=(
                        "identity_is_witnessed_by_visual_existence"
                        if claim_is_true
                        else "identity_relation_intrinsic_but_claim_verdict_not_true"
                    ),
                    witness_id=identity.id if claim_is_true else None,
                    compatible=True,
                    closure_explicit=True,
                    meets_visual_existence=True,
                    closure_admitted=claim_is_true,
                )
            )
        elif not endpoints_exist:
            evaluations.append(
                RelativeTruthEvaluation(
                    truth_id=truth.id,
                    source=truth.source,
                    target=truth.target,
                    verdict=truth.verdict,
                    endpoints_exist=False,
                    status=WitnessStatus.NOT_WITNESSED,
                    reason="endpoint_not_in_visual_existence",
                    witness_id=None,
                    compatible=truth.compatibility.witnessed,
                    closure_explicit=truth.closure_explicit.witnessed,
                    meets_visual_existence=truth.meets_visual_existence,
                    closure_admitted=False,
                )
            )
        elif truth.verdict is not TruthVerdict.TRUE:
            evaluations.append(
                RelativeTruthEvaluation(
                    truth_id=truth.id,
                    source=truth.source,
                    target=truth.target,
                    verdict=truth.verdict,
                    endpoints_exist=True,
                    status=WitnessStatus.NOT_WITNESSED,
                    reason="cross_translation_requires_true_verdict",
                    witness_id=None,
                    compatible=truth.compatibility.witnessed,
                    closure_explicit=truth.closure_explicit.witnessed,
                    meets_visual_existence=truth.meets_visual_existence,
                    closure_admitted=False,
                )
            )
        elif not truth.compatibility.witnessed:
            evaluations.append(
                RelativeTruthEvaluation(
                    truth_id=truth.id,
                    source=truth.source,
                    target=truth.target,
                    verdict=truth.verdict,
                    endpoints_exist=True,
                    status=WitnessStatus.NOT_WITNESSED,
                    reason="cross_translation_requires_compatibility_witness",
                    witness_id=None,
                    compatible=False,
                    closure_explicit=truth.closure_explicit.witnessed,
                    meets_visual_existence=False,
                    closure_admitted=False,
                )
            )
        elif not truth.has_valid_visual_equation:
            evaluations.append(
                RelativeTruthEvaluation(
                    truth_id=truth.id,
                    source=truth.source,
                    target=truth.target,
                    verdict=truth.verdict,
                    endpoints_exist=True,
                    status=WitnessStatus.NOT_WITNESSED,
                    reason=(
                        "cross_translation_requires_deterministic_endpoint_"
                        "matching_visual_equation"
                    ),
                    witness_id=None,
                    compatible=True,
                    closure_explicit=truth.closure_explicit.witnessed,
                    meets_visual_existence=False,
                    closure_admitted=False,
                )
            )
        else:
            witness = _cross_witness(
                truth,
                form_by_id[truth.source],
                form_by_id[truth.target],
                visual_mirror,
            )
            witnesses.append(witness)
            evaluations.append(
                RelativeTruthEvaluation(
                    truth_id=truth.id,
                    source=truth.source,
                    target=truth.target,
                    verdict=truth.verdict,
                    endpoints_exist=True,
                    status=WitnessStatus.WITNESSED,
                    reason=(
                        "true_relative_translation_meets_closure_explicitly"
                        if truth.closure_explicit.witnessed
                        else "translational_truth_axiom_waits_for_explicit_closure_meeting"
                    ),
                    witness_id=witness.id,
                    compatible=True,
                    closure_explicit=truth.closure_explicit.witnessed,
                    meets_visual_existence=truth.meets_visual_existence,
                    closure_admitted=truth.closure_explicit.witnessed,
                )
            )

    witness_tuple = tuple(sorted(witnesses, key=lambda item: item.id))
    axioms = tuple(
        sorted(
            (_promote_axiom(witness) for witness in witness_tuple),
            key=lambda item: item.id,
        )
    )
    axiometry = Axiometry(
        axioms=axioms,
        witness_ids=tuple(witness.id for witness in witness_tuple),
    )
    closure_meetings = _derive_closure_meetings(
        axioms,
        witness_tuple,
        truths,
        visual_mirror,
    )
    admitted_axiom_ids = {
        meeting.axiom_id for meeting in closure_meetings if meeting.admitted
    }
    admitted_axioms = tuple(
        axiom for axiom in axioms if axiom.id in admitted_axiom_ids
    )
    equivalence = _closure(form_ids, admitted_axioms)
    visual_truth_closure = _derive_visual_truth_closure(
        existence,
        equivalence,
        visual_mirror,
    )
    natural_forms = _natural_forms(
        visual_truth_closure,
        equivalence,
        admitted_axioms,
    )
    derivation_id = _stable_id(
        "closure-derivation",
        {
            "visual_existence": [
                {
                    "id": form.id,
                    "state": form.state,
                    "provenance": form.existence_provenance,
                    "source_returns": form.source_returns,
                }
                for form in sorted(forms, key=lambda item: item.id)
            ],
            "perspective_visual_mirror": visual_mirror.id,
            "truths": [
                {
                    "id": truth.id,
                    "source": truth.source,
                    "target": truth.target,
                    "verdict": truth.verdict.value,
                    "provenance": truth.provenance,
                    "source_returns": truth.source_returns,
                    "visual_equation": (
                        None
                        if truth.visual_equation is None
                        else truth.visual_equation.to_dict()
                    ),
                    "compatibility": truth.compatibility,
                    "closure_explicit": truth.closure_explicit,
                }
                for truth in sorted(truths, key=lambda item: item.id)
            ],
            "axioms": sorted(axiom.id for axiom in axioms),
            "closure_meetings": [
                {
                    "id": meeting.id,
                    "axiom_id": meeting.axiom_id,
                    "admitted": meeting.admitted,
                    "basis": meeting.basis,
                }
                for meeting in closure_meetings
            ],
            "nrrf840_visual_truth_closure": visual_truth_closure.id,
        },
    )
    return ClosureDerivation(
        id=derivation_id,
        visual_existence=existence,
        perspective_visual_mirror=visual_mirror,
        relative_truths=truths,
        truth_evaluations=tuple(evaluations),
        witnesses=witness_tuple,
        axiometry=axiometry,
        closure_meetings=closure_meetings,
        visual_truth_closure=visual_truth_closure,
        equivalence_closure=equivalence,
        natural_forms=natural_forms,
    )


def derive_closure(
    visual_existence: Iterable[VisualForm | Mapping[str, Any] | str],
    relative_truths: Iterable[RelativeTruth | Mapping[str, Any]] = (),
) -> ClosureDerivation:
    """Concise alias for :func:`derive_translational_truth_axiometry`."""

    return derive_translational_truth_axiometry(
        visual_existence,
        relative_truths,
    )


def _normalize_render_states(
    render_states: Mapping[str, Mapping[str, Any]]
    | Iterable[Mapping[str, Any]],
) -> tuple[Mapping[str, Any], ...]:
    normalized: list[Mapping[str, Any]] = []
    if isinstance(render_states, Mapping):
        items: Iterable[tuple[Any, Any]] = render_states.items()
        for member_id, state in items:
            if not isinstance(state, Mapping):
                raise TypeError("each render state must be a mapping")
            item = dict(state)
            declared = item.get("member_id")
            if declared is not None and str(declared) != str(member_id):
                raise ValueError("render-state key and member_id disagree")
            item["member_id"] = str(member_id)
            normalized.append(_freeze(item))
    else:
        for state in render_states:
            if not isinstance(state, Mapping):
                raise TypeError("each render state must be a mapping")
            item = dict(state)
            if item.get("member_id") is None:
                raise ValueError("iterable render states require member_id")
            item["member_id"] = str(item["member_id"])
            normalized.append(_freeze(item))
    normalized.sort(key=lambda item: item["member_id"])
    ids = [item["member_id"] for item in normalized]
    if len(ids) != len(set(ids)):
        raise ValueError("render states contain duplicate member ids")
    return tuple(normalized)


def derive_interface_natural_form(
    derivation: ClosureDerivation,
    render_states: Mapping[str, Mapping[str, Any]]
    | Iterable[Mapping[str, Any]],
) -> InterfaceNaturalForm:
    """Derive the whole UI as a reading that factors through closure truth.

    A state is required for every visually existing member.  States must be
    constant within each natural-form class, but may differ across classes.
    Consequently the function produces both the quotient render state and its
    full projection back over visual existence.  Presentation can distinguish
    unequal classes without inventing an equality between them.  HTML, canvas,
    native, spatial, and other external renderers only transport this result.
    """

    states = _normalize_render_states(render_states)
    member_ids = tuple(item["member_id"] for item in states)
    existence_ids = set(derivation.visual_existence.form_ids)
    supplied_ids = set(member_ids)
    unknown_ids = sorted(supplied_ids - existence_ids)
    if unknown_ids:
        raise ValueError(
            "render state references forms outside visual existence: "
            + ", ".join(unknown_ids)
        )
    missing_ids = sorted(existence_ids - supplied_ids)
    if missing_ids:
        raise ValueError(
            "whole-closure interface reading is missing forms: "
            + ", ".join(missing_ids)
        )

    payload_by_member = {
        item["member_id"]: {
            key: value for key, value in item.items() if key != "member_id"
        }
        for item in states
    }
    quotient_render_state: dict[str, Mapping[str, Any]] = {}
    for natural_form in derivation.natural_forms:
        class_payloads = [payload_by_member[item] for item in natural_form.members]
        first_payload = class_payloads[0]
        if any(
            _canonical_json(payload) != _canonical_json(first_payload)
            for payload in class_payloads[1:]
        ):
            raise ValueError(
                "interface reading does not factor through closure truth for "
                f"natural form {natural_form.id}"
            )
        quotient_render_state[natural_form.id] = _freeze(first_payload)

    closure_projection = _freeze({
        member_id: _freeze(
            quotient_render_state[
                derivation.natural_form_for(member_id).id
            ]
        )
        for member_id in sorted(existence_ids)
    })
    frozen_quotient_render_state = _freeze(quotient_render_state)
    natural_form_ids = tuple(item.id for item in derivation.natural_forms)
    truth_provenance = tuple(
        dict.fromkeys(
            item
            for natural_form in derivation.natural_forms
            for item in natural_form.truth_provenance
        )
    )
    axiom_provenance = tuple(
        item.id for item in derivation.axiometry.axioms
    )
    witness_provenance = tuple(
        item.id for item in derivation.witnesses
    )
    def natural_form_provenance(field_name: str) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                item
                for natural_form in derivation.natural_forms
                for item in getattr(natural_form, field_name)
            )
        )
    factorization_id = _stable_id(
        "interface-factorization-witness",
        {
            "closure": derivation.id,
            "quotient_render_state": frozen_quotient_render_state,
            "projection": closure_projection,
        },
    )
    interface_id = _stable_id(
        "interface-natural-form",
        {
            "closure": derivation.id,
            "quotient_render_state": frozen_quotient_render_state,
            "factorization": factorization_id,
        },
    )
    return InterfaceNaturalForm(
        id=interface_id,
        closure_id=derivation.id,
        natural_form_ids=natural_form_ids,
        members=member_ids,
        render_states=states,
        quotient_render_state=frozen_quotient_render_state,
        closure_projection=closure_projection,
        truth_provenance=truth_provenance,
        axiom_provenance=axiom_provenance,
        witness_provenance=witness_provenance,
        factorization_provenance=(factorization_id,),
        existence_provenance=natural_form_provenance(
            "existence_provenance"
        ),
        source_return_provenance=natural_form_provenance(
            "source_return_provenance"
        ),
        visual_equation_provenance=natural_form_provenance(
            "visual_equation_provenance"
        ),
        compatibility_provenance=natural_form_provenance(
            "compatibility_provenance"
        ),
        closure_explicit_provenance=natural_form_provenance(
            "closure_explicit_provenance"
        ),
        visual_mirror_provenance=natural_form_provenance(
            "visual_mirror_provenance"
        ),
        visual_mirror_id=derivation.perspective_visual_mirror.id,
        visual_closure_id=derivation.visual_truth_closure.id,
        vis_closure_membership_witness_ids=tuple(
            item.id for item in derivation.visual_truth_closure.memberships
        ),
    )


__all__ = [
    "Axiometry",
    "ClosureDerivation",
    "ClosureMeeting",
    "ConditionWitness",
    "DerivedVisualClosure",
    "EquivalenceClosure",
    "EquivalenceRelation",
    "EXTERNAL_RENDERER_CONTRACT",
    "ExternalRendererContract",
    "InterfaceNaturalForm",
    "NaturalForm",
    "NRRF840_CRITERION",
    "NRRF840_MODULE",
    "ObserverEquality",
    "PerspectiveVisualMirror",
    "PROTOCOL",
    "RelativeTruth",
    "RelativeTruthEvaluation",
    "RendererRole",
    "SCHEMA",
    "TranslationAxiom",
    "TruthVerdict",
    "TruthWitness",
    "VisualEquation",
    "VisualExistence",
    "VisualForm",
    "VisualMirrorConstraint",
    "VisClosureMembership",
    "VisClosureProperties",
    "WitnessKind",
    "WitnessStatus",
    "derive_closure",
    "derive_interface_natural_form",
    "derive_translational_truth_axiometry",
]
