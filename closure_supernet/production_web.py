PRODUCTION_HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Closure Supernet Production</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    body { margin:0; background:#0a0d12; color:#e8edf4; }
    main { max-width:900px; margin:0 auto; padding:48px 24px; }
    section { border:1px solid #273142; border-radius:16px; padding:22px; margin:18px 0; background:#111722; }
    input,button { font:inherit; border-radius:10px; padding:12px; }
    input { width:min(520px,calc(100% - 28px)); border:1px solid #3b4658; background:#090d14; color:#fff; }
    button { border:0; background:#e8edf4; color:#111722; cursor:pointer; margin-right:8px; }
    a { color:#9fc7ff; margin-right:14px; line-height:2; }
    pre { white-space:pre-wrap; overflow-wrap:anywhere; background:#080c12; border-radius:10px; padding:14px; }
    .muted { color:#9ba9bb; }
  </style>
</head>
<body><main>
  <h1>Closure Supernet — production entry</h1>
  <p class="muted">The public network is live interaction. This page establishes an authenticated browser session; it is not the network's truth or ontology.</p>
  <section>
    <h2>Session</h2>
    <input id="key" type="password" autocomplete="current-password" placeholder="Invite or operator API key" />
    <p><button onclick="login()">Sign in</button><button onclick="logout()">Sign out</button></p>
    <pre id="session">Loading…</pre>
  </section>
  <section>
    <h2>Active network surfaces</h2>
    <p>
      <a href="/">Living field</a>
      <a href="/translation">Translations</a>
      <a href="/resources">Resources</a>
      <a href="/reopening">Reopening</a>
      <a href="/equality">Relative equality</a>
      <a href="/runtime">Runtime</a>
      <a href="/docs">API</a>
    </p>
  </section>
  <section><h2>Readiness</h2><pre id="ready">Loading…</pre></section>
<script>
async function refresh(){
  const session = await fetch('/auth/session').then(r=>r.json()).catch(e=>({error:String(e)}));
  const ready = await fetch('/readyz').then(async r=>({status:r.status, body:await r.json()})).catch(e=>({error:String(e)}));
  document.getElementById('session').textContent=JSON.stringify(session,null,2);
  document.getElementById('ready').textContent=JSON.stringify(ready,null,2);
}
async function login(){
  const api_key=document.getElementById('key').value;
  const r=await fetch('/auth/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({api_key})});
  const body=await r.json(); if(!r.ok){alert(body.detail||'Login failed');} document.getElementById('key').value=''; await refresh();
}
async function logout(){ await fetch('/auth/logout',{method:'POST'}); await refresh(); }
refresh();
</script>
</main></body></html>'''
