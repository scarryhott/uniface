HARDWARE_CLOSURE_HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Black Mirror Hardware Closure Loop</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    body { margin: 0; background: #080b10; color: #e8edf4; }
    header { padding: 1.2rem 1.5rem; border-bottom: 1px solid #273140; position: sticky; top: 0; background: #080b10ee; backdrop-filter: blur(12px); }
    h1, h2 { margin: .2rem 0 .6rem; }
    main { max-width: 1180px; margin: auto; padding: 1rem; display: grid; gap: 1rem; }
    section { border: 1px solid #273140; border-radius: 14px; padding: 1rem; background: #0f141c; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); gap: .8rem; }
    .card { border: 1px solid #273140; border-radius: 10px; padding: .8rem; background: #0a0e14; overflow-wrap: anywhere; }
    .muted { color: #94a3b8; }
    .safe { color: #7ee787; }
    .open { color: #f2cc60; }
    button { font: inherit; color: inherit; background: #111923; border: 1px solid #344258; border-radius: 8px; padding: .55rem; cursor: pointer; }
    button:hover { border-color: #79c0ff; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #070a0e; border-radius: 8px; padding: .7rem; max-height: 360px; overflow: auto; }
    nav a { color: #79c0ff; margin-right: .8rem; text-decoration: none; }
    .row { display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; }
  </style>
</head>
<body>
<header>
  <h1>Black Mirror Hardware Closure Loop</h1>
  <div class="muted">Network interaction → bounded temporary constraint → deterministic device twin → sensor return → OPEN reintegration</div>
  <nav><a href="/">Living field</a><a href="/translation">Translations</a><a href="/resources">Resources</a><a href="/equality">Equality</a><a href="/production">Production</a></nav>
</header>
<main>
  <section>
    <h2>Safety boundary</h2>
    <div class="grid">
      <div class="card"><b class="safe">Simulation only</b><p>No direct physical, nuclear, quantum, high-energy laser, voltage, cryogenic, magnet, or plasma actuation is enabled.</p></div>
      <div class="card"><b>Temporary selection</b><p>Every proposal is bounded, expires, requires a safe twin run, and needs scoped participant admission plus operator execution.</p></div>
      <div class="card"><b>Physical meaning remains OPEN</b><p>A deterministic twin return becomes new network potential; it is not presented as empirical confirmation.</p></div>
    </div>
  </section>
  <section>
    <div class="row"><h2 style="flex:1">Current hardware field</h2><button onclick="refreshField()">Refresh</button></div>
    <div id="stats" class="grid"></div>
  </section>
  <section><h2>Devices</h2><div id="devices" class="grid"></div></section>
  <section><h2>Temporary constraints</h2><div id="constraints" class="grid"></div></section>
  <section><h2>Sensor returns</h2><div id="returns" class="grid"></div></section>
  <section><h2>Raw source-reversible projection</h2><pre id="raw">Loading…</pre></section>
</main>
<script>
function esc(value) { return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function card(title, body) { return `<div class="card"><b>${esc(title)}</b>${body}</div>`; }
async function refreshField() {
  const response = await fetch('/network/hardware/field', {credentials:'same-origin'});
  const data = await response.json();
  document.getElementById('raw').textContent = JSON.stringify(data, null, 2);
  const stats = data.stats || {};
  document.getElementById('stats').innerHTML = Object.entries(stats).map(([k,v]) => card(k, `<p>${esc(v)}</p>`)).join('');
  document.getElementById('devices').innerHTML = (data.devices || []).map(d => card(d.name, `<p>${esc(d.kind)}</p><p class="muted">${esc(d.id)}</p><p>controls: ${esc((d.control_channels || []).join(', '))}</p>`)).join('') || '<p class="muted">No simulated device registered.</p>';
  document.getElementById('constraints').innerHTML = (data.constraints || []).map(c => card(c.current_state, `<p>${esc(c.id)}</p><p>verdict: <span class="${c.current_verdict === 'TRUE' ? 'safe' : 'open'}">${esc(c.current_verdict)}</span></p><p>controls: ${esc(JSON.stringify(c.control_values))}</p><p>expires: ${esc(c.expires_at)}</p>`)).join('') || '<p class="muted">No temporary constraint proposed.</p>';
  document.getElementById('returns').innerHTML = (data.returns || []).map(r => card(r.reintegration_status, `<p>${esc(r.id)}</p><p>${esc(JSON.stringify(r.sensor_reading))}</p><p class="muted">source: ${esc(r.occurrence_id)}</p>`)).join('') || '<p class="muted">No sensor return yet.</p>';
}
refreshField().catch(error => { document.getElementById('raw').textContent = String(error); });
setInterval(refreshField, 5000);
</script>
</body>
</html>'''
