from __future__ import annotations


# There is intentionally no authored page inside the body.  The program below
# is a relation evaluator and a physical input aperture.  It owns no headings,
# buttons, fields, menus, explanations, product categories, or action names.
CLOSURE_ONLY_SUPERNET_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<title></title>
<style>
:root { color-scheme: dark; }
* { box-sizing: border-box; }
html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  overflow: hidden;
  background: #020305;
}
#translational-mirror {
  position: fixed;
  inset: 0;
  overflow: hidden;
  touch-action: manipulation;
  outline: none;
}
svg {
  display: block;
  width: 100%;
  height: 100%;
}
[data-return-sensor] {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  padding: 0;
  border: 0;
  opacity: .001;
  resize: none;
  color: transparent;
  background: transparent;
  caret-color: transparent;
  pointer-events: none;
}
.fibre-shell {
  fill: rgba(255,255,255,.018);
  stroke-width: 1.5;
  vector-effect: non-scaling-stroke;
}
.fibre-shell[data-focus="true"] {
  fill: rgba(255,255,255,.052);
  stroke-width: 2.8;
}
.translation {
  fill: none;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}
.translation[data-equality="true"] { stroke-width: 3; }
.translation[data-equality="false"] {
  stroke-width: 1.2;
  stroke-dasharray: 5 9;
  opacity: .44;
}
.potential {
  fill: none;
  stroke-width: 1;
  stroke-dasharray: 2 11;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
  opacity: .46;
}
.source-trace {
  color: rgba(249,251,255,.92);
  font: 430 clamp(13px, 1.45vw, 18px)/1.38 ui-sans-serif, system-ui, sans-serif;
  text-align: center;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  text-wrap: balance;
  pointer-events: none;
}
.draft-trace {
  color: rgba(249,251,255,.9);
  font: 470 clamp(18px, 3vw, 38px)/1.24 ui-sans-serif, system-ui, sans-serif;
  text-align: center;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  text-wrap: balance;
  pointer-events: none;
}
@media (prefers-reduced-motion: no-preference) {
  .potential { animation: relation-breathe 5.8s ease-in-out infinite; }
}
@keyframes relation-breathe {
  50% { opacity: .78; }
}
</style>
</head>
<body>
<main id="translational-mirror"></main>
<script>
(() => {
  "use strict";

  const namespace = "http://www.w3.org/2000/svg";
  const schema = "closure.supernet/translational-visualization-v2";
  const protocol = "SUPERNET-TRANSLATIONAL-VISUALIZATION";
  const statuses = new Set([
    "OPEN_SOURCE_BOUNDARY",
    "OPEN_TRUTH_CONSTRAINT",
    "WITNESSED",
  ]);
  const mount = document.getElementById("translational-mirror");
  const sensor = document.createElement("textarea");
  sensor.dataset.returnSensor = "";
  sensor.autocomplete = "off";
  sensor.autocapitalize = "sentences";
  sensor.spellcheck = true;
  sensor.setAttribute("aria-label", "");
  document.body.append(sensor);

  let active = null;
  let draft = "";
  let executing = false;

  function svgElement(name, attributes = {}) {
    const node = document.createElementNS(namespace, name);
    for (const [key, value] of Object.entries(attributes)) {
      node.setAttribute(key, String(value));
    }
    return node;
  }

  function asText(value) {
    return value === null || value === undefined ? "" : String(value);
  }

  function unique(values) {
    return [...new Set((values || []).map(asText).filter(Boolean))];
  }

  function sameMembers(left, right) {
    const a = unique(left).sort();
    const b = unique(right).sort();
    return a.length === b.length && a.every((item, index) => item === b[index]);
  }

  function derivationMatches(contract, derivation, allowOpen = false) {
    if (!derivation || typeof derivation !== "object") return false;
    if (derivation.status !== contract.status) return false;
    if (derivation.perspective_id !== contract.perspective_id) return false;
    if (derivation.truth_issued !== false) return false;
    if (contract.status === "OPEN_SOURCE_BOUNDARY") {
      return allowOpen
        && derivation.basis === "AUTHORED_PERSPECTIVE_SOURCE_BOUNDARY"
        && derivation.source_boundary_only === true
        && derivation.closure_derivation_id === null
        && derivation.visual_closure_id === null
        && derivation.nrrf843_ui_id === null
        && derivation.interaction_closure_id === null
        && derivation.field_event_seq === null;
    }
    if (contract.status === "OPEN_TRUTH_CONSTRAINT") {
      return derivation.basis === "OPEN_UNWITNESSED_TRANSLATIONAL_TRUTH_CONSTRAINT";
    }
    return derivation.basis === "TRANSLATIONAL_TRUTH_CLOSURE"
      && derivation.source_boundary_only === false
      && derivation.closure_derivation_id === contract.closure_derivation_id
      && derivation.visual_closure_id === contract.visual_closure_id
      && derivation.nrrf843_ui_id === contract.nrrf843_ui_id
      && derivation.interaction_closure_id === contract.interaction_closure_id
      && derivation.field_event_seq === contract.field_event_seq
      && unique(derivation.natural_form_ids).length > 0
      && unique(derivation.source_return_ids).length > 0
      && unique(derivation.natural_form_ids).every((item) => contract.natural_form_ids.includes(item))
      && unique(derivation.source_return_ids).every((item) => contract.source_return_ids.includes(item));
  }

  function validate(contract) {
    if (!contract || typeof contract !== "object") return false;
    if (contract.schema !== schema || contract.protocol !== protocol) return false;
    if (!statuses.has(contract.status)) return false;
    const renderer = contract.renderer_relation || {};
    if (renderer.role !== "TRANSLATIONAL_RELATION_EVALUATOR") return false;
    if (renderer.input !== "ACTIVE_PERSPECTIVE_RELATION_ONLY") return false;
    if (renderer.visible_words_source !== "SOURCE_RETURNS_ONLY") return false;
    if (!Array.isArray(renderer.fixed_visible_controls) || renderer.fixed_visible_controls.length) return false;
    if (!Array.isArray(renderer.authored_visible_vocabulary) || renderer.authored_visible_vocabulary.length) return false;
    if (!Array.isArray(renderer.fallback_visuals) || renderer.fallback_visuals.length) return false;
    if (renderer.can_define_semantics !== false || renderer.can_admit_forms !== false || renderer.can_issue_truth !== false) return false;
    const projection = contract.projection || {};
    if (projection.active_perspective_id !== contract.perspective_id) return false;
    if (!Array.isArray(projection.states) || !Array.isArray(projection.equality_fibres)) return false;
    if (!Array.isArray(projection.translations) || !Array.isArray(projection.potentials)) return false;
    if (!projection.reading || typeof projection.reading !== "object") return false;
    if (!derivationMatches(contract, (projection.visualization || {}).derivation, contract.status === "OPEN_SOURCE_BOUNDARY")) return false;
    const states = new Map();
    for (const state of projection.states) {
      if (!state.id || states.has(state.id)) return false;
      if (!asText(state.source_trace)) return false;
      if (projection.reading[state.id] !== state.display_fibre_id) return false;
      if (!derivationMatches(contract, state.derivation)) return false;
      states.set(state.id, state);
    }
    const members = [];
    for (const fibre of projection.equality_fibres) {
      if (!contract.natural_form_ids.includes(fibre.id)) return false;
      if (fibre.closure_fixed !== true || !derivationMatches(contract, fibre.derivation)) return false;
      if (!(fibre.member_state_ids || []).every((id) => states.has(id))) return false;
      members.push(...fibre.member_state_ids);
    }
    if (!sameMembers(members, [...states.keys()])) return false;
    for (const relation of projection.translations) {
      if (!states.has(relation.source_state_id) || !states.has(relation.target_state_id)) return false;
      if (relation.executes_as_equality === true
          && projection.reading[relation.source_state_id] !== projection.reading[relation.target_state_id]) return false;
      if (relation.relation_status !== "WITNESSED" && relation.executes_as_equality === true) return false;
      if (!derivationMatches(contract, relation.derivation)) return false;
    }
    for (const relation of projection.potentials) {
      if (relation.target_state_id !== null && !states.has(relation.target_state_id)) return false;
      if (relation.relation_status !== "WITNESSED" && relation.executes_as_equality === true) return false;
      if (!derivationMatches(contract, relation.derivation)) return false;
    }
    const visualization = projection.visualization || {};
    if (visualization.operator !== "PERSPECTIVE_RELATION_PROJECTIVE_FOLD") return false;
    if (JSON.stringify(visualization.view_box) !== JSON.stringify([0, 0, 1000, 1000])) return false;
    const fibrePrimitives = visualization.fibre_primitives || [];
    const translationPrimitives = visualization.translation_primitives || [];
    const potentialPrimitives = visualization.potential_primitives || [];
    if (fibrePrimitives.length !== projection.equality_fibres.length) return false;
    if (!fibrePrimitives.every((primitive) =>
      projection.equality_fibres.some((fibre) =>
        primitive.natural_form_id === fibre.id
        && sameMembers(primitive.source_state_ids, fibre.member_state_ids)
        && sameMembers(primitive.source_return_ids, fibre.source_return_ids)
      )
      && Array.isArray(primitive.centre)
      && primitive.centre.length === 2
      && Number.isFinite(primitive.centre[0])
      && Number.isFinite(primitive.centre[1])
      && Number.isFinite(primitive.radius)
      && Number.isInteger(primitive.hue)
      && derivationMatches(contract, primitive.derivation)
    )) return false;
    if (!translationPrimitives.every((primitive) =>
      projection.translations.some((relation) => relation.id === primitive.relation_id)
      && Array.isArray(primitive.quadratic_path)
      && primitive.quadratic_path.length === 3
      && derivationMatches(contract, primitive.derivation)
    )) return false;
    if (!potentialPrimitives.every((primitive) =>
      projection.potentials.some((relation) => relation.id === primitive.relation_id)
      && Array.isArray(primitive.quadratic_path)
      && primitive.quadratic_path.length === 3
      && derivationMatches(contract, primitive.derivation)
    )) return false;
    const relation = contract.return_relation;
    if (contract.status === "OPEN_TRUTH_CONSTRAINT") return relation === null;
    if (!relation || relation.kind !== "SOURCE_PRESERVING_TRANSLATIONAL_RETURN") return false;
    if (relation.full_surface_aperture !== true || relation.visible_control !== false) return false;
    if (relation.creates_truth_directly !== false || relation.reclose_after_return !== true) return false;
    if (!derivationMatches(contract, relation.derivation, contract.status === "OPEN_SOURCE_BOUNDARY")) return false;
    const execution = contract.execution || {};
    return execution.return_relation_id === relation.id
      && execution.only_relation_extension === true
      && execution.contract_revalidation_required === true
      && execution.closure_only === true;
  }

  function sourceBlock(svg, x, y, width, height, text, className) {
    const foreign = svgElement("foreignObject", {x, y, width, height});
    const block = document.createElement("div");
    block.className = className;
    block.textContent = text;
    foreign.append(block);
    svg.append(foreign);
  }

  function projectedPath(points) {
    if (!Array.isArray(points) || points.length !== 3) return "";
    return `M ${points[0][0]} ${points[0][1]} Q ${points[1][0]} ${points[1][1]} ${points[2][0]} ${points[2][1]}`;
  }

  function render(contract) {
    active = validate(contract) ? contract : null;
    mount.replaceChildren();
    mount.dataset.state = active ? active.status : "OPEN_TRUTH_CONSTRAINT";
    if (!active) return;
    const projection = active.projection;
    const visualization = projection.visualization;
    const svg = svgElement("svg", {viewBox: visualization.view_box.join(" ")});
    mount.append(svg);
    const fibreById = new Map(projection.equality_fibres.map((fibre) => [fibre.id, fibre]));
    const primitiveByForm = new Map(visualization.fibre_primitives.map((primitive) => [primitive.natural_form_id, primitive]));
    for (const relation of visualization.translation_primitives) {
      const path = svgElement("path", {
        d: projectedPath(relation.quadratic_path),
        class: "translation",
        stroke: `hsl(${relation.hue} 72% 66%)`,
        "data-equality": relation.executes_as_equality === true,
      });
      svg.append(path);
    }
    const focusForm = active.return_relation?.parent_natural_form_id || null;
    const focusPrimitive = primitiveByForm.get(focusForm) || {centre: [500, 500], radius: 54};
    visualization.potential_primitives.forEach((relation) => {
      svg.append(svgElement("path", {
        d: projectedPath(relation.quadratic_path),
        class: "potential",
        stroke: `hsl(${relation.hue} 68% 65%)`,
      }));
    });
    for (const primitive of visualization.fibre_primitives) {
      const fibre = fibreById.get(primitive.natural_form_id);
      if (!fibre) continue;
      const [x, y] = primitive.centre;
      const group = svgElement("g", {"data-natural-form-id": fibre.id});
      const color = `hsl(${primitive.hue} 76% 66%)`;
      const shell = svgElement("circle", {
        cx: x,
        cy: y,
        r: primitive.radius,
        class: "fibre-shell",
        stroke: color,
        "data-focus": fibre.id === focusForm,
      });
      group.append(shell);
      const memberStates = fibre.member_state_ids
        .map((id) => projection.states.find((state) => state.id === id))
        .filter(Boolean);
      const trace = memberStates.map((state) => state.source_trace).join("\n\n");
      const firstEvent = memberStates[0]?.event_id;
      if (firstEvent) {
        group.style.cursor = "pointer";
        group.addEventListener("pointerdown", (event) => {
          event.stopPropagation();
          const current = new URL(window.location.href);
          current.searchParams.set("focus_event_id", firstEvent);
          current.searchParams.set("perspective_id", active.perspective_id);
          history.replaceState(null, "", current);
          load(firstEvent, active.perspective_id).finally(() => sensor.focus());
        });
      }
      svg.append(group);
      const traceWidth = Math.max(120, primitive.radius * 2.8);
      sourceBlock(
        svg,
        x - traceWidth / 2,
        y - primitive.radius * .55,
        traceWidth,
        primitive.radius * 1.25,
        trace,
        "source-trace",
      );
    }
    renderDraft(svg, focusPrimitive);
  }

  function renderDraft(svg, focusPrimitive) {
    if (!draft) return;
    const [x, y] = focusPrimitive?.centre || [500, 500];
    const blockWidth = 720;
    sourceBlock(
      svg,
      x - blockWidth / 2,
      y - 180,
      blockWidth,
      360,
      draft,
      "draft-trace",
    );
  }

  function perspectiveFromLocation() {
    const current = new URL(window.location.href);
    let perspective = current.searchParams.get("perspective_id");
    if (!perspective) {
      const identity = crypto.randomUUID
        ? crypto.randomUUID()
        : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
      perspective = `perspective:${identity}`;
      current.searchParams.set("perspective_id", perspective);
      history.replaceState(null, "", current);
    }
    return perspective;
  }

  async function load(focusEventId, perspectiveId) {
    const params = new URLSearchParams({perspective_id: perspectiveId});
    if (focusEventId) params.set("focus_event_id", focusEventId);
    const response = await fetch(`/supernet/interface?${params}`, {credentials: "same-origin"});
    if (!response.ok) return render(null);
    const payload = await response.json();
    render(payload.closure_ui_contract || null);
  }

  async function returnSource() {
    if (executing || !active || !active.return_relation || !draft.trim()) return;
    executing = true;
    const relation = active.return_relation;
    const endpoint = active.execution.endpoint_template.replace(
      "{contract_id}",
      encodeURIComponent(active.id),
    );
    const exactSourceReturn = draft;
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        credentials: "same-origin",
        headers: {"content-type": "application/json"},
        body: JSON.stringify({
          return_relation_id: relation.id,
          perspective_id: active.perspective_id,
          focus_event_id: active.focus_event_id,
          exact_source_return: exactSourceReturn,
        }),
      });
      const payload = await response.json();
      if (response.status === 409) {
        await load(active.focus_event_id, active.perspective_id);
        return;
      }
      const next = payload.closure_ui_contract
        || payload.interface?.closure_ui_contract
        || payload.detail?.closure_ui_contract;
      if (!response.ok || !next) return;
      draft = "";
      sensor.value = "";
      const current = new URL(window.location.href);
      if (next.focus_event_id) current.searchParams.set("focus_event_id", next.focus_event_id);
      current.searchParams.set("perspective_id", next.perspective_id);
      history.replaceState(null, "", current);
      render(next);
    } finally {
      executing = false;
      sensor.focus();
    }
  }

  sensor.addEventListener("input", () => {
    draft = sensor.value;
    if (active) render(active);
  });
  sensor.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      returnSource();
    } else if (event.key === "Escape") {
      draft = "";
      sensor.value = "";
      if (active) render(active);
    }
  });
  mount.addEventListener("pointerdown", () => sensor.focus());
  window.addEventListener("resize", () => {
    if (active) render(active);
  });

  const perspective = perspectiveFromLocation();
  const current = new URL(window.location.href);
  load(current.searchParams.get("focus_event_id"), perspective)
    .finally(() => sensor.focus());
})();
</script>
</body>
</html>
"""


__all__ = ["CLOSURE_ONLY_SUPERNET_HTML"]
