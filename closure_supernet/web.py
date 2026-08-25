from __future__ import annotations

DASHBOARD_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Closure Supernet Runtime</title>
<style>
:root{--bg:#080b11;--panel:#151b29;--line:#394660;--text:#edf2f9;--muted:#aab6c8;--accent:#a2b6ff;--true:#59d494;--open:#e7bd55;--false:#ff747d}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#192441,var(--bg) 45%);color:var(--text);font-family:Inter,system-ui,sans-serif}header,main{padding:24px clamp(16px,5vw,64px)}header{border-bottom:1px solid var(--line)}h1{margin:0 0 8px;font-size:clamp(30px,5vw,56px)}.sub{color:var(--muted);max-width:1000px;line-height:1.55}.eq,.panel{background:rgba(21,27,41,.95);border:1px solid var(--line);border-radius:15px;padding:16px}.eq{font-family:ui-monospace,monospace;margin-top:16px}.grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:16px}.c4{grid-column:span 4}.c8{grid-column:span 8}.c12{grid-column:span 12}@media(max-width:900px){.c4,.c8,.c12{grid-column:1/-1}}button,textarea{width:100%;background:#1d2536;color:var(--text);border:1px solid var(--line);border-radius:10px;padding:10px}button{cursor:pointer;margin-top:8px}.metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.metric{background:#1d2536;padding:10px;border-radius:10px}.metric strong{display:block;font-size:20px}.muted{color:var(--muted)}pre{white-space:pre-wrap;max-height:430px;overflow:auto;background:#0d121d;padding:12px;border-radius:10px}table{width:100%;border-collapse:collapse;font-size:12px}th,td{padding:8px;border-bottom:1px solid #303a50;text-align:left}.badge{display:inline-block;padding:6px 9px;border-radius:999px;margin:3px;font-weight:700}.TRUE{color:var(--true)}.OPEN{color:var(--open)}.FALSE{color:var(--false)}
</style>
</head>
<body>
<header><h1>Closure Supernet Runtime</h1><div class="sub">Autonomous sensing, configured interpretation, constitutional admission, Black Mirror projection, and continuous reopening. Exact notes remain canonical; no Turing-completeness or terminal-closure assumption is made.</div><div class="eq">source note ↔ understanding ↔ interpretation ↔ interaction ↔ admission ↔ provisional return ↔ reopening</div></header>
<main><div class="grid">
<section class="panel c4"><h2>Runtime</h2><div id="status" class="metrics"></div><button onclick="cycle()">Run one cycle</button><button onclick="start()">Start autonomy</button><button onclick="stop()">Stop autonomy</button></section>
<section class="panel c8"><h2>Ingest exact occurrence</h2><textarea id="note" rows="8" placeholder="Paste exact notes here; original text will be immutable."></textarea><button onclick="ingest()">Ingest and reopen</button><div id="ingestResult" class="muted"></div></section>
<section class="panel c8"><h2>Black Mirror projection</h2><pre id="projection"></pre></section>
<section class="panel c4"><h2>Open seams</h2><div id="seams"></div></section>
<section class="panel c12"><h2>Recent events</h2><div style="overflow:auto"><table><thead><tr><th>seq</th><th>event</th><th>entity</th><th>time</th></tr></thead><tbody id="events"></tbody></table></div></section>
</div></main>
<script>
async function req(url,opts){const r=await fetch(url,opts);if(!r.ok)throw new Error(await r.text());return r.json()}
function metric(n,v){return `<div class="metric"><span class="muted">${n}</span><strong>${v}</strong></div>`}
async function refresh(){const [s,p,e,seams]=await Promise.all([req('/runtime/status'),req('/projection'),req('/events?limit=40'),req('/open-seams')]);document.getElementById('status').innerHTML=metric('running',s.running)+metric('cycles',s.cycle_count)+metric('LLM mode',s.llm_mode)+metric('Turing assumed',s.turing_complete_assumed);document.getElementById('projection').textContent=JSON.stringify(p,null,2);document.getElementById('seams').innerHTML=seams.slice(-20).map(x=>`<div class="badge OPEN">OPEN</div><div class="muted">${x.reason}</div>`).join('');document.getElementById('events').innerHTML=e.map(x=>`<tr><td>${x.seq}</td><td>${x.event_type}</td><td>${x.entity_type}:${x.entity_id}</td><td>${x.created_at}</td></tr>`).join('')}
async function ingest(){const text=document.getElementById('note').value;if(!text.trim())return;const r=await req('/occurrences',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({exact_text:text,source_id:'dashboard'})});document.getElementById('ingestResult').textContent=`Stored immutable occurrence ${r.id}`;document.getElementById('note').value='';await req('/runtime/cycle',{method:'POST'});refresh()}
async function cycle(){await req('/runtime/cycle',{method:'POST'});refresh()}async function start(){await req('/runtime/start',{method:'POST'});refresh()}async function stop(){await req('/runtime/stop',{method:'POST'});refresh()}
setInterval(refresh,3000);refresh();
</script></body></html>'''
