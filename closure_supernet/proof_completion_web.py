from __future__ import annotations


PROOF_COMPLETION_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Proof → Completion → Balance · Supernet</title>
<style>
:root{color-scheme:dark;font-family:Inter,system-ui,sans-serif;--bg:#070a0f;--panel:#101722;--line:#2b3a50;--text:#e9f0f7;--muted:#93a4b7;--open:#d4a84b;--blue:#8ec5ff;--green:#72d5a0}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#15243a,#070a0f 55%);color:var(--text)}main{max-width:1180px;margin:auto;padding:28px}h1{margin:0 0 4px}.sub{color:var(--muted);margin:0 0 24px}.layers{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.layer,.panel{border:1px solid var(--line);border-radius:14px;background:#0c121be8;padding:16px}.layer b{display:block;color:var(--blue);margin-bottom:8px}.arrow{text-align:center;color:var(--muted)}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px}.panel h2{font-size:15px;margin:0 0 12px}label{display:block;font-size:11px;color:var(--muted);margin:9px 0 4px}input,textarea,select,button{font:inherit;color:inherit}input,textarea,select{width:100%;border:1px solid var(--line);border-radius:9px;background:#070b11;padding:9px}textarea{min-height:105px}button{border:1px solid #48617f;border-radius:9px;background:#17263a;padding:8px 11px;cursor:pointer;margin:8px 5px 0 0}button.primary{background:#e8f1fa;color:#07101a;border-color:#e8f1fa}.status{color:var(--open)}pre{white-space:pre-wrap;overflow:auto;max-height:520px;background:#06090e;border:1px solid #202d3e;border-radius:10px;padding:12px;font:11px ui-monospace,SFMono-Regular,monospace}.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{border:1px solid var(--line);border-radius:999px;padding:4px 7px;font-size:10px;color:#b9c8d8}.good{color:var(--green)}@media(max-width:850px){.layers,.grid{grid-template-columns:1fr}.arrow{display:none}}
</style>
</head>
<body><main>
<h1>Completion is proof after meta abstraction</h1>
<p class="sub">NRRF811 · the Black Mirror folds a proof fibre into admission, reciprocal balance, and a closure class without deleting the concrete derivations beneath it.</p>
<div class="layers">
<div class="layer"><b>1 · Proof data</b><code>Deriv r a b</code><p>Length, ordered trace, admitted edges, source lineage.</p></div>
<div class="layer"><b>2 · Completion</b><code>Admits r a b</code><p>The proposition that at least one derivation exists.</p></div>
<div class="layer"><b>3 · Relative balance</b><code>Admits a b ∧ Admits b a</code><p>Mutual proof, with both directions retained.</p></div>
<div class="layer"><b>4 · Meta abstraction</b><code>X / Balance</code><p>Visible closure class; proof fibre remains reopenable.</p></div>
</div>
<div class="grid">
<section class="panel"><h2>Create an admitted relation</h2>
<label>Name</label><input id="name" value="branching proof field">
<label>Presentations (comma separated)</label><input id="presentations" value="a,b,c,d">
<label>Admitted steps JSON</label><textarea id="steps">[{"source":"a","target":"b","label":"a→b"},{"source":"b","target":"d","label":"b→d"},{"source":"a","target":"c","label":"a→c"},{"source":"c","target":"d","label":"c→d"}]</textarea>
<button class="primary" id="create">Integrate proof field</button><button id="refresh">Refresh</button>
<p class="status" id="status">OPEN · no canonical proof</p>
<label>Stored proof systems</label><select id="systems"></select>
</section>
<section class="panel"><h2>Open the proof fibre</h2>
<div class="chips"><span class="chip">geometry ≠ proof</span><span class="chip">balance = mutual admission</span><span class="chip">TRUE not issued</span></div>
<label>Source</label><input id="source" value="a"><label>Target</label><input id="target" value="d">
<button id="derive">Read derivation</button><button id="persist">Commit proof receipt</button><button id="balance">Read balance</button>
<label>Admission seeds (comma separated)</label><input id="seeds" value="a"><button id="admit">Close admitted set</button>
<pre id="output">Select or create a system.</pre>
</section></div>
<section class="panel" style="margin-top:14px"><h2>Canonical finite Turing Being / QG reading</h2><p>The finite hand × ball being is shown only under the module’s stated formal scope; it is not an empirical gravitation claim.</p><button id="qg">Load finite QG receipt</button><pre id="qgout"></pre></section>
<script>
const $=id=>document.getElementById(id);let current=null;
async function json(url,options){const r=await fetch(url,options);const text=await r.text();if(!r.ok)throw new Error(text);return text?JSON.parse(text):{} }
function selected(){return $('systems').value||current}
async function refresh(){const items=await json('/network/proofs/systems');$('systems').innerHTML=items.map(x=>`<option value="${x.id}">${x.name}</option>`).join('');if(items.length){current=items[0].id;$('systems').value=current;$('output').textContent=JSON.stringify(items[0].evaluation,null,2)}}
$('create').onclick=async()=>{try{const presentations=$('presentations').value.split(',').map(x=>x.trim()).filter(Boolean);const steps=JSON.parse($('steps').value);const data=await json('/network/proofs/systems',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({name:$('name').value,presentations,steps})});current=data.id;$('status').textContent='RETURNED / OPEN · proof fibre retained';await refresh();$('systems').value=current;$('output').textContent=JSON.stringify(data.evaluation,null,2)}catch(e){$('status').textContent=e}}
$('refresh').onclick=refresh;$('systems').onchange=async()=>{current=selected();$('output').textContent=JSON.stringify(await json(`/network/proofs/systems/${current}`),null,2)};
$('derive').onclick=async()=>{$('output').textContent=JSON.stringify(await json(`/network/proofs/systems/${selected()}/derivation?source=${encodeURIComponent($('source').value)}&target=${encodeURIComponent($('target').value)}`),null,2)};
$('persist').onclick=async()=>{$('output').textContent=JSON.stringify(await json(`/network/proofs/systems/${selected()}/derivations`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({source:$('source').value,target:$('target').value})}),null,2)};
$('balance').onclick=async()=>{$('output').textContent=JSON.stringify(await json(`/network/proofs/systems/${selected()}/balance?left=${encodeURIComponent($('source').value)}&right=${encodeURIComponent($('target').value)}`),null,2)};
$('admit').onclick=async()=>{const seeds=$('seeds').value.split(',').map(x=>x.trim()).filter(Boolean);$('output').textContent=JSON.stringify(await json(`/network/proofs/systems/${selected()}/admissions`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({seeds})}),null,2)};
$('qg').onclick=async()=>{$('qgout').textContent=JSON.stringify(await json('/network/proofs/canonical-qg'),null,2)};
refresh().catch(e=>$('output').textContent=e);
</script></main></body></html>'''
