from __future__ import annotations


HANDED_LIFE_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Handed Life · Closure Supernet</title>
<style>
:root{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:#090b0d;color:#e9edf0}body{margin:0;padding:24px}main{max-width:1180px;margin:auto}h1,h2{font-weight:600}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}.card{border:1px solid #39414a;border-radius:12px;padding:16px;background:#11151a}label{display:block;margin:8px 0 4px}input,select,button,textarea{box-sizing:border-box;width:100%;padding:10px;border-radius:8px;border:1px solid #4a5561;background:#0b0f13;color:inherit}button{margin-top:12px;cursor:pointer}pre{white-space:pre-wrap;word-break:break-word;max-height:560px;overflow:auto}.small{opacity:.78}.status{padding:8px 0}</style>
</head>
<body><main>
<h1>Handed life temporal closure</h1>
<p class="small">NRRF799/800 as one Supernet lens: four ball phases generate one hair class; ball return preserves hand; inverse hair return crosses the hand; self-limit is hand inversion at fixed phase. Submitted human standings are read relationally. No biological or universal human-law claim is issued.</p>
<div class="grid">
<section class="card"><h2>Create four-ball / one-hair system</h2>
<form id="systemForm">
<label>Name</label><input name="name" value="left-handed potential gate">
<label>Author</label><input name="authored_by" value="participant">
<label>Initial hand</label><select name="initial_hand"><option>LEFT</option><option>RIGHT</option></select>
<label>Initial ball phase</label><input name="initial_ball_phase" type="number" min="0" max="3" value="0">
<button>Create and integrate</button></form></section>
<section class="card"><h2>Read a human relation</h2>
<form id="relationForm">
<label>Name</label><input name="name" value="submitted human relation">
<label>Author</label><input name="authored_by" value="participant">
<label>Source participant</label><input name="source_participant" value="u">
<label>Target participant</label><input name="target_participant" value="v">
<label>Source standing</label><input name="source_standing" type="number" value="0">
<label>Target standing</label><input name="target_standing" type="number" value="1">
<label>Gate hand (explicit tie orientation)</label><select name="gate_hand"><option>LEFT</option><option>RIGHT</option></select>
<label>After source standing (optional)</label><input name="after_source_standing" type="number">
<label>After target standing (optional)</label><input name="after_target_standing" type="number">
<button>Read and integrate</button></form></section>
</div>
<section class="card" style="margin-top:16px"><div class="status" id="status">Loading field…</div><pre id="out"></pre></section>
<script>
const out=document.getElementById('out'),status=document.getElementById('status');
async function request(url,options){const r=await fetch(url,options);const text=await r.text();if(!r.ok)throw new Error(text);return JSON.parse(text)}
async function refresh(){const data=await request('/network/handed-life/field');status.textContent=`systems ${data.stats.systems} · records ${data.stats.records} · four-ball/one-hair ${data.stats.four_ball_one_hair}`;out.textContent=JSON.stringify(data,null,2)}
function formObject(form){return Object.fromEntries(new FormData(form).entries())}
document.getElementById('systemForm').addEventListener('submit',async e=>{e.preventDefault();try{const d=formObject(e.target);d.initial_ball_phase=Number(d.initial_ball_phase);await request('/network/handed-life/systems',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(d)});await refresh()}catch(err){status.textContent=err.message}});
document.getElementById('relationForm').addEventListener('submit',async e=>{e.preventDefault();try{const d=formObject(e.target);for(const k of ['source_standing','target_standing'])d[k]=Number(d[k]);for(const k of ['after_source_standing','after_target_standing']){if(d[k]==='')delete d[k];else d[k]=Number(d[k])}await request('/network/handed-life/human-relations',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(d)});await refresh()}catch(err){status.textContent=err.message}});
refresh().catch(err=>status.textContent=err.message);
</script>
</main></body></html>'''
