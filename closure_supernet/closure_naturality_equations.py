from __future__ import annotations

"""Finite executable NRRF866 closure-naturality equations for the UI.

The formal module works with arbitrary charts, hair and arena relabellings.  A
running Supernet contract has a finite quotient instance of those objects:

* a chart is an explicit perspective reading of the source-return carrier;
* hair is the faithful display relabelling between two readings;
* the natural form is the canonical section of the reading kernel;
* pull is restriction along an explicitly listed sub-arena inclusion.

The function below derives that entire finite equation object from contract
operands.  It accepts no trusted status booleans.  Python and the browser both
recompute the object before the contract can become an interface.
"""

import hashlib
import json
from typing import Any, Mapping


PROTOCOL = "closure.supernet/closure-naturality-equations-v1"
FORMAL_MODULE = (
    "NRRF866ClosureNaturalityIsTranslationalTruthIsTheGrowthOfTheUniverse"
)
WITNESSED_STATUS = "WITNESSED"


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _digest(prefix: str, value: Any) -> str:
    content = hashlib.sha256(_stable(value).encode("utf-8")).hexdigest()
    return f"{prefix}:{content[:24]}"


def _unique_strings(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return list(
        dict.fromkeys(
            str(item) for item in value if item is not None and str(item)
        )
    )


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, (list, tuple)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def reading_kernel(reading: Mapping[str, Any]) -> list[list[str]]:
    """The finite closure fibres of one perspective reading."""

    fibres: dict[str, list[str]] = {}
    for state_id, value in reading.items():
        fibres.setdefault(str(value), []).append(str(state_id))
    return sorted(
        (sorted(members) for members in fibres.values()),
        key=lambda members: members[0] if members else "",
    )


def derive_closure_naturality_equations(
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Derive the pull/translation/fibre/growth equations of one contract."""

    status = str(contract.get("status") or "OPEN_SOURCE_BOUNDARY")
    projection = contract.get("projection")
    projection = projection if isinstance(projection, Mapping) else {}
    perspective_closure = contract.get("perspective_closure")
    perspective_closure = (
        perspective_closure
        if isinstance(perspective_closure, Mapping)
        else {}
    )

    states = [
        item
        for item in _rows(projection.get("states"))
        if item.get("id")
    ]
    carrier = sorted(str(item["id"]) for item in states)
    state_by_event = {
        str(item.get("event_id") or ""): str(item["id"])
        for item in states
        if item.get("event_id")
    }

    raw_readings = perspective_closure.get("readings")
    readings = {
        str(perspective): {
            str(state_id): str(value)
            for state_id, value in reading.items()
        }
        for perspective, reading in (
            raw_readings.items() if isinstance(raw_readings, Mapping) else []
        )
        if isinstance(reading, Mapping)
    }
    perspective_ids = sorted(readings)
    kernels = {
        perspective: reading_kernel(readings[perspective])
        for perspective in perspective_ids
    }
    common_kernel = next(iter(kernels.values()), [])
    kernels_agree = all(kernel == common_kernel for kernel in kernels.values())
    active_perspective = str(contract.get("perspective_id") or "")
    raw_projection_reading = projection.get("reading")
    projection_reading = {
        str(state_id): str(value)
        for state_id, value in (
            raw_projection_reading.items()
            if isinstance(raw_projection_reading, Mapping)
            else []
        )
    }
    active_reading_is_projection = bool(
        status != WITNESSED_STATUS
        or readings.get(active_perspective) == projection_reading
    )

    fibre_rows = [
        item
        for item in _rows(projection.get("equality_fibres"))
        if item.get("id")
    ]
    projection_kernel = sorted(
        (
            sorted(_unique_strings(item.get("member_state_ids")))
            for item in fibre_rows
        ),
        key=lambda members: members[0] if members else "",
    )
    section = {
        state_id: str(item["id"])
        for item in fibre_rows
        for state_id in _unique_strings(item.get("member_state_ids"))
    }

    translation_equations: list[dict[str, Any]] = []
    for raw in _rows(perspective_closure.get("translations")):
        source = str(raw.get("source_perspective_id") or "")
        target = str(raw.get("target_perspective_id") or "")
        expected: dict[str, str] = {}
        well_defined = source in readings and target in readings
        for state_id in carrier:
            source_value = readings.get(source, {}).get(state_id)
            target_value = readings.get(target, {}).get(state_id)
            if source_value is None or target_value is None:
                well_defined = False
                continue
            prior = expected.get(source_value)
            if prior is not None and prior != target_value:
                well_defined = False
            expected[source_value] = target_value
        raw_mapping = raw.get("display_translation")
        supplied = {
            str(key): str(value)
            for key, value in (
                raw_mapping.items() if isinstance(raw_mapping, Mapping) else []
            )
        }
        faithful = bool(
            well_defined
            and bool(raw.get("id"))
            and source != target
            and supplied == expected
            and len(set(expected)) == len(set(expected.values()))
            and kernels.get(source) == kernels.get(target)
        )
        translation_equations.append(
            {
                "id": str(raw.get("id") or ""),
                "source_perspective_id": source,
                "target_perspective_id": target,
                "derived_hair_relabelling": expected,
                "source_kernel": kernels.get(source, []),
                "target_kernel": kernels.get(target, []),
                "translation_equation_holds": faithful,
            }
        )

    translation_graph = {
        perspective: set() for perspective in perspective_ids
    }
    for equation in translation_equations:
        if not equation["translation_equation_holds"]:
            continue
        source = equation["source_perspective_id"]
        target = equation["target_perspective_id"]
        translation_graph[source].add(target)
        translation_graph[target].add(source)
    reached: set[str] = set()
    if perspective_ids:
        frontier = [perspective_ids[0]]
        reached.add(perspective_ids[0])
        while frontier:
            current = frontier.pop()
            for neighbour in translation_graph[current]:
                if neighbour not in reached:
                    reached.add(neighbour)
                    frontier.append(neighbour)
    translation_family_connected = bool(
        not perspective_ids or reached == set(perspective_ids)
    )

    lineage_ids = _unique_strings(contract.get("continuation_lineage_ids"))
    lineage_states = list(
        dict.fromkeys(
            state_by_event[event_id]
            for event_id in lineage_ids
            if event_id in state_by_event
        )
    )
    lineage_set = set(lineage_states)
    arena_order = [
        *lineage_states,
        *(state_id for state_id in carrier if state_id not in lineage_set),
    ]

    growth_stages: list[dict[str, Any]] = []
    previous_distinctions = 0
    previous_square = True
    section_counts: dict[str, int] = {}
    section_members: dict[str, list[str]] = {}
    reading_counts: dict[str, dict[str, int]] = {
        perspective: {} for perspective in perspective_ids
    }
    reading_members: dict[str, dict[str, list[str]]] = {
        perspective: {} for perspective in perspective_ids
    }
    for index, state_id in enumerate(arena_order, start=1):
        section_value = section.get(state_id)
        section_key = str(section_value)
        equal_prior_count = section_counts.get(section_key, 0)
        equal_prior_state_ids = section_members.get(section_key, [])
        translated_values = {
            perspective: readings[perspective].get(state_id)
            for perspective in perspective_ids
        }
        translated_equal_counts = {
            perspective: reading_counts[perspective].get(
                str(translated_values[perspective]), 0
            )
            for perspective in perspective_ids
        }
        translated_equal_state_ids = {
            perspective: reading_members[perspective].get(
                str(translated_values[perspective]), []
            )
            for perspective in perspective_ids
        }
        closure_prior_digest = _digest(
            "arena-fibre", equal_prior_state_ids
        )
        translated_prior_digests = {
            perspective: _digest(
                "arena-fibre", translated_equal_state_ids[perspective]
            )
            for perspective in perspective_ids
        }
        new_distinctions = index - 1 - equal_prior_count
        pair_agreement = bool(
            section_value is not None
            and all(
                translated_values[perspective] is not None
                and translated_prior_digests[perspective]
                == closure_prior_digest
                for perspective in perspective_ids
            )
        )
        square_commutes = previous_square and pair_agreement
        distinctions = previous_distinctions + new_distinctions
        growth_stages.append(
            {
                "index": index,
                "arena_size": index,
                "added_state_id": state_id,
                "pull_map_entry": [state_id, state_id],
                "translated_reading_values": translated_values,
                "translated_equal_prior_counts": translated_equal_counts,
                "translated_equal_prior_digests": translated_prior_digests,
                "closure_section_value": section_value,
                "closure_equal_prior_count": equal_prior_count,
                "closure_equal_prior_digest": closure_prior_digest,
                "new_distinctions": new_distinctions,
                "naturality_square_commutes": square_commutes,
                "distinction_count": distinctions,
                "prior_distinctions_preserved": new_distinctions >= 0,
                "strictly_grows": new_distinctions > 0,
                "at_full_reach": index == len(arena_order),
            }
        )
        section_counts[section_key] = equal_prior_count + 1
        section_members.setdefault(section_key, []).append(state_id)
        for perspective, value in translated_values.items():
            reading_key = str(value)
            reading_counts[perspective][reading_key] = (
                reading_counts[perspective].get(reading_key, 0) + 1
            )
            reading_members[perspective].setdefault(
                reading_key, []
            ).append(state_id)
        previous_square = square_commutes
        previous_distinctions = distinctions

    all_squares = all(
        stage["naturality_square_commutes"] for stage in growth_stages
    )
    all_growth = all(
        stage["prior_distinctions_preserved"] for stage in growth_stages
    )
    full_reach = bool(
        not carrier
        or (
            growth_stages
            and growth_stages[-1]["at_full_reach"]
            and growth_stages[-1]["arena_size"] == len(carrier)
            and projection_kernel == common_kernel
        )
    )
    finite_checked = bool(
        status != WITNESSED_STATUS
        or (
            carrier
            and perspective_ids
            and kernels_agree
            and active_reading_is_projection
            and projection_kernel == common_kernel
            and translation_family_connected
            and set(section) == set(carrier)
            and all(
                item["translation_equation_holds"]
                for item in translation_equations
            )
            and all_squares
            and all_growth
            and full_reach
        )
    )

    body: dict[str, Any] = {
        "protocol": PROTOCOL,
        "formal_module": FORMAL_MODULE,
        "formal_source_verified_by_runtime": False,
        "runtime_reproves_lean": False,
        "status": status,
        "active_perspective_id": contract.get("perspective_id"),
        "interactive_translation_id": contract.get(
            "interactive_translation_id"
        ),
        "operators": {
            "chart": "EXPLICIT_PERSPECTIVE_READING",
            "hair_action": "FAITHFUL_DISPLAY_RELABELING",
            "pull": "RESTRICT_READING_ALONG_ARENA_MAP",
            "natural_form": "CANONICAL_READING_KERNEL_SECTION",
            "closure_fibre": "EQUALITY_OF_NATURAL_FORMS",
        },
        "equations": {
            "pull_identity": "pull(id,c)=c",
            "pull_composition": "pull(g,pull(f,c))=pull(f∘g,c)",
            "naturality_square": (
                "naturalForm(o,pull(f,c))="
                "pull(f,naturalForm(f(o),c))"
            ),
            "translation_truth": (
                "closure(c)=closure(d) iff d=hairAct(h,c)"
            ),
            "growth": "agreement(W)<=agreement(V) along f:W→V",
        },
        "finite_instance": {
            "carrier_state_ids": carrier,
            "perspective_ids": perspective_ids,
            "reading_kernels": kernels,
            "closure_fibres": common_kernel,
            "natural_form_section": section,
            "translation_equations": translation_equations,
            "growth_order": arena_order,
            "pull_growth_stages": growth_stages,
        },
        "checks": {
            "translated_readings_have_one_closure": kernels_agree,
            "active_reading_is_projection": active_reading_is_projection,
            "translation_family_connected": translation_family_connected,
            "closure_fibres_are_translation_classes": (
                projection_kernel == common_kernel
                and translation_family_connected
            ),
            "closure_is_canonical_section": set(section) == set(carrier),
            "all_translation_equations_hold": all(
                item["translation_equation_holds"]
                for item in translation_equations
            ),
            "all_pull_naturality_squares_commute": all_squares,
            "distinctions_only_grow_with_arena": all_growth,
            "growth_saturates_at_reach": full_reach,
            "strict_growth_witnessed": any(
                stage["strictly_grows"] for stage in growth_stages
            ),
            "finite_runtime_instance_checked": finite_checked,
        },
        "boundary": {
            "runtime_is_finite_quotient_instance": True,
            "lean_theorems_are_not_reproved_by_runtime": True,
            "universe_growth_is_relational_arena_growth": True,
            "physical_cosmology_claimed": False,
            "truth_issued": False,
        },
    }
    body["id"] = _digest("closure-naturality-equations", body)
    return body


__all__ = [
    "FORMAL_MODULE",
    "PROTOCOL",
    "derive_closure_naturality_equations",
    "reading_kernel",
]
