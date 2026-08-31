from __future__ import annotations

"""Shared translational-continuity semantics for the executable Supernet.

The kernel enforces a narrow authorship rule:

* source-preserving interaction may contribute evidence;
* re-closure may witness relative truth;
* configuration and finite computation bounds may only leave a result OPEN.

Nothing in this module selects an absolute representative. Partitions are
compared extensionally, so changing display labels without changing fibres is a
translation of presentation rather than a change of truth.
"""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

OPEN_STATUS = "OPEN"
WITNESSED_STATUS = "WITNESSED"


@dataclass(frozen=True, slots=True)
class ClosureWitness:
    """One source-derived condition used by a relative closure receipt."""

    name: str
    holds: bool
    basis: str
    source_ids: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "holds": self.holds,
            "basis": self.basis,
            "source_ids": list(self.source_ids),
            "semantic_authority": "SOURCE_INTERACTION_AND_RECLOSURE",
        }


def unique_strings(values: Iterable[Any]) -> list[str]:
    return list(
        dict.fromkeys(
            str(value)
            for value in values
            if value is not None and str(value)
        )
    )


def partition_signature(reading: Mapping[str, Any]) -> tuple[tuple[str, ...], ...]:
    """Return the unlabeled fibre partition of a member -> display/form map."""

    groups: dict[str, set[str]] = {}
    for member, label in reading.items():
        groups.setdefault(str(label), set()).add(str(member))
    return tuple(sorted(tuple(sorted(group)) for group in groups.values()))


def derive_perspective_reading(
    *,
    nrrf843_ui: Mapping[str, Any],
    nrrf842_journey: Mapping[str, Any],
    truth_members: set[str],
) -> dict[str, Any]:
    """Derive an active reading only from an explicit source-authored choice.

    A singleton UI family is not silently selected. Absence of a returned
    perspective is an OPEN state, not permission for the runtime to author one.
    """

    ui_family = nrrf843_ui.get("ui_family", {})
    perspectives = unique_strings(ui_family.get("perspective_ids", []))
    readings = ui_family.get("readings", {})
    if not isinstance(readings, Mapping):
        readings = {}

    chosen_record = nrrf842_journey.get("chosen_perspective", {})
    if not isinstance(chosen_record, Mapping):
        chosen_record = {}
    chosen = str(chosen_record.get("perspective_id") or "")
    choice_source = str(chosen_record.get("choice_source") or "OPEN")
    explicit = bool(
        chosen
        and chosen_record.get("chosen") is True
        and str(chosen_record.get("status") or "").upper() == "CHOSEN"
        and choice_source.upper() != "OPEN"
    )
    in_family = chosen in perspectives
    active = chosen if explicit and in_family else None
    raw_reading = readings.get(active, {}) if active else {}
    reading = dict(raw_reading) if isinstance(raw_reading, Mapping) else {}
    reading_total = bool(active and set(map(str, reading)) == truth_members)

    return {
        "active_perspective_id": active,
        "projection_reading": reading,
        "perspective_ids": perspectives,
        "choice_source": choice_source,
        "explicit_source_choice": explicit,
        "choice_in_ui_family": in_family,
        "reading_total": reading_total,
        "fallback_selection_used": False,
        "selection_witnessed": bool(explicit and in_family),
    }


def derive_projection_equivalence(
    *,
    reading: Mapping[str, Any],
    form_by_member: Mapping[str, str],
    conflicting_form_members: Iterable[str] = (),
) -> dict[str, Any]:
    """Recompute UI-kernel equality from source partitions.

    Stored booleans saying that closure has already been established are not
    consulted. Equality holds exactly when the UI fibres and natural-form
    fibres partition the same source members.
    """

    conflicts = sorted(set(map(str, conflicting_form_members)))
    truth_members = set(map(str, form_by_member))
    reading_members = set(map(str, reading))
    reading_total = reading_members == truth_members and bool(truth_members)
    reading_partition = partition_signature(
        {str(member): label for member, label in reading.items()}
    )
    form_partition = partition_signature(
        {str(member): str(form) for member, form in form_by_member.items()}
    )
    partition_equal = bool(
        reading_total and not conflicts and reading_partition == form_partition
    )

    return {
        "reading_total": reading_total,
        "truth_member_ids": sorted(truth_members),
        "reading_member_ids": sorted(reading_members),
        "reading_partition": [list(group) for group in reading_partition],
        "natural_form_partition": [list(group) for group in form_partition],
        "conflicting_form_members": conflicts,
        "partition_equal": partition_equal,
        "display_labels_are_semantic_authority": False,
    }


def combine_witnesses(
    witnesses: Sequence[ClosureWitness],
) -> dict[str, Any]:
    witness_map = {witness.name: witness.as_dict() for witness in witnesses}
    witnessed = bool(witnesses) and all(witness.holds for witness in witnesses)
    return {
        "status": WITNESSED_STATUS if witnessed else OPEN_STATUS,
        "translational_truth_witnessed": witnessed,
        "absolute_truth_issued": False,
        "existence_closed": False,
        "continuation_status": OPEN_STATUS,
        "semantic_authors": ["SOURCE_INTERACTION", "RECLOSURE"],
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "witnesses": witness_map,
        "open_reasons": [
            witness.basis for witness in witnesses if not witness.holds
        ],
    }


def computation_boundary_open(
    *,
    boundary: str,
    configured_limit: int | float | str | None,
    observed: int | float | str | None = None,
) -> dict[str, Any]:
    """Represent exhausted resources without converting them into a verdict."""

    return {
        "status": OPEN_STATUS,
        "boundary": boundary,
        "configured_limit": configured_limit,
        "observed": observed,
        "truth_issued": False,
        "limit_is_semantic": False,
        "existence_closed": False,
        "continuation_required": True,
    }


def finite_horn_closure(
    seed: Iterable[str],
    rules: Sequence[Mapping[str, Any]],
    *,
    max_iterations: int | None = None,
) -> dict[str, Any]:
    """Compute one finite relative rule-chart closure with an explicit receipt.

    The rule chart is an authored local perspective. Stabilisation witnesses a
    fixed point of that chart only; it never promotes those rules to universal
    truth and never closes dialectic continuation.
    """

    normalized_rules: list[dict[str, Any]] = []
    result = set(unique_strings(seed))
    universe = set(result)
    for raw in rules:
        rule = dict(raw)
        premises = unique_strings(rule.get("premise_occurrence_ids", []))
        conclusion = str(rule.get("conclusion_occurrence_id") or "")
        if not conclusion:
            raise ValueError("A closure rule requires a conclusion occurrence")
        normalized_rules.append(
            {
                "premise_occurrence_ids": premises,
                "conclusion_occurrence_id": conclusion,
                "label": rule.get("label"),
            }
        )
        universe.update(premises)
        universe.add(conclusion)

    derived_bound = len(universe) + 1
    iteration_bound = derived_bound if max_iterations is None else max(0, max_iterations)
    iterations = 0
    stabilized = False

    for _ in range(iteration_bound):
        iterations += 1
        changed = False
        for rule in normalized_rules:
            premises = set(rule["premise_occurrence_ids"])
            conclusion = rule["conclusion_occurrence_id"]
            if premises.issubset(result) and conclusion not in result:
                result.add(conclusion)
                changed = True
        if not changed:
            stabilized = True
            break

    if not stabilized:
        stabilized = not any(
            set(rule["premise_occurrence_ids"]).issubset(result)
            and rule["conclusion_occurrence_id"] not in result
            for rule in normalized_rules
        )

    status = WITNESSED_STATUS if stabilized else OPEN_STATUS
    receipt = {
        "status": status,
        "members": sorted(result),
        "iterations": iterations,
        "derived_finite_bound": derived_bound,
        "configured_iteration_bound": max_iterations,
        "fixed_point_witnessed": stabilized,
        "rule_chart_kind": "PARTICIPANT_AUTHORED_RELATIVE_READING",
        "rule_chart_is_universal_truth": False,
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "existence_closed": False,
        "continuation_status": OPEN_STATUS,
    }
    if not stabilized:
        receipt["boundary_receipt"] = computation_boundary_open(
            boundary="FINITE_CLOSURE_ITERATION_BOUND",
            configured_limit=iteration_bound,
            observed=iterations,
        )
    return receipt


def audit_translational_continuity(value: Any) -> dict[str, Any]:
    """Audit a runtime receipt for known sources of external truth authorship.

    The audit is structural and conservative. A violation keeps the audit OPEN;
    it never declares the underlying proposition false.
    """

    forbidden_true = {
        "absolute_truth_issued",
        "configuration_authors_truth",
        "computation_bounds_author_truth",
        "existence_closed",
        "fallback_selection_used",
        "stored_status_flags_used_as_evidence",
        "parallel_truth_runtime_present",
        "limit_is_semantic",
    }
    violations: list[dict[str, Any]] = []

    def visit(item: Any, path: tuple[str, ...]) -> None:
        if isinstance(item, Mapping):
            for raw_key, child in item.items():
                key = str(raw_key)
                child_path = (*path, key)
                if key in forbidden_true and child is True:
                    violations.append(
                        {
                            "path": ".".join(child_path),
                            "kind": "EXTERNAL_SEMANTIC_AUTHORSHIP",
                            "value": True,
                        }
                    )
                if key == "operation_enum" and child is not None:
                    violations.append(
                        {
                            "path": ".".join(child_path),
                            "kind": "FIXED_OPERATION_ENUM",
                            "value": child,
                        }
                    )
                visit(child, child_path)
        elif isinstance(item, (list, tuple)):
            for index, child in enumerate(item):
                visit(child, (*path, str(index)))

    visit(value, ())
    return {
        "status": WITNESSED_STATUS if not violations else OPEN_STATUS,
        "violations": violations,
        "violation_count": len(violations),
        "truth_issued": False,
        "clean_means_no_known_external_author": True,
        "clean_does_not_prove_empirical_truth": True,
    }


def _collect_link_ids(value: Any, keys: set[str]) -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in keys and item:
                found.add(str(item))
            found.update(_collect_link_ids(item, keys))
    elif isinstance(value, (list, tuple)):
        for item in value:
            found.update(_collect_link_ids(item, keys))
    return found


def compatibility_reading_receipt(
    name: str,
    value: Mapping[str, Any],
    *,
    closure_derivation_id: str,
) -> dict[str, Any]:
    """Demote a historical materialization to a non-authoritative projection."""

    link_ids = _collect_link_ids(
        value,
        {"closure_derivation_id", "truth_derivation_id"},
    )
    return {
        "name": name,
        "present": bool(value),
        "linked_closure_derivation_ids": sorted(link_ids),
        "factors_through_current_closure": bool(
            closure_derivation_id and closure_derivation_id in link_ids
        ),
        "semantic_authority": False,
        "may_gate_interaction": False,
        "may_widen_truth": False,
        "continuity_if_unlinked": OPEN_STATUS,
    }


__all__ = [
    "OPEN_STATUS",
    "WITNESSED_STATUS",
    "ClosureWitness",
    "audit_translational_continuity",
    "combine_witnesses",
    "compatibility_reading_receipt",
    "computation_boundary_open",
    "derive_perspective_reading",
    "derive_projection_equivalence",
    "finite_horn_closure",
    "partition_signature",
    "unique_strings",
]
