from __future__ import annotations

"""Current-closure-relative admissible natural-form atlas.

The existing versioned historical atlas is the carrier. Trading is one runtime
projection, never the ontology. For every current translational-truth class:

LOCAL  = one witnessed returned atlas translation from the current TT chart.
GLOBAL = transitively witnessed compatibility from the current TT chart.
OPEN   = no source-preserving returned compatibility yet.

Every historical family remains present even when OPEN. Local/global therefore
change relative to current translational truth; family names, resemblance,
strategy scores, and configured horizons do not author admissibility.
"""

from collections import deque
import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .natural_form_atlas import (
    FAMILY_SEMANTICS,
    STATIC_FAMILIES,
    derive_versioned_natural_form_atlas,
    historical_charts,
)

PROTOCOL = "closure.supernet/current-closure-relative-natural-form-atlas-v1"

FAMILY_ANCHOR_NAMES: dict[str, str] = {
    "INTERBOUND_PRE_DIRECTIONAL": "local-global",
    "DIMENSIONAL_POINT_LINE_TRIANGLE": "point-line duality",
    "SEAM_FOLD_BOUNDARY_INVERSION": "fold",
    "REFINEMENT_PATH_HIDDEN_TRAJECTORY": "closed itinerary",
    "BALL_HAIR": "closure ball",
    "MIRROR_OBSERVER_CONSCIOUS_INTERFACE": "observer mirror",
    "SHEAF_TOPOS_LATTICE_ALGEBRA": "local-global sheaf",
    "CURVATURE_MAZE_LIGHTCONE_SUPERNET": "unitary curvature",
    "AI_TOKEN_MARKET_TRADING": "profit curvature",
    "PHYSICAL_COSMOLOGICAL_COLOR": "QG loop",
}


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _unique(values: Sequence[Any]) -> list[str]:
    return list(dict.fromkeys(str(v) for v in values if v is not None and str(v)))


def _anchors() -> dict[str, dict[str, Any]]:
    charts = historical_charts()
    result: dict[str, dict[str, Any]] = {}
    for family, name in FAMILY_ANCHOR_NAMES.items():
        row = next((dict(c) for c in charts if c.get("family") == family and c.get("name") == name), None)
        if row is None:
            raise AssertionError(f"missing family anchor {family}/{name}")
        result[family] = row
    return result


def _automatic_evidence(
    *, observer_id: str | None, form: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    source_ids = _unique(form.get("source_ids", []))
    return_ids = _unique(form.get("return_ids", []))
    witness_ids = _unique([*source_ids, *return_ids])
    witnessed = form.get("status") == WITNESSED_STATUS and bool(witness_ids)
    path = [str(v) for v in form.get("token_path", [])]
    closed_path = len(path) >= 2 and path[0] == path[-1]
    evidence = {
        family: {"witnessed": False, "source_return_ids": witness_ids, "basis": "OPEN_NO_RETURNED_FAMILY_TRANSLATION"}
        for family in STATIC_FAMILIES
    }
    def mark(family: str, basis: str) -> None:
        evidence[family] = {"witnessed": True, "source_return_ids": witness_ids, "basis": basis}
    if witnessed and closed_path:
        mark("REFINEMENT_PATH_HIDDEN_TRAJECTORY", "RETURNED_CLOSED_ITINERARY")
    if witnessed and form.get("ball_id") and form.get("hair_closes_on_return") is True:
        mark("BALL_HAIR", "RETURNED_BALL_WITH_CLOSED_HAIR")
    if witnessed and observer_id and source_ids:
        mark("MIRROR_OBSERVER_CONSCIOUS_INTERFACE", "SOURCE_PRESERVING_OBSERVER_RETURN")
    if witnessed and form.get("unitary_curvature") is not None and isinstance(form.get("closure_ball_partition"), Mapping):
        mark("CURVATURE_MAZE_LIGHTCONE_SUPERNET", "RETURNED_UNITARY_CURVATURE_AND_MAZE_PARTITION")
    if witnessed and isinstance(form.get("trade_projection"), Mapping):
        mark("AI_TOKEN_MARKET_TRADING", "RETURNED_VALUE_FLOW_AND_TRADE_PROJECTION")
    return evidence


def _truth_derivation(
    *, observer_id: str | None, natural_closure: Mapping[str, Any]
) -> tuple[dict[str, Any], list[str], dict[str, dict[str, Any]]]:
    anchors = _anchors()
    natural_forms: list[dict[str, Any]] = []
    translations: list[dict[str, Any]] = []
    active: list[str] = []
    evidence_by_tt: dict[str, dict[str, Any]] = {}
    for raw in natural_closure.get("natural_forms", []):
        form = dict(raw)
        tt = str(form.get("closure_truth_id") or form.get("closure_id") or "")
        if not tt:
            continue
        active.append(tt)
        source_returns = _unique([*form.get("source_ids", []), *form.get("return_ids", [])])
        natural_forms.append({"id": tt, "name": f"current closure truth {tt}", "members": [tt], "source_return_ids": source_returns})
        evidence = _automatic_evidence(observer_id=observer_id, form=form)
        evidence_by_tt[tt] = evidence
        runtime_chart = f"runtime-nf:{tt}"
        for family in STATIC_FAMILIES:
            ev = evidence[family]
            returned = bool(ev["witnessed"] and ev["source_return_ids"])
            translations.append({
                "source_chart_id": runtime_chart,
                "target_chart_id": anchors[family]["id"],
                "returned": returned,
                "source_preserved": returned,
                "closure_commutes": returned,
                "return_preserved": returned,
                "source_return_ids": list(ev["source_return_ids"]),
                "return_witness_id": _digest("current-family-return", {"tt": tt, "family": family, "basis": ev["basis"]}) if returned else None,
            })
    return {"natural_forms": natural_forms, "atlas_translations": translations}, active, evidence_by_tt


def _graph(atlas: Mapping[str, Any]) -> tuple[dict[str, set[str]], dict[tuple[str, str], list[str]]]:
    graph: dict[str, set[str]] = {}
    ids: dict[tuple[str, str], list[str]] = {}
    for raw in atlas.get("translations", []):
        r = dict(raw)
        if r.get("status") != WITNESSED_STATUS:
            continue
        a, b = str(r.get("source_chart_id") or ""), str(r.get("target_chart_id") or "")
        if not a or not b:
            continue
        graph.setdefault(a, set()).add(b); graph.setdefault(b, set()).add(a)
        ids.setdefault((a,b), []).append(str(r.get("id"))); ids.setdefault((b,a), []).append(str(r.get("id")))
    return graph, ids


def _distances(start: str, graph: Mapping[str, set[str]]) -> tuple[dict[str,int], dict[str,str|None]]:
    dist = {start: 0}; parent: dict[str,str|None] = {start: None}; q: deque[str] = deque([start])
    while q:
        cur = q.popleft()
        for nxt in sorted(graph.get(cur, ())):
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1; parent[nxt] = cur; q.append(nxt)
    return dist, parent


def _path_ids(start: str, target: str, parent: Mapping[str,str|None], rel_ids: Mapping[tuple[str,str],list[str]]) -> list[str]:
    if target not in parent:
        return []
    nodes = [target]
    while nodes[-1] != start:
        p = parent.get(nodes[-1])
        if p is None: return []
        nodes.append(p)
    nodes.reverse(); result: list[str] = []
    for a,b in zip(nodes,nodes[1:]):
        choices = rel_ids.get((a,b), [])
        if choices: result.append(sorted(choices)[0])
    return result


def derive_current_closure_relative_atlas(
    *,
    observer_id: str | None,
    natural_closure: Mapping[str, Any],
    preaction_coordinates: Mapping[str, Mapping[str, Any]] | None = None,
    trading_projection_field: Mapping[str, Any] | None = None,
    additional_translation_sources: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Derive all natural-form families relative to each current TT class."""
    truth_derivation, active, evidence_by_tt = _truth_derivation(observer_id=observer_id, natural_closure=natural_closure)
    atlas = derive_versioned_natural_form_atlas(
        truth_derivation=truth_derivation,
        interactive_translation={},
        active_perspective_id=observer_id,
        active_reading={tt: tt for tt in active},
        additional_translation_sources=additional_translation_sources,
    )
    charts = [dict(c) for c in atlas.get("charts", [])]
    historical = {family: {str(c["id"]) for c in charts if c.get("family") == family and c.get("runtime_generated") is False} for family in STATIC_FAMILIES}
    anchors = _anchors(); graph, rel_ids = _graph(atlas)
    trade_by_tt = {str(r.get("closure_id")): dict(r) for r in (trading_projection_field or {}).get("returned_natural_forms", []) if r.get("closure_id")}
    truths: list[dict[str, Any]] = []; actions: list[dict[str, Any]] = []
    for tt in active:
        runtime = f"runtime-nf:{tt}"; dist, parent = _distances(runtime, graph); families: list[dict[str, Any]] = []
        for family in STATIC_FAMILIES:
            reachable = sorted((dist[c], c) for c in historical[family] if c in dist)
            if reachable:
                d, representative = reachable[0]; role = "LOCAL" if d == 1 else "GLOBAL"; status = WITNESSED_STATUS
                path = _path_ids(runtime, representative, parent, rel_ids)
            else:
                d, representative, role, status, path = None, str(anchors[family]["id"]), OPEN_STATUS, OPEN_STATUS, []
                actions.append({
                    "kind": "RETURN_SOURCE_PRESERVING_ATLAS_TRANSLATION", "status": OPEN_STATUS,
                    "current_tt_id": tt, "family_id": family, "source_chart_id": runtime, "target_chart_id": representative,
                    "requires_return": True, "requires_source_preserving_return": True,
                    "expected_value": None, "predicted_profit": None, "may_author_truth": False,
                    "semantic_authority": False, "automatic_order_submission": False,
                })
            families.append({
                "family_id": family, "status": status, "relative_role": role,
                "distance_from_current_tt": d, "current_tt_id": tt, "runtime_chart_id": runtime,
                "representative_chart_id": representative, "family_semantics": dict(FAMILY_SEMANTICS[family]),
                "translation_path_ids": path, "local_global_is_relative_to_current_tt": True,
                "family_name_does_not_author_role": True, "visual_resemblance_does_not_author_admissibility": True,
            })
        local = [r["family_id"] for r in families if r["relative_role"] == "LOCAL"]
        global_ = [r["family_id"] for r in families if r["relative_role"] == "GLOBAL"]
        open_ = [r["family_id"] for r in families if r["relative_role"] == OPEN_STATUS]
        projection = trade_by_tt.get(tt)
        truths.append({
            "current_tt_id": tt, "runtime_chart_id": runtime, "family_field": families,
            "local_family_ids": local, "global_family_ids": global_, "open_family_ids": open_,
            "admissible_family_ids": [*local,*global_], "all_historical_family_ids": list(STATIC_FAMILIES),
            "automatic_family_evidence": evidence_by_tt.get(tt, {}), "trading_projection": projection,
            "profit_projection": projection.get("natural_profit") if projection else None,
            "relative_hair_horizon": projection.get("relative_hair_horizon") if projection else None,
            "relative_ball_size": projection.get("relative_ball_size") if projection else None,
            "recognition_equals_selection": True, "local_global_relative_to_current_translational_truth": True,
            "trading_family_is_not_carrier": True,
        })
        if projection and projection.get("action_projection") is not None:
            action = dict(projection["action_projection"])
            action.update({"current_tt_id": tt, "derived_from_current_closure_relative_atlas": True, "admissible_family_ids": [*local,*global_], "trading_projection_is_one_family_reading": True})
            actions.append(action)
    for raw in (trading_projection_field or {}).get("action_projections", []):
        row = dict(raw)
        if row.get("closure_id"): continue
        row.update({"derived_from_current_closure_relative_atlas": True, "trading_projection_is_one_family_reading": True, "carrier_authority": False})
        actions.append(row)
    dedup = {_stable(a): a for a in actions}; actions = [dedup[k] for k in sorted(dedup)]
    body = {
        "protocol": PROTOCOL,
        "equation": "CurrentNaturalForm(Q,o)=Rel_(Q,o)(VersionedNaturalFormAtlas); LOCAL=one returned translation; GLOBAL=transitive returned compatibility; OPEN=no returned compatibility",
        "status": atlas.get("status", OPEN_STATUS), "observer_id": observer_id,
        "versioned_atlas_id": atlas.get("id"), "versioned_atlas": atlas,
        "historical_family_carrier": [{"family_id": f, "semantics": dict(FAMILY_SEMANTICS[f]), "chart_count": len(historical[f])} for f in STATIC_FAMILIES],
        "historical_family_count": len(STATIC_FAMILIES), "truth_classes": truths, "truth_class_count": len(truths),
        "action_projections": actions, "action_projection_count": len(actions),
        "carrier_is_full_versioned_natural_form_atlas": True, "trading_specific_carrier": False,
        "trading_is_projection_family": True, "all_families_preserved_when_open": True,
        "admissibility_requires_source_preserving_returned_translation": True,
        "local_global_relative_to_current_translational_truth": True, "local_global_are_not_fixed_ontological_levels": True,
        "recognition_equals_selection": True, "single_final_form_selected": False, "selection_is_not_filtering": True,
        "name_equality_authors_admissibility": False, "visual_resemblance_authors_admissibility": False,
        "forecast_model_present": False, "similarity_tolerance_present": False, "automatic_order_submission": False,
        "truth_issued": False,
    }
    body["id"] = _digest("current-closure-relative-atlas", body)
    return body


__all__ = ["FAMILY_ANCHOR_NAMES", "PROTOCOL", "derive_current_closure_relative_atlas"]
