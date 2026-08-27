from __future__ import annotations


SELECTION_HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>NRRF790 Selection Audit</title>
  <style>
    :root { color-scheme: dark; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
    body { margin: 0; background: #090b10; color: #edf1f7; }
    main { max-width: 1040px; margin: 0 auto; padding: 28px 18px 80px; }
    h1 { font-size: clamp(1.7rem, 4vw, 3.1rem); margin-bottom: .35rem; }
    p { line-height: 1.55; color: #b8c1ce; }
    .law { border: 1px solid #303846; border-radius: 16px; padding: 16px; background: #11151d; margin: 18px 0; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(210px,1fr)); gap: 12px; }
    .card { border: 1px solid #303846; border-radius: 12px; padding: 14px; background: #10141b; }
    .state { font-weight: 700; }
    .natural { color: #8de5b0; } .forced { color: #ffcb73; }
    .open { color: #8dc8ff; } .empty { color: #ff8f8f; }
    label { display:block; margin: 10px 0 4px; color:#cad2de; }
    input, textarea, button { width:100%; box-sizing:border-box; border-radius:9px; border:1px solid #3a4453; background:#0b0e14; color:#f4f6fa; padding:10px; }
    button { margin-top:12px; cursor:pointer; background:#1c2634; }
    pre { overflow:auto; white-space:pre-wrap; background:#07090d; border-radius:10px; padding:12px; }
  </style>
</head>
<body><main>
  <h1>Complete / Incomplete Selection Audit</h1>
  <p>NRRF790 is live as one selector lens of the continuous Supernet. A complete reading naturally selects its unique admitted symbol. Selecting from a branching reading is recorded as forced isolation, with the removed alternatives, author, scope, and symmetry witness retained.</p>
  <div class="law"><strong>Natural selection never removes an admissible alternative.</strong><br/>Determination remains OPEN and does not issue TRUE.</div>
  <div class="grid">
    <div class="card"><div class="state natural">NATURAL_SELECTION</div><p>Exactly one symbol was already admissible.</p></div>
    <div class="card"><div class="state forced">FORCED_ISOLATION</div><p>An actor selected one while alternatives remained admissible.</p></div>
    <div class="card"><div class="state open">OPEN_BRANCHING</div><p>Several symbols remain; no natural selector exists.</p></div>
    <div class="card"><div class="state empty">EMPTY_TOTAL_ISOLATION</div><p>No symbol is admitted; nothing can be selected.</p></div>
  </div>
  <section class="card" style="margin-top:18px">
    <h2>Create reading</h2>
    <label>Name</label><input id="name" value="selection reading" />
    <label>Field symbols (comma-separated)</label><input id="field" value="point,line,loop" />
    <label>Admissible symbols (comma-separated; blank means empty)</label><input id="admitted" value="point,line" />
    <label>Selected symbol (optional)</label><input id="selected" value="point" />
    <label>Authored by</label><input id="author" value="participant" />
    <button id="submit">Integrate reading</button>
    <pre id="out">No reading submitted.</pre>
  </section>
  <script>
    const csv = id => document.getElementById(id).value.split(',').map(x=>x.trim()).filter(Boolean);
    document.getElementById('submit').onclick = async () => {
      const selected = document.getElementById('selected').value.trim();
      const body = {
        name: document.getElementById('name').value,
        authored_by: document.getElementById('author').value,
        field_symbols: csv('field'),
        admissible_symbols: csv('admitted'),
        selected_symbol: selected || null
      };
      const response = await fetch('/network/selections/readings', {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify(body)});
      document.getElementById('out').textContent = JSON.stringify(await response.json(), null, 2);
    };
  </script>
</main></body></html>'''
