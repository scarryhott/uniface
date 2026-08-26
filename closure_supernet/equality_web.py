RELATIVE_EQUALITY_HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Closure Supernet — Relative Equality</title>
  <style>
    :root { color-scheme: dark; font-family: ui-sans-serif, system-ui, sans-serif; }
    body { margin: 0; background: #080b10; color: #eef2f7; }
    header { padding: 2rem; border-bottom: 1px solid #253041; }
    main { padding: 1.5rem 2rem 4rem; display: grid; gap: 1rem; }
    nav a { color: #a8d5ff; margin-right: 1rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px,1fr)); gap: .8rem; }
    .card { border: 1px solid #253041; border-radius: 12px; padding: 1rem; background: #0e141d; }
    .open { color: #ffd48a; } .true { color: #9cf2bc; } .false { color: #ff9b9b; }
    code, pre { white-space: pre-wrap; overflow-wrap: anywhere; }
    button { padding: .65rem 1rem; border-radius: 8px; border: 1px solid #456; background:#162232; color:white; }
  </style>
</head>
<body>
<header>
  <h1>Context-indexed relative equality</h1>
  <p>Directed TranslationEvents become equality only through reverse translation, two return-coherence witnesses, and explicit scoped admission.</p>
  <nav><a href="/">Living field</a><a href="/translation">Translations</a><a href="/resources">Resources</a><a href="/reopening">Reopening</a><a href="/runtime">Runtime</a><a href="/docs">API</a></nav>
</header>
<main>
  <section class="card"><button onclick="loadField()">Refresh field</button><span id="status"></span></section>
  <section><h2>Closure relations</h2><div id="relations" class="grid"></div></section>
  <section><h2>Current statistics</h2><div id="stats" class="grid"></div></section>
  <section><h2>Natural-form components</h2><div id="components" class="grid"></div></section>
  <section><h2>Witnesses</h2><div id="witnesses" class="grid"></div></section>
  <section><h2>Source charts</h2><div id="charts" class="grid"></div></section>
</main>
<script>
const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function loadField(){
  const status=document.getElementById('status'); status.textContent=' loading…';
  const response=await fetch('/network/equality/field'); const field=await response.json();
  status.textContent=` generated ${field.stats.contexts} contexts / ${field.stats.witnesses} witnesses`;
  document.getElementById('relations').innerHTML=field.closure_relations.map(x=>`<div class="card"><strong>${esc(x)}</strong></div>`).join('');
  document.getElementById('stats').innerHTML=Object.entries(field.stats).map(([k,v])=>`<div class="card"><small>${esc(k)}</small><h3>${esc(v)}</h3></div>`).join('');
  document.getElementById('components').innerHTML=field.natural_components.map(c=>`<article class="card"><strong>${esc(c.id)}</strong><p>context ${esc(c.context_id)}</p><pre>${esc(c.member_forms.map(f=>`${f.form_type}:${f.form_id}`).join('\n'))}</pre><p>canonical form: none<br>canonical language: none</p></article>`).join('') || '<div class="card">No admitted equality components yet.</div>';
  document.getElementById('witnesses').innerHTML=field.witnesses.map(w=>`<article class="card"><strong>${esc(w.left_form.form_type+':'+w.left_form.form_id)} ↔ ${esc(w.right_form.form_type+':'+w.right_form.form_id)}</strong><p class="${w.current_verdict.toLowerCase()}">${esc(w.current_state)} / ${esc(w.current_verdict)}</p><p>${esc(w.current_reason)}</p><small>reversible ${esc(w.reversible)} · coherent ${esc(w.coherent)} · context ${esc(w.context_id)}</small></article>`).join('') || '<div class="card">No witnesses yet.</div>';
  document.getElementById('charts').innerHTML=field.charts.map(c=>`<article class="card"><strong>${esc(c.name)}</strong><p>${esc(c.generator)} ↔ ${esc(c.inverse_reading)}</p><small>return: ${esc(c.return_form)}<br>reopen: ${esc(c.reopening)}</small></article>`).join('') || '<div class="card">No source charts registered yet.</div>';
}
loadField();
</script>
</body>
</html>'''
