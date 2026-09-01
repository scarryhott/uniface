from __future__ import annotations

"""Browser realization of NRRF885 `Seen` / metaphor equality semantics."""

from .continuing_closure_interface import POTENTIAL_GATE_SUPERNET_HTML as _BASE_HTML


def _metaphor_surface(html: str) -> str:
    body = html

    verifier_anchor = (
        'if(full.continuing_translation_closure_id!==continuum.id)return false;'
    )
    verifier = verifier_anchor + r'''
  const metaphor=gate.visualization_metaphor_closure;
  if(!isRecord(metaphor))return false;
  if(metaphor.id!==await digest("visualization-metaphor-closure",withoutId(metaphor)))return false;
  if(full.visualization_metaphor_closure_id!==metaphor.id)return false;
  if(full.seen_id!==metaphor.seen_id||gate.seen_id!==metaphor.seen_id)return false;
  if(full.metaphor_class_id!==metaphor.metaphor_class_id||gate.metaphor_class_id!==metaphor.metaphor_class_id)return false;
  if(full.visual_equality_is_seen_equality!==true||gate.visual_equality_is_seen_equality!==true)return false;
  if(full.proof_by_visualization_uses_metaphor_equality!==true)return false;
  if(metaphor.metaphor_equality_runtime_criterion!=="SEEN_ID_EQUALITY")return false;
  if(metaphor.visual_invariants_factor_through_seen!==true)return false;
  if(metaphor.labels_author_metaphor_equality!==false)return false;
  if(metaphor.renderer_coordinates_author_metaphor_equality!==false)return false;
  if(metaphor.hair_authors_metaphor_equality!==false||metaphor.zoom_authors_metaphor_equality!==false)return false;
  const seenFoldIds=[...new Set((metaphor.currents||[]).map(row=>row.fold_class_id).filter(Boolean))].sort(compareCodePoints);
  if(JSON.stringify(seenFoldIds)!==JSON.stringify(metaphor.seen_fold_class_ids||[]))return false;
  if(metaphor.seen_id!==await digest("visualization-seen",{fold_class_ids:seenFoldIds}))return false;
  for(const current of metaphor.currents||[]){
    if(!isRecord(current)||current.id!==await digest("visualization-current",withoutId(current)))return false;
    if(current.labels_enter_seen!==false||current.renderer_coordinates_enter_seen!==false)return false;
    if(current.hair_enters_seen!==false||current.zoom_enters_seen!==false)return false;
    if(current.crystal_ball_id){
      const expectedBall=await digest("visualization-crystal-ball",{rotation_class_id:current.rotation_class_id});
      if(current.crystal_ball_id!==expectedBall)return false;
    }
  }'''
    if verifier_anchor not in body:
        raise RuntimeError("NRRF885 verifier anchor changed")
    body = body.replace(verifier_anchor, verifier, 1)

    continuum_fn = r'''function continuumRelation(full,path){
  const rows=full?.relative_natural_form_potential_gate?.continuing_translation_closure?.relations||[];
  return rows.find(row=>row.path_id===path.id)||null;
}'''
    metaphor_fn = continuum_fn + r'''
function visualizationCurrent(full,path){
  const rows=full?.relative_natural_form_potential_gate?.visualization_metaphor_closure?.currents||[];
  return rows.find(row=>row.path_id===path.id)||null;
}'''
    if continuum_fn not in body:
        raise RuntimeError("continuumRelation anchor changed")
    body = body.replace(continuum_fn, metaphor_fn, 1)

    render_anchor = (
        'const continuum=continuumRelation(active,path);const node=svg("path",{'
    )
    render_replacement = (
        'const continuum=continuumRelation(active,path);'
        'const current=visualizationCurrent(active,path);const node=svg("path",{'
    )
    if render_anchor not in body:
        raise RuntimeError("NRRF885 render anchor changed")
    body = body.replace(render_anchor, render_replacement, 1)

    attrs_anchor = '"data-continuing":continuum?.continuing===true,'
    attrs_replacement = attrs_anchor + ''.join((
        '"data-fold-class-id":current?.fold_class_id||"",',
        '"data-visualization-current-id":current?.id||"",',
        '"data-crystal-ball-id":current?.crystal_ball_id||"",',
        '"data-rotation-class-id":current?.rotation_class_id||"",',
    ))
    if attrs_anchor not in body:
        raise RuntimeError("NRRF885 relation-attribute anchor changed")
    body = body.replace(attrs_anchor, attrs_replacement, 1)

    root_anchor = '"data-nonreturned-is-continuation":"true",'
    root_replacement = root_anchor + ''.join((
        '"data-seen-id":gate.visualization_metaphor_closure?.seen_id||"",',
        '"data-metaphor-class-id":gate.visualization_metaphor_closure?.metaphor_class_id||"",',
        '"data-visual-equality-is-seen-equality":"true",',
        '"data-labels-author-visual-equality":"false",',
        '"data-renderer-authors-visual-equality":"false",',
        '"data-crystal-ball-is-local-chart":"true",',
    ))
    if root_anchor not in body:
        raise RuntimeError("NRRF885 root anchor changed")
    body = body.replace(root_anchor, root_replacement, 1)

    required = (
        "visualization_metaphor_closure",
        "SEEN_ID_EQUALITY",
        "visualizationCurrent(active,path)",
        "data-fold-class-id",
        "data-crystal-ball-id",
        "data-seen-id",
        "data-metaphor-class-id",
        "data-visual-equality-is-seen-equality",
    )
    if not all(token in body for token in required):
        raise RuntimeError("NRRF885 metaphor visualization surface was not installed")
    return body


POTENTIAL_GATE_SUPERNET_HTML = _metaphor_surface(_BASE_HTML)

__all__ = ["POTENTIAL_GATE_SUPERNET_HTML"]
