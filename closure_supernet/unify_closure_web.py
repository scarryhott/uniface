from __future__ import annotations


UNIFY_CLOSURE_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>One closure · Supernet</title>
<style>
body{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;max-width:980px;margin:0 auto;padding:32px;background:#0b0d10;color:#e8edf2;line-height:1.55}
h1{font-size:2rem}section{border:1px solid #39424e;padding:20px;margin:18px 0;border-radius:12px;background:#11151a}code,pre{background:#080a0c;padding:2px 6px;border-radius:5px}pre{overflow:auto;padding:16px}.open{color:#ffd166}.muted{color:#9ba8b5}a{color:#8ecae6}</style>
</head>
<body>
<h1>One closure, once</h1>
<p>NRRF802 is the deterministic-return interface to the existing generative completion engine. It does not create another closure runtime.</p>
<section>
<h2>Closure step</h2>
<pre>carrier X
step : X → X
cl step : X → Closure step
x ~ step(x)

invariant reading → unique lift through cl</pre>
</section>
<section>
<h2>Functorial and unique</h2>
<p>A map intertwining returns induces a closure map. A proposed external closure presentation is accepted exactly when its fibres are the generated closure classes; then the commuting isomorphism is unique.</p>
</section>
<section>
<h2>Prior forms are instances</h2>
<pre>hair(ballStep)       cardinality 1
hand(ballReturn)     cardinality 2
phase(selfLimit)     cardinality 4
Closure₂(ballReturn,hairReturn) cardinality 1</pre>
</section>
<section>
<h2>Runtime</h2>
<p><code>POST /network/completion/closures</code></p>
<p><code>POST /network/completion/closures/two-return</code></p>
<p><code>POST /network/completion/closures/maps</code></p>
<p><code>POST /network/completion/closures/presentations</code></p>
<p><code>GET /network/completion/closure-instances</code></p>
<p><code>GET /network/completion/unified-field</code></p>
</section>
<p class="open">Determination remains OPEN. No canonical representative and no automatic truth verdict are selected.</p>
<p class="muted">The general theorems remain in Lean; this page exposes finite executable receipts.</p>
</body>
</html>'''
