from __future__ import annotations


TRANSLATION_FIELD_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Closure Supernet Translation Field</title>
<style>
:root{--bg:#070a10;--panel:#151c2a;--panel2:#1c2638;--line:#34435e;--text:#eef3fb;--muted:#aeb9ca;--accent:#aabaff;--open:#e6bf5f;--true:#5bd49a;--false:#ff7882}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#1b2948,var(--bg) 45%);color:var(--text);font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif}header,main{padding:24px clamp(16px,5vw,70px)}header{border-bottom:1px solid var(--line)}h1{font-size:clamp(34px,5vw,62px);margin:0 0 8px}.sub{max-width:1100px;color:var(--muted);line-height:1.65}.eq,.panel,.card{border:1px solid var(--line);background:rgba(21,28,42,.96);border-radius:16px;padding:16px}.eq{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;margin-top:18px}.top{display:flex;gap:9px;flex-wrap:wrap;margin:0 0 18px}.button,button{border:1px solid var(--line);background:var(--panel2);color:var(--text);padding:9px 14px;border-radius:999px;text-decoration:none;cursor:pointer}.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px}.metric{background:var(--panel2);padding:13px;border-radius:12px}.metric strong{display:block;font-size:24px}.grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:16px}.c4{grid-column:span 4}.c8{grid-column:span 8}.c12{grid-column:span 12}@media(max-width:950px){.c4,.c8,.c12{grid-column:1/-1}}.cards{display:grid;gap:12px}.card{background:var(--panel2)}.badge{display:inline-block;border:1px solid currentColor;border-radius:999px;padding:4px 8px;font-weight:750;margin-right:5px}.OPEN,.PROPOSED,.INTERPRETED{color:var(--open)}.TRUE,.ADMITTED,.RETURNED{color:var(--true)}.FALSE,.REJECTED{color:var(--false)}.REOPENED{color:var(--accent)}.muted{color:var(--muted);line-height:1.5}.small{font-size:12px}.forms{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap}.notice{border-left:4px solid var(--accent);background:var(--panel2);padding:12px 14px;border-radius:0 10px 10px 0}select{background:var(--panel2);color:var(--text);border:1px solid var(--line);border-radius:9px;padding:8px}pre{white-space:pre-wrap;max-height:520px;overflow:auto;background:#0c111b;padding:12px;border-radius:10px}
</style>
</head>
<body>
<header>
<h1>Live Translation Field</h1>
<div class="sub">Closure is shown here as translational truth through interaction. HTTP, WebSocket, repositories, webhooks and database tables carry events; they do not define the field. Every return remains source-reversible and reopenable.</div>
<div class="eq">presentation → interaction → translation → relative admission → return → successor potential → reopening</div>
</header>
<main>
<div class="top"><a class="button" href="/">Living field</a><a class="button" href="/reopening">Iterated reopening</a><a class="button" href="/runtime">Runtime</a><a class="button" href="/docs">API</a><button onclick="reconcile()">Reconcile derived forms now</button><select id="stateFilter" onchange="render()"><option value="">all states</option><option>PROPOSED</option><option>INTERPRETED</option><option>ADMITTED</option><option>RETURNED</option><option>REOPENED</option><option>REJECTED</option></select></div>
<div class="grid">
<section class="panel c12"><h2>Field state</h2><div id="metrics" class="metrics"></div><p class="muted">Counts describe translation activity, not truth by popularity, value by quantity, or terminal completion.</p></section>
<section class="panel c8"><h2>Translations</h2><div class="notice">Candidate relations, notes, solutions, actions, consequences, order effects and residues are displayed as relative forms of Translation Events.</div><div id="translations" class="cards" style="margin-top:12px"></div></section>
<section class="panel c4"><h2>Source-reversible field</h2><pre id="reverseIndex"></pre></section>
<section class="panel c12"><h2>Derived form graph</h2><pre id="edges"></pre></section>
</div>
</main>
<script>
let FIELD={translations:[],stats:{},source_reverse_index:{},edges:[]};
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function req(url,opts){const r=await fetch(url,opts);if(!r.ok)throw new Error(await r.text());return r.json()}
function metric(name,value){return `<div class="metric"><span class="muted">${esc(name)}</span><strong>${esc(value)}</strong></div>`}
function formLabel(f){return `${f.role} ${f.form_type}:${f.form_id}${f.label?` · ${f.label}`:''}`}
function render(){const s=FIELD.stats||{};document.getElementById('metrics').innerHTML=metric('translations',s.translations||0)+metric('OPEN',s.open_translations||0)+metric('returned',s.returned_translations||0)+metric('reopened',s.reopened_translations||0)+metric('protocol is transport',s.protocol_is_transport_only)+metric('terminal closure',s.terminal_closure_available);
 const filter=document.getElementById('stateFilter').value;const items=(FIELD.translations||[]).filter(t=>!filter||t.current_state===filter).slice().reverse();document.getElementById('translations').innerHTML=items.length?items.map(t=>`<article class="card"><span class="badge ${esc(t.current_state)}">${esc(t.current_state)}</span><span class="badge ${esc(t.current_verdict)}">${esc(t.current_verdict)}</span><h3>${esc(t.kind)} · ${esc(t.relation_type)}</h3><div class="forms"><strong>source</strong>\n${esc((t.source_forms||[]).map(formLabel).join('\n'))}\n\n<strong>target / return</strong>\n${esc((t.target_forms||[]).map(formLabel).join('\n'))}</div><p><strong>preserves</strong><br>${esc((t.preserves||[]).join(' · '))}</p><p><strong>transforms</strong><br>${esc((t.transforms||[]).join(' · '))}</p>${(t.untranslated||[]).length?`<p class="OPEN"><strong>untranslated</strong><br>${esc(t.untranslated.join(' · '))}</p>`:''}<p class="muted">${esc(t.frame_and_scope)}<br>${esc(t.admission_scope)}</p><div class="small muted">${esc(t.id)} · ${esc(t.created_at)} · ${esc(t.generated_by)}</div></article>`).join(''):'<p class="muted">No translations match this view.</p>';
 document.getElementById('reverseIndex').textContent=JSON.stringify(FIELD.source_reverse_index||{},null,2);document.getElementById('edges').textContent=JSON.stringify(FIELD.edges||[],null,2)}
async function refresh(){FIELD=await req('/network/translations/field');render()}
async function reconcile(){await req('/network/translations/reconcile',{method:'POST'});await refresh()}
refresh();setInterval(refresh,5000);
</script>
</body></html>'''
