from __future__ import annotations

"""Render the natural form solved by interactive interface equality closure.

The server and browser derive the same canonical solver receipt from the
verified closure partition, returned/OPEN relations, source-return history,
versioned chart constraints and current atlas distance.  There is one generic
bounded harmonic basis. No family switch or named geometry template exists.

Rendering remains presentation-only: every solved layer is pointer-inert and
cannot witness equality. Local hair changes the presentation phase without
changing the solver's closure source.
"""

from .closure_only_interface import CLOSURE_ONLY_SUPERNET_HTML as _BASE_HTML


_CSS = r'''
  .natural-form-family-layer {
    pointer-events: none;
    transition: opacity 180ms linear;
  }
  .natural-form-family-path,
  .natural-form-family-fibre {
    fill: none;
    vector-effect: non-scaling-stroke;
  }
'''


_JS = r'''
  const interactiveNaturalFormSemanticFields = Object.freeze([
    "carrier", "standpoint", "boundary", "inversion", "paths",
    "return", "domain", "version", "semantic_role",
  ]);

  function solverUniqueSorted(values) {
    return unique(values).sort(compareUnicodeCodePoints);
  }

  function solverRoundRatioMilli(numerator, denominator) {
    if (!Number.isInteger(denominator) || denominator <= 0) return 0;
    return Math.floor((1000 * numerator + Math.floor(denominator / 2)) / denominator);
  }

  function solverNormalizeKernel(value) {
    if (!Array.isArray(value)) return [];
    const groups = [];
    const seen = new Set();
    for (const raw of value) {
      if (!Array.isArray(raw)) return [];
      const members = solverUniqueSorted(raw);
      if (!members.length || members.some((member) => seen.has(member))) return [];
      members.forEach((member) => seen.add(member));
      groups.push(members);
    }
    return groups.sort((left, right) => {
      const length = Math.min(left.length, right.length);
      for (let index = 0; index < length; index += 1) {
        const order = compareUnicodeCodePoints(left[index], right[index]);
        if (order !== 0) return order;
      }
      return left.length - right.length;
    });
  }

  function solverComponentCount(nodes, edges) {
    if (!nodes.length) return 0;
    const graph = new Map(nodes.map((node) => [node, new Set()]));
    for (const [source, target] of edges) {
      if (graph.has(source) && graph.has(target)) {
        graph.get(source).add(target);
        graph.get(target).add(source);
      }
    }
    const unseen = new Set(nodes);
    let count = 0;
    while (unseen.size) {
      count += 1;
      const root = [...unseen].sort(compareUnicodeCodePoints)[0];
      unseen.delete(root);
      const queue = [root];
      while (queue.length) {
        const current = queue.shift();
        for (const neighbour of [...graph.get(current)].sort(compareUnicodeCodePoints)) {
          if (unseen.has(neighbour)) {
            unseen.delete(neighbour);
            queue.push(neighbour);
          }
        }
      }
    }
    return count;
  }

  async function deriveInteractiveEqualityClosureSignature(contract) {
    const projection = isRecord(contract.projection) ? contract.projection : {};
    const closure = isRecord(contract.perspective_closure)
      ? contract.perspective_closure : {};

    const states = (projection.states || []).filter(isRecord)
      .filter((raw) => raw.id)
      .map((raw) => ({
        id: asText(raw.id),
        event_id: asText(raw.event_id),
        display_fibre_id: asText(raw.display_fibre_id),
        source_return_ids: solverUniqueSorted(raw.source_return_ids || []),
      })).sort((left, right) => compareUnicodeCodePoints(left.id, right.id));
    const stateIds = states.map((item) => item.id);

    const fibres = (projection.equality_fibres || []).filter(isRecord)
      .filter((raw) => raw.id)
      .map((raw) => ({
        id: asText(raw.id),
        member_state_ids: solverUniqueSorted(raw.member_state_ids || []),
        source_return_ids: solverUniqueSorted(raw.source_return_ids || []),
      })).sort((left, right) => compareUnicodeCodePoints(left.id, right.id));

    const witnessedEdges = [];
    const translations = (projection.translations || []).filter(isRecord)
      .filter((raw) => raw.id)
      .map((raw) => {
        const item = {
          id: asText(raw.id),
          source_state_id: asText(raw.source_state_id),
          target_state_id: asText(raw.target_state_id),
          relation_status: asText(raw.relation_status),
          executes_as_equality: raw.executes_as_equality === true,
        };
        if (item.relation_status === "WITNESSED"
            && item.source_state_id && item.target_state_id) {
          witnessedEdges.push([item.source_state_id, item.target_state_id]);
        }
        return item;
      }).sort((left, right) => compareUnicodeCodePoints(left.id, right.id));

    const potentials = (projection.potentials || []).filter(isRecord)
      .filter((raw) => raw.id)
      .map((raw) => ({
        id: asText(raw.id),
        source_state_id: asText(raw.source_state_id),
        target_state_id: raw.target_state_id === null || raw.target_state_id === undefined
          ? null : asText(raw.target_state_id),
        relation_status: asText(raw.relation_status),
        executes_as_equality: raw.executes_as_equality === true,
      })).sort((left, right) => compareUnicodeCodePoints(left.id, right.id));

    const componentCount = solverComponentCount(stateIds, witnessedEdges);
    const witnessedCount = translations.filter(
      (item) => item.relation_status === "WITNESSED",
    ).length;
    const openCount = translations.filter(
      (item) => item.relation_status !== "WITNESSED",
    ).length + potentials.length;
    const relationCount = witnessedCount + openCount;
    const sourceReturnIds = solverUniqueSorted(contract.source_return_ids || []);
    const partitionProfile = fibres.map((item) => item.member_state_ids.length)
      .sort((left, right) => left - right);
    const loopRank = Math.max(0, witnessedCount - stateIds.length + componentCount);

    const body = {
      status: asText(contract.status || "OPEN"),
      perspective_id: asText(contract.perspective_id),
      focus_event_id: asText(contract.focus_event_id),
      closure_equation_system_id: asText(contract.closure_naturality_equations?.id),
      states,
      fibres,
      translations,
      potentials,
      kernel: solverNormalizeKernel(closure.kernel || []),
      source_return_ids: sourceReturnIds,
      continuation_lineage_ids: (contract.continuation_lineage_ids || []).map(asText),
      state_count: states.length,
      fibre_count: fibres.length,
      partition_profile: partitionProfile,
      witnessed_relation_count: witnessedCount,
      open_relation_count: openCount,
      relation_count: relationCount,
      component_count: componentCount,
      loop_rank: loopRank,
      partition_density_milli: solverRoundRatioMilli(fibres.length, states.length),
      return_density_milli: solverRoundRatioMilli(
        sourceReturnIds.length, Math.max(1, states.length + sourceReturnIds.length),
      ),
      open_density_milli: solverRoundRatioMilli(openCount, Math.max(1, relationCount)),
    };
    return {...body, id: await digest("interactive-equality-closure", body)};
  }

  function solverAtlasGraph(atlas) {
    const chartIds = new Set((atlas.charts || []).filter(isRecord)
      .map((chart) => asText(chart.id)).filter(Boolean));
    const graph = new Map([...chartIds].map((id) => [id, new Set()]));
    for (const relation of atlas.translations || []) {
      if (!isRecord(relation)
          || relation.status !== "WITNESSED"
          || relation.kind === "IDENTITY") continue;
      const source = asText(relation.source_chart_id);
      const target = asText(relation.target_chart_id);
      if (graph.has(source) && graph.has(target)) {
        graph.get(source).add(target);
        graph.get(target).add(source);
      }
    }
    return graph;
  }

  function solverFamilyRelativeRoles(contract, atlas, localField) {
    const graph = solverAtlasGraph(atlas);
    const projection = isRecord(contract.projection) ? contract.projection : {};
    const stateToChart = isRecord(atlas.runtime_state_to_chart)
      ? atlas.runtime_state_to_chart : {};
    const roots = new Set();
    for (const state of projection.states || []) {
      if (!isRecord(state)) continue;
      const chartId = asText(stateToChart[asText(state.id)]);
      if (chartId && graph.has(chartId)) roots.add(chartId);
    }
    if (!roots.size) {
      for (const chart of atlas.charts || []) {
        if (isRecord(chart) && chart.runtime_generated === true
            && graph.has(asText(chart.id))) roots.add(asText(chart.id));
      }
    }
    const distance = new Map();
    const queue = [];
    for (const root of [...roots].sort(compareUnicodeCodePoints)) {
      distance.set(root, 0);
      queue.push(root);
    }
    while (queue.length) {
      const current = queue.shift();
      const nextDistance = distance.get(current) + 1;
      for (const neighbour of [...(graph.get(current) || [])].sort(compareUnicodeCodePoints)) {
        if (!distance.has(neighbour)) {
          distance.set(neighbour, nextDistance);
          queue.push(neighbour);
        }
      }
    }
    const roles = new Map();
    const rows = (localField.families || []).filter(isRecord)
      .sort((left, right) => compareUnicodeCodePoints(asText(left.family), asText(right.family)));
    for (const row of rows) {
      const family = asText(row.family);
      const candidates = (atlas.charts || []).filter(isRecord)
        .filter((chart) => asText(chart.family) === family
          && chart.runtime_generated !== true
          && distance.has(asText(chart.id)))
        .map((chart) => distance.get(asText(chart.id)));
      if (!candidates.length) roles.set(family, {role: "OPEN", distance: null});
      else {
        const minimum = Math.min(...candidates);
        roles.set(family, {role: minimum <= 1 ? "LOCAL" : "GLOBAL", distance: minimum});
      }
    }
    return roles;
  }

  function solverSemanticConstraints(family, atlas) {
    const constraints = new Map();
    for (const chart of atlas.charts || []) {
      if (!isRecord(chart) || asText(chart.family) !== family) continue;
      const row = Object.create(null);
      for (const field of interactiveNaturalFormSemanticFields) {
        if (chart[field] !== null && chart[field] !== undefined) row[field] = chart[field];
      }
      constraints.set(stable(row), row);
    }
    return [...constraints.keys()].sort(compareUnicodeCodePoints)
      .map((key) => constraints.get(key));
  }

  function solverSeedByte(seed, index) {
    const offset = (index * 2) % seed.length;
    return Number.parseInt(seed.slice(offset, offset + 2), 16);
  }

  function solverCoefficients(seedHex, equality, role, distance) {
    const partitionDensity = Number(equality.partition_density_milli || 0);
    const returnDensity = Number(equality.return_density_milli || 0);
    const openDensity = Number(equality.open_density_milli || 0);
    const fibreCount = Number(equality.fibre_count || 0);
    const loopRank = Number(equality.loop_rank || 0);
    const roleGain = role === "LOCAL" ? 1000 : role === "GLOBAL" ? 760 : 520;
    const distanceGain = distance === null
      ? 1000 : Math.max(420, 1000 - 95 * distance);
    const coefficients = {
      angle_millidegrees: Number.parseInt(seedHex.slice(0, 8), 16) % 360000,
      phase_millidegrees: Number.parseInt(seedHex.slice(8, 16), 16) % 360000,
      stretch_x_milli: 720 + (solverSeedByte(seedHex, 8) % 561),
      stretch_y_milli: 720 + (solverSeedByte(seedHex, 9) % 561),
      shear_x_milli: (solverSeedByte(seedHex, 10) - 128) * 2,
      shear_y_milli: (solverSeedByte(seedHex, 11) - 128) * 2,
      harmonic_order: 1 + (solverSeedByte(seedHex, 6) % 7) + (fibreCount % 3),
      radial_milli: Math.min(320,
        24 + (solverSeedByte(seedHex, 12) % 177)
        + Math.floor(partitionDensity / 12) + Math.min(56, loopRank * 7)),
      twist_milli: (solverSeedByte(seedHex, 13) - 128) * 2
        + Math.floor((openDensity - 500) / 8),
      fold_milli: (solverSeedByte(seedHex, 14) - 128)
        + Math.floor((partitionDensity - 500) / 10),
      cross_milli: (solverSeedByte(seedHex, 15) - 128)
        + Math.floor((returnDensity - 500) / 12),
      boundary_gain_milli: 620 + (solverSeedByte(seedHex, 16) % 881),
      open_aperture_milli: Math.min(300,
        20 + (solverSeedByte(seedHex, 17) % 121) + Math.floor(openDensity / 8)),
      return_pull_milli: Math.min(260,
        18 + (solverSeedByte(seedHex, 18) % 113) + Math.floor(returnDensity / 8)),
      hair_coupling_milli: 250 + (solverSeedByte(seedHex, 19) % 751),
      role_gain_milli: roleGain,
      distance_gain_milli: distanceGain,
      determinant_floor_million: 450000,
    };
    coefficients.linear_determinant_million =
      coefficients.stretch_x_milli * coefficients.stretch_y_milli
      - coefficients.shear_x_milli * coefficients.shear_y_milli;
    return coefficients;
  }

  async function deriveInteractiveNaturalFormSolver(contract) {
    const atlas = isRecord(contract.natural_form_atlas) ? contract.natural_form_atlas : {};
    const localField = isRecord(contract.local_natural_form_freedom)
      ? contract.local_natural_form_freedom : {};
    const equality = await deriveInteractiveEqualityClosureSignature(contract);
    const roles = solverFamilyRelativeRoles(contract, atlas, localField);
    const rows = (localField.families || []).filter(isRecord)
      .sort((left, right) => compareUnicodeCodePoints(asText(left.family), asText(right.family)));
    const solutions = [];
    for (const row of rows) {
      const family = asText(row.family);
      const relative = roles.get(family) || {role: "OPEN", distance: null};
      const constraints = solverSemanticConstraints(family, atlas);
      const semanticBody = {
        semantic_constraints: constraints,
        relative_role: relative.role,
        return_distance: relative.distance,
        family_status: asText(row.status || "OPEN"),
        empirical_return_required: row.empirical_return_required === true,
        equality_closure_id: equality.id,
      };
      const semanticConstraintId = await digest("natural-form-constraints", semanticBody);
      const seedHex = await sha256Hex(stable(semanticBody));
      const coefficients = solverCoefficients(
        seedHex, equality, relative.role, relative.distance,
      );
      const solution = {
        family_id: family,
        family_status: asText(row.status || "OPEN"),
        relative_role: relative.role,
        return_distance: relative.distance,
        semantic_constraint_id: semanticConstraintId,
        semantic_constraints: constraints,
        solver_basis: "GENERIC_BOUNDED_HARMONIC_EQUALITY_CLOSURE_BASIS",
        coefficients,
        constraints: {
          origin_fixed: true,
          bounded_on_viewbox: true,
          linear_invertibility_required: true,
          linear_invertibility_witnessed:
            coefficients.linear_determinant_million >= coefficients.determinant_floor_million,
          source_relation_paths_preserved: true,
          equality_partition_source: equality.id,
          family_name_used_as_geometry_selector: false,
          visual_resemblance_used_as_geometry_selector: false,
          named_geometry_template_present: false,
          rendering_executes_as_equality: false,
          selection_authors_truth: false,
          return_required_for_truth_refinement: true,
        },
      };
      solution.id = await digest("natural-form-solution", solution);
      solutions.push(solution);
    }
    const body = {
      protocol: "SUPERNET-INTERACTIVE-NATURAL-FORM-SOLVER",
      schema: "closure.supernet/interactive-natural-form-solver-v1",
      atlas_id: atlas.id,
      local_natural_form_freedom_id: localField.id,
      active_perspective_id: asText(contract.perspective_id),
      equality_closure_signature: equality,
      solver_kind: "CANONICAL_CONSTRAINT_SOLUTION_OVER_INTERACTIVE_EQUALITY_CLOSURE",
      basis_terms: [
        "INVERTIBLE_LINEAR_RELATIVE_CHART",
        "PARTITION_DENSITY_RADIAL_HARMONIC",
        "RETURN_DENSITY_SOURCE_PULL",
        "OPEN_DENSITY_APERTURE",
        "LOOP_RANK_TWIST",
        "PERSPECTIVE_HAIR_PHASE",
      ],
      semantic_constraint_fields: [...interactiveNaturalFormSemanticFields],
      solutions,
      solution_count: solutions.length,
      natural_form_is_interactive_interface_equality_closure: true,
      natural_form_is_posthoc_visual_template: false,
      family_switch_present: false,
      named_geometry_templates_present: false,
      family_name_authors_geometry: false,
      visual_resemblance_authors_geometry: false,
      rendering_can_witness_equality: false,
      hair_changes_presentation_not_truth: true,
      only_return_refines_equality_closure: true,
      truth_issued: false,
      existence_closed: false,
    };
    return {...body, id: await digest("interactive-natural-form-solver", body)};
  }

  async function interactiveNaturalFormSolverMatches(contract) {
    const supplied = contract?.interactive_natural_form_solver;
    if (!isRecord(supplied)) return false;
    const expected = await deriveInteractiveNaturalFormSolver(contract);
    if (stable(supplied) !== stable(expected)) return false;
    if (supplied.natural_form_is_interactive_interface_equality_closure !== true
        || supplied.natural_form_is_posthoc_visual_template !== false
        || supplied.family_switch_present !== false
        || supplied.named_geometry_templates_present !== false
        || supplied.family_name_authors_geometry !== false
        || supplied.visual_resemblance_authors_geometry !== false
        || supplied.rendering_can_witness_equality !== false
        || supplied.hair_changes_presentation_not_truth !== true
        || supplied.only_return_refines_equality_closure !== true) return false;
    return supplied.solutions.every((solution) => isRecord(solution)
      && solution.constraints?.linear_invertibility_witnessed === true
      && solution.constraints?.family_name_used_as_geometry_selector === false
      && solution.constraints?.named_geometry_template_present === false
      && solution.constraints?.rendering_executes_as_equality === false);
  }

  function solvedFamilyPhaseWeight(index, count) {
    if (!count) return 0;
    const phase = ((((localHairMillidegrees / 1000) % 360) + 360) % 360) / 360 * count;
    const raw = Math.abs(index - phase);
    const distance = Math.min(raw, count - raw);
    if (distance >= 2.25) return 0.05;
    if (distance >= 1.25) return 0.16;
    if (distance >= 0.55) return 0.42;
    return 1;
  }

  function solveNaturalFormPoint(solution, point) {
    const c = solution.coefficients;
    let x = (Number(point?.[0] ?? 500) - 500) / 500;
    let y = (Number(point?.[1] ?? 500) - 500) / 500;
    const origin = Math.abs(x) < 1e-15 && Math.abs(y) < 1e-15;
    const sx = c.stretch_x_milli / 1000;
    const sy = c.stretch_y_milli / 1000;
    const shx = c.shear_x_milli / 1000;
    const shy = c.shear_y_milli / 1000;
    const u0 = sx * x + shx * y;
    const v0 = shy * x + sy * y;
    const hair = localHairMillidegrees / 1000 * Math.PI / 180;
    let angle = c.angle_millidegrees / 1000 * Math.PI / 180;
    angle += hair * c.hair_coupling_milli / 1000;
    const ca = Math.cos(angle);
    const sa = Math.sin(angle);
    const u = ca * u0 - sa * v0;
    const v = sa * u0 + ca * v0;
    const radius = Math.hypot(u, v);
    const theta = Math.atan2(v, u);
    const phase = c.phase_millidegrees / 1000 * Math.PI / 180;
    const harmonic = Math.sin(c.harmonic_order * theta + phase + hair);
    const radial = 1 + c.radial_milli / 1000 * harmonic * Math.min(1, radius);
    const twist = c.twist_milli / 1000 * radius * radius;
    const boundary = c.boundary_gain_milli / 1000;
    const fold = c.fold_milli / 1000 * Math.tanh(boundary * u);
    const cross = c.cross_milli / 1000 * Math.tanh(boundary * v);
    const aperture = c.open_aperture_milli / 1000;
    const sourcePull = c.return_pull_milli / 1000;
    const gain = c.role_gain_milli * c.distance_gain_milli / 1000000;
    const theta2 = theta + twist * Math.min(1.25, radius);
    const rr = Math.min(1.38, Math.max(0, radius * radial));
    let solvedX = gain * (rr * Math.cos(theta2) + fold
      + aperture * Math.sin((c.harmonic_order + 1) * theta));
    let solvedY = gain * (rr * Math.sin(theta2) + cross
      - sourcePull * Math.cos((c.harmonic_order + 1) * theta));
    if (origin) { solvedX = 0; solvedY = 0; }
    return [
      Math.min(980, Math.max(20, 500 + 420 * solvedX)),
      Math.min(980, Math.max(20, 500 + 420 * solvedY)),
    ];
  }

  function solvedQuadraticPath(solution, points) {
    if (!Array.isArray(points) || points.length !== 3) return "";
    return projectedPath(points.map((point) => solveNaturalFormPoint(solution, point)));
  }

  function renderNaturalFormAtlas(layer, contract, projection, visualization) {
    const solver = contract.interactive_natural_form_solver;
    if (!isRecord(solver) || !Array.isArray(solver.solutions)) return;
    const fibreById = new Map((projection.equality_fibres || [])
      .map((fibre) => [fibre.id, fibre]));
    const familyLayer = svgElement("g", {
      "data-natural-render": "INTERACTIVE_EQUALITY_CLOSURE_SOLVER",
      "data-natural-form-is-interface-equality-closure": "true",
      "data-family-switch-present": "false",
      "data-named-geometry-template-present": "false",
      "data-rendering-can-witness-equality": "false",
      "data-return-required-for-truth": "true",
    });
    layer.insertBefore(familyLayer, layer.firstChild);

    solver.solutions.forEach((solution, index) => {
      const phaseWeight = solvedFamilyPhaseWeight(index, solver.solutions.length);
      const role = solution.relative_role;
      const witnessed = solution.family_status === "WITNESSED" && role !== "OPEN";
      const roleOpacity = role === "LOCAL" ? 0.64 : role === "GLOBAL" ? 0.44 : 0.20;
      const opacity = Math.max(0.025, roleOpacity * phaseWeight);
      const hue = ((solution.coefficients.angle_millidegrees / 1000)
        + (localHairMillidegrees / 1000) + 360) % 360;
      const group = svgElement("g", {
        class: "natural-form-family-layer",
        opacity,
        "data-natural-form-family": solution.family_id,
        "data-natural-form-solution-id": solution.id,
        "data-semantic-constraint-id": solution.semantic_constraint_id,
        "data-solver-basis": solution.solver_basis,
        "data-relative-role": role,
        "data-return-distance": solution.return_distance === null ? "OPEN" : solution.return_distance,
        "data-family-status": solution.family_status,
        "data-executes-as-equality": "false",
      });
      familyLayer.append(group);

      for (const relation of visualization.translation_primitives || []) {
        group.append(svgElement("path", {
          d: solvedQuadraticPath(solution, relation.quadratic_path),
          class: "natural-form-family-path",
          stroke: `hsl(${hue} 70% 68%)`,
          "stroke-width": role === "LOCAL" ? 2.2 : 1.35,
          "stroke-dasharray": witnessed ? "none" : "7 9",
          "data-source-relation-id": relation.relation_id,
          "data-source-equality": relation.executes_as_equality === true,
          "data-family-equality": "false",
        }));
      }
      for (const relation of visualization.potential_primitives || []) {
        group.append(svgElement("path", {
          d: solvedQuadraticPath(solution, relation.quadratic_path),
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
        const [cx, cy] = solveNaturalFormPoint(solution, primitive.centre);
        group.append(svgElement("circle", {
          cx,
          cy,
          r: Math.max(8, primitive.radius * (role === "LOCAL" ? 0.34 : 0.22)),
          class: "natural-form-family-fibre",
          stroke: `hsl(${hue} 68% 70%)`,
          "stroke-width": role === "LOCAL" ? 1.6 : 0.9,
          "stroke-dasharray": witnessed ? "none" : "4 8",
          "data-source-natural-form-id": primitive.natural_form_id,
          "data-family-equality": "false",
        }));
      }
    });

    layer.dataset.naturalRender = "INTERACTIVE_EQUALITY_CLOSURE_SOLVER";
    layer.dataset.naturalRenderSolutionCount = solver.solution_count;
    layer.dataset.naturalRenderHairDriven = "true";
    layer.dataset.naturalFormIsInterfaceEqualityClosure = "true";
    layer.dataset.naturalRenderFamilySwitchPresent = "false";
    layer.dataset.naturalRenderSelectionAuthorsTruth = "false";
    layer.dataset.naturalRenderReturnRequired = "true";
  }
'''


def _inject(html: str) -> str:
    if "</style>" not in html:
        raise RuntimeError("natural-form solver style target changed")
    if "  function render(contract) {\n" not in html:
        raise RuntimeError("natural-form solver function target changed")
    call_target = "    renderLocalModification(chartLayer, focusPrimitive);\n"
    if call_target not in html:
        raise RuntimeError("natural-form solver insertion target changed")
    verify_target = "      if (!validate(contract)\n"
    if verify_target not in html:
        raise RuntimeError("natural-form solver verification target changed")
    result = html.replace("</style>", _CSS + "\n</style>", 1)
    result = result.replace("  function render(contract) {\n", _JS + "\n  function render(contract) {\n", 1)
    result = result.replace(
        verify_target,
        verify_target + "          || !await interactiveNaturalFormSolverMatches(contract)\n",
        1,
    )
    result = result.replace(
        call_target,
        "    renderNaturalFormAtlas(chartLayer, active, projection, visualization);\n" + call_target,
        1,
    )
    return result


NATURAL_FORM_SUPERNET_HTML = _inject(_BASE_HTML)

__all__ = ["NATURAL_FORM_SUPERNET_HTML"]
