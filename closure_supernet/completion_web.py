from __future__ import annotations


COMPLETION_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Natural Translational Completion</title>
<style>
:root{color-scheme:dark;background:#080b10;color:#e8edf5;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
body{margin:0;padding:24px;max-width:1180px;margin-inline:auto}.grid{display:grid;grid-template-columns:minmax(300px,1fr) minmax(360px,1.5fr);gap:18px}.card{border:1px solid #293241;background:#10151d;border-radius:14px;padding:18px}h1{font-size:clamp(1.45rem,4vw,2.5rem);margin:.2rem 0}h2{font-size:1rem;color:#a9c3e8}.muted{color:#8c9aab}label{display:block;margin-top:10px;font-size:.85rem}input,textarea,button{width:100%;box-sizing:border-box;border:1px solid #344153;background:#0a0f16;color:#e8edf5;border-radius:8px;padding:10px;font:inherit}textarea{min-height:110px;resize:vertical}button{margin-top:14px;cursor:pointer;background:#172335}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#080c12;border-radius:9px;padding:12px;min-height:100px}.pill{display:inline-block;border:1px solid #344153;border-radius:999px;padding:4px 8px;margin:3px;font-size:.75rem}.ok{color:#9ee6b8}.open{color:#ffd38a}@media(max-width:820px){.grid{grid-template-columns:1fr}}</style>
</head>
<body>
<p class="muted">NRRF798 · NRRF799 · one canonical Supernet integrator</p>
<h1>Local step → finite reach → natural completion → translational truth</h1>
<p>Submit a finite local translation graph. The runtime does not assume an equivalence: it generates the completion, retains finite path witnesses, checks local/global invariant readings, returns the quotient, and keeps the field <span class="open">OPEN</span>.</p>
<div class="grid">
<section class="card">
<h2>Create completion</h2>
<label>Name<input id="name" value="translation by two"></label>
<label>Presentations (one per line)<textarea id="presentations">0
1
2
3</textarea></label>
<label>Admitted steps: source,target,label (one per line)<textarea id="steps">0,2,+2
1,3,+2</textarea></label>
<label>Optional reading values as JSON object<textarea id="reading">{"0":0,"1":1,"2":0,"3":1}</textarea></label>
<button id="submit">Integrate completion</button>
<p id="status" class="muted"></p>
</section>
<section class="card">
<h2>Current completion field</h2>
<div id="stats"></div>
<pre id="result">No completion submitted in this browser.</pre>
</section>
</div>
<script>
const $=id=>document.getElementById(id);
function lines(id){return $(id).value.split(/\n+/).map(x=>x.trim()).filter(Boolean)}
function render(obj){$('result').textContent=JSON.stringify(obj,null,2);if(obj&&obj.evaluation){const e=obj.evaluation;$('stats').innerHTML=`<span class="pill">classes ${e.classes.length}</span><span class="pill">max witness ${e.max_finite_witness_length}</span><span class="pill ok">finite lineage ${e.every_identification_has_finite_local_path}</span><span class="pill ok">local=global ${e.local_global_reading_equivalent}</span><span class="pill open">TRUE not issued</span>`}}
async function refresh(){const r=await fetch('/network/completion/field');if(r.ok){const p=await r.json();$('stats').innerHTML=`<span class="pill">systems ${p.stats.systems}</span><span class="pill">steps ${p.stats.local_steps}</span><span class="pill">classes ${p.stats.completion_classes}</span><span class="pill ok">finite path ${p.stats.finite_path_complete}</span>`}}
$('submit').onclick=async()=>{try{const presentations=lines('presentations');const steps=lines('steps').map(line=>{const [source,target,...rest]=line.split(',').map(x=>x.trim());return{source,target,label:rest.join(',')||'local translation',admitted_for_completion:true}});const raw=$('reading').value.trim();const readings=raw?[{name:'submitted reading',values:JSON.parse(raw)}]:[];$('status').textContent='integrating…';const r=await fetch('/network/completion/systems',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({name:$('name').value,authored_by:'public participant',presentations,steps,readings,truths:[]})});const payload=await r.json();if(!r.ok)throw new Error(payload.detail||r.statusText);render(payload);$('status').textContent='returned OPEN; new local steps may reopen';refresh()}catch(e){$('status').textContent=String(e)}};
refresh().catch(()=>{});
</script>
</body>
</html>'''
