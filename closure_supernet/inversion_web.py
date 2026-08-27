from __future__ import annotations


INVERSION_HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Representation-Free Self-Limit · Closure Supernet</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    body { margin: 0; background: #080b10; color: #ecf2f8; }
    main { max-width: 1080px; margin: auto; padding: 28px 20px 70px; }
    h1 { font-size: clamp(2rem, 5vw, 4.5rem); line-height: .95; margin: 12px 0; }
    h2 { margin-top: 0; }
    .eyebrow { letter-spacing: .16em; text-transform: uppercase; color: #8fb8ff; font-size: .76rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(280px,1fr)); gap: 16px; }
    .card { background: #101722; border: 1px solid #243246; border-radius: 16px; padding: 18px; }
    textarea, input, button { box-sizing: border-box; width: 100%; border-radius: 10px; border: 1px solid #31445f; background: #0b111a; color: #ecf2f8; padding: 11px; }
    textarea { min-height: 150px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
    button { background: #dbe8ff; color: #08101c; font-weight: 750; cursor: pointer; margin-top: 10px; }
    code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #070b11; border-radius: 10px; padding: 12px; }
    .pill { display: inline-block; border: 1px solid #36506f; border-radius: 999px; padding: 5px 9px; margin: 3px; font-size: .75rem; }
    .open { color: #ffd78b; }
    .muted { color: #9eb0c4; }
    a { color: #a9c8ff; }
  </style>
</head>
<body>
<main>
  <div class="eyebrow">Closure Supernet · NRRF795/796</div>
  <h1>One inversion.<br/>One hair.<br/>One self-limit.</h1>
  <p class="muted">The matrix itself is retained as source. The runtime derives −Aᵀ, scale, normalized hair, neutral shear, and an exact Frobenius-squared sector receipt. No representation is selected and no physical claim or TRUE verdict is issued.</p>
  <div>
    <span class="pill">return = −transpose</span>
    <span class="pill">scale = trace</span>
    <span class="pill">hair = inverse axial skew</span>
    <span class="pill">neutral = symmetric traceless</span>
    <span class="pill open">physical realization OPEN</span>
  </div>

  <div class="grid" style="margin-top:22px">
    <section class="card">
      <h2>Integrate a local relation</h2>
      <label>Name<input id="name" value="local closure relation" /></label>
      <label>Author<input id="author" value="participant" /></label>
      <label>3×3 matrix JSON<textarea id="matrix">[[2,-3,0],[1,4,-5],[6,2,-1]]</textarea></label>
      <button id="submit">Derive and integrate</button>
      <pre id="result">No relation submitted.</pre>
    </section>

    <section class="card">
      <h2>Current field</h2>
      <p class="muted">Every result is a lens of the same append-only Supernet field.</p>
      <button id="refresh">Refresh</button>
      <pre id="field">Loading…</pre>
    </section>
  </div>

  <section class="card" style="margin-top:16px">
    <h2>Scoped one-hair constructions</h2>
    <p>Entanglement is an axial order defect; superposition is hair linearity; the singularity chart distinguishes the finite tangent ratio from the seam field; the demon endpoint checks one submitted neutral no-gain witness. These names remain definition-scoped.</p>
    <p><a href="/docs">API documentation</a> · <a href="/supernet/project?lens=inversion">Inversion lens JSON</a> · <a href="/">Unified Supernet</a></p>
  </section>
</main>
<script>
const result = document.querySelector('#result');
const field = document.querySelector('#field');
async function refresh() {
  const response = await fetch('/network/inversion/field');
  const body = await response.json();
  field.textContent = JSON.stringify({stats: body.stats, recent: body.relations.slice(0,3)}, null, 2);
}
document.querySelector('#refresh').onclick = refresh;
document.querySelector('#submit').onclick = async () => {
  try {
    const payload = {
      name: document.querySelector('#name').value,
      authored_by: document.querySelector('#author').value,
      matrix: JSON.parse(document.querySelector('#matrix').value)
    };
    const response = await fetch('/network/inversion/relations', {
      method: 'POST', headers: {'content-type':'application/json'}, body: JSON.stringify(payload)
    });
    const body = await response.json();
    if (!response.ok) throw new Error(JSON.stringify(body));
    result.textContent = JSON.stringify({
      id: body.id,
      return_inversion: body.evaluation.return_inversion,
      divergence: body.evaluation.divergence,
      normalized_hair: body.evaluation.normalized_hair,
      neutral_part: body.evaluation.neutral_part,
      self_limit_exact: body.evaluation.self_limit_exact,
      representation_required: body.evaluation.representation_required,
      truth_issued: body.evaluation.truth_issued
    }, null, 2);
    refresh();
  } catch (error) { result.textContent = String(error); }
};
refresh();
</script>
</body>
</html>'''
