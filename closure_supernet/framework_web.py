from __future__ import annotations


FRAMEWORK_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Uniface — Natural Translational Truth</title>
<style>
:root{color-scheme:dark;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;--bg:#070a10;--p:#121a28;--p2:#182234;--l:#35445f;--t:#edf4fb;--m:#9eacc0;--a:#9eb7ff;--g:#57d597;--o:#e7bd57}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#1b2947,var(--bg) 45%);color:var(--t)}header,main{max-width:1350px;margin:auto;padding:28px 22px}h1{font-size:clamp(32px,5vw,62px);margin:0 0 10px}.sub{color:var(--m);line-height:1.55;max-width:1050px}.eq,pre,textarea,input,button{background:var(--p);border:1px solid var(--l);border-radius:12px;color:var(--t)}.eq,pre{padding:13px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;overflow:auto}.grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:14px}.c4{grid-column:span 4}.c12{grid-column:span 12}@media(max-width:950px){.c4,.c12{grid-column:1/-1}}.panel{background:rgba(18,26,40,.96);border:1px solid var(--l);border-radius:15px;padding:15px}.panel h2{margin-top:0}textarea{width:100%;min-height:250px;padding:10px;font:11px ui-monospace,SFMono-Regular,Menlo,monospace}button{padding:9px 12px;cursor:pointer;font-weight:750}.row{display:flex;gap:8px;flex-wrap:wrap}.badge{display:inline-block;padding:5px 8px;border:1px solid var(--l);border-radius:999px;margin:3px;font-size:11px}.good{color:var(--g)}.open{color:var(--o)}.muted{color:var(--m)}pre{max-height:520px;white-space:pre-wrap}.tabs a{color:var(--a);margin-right:12px}
</style>
</head>
<body><header>
<h1>Natural translational truth</h1>
<p class="sub"><strong>NRRF784 + NRRF785, one Supernet layer.</strong> Natural selection is fixed under level shifts and factors through form orbits. Classical and contextual frameworks share one partial truth on frame–observable orbits; they differ only by whether that truth admits a global assignment. Resource metrics remain downstream operational overlays.</p>
<div class="eq">explicit witnesses → level orbits → natural selector → orbit truth → classical section or contextual obstruction → return → reopening</div>
<div><span class="badge good">contextual truth retained</span><span class="badge good">resource metric foundational: false</span><span class="badge open">global assignment required for truth: false</span><span class="badge open">TRUE issued: false</span></div>
<p class="tabs"><a href="/">root loop</a><a href="/supernet">Supernet</a><a href="/constructive">NRRF783</a><a href="/field-run.json">field snapshot</a></p>
</header><main><div class="grid">
<section class="panel c4"><h2>NRRF784 arena</h2><p class="muted">Submit a finite level action, selector verdict, and optional resource metric.</p><textarea id="arena"></textarea><button id="sendArena">Integrate arena</button></section>
<section class="panel c4"><h2>NRRF785 framework</h2><p class="muted">Submit frames, observables, partial verdicts, and diagonal level actions.</p><textarea id="framework"></textarea><button id="sendFramework">Integrate framework</button></section>
<section class="panel c4"><h2>Reunification bridge</h2><p class="muted">Map each arena form equivariantly to one frame–observable presentation.</p><textarea id="bridge"></textarea><button id="sendBridge">Integrate bridge</button></section>
<section class="panel c12"><div class="row"><button id="refresh">Refresh field</button></div><h2>Live framework field</h2><pre id="output">loading…</pre></section>
</div></main>
<script>
const z3={name:'Z3',elements:['0','1','2'],zero:'0',addition:{'0':{'0':'0','1':'1','2':'2'},'1':{'0':'1','1':'2','2':'0'},'2':{'0':'2','1':'0','2':'1'}},inverse:{'0':'0','1':'2','2':'1'}};
const arena={name:'one natural orbit',authored_by:'participant',forms:['x0','x1','x2'],group:z3,action:{'0':{x0:'x0',x1:'x1',x2:'x2'},'1':{x0:'x1',x1:'x2',x2:'x0'},'2':{x0:'x2',x1:'x0',x2:'x1'}},selected:{x0:true,x1:true,x2:true},resource_metric:{x0:0,x1:1,x2:2}};
const framework={name:'contextual parity orbit truth',authored_by:'participant',observables:['q0','q1','q2'],frames:['f0','f1','f2'],values:['0','1'],default_value:'0',group:z3,frame_action:{'0':{f0:'f0',f1:'f1',f2:'f2'},'1':{f0:'f1',f1:'f2',f2:'f0'},'2':{f0:'f2',f1:'f0',f2:'f1'}},observable_action:{'0':{q0:'q0',q1:'q1',q2:'q2'},'1':{q0:'q1',q1:'q2',q2:'q0'},'2':{q0:'q2',q1:'q0',q2:'q1'}},verdicts:{f0:{q0:'0',q1:'1',q2:null},f1:{q0:null,q1:'0',q2:'1'},f2:{q0:'1',q1:null,q2:'0'}}};
document.getElementById('arena').value=JSON.stringify(arena,null,2);document.getElementById('framework').value=JSON.stringify(framework,null,2);document.getElementById('bridge').value=JSON.stringify({name:'natural truth bridge',authored_by:'participant',arena_id:'PASTE_ARENA_ID',framework_id:'PASTE_FRAMEWORK_ID',form_to_presentation:{x0:{frame:'f0',observable:'q0'},x1:{frame:'f1',observable:'q1'},x2:{frame:'f2',observable:'q2'}}},null,2);
async function post(path,id){try{const body=JSON.parse(document.getElementById(id).value);const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const j=await r.json();if(!r.ok)throw new Error(JSON.stringify(j));document.getElementById('output').textContent=JSON.stringify(j,null,2)}catch(e){document.getElementById('output').textContent=String(e)}}
async function refresh(){const r=await fetch('/network/frameworks/field',{cache:'no-store'});document.getElementById('output').textContent=JSON.stringify(await r.json(),null,2)}
document.getElementById('sendArena').onclick=()=>post('/network/frameworks/naturality','arena');document.getElementById('sendFramework').onclick=()=>post('/network/frameworks/truth','framework');document.getElementById('sendBridge').onclick=()=>post('/network/frameworks/bridges','bridge');document.getElementById('refresh').onclick=refresh;refresh();
</script></body></html>'''
