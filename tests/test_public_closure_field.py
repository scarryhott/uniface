from pathlib import Path
import json


DOCS = Path(__file__).resolve().parents[1] / "docs"
ROOT = DOCS / "index.html"
LOOP_JS = DOCS / "closure-field.js"
FIELD_RUN = DOCS / "field-run.json"


def _html() -> str:
    return ROOT.read_text(encoding="utf-8")


def _js() -> str:
    return LOOP_JS.read_text(encoding="utf-8")


def test_public_root_is_a_running_closure_field():
    html = _html()
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


def test_nrrf781_relative_renormalization_is_inside_the_live_te():
    html = _html()
    assert "function localCutoffFamily" in html
    assert "function pairwiseRelativeRenormalization" in html
    assert "relative_reading" in html
    assert "absolute_level:null" in html
    assert "scheme_selected:false" in html
    assert "truth_issued:false" in html
    assert "relative renormalization" in html
    assert "cell('relative renormalization'" in html
    assert "residue_scale" in html
    assert "loop.scale" in html
    assert "TRUE not issued" in html
    assert "['TRUE','not issued']" in html
    assert "scheme_chart" in html
    assert "never_selected_as_truth:true" in html
    assert "derived_chart:true" in html
    assert "not_lean:true" in html
    assert "/renormalization" not in html
    assert 'id="renormalization"' not in html
    assert "setInterval(tick,1400)" in html
    assert html.index("id=\"teGrid\"") < html.index("id=\"noteReturn\"")
    assert "Harry" not in html
    assert "ChatGPT" not in html
    assert html.count('id="teGrid"') == 1
    assert "addEventListener('click'" not in html.split("function bindPanZoom")[0]
    assert "function doTE" in html
    assert "function doReopen" in html
    assert "relative_renormalization" in html


def test_supernet_is_the_same_loop_panzoom_projection():
    html = _html()
    js = _js()
    supernet = (DOCS / "supernet.html").read_text(encoding="utf-8")
    vercel = json.loads((DOCS / "vercel.json").read_text(encoding="utf-8"))
    assert vercel["cleanUrls"] is True
    assert vercel["trailingSlash"] is False
    assert not vercel.get("rewrites")
    assert (DOCS / "supernet.html").is_file()
    assert not (DOCS / "supernet").exists()
    assert 'src="closure-field.js"' in supernet
    assert "function uniqueUnitaryPathPartition" not in supernet
    assert "function localCutoffFamily" not in supernet
    assert "function pairwiseRelativeRenormalization" not in supernet
    assert "setInterval(tick,1400)" in js
    assert "path==='/supernet'" in js
    assert "function bindPanZoom" in js
    assert "function fieldRunSnapshot" in js
    assert "Pan/zoom reading of the same live root closure loop" in js
    assert 'id="zoomIn"' in supernet
    assert 'id="zoomOut"' in supernet
    assert 'id="zoomFit"' in supernet
    assert 'aria-label="pan zoom reading"' in supernet
    assert 'data-projection="panzoom"' in supernet
    assert supernet.count('id="noteReturn"') == 1
    assert "write transport receipt" in supernet.split("Hidden transport evidence")[1]
    assert html.count("function persistCycle") == 1
    assert js.count("function persistCycle") == 1
    assert html.count("setInterval(tick,1400)") == 1
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in js
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in supernet
    assert "TRUE not issued" in supernet
    assert "truth_issued:false" in js
    assert FIELD_RUN.is_file()


def test_field_run_json_is_the_same_occurrence_snapshot():
    import shutil
    import subprocess

    payload = json.loads(FIELD_RUN.read_text(encoding="utf-8"))
    assert payload["truth_issued"] is False
    assert payload["two_person_E2E"] == "OPEN"
    assert payload["TRUE"] == "not issued"
    assert payload["stage"] in {"sense", "select", "te", "reopen"}
    assert isinstance(payload["cycle"], int)
    assert payload["relative_reading"] is not None
    assert payload["nrrf781"]["derived_chart"] is True
    assert payload["nrrf781"]["not_lean"] is True
    assert "not Lean" in payload["nrrf781"]["nrrf781"]
    assert payload["nrrf781"]["absolute_level"] is None
    assert payload["nrrf781"]["scheme_selected"] is False
    assert payload["of"] == "one public root closure loop"
    assert "Lean" not in FIELD_RUN.read_text(encoding="utf-8").replace("not Lean", "")
    node = shutil.which("node")
    if node is None:
        return
    script = (
        "const u=require(" + json.dumps(str(LOOP_JS)) + ");"
        "process.stdout.write(JSON.stringify(u.fieldRunSnapshot()));"
    )
    result = subprocess.run([node, "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr or result.stdout
    live = json.loads(result.stdout)
    assert live == payload


def test_derived_cutoff_family_pairwise_delta_is_constant_and_carries_scale():
    """The live-cycle derived chart: common divergence ⇒ cutoff-constant Δ, carried scale."""
    inherited = 1.0
    r, ss, phase = 1.8, 0.5, 2
    unit_angle, unit_mag = 0.25, 0.45
    next_r, next_ss, next_phase = 2.2, 0.5, 3
    common = inherited * (1 + r)
    offsets = {
        "sense": r + ss + phase,
        "path": unit_angle * 4 + unit_mag * 2 + 1,
        "returned": next_r + next_ss + next_phase,
    }
    members = {name: [common * n + off for n in range(3)] for name, off in offsets.items()}
    pairwise = {}
    for left in members:
        pairwise[left] = {}
        for right in members:
            deltas = [members[left][n] - members[right][n] for n in range(3)]
            assert abs(deltas[0] - deltas[1]) < 1e-8
            assert abs(deltas[1] - deltas[2]) < 1e-8
            pairwise[left][right] = deltas[0]
    relative_scale = pairwise["path"]["sense"]
    assert relative_scale == offsets["path"] - offsets["sense"]

    common_next = relative_scale * (1 + r)
    members_next = {
        name: [common_next * n + off for n in range(3)] for name, off in offsets.items()
    }
    for left in members_next:
        for right in members_next:
            deltas = [members_next[left][n] - members_next[right][n] for n in range(3)]
            assert abs(deltas[0] - deltas[1]) < 1e-8
            assert abs(deltas[1] - deltas[2]) < 1e-8
            assert abs(deltas[0] - pairwise[left][right]) < 1e-8
    assert common_next != common


def test_extracted_root_js_relative_renormalization_runs():
    import shutil
    import subprocess

    node = shutil.which("node")
    if node is None:
        return
    html = _html()
    js_fns = html[html.index("function r9(") : html.index("function translationEvent(")]
    script = (
        js_fns
        + """
const O0={cycle:0,residue_scale:null,undetermined_string:{r:1.8,i:1.57,ss:0.5,phase:2,pole:'∞'}};
const part0={unit_angle:1.57/(Math.PI*2),unit_magnitude:1.8/4,nextR:2.2,nextI:2,nextSs:0.5,nextPhase:3};
const family0=localCutoffFamily(O0,part0);
const rr0=pairwiseRelativeRenormalization(family0);
if(rr0.relative_reading==null) throw new Error('expected constant pairwise');
if(rr0.absolute_level!==null) throw new Error('absolute_level');
if(rr0.scheme_selected!==false) throw new Error('scheme_selected');
if(rr0.truth_issued!==false) throw new Error('truth_issued');
if(rr0.scheme_chart.scheme_is_closure!==false) throw new Error('scheme is closure');
if(rr0.TRUE!=='not issued') throw new Error('TRUE issued');
const names=Object.keys(family0.members);
for(const i of names) for(const j of names){
  const d0=family0.members[i][0]-family0.members[j][0];
  const d1=family0.members[i][1]-family0.members[j][1];
  const d2=family0.members[i][2]-family0.members[j][2];
  if(Math.abs(d0-d1)>1e-9||Math.abs(d1-d2)>1e-9) throw new Error('not constant '+i+' '+j);
}
const O1={cycle:1,residue_scale:{relative_scale:rr0.relative_scale,relative_reading:rr0.relative_reading},undetermined_string:O0.undetermined_string};
const family1=localCutoffFamily(O1,part0);
if(Math.abs(family1.inherited_scale-rr0.relative_scale)>1e-9) throw new Error('scale not carried');
const rr1=pairwiseRelativeRenormalization(family1);
if(rr1.relative_reading==null) throw new Error('cycle 1 not constant');
console.log(JSON.stringify({ok:true,relative_scale_0:rr0.relative_scale,inherited_1:family1.inherited_scale,common_0:family0.common_coeff,common_1:family1.common_coeff}));
"""
    )
    result = subprocess.run([node, "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["ok"] is True
    assert payload["inherited_1"] == payload["relative_scale_0"]
    assert payload["common_0"] != payload["common_1"]
