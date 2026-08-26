from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "docs" / "index.html"


def test_public_root_is_a_running_closure_field():
    html = ROOT.read_text(encoding="utf-8")
    assert "<title>Uniface — Closure field</title>" in html
    assert "Note-Guided Closure Interface" not in html
    assert "Sense(Obs) → unique unitary path selector → Translation Event (admit → return → reopen) → next Sense" in html
    assert "TRUE not issued" in html
    assert "Two-person E2E OPEN" in html
    assert "function uniqueUnitaryPathPartition" in html
    assert "runStage('sense')" in html
    assert "setInterval(tick,1400)" in html
    assert 'runtime_center:\'TranslationEvent\'' in html
    assert "participant:'OPEN'" in html
    assert "Harry" not in html
    assert "ChatGPT" not in html
    transport = html.split("Hidden transport evidence")[1]
    assert 'id="noteReturn"' in transport
    assert html.index("id=\"teGrid\"") < html.index("id=\"noteReturn\"")
    assert "leftover_pr_10:'not this'" in html or 'leftover_pr_10:\'not this\'' in html
