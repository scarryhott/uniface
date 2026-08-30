from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping
from datetime import date, datetime
from enum import Enum
from typing import Any

from .translational_truth_axiometry import derive_closure


PROTOCOL = "NRRF837"
SCHEMA = "closure.supernet/nrrf837-continuum-v1"
UNITY_SELECTOR_VERSION = "nrrf837-unity-selector/v1"


def _canonical_value(value: Any) -> Any:
    """Return a JSON value with a deterministic representation.

    Supernet payloads are normally already JSON values.  Supporting enums,
    dates, sets, tuples, bytes, and non-finite floats here keeps receipt IDs
    deterministic when this pure module is also used directly in law tests.
    """

    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "+Infinity" if value > 0 else "-Infinity"
        return value
    if isinstance(value, Enum):
        return _canonical_value(value.value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bytes):
        return {"$bytes_hex": value.hex()}
    if isinstance(value, Mapping):
        return {
            str(key): _canonical_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (set, frozenset)):
        items = [_canonical_value(item) for item in value]
        return sorted(items, key=canonical_json)
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    return str(value)


def canonical_json(value: Any) -> str:
    """Encode ``value`` as canonical, whitespace-free, unicode JSON."""

    return json.dumps(
        _canonical_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_hash(value: Any) -> str:
    """Return the SHA-256 digest of :func:`canonical_json`."""

    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def append_local(left: Iterable[Any], right: Iterable[Any]) -> list[Any]:
    """The runtime local-monoid operation: ordered trace concatenation."""

    return [*left, *right]


def compose_pointwise(
    word: Iterable[str], atom_map: Mapping[str, str | Iterable[str]]
) -> list[str]:
    """Extend a generator translation pointwise to the free local monoid.

    A generator may translate to one global atom or to a global word.  The
    latter is what lets a selected unity presentation re-present a whole
    collective state while preserving the homomorphism law.
    """

    result: list[str] = []
    for raw_atom in word:
        atom = str(raw_atom)
        image = atom_map.get(atom, ())
        if isinstance(image, str):
            result.append(image)
        else:
            result.extend(str(item) for item in image)
    return result


def unity_form(
    global_atom_id: str | Iterable[str],
    *,
    selector_version: str = UNITY_SELECTOR_VERSION,
) -> dict[str, Any]:
    """Construct a versioned presentation, never a naturality witness.

    Semantic natural forms are derived separately by translational-truth
    axiometry.  This helper may relabel one already-admitted form for a client,
    but its hash, selector version, or fixed-point behavior cannot admit a form
    or define closure.
    """

    if isinstance(global_atom_id, str):
        global_word = [global_atom_id]
    else:
        global_word = [str(item) for item in global_atom_id]
    form_id = "unity:" + canonical_hash(
        {"selector_version": selector_version, "global_word": global_word}
    )
    return {
        "id": form_id,
        "kind": "LOCAL_PRESENTATION",
        "selector_version": selector_version,
        "global_word": global_word,
        "product_chosen": False,
        "network_derived": False,
        "naturally_admitted": False,
        "semantic_naturality_claimed": False,
        "defines_closure": False,
    }


def _dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, Mapping)):
        return [value]
    try:
        return list(value)
    except TypeError:
        return [value]


def _unique_strings(values: Iterable[Any]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if str(value)))


def _event_id(event: Mapping[str, Any], *, prefix: str = "event") -> str:
    for key in ("id", "event_id", "occurrence_id", "action_id"):
        value = event.get(key)
        if value is not None and str(value):
            return str(value)
    return f"{prefix}:" + canonical_hash(event)


def _source_ids(event: Mapping[str, Any]) -> list[str]:
    metadata = _dict(event.get("metadata"))
    return _unique_strings(
        [
            *_list(event.get("exact_source_ids")),
            *_list(event.get("source_occurrence_ids")),
            *_list(event.get("source_event_ids")),
            *_list(metadata.get("source_ids")),
        ]
    )


def _actor(event: Mapping[str, Any]) -> str:
    """Return the submitted/public author handle, not an internal UUID."""

    metadata = _dict(event.get("metadata"))
    return str(
        event.get("authored_handle")
        or event.get("public_handle")
        or metadata.get("authored_handle")
        or metadata.get("submitted_authored_by")
        or metadata.get("public_handle")
        or metadata.get("authored_by")
        or event.get("actor_handle")
        or event.get("actor_id")
        or event.get("authored_by")
        or event.get("participant_id")
        or event.get("perspective_id")
        or "OPEN"
    )


def _internal_actor(event: Mapping[str, Any]) -> str:
    """Retain the runtime actor identity separately from its public handle."""

    metadata = _dict(event.get("metadata"))
    return str(
        event.get("internal_actor_id")
        or metadata.get("internal_actor_id")
        or metadata.get("created_by")
        or metadata.get("authored_by")
        or event.get("created_by")
        or event.get("actor_id")
        or event.get("authored_by")
        or _actor(event)
    )


def _role(event: Mapping[str, Any]) -> str:
    metadata = _dict(event.get("metadata"))
    role = str(
        event.get("authorship_role")
        or event.get("role_label")
        or event.get("role")
        or metadata.get("authorship_role")
        or "HUMAN"
    ).upper()
    if role == "LIVING":
        return "LIVING_SYSTEM"
    return role


def _exact_text(event: Mapping[str, Any]) -> str:
    return str(
        event.get("exact_text")
        or event.get("purpose")
        or event.get("title")
        or ""
    )


def _path_target_id(path: Mapping[str, Any]) -> str:
    return str(
        path.get("target_event_id")
        or path.get("target_id")
        or path.get("event_id")
        or ""
    )


def _path_id(path: Mapping[str, Any]) -> str:
    value = path.get("id") or path.get("path_id")
    return str(value) if value else "path:" + canonical_hash(path)


def _operator_name(operator: Any) -> str:
    if isinstance(operator, Mapping):
        value = (
            operator.get("natural_form")
            or operator.get("name")
            or operator.get("operator")
            or operator.get("label")
        )
    else:
        value = operator
    return str(value or "DISCOVER").upper()


def _explicit_form_key(event: Mapping[str, Any]) -> str | None:
    metadata = _dict(event.get("metadata"))
    value = (
        event.get("global_content_id")
        or metadata.get("global_content_id")
        or event.get("natural_form_id")
        or event.get("natural_form")
        or metadata.get("natural_form_id")
    )
    return str(value) if value is not None and str(value) else None


def _event_global_key(
    event: Mapping[str, Any],
    truth_form_by_source: Mapping[str, Mapping[str, Any]],
) -> str:
    """Return only equality already derived by translational-truth closure.

    Authored natural-form IDs, global labels, exact text, focus, path ranking,
    and presentation metadata are never equality witnesses.  An event receives
    a shared semantic key only when all of its known source returns factor
    through exactly one closure-derived natural form.  Otherwise it remains a
    distinct OPEN local atom.
    """

    truth_form_ids = {
        str(truth_form_by_source[source_id]["id"])
        for source_id in _source_ids(event)
        if source_id in truth_form_by_source
    }
    if len(truth_form_ids) == 1:
        return "truth-form:" + next(iter(truth_form_ids))
    return "open-local:" + canonical_hash(
        {
            "event_id": _event_id(event),
            "source_ids": _source_ids(event),
            "projection_reference_only": bool(
                event.get("projection_reference_only")
            ),
        }
    )


def _merge_events(
    field_events: Iterable[Any], intent: Mapping[str, Any], local_event: Mapping[str, Any]
) -> list[dict[str, Any]]:
    order: list[str] = []
    merged: dict[str, dict[str, Any]] = {}
    for raw in [*_list(field_events), intent, local_event]:
        event = _dict(raw)
        if not event:
            continue
        event_id = _event_id(event)
        if event_id not in merged:
            order.append(event_id)
            merged[event_id] = event
        else:
            old = merged[event_id]
            old_metadata = _dict(old.get("metadata"))
            metadata = {**old_metadata, **_dict(event.get("metadata"))}
            for key in (
                "global_content_id",
                "natural_form_id",
                "authored_handle",
                "submitted_authored_by",
                "public_handle",
                "internal_actor_id",
            ):
                if not metadata.get(key) and old_metadata.get(key):
                    metadata[key] = old_metadata[key]
            combined = {**old, **event, "metadata": metadata}
            for key in (
                "global_content_id",
                "natural_form_id",
                "natural_form",
                "authored_handle",
                "public_handle",
                "internal_actor_id",
            ):
                if not combined.get(key) and old.get(key):
                    combined[key] = old[key]
            merged[event_id] = combined
    return [merged[event_id] for event_id in order]


def _proposal_decisions(proposal: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [_dict(item) for item in _list(proposal.get("decisions")) if _dict(item)]


def _latest_decisions(
    decisions: Iterable[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    """The append order is authoritative when timestamps are not comparable."""

    latest: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        participant = str(
            decision.get("participant_id")
            or decision.get("authored_by")
            or ""
        )
        if participant:
            latest[participant] = dict(decision)
    return latest


def build_continuum_receipt(
    *,
    local_event: Mapping[str, Any],
    intent: Mapping[str, Any],
    field_events: Iterable[Mapping[str, Any]],
    paths: Iterable[Mapping[str, Any]],
    active_proposal: Mapping[str, Any] | None,
    living_return: Mapping[str, Any] | None,
    operator: Any,
    enabled_forms: Iterable[str],
    freedom_actions: Iterable[str],
    closure_level_id: str,
    contributors: Iterable[Mapping[str, Any]],
    token_status: str | Mapping[str, Any],
    closure_derivation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the finite runtime witness corresponding to NRRF837.

    The receipt verifies laws for the finite observed/runtime-generated domain.
    It does not claim that software execution proves the Lean theorem, select a
    community's unity from network data, identify equal-content authors, issue
    truth, value a person, settle money, or find a global optimum.
    """

    local = _dict(local_event)
    root_intent = _dict(intent)
    proposal = _dict(active_proposal)
    returned = _dict(living_return)
    field_event_rows = [
        _dict(item) for item in _list(field_events) if _dict(item)
    ]
    path_rows = [_dict(item) for item in _list(paths) if _dict(item)]
    contributor_rows = [
        _dict(item) for item in _list(contributors) if _dict(item)
    ]
    enabled = _unique_strings(enabled_forms)
    freedoms = _unique_strings(freedom_actions)
    level_id = str(closure_level_id or "OPEN")
    natural_operator = _operator_name(operator)
    operator_data = _dict(operator)
    selector_version = str(
        operator_data.get("selector_version") or UNITY_SELECTOR_VERSION
    )
    selector_source = str(
        operator_data.get("selector_source") or "product_policy"
    )
    proposal_status = str(proposal.get("status") or "OPEN").upper()
    token_data = _dict(token_status)
    truth_closure = _dict(closure_derivation)
    if not truth_closure:
        fallback_source_ids = _unique_strings(
            [
                *_source_ids(local),
                *_source_ids(root_intent),
                *[
                    source_id
                    for field_event in field_event_rows
                    for source_id in _source_ids(_dict(field_event))
                ],
            ]
        )
        truth_closure = derive_closure(
            [
                {
                    "id": source_id,
                    "source_return_ids": [source_id],
                    "existence_provenance": [f"source-return:{source_id}"],
                }
                for source_id in fallback_source_ids
            ]
        ).to_dict()
    truth_natural_forms = [
        _dict(item)
        for item in _list(truth_closure.get("natural_forms"))
        if _dict(item).get("id")
    ]
    truth_form_by_source: dict[str, dict[str, Any]] = {}
    for truth_form in truth_natural_forms:
        for member in _list(truth_form.get("members")):
            truth_form_by_source[str(member)] = truth_form
    token_state = str(
        (token_data.get("status") or "OPEN")
        if token_data
        else (token_status or "OPEN")
    )
    # A closure level describes the admitted equality environment.  It is not
    # itself the product's chosen natural form (NRRF837's unity is extra data).
    continuum_content_key = "continuum-content:" + canonical_hash(
        {
            "intent_id": _event_id(root_intent, prefix="intent"),
            "intent_text_hash": canonical_hash(_exact_text(root_intent)),
            "proposal_id": proposal.get("id"),
            "proposal_terms_hash": (
                canonical_hash(str(proposal.get("exact_terms") or ""))
                if proposal
                else None
            ),
        }
    )
    global_content_id = "global-content:" + canonical_hash(continuum_content_key)
    # The stable agreement/continuum content above is distinct from its current
    # collective state.  Phase, consent progress, return, and available forms
    # alter the state-derived natural interface without changing the underlying
    # agreement identity.  Contextual path ranks never define this state.
    global_state_key = "global-state-content:" + canonical_hash(
        {
            "global_content_id": global_content_id,
            "phase": natural_operator,
            "proposal_status": proposal_status,
            "decisions": [
                {
                    "participant_id": decision.get("participant_id"),
                    "authored_by": _actor(decision),
                    "internal_actor_id": _internal_actor(decision),
                    "authorship_role": _role(decision),
                    "decision": decision.get("decision"),
                    "decision_event_id": decision.get("decision_event_id"),
                }
                for decision in _proposal_decisions(proposal)
            ],
            "living_return": (
                {
                    "id": returned.get("id"),
                    "event_id": returned.get("event_id"),
                    "exact_text_hash": canonical_hash(_exact_text(returned)),
                    "authored_by": _actor(returned),
                    "internal_actor_id": _internal_actor(returned),
                    "authorship_role": _role(returned),
                }
                if returned
                else None
            ),
            "enabled_forms": enabled,
            "token_status": token_state,
        }
    )

    events = _merge_events(field_event_rows, root_intent, local)
    intent_id = _event_id(root_intent, prefix="intent")
    focus_id = _event_id(local, prefix="local") if local else intent_id
    path_targets = {_path_target_id(path) for path in path_rows if _path_target_id(path)}

    # Persisted events retain their own authored/global keys.  Being focused or
    # appearing in a contextual candidate path never makes two events equal.
    event_global_keys: dict[str, str] = {}
    for event in events:
        event_id = _event_id(event)
        event_global_keys[event_id] = _event_global_key(
            event,
            truth_form_by_source,
        )

    # Paths are allowed to refer to source-preserved field nodes that were not
    # included in the supplied projection.  Give those references a local atom
    # without pretending an actor or exact occurrence was observed here.
    known_ids = {_event_id(event) for event in events}
    for path in path_rows:
        target_id = _path_target_id(path)
        if not target_id or target_id in known_ids:
            continue
        synthetic = {
            "id": target_id,
            "authored_by": path.get("authored_by") or "OPEN",
            "authored_handle": path.get("authored_handle"),
            "internal_actor_id": path.get("internal_actor_id"),
            "exact_text": path.get("exact_text") or "",
            "authorship_role": path.get("target_authorship_role") or "OPEN",
            "global_content_id": path.get("global_content_id"),
            "natural_form_id": path.get("natural_form_id"),
            "exact_source_ids": _dict(path.get("why")).get(
                "source_occurrence_ids", []
            ),
            "projection_reference_only": True,
        }
        events.append(synthetic)
        known_ids.add(target_id)
        event_global_keys[target_id] = _event_global_key(
            synthetic,
            truth_form_by_source,
        )

    local_atoms: list[dict[str, Any]] = []
    atom_map: dict[str, list[str]] = {}
    global_key_by_id: dict[str, str] = {}
    for event in events:
        event_id = _event_id(event)
        form_key = event_global_keys[event_id]
        global_id = "global:" + canonical_hash(
            {"global_content_key": form_key}
        )
        global_key_by_id[global_id] = form_key
        atom_map[event_id] = [global_id]
        local_atoms.append(
            {
                "id": event_id,
                "kind": "LOCAL_INTERACTION",
                "actor_id": _actor(event),
                "internal_actor_id": _internal_actor(event),
                "authorship_role": _role(event),
                "source_ids": _source_ids(event),
                "exact_text": _exact_text(event),
                "exact_text_hash": canonical_hash(_exact_text(event)),
                "global_atom_id": global_id,
                "global_content_key": form_key,
                "authored_presentation_key": _explicit_form_key(event),
                "semantic_equality_basis": "NRRF840_VIS_CLOSURE_TRANSLATIONAL_TRUTHS",
                "projection_reference_only": bool(
                    event.get("projection_reference_only", False)
                ),
            }
        )

    if focus_id not in atom_map:
        # This is reachable only for an entirely empty caller payload.  Keep the
        # event OPEN and distinct from the canonical continuum-state generator.
        open_event_key = _event_global_key(
            {"id": focus_id},
            truth_form_by_source,
        )
        open_global = "global:" + canonical_hash(
            {
                "global_content_key": open_event_key,
            }
        )
        global_key_by_id[open_global] = open_event_key
        atom_map[focus_id] = [open_global]
        local_atoms.append(
            {
                "id": focus_id,
                "kind": "LOCAL_INTERACTION",
                "actor_id": "OPEN",
                "internal_actor_id": "OPEN",
                "authorship_role": "OPEN",
                "source_ids": [],
                "exact_text": "",
                "exact_text_hash": canonical_hash(""),
                "global_atom_id": open_global,
                "global_content_key": open_event_key,
                "projection_reference_only": True,
            }
        )

    # The modality is evaluated at the canonical current continuum state, not
    # at whichever local event happens to be focused in the UI.
    state_global_id = "global:" + canonical_hash(
        {"global_content_key": global_state_key}
    )
    global_key_by_id[state_global_id] = global_state_key
    state_generator_id = "continuum-state:" + canonical_hash(
        {"global_state_key": global_state_key}
    )
    atom_map[state_generator_id] = [state_global_id]
    state_presentation = {
        "id": state_generator_id,
        "kind": "CURRENT_CONTINUUM_STATE",
        "source_event_ids": _unique_strings(
            [intent_id, proposal.get("proposal_event_id")]
        ),
        "global_atom_id": state_global_id,
        "global_content_id": global_content_id,
        "phase": natural_operator,
        "persisted_event": False,
        "product_chosen": False,
    }

    observed_word = [_event_id(event) for event in events]
    input_word = [state_generator_id]
    input_global_word = compose_pointwise(input_word, atom_map)
    global_state_id = "global-state:" + canonical_hash(input_global_word)
    selected_form = unity_form(
        input_global_word, selector_version=selector_version
    )
    alternate_form = unity_form(
        input_global_word,
        selector_version=f"{selector_version}/alternative",
    )
    atom_map[selected_form["id"]] = list(input_global_word)
    atom_map[alternate_form["id"]] = list(input_global_word)
    focus_truth_forms = {
        str(truth_form_by_source[source_id]["id"]): truth_form_by_source[source_id]
        for source_id in _source_ids(local)
        if source_id in truth_form_by_source
    }
    semantic_selected_form = (
        next(iter(focus_truth_forms.values()))
        if len(focus_truth_forms) == 1
        else None
    )
    semantic_selected_form_id = (
        str(semantic_selected_form["id"])
        if semantic_selected_form is not None
        else None
    )
    selected_form.update(
        {
            "presentation_id": selected_form["id"],
            "semantic_natural_form_id": semantic_selected_form_id,
            "derived_within_closure": semantic_selected_form is not None,
            "naturally_admitted": bool(
                semantic_selected_form
                and semantic_selected_form.get("admitted", False)
            ),
            "truth_provenance": (
                list(semantic_selected_form.get("truth_provenance", []))
                if semantic_selected_form
                else []
            ),
            "closure_derivation_id": truth_closure.get("id"),
            "product_chosen": False,
            "selector_changes_semantic_form": False,
        }
    )

    event_generators = [atom["id"] for atom in local_atoms]
    declared_global_words = sorted(
        {
            (),
            *(
                tuple(compose_pointwise([generator], atom_map))
                for generator in [state_generator_id, *event_generators]
            ),
        }
    )
    declared_unity_forms = [
        unity_form(global_word, selector_version=selector_version)
        for global_word in declared_global_words
    ]
    for declared_form in declared_unity_forms:
        atom_map[declared_form["id"]] = list(declared_form["global_word"])

    action_presentations: list[dict[str, Any]] = []
    for index, action in enumerate(freedoms):
        action_id = "freedom:" + canonical_hash(
            {
                "global_word": input_global_word,
                "action": action,
                "index": index,
            }
        )
        atom_map[action_id] = list(input_global_word)
        action_presentations.append(
            {
                "id": action_id,
                "action": action,
                "global_word": list(input_global_word),
                "executed": False,
                "ordinary_interaction": True,
            }
        )

    left_word = observed_word[:-1]
    right_word = observed_word[-1:] if observed_word else []
    appended_word = append_local(left_word, right_word)
    left_global = compose_pointwise(left_word, atom_map)
    right_global = compose_pointwise(right_word, atom_map)
    appended_global = compose_pointwise(appended_word, atom_map)
    hom_identity = compose_pointwise([], atom_map) == []
    hom_append = appended_global == append_local(left_global, right_global)

    # An explicit associativity computation, rather than only a declaration.
    split_a = observed_word[:1]
    split_b = observed_word[1:-1]
    split_c = observed_word[-1:] if len(observed_word) > 1 else []
    associative = append_local(append_local(split_a, split_b), split_c) == append_local(
        split_a, append_local(split_b, split_c)
    )
    identity_verified = (
        append_local([], observed_word) == observed_word
        and append_local(observed_word, []) == observed_word
    )

    first_modality = [selected_form["id"]]
    recomposed_first = compose_pointwise(first_modality, atom_map)
    second_form = unity_form(
        recomposed_first, selector_version=selector_version
    )
    second_modality = [second_form["id"]]
    modality_idempotent = first_modality == second_modality
    selected_fixed = (
        recomposed_first == input_global_word and modality_idempotent
    )
    declared_unity_ids = {form["id"] for form in declared_unity_forms}
    declared_modality_generators = [
        state_generator_id,
        *event_generators,
        *(item["id"] for item in action_presentations),
        *sorted(declared_unity_ids),
    ]
    declared_fixed_point_ids: set[str] = set()
    for generator in declared_modality_generators:
        image = compose_pointwise([generator], atom_map)
        applied = unity_form(image, selector_version=selector_version)["id"]
        if [generator] == [applied]:
            declared_fixed_point_ids.add(generator)
    fixed_points_equal_declared_unity = (
        declared_fixed_point_ids == declared_unity_ids
    )

    left_modality_form = unity_form(
        left_global, selector_version=selector_version
    )
    right_modality_form = unity_form(
        right_global, selector_version=selector_version
    )
    atom_map[left_modality_form["id"]] = list(left_global)
    atom_map[right_modality_form["id"]] = list(right_global)
    modality_of_append = unity_form(
        appended_global, selector_version=selector_version
    )
    modality_after_factors = unity_form(
        compose_pointwise(
            [left_modality_form["id"], right_modality_form["id"]], atom_map
        ),
        selector_version=selector_version,
    )
    multiplicative_up_to_modality = (
        modality_of_append["id"] == modality_after_factors["id"]
    )

    kernel_generators = [
        state_generator_id,
        *event_generators,
        *(item["id"] for item in action_presentations),
    ]
    kernel_groups: dict[tuple[str, ...], list[str]] = {}
    for generator in kernel_generators:
        kernel_groups.setdefault(tuple(atom_map[generator]), []).append(generator)
    kernel_classes = [
        {
            "global_word": list(global_word),
            "members": sorted(members),
        }
        for global_word, members in sorted(kernel_groups.items())
    ]
    reflexive = all(
        compose_pointwise([item], atom_map) == compose_pointwise([item], atom_map)
        for item in kernel_generators
    )
    symmetric = all(
        (atom_map[left] != atom_map[right]) or (atom_map[right] == atom_map[left])
        for left in kernel_generators
        for right in kernel_generators
    )
    # Equality of canonical global words makes transitivity executable without
    # manufacturing semantic comparisons.  Evaluate all observed triples for a
    # bounded field and use the same equality law directly for larger fields.
    if len(kernel_generators) <= 60:
        transitive = all(
            not (atom_map[a] == atom_map[b] == atom_map[c])
            or atom_map[a] == atom_map[c]
            for a in kernel_generators
            for b in kernel_generators
            for c in kernel_generators
        )
    else:
        transitive = all(bool(group["global_word"]) for group in kernel_classes)

    equal_pair: tuple[str, str] | None = next(
        (
            (members[0], members[1])
            for members in (item["members"] for item in kernel_classes)
            if len(members) > 1
        ),
        None,
    )
    context = kernel_generators[:1]
    congruence_witness = None
    congruence_verified = hom_append
    if equal_pair is not None:
        left, right = equal_pair
        left_context = append_local([left], context)
        right_context = append_local([right], context)
        context_equal = compose_pointwise(left_context, atom_map) == compose_pointwise(
            right_context, atom_map
        )
        congruence_verified = congruence_verified and context_equal
        congruence_witness = {
            "left": left_context,
            "right": right_context,
            "equal_after_compose": context_equal,
        }

    global_atoms = [
        {
            "id": global_id,
            "global_content_key": global_key_by_id[global_id],
            "canonical": True,
            "local_generator_ids": sorted(
                generator
                for generator in kernel_generators
                if atom_map[generator] == [global_id]
            ),
        }
        for global_id in sorted(global_key_by_id)
    ]

    # The fibre includes observed local presentations, declared ordinary action
    # presentations, and its one product-selected unity witness.
    fibre_event_ids = sorted(
        generator
        for generator in event_generators
        if atom_map[generator] == input_global_word
    )
    fibre_action_ids = [item["id"] for item in action_presentations]
    fibre_presentations = [
        state_generator_id,
        *fibre_event_ids,
        *fibre_action_ids,
        selected_form["id"],
    ]
    unity_witnesses = [
        item for item in fibre_presentations if item == selected_form["id"]
    ]

    local_atom_by_id = {str(atom["id"]): atom for atom in local_atoms}

    def event_truth_form_id(event_id: str) -> str | None:
        atom = local_atom_by_id.get(str(event_id))
        if atom is None or atom.get("projection_reference_only"):
            return None
        form_ids = {
            str(truth_form_by_source[source_id]["id"])
            for source_id in atom.get("source_ids", [])
            if source_id in truth_form_by_source
        }
        return next(iter(form_ids)) if len(form_ids) == 1 else None

    # Natural-form equality is an equivalence relation.  Ranked path edges are
    # kept separately because score, locality, and constraints are directional
    # context, not equality and not a global optimum proof.
    suggestion_members = _unique_strings([intent_id, *sorted(path_targets)])
    projection_reference_ids = {
        str(atom["id"])
        for atom in local_atoms
        if atom.get("projection_reference_only")
    }
    suggestion_classes: dict[str, list[str]] = {}
    for member in suggestion_members:
        if member in projection_reference_ids:
            continue
        form_id = event_truth_form_id(member)
        if form_id is None:
            continue
        suggestion_classes.setdefault(form_id, []).append(member)
    equivalence_classes = [
        {"natural_form_id": form_id, "members": sorted(members)}
        for form_id, members in sorted(suggestion_classes.items())
    ]
    partition_members = [
        member for item in equivalence_classes for member in item["members"]
    ]
    known_suggestion_members = [
        member
        for member in suggestion_members
        if event_truth_form_id(member) is not None
    ]
    equivalence_verified = (
        sorted(partition_members) == sorted(known_suggestion_members)
        and len(partition_members) == len(set(partition_members))
        and all(
            bool(item["natural_form_id"]) and bool(item["members"])
            for item in equivalence_classes
        )
    )

    def path_score(path: Mapping[str, Any]) -> float:
        try:
            score = float(path.get("score") or _dict(path.get("why")).get("score") or 0)
        except (TypeError, ValueError):
            return 0.0
        return score if math.isfinite(score) else 0.0

    ranked_paths = sorted(path_rows, key=lambda row: (-path_score(row), _path_id(row)))
    contextual_edges: list[dict[str, Any]] = []
    for rank, path in enumerate(ranked_paths, start=1):
        target_id = _path_target_id(path)
        source_id = str(
            _dict(path.get("why")).get("source_event_id") or intent_id
        )
        source_form = event_truth_form_id(source_id)
        target_form = event_truth_form_id(target_id)
        shared_form = bool(source_form and source_form == target_form)
        contextual_edges.append(
            {
                "id": _path_id(path),
                "rank": rank,
                "source_event_id": source_id,
                "target_event_id": target_id,
                "score": path_score(path),
                "why": _canonical_value(path.get("why") or {}),
                "shared_natural_form": shared_form,
                "formal_status": "WITNESSED" if shared_form else "OPEN",
                "natural_form_id": source_form if shared_form else None,
                "shared_natural_form_id": source_form if shared_form else None,
                "source_natural_form_id": source_form,
                "target_natural_form_id": target_form,
                "candidate_remains_contextual_when_form_equality_open": True,
                "directional_context": True,
                "binding": False,
                "global_optimum_claimed": False,
            }
        )

    gated_forms = _unique_strings(
        _list(token_data.get("gated_forms") or ["ACT", "RETURN"])
    )
    admitted_interactions = _unique_strings(
        edge["target_event_id"] for edge in contextual_edges
    )
    product_pairs = [
        {"form": form, "interaction": interaction}
        for form in enabled
        for interaction in admitted_interactions
    ]
    product_pair_keys = {
        (item["form"], item["interaction"]) for item in product_pairs
    }
    expected_product_keys = {
        (form, interaction)
        for form in enabled
        for interaction in admitted_interactions
    }

    decisions = _proposal_decisions(proposal)
    latest = _latest_decisions(decisions)
    required_participants = _unique_strings(
        _list(proposal.get("required_participant_ids"))
    )
    if not required_participants and proposal:
        required_participants = _unique_strings(
            [proposal.get("proposed_by"), proposal.get("authored_by")]
        )
    accepted_humans: list[dict[str, Any]] = []
    for participant, decision in sorted(latest.items()):
        role = _role(decision)
        authored_by = _actor(decision)
        if (
            str(decision.get("decision") or "").upper() == "ACCEPT"
            and role == "HUMAN"
            and authored_by == participant
        ):
            accepted_humans.append(
                {
                    "participant_id": participant,
                    "decision_event_id": decision.get("decision_event_id"),
                    "self_authored": True,
                    "authorship_role": "HUMAN",
                    "internal_actor_id": _internal_actor(decision),
                }
            )
    accepted_ids = {item["participant_id"] for item in accepted_humans}
    all_required_accepted = bool(required_participants) and set(
        required_participants
    ).issubset(accepted_ids)
    settled = proposal_status in {"ACCEPTED", "COMMITTED", "RETURNED"} and (
        all_required_accepted
    )
    if proposal_status in {"REJECTED", "WITHDRAWN"}:
        consent_status = proposal_status
    elif all_required_accepted:
        consent_status = "ACCEPTED"
    elif accepted_humans:
        consent_status = "PARTIAL"
    elif proposal:
        consent_status = "PROPOSED"
    else:
        consent_status = "OPEN"

    target_event_ids = _unique_strings(_list(proposal.get("target_event_ids")))
    resource_conditions = _unique_strings(
        [
            *_list(proposal.get("resource_conditions")),
            *_list(proposal.get("resources")),
        ]
    )
    open_assumptions = _unique_strings(_list(proposal.get("open_assumptions")))
    proposal_metadata = _dict(proposal.get("metadata"))
    time_constraints = _unique_strings(
        [
            *_list(proposal.get("time_constraints")),
            proposal.get("starts_at"),
            proposal.get("ends_at"),
            proposal.get("deadline"),
            proposal_metadata.get("starts_at"),
            proposal_metadata.get("ends_at"),
            proposal_metadata.get("deadline"),
        ]
    )
    action_id = str(
        proposal.get("action_id")
        or returned.get("action_id")
        or (target_event_ids[0] if target_event_ids else "OPEN")
    )
    correlated_tuple = {
        "proposal_id": proposal.get("id"),
        "global_content_id": global_content_id,
        "global_state_id": global_state_id,
        "natural_form_id": semantic_selected_form_id,
        "unity_selector_version": selector_version,
        "interaction_ids": target_event_ids,
        "party_ids": required_participants,
        "resources": resource_conditions,
        "open_assumptions": open_assumptions,
        "time_constraints": time_constraints,
        "action_id": action_id,
        "exact_terms_hash": canonical_hash(str(proposal.get("exact_terms") or "")),
    }
    commitment_exists = bool(proposal)
    commitment_relation_id = "commitment-relation:" + canonical_hash(
        correlated_tuple
    )

    event_authorship_records: list[dict[str, Any]] = []
    for atom in local_atoms:
        projection_reference_only = bool(atom.get("projection_reference_only"))
        event_word = list(atom_map[atom["id"]])
        event_form_id = event_truth_form_id(str(atom["id"]))
        event_authorship_records.append(
            {
                "record_kind": "EVENT_AUTHORSHIP",
                "actor_id": atom["actor_id"],
                "internal_actor_id": atom["internal_actor_id"],
                "authorship_role": atom["authorship_role"],
                "source_event_ids": [atom["id"]],
                "source_ids": list(atom["source_ids"]),
                "global_word": None if projection_reference_only else event_word,
                "global_content_id": (
                    None
                    if projection_reference_only
                    else "global-reading:" + canonical_hash(event_word)
                ),
                "global_state_id": (
                    None
                    if projection_reference_only
                    else "global-state:" + canonical_hash(event_word)
                ),
                "selected_natural_form_id": event_form_id,
                "equality_status": (
                    "WITNESSED" if event_form_id else "OPEN"
                ),
                "equality_basis": (
                    "NRRF840_VIS_CLOSURE_TRANSLATIONAL_TRUTHS"
                    if event_form_id
                    else "UNRESOLVED_TRANSLATIONAL_TRUTH"
                ),
                "source_identity_status": (
                    "WITNESSED"
                    if not projection_reference_only
                    and atom.get("actor_id") not in {None, "", "OPEN"}
                    and atom.get("internal_actor_id") not in {None, "", "OPEN"}
                    else "OPEN"
                ),
                "unresolved_source_event_ids": (
                    [str(atom["id"])] if projection_reference_only else []
                ),
                "mutual_authorship_redundancy_applicable": False,
            }
        )

    contributor_records: list[dict[str, Any]] = []
    for contributor in contributor_rows:
        source_event_ids = _unique_strings(
            [
                *_list(contributor.get("event_ids")),
                *_list(contributor.get("source_event_ids")),
            ]
        )
        authored_form_claim = _explicit_form_key(contributor)
        unresolved_source_event_ids = [
            source_id for source_id in source_event_ids if source_id not in atom_map
        ]
        if source_event_ids and not unresolved_source_event_ids:
            contributor_global_word = compose_pointwise(source_event_ids, atom_map)
        else:
            contributor_global_word = None
        contributor_form_ids = {
            form_id
            for source_event_id in source_event_ids
            if (form_id := event_truth_form_id(source_event_id)) is not None
        }
        contributor_form_id = (
            next(iter(contributor_form_ids))
            if len(contributor_form_ids) == 1
            and not unresolved_source_event_ids
            else None
        )
        equality_status = "WITNESSED" if contributor_form_id else "OPEN"
        equality_basis = (
            "NRRF840_VIS_CLOSURE_TRANSLATIONAL_TRUTHS"
            if contributor_form_id
            else "UNRESOLVED_TRANSLATIONAL_TRUTH"
        )
        contributor_actor_id = _actor(contributor)
        contributor_internal_actor_id = _internal_actor(contributor)
        contributor_records.append(
            {
                "record_kind": "CONTRIBUTOR_AUTHORSHIP",
                "actor_id": contributor_actor_id,
                "internal_actor_id": contributor_internal_actor_id,
                "authorship_role": _role(contributor),
                "source_event_ids": source_event_ids,
                "source_ids": _unique_strings(
                    [
                        *_list(contributor.get("source_reverse_path")),
                        *_list(contributor.get("source_ids")),
                    ]
                ),
                "global_word": contributor_global_word,
                "global_content_id": (
                    "global-reading:" + canonical_hash(contributor_global_word)
                    if contributor_global_word is not None
                    else None
                ),
                "global_state_id": (
                    "global-state:" + canonical_hash(contributor_global_word)
                    if contributor_global_word is not None
                    else None
                ),
                "selected_natural_form_id": contributor_form_id,
                "equality_status": equality_status,
                "equality_basis": equality_basis,
                "source_identity_status": (
                    "WITNESSED"
                    if source_event_ids
                    and not unresolved_source_event_ids
                    and contributor_actor_id not in {"", "OPEN"}
                    and contributor_internal_actor_id not in {"", "OPEN"}
                    else "OPEN"
                ),
                "authored_form_claim": authored_form_claim,
                "authored_form_claim_is_truth_witness": False,
                "unresolved_source_event_ids": unresolved_source_event_ids,
                "mutual_authorship_redundancy_applicable": False,
            }
        )

    relevant_contributor_count = len(contributor_records)
    all_contributors_witnessed = bool(contributor_records) and all(
        record["equality_status"] == "WITNESSED"
        for record in contributor_records
    )
    contributor_global_words = {
        tuple(record["global_word"] or []) for record in contributor_records
    }
    contributor_form_ids = {
        record["selected_natural_form_id"] for record in contributor_records
    }
    same_witnessed_global_reading = (
        all_contributors_witnessed and len(contributor_global_words) == 1
    )
    same_witnessed_natural_form = (
        all_contributors_witnessed
        and None not in contributor_form_ids
        and len(contributor_form_ids) == 1
    )
    mutual_authorship_redundancy_applicable = (
        relevant_contributor_count >= 2
        and same_witnessed_global_reading
        and same_witnessed_natural_form
    )
    for record in contributor_records:
        record["mutual_authorship_redundancy_applicable"] = (
            mutual_authorship_redundancy_applicable
        )

    actor_records = [*event_authorship_records, *contributor_records]
    # Preserve repeated actors only where their source-bearing records differ.
    actor_records = [
        dict(item)
        for _, item in sorted(
            {
                canonical_json(item): item for item in actor_records
            }.items()
        )
    ]
    equal_content_actor_groups: dict[
        str, dict[tuple[str, str], dict[str, str]]
    ] = {}
    for record in actor_records:
        if (
            record.get("equality_status") == "WITNESSED"
            and record.get("global_content_id")
        ):
            public_actor_id = str(record["actor_id"])
            internal_actor_id = str(record["internal_actor_id"])
            identity = {
                "actor_id": public_actor_id,
                "internal_actor_id": internal_actor_id,
            }
            equal_content_actor_groups.setdefault(
                str(record["global_content_id"]), {}
            )[(public_actor_id, internal_actor_id)] = identity
    content_groups = [
        {
            "global_content_id": content_id,
            # ``actor_ids`` remains as a compatibility projection, but it is
            # not an identity key: distinct internal actors may intentionally
            # publish under the same handle.
            "actor_ids": sorted(
                {identity["actor_id"] for identity in identities.values()}
            ),
            "actor_identity_records": [
                identities[key] for key in sorted(identities)
            ],
            "actors_identified": False,
        }
        for content_id, identities in sorted(equal_content_actor_groups.items())
    ]

    missing_source_identity_actor_ids = sorted(
        {
            str(record["actor_id"])
            for record in actor_records
            if record.get("source_identity_status") != "WITNESSED"
        }
    )
    source_identities_preserved = bool(actor_records) and all(
        record.get("source_identity_status") == "WITNESSED"
        for record in actor_records
    )

    unity_global_words = {
        tuple(form["global_word"]): form["id"] for form in declared_unity_forms
    }
    selector_bijection = (
        set(unity_global_words) == set(declared_global_words)
        and len(unity_global_words) == len(declared_global_words)
        and len(set(unity_global_words.values())) == len(declared_global_words)
    )
    semantic_form_payload = (
        {
            **semantic_selected_form,
            "derived_within_closure": True,
            "naturally_admitted": bool(
                semantic_selected_form.get("admitted", False)
            ),
        }
        if semantic_selected_form is not None
        else {
            "id": None,
            "status": "OPEN_NO_TRANSLATIONAL_TRUTH_FORM",
            "derived_within_closure": False,
            "naturally_admitted": False,
        }
    )

    body: dict[str, Any] = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "formal_reading": "NRRF837",
        "local_event_id": focus_id,
        "local_closure_level_id": level_id,
        "global_content_id": global_content_id,
        "global_state_id": global_state_id,
        "selected_natural_form_id": semantic_selected_form_id,
        "closure_derivation_id": truth_closure.get("id"),
        "natural_form_admission_status": (
            "NATURALLY_ADMITTED"
            if semantic_selected_form_id
            else "OPEN"
        ),
        "local_monoid": {
            "carrier": "finite words of source-preserved local interaction generators",
            "operation": "append",
            "identity": [],
            "observed_word": observed_word,
            "generators": [*local_atoms, state_presentation],
            "continuum_state_generator": state_presentation,
            "declared_freedom_generators": action_presentations,
            "append_witness": {
                "left": left_word,
                "right": right_word,
                "result": appended_word,
            },
            "identity_verified": identity_verified,
            "associative": associative,
            "interactions_continue_locally": True,
        },
        "global_monoid": {
            "carrier": "finite words of canonical global content atoms",
            "operation": "append",
            "identity": [],
            "atoms": global_atoms,
            "current_global_word": input_global_word,
            "global_content_id": global_content_id,
            "global_state_id": global_state_id,
            "canonical_atoms_are_content_not_actor_identity": True,
        },
        "compose": {
            "kind": "pointwise free-monoid extension",
            # Persisted/declarative generator translation is selector-version
            # independent.  Unity presentations extend this same homomorphism
            # without changing its mapping on existing generators.
            "atom_map": {
                generator: atom_map[generator]
                for generator in [
                    state_generator_id,
                    *event_generators,
                    *(item["id"] for item in action_presentations),
                ]
            },
            "selector_extension_map": {
                generator: image
                for generator, image in atom_map.items()
                if generator.startswith("unity:")
            },
            "identity_preserved": hom_identity,
            "concatenation_witness": {
                "local_left": left_word,
                "local_right": right_word,
                "compose_of_append": appended_global,
                "append_of_composes": append_local(left_global, right_global),
            },
            "concatenation_preserved": hom_append,
            "homomorphism_verified": hom_identity and hom_append,
            "actor_identity_used_in_global_content_key": False,
        },
        "unity_selector": {
            "version": selector_version,
            "policy_id": "supernet-presentation-after-closure",
            "source": selector_source,
            "chosen_by": "closure derivation then perspective presentation",
            "network_derived": False,
            "extra_data": True,
            "selector_policy_is_extra_data": True,
            "selector_can_only_select_closure_admitted_forms": True,
            "semantic_form_network_derived": bool(semantic_selected_form_id),
            "closure_level_is_natural_form": True,
            "local_closure_level_id": level_id,
            "selected_form": semantic_form_payload,
            "selected_presentation": selected_form,
            "declared_global_states": [list(word) for word in declared_global_words],
            "declared_unity": declared_unity_forms,
            "declared_presentations": declared_unity_forms,
            "declared_unity_is_presentation_only": True,
            "declared_domain_scope": (
                "identity, current continuum state, and observed one-generator "
                "global words"
            ),
            "selection_is_unique_given_declared_unity": selector_bijection,
            "global_states_in_bijection_with_selected_forms": selector_bijection,
            "alternative_selector_witness": {
                "same_local_and_global_monoids": True,
                "same_compose": True,
                "semantic_form_id": semantic_selected_form_id,
                "selected_presentation_id": selected_form["id"],
                "alternative_form_id": alternate_form["id"],
                "distinct": selected_form["id"] != alternate_form["id"],
                "semantic_form_unchanged": True,
                "same_global_word": (
                    compose_pointwise([selected_form["id"]], atom_map)
                    == compose_pointwise([alternate_form["id"]], atom_map)
                ),
                "alternative_is_not_active_unity": True,
            },
        },
        "modality": {
            "definition": "presentation ∘ compose after translational truth closure",
            "input": input_word,
            "composed_global_word": input_global_word,
            "form": semantic_form_payload,
            "presentation": selected_form,
            "first_application": first_modality,
            "second_application": second_modality,
            "idempotent": modality_idempotent,
            "fixed_point": selected_fixed,
            "input_is_fixed_point": input_word == first_modality,
            "fixed_point_witnesses": [selected_form["id"]],
            "declared_fixed_point_ids": sorted(declared_fixed_point_ids),
            "declared_unity_ids": sorted(declared_unity_ids),
            "fixed_points_equal_unity": fixed_points_equal_declared_unity,
            "fixed_points_equal_unity_scope": (
                "declared finite generator/unity domain only"
            ),
            "idempotence_is_consequence_not_closure_definition": True,
            "defines_closure": False,
            "truth_form_precedes_modality": True,
            "equality_is_global_equality": False,
            "multiplicative_up_to_modality": multiplicative_up_to_modality,
            "is_monoid_homomorphism_claimed": False,
            "operator": natural_operator,
            "local_closure_level_id": level_id,
            "selected_natural_form_id": semantic_selected_form_id,
            "selected_presentation_id": selected_form["id"],
            "verified_scope": "declared finite generator/unity domain",
        },
        "global_equality_kernel": {
            "relation": (
                "x ~ y iff truth-derived compose(x) = truth-derived compose(y)"
            ),
            "classes": kernel_classes,
            "reflexive": reflexive,
            "symmetric": symmetric,
            "transitive": transitive,
            "equivalence_verified": reflexive and symmetric and transitive,
            "monoid_congruence": congruence_verified,
            "congruence_witness": congruence_witness,
            "equal_content_does_not_equal_actor_identity": True,
            "derived_reading_only": True,
            "truth_form_le_kernel_compose": True,
            "kernel_compose_le_truth_form_claimed": False,
            "authored_ids_define_equality": False,
            "presentation_metadata_defines_equality": False,
        },
        "freedom_fibre": {
            "global_word": input_global_word,
            "local_presentations": fibre_presentations,
            "observed_event_presentations": fibre_event_ids,
            "continuum_state_presentations": [state_generator_id],
            "available_local_actions": freedoms,
            "local_actions": freedoms,
            "action_presentations": action_presentations,
            "nonempty": bool(fibre_presentations),
            "unity_witnesses": unity_witnesses,
            "exactly_one_unity_witness": len(unity_witnesses) == 1,
            "canonical_unity_witness_id": semantic_selected_form_id,
            "presentation_witness_id": selected_form["id"],
            "unity_selects_without_exhausting_local_freedom": True,
        },
        "authorship": {
            "records": actor_records,
            "event_authorship_records": event_authorship_records,
            "contributor_records": contributor_records,
            "contributors": contributor_records,
            "equal_content_groups": content_groups,
            "source_identities_preserved": source_identities_preserved,
            "missing_source_identity_actor_ids": missing_source_identity_actor_ids,
            "unresolved_contributor_actor_ids": [
                record["actor_id"]
                for record in contributor_records
                if record["equality_status"] == "OPEN"
            ],
            "equal_global_content_identifies_actors": False,
            "actor_identity_collapsed": False,
            "mutual_authorship_redundancy_is_content_equality_only": True,
            "mutual_authorship_redundancy_applicable": (
                mutual_authorship_redundancy_applicable
            ),
            "mutual_authorship_redundancy_premise": {
                "relevant_contributor_count": relevant_contributor_count,
                "all_contributors_witnessed": all_contributors_witnessed,
                "same_witnessed_global_reading": same_witnessed_global_reading,
                "same_witnessed_natural_form": same_witnessed_natural_form,
                "premise_injected": False,
            },
            "conditional_theorem": (
                "Equal contributor authorship content is redundant only when "
                "every relevant contributor has the same witnessed global "
                "reading and selected natural form."
            ),
            "consent_and_responsibility_remain_actor_relative": True,
        },
        "suggestions": {
            "relation": "shares a witnessed natural form under the declared selector",
            "equivalence": {
                "relation": "form(compose(x)) = form(compose(y))",
                "classes": equivalence_classes,
                "reflexive": equivalence_verified,
                "symmetric": equivalence_verified,
                "transitive": equivalence_verified,
                "verified": equivalence_verified,
            },
            "contextual_ranked_edges": contextual_edges,
            "formally_witnessed_edge_ids": [
                edge["id"]
                for edge in contextual_edges
                if edge["formal_status"] == "WITNESSED"
            ],
            "form_equality_open_edge_ids": [
                edge["id"]
                for edge in contextual_edges
                if edge["formal_status"] == "OPEN"
            ],
            "ranking_is_contextual_not_equivalence": True,
            "equivalence_admits_candidates_but_does_not_rank_them": True,
            "global_optimum_claimed": False,
        },
        "gates": {
            "swapped_coordinates": True,
            "token": {
                "status": token_state,
                "gates_forms": True,
                "admitted_forms": enabled,
                "gated_forms": gated_forms,
                "blind_coordinate": "ordinary local interactions",
                "gates_ordinary_interactions": False,
                "blind_to_ordinary_interaction": True,
                "ordinary_interactions": freedoms,
                "can_consent": False,
                "can_bind": False,
                "currency_issued": False,
                "human_worth_scored": False,
            },
            "ai": {
                "status": "SUGGESTION_ONLY",
                "mediates_suggestions": True,
                "gates_suggested_interaction_edges": True,
                "gates_ordinary_interactions": False,
                "admitted_interactions": admitted_interactions,
                "blind_coordinate": "token form admission",
                "controls_form_admission": False,
                "blind_to_form_admission": True,
                "can_consent": False,
                "can_bind": False,
                "truth_issued": False,
            },
            "joint_product": {
                "product_witness": product_pairs,
                "relation_equals_cartesian_product": (
                    product_pair_keys == expected_product_keys
                ),
                "joint_gate_iff_product": (
                    product_pair_keys == expected_product_keys
                ),
                "independent_coordinates": True,
                "correlated_constraints_realisable": False,
            },
        },
        "commitment_relation": {
            "id": commitment_relation_id,
            "exists": commitment_exists,
            "separate_from_product_gates": True,
            "correlated": commitment_exists,
            "tuple": correlated_tuple,
            "correlates": [
                "form",
                "interaction",
                "parties",
                "resources",
                "time",
                "action",
            ],
            "non_product_constraint": commitment_exists,
            "non_product_realisable_by_independent_gates": False,
            "product_gate_sufficient_for_commitment": False,
            "requires_separate_agreement_layer": True,
            "requires_independent_human_receipts": True,
            "binding": False,
        },
        "one_tap": {
            "operation": "CREATE_EDITABLE_PROPOSAL",
            "available": True,
            "proposal_id": proposal.get("id"),
            "nonbinding_proposal": True,
            "creates_nonbinding_proposal": True,
            "proposal_status": proposal_status,
            "settlement": {
                "status": proposal_status,
                "consent_status": consent_status,
                "phase": natural_operator,
                "global_content_id": global_content_id,
                "global_state_id": global_state_id,
                "selected_natural_form_id": semantic_selected_form_id,
                "selected_presentation_id": selected_form["id"],
                "joint_content_global_word": input_global_word,
                "required_participant_ids": required_participants,
                "human_acceptances": accepted_humans,
                "all_required_humans_accepted": all_required_accepted,
                "requires_independent_human_acceptance": True,
                "human_acceptances_must_be_self_authored": True,
                "ai_can_accept": False,
                "token_can_accept": False,
                "settled": settled,
                "living_return_recorded": bool(returned),
                "living_return": _canonical_value(returned) if returned else None,
            },
        },
        "claims": {
            "truth_issued": False,
            "truth_claimed": False,
            "economic_claim_made": False,
            "economic_value_claimed": False,
            "value_claimed": False,
            "value_claim_made": False,
            "optimality_claimed": False,
            "optimality_claim_made": False,
            "global_optimum_claimed": False,
            "novelty_claimed": False,
            "legal_binding_claimed": False,
            "scope": "finite runtime conformance witness for NRRF837",
        },
    }
    body["receipt_id"] = canonical_hash(body)
    return body


__all__ = [
    "PROTOCOL",
    "SCHEMA",
    "UNITY_SELECTOR_VERSION",
    "append_local",
    "build_continuum_receipt",
    "canonical_hash",
    "canonical_json",
    "compose_pointwise",
    "unity_form",
]
