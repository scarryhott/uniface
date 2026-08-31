from __future__ import annotations

"""Browser transport for the proof-indexed versioned natural-form atlas.

The legacy renderer remains the geometry evaluator.  This wrapper independently
checks atlas/glue identity, the indexed Lean witness registry, and the final
Supernet closure certificate before any projection is rendered. Returned and
OPEN paths remain navigable view transport without inventing cross-form truth.
"""

from .closure_only_interface_legacy import CLOSURE_ONLY_SUPERNET_HTML as _BASE_HTML


_ATLAS_VALIDATOR = r'''
  async function atlasContractMatches(contract) {
    const atlas = contract?.natural_form_atlas;
    const glue = contract?.glued_ui_subatlas;
    const semantics = contract?.atlas_semantics;
    const proofIndex = contract?.formal_proof_index;
    const closure = contract?.supernet_closure_certificate;
    if (!isRecord(atlas) || !isRecord(glue) || !isRecord(semantics)
        || !isRecord(proofIndex) || !isRecord(closure)) return false;
    if (atlas.protocol !== "SUPERNET-VERSIONED-NATURAL-FORM-ATLAS"
        || atlas.schema !== "closure.supernet/versioned-natural-form-atlas-v1") return false;
    if (atlas.closure_ball_is_master_container !== false
        || atlas.closure_ball_is_one_chart !== true
        || atlas.visual_resemblance_can_witness_equality !== false
        || atlas.shared_name_can_witness_equality !== false
        || atlas.cross_form_equality_requires_returned_translation !== true
        || atlas.open_relation_is_preserved !== true
        || atlas.historical_semantics_are_versioned !== true
        || atlas.forms_may_disappear_without_returned_translation !== false
        || atlas.truth_issued !== false
        || atlas.empirical_claims_issued !== false) return false;
    if (!Array.isArray(atlas.charts) || !Array.isArray(atlas.translations)) return false;
    const chartIds = atlas.charts.map((chart) => isRecord(chart) ? asText(chart.id) : "");
    if (!chartIds.length || chartIds.some((id) => !id) || new Set(chartIds).size !== chartIds.length) return false;
    const chartSet = new Set(chartIds);
    const hairIds = new Set(atlas.charts
      .filter((chart) => isRecord(chart) && chart.name === "hair")
      .map((chart) => asText(chart.id)));
    for (let version = 1; version <= 5; version += 1) {
      if (!hairIds.has(`nf:hair:v${version}`)) return false;
    }
    const identity = new Set();
    const relationIds = new Set();
    for (const relation of atlas.translations) {
      if (!isRecord(relation) || typeof relation.id !== "string" || !relation.id) return false;
      if (relationIds.has(relation.id)) return false;
      relationIds.add(relation.id);
      const source = asText(relation.source_chart_id);
      const target = asText(relation.target_chart_id);
      if (!chartSet.has(source) || !chartSet.has(target)) return false;
      if (relation.status !== "OPEN" && relation.status !== "WITNESSED") return false;
      if (relation.visual_resemblance_used !== false || relation.name_equality_used !== false) return false;
      if (relation.kind === "IDENTITY") {
        if (source !== target || relation.status !== "WITNESSED") return false;
        identity.add(source);
      } else if (relation.status === "WITNESSED") {
        const sources = exactStringList(relation.source_return_ids);
        if (!sources || relation.source_preserved !== true
            || relation.closure_commutes !== true
            || relation.return_preserved !== true) return false;
      } else if (relation.executes_as_equality === true) {
        return false;
      }
    }
    if (identity.size !== chartSet.size || [...chartSet].some((id) => !identity.has(id))) return false;
    const atlasBody = Object.fromEntries(Object.entries(atlas).filter(([key]) => key !== "id"));
    if (atlas.id !== await digest("natural-form-atlas", atlasBody)) return false;

    const compatible = isRecord(atlas.compatible_subatlas) ? atlas.compatible_subatlas : {};
    const chartIdsCompatible = unique(compatible.chart_ids || []);
    const translationIds = unique(compatible.translation_ids || []);
    const openIds = unique(compatible.open_boundary_translation_ids || []);
    const glueBody = {
      protocol: "closure.supernet/glued-natural-form-subatlas-v1",
      atlas_id: atlas.id,
      active_perspective_id: atlas.active_perspective_id,
      chart_ids: chartIdsCompatible,
      translation_ids: translationIds,
      open_boundary_translation_ids: openIds,
      operator: "GLUE_COMPATIBLE_VERSIONED_NATURAL_FORM_CHARTS",
      edge_semantics: "ONGOING_VIEW_TRANSPORT",
      selector_semantics: "COMPATIBLE_SUBATLAS_NOT_SINGLE_FORM",
      hair_semantics: "VERSIONED_SOURCE_PRESERVING_RETURN_FIELD",
      return_semantics: "SAME_TRANSLATIONAL_TRUTH_WITH_HISTORY_NOT_LITERAL_STATE_RESET",
      closure_ball_is_master_container: false,
      single_final_form_selected: false,
      truth_issued: false,
    };
    const expectedGlue = {...glueBody, id: await digest("glued-subatlas", glueBody)};
    if (stable(glue) !== stable(expectedGlue)) return false;
    if (semantics.ui_is_locally_glued_atlas !== true
        || semantics.edge_is_ongoing_view_transport !== true
        || semantics.natural_form_selector_returns_compatible_subatlas !== true
        || semantics.single_final_form_selected !== false
        || semantics.closure_ball_is_master_container !== false
        || semantics.historical_form_meaning_may_be_replaced_without_return !== false
        || semantics.cross_form_equality_requires_source_preserving_return !== true
        || semantics.open_cross_form_relations_remain_navigable !== true
        || semantics.formal_proof_index_required !== true
        || semantics.archive_audit_gates_supernet_closure !== false
        || semantics.open_relation_breaks_supernet_closure !== false
        || semantics.truth_issued !== false) return false;

    if (proofIndex.protocol !== "SUPERNET-FORMAL-PROOF-INDEX"
        || proofIndex.schema !== "closure.supernet/formal-proof-index-v1"
        || proofIndex.atlas_id !== atlas.id
        || proofIndex.proof_index_closed !== true
        || proofIndex.required_core_modules_present !== true
        || proofIndex.lean_source_verified_by_runtime !== false
        || proofIndex.runtime_reproves_lean !== false
        || !Array.isArray(proofIndex.proofs)
        || !proofIndex.proofs.length
        || !Array.isArray(proofIndex.unresolved_chart_names)
        || proofIndex.unresolved_chart_names.length !== 0) return false;
    for (const proof of proofIndex.proofs) {
      if (!isRecord(proof)
          || typeof proof.id !== "string" || !proof.id
          || typeof proof.module !== "string" || !proof.module
          || proof.machine_checked_reported !== true
          || proof.source_verified_by_runtime !== false
          || proof.runtime_reproves_lean !== false
          || proof.cross_form_equality_authored !== false
          || proof.formal_witness_is_not_visual_resemblance !== true
          || !Array.isArray(proof.chart_ids)
          || !proof.chart_ids.every((id) => chartSet.has(asText(id)))) return false;
      const proofBody = Object.fromEntries(Object.entries(proof).filter(([key]) => key !== "id"));
      if (proof.id !== await digest("formal-proof-witness", proofBody)) return false;
    }
    const proofBody = Object.fromEntries(Object.entries(proofIndex).filter(([key]) => key !== "id"));
    if (proofIndex.id !== await digest("formal-proof-index", proofBody)) return false;

    if (closure.protocol !== "SUPERNET-PROOF-INDEXED-CLOSURE"
        || closure.schema !== "closure.supernet/proof-indexed-closure-certificate-v1"
        || closure.status !== "WITNESSED"
        || closure.supernet_closed !== true
        || closure.atlas_id !== atlas.id
        || closure.formal_proof_index_id !== proofIndex.id
        || closure.glued_subatlas_id !== glue.id
        || closure.archive_audit_required_for_supernet_closure !== false
        || closure.archive_audit_is_diagnostic_only !== true
        || closure.open_relation_breaks_supernet_closure !== false
        || closure.open_relations_are_part_of_closure !== true
        || closure.complete_does_not_mean_every_open_relation_resolved !== true
        || closure.formal_proof_source_verified_by_runtime !== false
        || closure.runtime_reproves_lean !== false
        || closure.existence_closed !== false
        || closure.dialectic_continuation_status !== "OPEN"
        || closure.truth_issued !== false
        || !isRecord(closure.checks)
        || !Object.values(closure.checks).every((value) => value === true)) return false;
    const closureBody = Object.fromEntries(Object.entries(closure).filter(([key]) => key !== "id"));
    if (closure.id !== await digest("supernet-closure", closureBody)) return false;
    return true;
  }
'''

_OLD_TRANSLATION_BLOCK = r'''    for (const relation of visualization.translation_primitives) {
      const path = svgElement("path", {
        d: projectedPath(relation.quadratic_path),
        class: "translation",
        stroke: `hsl(${relation.hue} 72% 66%)`,
        "data-equality": relation.executes_as_equality === true,
      });
      chartLayer.append(path);
    }
'''

_NEW_TRANSLATION_BLOCK = r'''    for (const relation of visualization.translation_primitives) {
      const path = svgElement("path", {
        d: projectedPath(relation.quadratic_path),
        class: "translation",
        stroke: `hsl(${relation.hue} 72% 66%)`,
        "data-equality": relation.executes_as_equality === true,
        "data-view-transport": "ONGOING_VIEW_TRANSPORT",
      });
      const translatedRelation = projection.translations.find(
        (item) => item.id === relation.relation_id,
      );
      const targetState = projection.states.find(
        (item) => item.id === translatedRelation?.target_state_id,
      );
      if (targetState?.event_id) {
        path.style.cursor = "pointer";
        path.addEventListener("pointerdown", (event) => {
          event.stopPropagation();
          const origin = active;
          load(targetState.event_id, origin.perspective_id, {
            preserveOnFailure: true,
            expectedActive: origin,
          }).then((loaded) => {
            if (!loaded) return;
            const current = new URL(window.location.href);
            current.searchParams.set("focus_event_id", targetState.event_id);
            current.searchParams.set("perspective_id", origin.perspective_id);
            history.replaceState(null, "", current);
          }).finally(() => sensor.focus());
        });
      }
      chartLayer.append(path);
    }
'''

_OLD_POTENTIAL_BLOCK = r'''    visualization.potential_primitives.forEach((relation) => {
      chartLayer.append(svgElement("path", {
        d: projectedPath(relation.quadratic_path),
        class: "potential",
        stroke: `hsl(${relation.hue} 68% 65%)`,
      }));
    });
'''

_NEW_POTENTIAL_BLOCK = r'''    visualization.potential_primitives.forEach((relation) => {
      const path = svgElement("path", {
        d: projectedPath(relation.quadratic_path),
        class: "potential",
        stroke: `hsl(${relation.hue} 68% 65%)`,
        "data-view-transport": "OPEN_VIEW_TRANSPORT",
      });
      const potential = projection.potentials.find(
        (item) => item.id === relation.relation_id,
      );
      const targetEvent = potential?.target_event_id;
      if (targetEvent) {
        path.style.cursor = "pointer";
        path.addEventListener("pointerdown", (event) => {
          event.stopPropagation();
          const origin = active;
          load(targetEvent, origin.perspective_id, {
            preserveOnFailure: true,
            expectedActive: origin,
          }).then((loaded) => {
            if (!loaded) return;
            const current = new URL(window.location.href);
            current.searchParams.set("focus_event_id", targetEvent);
            current.searchParams.set("perspective_id", origin.perspective_id);
            history.replaceState(null, "", current);
          }).finally(() => sensor.focus());
        });
      }
      chartLayer.append(path);
    });
'''


def _inject(html: str) -> str:
    replacements = [
        (
            "  function validate(contract) {\n",
            _ATLAS_VALIDATOR + "\n  function validate(contract) {\n",
        ),
        (
            "      if (!validate(contract)\n          || !await closureNaturalityEquationsMatch(contract)\n",
            "      if (!validate(contract)\n          || !await atlasContractMatches(contract)\n          || !await closureNaturalityEquationsMatch(contract)\n",
        ),
        (
            "    mount.dataset.closureNaturality = \"PULL_SQUARES_AND_ARENA_GROWTH\";\n",
            "    mount.dataset.closureNaturality = \"PULL_SQUARES_AND_ARENA_GROWTH\";\n"
            "    mount.dataset.naturalFormAtlasId = active.natural_form_atlas.id;\n"
            "    mount.dataset.gluedSubatlasId = active.glued_ui_subatlas.id;\n"
            "    mount.dataset.formalProofIndexId = active.formal_proof_index.id;\n"
            "    mount.dataset.supernetClosureCertificateId = active.supernet_closure_certificate.id;\n"
            "    mount.dataset.supernetClosed = active.supernet_closure_certificate.supernet_closed;\n"
            "    mount.dataset.edgeSemantics = active.glued_ui_subatlas.edge_semantics;\n",
        ),
        (_OLD_TRANSLATION_BLOCK, _NEW_TRANSLATION_BLOCK),
        (_OLD_POTENTIAL_BLOCK, _NEW_POTENTIAL_BLOCK),
    ]
    result = html
    for old, new in replacements:
        if old not in result:
            raise RuntimeError("proof-indexed atlas browser integration target changed")
        result = result.replace(old, new, 1)
    return result


CLOSURE_ONLY_SUPERNET_HTML = _inject(_BASE_HTML)


__all__ = ["CLOSURE_ONLY_SUPERNET_HTML"]
