CONSTRUCTIVE_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NRRF783 Constructive Closure — Closure Supernet</title>
<style>
:root{color-scheme:dark;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;--bg:#080b11;--panel:#111827;--line:#334155;--text:#eef4fb;--muted:#94a3b8;--open:#eabf64;--ok:#63d89c;--accent:#a9b9ff}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#1b2641,var(--bg) 46%);color:var(--text)}header{padding:28px clamp(18px,5vw,64px);border-bottom:1px solid var(--line)}h1{margin:0 0 8px;font-size:clamp(28px,5vw,52px)}h2{margin-top:0}.sub{max-width:1000px;color:var(--muted);line-height:1.55}.eq,.code{background:#0b1220;border:1px solid var(--line);border-radius:12px;padding:12px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;overflow:auto}main{padding:20px clamp(18px,5vw,64px) 60px}.grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:16px}.c12{grid-column:span 12}@media(max-width:920px){.c12{grid-column:1/-1}}.panel{background:rgba(17,24,39,.96);border:1px solid var(--line);border-radius:16px;padding:16px}.muted{color:var(--muted);line-height:1.5}.row{display:grid;grid-template-columns:1fr 1fr;gap:9px}@media(max-width:650px){.row{grid-template-columns:1fr}}label{display:block;color:var(--muted);font-size:12px;margin:8px 0 5px}input,textarea,button{width:100%;padding:9px;border-radius:9px;border:1px solid var(--line);background:#0b1220;color:var(--text)}textarea{min-height:88px;resize:vertical}button{cursor:pointer;font-weight:800;margin-top:10px}.primary{background:#e7eef7;color:#071019}.badges{display:flex;gap:7px;flex-wrap:wrap}.badge{border:1px solid var(--line);border-radius:999px;padding:6px 9px;font-size:12px}.ok{color:var(--ok);border-color:#39765d}.open{color:var(--open);border-color:#806934}.cards{display:grid;gap:10px}.card{background:#0b1220;border:1px solid var(--line);border-radius:12px;padding:12px}.card h3{margin:0 0 7px}.kv{display:grid;grid-template-columns:150px 1fr;gap:5px 8px;font-size:12px}.kv dt{color:var(--muted)}.kv dd{margin:0;overflow-wrap:anywhere}.actions{display:flex;gap:8px;flex-wrap:wrap}.actions a{color:var(--accent)}.state{white-space:pre-wrap;max-height:360px;overflow:auto}.notice{border-left:4px solid var(--accent);padding:10px 13px;background:#172034;border-radius:0 10px 10px 0}
</style>
</head>
<body>
<header>
<h1>NRRF783 constructive unification</h1>
<div class="sub">The form carries its section as data. U1 is checked directly, U2 is derived through the hold, and U3 is read as emptiness of the explicit defect. Translational closure uses a supplied base site and finite group witnesses. The runtime does not choose a section, decide a global equal/disjoint dichotomy, or issue TRUE from determination.</div>
<div class="eq" style="margin-top:14px">relation explicit → witness carried → form determined → translation continued</div>
</header>
<main><div class="grid">
<section class="panel c12">
<div class="badges">
<span class="badge ok">section carried as data</span>
<span class="badge ok">Classical.choice required: false</span>
<span class="badge ok">excluded middle required: false</span>
<span class="badge open">runtime is the proof: false</span>
<span class="badge open">TRUE issued by determination: false</span>
</div>
<p class="notice">The Lean modules prove the constructive theorems. This page is the executable finite witness chart inside the one Supernet integrator.</p>
<div class="actions"><a href="/supernet">Supernet</a><a href="/renormalization">NRRF781</a><a href="/trading">NRRF780</a><a href="/docs">API</a></div>
</section>

<section class="panel c12" style="grid-column:span 6">
<h2>Explicit axiometric form</h2>
<form id="formCreate">
<label>Name</label><input id="formName" value="constructive closure form">
<div class="row"><div><label>Source carrier (comma)</label><input id="sourceCarrier" value="a,b"></div><div><label>Presentation carrier (comma)</label><input id="presentationCarrier" value="A,B,ghost"></div></div>
<label>encode JSON</label><textarea id="encode">{"a":"A","b":"B"}</textarea>
<label>evaluate JSON</label><textarea id="evaluate">{"A":"a","B":"b","ghost":"a"}</textarea>
<label>Author</label><input id="formAuthor" value="participant">
<button class="primary" type="submit">Integrate form</button>
</form>
</section>

<section class="panel c12" style="grid-column:span 6">
<h2>Form from idempotent translation</h2>
<form id="idemCreate">
<label>Name</label><input id="idemName" value="idempotent hold form">
<label>Carrier (comma)</label><input id="idemCarrier" value="x,y">
<label>Translation JSON</label><textarea id="idemMap">{"x":"x","y":"x"}</textarea>
<label>Author</label><input id="idemAuthor" value="participant">
<button class="primary" type="submit">Construct form</button>
</form>
</section>

<section class="panel c12">
<h2>Constructive translational closure</h2>
<p class="muted">The example is ℤ₂. The base site is supplied as data; it is not extracted by runtime choice.</p>
<form id="translationCreate">
<div class="row"><div><label>Name</label><input id="closureName" value="Z2 relative closure"></div><div><label>Author</label><input id="closureAuthor" value="participant"></div></div>
<label>Group JSON</label><textarea id="groupJson">{"name":"Z2","elements":["0","1"],"zero":"0","addition":{"0":{"0":"0","1":"1"},"1":{"0":"1","1":"0"}},"inverse":{"0":"0","1":"1"}}</textarea>
<div class="row"><div><label>Sites (comma)</label><input id="sites" value="p,q"></div><div><label>Base site</label><input id="baseSite" value="p"></div></div>
<label>Levels JSON</label><textarea id="levels">{"p":"0","q":"1"}</textarea>
<button class="primary" type="submit">Integrate translational closure</button>
</form>
</section>

<section class="panel c12">
<h2>Live constructive field</h2>
<div id="stats" class="badges"></div>
<div id="forms" class="cards" style="margin-top:12px"></div>
<div id="translations" class="cards" style="margin-top:12px"></div>
</section>

<section class="panel c12">
<h2>Last receipt</h2>
<pre id="result" class="code state">No constructive event submitted yet.</pre>
</section>
</div></main>
<script>
const $=id=>document.getElementById(id);
const csv=value=>value.split(",").map(x=>x.trim()).filter(Boolean);
const show=value=>{$("result").textContent=JSON.stringify(value,null,2)};
async function request(url,options={}){
  const response=await fetch(url,{headers:{"Content-Type":"application/json"},...options});
  const data=await response.json().catch(()=>({detail:response.statusText}));
  if(!response.ok) throw new Error(data.detail||response.statusText);
  return data;
}
async function refresh(){
  const field=await request("/network/constructive/field");
  $("stats").innerHTML=Object.entries(field.stats).map(([k,v])=>`<span class="badge">${k}: ${v}</span>`).join("");
  $("forms").innerHTML=field.forms.map(item=>`<div class="card"><h3>${item.name}</h3><div class="kv"><dt>origin</dt><dd>${item.origin}</dd><dt>U1</dt><dd>${item.evaluation.u1_return}</dd><dt>U2</dt><dd>${item.evaluation.u2_hold_idempotent}</dd><dt>U3</dt><dd>${item.evaluation.u3_closes}</dd><dt>defect</dt><dd>${JSON.stringify(item.evaluation.defect)}</dd><dt>choice required</dt><dd>${item.evaluation.classical_choice_required}</dd></div></div>`).join("")||'<p class="muted">No forms yet.</p>';
  $("translations").innerHTML=field.translations.map(item=>`<div class="card"><h3>${item.name}</h3><div class="kv"><dt>base site</dt><dd>${item.base_site}</dd><dt>levels</dt><dd>${JSON.stringify(item.levels)}</dd><dt>relative potential</dt><dd>${JSON.stringify(item.evaluation.relative_potential)}</dd><dt>closure form</dt><dd>${item.evaluation.closure_form_id}</dd><dt>absolute level</dt><dd>${item.evaluation.canonical_absolute_level}</dd></div></div>`).join("")||'<p class="muted">No translational closures yet.</p>';
}
$("formCreate").addEventListener("submit",async event=>{
  event.preventDefault();
  try{
    const data=await request("/network/constructive/forms",{method:"POST",body:JSON.stringify({
      name:$("formName").value,authored_by:$("formAuthor").value,
      source_carrier:csv($("sourceCarrier").value),
      presentation_carrier:csv($("presentationCarrier").value),
      encode:JSON.parse($("encode").value),evaluate:JSON.parse($("evaluate").value)
    })}); show(data); await refresh();
  }catch(error){show({error:String(error)})}
});
$("idemCreate").addEventListener("submit",async event=>{
  event.preventDefault();
  try{
    const data=await request("/network/constructive/forms/from-idempotent",{method:"POST",body:JSON.stringify({
      name:$("idemName").value,authored_by:$("idemAuthor").value,
      carrier:csv($("idemCarrier").value),translation:JSON.parse($("idemMap").value)
    })}); show(data); await refresh();
  }catch(error){show({error:String(error)})}
});
$("translationCreate").addEventListener("submit",async event=>{
  event.preventDefault();
  try{
    const data=await request("/network/constructive/translations",{method:"POST",body:JSON.stringify({
      name:$("closureName").value,authored_by:$("closureAuthor").value,
      group:JSON.parse($("groupJson").value),sites:csv($("sites").value),
      base_site:$("baseSite").value,levels:JSON.parse($("levels").value)
    })}); show(data); await refresh();
  }catch(error){show({error:String(error)})}
});
refresh().catch(error=>show({error:String(error)}));
</script>
</body></html>"""
