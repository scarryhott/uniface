from __future__ import annotations

REOPENING_NETWORK_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Closure Supernet · Iterated Reopening</title>
<style>
:root{--bg:#070a10;--panel:#141a27;--line:#35425c;--text:#eef3fa;--muted:#aab6c8;--open:#e8bf58;--true:#58d493}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#1a2746,var(--bg) 44%);color:var(--text);font-family:Inter,system-ui,sans-serif}header,main{padding:24px clamp(15px,5vw,66px)}header{border-bottom:1px solid var(--line)}h1{margin:0 0 8px;font-size:clamp(32px,5vw,58px)}.muted{color:var(--muted);line-height:1.55}.eq,.panel{background:rgba(20,26,39,.97);border:1px solid var(--line);border-radius:15px;padding:16px}.eq{font-family:ui-monospace,monospace;margin-top:16px}.grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:16px}.c4{grid-column:span 4}.c8{grid-column:span 8}.c12{grid-column:span 12}@media(max-width:900px){.c4,.c8,.c12{grid-column:1/-1}}.metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.metric{padding:10px;background:#1b2435;border-radius:10px}.metric strong{display:block;font-size:22px}pre{white-space:pre-wrap;max-height:560px;overflow:auto;background:#0c111b;padding:12px;border-radius:10px}.OPEN{color:var(--open)}.TRUE{color:var(--true)}a{color:#a8b9ff}</style>
</head>
<body>
<header><h1>Iterated Reopening Field</h1><p class="muted">Admissible reopening families, dependency-sensitive readings, decreasing closed residues and moral connection on the shared residue. A finite stabilization is never presented as a final moral core.</p><div class="eq">ordered assumptions → reopening family → remainingStar → next assumptions → further reopening</div></header>
<main><div class="grid">
<section class="panel c12"><h2>Current field</h2><div id="metrics" class="metrics"></div><p class="muted">Plurality outside the residue remains visible. Meaning-changing reorders remain OPEN.</p></section>
<section class="panel c8"><h2>Processes and residue rounds</h2><pre id="processes"></pre></section>
<section class="panel c4"><h2>Order effects</h2><pre id="orders"></pre></section>
<section class="panel c8"><h2>Reopening families</h2><pre id="families"></pre></section>
<section class="panel c4"><h2>Moral connection</h2><pre id="connections"></pre></section>
<section class="panel c12"><a href="/">Living field</a> · <a href="/runtime">Runtime</a> · <a href="/docs">API</a></section>
</div></main>
<script>
async function refresh(){const r=await fetch('/network/reopening/field');const p=await r.json();const s=p.stats||{};document.getElementById('metrics').innerHTML=['families','rounds','active_processes','meaning_changing_reorders','moral_connections','connections_on_residue'].map(k=>`<div class="metric"><span class="muted">${k.replaceAll('_',' ')}</span><strong>${s[k]??0}</strong></div>`).join('');document.getElementById('processes').textContent=JSON.stringify({processes:p.processes,rounds:p.rounds},null,2);document.getElementById('orders').textContent=JSON.stringify(p.order_assessments,null,2);document.getElementById('families').textContent=JSON.stringify(p.families,null,2);document.getElementById('connections').textContent=JSON.stringify(p.moral_connections,null,2)}
setInterval(refresh,4000);refresh();
</script></body></html>'''
