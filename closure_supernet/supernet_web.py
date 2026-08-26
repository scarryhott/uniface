SUPERNET_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Closure Supernet — Continuous Integrator</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:#e9edf2;background:#080b10}
*{box-sizing:border-box} body{margin:0;min-height:100vh;background:radial-gradient(circle at 50% 0,#182334 0,#080b10 45%)}
header{position:sticky;top:0;z-index:3;padding:18px 24px;border-bottom:1px solid #283240;background:#080b10e8;backdrop-filter:blur(16px)}
h1{margin:0;font-size:20px;font-weight:650}.subtitle{margin-top:5px;color:#9eabb9;font-size:13px}
main{display:grid;grid-template-columns:minmax(300px,390px) 1fr;gap:16px;padding:16px;max-width:1600px;margin:auto}
.panel{background:#0f141c;border:1px solid #27303d;border-radius:16px;padding:16px;box-shadow:0 20px 50px #0006}
label{display:block;color:#aeb9c6;font-size:12px;margin:12px 0 5px}input,textarea,select,button{font:inherit}
input,textarea,select{width:100%;padding:10px 11px;border-radius:10px;border:1px solid #303b49;background:#090d13;color:#eef3f8}
textarea{min-height:120px;resize:vertical}button{border:0;border-radius:10px;padding:10px 13px;background:#edf2f7;color:#0a0d12;font-weight:650;cursor:pointer}
button.secondary{background:#1b2430;color:#dce5ee;border:1px solid #334052}.actions{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}
.lenses{display:flex;gap:7px;flex-wrap:wrap;margin:0 0 12px}.lens{font-size:12px;padding:7px 10px}.lens.active{background:#e8eef5;color:#080b10}
.stats{display:grid;grid-template-columns:repeat(4,minmax(90px,1fr));gap:8px;margin-bottom:12px}.stat{padding:10px;border-radius:11px;background:#0a0f16;border:1px solid #252f3b}.stat strong{display:block;font-size:20px}.stat span{font-size:11px;color:#93a1b0}
.stage{font-family:ui-monospace,SFMono-Regular,monospace;font-size:11px;color:#aeb9c6;padding:9px 10px;background:#090d13;border-radius:10px;overflow:auto;margin-bottom:12px}
.events{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}.event{border:1px solid #293440;background:#0b1017;border-radius:13px;padding:12px;min-height:155px}.event h3{margin:0 0 7px;font-size:14px}.meta{font-size:11px;color:#8f9cab;line-height:1.45}.text{font-size:13px;line-height:1.45;white-space:pre-wrap;overflow-wrap:anywhere;margin:9px 0}.badges{display:flex;gap:5px;flex-wrap:wrap}.badge{font-size:10px;padding:3px 6px;border:1px solid #354252;border-radius:999px;color:#bdc8d4}.OPEN{border-color:#816d2c}.TRUE{border-color:#2e7154}.FALSE{border-color:#7a3540}
.notice{font-size:12px;color:#93a1b0;line-height:1.5}.error{color:#ff9da9}.links{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}.links a{color:#a9c9ff;font-size:12px;text-decoration:none}
@media(max-width:850px){main{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<header><h1>Closure Supernet</h1><div class="subtitle">One continuous integrator. Resources, translations, problems, actions, agents, selectors, and hardware are lenses of the same living field.</div></header>
<main>
<section class="panel">
<h2 style="margin-top:0;font-size:16px">Integrate a relative form</h2>
<p class="notice">The exact source is preserved first. Integration relates it to the field, keeps non-rigid structure OPEN, and never issues TRUE merely because a form is determined.</p>
<form id="form">
<label>Exact source</label><textarea id="text" required placeholder="A note, question, problem, proof, resource, sensor return, or form not yet named..."></textarea>
<label>Form label</label><input id="formLabel" value="note" required />
<label>Authored by</label><input id="author" value="participant" required />
<label>Language / frame</label><input id="language" placeholder="optional" />
<label>Relation hints</label><input id="hints" placeholder="comma separated; hints do not self-certify truth" />
<div class="actions"><button type="submit">Integrate</button><button type="button" class="secondary" id="refresh">Refresh field</button></div>
<div id="message" class="notice" style="margin-top:10px"></div>
</form>
<div class="links"><a href="/translation">Translation lens</a><a href="/resources">Resource lens</a><a href="/reopening">Reopening lens</a><a href="/equality">Equality lens</a><a href="/hardware">Hardware lens</a><a href="/runtime">Runtime diagnostics</a><a href="/docs">API</a></div>
</section>
<section class="panel">
<div class="lenses" id="lenses"></div><div class="stats" id="stats"></div><div class="stage" id="stage">No committed field stage yet.</div><div class="events" id="events"></div>
</section>
</main>
<script>
const lenses=['all','source','problem','resource','translation','selector','reopening','action','hardware','equality','agent'];let active='all';const q=s=>document.querySelector(s);
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function renderLenses(){q('#lenses').innerHTML=lenses.map(x=>`<button class="lens secondary ${x===active?'active':''}" data-lens="${x}">${x}</button>`).join('');document.querySelectorAll('.lens').forEach(b=>b.onclick=()=>{active=b.dataset.lens;renderLenses();load()})}
async function load(){const res=await fetch('/supernet/project?lens='+encodeURIComponent(active));const f=await res.json();const s=f.stats||{};q('#stats').innerHTML=[['events',s.all_events??0],['open',s.open_events??0],['determined',s.determined_events??0],['returned',s.returned_events??0]].map(([k,v])=>`<div class="stat"><strong>${v}</strong><span>${k}</span></div>`).join('');const st=f.current_stage;q('#stage').textContent=st?`stage ${st.stage_index} · history ${st.history_signature.slice(0,12)} · limit ${st.limit_signature.slice(0,12)} · ${st.trigger}`:'No committed field stage yet.';q('#events').innerHTML=(f.events||[]).slice().reverse().map(e=>{const occ=(e.exact_source_ids||[])[0];const source=(e.metadata||{}).source_context||(e.metadata||{}).source_id||'';return `<article class="event ${esc(e.current_verdict)}"><h3>${esc(e.form_label)}</h3><div class="badges"><span class="badge">${esc(e.current_stage)}</span><span class="badge">${esc(e.current_verdict)}</span><span class="badge">${esc(e.adapter_label||'source')}</span></div><div class="text">${esc(source||occ||e.id)}</div><div class="meta">by ${esc(e.authored_by)}<br>sources ${(e.exact_source_ids||[]).length} · relations ${(e.relation_hints||[]).length}<br>${esc(e.created_at)}</div></article>`}).join('')||'<p class="notice">No forms in this lens yet.</p>'}
q('#form').onsubmit=async e=>{e.preventDefault();q('#message').textContent='Integrating…';q('#message').className='notice';const body={exact_text:q('#text').value,form_label:q('#formLabel').value,authored_by:q('#author').value,language_label:q('#language').value||null,relation_hints:q('#hints').value.split(',').map(x=>x.trim()).filter(Boolean)};const res=await fetch('/supernet/integrate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const data=await res.json();if(!res.ok){q('#message').textContent=data.detail||'Integration failed';q('#message').className='notice error';return}q('#message').textContent=`Integrated event ${data.event_id}; field stage ${data.field_stage_index}.`;q('#text').value='';await load()};q('#refresh').onclick=load;renderLenses();load();setInterval(load,5000);
</script>
</body></html>"""
