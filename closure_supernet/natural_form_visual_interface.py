from __future__ import annotations

"""Natural-form visual translation over the verified Supernet contract.

This module does not add a second semantic runtime and does not let rendering
witness equality.  It derives family-specific SVG geometry from the already
verified versioned atlas/local natural-form freedom field and the current finite
closure projection.  The same current relation paths are transformed through
all retained family render operators; LOCAL/GLOBAL/OPEN are derived from the
returned atlas graph, and local hair continuously changes which family charts
are visually foregrounded.

The visual operators are presentation translations only.  OPEN family layers
remain OPEN, pointer-inert, and cannot author cross-form equality.
"""

from .closure_only_interface import CLOSURE_ONLY_SUPERNET_HTML as _BASE_HTML


_CSS = r'''
  .natural-form-family-layer {
    pointer-events: none;
    transition: opacity 180ms linear;
  }
  .natural-form-family-path {
    fill: none;
    vector-effect: non-scaling-stroke;
  }
  .natural-form-family-fibre {
    fill: none;
    vector-effect: non-scaling-stroke;
  }
'''


_JS = r'''
  const naturalFormFamilyOperators = Object.freeze({
    INTERBOUND_PRE_DIRECTIONAL: "INTERBOUND_POLAR_RING_STRING",
    DIMENSIONAL_POINT_LINE_TRIANGLE: "DIMENSIONAL_TRIANGULARIZATION",
    SEAM_FOLD_BOUNDARY_INVERSION: "SEAM_FOLD_INVERSION",
    REFINEMENT_PATH_HIDDEN_TRAJECTORY: "REFINEMENT_SPIRAL_HIDDEN_PATH",
    BALL_HAIR: "BALL_HAIR_RADIAL_FIELD",
    MIRROR_OBSERVER_CONSCIOUS_INTERFACE: "MIRROR_ELLIPTIC_REFLECTION",
    SHEAF_TOPOS_LATTICE_ALGEBRA: "SHEAF_FIBRE_BUNDLE",
    CURVATURE_MAZE_LIGHTCONE_SUPERNET: "CURVATURE_LIGHTCONE_WARP",
    AI_TOKEN_MARKET_TRADING: "AI_TOKEN_RETURN_FLOW",
    PHYSICAL_COSMOLOGICAL_COLOR: "DUAL_CONE_HORIZON",
    RUNTIME_RELATIVE_NATURAL_FORM: "CURRENT_TRANSLATIONAL_PROJECTION",
  });

  function familyPhaseWeight(index, count) {
    if (!count) return 0;
    const phase = ((((localHairMillidegrees / 1000) % 360) + 360) % 360) / 360 * count;
    const raw = Math.abs(index - phase);
    const distance = Math.min(raw, count - raw);
    if (distance >= 2.25) return 0.05;
    if (distance >= 1.25) return 0.16;
    if (distance >= 0.55) return 0.42;
    return 1;
  }

  function familyRelativeRoles(contract) {
    const atlas = contract.natural_form_atlas;
    const projection = contract.projection || {};
    const chartById = new Map((atlas.charts || []).map((chart) => [asText(chart.id), chart]));
    const graph = new Map((atlas.charts || []).map((chart) => [asText(chart.id), new Set()]));
    for (const relation of atlas.translations || []) {
      if (!isRecord(relation) || relation.status !== "WITNESSED" || relation.kind === "IDENTITY") continue;
      const source = asText(relation.source_chart_id);
      const target = asText(relation.target_chart_id);
      if (!graph.has(source) || !graph.has(target)) continue;
      graph.get(source).add(target);
      graph.get(target).add(source);
    }
    const roots = new Set();
    for (const state of projection.states || []) {
      const chartId = atlas.runtime_state_to_chart?.[asText(state.id)];
      if (chartId && graph.has(chartId)) roots.add(chartId);
    }
    if (!roots.size) {
      for (const chart of atlas.charts || []) {
        if (chart.runtime_generated === true && graph.has(asText(chart.id))) roots.add(asText(chart.id));
      }
    }
    const distance = new Map();
    const queue = [];
    for (const root of roots) {
      distance.set(root, 0);
      queue.push(root);
    }
    while (queue.length) {
      const current = queue.shift();
      const nextDistance = distance.get(current) + 1;
      for (const neighbor of graph.get(current) || []) {
        if (!distance.has(neighbor)) {
          distance.set(neighbor, nextDistance);
          queue.push(neighbor);
        }
      }
    }
    const roles = new Map();
    const familyNames = [...new Set((contract.local_natural_form_freedom?.families || [])
      .map((row) => asText(row.family)).filter(Boolean))];
    for (const family of familyNames) {
      const candidates = (atlas.charts || [])
        .filter((chart) => chart.family === family && chart.runtime_generated !== true)
        .map((chart) => distance.get(asText(chart.id)))
        .filter((value) => Number.isInteger(value));
      if (!candidates.length) {
        roles.set(family, {role: "OPEN", distance: null});
        continue;
      }
      const d = Math.min(...candidates);
      roles.set(family, {role: d <= 1 ? "LOCAL" : "GLOBAL", distance: d});
    }
    return roles;
  }

  function transformNaturalFormPoint(family, point) {
    const x = Number(point?.[0] ?? 500);
    const y = Number(point?.[1] ?? 500);
    const dx = x - 500;
    const dy = y - 500;
    const r = Math.max(1, Math.hypot(dx, dy));
    const theta = Math.atan2(dy, dx);
    switch (family) {
      case "INTERBOUND_PRE_DIRECTIONAL": {
        const angle = ((x / 1000) * 2 - 1) * Math.PI;
        const radius = 105 + 0.72 * Math.abs(y - 500);
        return [500 + radius * Math.cos(angle), 500 + radius * Math.sin(angle)];
      }
      case "DIMENSIONAL_POINT_LINE_TRIANGLE": {
        const vertical = Math.max(0.14, 1 - Math.abs(dy) / 620);
        return [500 + dx * vertical, 500 + dy * 0.92 - Math.abs(dx) * 0.18];
      }
      case "SEAM_FOLD_BOUNDARY_INVERSION": {
        const side = dx < 0 ? -1 : 1;
        const folded = Math.abs(dx) * 0.62;
        return [500 + side * folded + 58 * Math.sin(y / 86), y + 26 * Math.sin(x / 73)];
      }
      case "REFINEMENT_PATH_HIDDEN_TRAJECTORY": {
        const twist = theta + r / 205;
        const radius = Math.min(455, 0.76 * r + 34 * Math.sin(r / 52));
        return [500 + radius * Math.cos(twist), 500 + radius * Math.sin(twist)];
      }
      case "BALL_HAIR": {
        const radius = 120 + Math.min(320, r * 0.58);
        return [500 + radius * Math.cos(theta), 500 + radius * Math.sin(theta)];
      }
      case "MIRROR_OBSERVER_CONSCIOUS_INTERFACE": {
        const ellipseX = 0.78 * dx;
        const ellipseY = 0.56 * dy;
        const mirror = dx >= 0 ? 1 : -1;
        return [500 + mirror * Math.abs(ellipseX), 500 + ellipseY + 28 * Math.sin(theta * 2)];
      }
      case "SHEAF_TOPOS_LATTICE_ALGEBRA": {
        const fibre = Math.round(dx / 82) * 82;
        return [500 + fibre + 17 * Math.sin(y / 64), 500 + dy * 0.88];
      }
      case "CURVATURE_MAZE_LIGHTCONE_SUPERNET": {
        const cone = Math.max(0.18, Math.abs(dy) / 500);
        const lens = 1 + 0.18 * Math.sin(theta * 3);
        return [500 + dx * cone * lens, 500 + dy * 0.92];
      }
      case "AI_TOKEN_MARKET_TRADING": {
        return [x + 72 * Math.sin(y / 112), y + 44 * Math.sin(x / 96)];
      }
      case "PHYSICAL_COSMOLOGICAL_COLOR": {
        const cone = Math.max(0.08, Math.abs(dy) / 500);
        return [500 + dx * cone, y];
      }
      default:
        return [x, y];
    }
  }

  function transformedQuadraticPath(family, points) {
    if (!Array.isArray(points) || points.length !== 3) return "";
    return projectedPath(points.map((point) => transformNaturalFormPoint(family, point)));
  }

  function renderNaturalFormAtlas(layer, contract, projection, visualization) {
    const localField = contract.local_natural_form_freedom;
    if (!isRecord(localField) || !Array.isArray(localField.families)) return;
    const requiredFamilies = Array.isArray(localField.local_constraint?.required_historical_family_ids)
      ? [...localField.local_constraint.required_historical_family_ids]
      : localField.families.map((row) => asText(row.family)).filter(Boolean);
    const roles = familyRelativeRoles(contract);
    const familyRows = new Map(localField.families.map((row) => [asText(row.family), row]));
    const fibreById = new Map((projection.equality_fibres || []).map((fibre) => [fibre.id, fibre]));
    const familyLayer = svgElement("g", {
      "data-natural-render": "CURRENT_TT_RELATIVE_FAMILY_MORPH",
      "data-selection-authors-truth": "false",
      "data-return-required-for-truth": "true",
    });
    layer.insertBefore(familyLayer, layer.firstChild);

    requiredFamilies.forEach((family, index) => {
      const row = familyRows.get(family);
      if (!row) return;
      const relative = roles.get(family) || {role: "OPEN", distance: null};
      const phaseWeight = familyPhaseWeight(index, requiredFamilies.length);
      const witnessed = row.status === "WITNESSED" && relative.role !== "OPEN";
      const roleOpacity = relative.role === "LOCAL" ? 0.64 : relative.role === "GLOBAL" ? 0.44 : 0.20;
      const opacity = Math.max(0.025, roleOpacity * phaseWeight);
      const hue = (index * 360 / Math.max(1, requiredFamilies.length)
        + (localHairMillidegrees / 1000)) % 360;
      const group = svgElement("g", {
        class: "natural-form-family-layer",
        opacity,
        "data-natural-form-family": family,
        "data-natural-form-operator": naturalFormFamilyOperators[family] || "CURRENT_TRANSLATIONAL_PROJECTION",
        "data-relative-role": relative.role,
        "data-return-distance": relative.distance === null ? "OPEN" : relative.distance,
        "data-family-status": row.status,
        "data-executes-as-equality": "false",
      });
      familyLayer.append(group);

      for (const relation of visualization.translation_primitives || []) {
        group.append(svgElement("path", {
          d: transformedQuadraticPath(family, relation.quadratic_path),
          class: "natural-form-family-path",
          stroke: `hsl(${hue} 70% 68%)`,
          "stroke-width": relative.role === "LOCAL" ? 2.2 : 1.35,
          "stroke-dasharray": witnessed ? "none" : "7 9",
          "data-source-relation-id": relation.relation_id,
          "data-source-equality": relation.executes_as_equality === true,
          "data-family-equality": "false",
        }));
      }
      for (const relation of visualization.potential_primitives || []) {
        group.append(svgElement("path", {
          d: transformedQuadraticPath(family, relation.quadratic_path),
          class: "natural-form-family-path",
          stroke: `hsl(${hue} 58% 62%)`,
          "stroke-width": 1,
          "stroke-dasharray": "3 10",
          "data-source-relation-id": relation.relation_id,
          "data-open-family-proposal": "true",
          "data-family-equality": "false",
        }));
      }
      for (const primitive of visualization.fibre_primitives || []) {
        if (!fibreById.has(primitive.natural_form_id)) continue;
        const [cx, cy] = transformNaturalFormPoint(family, primitive.centre);
        group.append(svgElement("circle", {
          cx,
          cy,
          r: Math.max(8, primitive.radius * (relative.role === "LOCAL" ? 0.34 : 0.22)),
          class: "natural-form-family-fibre",
          stroke: `hsl(${hue} 68% 70%)`,
          "stroke-width": relative.role === "LOCAL" ? 1.6 : 0.9,
          "stroke-dasharray": witnessed ? "none" : "4 8",
          "data-source-natural-form-id": primitive.natural_form_id,
          "data-family-equality": "false",
        }));
      }
    });

    layer.dataset.naturalRender = "CURRENT_TT_RELATIVE_FAMILY_MORPH";
    layer.dataset.naturalRenderFamilyCount = requiredFamilies.length;
    layer.dataset.naturalRenderHairDriven = "true";
    layer.dataset.naturalRenderSelectionAuthorsTruth = "false";
    layer.dataset.naturalRenderReturnRequired = "true";
  }
'''


def _inject(html: str) -> str:
    if "</style>" not in html:
        raise RuntimeError("natural-form renderer style target changed")
    if "  function render(contract) {\n" not in html:
        raise RuntimeError("natural-form renderer function target changed")
    call_target = "    renderLocalModification(chartLayer, focusPrimitive);\n"
    if call_target not in html:
        raise RuntimeError("natural-form renderer insertion target changed")
    result = html.replace("</style>", _CSS + "\n</style>", 1)
    result = result.replace("  function render(contract) {\n", _JS + "\n  function render(contract) {\n", 1)
    result = result.replace(
        call_target,
        "    renderNaturalFormAtlas(chartLayer, active, projection, visualization);\n" + call_target,
        1,
    )
    return result


NATURAL_FORM_SUPERNET_HTML = _inject(_BASE_HTML)

__all__ = ["NATURAL_FORM_SUPERNET_HTML"]
