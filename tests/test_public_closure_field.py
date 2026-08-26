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
    js = _js()
    assert "<title>Uniface — Closure field</title>" in html
    assert "Note-Guided Closure Interface" not in html
    assert "Sense(Obs) → unique unitary path selector → Translation Event (admit → return → reopen) → next Sense" in html
    assert "TRUE not issued" in html
    assert "Two-person E2E OPEN" in html
    assert "function uniqueUnitaryPathPartition" in html
    assert "function uniqueUnitaryPathPartition" in js
    assert "runStage('sense')" in html
    assert "setInterval(tick,1400)" in html
    assert "runtime_center:'TranslationEvent'" in html
    assert "participant:'OPEN'" in html
    assert "Harry" not in html
    assert "ChatGPT" not in html
    assert "Harry" not in js
    assert "ChatGPT" not in js
    transport = html.split("Hidden transport evidence")[1]
    assert 'id="noteReturn"' in transport
    assert html.index('id="teGrid"') < html.index('id="noteReturn"')
    assert "leftover_pr_10:'not this'" in html or 'leftover_pr_10:\'not this\'' in html
    assert "function currentUnifiedField" in js
    assert "consumes:'unified supernet field'" in js


def test_nrrf781_relative_renormalization_is_inside_the_live_te():
    html = _html()
    js = _js()
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
    assert html.index('id="teGrid"') < html.index('id="noteReturn"')
    assert "Harry" not in html
    assert "ChatGPT" not in html
    assert html.count('id="teGrid"') == 1
    assert "addEventListener('click'" not in html.split("function bindPanZoom")[0]
    assert "function doTE" in html
    assert "function doReopen" in html
    assert "relative_renormalization" in html
    assert "function unifyField" in js
    assert "function unifyField" not in html


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
    assert "function uniqueUnitaryPathPartition" in html
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
    assert supernet.count("function persistCycle") == 0
    assert js.count("function persistCycle") == 1
    assert html.count("setInterval(tick,1400)") == 1
    assert "TRUE not issued" in supernet
    assert "truth_issued:false" in js
    assert FIELD_RUN.is_file()
    assert "consumes the currently unified field" in supernet
    assert "function uniqueUnitaryPathPartition" not in supernet
    assert "function currentUnifiedField" in js


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
    assert payload["sense_consumes"] == "unified supernet field"
    assert payload["prior_cycle_residues"] == []
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
    js = _js()
    js_fns = js[js.index("function r9(") : js.index("function translationEvent(")]
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


def test_reopening_sense_consumes_the_unified_field_not_only_last_te():
    import shutil
    import subprocess

    node = shutil.which("node")
    if node is None:
        return
    script = (
        "const u=require(" + json.dumps(str(LOOP_JS)) + ");"
        + r"""
u.resetLoop();
u.loop.geom.ss = 0.2;
u.doSense();
u.doSelect();
const p0 = u.loop.path;
if (p0.field_unit !== 0) throw new Error('cycle 0 should not mix an empty field');
if (Math.abs(p0.nextSs - 0.8) > 1e-12) throw new Error('halt/continuation must invert ss');
if (p0.zero_inf.indexOf('halt-as-reading') < 0) throw new Error('ss<0.5 is halt-as-reading');
if (p0.inverse_sensor_selection !== true) throw new Error('inverse_sensor_selection');
if (p0.finite_halt_oracle !== false) throw new Error('finite halt oracle');
u.loop.te = u.translationEvent();
if (u.loop.te.TRUE !== 'not issued') throw new Error('TRUE issued');
if (u.loop.te.two_person_E2E !== 'OPEN') throw new Error('E2E faked');
u.doReopen();
u.doSense();
const o1 = u.loop.obs;
if (o1.consumes !== 'unified supernet field') throw new Error('Sense does not consume unified field');
if (!o1.relative_reading || !o1.relative_reading.path) throw new Error('missing relative_reading matrix');
if (!o1.residue_scale || typeof o1.residue_scale.relative_scale !== 'number') throw new Error('missing residue_scale');
if (!Array.isArray(o1.prior_cycle_residues) || o1.prior_cycle_residues.length !== 1) throw new Error('missing prior cycle residues');
if (!o1.live_relation || !o1.live_relation.geom || !o1.live_relation.relative_renormalization) throw new Error('missing live_relation');
if (!o1.unified_field || o1.unified_field.unified !== true) throw new Error('unified_field not present');
if (o1.TRUE !== 'not issued' || o1.two_person_E2E !== 'OPEN') throw new Error('truth/e2e');
u.doSelect();
const p1 = u.loop.path;
if (p1.over !== 'unified supernet field' || p1.field_wide !== true) throw new Error('path not over field');
if (!(p1.field_unit > 0)) throw new Error('field unit did not enter the unique path');
if (Math.abs(p1.nextSs + o1.undetermined_string.ss - 1) > 1e-12) throw new Error('nextSs is not inverse of ss');
const lastOnly = {
  undetermined_string: o1.undetermined_string,
  residue_scale: o1.residue_scale,
  relative_reading: o1.relative_reading
};
const pLast = u.uniqueUnitaryPathPartition(lastOnly);
const pFull = u.uniqueUnitaryPathPartition(o1);
if (pFull.field_unit === pLast.field_unit && pFull.nextR === pLast.nextR) {
  throw new Error('unique path still linear last-TE-only');
}
u.loop.te = u.translationEvent();
u.doReopen();
u.doSense();
const o2 = u.loop.obs;
if (o2.prior_cycle_residues.length !== 2) throw new Error('prior residues did not accumulate');
u.doSelect();
console.log(JSON.stringify({
  ok: true,
  field_unit_0: p0.field_unit,
  field_unit_1: p1.field_unit,
  field_unit_full: pFull.field_unit,
  field_unit_last_te: pLast.field_unit,
  prior_1: o1.prior_cycle_residues.length,
  prior_2: o2.prior_cycle_residues.length,
  TRUE: o2.TRUE,
  two_person_E2E: o2.two_person_E2E
}));
"""
    )
    result = subprocess.run([node, "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["ok"] is True
    assert payload["field_unit_0"] == 0
    assert payload["field_unit_1"] != payload["field_unit_last_te"]
    assert payload["prior_1"] == 1
    assert payload["prior_2"] == 2
    assert payload["TRUE"] == "not issued"
    assert payload["two_person_E2E"] == "OPEN"


def test_root_and_supernet_share_field_wide_sense():
    html = _html()
    supernet = (DOCS / "supernet.html").read_text(encoding="utf-8")
    js = _js()
    assert "function unifyField" in js
    assert "function unifyField" not in html
    assert "function unifiedFieldUnit" in js
    assert "function currentUnifiedField" in js
    assert "consumes:'unified supernet field'" in js
    assert "over:'unified supernet field'" in js
    assert "function unifyField" not in supernet
    assert 'src="closure-field.js"' in supernet
    assert js.count("function uniqueUnitaryPathPartition") == 1
    assert "eyJ" not in js
    assert "eyJ" not in supernet
