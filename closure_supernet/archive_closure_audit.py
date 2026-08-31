from __future__ import annotations

"""Deterministic archive-to-runtime closure audit for Supernet.

The audit never infers equality from semantic similarity. Historical natural
forms are REGISTERED, current runtime invariants are EXECUTABLE, cross-form
relations are WITNESSED only through source-preserving returned atlas paths,
explicit/unreturned relations remain OPEN, and unmatched Supernet conditions
are MISSING.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

from .closure_continuity import WITNESSED_STATUS
from .natural_form_atlas import historical_charts, validate_versioned_natural_form_atlas

PROTOCOL = "closure.supernet/archive-closure-audit-v1"
SCHEMA = "closure.supernet/archive-condition-classification-v1"
EXECUTABLE, WITNESSED, REGISTERED, OPEN, MISSING = (
    "EXECUTABLE", "WITNESSED", "REGISTERED", "OPEN", "MISSING"
)
STATUSES = (EXECUTABLE, WITNESSED, REGISTERED, OPEN, MISSING)


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode()).hexdigest()[:24]}"


def _normalize(value: str) -> str:
    text = value.casefold()
    for source, target in {
        "∞": " infinity ", "↔": " to ", "→": " to ", "⇄": " to ",
        "–": "-", "—": "-", "π": " pi ", "ρ": " rho ", "κ": " kappa ",
    }.items():
        text = text.replace(source, target)
    return " ".join(re.sub(r"[^a-z0-9+./=-]+", " ", text).split())


def _unique(values: Iterable[Any]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if value is not None and str(value)))


# id -> (aliases, runtime source symbols). Plain "natural form" is intentionally
# absent: mentioning a historical natural form does not make it executable.
CAPABILITIES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "observer-observed-translation": (
        ("observer observed interactive translation", "observer-observed interactive translation", "observer observed relation"),
        ("interactive_translation_relation.derive_feedback_translation",),
    ),
    "source-preserving-return": (
        ("source preserving return", "source-preserving return", "returned interaction", "return witness"),
        ("interactive_derivation_calculus.translation_certificate",),
    ),
    "open-preservation": (
        ("open relation", "open seam", "open aperture", "remain open", "remains open", "continuation status open"),
        ("closure_continuity.OPEN_STATUS",),
    ),
    "translational-truth": (
        ("translational truth", "translation equivalence", "same translational truth"),
        ("interaction_closure.translational_truth_id",),
    ),
    "natural-form-partition": (
        ("natural form partition", "natural-form partition", "natural forms partition"),
        ("natural_form_atlas.derive_versioned_natural_form_atlas",),
    ),
    "versioned-atlas": (
        ("versioned natural form atlas", "versioned natural-form atlas", "closeatlas", "compatible subatlas", "compatible sub-atlas", "glued atlas"),
        ("natural_form_atlas.derive_versioned_natural_form_atlas",),
    ),
    "ui-glue": (
        ("ui is the glued", "ui is locally glued", "glue compatible", "glued presentation"),
        ("natural_form_atlas.derive_glued_ui_subatlas",),
    ),
    "edge-view-transport": (
        ("edge is ongoing view transport", "ongoing view transport", "edge view transport", "edge-view identity"),
        ("closure_only_interface.render",),
    ),
    "perspective-reading": (
        ("perspective reading", "perspectival translation", "active perspective", "perspective flow"),
        ("closure_continuity.derive_perspective_reading",),
    ),
    "closure-naturality": (
        ("closure naturality", "naturality square", "pull square", "arena growth"),
        ("closure_naturality_equations.derive_closure_naturality_equations",),
    ),
    "hair-self-location": (
        ("hair as inversion of self location", "hair as inversion of self-location", "inversion of self location", "inversion of self-location", "perspective hair"),
        ("minimal_projection_runtime.local_perspective_hair_millidegrees",),
    ),
    "maze-partition": (
        ("maze partition", "partition maze", "trading maze"),
        ("trading_natural_form_closure", "natural_form_atlas"),
    ),
    "unitary-curvature": (
        ("unitary curvature", "profit curvature", "returned curvature"),
        ("trading_natural_form_closure.resolve_open_sensor_trading_closure",),
    ),
    "closed-itinerary-profit": (
        ("closed itinerary", "completed round trip profit", "completed round-trip profit", "round trip profit", "round-trip profit"),
        ("trading_natural_form_closure",),
    ),
    "authenticated-execution-return": (
        ("authenticated leg", "authenticated fill", "execution return", "cost complete", "cost-complete"),
        ("trading_natural_form_closure",),
    ),
    "configuration-nonauthority": (
        ("configuration authors truth", "configuration cannot author truth", "configuration does not author truth"),
        ("closure_continuity.audit_translational_continuity",),
    ),
    "computation-boundary-open": (
        ("computation bounds author truth", "computation boundary open", "finite computation boundary"),
        ("closure_continuity.computation_boundary_open",),
    ),
    "no-absolute-truth": (
        ("absolute truth issued", "no absolute truth", "does not issue absolute truth"),
        ("closure_continuity.combine_witnesses",),
    ),
    "open-existence": (
        ("existence closed", "existence remains open", "argument never closes existence", "no closed existence"),
        ("interaction_closure", "closure_ui_contract"),
    ),
    "noncollapse-cross-form-equality": (
        ("cross form equality requires returned translation", "cross-form equality requires returned translation", "visual resemblance cannot witness equality", "shared name cannot witness equality"),
        ("natural_form_atlas.validate_versioned_natural_form_atlas",),
    ),
}

THEORY_CONTEXT = tuple(_normalize(x) for x in (
    "Supernet", "IVI", "NRR", "closure", "translational truth", "natural form",
    "predual", "0↔∞", "hair", "unitary curvature", "Black Mirror", "Slearn",
    "triangle time", "Kakeya", "Lambert", "fractal hypotenuse", "ball-time", "loop sensor",
))
RELATION_MARKERS = tuple(_normalize(x) for x in (
    "equal", "equality", "equivalent", "same as", "is the", "translation", "translate",
    "returns", "return", "close", "closure", "iff", "if and only if", "maps to",
    "projection", "inversion", "dual", "predual", "preserve", "commute", "open", "witness",
))
EXPLICIT_OPEN = tuple(_normalize(x) for x in (
    "remains open", "remain open", "is open", "still open", "empirical boundary",
    "not empirically", "speculative", "hypothesis",
))
GENERIC_CHART_ALIASES = {_normalize(x) for x in (
    "0", "infinity", "point", "line", "path", "edge", "loop", "matrix", "rotation",
    "extension", "local", "global", "mirror", "inversion", "hair", "fold", "seam", "sphere",
)}


def _contains(text: str, term: str) -> bool:
    return bool(term) and f" {term} " in f" {text} "


def _chart_aliases(chart: Mapping[str, Any]) -> set[str]:
    name = str(chart.get("name") or "")
    variants = {
        name, name.replace("Mobius", "Möbius"), name.replace("infinity", "∞"),
        name.replace("0-infinity", "0↔∞"), name.replace("ball-hair", "ball hair"),
        name.replace("point-ball", "point ball"), name.replace("point-sphere", "point sphere"),
        name.replace("light-cone", "light cone"), name.replace("round-trip", "round trip"),
    }
    return {_normalize(v) for v in variants if v}


CHARTS = {str(chart["id"]): chart for chart in historical_charts()}
CHART_ALIASES = sorted(
    ((alias, chart_id) for chart_id, chart in CHARTS.items() for alias in _chart_aliases(chart)),
    key=lambda item: (-len(item[0]), item[0], item[1]),
)
CAPABILITY_ALIASES = sorted(
    ((_normalize(alias), cid) for cid, (aliases, _) in CAPABILITIES.items() for alias in aliases),
    key=lambda item: (-len(item[0]), item[0]),
)


def _theory_context(text: str) -> bool:
    return any(_contains(text, term) for term in THEORY_CONTEXT)


def _match_charts(raw: str) -> list[str]:
    text = _normalize(raw)
    theory = _theory_context(text)
    result: list[str] = []
    for alias, chart_id in CHART_ALIASES:
        if alias in GENERIC_CHART_ALIASES and not theory:
            continue
        if _contains(text, alias):
            result.append(chart_id)
    return _unique(result)


def _match_capabilities(raw: str) -> list[str]:
    text = _normalize(raw)
    result: list[str] = []
    for alias, cid in CAPABILITY_ALIASES:
        if _contains(text, alias):
            result.append(cid)
    return _unique(result)


def _relation_statement(raw: str, charts: Sequence[str]) -> bool:
    text = _normalize(raw)
    return len(set(charts)) >= 2 and any(_contains(text, marker) for marker in RELATION_MARKERS)


def _explicit_open(raw: str, charts: Sequence[str]) -> bool:
    text = _normalize(raw)
    if any(_contains(text, marker) for marker in EXPLICIT_OPEN):
        return True
    empirical = any(CHARTS.get(cid, {}).get("empirical_return_required") is True for cid in charts)
    return empirical and any(_contains(text, _normalize(x)) for x in ("physical", "empirical", "cosmological"))


def _witness_graph(atlas: Mapping[str, Any] | None) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {}
    if not atlas:
        return graph
    for raw in atlas.get("translations", []):
        if not isinstance(raw, Mapping) or raw.get("status") != WITNESSED_STATUS or raw.get("kind") == "IDENTITY":
            continue
        source, target = str(raw.get("source_chart_id") or ""), str(raw.get("target_chart_id") or "")
        if not source or not target:
            continue
        if not _unique(raw.get("source_return_ids", [])):
            continue
        if raw.get("source_preserved") is not True or raw.get("closure_commutes") is not True or raw.get("return_preserved") is not True:
            continue
        graph.setdefault(source, set()).add(target)
        graph.setdefault(target, set()).add(source)
    return graph


def _all_connected(chart_ids: Sequence[str], graph: Mapping[str, set[str]]) -> bool:
    nodes = set(chart_ids)
    if len(nodes) <= 1:
        return True
    reached = {next(iter(nodes))}
    frontier = list(reached)
    while frontier:
        current = frontier.pop()
        for neighbour in graph.get(current, set()):
            if neighbour not in reached:
                reached.add(neighbour)
                frontier.append(neighbour)
    return nodes.issubset(reached)


def classify_condition(*, text: str, atlas: Mapping[str, Any] | None = None) -> dict[str, Any]:
    charts = _match_charts(text)
    capabilities = _match_capabilities(text)
    relation = _relation_statement(text, charts)
    graph = _witness_graph(atlas)
    if _explicit_open(text, charts):
        status, basis = OPEN, "EXPLICIT_OR_EMPIRICAL_OPEN_BOUNDARY"
    elif relation and not _all_connected(charts, graph):
        status, basis = OPEN, "CROSS_FORM_RELATION_AWAITS_RETURNED_TRANSLATION"
    elif relation and graph and _all_connected(charts, graph):
        status, basis = WITNESSED, "SOURCE_PRESERVING_RETURNED_ATLAS_TRANSLATION"
    elif capabilities:
        status, basis = EXECUTABLE, "CURRENT_RUNTIME_CAPABILITY"
    elif charts:
        status, basis = REGISTERED, "VERSIONED_ATLAS_CHART_REGISTERED"
    else:
        status, basis = MISSING, "THEORY_CONDITION_NOT_MAPPED_TO_ATLAS_OR_RUNTIME_CAPABILITY"
    return {
        "status": status,
        "basis": basis,
        "chart_ids": charts,
        "capability_ids": capabilities,
        "runtime_source_symbols": _unique(
            symbol for cid in capabilities for symbol in CAPABILITIES[cid][1]
        ),
        "cross_form_relation": relation,
        "truth_issued": False,
    }


MESSAGE_RE = re.compile(r"^### Message\s+(?P<number>\d+)\s+—\s+(?P<timestamp>.+?)\s*$", re.MULTILINE)
CONVERSATION_RE = re.compile(
    r"^##\s+(?P<title>.+?)\s*\n\s*\n_Conversation ID:\s*`(?P<id>[^`]+)`_",
    re.MULTILINE,
)
HEADER_MESSAGES_RE = re.compile(r"^- User messages:\s*(?P<count>\d+)\s*$", re.MULTILINE)
HEADER_CONVERSATIONS_RE = re.compile(r"^- Conversations with user messages:\s*(?P<count>\d+)\s*$", re.MULTILINE)


def parse_archive(markdown: str) -> dict[str, Any]:
    conversations = list(CONVERSATION_RE.finditer(markdown))
    messages: list[dict[str, Any]] = []
    ids: set[str] = set()
    for i, conversation in enumerate(conversations):
        block = markdown[conversation.end():(conversations[i + 1].start() if i + 1 < len(conversations) else len(markdown))]
        cid = conversation.group("id").strip()
        ids.add(cid)
        message_matches = list(MESSAGE_RE.finditer(block))
        for j, match in enumerate(message_matches):
            end = message_matches[j + 1].start() if j + 1 < len(message_matches) else len(block)
            messages.append({
                "conversation_title": conversation.group("title").strip(),
                "conversation_id": cid,
                "message_number": int(match.group("number")),
                "timestamp": match.group("timestamp").strip(),
                "text": block[match.end():end].strip(),
            })
    dm, dc = HEADER_MESSAGES_RE.search(markdown), HEADER_CONVERSATIONS_RE.search(markdown)
    return {
        "messages": messages,
        "declared_user_message_count": int(dm.group("count")) if dm else None,
        "declared_conversation_count": int(dc.group("count")) if dc else None,
        "parsed_conversation_count": len(ids),
    }


def _split_units(message: str) -> list[str]:
    result: list[str] = []
    for line in (line.strip() for line in message.splitlines() if line.strip()):
        if line.startswith(("-", "*", ">", "\\", "$", "[", "{")) or any(x in line for x in ("=", "→", "↔")) or "iff" in line.casefold() or len(line) <= 220:
            candidates = [line]
        else:
            candidates = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\\])", line)
        result.extend(candidate.strip() for candidate in candidates if 3 <= len(candidate.strip()) <= 4000)
    return result


def _candidate(unit: str) -> bool:
    if _match_charts(unit) or _match_capabilities(unit):
        return True
    text = _normalize(unit)
    return _theory_context(text) and any(_contains(text, marker) for marker in RELATION_MARKERS)


def audit_archive(markdown: str, *, atlas: Mapping[str, Any] | None = None, archive_name: str | None = None) -> dict[str, Any]:
    parsed = parse_archive(markdown)
    atlas_validation = None
    if atlas is not None:
        atlas_validation = validate_versioned_natural_form_atlas(atlas)
        if not atlas_validation.get("valid"):
            raise ValueError("atlas must validate before archive audit")
    conditions: list[dict[str, Any]] = []
    candidate_messages: set[tuple[str, int]] = set()
    for message in parsed["messages"]:
        for unit_index, unit in enumerate(_split_units(message["text"])):
            if not _candidate(unit):
                continue
            provenance = {
                "conversation_id": message["conversation_id"],
                "conversation_title": message["conversation_title"],
                "message_number": message["message_number"],
                "timestamp": message["timestamp"],
                "unit_index": unit_index,
            }
            conditions.append({
                "id": _digest("archive-condition", {"source": provenance, "text": unit}),
                "source": provenance,
                "text": unit,
                **classify_condition(text=unit, atlas=atlas),
            })
            candidate_messages.add((message["conversation_id"], message["message_number"]))
    counts = {status: 0 for status in STATUSES}
    for condition in conditions:
        counts[condition["status"]] += 1
    parsed_messages = len(parsed["messages"])
    parsed_conversations = int(parsed["parsed_conversation_count"])
    declared_messages = parsed["declared_user_message_count"]
    declared_conversations = parsed["declared_conversation_count"]
    source_counts_match = bool(
        (declared_messages is None or declared_messages == parsed_messages)
        and (declared_conversations is None or declared_conversations == parsed_conversations)
    )
    missing_ids = [c["id"] for c in conditions if c["status"] == MISSING]
    open_ids = [c["id"] for c in conditions if c["status"] == OPEN]
    registered_ids = [c["id"] for c in conditions if c["status"] == REGISTERED]
    inventory_closed = bool(source_counts_match and not missing_ids)
    execution_closed = bool(inventory_closed and not open_ids and not registered_ids)
    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "archive_name": archive_name,
        "archive_sha256": hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
        "declared_user_message_count": declared_messages,
        "parsed_user_message_count": parsed_messages,
        "declared_conversation_count": declared_conversations,
        "parsed_conversation_count": parsed_conversations,
        "source_count_matches_declared_archive": source_counts_match,
        "theory_candidate_message_count": len(candidate_messages),
        "semantic_condition_count": len(conditions),
        "classification_counts": counts,
        "conditions": conditions,
        "missing_condition_ids": missing_ids,
        "open_condition_ids": open_ids,
        "registered_only_condition_ids": registered_ids,
        "historical_inventory_closed": inventory_closed,
        "runtime_execution_closed": execution_closed,
        "open_is_valid_historical_classification": True,
        "missing_is_not_silently_open": True,
        "registered_is_not_silently_executable": True,
        "witnessed_requires_returned_atlas_translation": True,
        "classification_is_deterministic_text_and_registry_match": True,
        "semantic_similarity_model_used": False,
        "atlas_id": atlas.get("id") if atlas else None,
        "atlas_validation": atlas_validation,
        "truth_issued": False,
    }
    body["id"] = _digest("archive-closure-audit", body)
    return body


def audit_summary(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "audit_id": receipt.get("id"),
        "archive_sha256": receipt.get("archive_sha256"),
        "declared_user_message_count": receipt.get("declared_user_message_count"),
        "parsed_user_message_count": receipt.get("parsed_user_message_count"),
        "declared_conversation_count": receipt.get("declared_conversation_count"),
        "parsed_conversation_count": receipt.get("parsed_conversation_count"),
        "semantic_condition_count": receipt.get("semantic_condition_count"),
        "classification_counts": dict(receipt.get("classification_counts") or {}),
        "historical_inventory_closed": receipt.get("historical_inventory_closed") is True,
        "runtime_execution_closed": receipt.get("runtime_execution_closed") is True,
        "missing_condition_count": len(receipt.get("missing_condition_ids") or []),
        "open_condition_count": len(receipt.get("open_condition_ids") or []),
        "registered_only_condition_count": len(receipt.get("registered_only_condition_ids") or []),
        "truth_issued": False,
    }


def validate_archive_audit(receipt: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if receipt.get("protocol") != PROTOCOL: errors.append("audit:protocol")
    if receipt.get("schema") != SCHEMA: errors.append("audit:schema")
    conditions = receipt.get("conditions")
    if not isinstance(conditions, list):
        errors.append("audit:conditions")
        conditions = []
    counts = {status: 0 for status in STATUSES}
    ids: list[str] = []
    for condition in conditions:
        if not isinstance(condition, Mapping):
            errors.append("audit:condition-shape")
            continue
        cid = str(condition.get("id") or "")
        ids.append(cid)
        status = condition.get("status")
        if status not in STATUSES:
            errors.append(f"audit:{cid}:status")
        else:
            counts[str(status)] += 1
        if condition.get("truth_issued") is not False:
            errors.append(f"audit:{cid}:truth-issued")
    if len(ids) != len(set(ids)): errors.append("audit:duplicate-condition-id")
    if receipt.get("classification_counts") != counts: errors.append("audit:classification-counts")
    if receipt.get("semantic_condition_count") != len(conditions): errors.append("audit:semantic-condition-count")
    expected_inventory = bool(receipt.get("source_count_matches_declared_archive") is True and counts[MISSING] == 0)
    expected_execution = bool(expected_inventory and counts[OPEN] == 0 and counts[REGISTERED] == 0)
    if receipt.get("historical_inventory_closed") is not expected_inventory: errors.append("audit:historical-inventory-closure")
    if receipt.get("runtime_execution_closed") is not expected_execution: errors.append("audit:runtime-execution-closure")
    if receipt.get("truth_issued") is not False: errors.append("audit:truth-issued")
    body = {key: value for key, value in receipt.items() if key != "id"}
    if receipt.get("id") != _digest("archive-closure-audit", body): errors.append("audit:id")
    return {
        "valid": not errors,
        "errors": errors,
        "historical_inventory_closed": expected_inventory,
        "runtime_execution_closed": expected_execution,
        "classification_counts": counts,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit a Supernet user-input archive")
    parser.add_argument("archive", type=Path)
    parser.add_argument("--atlas-json", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    markdown = args.archive.read_text(encoding="utf-8")
    atlas = json.loads(args.atlas_json.read_text(encoding="utf-8")) if args.atlas_json else None
    receipt = audit_archive(markdown, atlas=atlas, archive_name=args.archive.name)
    validation = validate_archive_audit(receipt)
    if not validation["valid"]:
        raise SystemExit("audit receipt failed self-validation: " + ", ".join(validation["errors"]))
    output = audit_summary(receipt) if args.summary else receipt
    rendered = json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROTOCOL", "SCHEMA", "EXECUTABLE", "WITNESSED", "REGISTERED", "OPEN", "MISSING",
    "STATUSES", "RUNTIME_CAPABILITIES", "CAPABILITIES", "audit_archive", "audit_summary",
    "classify_condition", "parse_archive", "validate_archive_audit",
]

# Backward-compatible public name used by audit/introspection callers.
RUNTIME_CAPABILITIES = CAPABILITIES
