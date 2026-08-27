from __future__ import annotations


EMBODIED_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Embodied Eight-Sheaf Supernet</title>
<style>
:root{color-scheme:dark;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;--bg:#070a10;--panel:#121927;--line:#344158;--text:#eef4fb;--muted:#a8b5c8;--accent:#a7b8ff;--good:#62d79d;--open:#e7bd58}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#1a2742,var(--bg) 48%);color:var(--text)}main{max-width:1240px;margin:auto;padding:38px 20px 70px}h1{font-size:clamp(34px,6vw,64px);margin:0 0 12px}.sub{max-width:1040px;color:var(--muted);line-height:1.62}.eq,.panel,pre{background:rgba(18,25,39,.97);border:1px solid var(--line);border-radius:15px;padding:15px}.eq,pre{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;overflow:auto}.grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:14px;margin-top:18px}.c4{grid-column:span 4}.c6{grid-column:span 6}.c8{grid-column:span 8}.c12{grid-column:span 12}@media(max-width:900px){.c4,.c6,.c8,.c12{grid-column:1/-1}}.panel h2{margin-top:0}.badges{display:flex;flex-wrap:wrap;gap:7px}.badge{padding:6px 9px;border:1px solid var(--line);border-radius:999px;font-size:12px}.good{color:var(--good);border-color:#39755b}.open{color:var(--open);border-color:#80682f}.muted{color:var(--muted);line-height:1.5}.sheaves{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.sheaf{background:#182033;border:1px solid #303c53;border-radius:11px;padding:10px}.sheaf strong{display:block;margin-bottom:4px}.scroll{overflow:auto;max-height:420px}table{width:100%;border-collapse:collapse;font-size:12px}th,td{padding:8px;border-bottom:1px solid #303c53;text-align:left}a{color:var(--accent)}
</style>
</head>
<body><main>
<h1>Embodied Eight-Sheaf Supernet</h1>
<p class="sub">One continuous field: embodied human interaction, Slearn perspective paths, Black Mirror sensing, tokenomic AI, physical resources, AGI/second-brain memory, first-person reports, and unknown/UAP hypotheses. The local ball is the current embodied return; the global hair is the still-open field of possible translations. “Memetic love” is represented only as reciprocal, source-preserving, consent-scoped, perspective-inclusive, reopenable translation—not as a physical force, emotion classifier, or score of human worth.</p>
<div class="eq">exact section → reciprocal translation → non-scalar natural component → local ball return ↔ global hair reopening → loop-sensor reintegration</div>
<div class="badges" style="margin-top:14px"><span class="badge good">one Supernet integrator</span><span class="badge good">resource metrics downstream</span><span class="badge open">unknown hypotheses remain OPEN</span><span class="badge open">TRUE not issued</span></div>
<div class="grid">
<section class="panel c6"><h2>Local ball</h2><div id="local" class="sheaves"></div></section>
<section class="panel c6"><h2>Global hair</h2><div id="global" class="sheaves"></div></section>
<section class="panel c4"><h2>Field state</h2><pre id="stats">loading</pre></section>
<section class="panel c8"><h2>Current closures</h2><div class="scroll"><table><thead><tr><th>Field</th><th>8 sheaves</th><th>Connected</th><th>Natural component</th><th>Global hair</th></tr></thead><tbody id="fields"></tbody></table></div></section>
<section class="panel c6"><h2>Reciprocal relations</h2><div class="scroll"><table><thead><tr><th>Relation</th><th>Left</th><th>Right</th><th>Love-admissible</th></tr></thead><tbody id="relations"></tbody></table></div></section>
<section class="panel c6"><h2>Loop-sensor returns</h2><div class="scroll"><table><thead><tr><th>Sensor</th><th>Resolution</th><th>Local halt</th><th>Global continuation</th><th>Complete?</th></tr></thead><tbody id="sensors"></tbody></table></div></section>
<section class="panel c12"><h2>Exact boundary</h2><p class="muted">The unknown/UAP sheaf stores observations and hypotheses as source-preserving OPEN material. This runtime does not verify alien claims, infer intention or emotion, define a physical syntropic force, establish quantum gravity, or let a resource metric determine foundational selection. All results remain relative forms of the same append-only Supernet field.</p><p><a href="/">root field</a> · <a href="/supernet">Supernet topology</a> · <a href="/frameworks">translational frameworks</a> · <a href="/docs">API</a></p></section>
</div>
</main>
<script>
const localKinds=['HUMAN_INTERACTION','SLEARN_PERSPECTIVE','BLACK_MIRROR_SENSOR','TOKENOMIC_AI'];
const globalKinds=['RESOURCE_WORLD','AGI_SECOND_BRAIN','PSYCHOPHENOMENAL','UNKNOWN_UAP_HYPOTHESIS'];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function card(section){return `<div class="sheaf"><strong>${esc(section.sheaf)}</strong><span>${esc(section.name)}</span><div class="muted">${esc(section.exact_text).slice(0,180)}</div></div>`}
(async()=>{try{const r=await fetch('/network/embodied/field',{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);const f=await r.json();document.getElementById('local').innerHTML=f.sections.filter(s=>localKinds.includes(s.sheaf)).map(card).join('')||'<span class="muted">OPEN</span>';document.getElementById('global').innerHTML=f.sections.filter(s=>globalKinds.includes(s.sheaf)).map(card).join('')||'<span class="muted">OPEN</span>';document.getElementById('stats').textContent=JSON.stringify(f.stats,null,2);document.getElementById('fields').innerHTML=f.fields.map(x=>`<tr><td>${esc(x.name)}</td><td>${x.evaluation.all_eight_sheaves_present}</td><td>${x.evaluation.field_connected}</td><td>${x.evaluation.unique_natural_component}</td><td>${x.evaluation.global_hair_open?'OPEN':'closed'}</td></tr>`).join('');document.getElementById('relations').innerHTML=f.relations.map(x=>`<tr><td>${esc(x.name)}</td><td>${esc(x.left_section_id)}</td><td>${esc(x.right_section_id)}</td><td>${x.evaluation.love_admissible}</td></tr>`).join('');document.getElementById('sensors').innerHTML=f.sensor_reads.map(x=>`<tr><td>${esc(x.name)}</td><td>${x.resolution}</td><td>${x.evaluation.local_halt_reading}</td><td>${x.evaluation.global_continuation_reading}</td><td>${x.evaluation.single_sensor_complete}</td></tr>`).join('')}catch(e){document.getElementById('stats').textContent=String(e)}})();
</script>
</body></html>'''
