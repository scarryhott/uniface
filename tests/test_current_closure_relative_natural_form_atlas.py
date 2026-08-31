from __future__ import annotations

from closure_supernet.current_closure_relative_natural_form_atlas import FAMILY_ANCHOR_NAMES
from closure_supernet.interactive_translation_equations_current import resolve_trading_equation
from closure_supernet.natural_form_atlas import STATIC_FAMILIES, historical_charts


def returned(rid: str, source: str, target: str, value: str, *, hair_delta: str = "0") -> dict[str, object]:
    return {
        "id": rid, "source": source, "target": target, "value": value,
        "hair_delta": hair_delta, "source_ids": [f"source:{rid}"], "returned": True,
        "authenticated": True, "cost_complete": True,
        "relative_size": "3", "relative_size_unit": "risk-unit",
    }


def frame() -> list[dict[str, object]]:
    return [returned("ab", "A", "B", "-3"), returned("ba", "B", "A", "2")]


def formal_resolve(**kwargs: object) -> dict[str, object]:
    return resolve_trading_equation(source_truth_mode="FORMAL_FIXTURE", **kwargs)


def anchor_id(family: str) -> str:
    name = FAMILY_ANCHOR_NAMES[family]
    return next(str(c["id"]) for c in historical_charts() if c["family"] == family and c["name"] == name)


def test_full_historical_family_atlas_is_carrier_not_trading() -> None:
    receipt = formal_resolve(observer_id="o", sensor_feedback=frame())
    atlas = receipt["current_closure_relative_atlas"]
    assert receipt["natural_form_field"] == atlas
    assert atlas["carrier_is_full_versioned_natural_form_atlas"] is True
    assert atlas["trading_specific_carrier"] is False
    assert atlas["historical_family_count"] == len(STATIC_FAMILIES)
    assert {r["family_id"] for r in atlas["historical_family_carrier"]} == set(STATIC_FAMILIES)


def test_returned_trading_closure_has_local_and_open_family_readings() -> None:
    receipt = formal_resolve(observer_id="o", sensor_feedback=frame())
    truth = receipt["current_closure_relative_atlas"]["truth_classes"][0]
    expected_local = {
        "REFINEMENT_PATH_HIDDEN_TRAJECTORY", "BALL_HAIR",
        "MIRROR_OBSERVER_CONSCIOUS_INTERFACE", "CURVATURE_MAZE_LIGHTCONE_SUPERNET",
        "AI_TOKEN_MARKET_TRADING",
    }
    assert set(truth["local_family_ids"]) == expected_local
    assert not truth["global_family_ids"]
    assert set(truth["open_family_ids"]) == set(STATIC_FAMILIES) - expected_local


def test_returned_cross_family_translation_makes_family_global() -> None:
    source = anchor_id("CURVATURE_MAZE_LIGHTCONE_SUPERNET")
    target = anchor_id("DIMENSIONAL_POINT_LINE_TRIANGLE")
    extra = {"atlas_translations": [{
        "source_chart_id": source, "target_chart_id": target,
        "returned": True, "source_preserved": True, "closure_commutes": True,
        "return_preserved": True, "source_return_ids": ["return:curvature-dimensional"],
    }]}
    receipt = formal_resolve(observer_id="o", sensor_feedback=frame(), atlas_translation_sources=[extra])
    truth = receipt["current_closure_relative_atlas"]["truth_classes"][0]
    row = next(r for r in truth["family_field"] if r["family_id"] == "DIMENSIONAL_POINT_LINE_TRIANGLE")
    assert row["relative_role"] == "GLOBAL"
    assert row["distance_from_current_tt"] == 2
    assert len(row["translation_path_ids"]) == 2


def test_direct_returned_family_translation_is_local() -> None:
    base = formal_resolve(observer_id="o", sensor_feedback=frame())
    tt = base["current_closure_relative_atlas"]["truth_classes"][0]["current_tt_id"]
    target = anchor_id("DIMENSIONAL_POINT_LINE_TRIANGLE")
    extra = {"atlas_translations": [{
        "source_chart_id": f"runtime-nf:{tt}", "target_chart_id": target,
        "returned": True, "source_preserved": True, "closure_commutes": True,
        "return_preserved": True, "source_return_ids": ["return:direct-dimensional"],
    }]}
    receipt = formal_resolve(observer_id="o", sensor_feedback=frame(), atlas_translation_sources=[extra])
    truth = receipt["current_closure_relative_atlas"]["truth_classes"][0]
    row = next(r for r in truth["family_field"] if r["family_id"] == "DIMENSIONAL_POINT_LINE_TRIANGLE")
    assert row["relative_role"] == "LOCAL"
    assert row["distance_from_current_tt"] == 1


def test_open_family_remains_in_carrier_and_enters_nrrf874_boundary() -> None:
    receipt = formal_resolve(observer_id="o", sensor_feedback=frame())
    truth = receipt["current_closure_relative_atlas"]["truth_classes"][0]
    physical = next(r for r in truth["family_field"] if r["family_id"] == "PHYSICAL_COSMOLOGICAL_COLOR")
    assert physical["status"] == "OPEN"
    atlas_requests = [r for r in receipt["selected_interactions"] if r.get("kind") == "RETURN_SOURCE_PRESERVING_ATLAS_TRANSLATION" and r.get("family_id") == "PHYSICAL_COSMOLOGICAL_COLOR"]
    assert atlas_requests and all(r["predicted_profit"] is None for r in atlas_requests)
    learning = receipt["open_boundary_natural_selection"]
    assert learning["open_boundary_drives_learning_selection"] if "open_boundary_drives_learning_selection" in learning else learning["boundary_driven"]
    assert any(r.get("interaction", {}).get("family_id") == "PHYSICAL_COSMOLOGICAL_COLOR" for r in learning["open_boundary"])


def test_hair_equivalent_presentations_preserve_relative_roles() -> None:
    left = [returned("ab0", "A", "B", "-3"), returned("ba0", "B", "A", "2")]
    right = [returned("ab1", "A", "B", "2", hair_delta="5"), returned("ba1", "B", "A", "-3", hair_delta="-5")]
    a = formal_resolve(observer_id="o", sensor_feedback=left)["current_closure_relative_atlas"]["truth_classes"][0]
    b = formal_resolve(observer_id="o", sensor_feedback=right)["current_closure_relative_atlas"]["truth_classes"][0]
    assert a["current_tt_id"] == b["current_tt_id"]
    assert a["local_family_ids"] == b["local_family_ids"]
    assert a["global_family_ids"] == b["global_family_ids"]
    assert a["open_family_ids"] == b["open_family_ids"]
