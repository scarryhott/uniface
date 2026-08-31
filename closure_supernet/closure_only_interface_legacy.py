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
.local-potential-shell {
  fill: rgba(255,255,255,.01);
  stroke-width: 1.4;
  stroke-dasharray: 3 8;
  vector-effect: non-scaling-stroke;
}
.local-potential-path {
  fill: none;
  stroke-width: 1.3;
  stroke-dasharray: 3 8;
  vector-effect: non-scaling-stroke;
  opacity: .72;
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
  const schema = "closure.supernet/translational-visualization-v6";
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
  let localHairMillidegrees = 0;
  const verifiedContracts = new WeakSet();
  const locallyDerivedVisualizations = new WeakMap();

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

  function compareUnicodeCodePoints(left, right) {
    const a = Array.from(asText(left), (item) => item.codePointAt(0));
    const b = Array.from(asText(right), (item) => item.codePointAt(0));
    const length = Math.min(a.length, b.length);
    for (let index = 0; index < length; index += 1) {
      if (a[index] !== b[index]) return a[index] - b[index];
    }
    return a.length - b.length;
  }

  function sameMembers(left, right) {
    const a = unique(left).sort(compareUnicodeCodePoints);
    const b = unique(right).sort(compareUnicodeCodePoints);
    return a.length === b.length && a.every((item, index) => item === b[index]);
  }

  function stable(value) {
    if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
    if (value && typeof value === "object") {
      return `{${Object.keys(value).sort(compareUnicodeCodePoints).map((key) =>
        `${JSON.stringify(key)}:${stable(value[key])}`
      ).join(",")}}`;
    }
    return JSON.stringify(value);
  }

  async function contractIdMatchesContent(contract) {
    if (!contract || !crypto.subtle || typeof TextEncoder === "undefined") return false;
    const body = Object.create(null);
    for (const [key, value] of Object.entries(contract)) {
      if (key !== "id") body[key] = value;
    }
    const digest = await crypto.subtle.digest(
      "SHA-256",
      new TextEncoder().encode(stable(body)),
    );
    const hexadecimal = [...new Uint8Array(digest)]
      .map((value) => value.toString(16).padStart(2, "0"))
      .join("");
    return contract.id === `translational-visualization:${hexadecimal.slice(0, 24)}`;
  }

  async function sha256Hex(value) {
    const digest = await crypto.subtle.digest(
      "SHA-256", new TextEncoder().encode(value),
    );
    return [...new Uint8Array(digest)]
      .map((item) => item.toString(16).padStart(2, "0")).join("");
  }

  async function digest(prefix, value) {
    return `${prefix}:${(await sha256Hex(stable(value))).slice(0, 24)}`;
  }

  function rounded(value) {
    return Number(value.toFixed(6));
  }

  function visualSignature(fibre, stateById) {
    const members = (fibre.member_state_ids || [])
      .map((id) => stateById.get(asText(id))).filter(Boolean);
    return stable({
      display: unique(fibre.display_fibre_ids).sort(compareUnicodeCodePoints),
      source: members.map((item) => asText(item.source_trace))
        .sort(compareUnicodeCodePoints),
      source_returns: unique(members.flatMap((item) => item.source_return_ids || []))
        .sort(compareUnicodeCodePoints),
    });
  }

  async function hue(signature) {
    return Number.parseInt((await sha256Hex(signature)).slice(0, 8), 16) % 360;
  }

  async function locallyDeriveVisualization(contract) {
    const projection = contract.projection;
    const stateById = new Map(projection.states.map((item) => [asText(item.id), item]));
    const decorated = await Promise.all(projection.equality_fibres.map(async (fibre) => ({
      fibre,
      signature: visualSignature(fibre, stateById),
    })));
    decorated.sort((left, right) => {
      const leftFocus = asText(left.fibre.id) === asText(contract.return_relation?.parent_natural_form_id) ? 0 : 1;
      const rightFocus = asText(right.fibre.id) === asText(contract.return_relation?.parent_natural_form_id) ? 0 : 1;
      return leftFocus - rightFocus || compareUnicodeCodePoints(left.signature, right.signature);
    });
    const focusId = contract.return_relation?.parent_natural_form_id || null;
    const count = decorated.length;
    const orbit = Math.min(338, 172 + Math.max(0, count - 2) * 18);
    const peripheralCount = Math.max(1, count - (focusId ? 1 : 0));
    let peripheralIndex = 0;
    const positions = new Map();
    const fibrePrimitives = [];
    for (const {fibre, signature} of decorated) {
      const fibreId = asText(fibre.id);
      const focused = fibreId === asText(focusId);
      let x = 500;
      let y = 500;
      let parameter = 0;
      if (!focused && count !== 1) {
        const phase = (2 * Math.PI * peripheralIndex / peripheralCount) - Math.PI / 2;
        peripheralIndex += 1;
        parameter = Math.tan(phase / 2);
        x = 500 + orbit * Math.cos(phase);
        y = 500 + orbit * .72 * Math.sin(phase);
      }
      const members = (fibre.member_state_ids || [])
        .map((stateId) => stateById.get(asText(stateId))).filter(Boolean);
      const sourceExtent = members.reduce(
        (total, member) => total + Array.from(asText(member.source_trace)).length,
        0,
      );
      const radius = Math.min(190, Math.max(
        72,
        54 + Math.sqrt(Math.max(1, (fibre.member_state_ids || []).length)) * 18,
        60 + Math.sqrt(Math.max(1, sourceExtent)) * 7,
      ));
      fibrePrimitives.push({
        natural_form_id: fibreId,
        centre: [rounded(x), rounded(y)],
        radius: rounded(radius),
        projective_parameter: Number.isFinite(parameter) ? rounded(parameter) : "INFINITY",
        hue: await hue(signature),
        focused,
        source_state_ids: [...(fibre.member_state_ids || [])],
        source_return_ids: [...(fibre.source_return_ids || [])],
        derivation: fibre.derivation,
      });
      positions.set(fibreId, {x, y});
    }
    const formByState = new Map();
    for (const fibre of projection.equality_fibres) {
      for (const stateId of fibre.member_state_ids || []) formByState.set(asText(stateId), asText(fibre.id));
    }
    const pathBetween = (sourceForm, targetForm) => {
      const source = positions.get(sourceForm);
      const target = positions.get(targetForm);
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const length = Math.max(1, Math.hypot(dx, dy));
      const bend = Math.min(86, length * .18);
      return [[rounded(source.x), rounded(source.y)], [
        rounded((source.x + target.x) / 2 - dy / length * bend),
        rounded((source.y + target.y) / 2 + dx / length * bend),
      ], [rounded(target.x), rounded(target.y)]];
    };
    const translationPrimitives = [];
    for (const relation of projection.translations) {
      const sourceForm = formByState.get(asText(relation.source_state_id));
      const targetForm = formByState.get(asText(relation.target_state_id));
      if (!positions.has(sourceForm) || !positions.has(targetForm)) continue;
      translationPrimitives.push({
        relation_id: relation.id,
        source_natural_form_id: sourceForm,
        target_natural_form_id: targetForm,
        quadratic_path: pathBetween(sourceForm, targetForm),
        executes_as_equality: relation.executes_as_equality === true,
        hue: await hue(`${sourceForm}\u2192${targetForm}`),
        derivation: relation.derivation,
      });
    }
    const focusForm = positions.has(asText(focusId))
      ? asText(focusId) : (decorated.length ? asText(decorated[0].fibre.id) : "");
    const focusPosition = positions.get(focusForm) || {x: 500, y: 500};
    const potentialPrimitives = [];
    for (const relation of projection.potentials) {
      const targetFormValue = formByState.get(asText(relation.target_state_id));
      const targetForm = targetFormValue === undefined ? null : targetFormValue;
      let points;
      if (targetForm !== null && positions.has(targetForm)) {
        points = pathBetween(focusForm, targetForm);
      } else {
        const signature = stable({
          relation: relation.id,
          natural_form: relation.shared_natural_form_id,
          source_returns: relation.derivation?.source_return_ids || [],
        });
        const phase = 2 * Math.PI * (await hue(signature) / 360);
        const targetX = 500 + 455 * Math.cos(phase);
        const targetY = 500 + 455 * Math.sin(phase);
        const dx = targetX - focusPosition.x;
        const dy = targetY - focusPosition.y;
        const length = Math.max(1, Math.hypot(dx, dy));
        const bend = Math.min(86, length * .18);
        points = [[rounded(focusPosition.x), rounded(focusPosition.y)], [
          rounded((focusPosition.x + targetX) / 2 - dy / length * bend),
          rounded((focusPosition.y + targetY) / 2 + dx / length * bend),
        ], [rounded(targetX), rounded(targetY)]];
      }
      potentialPrimitives.push({
        relation_id: relation.id,
        source_natural_form_id: focusForm || null,
        target_natural_form_id: targetForm,
        quadratic_path: points,
        hue: await hue(asText(relation.id)),
        derivation: relation.derivation,
      });
    }
    const withoutDerivation = (items) => items.map((item) => Object.fromEntries(
      Object.entries(item).filter(([key]) => key !== "derivation"),
    ));
    const stateBasis = projection.states.map((item) => Object.fromEntries(
      Object.entries(item).filter(([key]) => key !== "derivation" && key !== "source_trace"),
    ));
    const relationDigest = await digest("projection-relation", {
      reading: projection.reading,
      states: stateBasis,
      equality_fibres: withoutDerivation(projection.equality_fibres),
      translations: withoutDerivation(projection.translations),
      potentials: withoutDerivation(projection.potentials),
    });
    return {
      operator: "PERSPECTIVE_RELATION_PROJECTIVE_FOLD",
      axiometry: {
        finite_pole: 0,
        projective_seam: "tan(pi/2)=infinity",
        fold: "RP1_TO_VISUAL_ORBIT",
        one_primitive_per_equality_fibre: true,
      },
      view_box: [0, 0, 1000, 1000],
      fibre_primitives: fibrePrimitives,
      translation_primitives: translationPrimitives,
      potential_primitives: potentialPrimitives,
      derivation: projection.visualization.derivation,
      relation_digest: relationDigest,
    };
  }

  async function visualizationMatches(contract) {
    const local = await locallyDeriveVisualization(contract);
    locallyDerivedVisualizations.set(contract, local);
    if (stable(local) !== stable(contract.projection.visualization)) return false;
    return true;
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

  function isRecord(value) {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
  }

  function owns(value, key) {
    return isRecord(value) && Object.prototype.hasOwnProperty.call(value, key);
  }

  function exactStringList(value, allowEmpty = false) {
    if (!Array.isArray(value)) return null;
    if (value.some((item) => typeof item !== "string" || !item)) return null;
    if (!allowEmpty && value.length === 0) return null;
    if (new Set(value).size !== value.length) return null;
    return [...value];
  }

  function compareStringArrays(left, right) {
    const length = Math.min(left.length, right.length);
    for (let index = 0; index < length; index += 1) {
      const order = compareUnicodeCodePoints(left[index], right[index]);
      if (order !== 0) return order;
    }
    return left.length - right.length;
  }

  function normalizeKernel(value) {
    if (!Array.isArray(value)) return null;
    const seen = new Set();
    const groups = [];
    for (const rawMembers of value) {
      if (!Array.isArray(rawMembers) || rawMembers.length === 0) return null;
      if (rawMembers.some((item) => typeof item !== "string" || !item)) return null;
      const members = [...rawMembers].sort(compareUnicodeCodePoints);
      for (const stateId of members) {
        if (seen.has(stateId)) return null;
        seen.add(stateId);
      }
      groups.push(members);
    }
    return groups.sort(compareStringArrays);
  }

  function readingKernel(reading) {
    if (!isRecord(reading)) return null;
    const fibres = new Map();
    for (const stateId of Object.keys(reading).sort(compareUnicodeCodePoints)) {
      const display = reading[stateId];
      if (typeof display !== "string" || !display) return null;
      if (!fibres.has(display)) fibres.set(display, []);
      fibres.get(display).push(stateId);
    }
    return [...fibres.values()]
      .map((members) => members.sort(compareUnicodeCodePoints))
      .sort(compareStringArrays);
  }

  async function deriveClosureNaturalityEquations(contract) {
    const status = asText(contract.status || "OPEN_SOURCE_BOUNDARY");
    const projection = isRecord(contract.projection) ? contract.projection : {};
    const closure = isRecord(contract.perspective_closure)
      ? contract.perspective_closure : {};
    const states = Array.isArray(projection.states)
      ? projection.states.filter((item) => isRecord(item) && item.id) : [];
    const carrier = states.map((item) => asText(item.id)).sort(compareUnicodeCodePoints);
    const stateByEvent = Object.create(null);
    for (const state of states) {
      if (state.event_id) stateByEvent[asText(state.event_id)] = asText(state.id);
    }

    const readings = Object.create(null);
    if (isRecord(closure.readings)) {
      for (const [perspective, rawReading] of Object.entries(closure.readings)) {
        if (!isRecord(rawReading)) continue;
        const reading = Object.create(null);
        for (const [stateId, value] of Object.entries(rawReading)) {
          reading[asText(stateId)] = asText(value);
        }
        readings[asText(perspective)] = reading;
      }
    }
    const perspectiveIds = Object.keys(readings).sort(compareUnicodeCodePoints);
    const kernels = Object.create(null);
    for (const perspective of perspectiveIds) {
      kernels[perspective] = readingKernel(readings[perspective]) || [];
    }
    const commonKernel = perspectiveIds.length ? kernels[perspectiveIds[0]] : [];
    const kernelsAgree = perspectiveIds.every(
      (perspective) => stable(kernels[perspective]) === stable(commonKernel),
    );
    const projectionReading = Object.create(null);
    if (isRecord(projection.reading)) {
      for (const [stateId, value] of Object.entries(projection.reading)) {
        projectionReading[asText(stateId)] = asText(value);
      }
    }
    const activeReadingIsProjection = status !== "WITNESSED" || (
      owns(readings, asText(contract.perspective_id))
      && stable(readings[asText(contract.perspective_id)]) === stable(projectionReading)
    );

    const fibreRows = Array.isArray(projection.equality_fibres)
      ? projection.equality_fibres.filter((item) => isRecord(item) && item.id) : [];
    const projectionKernel = fibreRows.map((item) =>
      unique(item.member_state_ids).sort(compareUnicodeCodePoints)
    ).sort(compareStringArrays);
    const section = Object.create(null);
    for (const fibre of fibreRows) {
      for (const stateId of unique(fibre.member_state_ids)) {
        section[stateId] = asText(fibre.id);
      }
    }

    const translationEquations = [];
    const rawTranslations = Array.isArray(closure.translations) ? closure.translations : [];
    for (const raw of rawTranslations.filter(isRecord)) {
      const source = asText(raw.source_perspective_id);
      const target = asText(raw.target_perspective_id);
      const expected = Object.create(null);
      let wellDefined = owns(readings, source) && owns(readings, target);
      for (const stateId of carrier) {
        const sourceValue = readings[source]?.[stateId];
        const targetValue = readings[target]?.[stateId];
        if (sourceValue === undefined || targetValue === undefined) {
          wellDefined = false;
          continue;
        }
        if (owns(expected, sourceValue) && expected[sourceValue] !== targetValue) {
          wellDefined = false;
        }
        expected[sourceValue] = targetValue;
      }
      const supplied = Object.create(null);
      if (isRecord(raw.display_translation)) {
        for (const [key, value] of Object.entries(raw.display_translation)) {
          supplied[asText(key)] = asText(value);
        }
      }
      const expectedKeys = Object.keys(expected);
      const faithful = wellDefined
        && Boolean(raw.id)
        && source !== target
        && stable(supplied) === stable(expected)
        && new Set(expectedKeys).size === new Set(expectedKeys.map((key) => expected[key])).size
        && stable(kernels[source] || []) === stable(kernels[target] || []);
      translationEquations.push({
        id: asText(raw.id),
        source_perspective_id: source,
        target_perspective_id: target,
        derived_hair_relabelling: expected,
        source_kernel: kernels[source] || [],
        target_kernel: kernels[target] || [],
        translation_equation_holds: faithful,
      });
    }
    const translationGraph = new Map(
      perspectiveIds.map((perspective) => [perspective, new Set()]),
    );
    for (const equation of translationEquations) {
      if (!equation.translation_equation_holds) continue;
      translationGraph.get(equation.source_perspective_id).add(
        equation.target_perspective_id,
      );
      translationGraph.get(equation.target_perspective_id).add(
        equation.source_perspective_id,
      );
    }
    const reachedPerspectives = new Set();
    const perspectiveFrontier = perspectiveIds.length ? [perspectiveIds[0]] : [];
    if (perspectiveFrontier.length) reachedPerspectives.add(perspectiveIds[0]);
    while (perspectiveFrontier.length) {
      const current = perspectiveFrontier.pop();
      for (const neighbour of translationGraph.get(current)) {
        if (!reachedPerspectives.has(neighbour)) {
          reachedPerspectives.add(neighbour);
          perspectiveFrontier.push(neighbour);
        }
      }
    }
    const translationFamilyConnected = perspectiveIds.length === 0
      || reachedPerspectives.size === perspectiveIds.length;

    const lineageIds = unique(contract.continuation_lineage_ids);
    const lineageStates = unique(lineageIds.map((eventId) => stateByEvent[eventId]));
    const lineageSet = new Set(lineageStates);
    const arenaOrder = [...lineageStates, ...carrier.filter((stateId) => !lineageSet.has(stateId))];
    const growthStages = [];
    let previousDistinctions = 0;
    let previousSquare = true;
    const sectionCounts = new Map();
    const sectionMembers = new Map();
    const readingCounts = new Map(
      perspectiveIds.map((perspective) => [perspective, new Map()]),
    );
    const readingMembers = new Map(
      perspectiveIds.map((perspective) => [perspective, new Map()]),
    );
    for (const [rawIndex, stateId] of arenaOrder.entries()) {
      const index = rawIndex + 1;
      const sectionValue = owns(section, stateId) ? section[stateId] : null;
      const sectionKey = sectionValue === null ? "None" : asText(sectionValue);
      const equalPriorCount = sectionCounts.get(sectionKey) || 0;
      const equalPriorStateIds = sectionMembers.get(sectionKey) || [];
      const translatedValues = Object.create(null);
      const translatedEqualCounts = Object.create(null);
      const translatedEqualStateIds = Object.create(null);
      for (const perspective of perspectiveIds) {
        const value = owns(readings[perspective], stateId)
          ? readings[perspective][stateId] : null;
        translatedValues[perspective] = value;
        const readingKey = value === null ? "None" : asText(value);
        translatedEqualCounts[perspective] = readingCounts.get(perspective).get(readingKey) || 0;
        translatedEqualStateIds[perspective] = readingMembers.get(perspective).get(readingKey) || [];
      }
      const closurePriorDigest = await digest("arena-fibre", equalPriorStateIds);
      const translatedPriorDigests = Object.create(null);
      for (const perspective of perspectiveIds) {
        translatedPriorDigests[perspective] = await digest(
          "arena-fibre", translatedEqualStateIds[perspective],
        );
      }
      const newDistinctions = index - 1 - equalPriorCount;
      const pairAgreement = sectionValue !== null && perspectiveIds.every(
        (perspective) => translatedValues[perspective] !== null
          && translatedPriorDigests[perspective] === closurePriorDigest,
      );
      const squareCommutes = previousSquare && pairAgreement;
      const distinctions = previousDistinctions + newDistinctions;
      growthStages.push({
        index,
        arena_size: index,
        added_state_id: stateId,
        pull_map_entry: [stateId, stateId],
        translated_reading_values: translatedValues,
        translated_equal_prior_counts: translatedEqualCounts,
        translated_equal_prior_digests: translatedPriorDigests,
        closure_section_value: sectionValue,
        closure_equal_prior_count: equalPriorCount,
        closure_equal_prior_digest: closurePriorDigest,
        new_distinctions: newDistinctions,
        naturality_square_commutes: squareCommutes,
        distinction_count: distinctions,
        prior_distinctions_preserved: newDistinctions >= 0,
        strictly_grows: newDistinctions > 0,
        at_full_reach: index === arenaOrder.length,
      });
      sectionCounts.set(sectionKey, equalPriorCount + 1);
      if (!sectionMembers.has(sectionKey)) sectionMembers.set(sectionKey, []);
      sectionMembers.get(sectionKey).push(stateId);
      for (const perspective of perspectiveIds) {
        const value = translatedValues[perspective];
        const readingKey = value === null ? "None" : asText(value);
        const counts = readingCounts.get(perspective);
        counts.set(readingKey, (counts.get(readingKey) || 0) + 1);
        const members = readingMembers.get(perspective);
        if (!members.has(readingKey)) members.set(readingKey, []);
        members.get(readingKey).push(stateId);
      }
      previousSquare = squareCommutes;
      previousDistinctions = distinctions;
    }

    const allSquares = growthStages.every((stage) => stage.naturality_square_commutes);
    const allGrowth = growthStages.every((stage) => stage.prior_distinctions_preserved);
    const fullReach = carrier.length === 0 || (
      growthStages.at(-1)?.at_full_reach === true
      && growthStages.at(-1)?.arena_size === carrier.length
      && stable(projectionKernel) === stable(commonKernel)
    );
    const finiteChecked = status !== "WITNESSED" || (
      carrier.length > 0
      && perspectiveIds.length > 0
      && kernelsAgree
      && activeReadingIsProjection
      && stable(projectionKernel) === stable(commonKernel)
      && translationFamilyConnected
      && sameMembers(Object.keys(section), carrier)
      && translationEquations.every((item) => item.translation_equation_holds)
      && allSquares && allGrowth && fullReach
    );
    return {
      protocol: "closure.supernet/closure-naturality-equations-v1",
      formal_module: "NRRF866ClosureNaturalityIsTranslationalTruthIsTheGrowthOfTheUniverse",
      formal_source_verified_by_runtime: false,
      runtime_reproves_lean: false,
      status,
      active_perspective_id: contract.perspective_id ?? null,
      interactive_translation_id: contract.interactive_translation_id ?? null,
      operators: {
        chart: "EXPLICIT_PERSPECTIVE_READING",
        hair_action: "FAITHFUL_DISPLAY_RELABELING",
        pull: "RESTRICT_READING_ALONG_ARENA_MAP",
        natural_form: "CANONICAL_READING_KERNEL_SECTION",
        closure_fibre: "EQUALITY_OF_NATURAL_FORMS",
      },
      equations: {
        pull_identity: "pull(id,c)=c",
        pull_composition: "pull(g,pull(f,c))=pull(f∘g,c)",
        naturality_square: "naturalForm(o,pull(f,c))=pull(f,naturalForm(f(o),c))",
        translation_truth: "closure(c)=closure(d) iff d=hairAct(h,c)",
        growth: "agreement(W)<=agreement(V) along f:W→V",
      },
      finite_instance: {
        carrier_state_ids: carrier,
        perspective_ids: perspectiveIds,
        reading_kernels: kernels,
        closure_fibres: commonKernel,
        natural_form_section: section,
        translation_equations: translationEquations,
        growth_order: arenaOrder,
        pull_growth_stages: growthStages,
      },
      checks: {
        translated_readings_have_one_closure: kernelsAgree,
        active_reading_is_projection: activeReadingIsProjection,
        translation_family_connected: translationFamilyConnected,
        closure_fibres_are_translation_classes: stable(projectionKernel) === stable(commonKernel)
          && translationFamilyConnected,
        closure_is_canonical_section: sameMembers(Object.keys(section), carrier),
        all_translation_equations_hold: translationEquations.every((item) => item.translation_equation_holds),
        all_pull_naturality_squares_commute: allSquares,
        distinctions_only_grow_with_arena: allGrowth,
        growth_saturates_at_reach: fullReach,
        strict_growth_witnessed: growthStages.some((stage) => stage.strictly_grows),
        finite_runtime_instance_checked: finiteChecked,
      },
      boundary: {
        runtime_is_finite_quotient_instance: true,
        lean_theorems_are_not_reproved_by_runtime: true,
        universe_growth_is_relational_arena_growth: true,
        physical_cosmology_claimed: false,
        truth_issued: false,
      },
    };
  }

  async function closureNaturalityEquationsMatch(contract) {
    const supplied = contract.closure_naturality_equations;
    if (!isRecord(supplied)) return false;
    const body = await deriveClosureNaturalityEquations(contract);
    const suppliedBody = Object.fromEntries(
      Object.entries(supplied).filter(([key]) => key !== "id"),
    );
    if (stable(suppliedBody) !== stable(body)) return false;
    return supplied.id === await digest("closure-naturality-equations", body);
  }

  function perspectiveClosureMatches(contract, projection) {
    const closure = contract.perspective_closure;
    if (!isRecord(closure)) return false;
    if (closure.status !== contract.status) return false;
    if (closure.active_perspective_id !== contract.perspective_id) return false;
    if (closure.equality_basis !== "EXPLICIT_TRANSLATED_PERSPECTIVE_READINGS") return false;
    if (closure.source_provenance_defines_equality !== false) return false;
    if (!isRecord(closure.readings) || !Array.isArray(closure.translations)) return false;
    if (!isRecord(projection.reading)
        || !Array.isArray(projection.states)
        || !Array.isArray(projection.equality_fibres)) return false;

    const perspectiveIds = Object.keys(closure.readings).sort(compareUnicodeCodePoints);
    if (contract.status !== "WITNESSED") {
      const kernels = closure.kernels;
      return perspectiveIds.length === 0
        && closure.translations.length === 0
        && Array.isArray(closure.kernel)
        && closure.kernel.length === 0
        && (kernels === undefined || (isRecord(kernels) && Object.keys(kernels).length === 0))
        && Object.keys(projection.reading).length === 0
        && projection.states.length === 0
        && projection.equality_fibres.length === 0;
    }

    if (perspectiveIds.length === 0 || !owns(closure.readings, contract.perspective_id)) return false;
    const stateIds = [];
    const stateById = new Map();
    const eventIds = new Set();
    for (const state of projection.states) {
      if (!isRecord(state) || typeof state.id !== "string" || !state.id) return false;
      if (stateById.has(state.id)) return false;
      if (typeof state.event_id !== "string" || !state.event_id || eventIds.has(state.event_id)) return false;
      stateIds.push(state.id);
      stateById.set(state.id, state);
      eventIds.add(state.event_id);
    }
    if (stateIds.length === 0) return false;

    const computedKernels = Object.create(null);
    let commonKernel = null;
    for (const perspectiveId of perspectiveIds) {
      const reading = closure.readings[perspectiveId];
      if (!isRecord(reading) || !sameMembers(Object.keys(reading), stateIds)) return false;
      const kernel = readingKernel(reading);
      if (!kernel) return false;
      computedKernels[perspectiveId] = kernel;
      if (commonKernel === null) commonKernel = kernel;
      else if (stable(kernel) !== stable(commonKernel)) return false;
    }
    if (!isRecord(closure.kernels)
        || !sameMembers(Object.keys(closure.kernels), perspectiveIds)) return false;
    for (const perspectiveId of perspectiveIds) {
      const supplied = normalizeKernel(closure.kernels[perspectiveId]);
      if (!supplied || stable(supplied) !== stable(computedKernels[perspectiveId])) return false;
    }
    const suppliedKernel = normalizeKernel(closure.kernel);
    if (!suppliedKernel || stable(suppliedKernel) !== stable(commonKernel)) return false;

    const activeReading = closure.readings[contract.perspective_id];
    if (!sameMembers(Object.keys(projection.reading), stateIds)
        || stable(activeReading) !== stable(projection.reading)) return false;
    const projectionKernel = normalizeKernel(
      projection.equality_fibres.map((fibre) =>
        isRecord(fibre) ? fibre.member_state_ids : null
      ),
    );
    if (!projectionKernel || stable(projectionKernel) !== stable(commonKernel)) return false;

    const contractSources = exactStringList(contract.source_return_ids);
    if (!contractSources) return false;
    const witnessedSources = [];
    const fibreIds = new Set();
    for (const state of projection.states) {
      const stateSources = exactStringList(state.source_return_ids);
      if (!stateSources || !stateSources.every((item) => contractSources.includes(item))) return false;
      witnessedSources.push(...stateSources);
    }
    if (!sameMembers(witnessedSources, contractSources)) return false;
    for (const fibre of projection.equality_fibres) {
      if (!isRecord(fibre) || typeof fibre.id !== "string" || !fibre.id || fibreIds.has(fibre.id)) return false;
      fibreIds.add(fibre.id);
      const members = exactStringList(fibre.member_state_ids);
      const fibreSources = exactStringList(fibre.source_return_ids);
      if (!members || !fibreSources) return false;
      const expectedDisplays = unique(members.map((stateId) => activeReading[stateId]));
      const expectedSources = unique(members.flatMap((stateId) => stateById.get(stateId).source_return_ids));
      if (!sameMembers(fibre.display_fibre_ids, expectedDisplays)
          || !sameMembers(fibreSources, expectedSources)
          || !fibreSources.every((item) => contractSources.includes(item))) return false;
    }

    const graph = new Map(perspectiveIds.map((item) => [item, new Set()]));
    const translationIds = new Set();
    for (const translation of closure.translations) {
      if (!isRecord(translation)
          || typeof translation.id !== "string"
          || !translation.id
          || translationIds.has(translation.id)) return false;
      translationIds.add(translation.id);
      const source = translation.source_perspective_id;
      const target = translation.target_perspective_id;
      const mapping = translation.display_translation;
      if (typeof source !== "string"
          || typeof target !== "string"
          || source === target
          || !owns(closure.readings, source)
          || !owns(closure.readings, target)
          || !isRecord(mapping)) return false;
      const expected = Object.create(null);
      for (const stateId of stateIds) {
        const sourceDisplay = closure.readings[source][stateId];
        const targetDisplay = closure.readings[target][stateId];
        if (owns(expected, sourceDisplay) && expected[sourceDisplay] !== targetDisplay) return false;
        expected[sourceDisplay] = targetDisplay;
      }
      const expectedKeys = Object.keys(expected);
      if (!sameMembers(Object.keys(mapping), expectedKeys)) return false;
      if (!expectedKeys.every((key) => mapping[key] === expected[key])) return false;
      if (new Set(expectedKeys.map((key) => expected[key])).size !== expectedKeys.length) return false;
      const sourceIds = exactStringList(translation.source_return_ids);
      if (!sourceIds || !sourceIds.every((item) => contractSources.includes(item))) return false;
      if (translation.witnessed !== true
          || translation.well_defined !== true
          || translation.faithful !== true
          || translation.same_kernel !== true
          || stable(computedKernels[source]) !== stable(computedKernels[target])) return false;
      graph.get(source).add(target);
      graph.get(target).add(source);
    }
    if (perspectiveIds.length === 1 && closure.translations.length !== 0) return false;
    const reached = new Set([perspectiveIds[0]]);
    const frontier = [perspectiveIds[0]];
    while (frontier.length) {
      const current = frontier.pop();
      for (const neighbour of graph.get(current)) {
        if (!reached.has(neighbour)) {
          reached.add(neighbour);
          frontier.push(neighbour);
        }
      }
    }
    return reached.size === perspectiveIds.length;
  }

  function closureProcessMatches(contract) {
    const closure = contract.perspective_closure;
    const translated = contract.status === "WITNESSED"
      && isRecord(closure)
      && closure.status === "WITNESSED";
    const sourceReturnIds = exactStringList(
      contract.source_return_ids,
      contract.status !== "WITNESSED",
    );
    const lineageIds = exactStringList(contract.continuation_lineage_ids, true);
    if (!sourceReturnIds || !lineageIds) return false;
    if (contract.continuation_index !== lineageIds.length) return false;
    if (!lineageIds.every((item) => sourceReturnIds.includes(item))) return false;
    if (contract.status === "WITNESSED"
        && lineageIds.length
        && sourceReturnIds.includes(contract.focus_event_id)
        && lineageIds.at(-1) !== contract.focus_event_id) return false;
    const witnessedStatus = translated ? "WITNESSED" : contract.status;
    const naturality = isRecord(contract.closure_naturality_equations)
      ? contract.closure_naturality_equations : {};
    const expected = {
      formal_interpretation: {
        module: "NRRF858ConsciousNatureRelativeAxiomsProofsUnderstandingClosuresTranslationalTruthContinuingExistence",
        runtime_bridge: "NRRF859ConsciousSupernetInteractiveProjectionBridge",
        lean_theorems_reproved_by_python: false,
        finite_runtime_instance_checked: true,
        conscious_hypothesis_verified_by_runtime: false,
      },
      relative_axioms: {
        status: witnessedStatus,
        formal_implication_under_conscious_hypothesis: true,
        formal_theorems: ["no_absolute_axioms", "axiomsOf_eq_iff_translational"],
        runtime_translated_chart_family_verified: translated,
        runtime_claim_body_soundness_verified: false,
        runtime_closure_registration_verified: false,
        external_absolute_step_claims_admitted: false,
      },
      relative_proofs: {
        status: witnessedStatus,
        formal_implication_under_conscious_hypothesis: true,
        formal_theorem: "conscious_proves_composite",
        runtime_composite_closure_witness_verified: false,
        runtime_additive_content_verified: false,
        source_returns_preserved: translated,
      },
      understanding: {
        status: witnessedStatus,
        formal_implication_under_conscious_hypothesis: true,
        formal_theorems: ["mem_understanding_iff", "understanding_eq_iff_translational"],
        runtime_translated_chart_family_verified: translated,
        active_perspective_id: contract.perspective_id,
      },
      continuing_existence: {
        status: witnessedStatus,
        formal_implication_under_conscious_hypothesis: true,
        formal_theorem: "conscious_continues_existence",
        continuation_index: contract.continuation_index,
        continuation_lineage_ids: lineageIds,
        runtime_continuation_is_append_only_lineage: true,
        formal_n_fold_defect_verified_by_runtime: false,
        reopens_after_return: true,
        terminal: false,
        new_empirical_evidence_created_by_iteration: false,
      },
      interactive_translation_dialectic: {
        formal_module: "NRRF862InteractiveTranslationRelativeUnityOfNaturalFormsArgumentFlowPolicePerspectiveTruthNoClosedExistenceDialecticContinuation",
        formal_module_source_verified_by_runtime: false,
        dialogue: {
          formal_theorems: ["replay_eq_hairAct_accum", "translationalTruth_eq_dialogues"],
          turn_ids: lineageIds,
          accumulation_is_append_only: true,
          runtime_hair_potential_composition_verified: false,
        },
        natural_forms: {
          formal_theorem: "naturalForms_eq_iff_obsEquiv",
          translated_reading_family_verified: translated,
          one_geometry_kernel_verified: translated,
          complete_invariant_over_all_charts_verified_by_runtime: false,
        },
        perspective_flow: {
          formal_theorem: "coherent_iff_single_chart",
          single_runtime_chart_family_verified: translated,
          all_stage_dialogue_reachability_verified_by_runtime: false,
        },
        argument_truth: {
          formal_theorems: ["police_eq_truth", "police_and_perspective_translate_equally_into_truth", "isPolice_truthVerdict"],
          structured_route_and_value_supplied: false,
          round_argument_admission_verified_by_runtime: false,
          police_verdict_issued: false,
        },
        open_existence: {
          formal_theorems: ["argument_never_closes_existence", "argument_compatible_with_existence", "chain_open", "interactive_translation_relative_unity_of_natural_forms", "exists_live_argument"],
          formal_two_distinct_tokens_required: true,
          runtime_distinct_perspectives: Object.keys(closure.readings || {}).length,
          runtime_two_token_premise_verified: Object.keys(closure.readings || {}).length >= 2,
          continuation_reopens: true,
          terminal: false,
          one_token_closure_limit_preserved: true,
        },
      },
      closure_naturality_growth: {
        formal_module: "NRRF866ClosureNaturalityIsTranslationalTruthIsTheGrowthOfTheUniverse",
        formal_theorem: "closure_naturality_is_translational_truth_is_the_growth_of_the_universe",
        equation_protocol: "closure.supernet/closure-naturality-equations-v1",
        equation_system_id: naturality.id ?? null,
        interactive_translation_id: naturality.interactive_translation_id ?? null,
        runtime_checks: isRecord(naturality.checks) ? {...naturality.checks} : {},
        finite_runtime_instance_only: true,
        lean_theorems_reproved_by_python: false,
      },
      latent_interactive_interface: {
        latent_structure: "VERIFIED_CLOSURE_RELATION",
        latent_equation_system_id: naturality.id ?? null,
        all_interface_relations_factor_through_closure_equations: true,
        visible_projection_is_derived: true,
        local_perspective_hair_is_mutable: true,
        local_modification_is_potential_until_commit: true,
        commit_binds_contract_perspective_source_and_kernel: true,
        server_rederives_commitment_before_append: true,
        committed_hair_defines_equality: false,
        commit_extends_latent_closure: true,
      },
      boundary: {
        source_preserved: true,
        truth_issued: false,
        physical_law_claimed: false,
        consciousness_claimed: false,
        nature_consciousness_proved: false,
        universal_language_for_all_nature_proved: false,
        external_resource_admitted: false,
        empirical_verification_replaced: false,
        authenticated_external_effect_receipt_required: true,
      },
    };
    return stable(contract.closure_process) === stable(expected);
  }

  function validate(contract) {
    if (!contract || typeof contract !== "object") return false;
    if (contract.schema !== schema || contract.protocol !== protocol) return false;
    if (!statuses.has(contract.status)) return false;
    const renderer = contract.renderer_relation || {};
    if (renderer.role !== "TRANSLATIONAL_RELATION_EVALUATOR") return false;
    if (renderer.input !== "INTERACTIVE_TRANSLATION_OF_CLOSURE_EQUATIONS_ONLY") return false;
    if (renderer.visible_words_source !== "SOURCE_RETURNS_ONLY") return false;
    if (renderer.geometry_source !== "CLOSURE_EQUATION_FIBRES_AND_PULL_SQUARES_ONLY") return false;
    if (renderer.natural_form_constraint !== "NRRF866_INTERACTIVE_CLOSURE_EQUATION_SYSTEM") return false;
    if (renderer.equation_system_required !== true) return false;
    if (renderer.geometry_acceptance !== "EXACT_LOCAL_CLOSURE_REDERIVATION") return false;
    if (renderer.successor_acceptance !== "VERIFIED_CLOSURE_BEFORE_INTERFACE_COMMIT") return false;
    if (renderer.latent_structure !== "VERIFIED_CLOSURE_RELATION") return false;
    if (renderer.local_navigation !== "PERSPECTIVE_HAIR_AND_FOCUS") return false;
    if (renderer.local_modification !== "UNCOMMITTED_CLOSURE_POTENTIAL") return false;
    if (renderer.commit_protocol !== "LOCAL_PROJECTION_COMMITMENT_THEN_REDERIVATION") return false;
    if (!Array.isArray(renderer.fixed_visible_controls) || renderer.fixed_visible_controls.length) return false;
    if (!Array.isArray(renderer.authored_visible_vocabulary) || renderer.authored_visible_vocabulary.length) return false;
    if (!Array.isArray(renderer.fallback_visuals) || renderer.fallback_visuals.length) return false;
    if (renderer.can_define_semantics !== false || renderer.can_admit_forms !== false || renderer.can_issue_truth !== false) return false;
    const claims = contract.claims || {};
    if (claims.truth_issued !== false
        || claims.physical_law_claimed !== false
        || claims.consciousness_claimed !== false
        || claims.external_resource_admitted !== false) return false;
    if (!Number.isInteger(contract.continuation_index) || contract.continuation_index < 0) return false;
    const process = contract.closure_process || {};
    const boundary = process.boundary || {};
    if (boundary.source_preserved !== true
        || boundary.truth_issued !== false
        || boundary.physical_law_claimed !== false
        || boundary.consciousness_claimed !== false
        || boundary.nature_consciousness_proved !== false
        || boundary.universal_language_for_all_nature_proved !== false
        || boundary.external_resource_admitted !== false
        || boundary.empirical_verification_replaced !== false
        || boundary.authenticated_external_effect_receipt_required !== true) return false;
    const projection = contract.projection || {};
    if (projection.active_perspective_id !== contract.perspective_id) return false;
    if (!Array.isArray(projection.states) || !Array.isArray(projection.equality_fibres)) return false;
    if (!Array.isArray(projection.translations) || !Array.isArray(projection.potentials)) return false;
    if (!projection.reading || typeof projection.reading !== "object") return false;
    if (!perspectiveClosureMatches(contract, projection)) return false;
    if (!closureProcessMatches(contract)) return false;
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
    const execution = contract.execution || {};
    if (execution.endpoint_template !== "/supernet/interface/projections/{contract_id}/return") return false;
    if (execution.contract_revalidation_required !== true
        || execution.only_relation_extension !== true
        || execution.closure_only !== true) return false;
    if (contract.status === "OPEN_TRUTH_CONSTRAINT") {
      return relation === null && execution.return_relation_id === null;
    }
    if (!relation || relation.kind !== "SOURCE_PRESERVING_TRANSLATIONAL_RETURN") return false;
    if (relation.full_surface_aperture !== true || relation.visible_control !== false) return false;
    if (relation.creates_truth_directly !== false || relation.reclose_after_return !== true) return false;
    if (!derivationMatches(contract, relation.derivation, contract.status === "OPEN_SOURCE_BOUNDARY")) return false;
    return execution.return_relation_id === relation.id;
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

  function localDraftScalar(source) {
    let value = 2166136261;
    for (const symbol of Array.from(source)) {
      value ^= symbol.codePointAt(0);
      value = Math.imul(value, 16777619) >>> 0;
    }
    return value;
  }

  function renderLocalModification(layer, focusPrimitive) {
    if (!draft) return;
    const [sourceX, sourceY] = focusPrimitive?.centre || [500, 500];
    const scalar = localDraftScalar(draft);
    const phase = 2 * Math.PI * ((scalar % 360) / 360);
    const distance = Math.min(350, (focusPrimitive?.radius || 54) + 150);
    const x = 500 + distance * Math.cos(phase);
    const y = 500 + distance * Math.sin(phase);
    const radius = Math.min(150, 54 + Math.sqrt(Array.from(draft).length) * 6);
    const hueValue = scalar % 360;
    const dx = x - sourceX;
    const dy = y - sourceY;
    const length = Math.max(1, Math.hypot(dx, dy));
    const bend = Math.min(86, length * .18);
    const points = [[sourceX, sourceY], [
      (sourceX + x) / 2 - dy / length * bend,
      (sourceY + y) / 2 + dx / length * bend,
    ], [x, y]];
    layer.append(svgElement("path", {
      d: projectedPath(points),
      class: "local-potential-path",
      stroke: `hsl(${hueValue} 72% 68%)`,
      "data-local-modification": "UNCOMMITTED_CLOSURE_POTENTIAL",
    }));
    layer.append(svgElement("circle", {
      cx: x,
      cy: y,
      r: radius,
      class: "local-potential-shell",
      stroke: `hsl(${hueValue} 72% 68%)`,
      "data-local-modification": "UNCOMMITTED_CLOSURE_POTENTIAL",
    }));
    const width = Math.max(180, radius * 2.8);
    sourceBlock(
      layer,
      x - width / 2,
      y - radius * .8,
      width,
      radius * 1.6,
      draft,
      "draft-trace",
    );
  }

  function render(contract) {
    active = validate(contract) && verifiedContracts.has(contract) ? contract : null;
    mount.replaceChildren();
    mount.dataset.state = active ? active.status : "OPEN_TRUTH_CONSTRAINT";
    delete mount.dataset.closureEquationSystemId;
    delete mount.dataset.closureNaturality;
    if (!active) return;
    mount.dataset.closureEquationSystemId = active.closure_naturality_equations.id;
    mount.dataset.closureNaturality = "PULL_SQUARES_AND_ARENA_GROWTH";
    const projection = active.projection;
    const visualization = locallyDerivedVisualizations.get(active);
    if (!visualization) { active = null; return; }
    const svg = svgElement("svg", {viewBox: visualization.view_box.join(" ")});
    mount.append(svg);
    const chartLayer = svgElement("g", {
      transform: `rotate(${localHairMillidegrees / 1000} 500 500)`,
      "data-local-perspective-hair": localHairMillidegrees,
    });
    svg.append(chartLayer);
    const fibreById = new Map(projection.equality_fibres.map((fibre) => [fibre.id, fibre]));
    const primitiveByForm = new Map(visualization.fibre_primitives.map((primitive) => [primitive.natural_form_id, primitive]));
    for (const relation of visualization.translation_primitives) {
      const path = svgElement("path", {
        d: projectedPath(relation.quadratic_path),
        class: "translation",
        stroke: `hsl(${relation.hue} 72% 66%)`,
        "data-equality": relation.executes_as_equality === true,
      });
      chartLayer.append(path);
    }
    const focusForm = active.return_relation?.parent_natural_form_id || null;
    const focusPrimitive = primitiveByForm.get(focusForm) || {centre: [500, 500], radius: 54};
    visualization.potential_primitives.forEach((relation) => {
      chartLayer.append(svgElement("path", {
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
          const origin = active;
          const perspectiveId = origin.perspective_id;
          load(firstEvent, perspectiveId, {
            preserveOnFailure: true,
            expectedActive: origin,
          }).then((loaded) => {
            if (!loaded) return;
            const current = new URL(window.location.href);
            current.searchParams.set("focus_event_id", firstEvent);
            current.searchParams.set("perspective_id", perspectiveId);
            history.replaceState(null, "", current);
          }).finally(() => sensor.focus());
        });
      }
      chartLayer.append(group);
      const traceWidth = Math.max(120, primitive.radius * 2.8);
      sourceBlock(
        chartLayer,
        x - traceWidth / 2,
        y - primitive.radius * .8,
        traceWidth,
        primitive.radius * 1.6,
        trace,
        "source-trace",
      );
    }
    renderLocalModification(chartLayer, focusPrimitive);
  }

  async function verifyContract(contract) {
    try {
      if (!validate(contract)
          || !await closureNaturalityEquationsMatch(contract)
          || !await visualizationMatches(contract)
          || !await contractIdMatchesContent(contract)) return false;
      verifiedContracts.add(contract);
      return true;
    } catch (_error) {
      return false;
    }
  }

  async function renderVerified(contract) {
    if (await verifyContract(contract)) {
      render(contract);
      return true;
    }
    render(null);
    return false;
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

  async function load(
    focusEventId,
    perspectiveId,
    {preserveOnFailure = false, expectedActive = null} = {},
  ) {
    const params = new URLSearchParams({perspective_id: perspectiveId});
    if (focusEventId) params.set("focus_event_id", focusEventId);
    const response = await fetch(`/supernet/interface?${params}`, {credentials: "same-origin"});
    if (!response.ok) {
      if (!preserveOnFailure) render(null);
      return false;
    }
    const payload = await response.json();
    const candidate = payload.closure_ui_contract || null;
    if (!await verifyContract(candidate)) {
      if (!preserveOnFailure) render(null);
      return false;
    }
    if (expectedActive && active !== expectedActive) return false;
    render(candidate);
    return true;
  }

  async function returnSource() {
    if (executing || !active || !active.return_relation || !draft.trim()) return;
    executing = true;
    const submittedContract = active;
    const relation = submittedContract.return_relation;
    const endpoint = `/supernet/interface/projections/${encodeURIComponent(submittedContract.id)}/return`;
    const exactSourceReturn = draft;
    const submittedHair = localHairMillidegrees;
    try {
      const localProjectionCommitment = await digest("local-projection", {
        contract_id: submittedContract.id,
        closure_equation_system_id: submittedContract.closure_naturality_equations.id,
        return_relation_id: relation.id,
        perspective_id: submittedContract.perspective_id,
        focus_event_id: submittedContract.focus_event_id,
        exact_source_return: exactSourceReturn,
        local_perspective_hair_millidegrees: submittedHair,
        reading_kernel: submittedContract.perspective_closure.kernel,
      });
      const response = await fetch(endpoint, {
        method: "POST",
        credentials: "same-origin",
        headers: {"content-type": "application/json"},
        body: JSON.stringify({
          return_relation_id: relation.id,
          perspective_id: submittedContract.perspective_id,
          focus_event_id: submittedContract.focus_event_id,
          exact_source_return: exactSourceReturn,
          closure_equation_system_id: submittedContract.closure_naturality_equations.id,
          local_projection_commitment: localProjectionCommitment,
          local_perspective_hair_millidegrees: submittedHair,
          source_stream: "full-surface-interaction",
        }),
      });
      const payload = await response.json();
      if (response.status === 409) {
        if (active === submittedContract) {
          await load(submittedContract.focus_event_id, submittedContract.perspective_id, {
            preserveOnFailure: true,
            expectedActive: submittedContract,
          });
        }
        return;
      }
      const next = payload.closure_ui_contract
        || payload.interface?.closure_ui_contract
        || payload.detail?.closure_ui_contract;
      if (!response.ok || !next) return;
      const committed = payload.committed_local_projection || {};
      if (committed.id !== localProjectionCommitment
          || committed.latent_contract_id !== submittedContract.id
          || committed.closure_equation_system_id !== submittedContract.closure_naturality_equations.id
          || committed.perspective_id !== submittedContract.perspective_id
          || committed.focus_event_id !== submittedContract.focus_event_id
          || committed.hair_millidegrees !== submittedHair
          || committed.closure_rederived !== true) return;
      if (!await verifyContract(next)) return;
      if (active !== submittedContract
          || next.perspective_id !== submittedContract.perspective_id) return;
      if (draft === exactSourceReturn) {
        draft = "";
        sensor.value = "";
      }
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
  mount.addEventListener("pointermove", (event) => {
    if (!active || event.buttons !== 1) return;
    const bounds = mount.getBoundingClientRect();
    const x = event.clientX - bounds.left - bounds.width / 2;
    const y = event.clientY - bounds.top - bounds.height / 2;
    localHairMillidegrees = Math.round(
      Math.atan2(y, x) * 180 / Math.PI * 1000,
    );
    render(active);
  });
  mount.addEventListener("dblclick", () => {
    localHairMillidegrees = 0;
    if (active) render(active);
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
