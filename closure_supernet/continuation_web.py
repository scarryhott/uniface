from __future__ import annotations


CONTINUATION_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rule · Geometry · Continuation · Supernet</title>
<style>
body{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;max-width:980px;margin:0 auto;padding:32px;background:#0b0d10;color:#e8edf2;line-height:1.55}h1{font-size:2rem}section{border:1px solid #39424e;padding:20px;margin:18px 0;border-radius:12px;background:#11151a}code,pre{background:#080a0c;padding:2px 6px;border-radius:5px}pre{overflow:auto;padding:16px}.open{color:#ffd166}.muted{color:#9ba8b5}a{color:#8ecae6}</style>
</head>
<body>
<h1>Rule and geometry are two lenses of one continuation</h1>
<section>
<h2>One supplied translation</h2>
<pre>continuation(x,n) = step^[n](x)

RuleRel(x,y)  ⇔  ∃ n, y = continuation(x,n)
GeomRel(x,y)  ⇔  cl(step,x) = cl(step,y)
              ⇔  ∃ m n, continuation(x,m) = continuation(y,n)</pre>
</section>
<section>
<h2>Non-collapse boundary</h2>
<pre>RuleRel ⊆ GeomRel
GeomRel = EqvGen RuleRel
RuleRel = GeomRel exactly when RuleRel is symmetric</pre>
<p>Geometry can preserve a shared fold without inventing a missing directed path, causal history, authorship, or consent receipt.</p>
</section>
<section>
<h2>Turing Being integration</h2>
<p>A Turing Being life event may generate this lens only after its action–reaction return has completed translational truth. Returned global hair 0+ is read as the next stage of the same continuation, not as a second independent loop.</p>
</section>
<section>
<h2>API</h2>
<p><code>POST /network/continuations/systems</code></p>
<p><code>POST /network/turing-being/life-events/{id}/continuation</code></p>
<p><code>GET /network/continuations/systems/{id}/continuation</code></p>
<p><code>GET /network/continuations/systems/{id}/rule</code></p>
<p><code>GET /network/continuations/systems/{id}/geometry</code></p>
<p><code>POST /network/continuations/maps</code></p>
<p><code>GET /network/continuations/field</code></p>
</section>
<p class="open">Every determination remains OPEN. The supplied step is not itself selected or physically validated by NRRF807.</p>
<p class="muted">Finite runtime charts retain exact witnesses; the free line and shift-by-π examples remain theorem-level symbolic cases.</p>
</body>
</html>'''
