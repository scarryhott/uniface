from __future__ import annotations


CLOSURE_ONLY_SUPERNET_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title></title>
<style>
:root {
  color-scheme: dark;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
* { box-sizing: border-box; }
html, body { margin: 0; min-height: 100%; }
body {
  min-height: 100vh;
  background: var(--closure-background);
  color: var(--closure-text);
}
[data-closure-only-contract] {
  min-height: 100vh;
  opacity: 0;
  transition: opacity 180ms ease;
}
[data-closure-only-contract][data-ready="true"] { opacity: 1; }
[data-kind="surface"] {
  width: min(calc(100% - 28px), var(--closure-max-width));
  margin: 0 auto;
  padding: clamp(22px, 4vw, 54px) 0;
  display: grid;
  gap: var(--closure-gap);
}
[data-kind="region"],
[data-kind="topology"] {
  min-width: 0;
  padding: clamp(18px, 3vw, 30px);
  border: 1px solid var(--closure-line);
  border-radius: var(--closure-radius);
  background: color-mix(in srgb, var(--closure-surface) 92%, transparent);
  box-shadow: 0 24px 80px color-mix(in srgb, var(--closure-background) 74%, transparent);
}
[data-presentation="reading"] {
  background:
    radial-gradient(circle at 82% 10%, color-mix(in srgb, var(--closure-accent) 22%, transparent), transparent 38%),
    var(--closure-surface);
}
[data-presentation="composer"],
[data-presentation="agreement"] {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--closure-gap);
}
[data-presentation="composer"] > [data-kind="text"],
[data-presentation="agreement"] > [data-kind="text"],
[data-presentation="composer"] > [data-kind="textarea"],
[data-presentation="agreement"] > [data-kind="textarea"] {
  grid-column: 1 / -1;
}
[data-presentation="potentials"] > [data-kind="region"] {
  margin-top: 12px;
  border-left: 3px solid var(--closure-open);
  padding: 13px 15px;
  background: var(--closure-surface-alt);
}
[data-presentation="witnessed"] { border-left-color: var(--closure-witnessed) !important; }
h1, h2, h3, p { margin: 0; }
h1 {
  max-width: 20ch;
  font-size: clamp(2.2rem, 7vw, 6.4rem);
  line-height: .92;
  letter-spacing: -.065em;
  text-wrap: balance;
}
h2 { font-size: clamp(1.2rem, 2.5vw, 2rem); letter-spacing: -.035em; }
p { color: var(--closure-muted); line-height: 1.6; }
[data-kind="metric"] {
  display: inline-grid;
  gap: 4px;
  margin: 22px 20px 0 0;
  vertical-align: top;
}
[data-kind="metric"] > :first-child {
  color: var(--closure-muted);
  font-size: .72rem;
  letter-spacing: .12em;
  text-transform: uppercase;
}
[data-kind="metric"] > :last-child { color: var(--closure-witnessed); font-weight: 700; }
[data-kind="input"],
[data-kind="textarea"],
[data-kind="select"] {
  display: grid;
  align-content: start;
  gap: 8px;
}
label {
  color: var(--closure-muted);
  font-size: .76rem;
  letter-spacing: .11em;
  text-transform: uppercase;
}
input, textarea, select, button {
  width: 100%;
  border: 1px solid var(--closure-line);
  border-radius: calc(var(--closure-radius) * .58);
  font: inherit;
  color: var(--closure-text);
}
input, textarea, select {
  padding: 13px 14px;
  background: var(--closure-surface-alt);
  outline: none;
}
textarea { min-height: 116px; resize: vertical; }
input:focus, textarea:focus, select:focus {
  border-color: var(--closure-accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--closure-accent) 18%, transparent);
}
[aria-invalid="true"] { border-color: var(--closure-open) !important; }
button {
  min-height: 48px;
  align-self: end;
  padding: 12px 16px;
  cursor: pointer;
  border-color: color-mix(in srgb, var(--closure-accent) 66%, var(--closure-line));
  background: color-mix(in srgb, var(--closure-accent) 17%, var(--closure-surface-alt));
  font-weight: 760;
}
button:hover { background: color-mix(in srgb, var(--closure-accent) 27%, var(--closure-surface-alt)); }
button:disabled { cursor: wait; opacity: .52; }
svg { display: block; width: 100%; height: var(--closure-topology-height); overflow: visible; }
.closure-edge {
  stroke: var(--closure-line);
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}
.closure-edge[data-truth="WITNESSED"] { stroke: var(--closure-witnessed); }
.closure-edge[data-truth="OPEN"] { stroke: var(--closure-open); stroke-dasharray: 8 10; }
.closure-node circle {
  fill: color-mix(in srgb, var(--closure-surface-alt) 88%, transparent);
  stroke: var(--closure-accent);
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
}
.closure-node[data-truth="WITNESSED"] circle { stroke: var(--closure-witnessed); }
.closure-node text {
  fill: var(--closure-text);
  font-size: 13px;
  text-anchor: middle;
  paint-order: stroke;
  stroke: var(--closure-background);
  stroke-width: 5px;
  stroke-linejoin: round;
}
.closure-node text + text { fill: var(--closure-muted); font-size: 10px; }
@media (max-width: 760px) {
  [data-presentation="composer"],
  [data-presentation="agreement"] { grid-template-columns: 1fr; }
  [data-kind="surface"] { width: min(calc(100% - 18px), var(--closure-max-width)); }
}
</style>
</head>
<body>
<main id="closure-contract-root" data-closure-only-contract></main>
<script>
(() => {
  "use strict";

  const mount = document.getElementById("closure-contract-root");
  const namespace = "http://www.w3.org/2000/svg";
  const schema = "closure.supernet/perspective-interaction-ui-contract-v1";
  const protocol = "SUPERNET-CLOSURE-ONLY-UI";
  const statuses = new Set(["OPEN_SOURCE_BOUNDARY", "OPEN_TRUTH_CONSTRAINT", "WITNESSED"]);
  const kinds = new Set(["surface", "region", "text", "metric", "input", "textarea", "select", "button", "topology"]);
  const tags = new Set(["h1", "h2", "h3", "p", "strong", "span"]);
  const inputKinds = new Set(["input", "textarea", "select"]);
  const operations = new Set(["OFFER_SOURCE", "CONTINUE_INTERACTION", "PROPOSE_AGREEMENT", "DECIDE_AGREEMENT", "RETURN_AGREEMENT"]);
  const fields = new Map();
  let activeContract = null;

  function asText(value) {
    return value === null || value === undefined ? "" : String(value);
  }

  function walk(node, output = []) {
    if (!node || typeof node !== "object") return output;
    output.push(node);
    if (Array.isArray(node.children)) {
      for (const child of node.children) walk(child, output);
    }
    return output;
  }

  function sameMembers(left, right) {
    if (!Array.isArray(left) || !Array.isArray(right)) return false;
    const a = [...new Set(left.map(asText))].sort();
    const b = [...new Set(right.map(asText))].sort();
    return a.length === b.length && a.every((item, index) => item === b[index]);
  }

  function derivationMatches(contract, derivation) {
    if (!derivation || typeof derivation !== "object") return false;
    if (derivation.status !== contract.status) return false;
    if (derivation.perspective_id !== contract.perspective_id) return false;
    if (derivation.truth_issued !== false) return false;
    if (contract.status === "OPEN_SOURCE_BOUNDARY") {
      return derivation.basis === "OPEN_AUTHORED_PERSPECTIVE_SOURCE_BOUNDARY"
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
    const derivedForms = new Set((derivation.natural_form_ids || []).map(asText));
    const derivedSources = new Set((derivation.source_return_ids || []).map(asText));
    const formUniverse = new Set((contract.natural_form_ids || []).map(asText));
    const sourceUniverse = new Set((contract.source_return_ids || []).map(asText));
    return derivation.basis === "TRANSLATIONAL_TRUTH_CLOSURE"
      && derivation.source_boundary_only === false
      && derivation.closure_derivation_id === contract.closure_derivation_id
      && derivation.visual_closure_id === contract.visual_closure_id
      && derivation.nrrf843_ui_id === contract.nrrf843_ui_id
      && derivation.interaction_closure_id === contract.interaction_closure_id
      && derivation.field_event_seq === contract.field_event_seq
      && derivedForms.size > 0
      && derivedSources.size > 0
      && [...derivedForms].every((item) => formUniverse.has(item))
      && [...derivedSources].every((item) => sourceUniverse.has(item));
  }

  function validateContract(contract) {
    if (!contract || typeof contract !== "object") return false;
    if (contract.schema !== schema || contract.protocol !== protocol) return false;
    if (!statuses.has(contract.status)) return false;
    if (contract.status === "WITNESSED" && (!Number.isInteger(contract.field_event_seq) || contract.field_event_seq < 1)) return false;
    if (!contract.audit || contract.audit.closure_only_execution !== true) return false;
    const renderer = contract.renderer_contract || {};
    if (renderer.role !== "GENERIC_CONTRACT_INTERPRETER") return false;
    if (renderer.visible_instance_source !== "CONTRACT_ONLY") return false;
    if (renderer.hardcoded_visible_instances !== false || renderer.semantic_fallback !== false) return false;
    if (!sameMembers(renderer.allowed_node_kinds, [...kinds])) return false;
    if (!sameMembers(renderer.allowed_text_tags, [...tags])) return false;
    if (!derivationMatches(contract, (contract.visual_form || {}).derivation)) return false;
    const nodes = walk(contract.root);
    if (!nodes.length) return false;
    const nodeIds = nodes.map((node) => asText(node.id));
    if (nodeIds.some((id) => !id) || new Set(nodeIds).size !== nodeIds.length) return false;
    const fieldIds = [];
    const controlIds = [];
    for (const node of nodes) {
      if (!kinds.has(node.kind) || !derivationMatches(contract, node.derivation)) return false;
      if (node.kind === "text" && !tags.has(node.tag)) return false;
      if (inputKinds.has(node.kind)) fieldIds.push(asText(node.id));
      if (node.kind === "button") controlIds.push(asText(node.action_id));
      if (node.kind === "topology") {
        const topology = node.topology || {};
        if (!topology.projection || topology.projection.static_external_map !== false) return false;
        if (!derivationMatches(contract, topology.projection.derivation)) return false;
        const topologyIds = (topology.nodes || []).map((item) => asText(item.id));
        if (new Set(topologyIds).size !== topologyIds.length) return false;
        if (!sameMembers(Object.keys(topology.positions || {}), topologyIds)) return false;
        for (const item of topology.nodes || []) {
          if (!derivationMatches(contract, item.derivation)) return false;
        }
        for (const item of topology.edges || []) {
          if (!topologyIds.includes(asText(item.source)) || !topologyIds.includes(asText(item.target))) return false;
          if (item.truth_status !== "WITNESSED" && item.executes_as_equality === true) return false;
          if (!derivationMatches(contract, item.derivation)) return false;
        }
      }
    }
    if (new Set(fieldIds).size !== fieldIds.length) return false;
    if (new Set(controlIds).size !== controlIds.length) return false;
    const actions = Array.isArray(contract.action_bindings) ? contract.action_bindings : [];
    const actionIds = actions.map((action) => asText(action.id));
    if (!sameMembers(controlIds, actionIds)) return false;
    if (!sameMembers(actionIds, (contract.execution || {}).allowed_action_ids || [])) return false;
    if ((contract.execution || {}).endpoint_template !== "/supernet/interface/contracts/{contract_id}/execute") return false;
    if ((contract.execution || {}).contract_revalidation_required !== true) return false;
    if ((contract.execution || {}).closure_only !== true) return false;
    for (const action of actions) {
      if (!operations.has(action.operation)) return false;
      if (action.enabled !== true || action.external_semantic_action !== false) return false;
      if (!derivationMatches(contract, action.derivation)) return false;
      if (["endpoint", "endpoint_selector", "method", "payload", "url"].some((key) => key in action)) return false;
      if (!(action.input_field_ids || []).every((id) => fieldIds.includes(asText(id)))) return false;
      if (!(action.required_field_ids || []).every((id) => (action.input_field_ids || []).includes(id))) return false;
    }
    if (contract.status === "OPEN_TRUTH_CONSTRAINT") {
      return actions.length === 0 && contract.root.visible === false;
    }
    return true;
  }

  function applyVisualForm(contract) {
    const palette = (contract.visual_form || {}).palette || {};
    const geometry = (contract.visual_form || {}).geometry || {};
    const colorPattern = /^hsl\(\d{1,3}\s+\d{1,3}%\s+\d{1,3}%\)$/;
    const colors = {
      background: "--closure-background",
      surface: "--closure-surface",
      surface_alt: "--closure-surface-alt",
      text: "--closure-text",
      muted: "--closure-muted",
      accent: "--closure-accent",
      witnessed: "--closure-witnessed",
      open: "--closure-open",
      line: "--closure-line",
    };
    for (const [key, variable] of Object.entries(colors)) {
      const value = asText(palette[key]);
      if (!colorPattern.test(value)) throw new Error("invalid contract color");
      document.documentElement.style.setProperty(variable, value);
    }
    const dimensions = {
      max_width_px: "--closure-max-width",
      gap_px: "--closure-gap",
      radius_px: "--closure-radius",
      topology_height_px: "--closure-topology-height",
    };
    for (const [key, variable] of Object.entries(dimensions)) {
      const value = Number(geometry[key]);
      if (!Number.isFinite(value) || value < 0 || value > 4000) throw new Error("invalid contract geometry");
      document.documentElement.style.setProperty(variable, value + "px");
    }
  }

  function svgElement(name, attributes = {}) {
    const element = document.createElementNS(namespace, name);
    for (const [key, value] of Object.entries(attributes)) {
      element.setAttribute(key, asText(value));
    }
    return element;
  }

  function renderTopology(node) {
    const topology = node.topology;
    const titleId = node.id + "-title";
    const svg = svgElement("svg", {
      role: "img",
      viewBox: topology.view_box.join(" "),
      "aria-labelledby": titleId,
    });
    const title = svgElement("title", { id: titleId });
    title.textContent = asText(topology.projection.active_perspective_id);
    svg.append(title);
    const positions = topology.positions;
    for (const edge of topology.edges) {
      const source = positions[edge.source];
      const target = positions[edge.target];
      const line = svgElement("line", {
        x1: source.x,
        y1: source.y,
        x2: target.x,
        y2: target.y,
      });
      line.setAttribute("class", "closure-edge");
      line.dataset.truth = asText(edge.truth_status);
      line.style.strokeWidth = asText(edge.width);
      const edgeTitle = svgElement("title");
      edgeTitle.textContent = asText(edge.label);
      line.append(edgeTitle);
      svg.append(line);
    }
    for (const item of topology.nodes) {
      const position = positions[item.id];
      const group = svgElement("g", {
        transform: "translate(" + position.x + " " + position.y + ")",
      });
      group.setAttribute("class", "closure-node");
      group.dataset.truth = asText(item.truth_status);
      const circle = svgElement("circle", { r: item.radius });
      const nodeTitle = svgElement("title");
      nodeTitle.textContent = asText(item.label);
      circle.append(nodeTitle);
      const label = svgElement("text", { y: Number(item.radius) + 18 });
      label.textContent = asText(item.label);
      const sublabel = svgElement("text", { y: Number(item.radius) + 34 });
      sublabel.textContent = asText(item.sublabel);
      group.append(circle, label, sublabel);
      svg.append(group);
    }
    return svg;
  }

  function renderNode(node) {
    if (node.visible === false) return null;
    let element;
    if (node.kind === "surface") {
      element = document.createElement("div");
    } else if (node.kind === "region") {
      element = document.createElement("section");
    } else if (node.kind === "text") {
      element = document.createElement(node.tag);
      element.textContent = asText(node.text);
    } else if (node.kind === "metric") {
      element = document.createElement("div");
      const label = document.createElement("span");
      const value = document.createElement("span");
      label.textContent = asText(node.label);
      value.textContent = asText(node.value);
      element.append(label, value);
    } else if (inputKinds.has(node.kind)) {
      element = document.createElement("div");
      const label = document.createElement("label");
      const controlId = "closure-field-" + node.id;
      label.htmlFor = controlId;
      label.textContent = asText(node.label);
      const control = document.createElement(node.kind === "select" ? "select" : node.kind);
      control.id = controlId;
      control.name = asText(node.id);
      control.required = node.required === true;
      if (Number.isInteger(node.max_length)) control.maxLength = node.max_length;
      if (node.kind === "select") {
        for (const optionRecord of node.options) {
          const option = document.createElement("option");
          option.value = asText(optionRecord.value);
          option.textContent = asText(optionRecord.label);
          option.selected = option.value === asText(node.value);
          control.append(option);
        }
      } else {
        control.value = asText(node.value);
        control.placeholder = asText(node.placeholder);
      }
      fields.set(asText(node.id), control);
      element.append(label, control);
    } else if (node.kind === "button") {
      element = document.createElement("button");
      element.type = "button";
      element.textContent = asText(node.label);
      element.dataset.actionId = asText(node.action_id);
      element.addEventListener("click", () => executeAction(asText(node.action_id)));
    } else if (node.kind === "topology") {
      element = document.createElement("section");
      element.append(renderTopology(node));
    } else {
      return null;
    }
    element.dataset.kind = asText(node.kind);
    element.dataset.nodeId = asText(node.id);
    if (node.presentation) element.dataset.presentation = asText(node.presentation);
    if (Array.isArray(node.children)) {
      for (const child of node.children) {
        const rendered = renderNode(child);
        if (rendered) element.append(rendered);
      }
    }
    return element;
  }

  function firstTitle(node) {
    return walk(node).find((item) => item.kind === "text" && item.tag === "h1");
  }

  function renderContract(contract) {
    mount.replaceChildren();
    fields.clear();
    mount.dataset.ready = "false";
    mount.dataset.state = "OPEN";
    activeContract = null;
    if (!validateContract(contract)) return;
    if (contract.status === "OPEN_TRUTH_CONSTRAINT" || contract.root.visible === false) return;
    applyVisualForm(contract);
    const rendered = renderNode(contract.root);
    if (!rendered) return;
    mount.append(rendered);
    const title = firstTitle(contract.root);
    document.title = title ? asText(title.text) : "";
    activeContract = contract;
    mount.dataset.contractId = asText(contract.id);
    mount.dataset.state = asText(contract.status);
    mount.dataset.ready = "true";
  }

  function fieldValue(fieldId) {
    const control = fields.get(fieldId);
    return control ? control.value : "";
  }

  async function loadContract(focusEventId, perspectiveId) {
    const query = new URLSearchParams();
    if (focusEventId) query.set("focus_event_id", asText(focusEventId));
    if (perspectiveId) query.set("perspective_id", asText(perspectiveId));
    const suffix = query.toString() ? "?" + query.toString() : "";
    const response = await fetch("/supernet/interface" + suffix, {
      headers: { accept: "application/json" },
    });
    if (!response.ok) return false;
    const payload = await response.json();
    const contract = payload.closure_ui_contract
      || (payload.visual_closure || {}).closure_ui_contract;
    if (!contract) return false;
    renderContract(contract);
    return true;
  }

  async function executeAction(actionId) {
    const contract = activeContract;
    if (!contract || !validateContract(contract)) return;
    const binding = contract.action_bindings.find((item) => item.id === actionId);
    if (!binding || binding.enabled !== true) return;
    const values = {};
    let invalid = false;
    for (const fieldId of binding.input_field_ids) {
      const control = fields.get(fieldId);
      if (!control) return;
      const value = fieldValue(fieldId);
      values[fieldId] = value;
      const required = binding.required_field_ids.includes(fieldId);
      const empty = !asText(value).trim();
      control.setAttribute("aria-invalid", required && empty ? "true" : "false");
      if (required && empty) invalid = true;
    }
    if (invalid) return;
    mount.querySelectorAll("[data-action-id]").forEach((button) => {
      button.disabled = true;
    });
    mount.dataset.state = "EXECUTING";
    const endpoint = contract.execution.endpoint_template.replace(
      "{contract_id}",
      encodeURIComponent(contract.id),
    );
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          action_id: actionId,
          perspective_id: contract.perspective_id,
          focus_event_id: contract.focus_event_id,
          values,
        }),
      });
      const payload = await response.json();
      if (response.status === 409) {
        await loadContract(contract.focus_event_id, contract.perspective_id);
        return;
      }
      const next = payload.closure_ui_contract
        || (payload.interface || {}).closure_ui_contract
        || (payload.detail || {}).closure_ui_contract;
      if (next) {
        renderContract(next);
        return;
      }
      mount.dataset.state = response.ok ? "OPEN" : "REJECTED";
    } catch (_error) {
      mount.dataset.state = "OPEN";
    } finally {
      mount.querySelectorAll("[data-action-id]").forEach((button) => {
        button.disabled = false;
      });
    }
  }

  async function bootstrap() {
    const current = new URL(window.location.href);
    try {
      await loadContract(
        current.searchParams.get("focus_event_id"),
        current.searchParams.get("perspective_id"),
      );
    } catch (_error) {
      mount.dataset.state = "OPEN";
    }
  }

  bootstrap();
})();
</script>
</body>
</html>
"""


__all__ = ["CLOSURE_ONLY_SUPERNET_HTML"]
