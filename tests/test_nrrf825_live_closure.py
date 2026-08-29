from __future__ import annotations

import math
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_natural_interface import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.nrrf825 import closure_level_receipt


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "nrrf825-live.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def edge(left: str, right: str, verdict: str = "TRUE") -> dict[str, str]:
    return {
        "candidate_relation_id": f"{left}:{right}",
        "source_occurrence": left,
        "target_occurrence": right,
        "verdict": verdict,
    }


def test_projective_coordinate_is_derived_from_the_admitted_level() -> None:
    bottom = closure_level_receipt(
        source_occurrence_ids=["a", "b", "c"], relation_receipts=[]
    )
    assert bottom["endpoint"] == "⊥"
    assert bottom["class_count"] == 3
    assert bottom["projective_fold"]["collapse"] == 0
    assert bottom["projective_fold"]["tan_value"] == 0
    assert bottom["truth_closes_level_alone"]["identity_reading_closed"] is True

    relative = closure_level_receipt(
        source_occurrence_ids=["a", "b", "c"],
        relation_receipts=[edge("a", "b")],
    )
    assert relative["endpoint"] == "relative"
    assert relative["equality_classes"] == [["a", "b"], ["c"]]
    assert relative["projective_fold"]["collapse"] == 0.5
    assert math.isclose(relative["projective_fold"]["tan_value"], 1.0)
    assert (
        relative["truth_closes_level_alone"][
            "no_direct_or_indirect_state_recovery_above_bottom"
        ]
        is True
    )

    top = closure_level_receipt(
        source_occurrence_ids=["a", "b", "c"],
        relation_receipts=[edge("a", "b"), edge("b", "c", "OPEN")],
    )
    assert top["endpoint"] == "⊤"
    assert top["class_count"] == 1
    assert top["projective_fold"]["collapse"] == 1
    assert top["projective_fold"]["tan_value"] == "∞"
    assert top["existence_to_admission"]["existence_readings_are_constant"] is True
    assert top["truth_closes_level_alone"]["identity_reading_closed"] is False
    assert top["two_person_E2E"] == "OPEN"


def test_false_returns_do_not_generate_the_equality_level() -> None:
    level = closure_level_receipt(
        source_occurrence_ids=["a", "b"],
        relation_receipts=[edge("a", "b", "FALSE")],
    )
    assert level["endpoint"] == "⊥"
    assert level["equality_classes"] == [["a"], ["b"]]
    assert level["existence_to_admission"]["environment"] == []
    assert level["truth_issued"] is False


def test_live_sense_closes_the_level_and_drives_the_primary_interface(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        first = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": "same source returns through the living field",
                "authored_by": "person-a",
                "form_label": "note",
            },
        )
        assert first.status_code == 200, first.text
        first_level = first.json()["sense_receipt"]["closure_level"]
        assert first_level["endpoint"] == "⊥=⊤"
        assert first_level["projective_fold"]["not_a_user_selected_phase"] is True

        second = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": "same source returns through the living field",
                "authored_by": "person-b",
                "form_label": "note",
            },
        )
        assert second.status_code == 200, second.text
        payload = second.json()
        level = payload["sense_receipt"]["closure_level"]
        assert level["derived_from"].startswith("interaction-time Sense")
        assert level["endpoint"] == "⊤"
        assert level["class_count"] == 1
        assert level["state_count"] == 2
        assert level["projective_fold"]["tan_value"] == "∞"
        assert payload["sense_receipt"]["two_person_E2E"] == "OPEN"

        interface = client.get(
            "/supernet/interface",
            params={"focus_event_id": payload["event_id"]},
        )
        assert interface.status_code == 200, interface.text
        receipt = interface.json()
        assert receipt["closure_level"]["level_id"] == level["level_id"]
        assert receipt["sense_depth"]["nrrf825_derived"] is True
        assert receipt["sense_depth"]["closure_level_endpoint"] == "⊤"
        assert receipt["sense_depth"]["projective_fold_is_user_selected"] is False
        assert receipt["two_person_E2E"] == "OPEN"


def test_primary_supernet_renders_the_live_fold_without_a_level_widget(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        root = client.get("/")
        assert root.status_code == 200
        assert "Derived closure level · NRRF825" in root.text
        assert "data-derived-by':'NRRF825'" in root.text
        assert "tan((π/2)·collapse)" in root.text
        assert "no level control exists" in root.text
        assert 'type="range"' not in root.text

        capabilities = client.get("/supernet/interface/capabilities").json()
        assert capabilities["nrrf825_level_derived_on_primary_surface"] is True
        assert capabilities["projective_fold_is_user_selected"] is False
        assert capabilities["two_person_E2E"] == "OPEN"
