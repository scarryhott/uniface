from pathlib import Path
import json
import shutil
import subprocess


DOCS = Path(__file__).resolve().parents[1] / "docs"
ROOT = DOCS / "index.html"
LOOP_JS = DOCS / "closure-field.js"
FIELD_RUN = DOCS / "field-run.json"
FIELD_RUN_API = DOCS / "api" / "field-run.js"


def _html() -> str:
    return ROOT.read_text(encoding="utf-8")


def _js() -> str:
    return LOOP_JS.read_text(encoding="utf-8")


def _node_json(script: str):
    node = shutil.which("node")
    if node is None:
        return None
    result = subprocess.run([node, "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr or result.stdout
    return json.loads(result.stdout)


def _live_field_run_snapshot():
    return _node_json(
        "const u=require(" + json.dumps(str(LOOP_JS)) + ");"
        "process.stdout.write(JSON.stringify(u.fieldRunSnapshot()));"
    )


def _invoke_field_run_handler(method: str = "GET"):
    script = (
        "const handler=require(" + json.dumps(str(FIELD_RUN_API)) + ");"
        "const headers={}; let body='';"
        "const res={statusCode:200,setHeader(k,v){headers[String(k).toLowerCase()]=v},"
        "end(b){body=b==null?'':String(b)}};"
        "handler({method:" + json.dumps(method) + "},res);"
        "process.stdout.write(JSON.stringify({status:res.statusCode,headers:headers,body:body}));"
    )
    return _node_json(script)


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
    rewrites = vercel.get("rewrites") or []
    assert not any(
        str(rule.get("source", "")).rstrip("/") in {"/supernet", "/supernet.html"}
        and str(rule.get("destination", "")).rstrip("/") in {"", "/", "/index", "/index.html"}
        for rule in rewrites
    )
    field_run = [rule for rule in rewrites if rule.get("source") == "/field-run.json"]
    assert field_run == [{"source": "/field-run.json", "destination": "/api/field-run"}]
    assert vercel.get("functions", {}).get("api/field-run.js", {}).get("includeFiles") == "closure-field.js"
    assert (DOCS / "supernet.html").is_file()
    assert not (DOCS / "supernet").exists()
    assert FIELD_RUN_API.is_file()
    assert not FIELD_RUN.exists()
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
    assert not FIELD_RUN.exists()
    assert FIELD_RUN_API.is_file()
    assert "consumes the currently unified field" in supernet
    assert "function uniqueUnitaryPathPartition" not in supernet
    assert "function currentUnifiedField" in js


def test_field_run_json_is_live_fieldRunSnapshot_projection():
    api = FIELD_RUN_API.read_text(encoding="utf-8")
    vercel = json.loads((DOCS / "vercel.json").read_text(encoding="utf-8"))
    assert not FIELD_RUN.exists()
    assert FIELD_RUN_API.is_file()
    assert "require('../closure-field.js')" in api
    assert "fieldRunSnapshot()" in api
    assert "application/json" in api
    assert "no-store" in api
    assert "eyJ" not in api
    rewrites = vercel.get("rewrites") or []
    assert {"source": "/field-run.json", "destination": "/api/field-run"} in rewrites
    assert not any(
        str(rule.get("source", "")).startswith("/supernet")
        and str(rule.get("destination", "")).rstrip("/") in {"", "/", "/index", "/index.html"}
        for rule in rewrites
    )

    live = _live_field_run_snapshot()
    if live is None:
        return
    served = _invoke_field_run_handler("GET")
    assert served is not None
    payload = json.loads(served["body"])
    assert served["status"] == 200
    assert served["headers"]["content-type"].startswith("application/json")
    assert served["headers"]["cache-control"] == "no-store"
    assert payload == live
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
    assert payload["brain_field"]["of"] == "brain field"
    assert payload["brain_field"]["kind"] == "hidden memory translation"
    assert payload["brain_field"]["not"] == "app"
    assert payload["brain_field"]["not_join"] is True
    assert payload["brain_field"]["not_blog"] is True
    assert payload["brain_field"]["not_catalog"] is True
    assert payload["brain_field"]["not_playlist"] is True
    assert payload["brain_field"]["TRUE"] == "not issued"
    assert payload["brain_field"]["truth_issued"] is False
    assert payload["brain_field"]["two_person_E2E"] == "OPEN"
    assert payload["brain_field"]["same_family"] is True
    assert "latent tumors" in payload["brain_field"]["occurrence"]["exact"]
    assert payload["field_relation"]["not_playlist"] is True
    assert payload["music_as_path"]["not_mp3"] is True
    assert payload["music_as_path"]["suno"].startswith("https://suno.com/song/")
    assert payload["not_mp3"] is True
    assert payload["field_relation"]["title"] == "Rising Sun"
    assert payload["prior_cycle_residues"] == []
    assert isinstance(payload["unresolved_alternatives"], list)
    assert payload["selected_path"] not in payload["unresolved_alternatives"]
    assert payload["admissibility_space"]["realized_closure"] == payload["selected_path"]
    assert payload["admissibility_space"]["remaining_potential"] == payload["unresolved_alternatives"]
    assert payload["admissibility_space"]["discarded_linear_leftover"] is False
    assert payload["admissibility_space"]["live_potential"] is True
    assert payload["admissibility_space"]["TRUE"] == "not issued"
    assert payload["admissibility_space"]["two_person_E2E"] == "OPEN"
    assert payload["admissibility_space"]["finite_halt_oracle"] is False
    assert isinstance(payload["isomorphism_classes"], list)
    assert payload["isomorphism_classes"] == payload["admissibility_space"]["isomorphism_classes"]
    assert payload["selected_path"] in payload["selected_class"]
    assert payload["selected_class"] == payload["admissibility_space"]["selected_class"]
    for member in payload["selected_class"]:
        assert member not in payload["unresolved_alternatives"]
    other = [
        member
        for cls in payload["isomorphism_classes"]
        if payload["selected_path"] not in cls
        for member in cls
    ]
    assert payload["unresolved_alternatives"] == other
    assert ["rule", "computational"] in payload["isomorphism_classes"]
    dumped = json.dumps(payload)
    assert "Lean" not in dumped.replace("not Lean", "")

    again = json.loads(_invoke_field_run_handler("GET")["body"])
    assert again == live
    assert again["isomorphism_classes"] == live["isomorphism_classes"]
    assert again["selected_class"] == live["selected_class"]
    assert again["truth_issued"] is False


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
if (!u.loop.obs.brain_field || !u.loop.obs.brain_occurrence) throw new Error('Sense missing brain field');
if (u.loop.obs.brain_field.of !== 'brain field') throw new Error('brain field of');
if ((u.loop.obs.prior_cycle_residues||[]).length !== 0) throw new Error('cycle 0 already has prior residues');
u.doSelect();
const p0 = u.loop.path;
const p0bare = u.uniqueUnitaryPathPartition({undetermined_string: u.loop.obs.undetermined_string, residue_scale: u.loop.obs.residue_scale, relative_reading: u.loop.obs.relative_reading});
if (p0bare.field_unit !== 0) throw new Error('cycle 0 local-only unit should be 0');
if (p0.field_unit === p0bare.field_unit) throw new Error('brain field writing did not enter the unique path');
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
  field_unit_0_bare: p0bare.field_unit,
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
    assert payload["field_unit_0_bare"] == 0
    assert payload["field_unit_0"] != payload["field_unit_0_bare"]
    assert payload["field_unit_1"] != payload["field_unit_last_te"]
    assert payload["prior_1"] == 1
    assert payload["prior_2"] == 2
    assert payload["TRUE"] == "not issued"
    assert payload["two_person_E2E"] == "OPEN"


def test_te_feeds_unresolved_alternatives_into_unified_field():
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
const rem0 = u.loop.obs.undetermined_string.remainder.slice();
const realized0 = u.loop.obs.undetermined_string.scenario;
u.doSelect();
const p0 = u.loop.path;
const unresolved0 = p0.unresolved_alternatives;
if (!Array.isArray(unresolved0) || unresolved0.length < 1) throw new Error('unresolved dropped other classes');
if (unresolved0.indexOf(p0.formId) >= 0) throw new Error('selected form still in unresolved');
if (!Array.isArray(p0.selected_class) || p0.selected_class.indexOf(p0.formId) < 0) throw new Error('selected class missing representative');
p0.selected_class.forEach(function(id){if (unresolved0.indexOf(id) >= 0) throw new Error('selected class member still a distinct remaining direction');});
const other0 = rem0.filter(function(id){return p0.selected_class.indexOf(id) < 0;});
if (JSON.stringify(unresolved0) !== JSON.stringify(other0)) throw new Error('unresolved is not the other isomorphism classes');
if (p0.selects_over !== 'translational isomorphism classes') throw new Error('selector not over isomorphism classes');
if (p0.class_count !== p0.isomorphism_classes.length) throw new Error('class_count');
if (p0.class_count > rem0.length) throw new Error('more classes than remainder');
if (p0.discarded_linear_leftover !== false) throw new Error('leftover still discarded');
if (Math.abs(p0.nextSs - 0.8) > 1e-12) throw new Error('halt/continuation must invert ss');
if (p0.finite_halt_oracle !== false) throw new Error('finite halt oracle');
u.loop.te = u.translationEvent();
if (u.loop.te.TRUE !== 'not issued') throw new Error('TRUE issued');
if (u.loop.te.two_person_E2E !== 'OPEN') throw new Error('E2E faked');
if (JSON.stringify(u.loop.te.unresolved_alternatives) !== JSON.stringify(unresolved0)) throw new Error('TE dropped unresolved');
if (u.loop.te.admissibility_space.realized_closure !== p0.formId) throw new Error('TE missing realized closure');
if (JSON.stringify(u.loop.te.admissibility_space.remaining_potential) !== JSON.stringify(unresolved0)) throw new Error('TE missing remaining potential');
u.doReopen();
const field = u.currentUnifiedField();
if (JSON.stringify(field.unresolved_alternatives) !== JSON.stringify(unresolved0)) throw new Error('field dropped unresolved');
if (field.selected_path !== p0.formId) throw new Error('field missing selected path');
if (field.admissibility_space.realized_closure !== p0.formId) throw new Error('field missing realized closure');
if (JSON.stringify(field.admissibility_space.remaining_potential) !== JSON.stringify(unresolved0)) throw new Error('field missing remaining potential');
if (field.truth_issued !== false || field.TRUE !== 'not issued' || field.two_person_E2E !== 'OPEN') throw new Error('truth/e2e');
u.doSense();
const o1 = u.loop.obs;
if (JSON.stringify(o1.undetermined_string.remainder) !== JSON.stringify(unresolved0)) throw new Error('next Sense remainder refilled linearly');
if (o1.undetermined_string.remainder.indexOf(realized0) >= 0) throw new Error('previously realized form reintroduced as leftover');
if (o1.undetermined_string.remainder.indexOf(p0.formId) >= 0) throw new Error('selected form still in next remainder');
if (JSON.stringify(o1.unresolved_alternatives) !== JSON.stringify(unresolved0)) throw new Error('Sense did not consume unresolved');
if (!o1.admissibility_space || o1.admissibility_space.realized_closure !== p0.formId) throw new Error('Sense missing admissibility_space');
u.doSelect();
const p1 = u.loop.path;
if (JSON.stringify(p1.remainder) !== JSON.stringify(unresolved0)) throw new Error('selector did not read remaining potential');
if (Math.abs(p1.nextSs + o1.undetermined_string.ss - 1) > 1e-12) throw new Error('nextSs is not inverse of ss');
const withoutAlts = {
  undetermined_string: o1.undetermined_string,
  residue_scale: o1.residue_scale,
  relative_reading: o1.relative_reading,
  prior_cycle_residues: o1.prior_cycle_residues,
  live_relation: o1.live_relation,
  unified_field: Object.assign({}, o1.unified_field, {unresolved_alternatives: [], admissibility_space: null})
};
const pNoAlts = u.uniqueUnitaryPathPartition(withoutAlts);
if (p1.field_unit === pNoAlts.field_unit) throw new Error('remaining potential did not enter the unique path mix');
console.log(JSON.stringify({
  ok: true,
  selected_0: p0.formId,
  rem0: rem0,
  unresolved0: unresolved0,
  rem1: o1.undetermined_string.remainder,
  TRUE: field.TRUE,
  two_person_E2E: field.two_person_E2E,
  truth_issued: field.truth_issued
}));
"""
    )
    result = subprocess.run([node, "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["ok"] is True
    assert payload["selected_0"] not in payload["unresolved0"]
    assert payload["rem1"] == payload["unresolved0"]
    assert payload["TRUE"] == "not issued"
    assert payload["two_person_E2E"] == "OPEN"
    assert payload["truth_issued"] is False


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
    assert "function remainingPotential" in js
    assert "function liveRemainder" in js
    assert "function isomorphismClassesOf" in js
    assert "function translationalSignature" in js
    assert "function classRemainder" in js
    assert "unresolved_alternatives" in js
    assert "admissibility_space" in js
    assert "remaining_potential" in js
    assert "selects_over:'translational isomorphism classes'" in js
    assert "function remainingPotential" not in html
    assert "function liveRemainder" not in html
    assert "function isomorphismClassesOf" not in html
    assert "function unifyField" not in supernet
    assert 'src="closure-field.js"' in supernet
    assert js.count("function uniqueUnitaryPathPartition") == 1
    assert "eyJ" not in js
    assert "eyJ" not in supernet
    assert "remaining potential" in supernet
    assert "unresolved alternatives as live admissibility space" in supernet
    assert "translational isomorphism classes of those unresolved admissible translations" in supernet
    assert "this writing as hidden memory" in supernet
    assert "function brainFieldReading" in js
    assert "function brainFieldReading" not in html
    assert "function brainFieldReading" not in supernet
    assert "BRAIN_OCCURRENCES" in js
    assert "holllow grounds of night" in js
    assert "FIELD_RELATIONS" in js
    assert "not_playlist:true" in js


def test_selector_operates_over_translational_isomorphism_classes():
    import shutil
    import subprocess

    node = shutil.which("node")
    if node is None:
        return
    script = (
        "const u=require(" + json.dumps(str(LOOP_JS)) + ");"
        + r"""
u.resetLoop();
u.doSense();
const rem0 = u.loop.obs.undetermined_string.remainder.slice();
const classes0 = u.isomorphismClassesOf(rem0, u.loop.obs);
const ruleClass = classes0.find(function(c){return c.members.indexOf('rule')>=0;});
if (!ruleClass || ruleClass.members.indexOf('computational')<0) throw new Error('rule and computational must be isomorphic under TENM');
if (ruleClass.key !== 'OPEN|TRUE|FALSE|OPEN') throw new Error('cycle-0 signature is TENM, not relative_reading');
if (classes0.length !== 4) throw new Error('expected 4 TENM classes on cycle 0, got '+classes0.length);
u.doSelect();
const p0 = u.loop.path;
if (p0.selects_over !== 'translational isomorphism classes') throw new Error('selects_over');
if (p0.class_count !== 4) throw new Error('selector still slots remainder length');
if (p0.slot !== 2) throw new Error('class slot should be 2 under default t');
if (JSON.stringify(p0.selected_class) !== JSON.stringify(['rule','computational'])) throw new Error('selected class');
if (p0.formId !== 'rule') throw new Error('representative is first class member');
if (p0.unresolved_alternatives.indexOf('computational')>=0) throw new Error('isomorphic sibling still a distinct direction');
if (JSON.stringify(p0.unresolved_alternatives) !== JSON.stringify(['coherent','contradiction','culture'])) throw new Error('other classes dropped');
if (Math.abs(p0.nextSs + u.loop.obs.undetermined_string.ss - 1) > 1e-12) throw new Error('halt/continuation not inverse');
if (p0.finite_halt_oracle !== false) throw new Error('finite halt oracle');
u.loop.te = u.translationEvent();
if (u.loop.te.TRUE !== 'not issued') throw new Error('TRUE issued');
if (u.loop.te.two_person_E2E !== 'OPEN') throw new Error('E2E faked');
u.doReopen();
u.doSense();
const o1 = u.loop.obs;
if (JSON.stringify(o1.undetermined_string.remainder) !== JSON.stringify(['coherent','contradiction','culture'])) throw new Error('next remainder not other classes');
if (!o1.relative_reading || !o1.relative_reading.path) throw new Error('missing relative_reading');
const classes1 = u.isomorphismClassesOf(o1.undetermined_string.remainder, o1);
if (classes1.some(function(c){return c.key.indexOf(',')<0;})) throw new Error('cycle 1 still using TENM key under relative_reading');
if (classes1.length !== 3) throw new Error('other classes must remain distinct under default relative_reading');
const stillIso = u.isomorphismClassesOf(['rule','computational','coherent'], o1);
const stillRule = stillIso.find(function(c){return c.members.indexOf('rule')>=0;});
if (!stillRule || stillRule.members.indexOf('computational')<0) throw new Error('same TENM must stay isomorphic under relative_reading');
if (stillRule.members.indexOf('coherent')>=0) throw new Error('distinct TENM merged under default relative_reading');
const zeroRr = {
  sense:{sense:0,path:0,returned:0},
  path:{sense:0,path:0,returned:0},
  returned:{sense:0,path:0,returned:0}
};
const merged = u.isomorphismClassesOf(rem0, Object.assign({}, u.loop.obs, {relative_reading: zeroRr, live_relation:null, selected_path:'during', undetermined_string:Object.assign({}, u.loop.obs.undetermined_string, {scenario:'during'})}));
const memOpen = merged.find(function(c){return c.members.indexOf('coherent')>=0;});
if (!memOpen || memOpen.members.indexOf('rule')<0 || memOpen.members.indexOf('computational')<0) throw new Error('zero relative_reading should merge same-M translations');
const memFalse = merged.find(function(c){return c.members.indexOf('culture')>=0;});
if (!memFalse || memFalse.members.indexOf('contradiction')<0) throw new Error('zero relative_reading should merge FALSE-memory translations');
if (merged.length !== 2) throw new Error('zero relative_reading should yield two M-delta classes');
console.log(JSON.stringify({
  ok: true,
  class_count_0: p0.class_count,
  selected_class: p0.selected_class,
  unresolved0: p0.unresolved_alternatives,
  rem1: o1.undetermined_string.remainder,
  class_count_1: classes1.length,
  merged_zero: merged.map(function(c){return c.members;}),
  TRUE: o1.TRUE,
  two_person_E2E: o1.two_person_E2E
}));
"""
    )
    result = subprocess.run([node, "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["ok"] is True
    assert payload["class_count_0"] == 4
    assert payload["selected_class"] == ["rule", "computational"]
    assert payload["unresolved0"] == ["coherent", "contradiction", "culture"]
    assert payload["rem1"] == payload["unresolved0"]
    assert payload["class_count_1"] == 3
    assert payload["TRUE"] == "not issued"
    assert payload["two_person_E2E"] == "OPEN"


def test_sense_consumes_brain_field_writing_on_the_public_page():
    html = _html()
    js = _js()
    supernet = (DOCS / "supernet.html").read_text(encoding="utf-8")
    assert "not an app and not a join product" in supernet
    assert "font-family:Inter" not in supernet
    assert "#19243f" not in supernet
    assert "font-family:Palatino" in supernet
    assert 'id="brainFace"' in supernet
    assert 'id="pathTitle"' in supernet
    assert 'id="pathLyric"' in supernet
    assert 'id="pathSound"' in supernet
    assert "anatomy tree, rings of time, drone-wire forest" in supernet
    assert "Join" not in supernet
    assert "invite" not in supernet.lower()
    assert "Share" not in supernet
    assert "playlist" not in supernet.lower()
    assert "INDEX.md" not in supernet
    assert "suno.com/song" not in supernet
    assert "Goldfish Don't Fly" not in supernet
    assert "Check Your Shoulders" not in supernet
    assert "Common App" not in supernet
    assert "bitcoin" not in supernet.lower()
    assert "Harry" not in supernet
    assert "ChatGPT" not in supernet
    assert "Harry" not in js
    assert "ChatGPT" not in js
    assert "Harry" not in html
    assert "ChatGPT" not in html
    assert "BRAIN_OCCURRENCES" in js
    assert "FIELD_RELATIONS" in js
    assert "function fieldRelationOf" in js
    assert "function brainFieldReading" in js
    assert "function currentBrainOccurrence" in js
    assert "same_family:true" in js
    assert "not_two_products:true" in js
    assert "not_join:true" in js
    assert "not_blog:true" in js
    assert "not_playlist:true" in js
    assert "not_inventory:true" in js
    assert "holllow grounds of night" in js
    assert "shared seeds of flowing flowering experience" in js
    assert "tree of life extends its naked leaves to the sky" in js
    assert "You can't let go of who you are" in js
    assert "Without nature there is no life" in js
    assert "A Field for Brains" in js
    assert "Goldfish Don't Fly" in js
    assert "https://suno.com/song/688e6054-0d09-4669-8f43-d588486658f2" in js
    assert "drone-wire forest" in js
    assert "source–sink / up–down–through" in js
    assert "yin–yang as relation not physics" in js
    assert "not_physics:true" in js
    assert "id=\"glass\"" in js
    assert "mirrored-looking device" in js
    assert "the third is through" in js
    assert "Local representation with global action through agentic second brains." in js
    assert "BLACK_MIRROR_TRANSLATIONAL_TRUTH" not in js
    assert "BLACK_MIRROR_TRANSLATIONAL_TRUTH.md" not in supernet
    assert not (ROOT.parents[0] / "BLACK_MIRROR_TRANSLATIONAL_TRUTH.md").exists()
    assert "scarryhott/black-mirror" not in supernet
    assert 'id="teGrid"' in supernet
    assert "Sense(Obs) → unique unitary path selector → Translation Event (admit → return → reopen) → next Sense" in supernet
    assert "function uniqueUnitaryPathPartition" not in supernet
    assert "function uniqueUnitaryPathPartition" in js
    assert "function currentUnifiedField" in js
    assert "function isomorphismClassesOf" in js
    assert "truth_issued:false" in js
    assert "FOUNDATION.md" not in supernet
    assert "When we forget the learned lessons" not in supernet
    assert "holllow grounds of night" not in supernet
    assert "one light-bulb idea a day" not in supernet
    assert "Three Body Problem" not in supernet
    assert "Purple Rain" not in supernet
    assert "embodied.html" not in supernet
    assert "/embodied" not in supernet
    assert supernet.index('id="canvas"') < supernet.index('id="teGrid"')
    assert "<summary>Translation Event cells (chart, not the face)</summary>" in supernet
    te_block = supernet.split('id="teGrid"')[0]
    assert te_block.rfind("<details>") > te_block.rfind("</details>")
    assert "min-height:100vh" in supernet
    node = shutil.which("node")
    if node is None:
        return
    live = _live_field_run_snapshot()
    assert live is not None
    assert live["truth_issued"] is False
    assert live["TRUE"] == "not issued"
    assert live["two_person_E2E"] == "OPEN"
    brain = live["brain_field"]
    assert brain["of"] == "brain field"
    assert brain["not"] == "app"
    assert brain["not_join"] is True
    assert brain["not_blog"] is True
    assert brain["not_catalog"] is True
    assert brain["not_playlist"] is True
    assert brain["same_family"] is True
    assert brain["truth_issued"] is False
    assert brain["not_physics"] is True
    assert brain["alternative"] == "translational truth"
    assert brain["capture"] == "relative representation mistaken for the whole relation"
    assert brain["device"] == "mirrored-looking device"
    assert brain["through"] == "the third is through"
    assert "yin–yang as relation not physics" in brain["grammar"]
    assert "mirrored-looking device" in brain["visual"]
    assert brain["not_invite"] is True
    assert brain["money_not_network"] is True
    assert brain["not_product_spec"] is True
    assert brain["drive_notes"] == "same brain field"
    assert live["field_relation"]["title"] == "Rising Sun"
    assert live["field_relation"]["not_playlist"] is True
    assert live["field_relation"]["suno"].startswith("https://suno.com/song/")
    assert live["field_relation"]["not_mp3"] is True
    assert live["field_relation"]["not_lfs"] is True
    assert live["field_relation"]["official_pages"] is True
    assert live["field_relation"]["style"] == "You can't let go of who you are"
    assert live["music_as_path"]["title"] == "Rising Sun"
    assert live["music_as_path"]["suno"] == live["field_relation"]["suno"]
    assert live["not_mp3"] is True
    assert live["not_lfs"] is True
    assert live["not_playlist"] is True
    assert "https://suno.com/song/2c2bc9b0-b18b-4e8e-b347-4db1ef4c387e" in js
    assert "https://suno.com/song/cb02239a-7c30-4fd2-aa41-c3b2498a16ee" in js
    assert "https://suno.com/song/c3522059-b222-4990-8108-4ffbaa4d74a3" in js
    assert "https://suno.com/song/3cfa0f34-2fc3-4cf7-8e3c-fc306f2d42f9" in js
    assert "Three Body Problem" in js
    assert "Purple Rain" in js
    assert "Another Mother Running Roads" in js
    assert "Blue Grey Melodies" in js
    assert "Ocean Winds" in js
    assert "Mushroom Clouds" in js
    assert "Remove Section" not in supernet
    assert "*.mp3" in (DOCS.parent / ".gitignore").read_text(encoding="utf-8")
    assert not list(DOCS.rglob("*.mp3"))
    assert not list(DOCS.parent.glob("*.mp3"))
    ids = [item["id"] for item in brain["occurrences"]]
    assert "hidden-memory-2026-08-26" in ids
    assert "naked-leaves-sky" in ids
    assert "flowering-seeds" in ids
    assert "drone-wire-forest" in ids
    assert "lyric-cant-let-go" in ids
    assert "field-for-brains" in ids
    assert "black-mirror-translation" in ids
    assert "black-mirror-through" in ids
    assert "black-mirror-local-global" in ids
    assert "three-body" in ids
    assert "ocean-winds" in ids
    assert "closure-doc-nature" in ids
    assert "closure-doc-unification" in ids
    assert "closure-doc-moral" in ids
    assert "originlessness" in ids
    assert "ball-thrown" in ids
    assert "color-collapse" in ids
    assert "closure-doc-mirror" in ids
    assert "lyric-style-is-brain" in ids
    exacts = "\n".join(item["exact"] for item in brain["occurrences"])
    assert "latent tumors" in exacts
    assert "holllow grounds of night" in exacts
    assert "tree of life extends its naked leaves to the sky" in exacts
    assert "You can only point where you want to go" in exacts
    assert "Without nature there is no life" in exacts
    assert "thermodynamic potential gate" in exacts
    assert "We who share moral truth will not law suffering" in exacts
    assert "unification of axiom and geometry" in exacts
    assert "Style is the brain." in exacts
    assert "Flip the triangle so the base is in the sky." in exacts
    assert "a black mirror" in exacts
    assert "Style is the brain." in js
    assert "thermodynamic potential gate" not in supernet
    assert "Common App" not in supernet
    assert "Empathy" not in supernet
    assert "MainStreet" not in supernet
    assert "Untitled" not in supernet
    assert "bitcoin" not in supernet.lower()
    assert "bitcoin" not in js.lower()
    assert "Join" not in supernet
    assert ["rule", "computational"] in live["isomorphism_classes"]

