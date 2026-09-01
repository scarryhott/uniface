from __future__ import annotations

"""Browser realization of visual identity iff user/token interactions are equal."""

from .potential_gate_unified_interface import POTENTIAL_GATE_SUPERNET_HTML as _BASE_HTML


def _derive_equal_interaction_surface(html: str) -> str:
    body = html

    verifier_anchor = (
        'if(!Array.isArray(gate.paths)||!Array.isArray(gate.localities)||!Array.isArray(gate.family_potentials))return false;'
    )
    verifier = verifier_anchor + r'''
  const visualIdentification=gate.equal_user_token_visual_identification;
  if(!isRecord(visualIdentification))return false;
  if(visualIdentification.id!==await digest("equal-user-token-visual-identification",withoutId(visualIdentification)))return false;
  if(visualIdentification.visual_identification_iff_equal_user_token_interaction!==true)return false;
  if(visualIdentification.user_interaction_and_token_interaction_share_one_quotient!==true)return false;
  if(visualIdentification.rendering_authors_equality!==false||visualIdentification.rendering_authors_truth!==false)return false;
  if(full.equal_user_token_visual_identification_id!==visualIdentification.id)return false;
  if(full.visual_identification_iff_equal_user_token_interaction!==true||full.ui_is_visual_reading_of_equal_user_token_interactions!==true)return false;
  for(const row of visualIdentification.relations||[]){
    if(!isRecord(row)||row.id!==await digest("user-token-visual-relation",withoutId(row)))return false;
    const equal=row.equal_user_token_interaction===true;
    const identified=row.visually_identified===true;
    const semanticControlled=row.semantic_translation_controlled===true;
    const witnessed=row.path_status==="WITNESSED";
    if(identified!==(equal&&(!semanticControlled||witnessed)))return false;
    if(identified&&!row.visual_identification_id)return false;
    if(row.renderer_authors_identification!==false||row.selection_authors_identification!==false)return false;
  }'''
    if verifier_anchor not in body:
        raise RuntimeError("full-gate browser verifier anchor changed")
    body = body.replace(verifier_anchor, verifier, 1)

    function_anchor = (
        'function activePath(full){return(full.relative_natural_form_potential_gate.paths||[]).find(path=>path.id===activeRelationId)||null}'
    )
    function_replacement = function_anchor + r'''
function visualInteraction(full,path){
  const rows=full?.relative_natural_form_potential_gate?.equal_user_token_visual_identification?.relations||[];
  return rows.find(row=>row.path_id===path.id)||null;
}'''
    if function_anchor not in body:
        raise RuntimeError("active-path browser anchor changed")
    body = body.replace(function_anchor, function_replacement, 1)

    render_anchor = (
        'for(const path of geometry.paths){const points=path.points.map(point=>solvePoint(solution,point));const selected=path.id===activeRelationId;const node=svg("path",{'
    )
    render_replacement = (
        'for(const path of geometry.paths){const points=path.points.map(point=>solvePoint(solution,point));'
        'const selected=path.id===activeRelationId;const visual=visualInteraction(active,path);'
        'const node=svg("path",{'
    )
    if render_anchor not in body:
        raise RuntimeError("path rendering browser anchor changed")
    body = body.replace(render_anchor, render_replacement, 1)

    attrs_anchor = (
        '"data-return-aperture":path.status!=="WITNESSED"});'
    )
    attrs_replacement = ''.join((
        '"data-return-aperture":path.status!=="WITNESSED",',
        '"data-user-token-interaction-equal":visual?.equal_user_token_interaction===true,',
        '"data-visually-identified":visual?.visually_identified===true,',
        '"data-visual-identification-id":visual?.visual_identification_id||"",',
        '"data-maze-cell-id":visual?.maze_cell_id||"",',
        '"data-semantic-family-id":visual?.semantic_family_id||"",',
        '"data-natural-form-id":visual?.natural_form_id||""});',
    ))
    if attrs_anchor not in body:
        raise RuntimeError("path attribute browser anchor changed")
    body = body.replace(attrs_anchor, attrs_replacement, 1)

    root_anchor = (
        '"data-equality-is-local-gate-constraint":"true",'
    )
    root_replacement = root_anchor + ''.join((
        '"data-visual-identification-iff-equal-user-token-interaction":"true",',
        '"data-ui-is-relative-user-token-interaction":"true",',
    ))
    if root_anchor not in body:
        raise RuntimeError("surface root browser anchor changed")
    body = body.replace(root_anchor, root_replacement, 1)

    required = (
        "equal_user_token_visual_identification",
        "visual_identification_iff_equal_user_token_interaction",
        "visualInteraction(active,path)",
        "data-user-token-interaction-equal",
        "data-visual-identification-id",
        "data-maze-cell-id",
        "data-semantic-family-id",
        "data-ui-is-relative-user-token-interaction",
    )
    if not all(token in body for token in required):
        raise RuntimeError("equal user/token visual identification was not installed")
    return body


POTENTIAL_GATE_SUPERNET_HTML = _derive_equal_interaction_surface(_BASE_HTML)

__all__ = ["POTENTIAL_GATE_SUPERNET_HTML"]
