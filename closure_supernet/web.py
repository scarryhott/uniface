from __future__ import annotations

DASHBOARD_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Closure Supernet Runtime</title>
<style>
:root{--bg:#080b11;--panel:#151b29;--line:#394660;--text:#edf2f9;--muted:#aab6c8;--accent:#a2b6ff;--true:#59d494;--open:#e7bd55;--false:#ff747d}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#192441,var(--bg) 45%);color:var(--text);font-family:Inter,system-ui,sans-serif}header,main{padding:24px clamp(16px,5vw,64px)}header{border-bottom:1px solid var(--line)}h1{margin:0 0 8px;font-size:clamp(30px,5vw,56px)}h2{margin-top:0}.sub{color:var(--muted);max-width:1050px;line-height:1.55}.eq,.panel{background:rgba(21,27,41,.95);border:1px solid var(--line);border-radius:15px;padding:16px}.eq{font-family:ui-monospace,monospace;margin-top:16px}.grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:16px}.c4{grid-column:span 4}.c6{grid-column:span 6}.c8{grid-column:span 8}.c12{grid-column:span 12}@media(max-width:900px){.c4,.c6,.c8,.c12{grid-column:1/-1}}button,textarea{width:100%;background:#1d2536;color:var(--text);border:1px solid var(--line);border-radius:10px;padding:10px}button{cursor:pointer;margin-top:8px}.metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.metric{background:#1d2536;padding:10px;border-radius:10px}.metric strong{display:block;font-size:20px}.muted{color:var(--muted)}pre{white-space:pre-wrap;max-height:430px;overflow:auto;background:#0d121d;padding:12px;border-radius:10px}table{width:100%;border-collapse:collapse;font-size:12px}th,td{padding:8px;border-bottom:1px solid #303a50;text-align:left;vertical-align:top}.scroll{overflow:auto;max-height:390px}.badge{display:inline-block;padding:6px 9px;border-radius:999px;margin:3px;font-weight:700}.TRUE{color:var(--true)}.OPEN{color:var(--open)}.FALSE,.ERROR{color:var(--false)}
</style>
</head>
<body>
<header><h1>Closure Supernet Runtime</h1><div class="sub">Autonomous sensing, configured interpretation, constitutional admission, source-neutral digital integrations, Black Mirror projection, and continuous reopening. In the source notes, <strong>0 and ∞ are reciprocal poles</strong>; they are not renamed as the axiometry itself.</div><div class="eq">source note ↔ digital source ↔ understanding ↔ interpretation ↔ admission ↔ provisional return ↔ reopening</div></header>
<main><div class="grid">
<section class="panel c4"><h2>Runtime</h2><div id="status" class="metrics"></div><button onclick="cycle()">Run one cycle</button><button onclick="start()">Start autonomy</button><button onclick="stop()">Stop autonomy</button></section>
<section class="panel c8"><h2>Ingest exact occurrence</h2><textarea id="note" rows="8" placeholder="Paste exact notes here; original text will be immutable."></textarea><button onclick="ingest()">Ingest and reopen</button><div id="ingestResult" class="muted"></div></section>
<section class="panel c8"><h2>Black Mirror projection</h2><pre id="projection"></pre></section>
<section class="panel c4"><h2>Open seams</h2><div id="seams"></div></section>
<section class="panel c6"><h2>Digital integrations</h2><div class="scroll"><table><thead><tr><th>name</th><th>kind</th><th>state</th><th>cursor/error</th></tr></thead><tbody id="integrations"></tbody></table></div></section>
<section class="panel c6"><h2>Integration runs</h2><div class="scroll"><table><thead><tr><th>status</th><th>direction</th><th>pull/push</th><th>message</th></tr></thead><tbody id="integrationRuns"></tbody></table></div></section>
<section class="panel c12"><h2>Recent events</h2><div class="scroll"><table><thead><tr><th>seq</th><th>event</th><th>entity</th><th>time</th></tr></thead><tbody id="events"></tbody></table></div></section>
</div></main>
<script>
async function req(url,opts){const r=await fetch(url,opts);if(!r.ok)throw new Error(await r.text());return r.json()}
function metric(n,v){return `<div class="metric"><span class="muted">${n}</span><strong>${v}</strong></div>`}
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function refresh(){
 const [s,p,e,seams,integrations,runs]=await Promise.all([
  req('/runtime/status'),req('/projection'),req('/events?limit=40'),req('/open-seams'),req('/integrations'),req('/integrations/runs?limit=30')
 ]);
 document.getElementById('status').innerHTML=metric('running',s.running)+metric('cycles',s.cycle_count)+metric('integrations',s.enabled_integrations)+metric('integration errors',s.integration_errors)+metric('LLM mode',s.llm_mode)+metric('Turing assumed',s.turing_complete_assumed);
 document.getElementById('projection').textContent=JSON.stringify(p,null,2);
 document.getElementById('seams').innerHTML=seams.slice(-20).map(x=>`<div class="badge OPEN">OPEN</div><div class="muted">${esc(x.reason)}</div>`).join('');
 document.getElementById('events').innerHTML=e.map(x=>`<tr><td>${x.seq}</td><td>${esc(x.event_type)}</td><td>${esc(x.entity_type)}:${esc(x.entity_id)}</td><td>${esc(x.created_at)}</td></tr>`).join('');
 document.getElementById('integrations').innerHTML=integrations.map(x=>`<tr><td>${esc(x.name)}</td><td>${esc(x.kind)}</td><td>${x.enabled?'enabled':'disabled'}</td><td>${x.last_error?'<span class="ERROR">'+esc(x.last_error)+'</span>':esc(JSON.stringify(x.cursor))}</td></tr>`).join('');
 document.getElementById('integrationRuns').innerHTML=runs.map(x=>`<tr><td class="${esc(x.status)}">${esc(x.status)}</td><td>${esc(x.direction)}</td><td>${x.pulled}/${x.pushed}</td><td>${esc(x.message)}</td></tr>`).join('');
}
async function ingest(){const text=document.getElementById('note').value;if(!text.trim())return;const r=await req('/occurrences',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({exact_text:text,source_id:'dashboard'})});document.getElementById('ingestResult').textContent=`Stored immutable occurrence ${r.id}`;document.getElementById('note').value='';await req('/runtime/cycle',{method:'POST'});refresh()}
async function cycle(){await req('/runtime/cycle',{method:'POST'});refresh()}async function start(){await req('/runtime/start',{method:'POST'});refresh()}async function stop(){await req('/runtime/stop',{method:'POST'});refresh()}
setInterval(refresh,3000);refresh();
</script></body></html>'''
