from __future__ import annotations

"""The published Supernet surface: a closure ball projecting and navigating itself."""


CLOSURE_BALL_SUPERNET_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="color-scheme" content="dark light">
  <title>Supernet closure ball</title>
  <style>
    :root {
      color-scheme: dark;
      --void: #07100f;
      --field: #0b1715;
      --ink: #e7f3ed;
      --muted: #8da59c;
      --line: rgba(210, 240, 226, .22);
      --witness: #9ee8c0;
      --open: #efbe82;
      --focus: #dff9ec;
      --surface: rgba(8, 19, 17, .78);
    }
    * { box-sizing: border-box; }
    html, body { width: 100%; min-height: 100%; margin: 0; }
    body {
      overflow: hidden;
      background:
        radial-gradient(circle at 50% 45%, rgba(69, 122, 99, .14), transparent 48%),
        var(--void);
      color: var(--ink);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    button, textarea, input { font: inherit; color: inherit; }
    #shell {
      position: fixed;
      inset: 0;
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
      isolation: isolate;
    }
    header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: baseline;
      gap: 1rem;
      padding: max(14px, env(safe-area-inset-top)) 18px 10px;
      pointer-events: none;
      z-index: 4;
    }
    #identity {
      min-width: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      letter-spacing: .035em;
      font-size: 12px;
      color: var(--muted);
    }
    #status {
      font-size: 11px;
      letter-spacing: .14em;
      text-transform: uppercase;
    }
    #status[data-open="true"] { color: var(--open); }
    #status[data-open="false"] { color: var(--witness); }
    #field-wrap { position: relative; min-height: 0; }
    #field {
      width: 100%;
      height: 100%;
      display: block;
      touch-action: manipulation;
    }
    .closure-boundary {
      fill: rgba(150, 220, 190, .018);
      stroke: var(--line);
      stroke-width: 1.4;
      vector-effect: non-scaling-stroke;
    }
    .boundary-seam {
      fill: none;
      stroke: var(--open);
      stroke-width: 3;
      stroke-linecap: round;
      stroke-dasharray: 2 11;
      opacity: .72;
      vector-effect: non-scaling-stroke;
    }
    .locality {
      cursor: pointer;
      outline: none;
    }
    .locality-shape {
      fill: rgba(123, 194, 162, .055);
      stroke: rgba(191, 232, 213, .18);
      stroke-width: 1;
      transition: fill .18s ease, stroke .18s ease, opacity .18s ease;
      vector-effect: non-scaling-stroke;
    }
    .locality:hover .locality-shape,
    .locality:focus .locality-shape {
      fill: rgba(123, 194, 162, .12);
      stroke: rgba(215, 247, 232, .55);
    }
    .locality[data-focused="true"] .locality-shape {
      fill: rgba(158, 232, 192, .12);
      stroke: rgba(223, 249, 236, .62);
      stroke-width: 1.7;
    }
    .locality-label {
      fill: var(--ink);
      font-size: 11px;
      text-anchor: middle;
      pointer-events: none;
      opacity: .88;
    }
    .locality-meta {
      fill: var(--muted);
      font-size: 8.5px;
      text-anchor: middle;
      pointer-events: none;
      letter-spacing: .08em;
    }
    .hair-visible {
      fill: none;
      stroke-width: 2.2;
      stroke-linecap: round;
      vector-effect: non-scaling-stroke;
      opacity: .68;
      transition: opacity .15s ease, stroke-width .15s ease;
    }
    .hair-visible.witnessed { stroke: var(--witness); }
    .hair-visible.open {
      stroke: var(--open);
      stroke-dasharray: 7 10;
    }
    .hair-hit {
      fill: none;
      stroke: transparent;
      stroke-width: 24;
      cursor: pointer;
      pointer-events: stroke;
      vector-effect: non-scaling-stroke;
    }
    .hair-group:focus { outline: none; }
    .hair-group:hover .hair-visible,
    .hair-group:focus .hair-visible,
    .hair-group[data-selected="true"] .hair-visible {
      opacity: 1;
      stroke-width: 4;
    }
    .path-mark {
      fill: currentColor;
      opacity: .8;
      pointer-events: none;
    }
    #centre-reading {
      fill: var(--muted);
      font-size: 10px;
      text-anchor: middle;
      letter-spacing: .11em;
      pointer-events: none;
    }
    #reading {
      position: absolute;
      left: 50%;
      bottom: 9px;
      width: min(920px, calc(100% - 32px));
      transform: translateX(-50%);
      margin: 0;
      padding: 10px 12px;
      border-top: 1px solid var(--line);
      background: linear-gradient(180deg, transparent, rgba(7, 16, 15, .72) 28%);
      color: var(--muted);
      font-size: 11px;
      line-height: 1.45;
      white-space: pre-wrap;
      pointer-events: none;
      z-index: 3;
    }
    #hair-control {
      position: absolute;
      top: 12px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 5px 8px;
      color: var(--muted);
      font-size: 9px;
      letter-spacing: .08em;
      text-transform: uppercase;
      background: rgba(7, 16, 15, .48);
      border-radius: 999px;
      z-index: 3;
    }
    #hair-angle { width: min(250px, 42vw); accent-color: var(--witness); }
    #return-flow {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 9px;
      align-items: end;
      padding: 10px 18px max(14px, env(safe-area-inset-bottom));
      background: linear-gradient(180deg, transparent, rgba(7, 16, 15, .95) 22%);
      z-index: 5;
    }
    #return-flow[hidden] { display: none; }
    #return-source {
      width: 100%;
      min-height: 58px;
      max-height: 24vh;
      resize: vertical;
      padding: 9px 10px;
      border: 1px solid rgba(239, 190, 130, .32);
      border-radius: 4px;
      outline: none;
      background: var(--surface);
      line-height: 1.42;
    }
    #return-source:focus { border-color: var(--open); }
    #return-submit {
      min-height: 58px;
      padding: 8px 14px;
      border: 1px solid rgba(239, 190, 130, .42);
      border-radius: 4px;
      background: rgba(239, 190, 130, .09);
      cursor: pointer;
    }
    #return-submit:disabled { opacity: .42; cursor: not-allowed; }
    #fatal {
      position: fixed;
      inset: 0;
      display: grid;
      place-items: center;
      padding: 2rem;
      background: var(--void);
      color: var(--open);
      text-align: center;
      z-index: 10;
    }
    #fatal[hidden] { display: none; }
    @media (max-width: 640px) {
      header { padding-inline: 12px; }
      #return-flow { grid-template-columns: 1fr; padding-inline: 12px; }
      #return-submit { min-height: 42px; }
      #reading { font-size: 9.5px; bottom: 4px; }
      .locality-label { font-size: 9px; }
    }
    @media (prefers-reduced-motion: reduce) {
      * { transition: none !important; }
    }
  </style>
</head>
<body>
  <main id="shell" data-closure-ball-derived="true">
    <header>
      <div id="identity">closure ball</div>
      <div id="status" data-open="true">OPEN</div>
    </header>
    <section id="field-wrap" aria-label="Navigable closure ball">
      <div id="hair-control" hidden>
        <label for="hair-angle">perspective hair</label>
        <input id="hair-angle" type="range" min="-180000" max="180000" value="0" step="1000">
        <output id="hair-angle-value" for="hair-angle">0°</output>
      </div>
      <svg id="field" viewBox="0 0 1000 720" role="application" aria-label="Closure ball perspective flow">
        <g id="ball-layer"></g>
      </svg>
      <output id="reading" aria-live="polite">Deriving the active perspective from closure…</output>
    </section>
    <form id="return-flow" hidden>
      <textarea id="return-source" required maxlength="20000" aria-label="Exact source-preserving return" placeholder="Return a source through the active OPEN seam"></textarea>
      <button id="return-submit" type="submit">return → reclose</button>
    </form>
  </main>
  <div id="fatal" hidden></div>
<script>
(() => {
  "use strict";

  const NS = "http://www.w3.org/2000/svg";
  const EXPECTED_PROTOCOL = "closure.supernet/closure-ball-perspective-flow-v1";
  const state = {
    ball: null,
    contract: null,
    perspectiveId: new URLSearchParams(location.search).get("perspective_id") || "perspective",
    focusEventId: new URLSearchParams(location.search).get("focus_event_id"),
    hairMillidegrees: 0,
    selectedActionId: null,
    selectedEventId: null,
  };

  const field = document.getElementById("field");
  const layer = document.getElementById("ball-layer");
  const identity = document.getElementById("identity");
  const statusNode = document.getElementById("status");
  const reading = document.getElementById("reading");
  const returnFlow = document.getElementById("return-flow");
  const returnSource = document.getElementById("return-source");
  const returnSubmit = document.getElementById("return-submit");
  const hairControl = document.getElementById("hair-control");
  const hairAngle = document.getElementById("hair-angle");
  const hairAngleValue = document.getElementById("hair-angle-value");
  const fatal = document.getElementById("fatal");

  function canonical(value) {
    if (Array.isArray(value)) return value.map(canonical);
    if (value && typeof value === "object") {
      return Object.fromEntries(
        Object.keys(value).sort().map((key) => [key, canonical(value[key])]),
      );
    }
    return value;
  }

  function stable(value) {
    return JSON.stringify(canonical(value));
  }

  async function sha256(value) {
    const bytes = new TextEncoder().encode(value);
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(digest)]
      .map((part) => part.toString(16).padStart(2, "0"))
      .join("");
  }

  async function digest(prefix, value) {
    return `${prefix}:${(await sha256(stable(value))).slice(0, 24)}`;
  }

  function svg(name, attributes = {}, text = null) {
    const node = document.createElementNS(NS, name);
    for (const [key, value] of Object.entries(attributes)) {
      if (value !== null && value !== undefined) node.setAttribute(key, String(value));
    }
    if (text !== null) node.textContent = text;
    return node;
  }

  function short(value, limit = 86) {
    const text = String(value || "").replace(/\s+/g, " ").trim();
    return text.length <= limit ? text : `${text.slice(0, limit - 1)}…`;
  }

  function actionById(id) {
    return (state.ball?.hair?.actions || []).find((item) => item.id === id) || null;
  }

  function eventByAction(id) {
    return (state.ball?.interaction_events || []).find((item) => item.hair_action_id === id) || null;
  }

  function returnAction() {
    return (state.ball?.hair?.actions || []).find(
      (item) => item.kind === "EXTEND_SOURCE_PRESERVING_RETURN",
    ) || null;
  }

  async function verifyBall(ball) {
    if (!ball || ball.protocol !== EXPECTED_PROTOCOL) return false;
    if (ball.id !== await digest("closure-ball", ball.identity_basis)) return false;
    if (ball.projection_id !== await digest(
      "closure-ball-relative-projection",
      ball.projection_identity_basis,
    )) return false;
    const maze = ball.maze_partition;
    if (!maze || maze.id !== await digest("closure-maze-partition", maze.identity_basis)) return false;
    for (const cell of maze.cells || []) {
      if (cell.id !== await digest("closure-locality", cell.identity_basis)) return false;
    }
    const actionIds = [];
    for (const action of ball.hair?.actions || []) {
      if (action.id !== await digest("closure-hair-action", action.identity_basis)) return false;
      if (action.closure_ball_id !== ball.id || action.projection_id !== ball.projection_id) return false;
      actionIds.push(action.id);
    }
    if (stable(actionIds) !== stable(ball.hair?.action_ids || [])) return false;
    if (stable(actionIds) !== stable(ball.natural_ui?.hair_action_ids || [])) return false;

    const eventActionIds = [];
    for (const event of ball.interaction_events || []) {
      const projection = event.event_projection;
      if (projection.underlying_path_id !== await digest(
        "closure-interaction-path",
        projection.path_identity_basis,
      )) return false;
      if (event.id !== await digest("closure-interaction-event", event.identity_basis)) return false;
      if (event.underlying_path_id !== projection.underlying_path_id) return false;
      if (projection.closure_ball_id !== ball.id || projection.projection_id !== ball.projection_id) return false;
      if (stable(event.readings?.ui) !== stable(projection)
          || stable(event.readings?.ai) !== stable(projection)
          || stable(event.readings?.token) !== stable(projection)
          || stable(event.readings?.closure) !== stable(projection)) return false;
      if (projection.open_seam === true && projection.executes_as_equality === true) return false;
      if (projection.executes_as_equality === true && projection.closure_defect !== 0) return false;
      eventActionIds.push(event.hair_action_id);
    }
    if (stable([...eventActionIds].sort()) !== stable([...actionIds].sort())) return false;
    return ball.checks?.equality_closure_preserved === true
      && ball.natural_ui?.closure_ball_id === ball.id
      && ball.natural_ui?.projection_id === ball.projection_id
      && ball.natural_ui?.interface_is_external_scene === false;
  }

  function petalPath(cell) {
    const centre = cell.geometry?.centre || [500, 360];
    const radius = Number(cell.geometry?.radius || 90);
    const cx = Number(centre[0]);
    const cy = Number(centre[1]);
    if (cell.focused) {
      return `M ${cx - radius} ${cy} a ${radius} ${radius} 0 1 0 ${radius * 2} 0 a ${radius} ${radius} 0 1 0 ${-radius * 2} 0`;
    }
    const dx = cx - 500;
    const dy = cy - 360;
    const length = Math.max(1, Math.hypot(dx, dy));
    const nx = -dy / length;
    const ny = dx / length;
    const width = radius * .72;
    const nearX = 500 + dx * .34;
    const nearY = 360 + dy * .34;
    const leftNear = [nearX + nx * width * .35, nearY + ny * width * .35];
    const rightNear = [nearX - nx * width * .35, nearY - ny * width * .35];
    const leftFar = [cx + nx * width, cy + ny * width];
    const rightFar = [cx - nx * width, cy - ny * width];
    return [
      `M 500 360`,
      `Q ${leftNear[0]} ${leftNear[1]} ${leftFar[0]} ${leftFar[1]}`,
      `Q ${cx + dx / length * radius} ${cy + dy / length * radius} ${rightFar[0]} ${rightFar[1]}`,
      `Q ${rightNear[0]} ${rightNear[1]} 500 360 Z`,
    ].join(" ");
  }

  function pathData(points) {
    if (!Array.isArray(points) || points.length !== 3) return "";
    return `M ${points[0][0]} ${points[0][1]} Q ${points[1][0]} ${points[1][1]} ${points[2][0]} ${points[2][1]}`;
  }

  function tracesForCell(cell) {
    return (cell.source_traces || []).map((trace) => trace.exact_source).filter(Boolean);
  }

  function describe(action, event) {
    const projection = event?.event_projection || {};
    const parts = [
      `${action.kind}`,
      `path ${short(projection.underlying_path_id, 34)}`,
      `UI = AI = TOKEN = CLOSURE`,
      projection.open_seam ? "OPEN: return required" : "WITNESSED: closure defect 0",
    ];
    if (action.target_perspective_id && action.target_perspective_id !== action.source_perspective_id) {
      parts.push(`${action.source_perspective_id} → ${action.target_perspective_id}`);
    }
    if (action.relation_id) parts.push(`relation ${short(action.relation_id, 42)}`);
    return parts.join("  ·  ");
  }

  function showReturn(action, event) {
    state.selectedActionId = action.id;
    state.selectedEventId = event?.id || null;
    returnFlow.hidden = false;
    returnSubmit.disabled = !returnAction();
    reading.textContent = describe(action, event);
    queueMicrotask(() => returnSource.focus());
  }

  async function activate(action, event) {
    state.selectedActionId = action.id;
    state.selectedEventId = event?.id || null;
    renderSelection();
    reading.textContent = describe(action, event);

    if (action.kind === "REBASE_PERSPECTIVE" && action.target_perspective_id) {
      state.perspectiveId = action.target_perspective_id;
      await loadBall();
      return;
    }
    if ((action.kind === "ENTER_CLOSURE_LOCALITY"
         || action.kind === "FOLLOW_WITNESSED_TRANSLATION")
        && action.target_event_id) {
      state.focusEventId = action.target_event_id;
      await loadBall();
      return;
    }
    if (action.kind === "FOLLOW_OPEN_SEAM"
        || action.kind === "EXTEND_SOURCE_PRESERVING_RETURN") {
      showReturn(action, event);
      return;
    }
    if (action.kind === "REPARAMETERIZE_PERSPECTIVE_HAIR") {
      hairControl.hidden = false;
    }
  }

  function keyboardActivate(node, callback) {
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        callback();
      }
    });
  }

  function renderSelection() {
    for (const node of layer.querySelectorAll(".hair-group")) {
      node.dataset.selected = String(node.dataset.actionId === state.selectedActionId);
    }
  }

  function renderBall() {
    const ball = state.ball;
    const maze = ball.maze_partition;
    const geometry = ball.natural_ui.geometry;
    layer.replaceChildren();
    layer.setAttribute("transform", `rotate(${state.hairMillidegrees / 1000} 500 360)`);

    const boundary = geometry.closure_boundary;
    layer.append(svg("circle", {
      class: "closure-boundary",
      cx: boundary.centre[0], cy: boundary.centre[1], r: boundary.radius,
    }));
    if ((ball.unitary_curvature?.open_event_ids || []).length) {
      layer.append(svg("path", {
        class: "boundary-seam",
        d: `M 500 ${360 - boundary.radius} A ${boundary.radius} ${boundary.radius} 0 0 1 ${500 + boundary.radius * .72} ${360 - boundary.radius * .69}`,
      }));
    }

    const localityLayer = svg("g", {"aria-label": "Maze partition localities"});
    for (const cell of maze.cells || []) {
      const localityAction = (ball.hair.actions || []).find(
        (action) => action.kind === "ENTER_CLOSURE_LOCALITY"
          && action.target_natural_form_id === cell.natural_form_id
          && action.target_state_id === cell.representative_state_id,
      );
      const group = svg("g", {
        class: "locality",
        tabindex: localityAction ? 0 : -1,
        role: localityAction ? "button" : "group",
        "aria-label": `Closure locality ${cell.natural_form_id || cell.id}`,
        "data-focused": cell.focused,
      });
      group.append(svg("path", {class: "locality-shape", d: petalPath(cell)}));
      const [cx, cy] = cell.geometry.centre;
      const traces = tracesForCell(cell);
      group.append(svg("text", {class: "locality-label", x: cx, y: cy - 4}, short(traces[0] || cell.natural_form_id || "locality", 42)));
      group.append(svg("text", {class: "locality-meta", x: cx, y: cy + 13}, `${cell.member_state_ids.length} relative form${cell.member_state_ids.length === 1 ? "" : "s"}`));
      if (localityAction) {
        const event = eventByAction(localityAction.id);
        group.addEventListener("click", () => activate(localityAction, event));
        keyboardActivate(group, () => activate(localityAction, event));
      }
      localityLayer.append(group);
    }
    layer.append(localityLayer);

    const hairLayer = svg("g", {"aria-label": "Hair-derived interactions"});
    const pathByAction = new Map(
      (geometry.hair_paths || []).map((path) => [path.hair_action_id, path]),
    );
    for (const action of ball.hair.actions || []) {
      if (action.kind === "ENTER_CLOSURE_LOCALITY") continue;
      const path = pathByAction.get(action.id);
      const event = eventByAction(action.id);
      if (!path || !event) continue;
      const group = svg("g", {
        class: "hair-group",
        tabindex: 0,
        role: "button",
        "aria-label": `${action.kind}: ${event.event_projection.open_seam ? "OPEN" : "WITNESSED"}`,
        "data-action-id": action.id,
        "data-selected": action.id === state.selectedActionId,
      });
      const d = pathData(path.quadratic_path);
      group.append(svg("path", {
        class: `hair-visible ${path.open_seam ? "open" : "witnessed"}`,
        d,
      }));
      group.append(svg("path", {class: "hair-hit", d}));
      const endpoint = path.quadratic_path?.[2];
      if (endpoint) group.append(svg("circle", {
        class: "path-mark",
        cx: endpoint[0], cy: endpoint[1], r: path.open_seam ? 4.5 : 3.2,
        style: `color:${path.open_seam ? "var(--open)" : "var(--witness)"}`,
      }));
      group.addEventListener("click", () => activate(action, event));
      keyboardActivate(group, () => activate(action, event));
      hairLayer.append(group);
    }
    layer.append(hairLayer);
    layer.append(svg("text", {id: "centre-reading", x: 500, y: 366}, short(ball.active_perspective_id, 46)));

    identity.textContent = `${short(ball.active_perspective_id, 42)}  ·  ball ${short(ball.id, 40)}  ·  projection ${short(ball.projection_id, 40)}`;
    const open = (ball.unitary_curvature?.open_event_ids || []).length > 0 || String(ball.status).startsWith("OPEN");
    statusNode.textContent = open ? "OPEN" : "WITNESSED";
    statusNode.dataset.open = String(open);

    const reparameterize = (ball.hair.actions || []).find(
      (action) => action.kind === "REPARAMETERIZE_PERSPECTIVE_HAIR",
    );
    hairControl.hidden = !reparameterize;
    const hasReturn = Boolean(returnAction());
    returnFlow.hidden = !hasReturn || !open;
    returnSubmit.disabled = !hasReturn;

    const focused = (maze.cells || []).find((cell) => cell.focused);
    const focusedTraces = focused ? tracesForCell(focused) : [];
    reading.textContent = focusedTraces.length
      ? focusedTraces.join("  ↔  ")
      : "The interface is the active perspective projection of this closure ball. Follow a hair path; OPEN paths require a source-preserving return.";
  }

  async function loadBall() {
    fatal.hidden = true;
    reading.textContent = "Reprojecting closure from the active locality…";
    const params = new URLSearchParams({perspective_id: state.perspectiveId});
    if (state.focusEventId) params.set("focus_event_id", state.focusEventId);
    const response = await fetch(`/supernet/ball?${params}`, {
      headers: {Accept: "application/json"},
      cache: "no-store",
    });
    if (!response.ok) throw new Error(`closure projection ${response.status}`);
    const payload = await response.json();
    if (!await verifyBall(payload.closure_ball)) {
      throw new Error("closure ball failed local equality re-derivation");
    }
    if (payload.closure_ball.contract_id !== payload.closure_ui_contract.id) {
      throw new Error("closure ball is not bound to the active contract");
    }
    state.ball = payload.closure_ball;
    state.contract = payload.closure_ui_contract;
    state.focusEventId = payload.closure_ui_contract.focus_event_id || null;
    state.selectedActionId = null;
    state.selectedEventId = null;
    renderBall();
  }

  hairAngle.addEventListener("input", () => {
    state.hairMillidegrees = Number(hairAngle.value || 0);
    hairAngleValue.value = `${state.hairMillidegrees / 1000}°`;
    layer.setAttribute("transform", `rotate(${state.hairMillidegrees / 1000} 500 360)`);
  });

  returnFlow.addEventListener("submit", async (event) => {
    event.preventDefault();
    const exactSource = returnSource.value.trim();
    const contract = state.contract;
    const action = returnAction();
    if (!exactSource || !contract || !action) return;
    returnSubmit.disabled = true;
    reading.textContent = "Returning the exact source, re-closing, then deriving the successor ball…";
    try {
      const commitmentBody = {
        contract_id: contract.id,
        closure_equation_system_id: contract.closure_naturality_equations.id,
        return_relation_id: contract.return_relation.id,
        perspective_id: contract.perspective_id,
        focus_event_id: contract.focus_event_id,
        exact_source_return: exactSource,
        local_perspective_hair_millidegrees: state.hairMillidegrees,
        reading_kernel: contract.perspective_closure.kernel || [],
      };
      const localCommitment = `local-projection:${(await sha256(stable(commitmentBody))).slice(0, 24)}`;
      const response = await fetch(
        `/supernet/interface/projections/${encodeURIComponent(contract.id)}/return`,
        {
          method: "POST",
          headers: {"Content-Type": "application/json", Accept: "application/json"},
          body: JSON.stringify({
            return_relation_id: contract.return_relation.id,
            perspective_id: contract.perspective_id,
            focus_event_id: contract.focus_event_id,
            exact_source_return: exactSource,
            closure_equation_system_id: contract.closure_naturality_equations.id,
            local_projection_commitment: localCommitment,
            local_perspective_hair_millidegrees: state.hairMillidegrees,
            source_stream: "closure-ball-perspective-flow",
          }),
        },
      );
      const payload = await response.json();
      if (!response.ok && response.status !== 409) {
        throw new Error(payload.detail || payload.status || `return ${response.status}`);
      }
      state.focusEventId = payload.focus_event_id
        || payload.closure_ui_contract?.focus_event_id
        || state.focusEventId;
      returnSource.value = "";
      await loadBall();
    } catch (error) {
      reading.textContent = `OPEN · ${error instanceof Error ? error.message : String(error)}`;
    } finally {
      returnSubmit.disabled = !returnAction();
    }
  });

  loadBall().catch((error) => {
    fatal.hidden = false;
    fatal.textContent = `The interface remains OPEN because its closure projection could not be derived: ${error instanceof Error ? error.message : String(error)}`;
  });
})();
</script>
</body>
</html>
"""


__all__ = ["CLOSURE_BALL_SUPERNET_HTML"]
