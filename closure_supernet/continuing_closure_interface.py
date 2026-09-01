from __future__ import annotations

"""Browser surface for closure as returned + continuing translation family.

Legacy WITNESSED/OPEN path status remains inside the verified predecessor
contract, but the published surface reads only the canonical continuum:
RETURNED paths navigate; CONTINUING paths expose continuation/return input.
"""

from .equal_user_token_visual_interface import POTENTIAL_GATE_SUPERNET_HTML as _BASE_HTML


def _continuing_surface(html: str) -> str:
    body = html

    verifier_anchor = (
        'if(full.equal_user_token_visual_identification_id!==visualIdentification.id)return false;'
    )
    verifier = verifier_anchor + r'''
  const continuum=gate.continuing_translation_closure;
  if(!isRecord(continuum))return false;
  if(continuum.id!==await digest("continuing-translation-closure",withoutId(continuum)))return false;
  if(full.continuing_translation_closure_id!==continuum.id)return false;
  if(full.closure_is_continuation_of_all!==true)return false;
  if(full.returned_and_continuing_are_states_inside_one_closure!==true)return false;
  if(full.ui_visualizes_natural_forms_selected_in_translation_closure!==true)return false;
  if(full.legacy_status_vocabulary_is_compatibility_only!==true)return false;
  if(JSON.stringify(full.published_relation_states)!==JSON.stringify(["RETURNED","CONTINUING"]))return false;
  if(continuum.closure_contains_every_current_translation!==true)return false;
  if(continuum.continuation_is_inside_closure!==true)return false;
  if(continuum.nonreturned_relation_is_continuation_not_nonclosure!==true)return false;
  if(continuum.returned_is_determination_not_membership!==true)return false;
  const continuumPathIds=new Set((continuum.relations||[]).map(row=>row.path_id));
  if(continuumPathIds.size!==(gate.paths||[]).length)return false;
  for(const row of continuum.relations||[]){
    if(!isRecord(row)||row.id!==await digest("continuing-translation-relation",withoutId(row)))return false;
    if(!["RETURNED","CONTINUING"].includes(row.closure_state))return false;
    if((row.returned===true)===(row.continuing===true))return false;
    if(row.returned===true&&row.closure_state!=="RETURNED")return false;
    if(row.continuing===true&&row.closure_state!=="CONTINUING")return false;
    if(row.membership_in_closure_is_unconditional!==true)return false;
  }'''
    if verifier_anchor not in body:
        raise RuntimeError("continuing closure verifier anchor changed")
    body = body.replace(verifier_anchor, verifier, 1)

    visual_fn = (
        'function visualInteraction(full,path){\n  const rows=full?.relative_natural_form_potential_gate?.equal_user_token_visual_identification?.relations||[];\n  return rows.find(row=>row.path_id===path.id)||null;\n}'
    )
    continuum_fn = visual_fn + r'''
function continuumRelation(full,path){
  const rows=full?.relative_natural_form_potential_gate?.continuing_translation_closure?.relations||[];
  return rows.find(row=>row.path_id===path.id)||null;
}'''
    if visual_fn not in body:
        raise RuntimeError("visualInteraction anchor changed")
    body = body.replace(visual_fn, continuum_fn, 1)

    body = body.replace(
        '.gate-path[data-status="WITNESSED"]{stroke-width:3.2}',
        '.gate-path[data-status="RETURNED"]{stroke-width:3.2}',
        1,
    )
    body = body.replace(
        '.gate-path[data-status="OPEN"]{stroke-width:2.1;stroke-dasharray:7 9}',
        '.gate-path[data-status="CONTINUING"]{stroke-width:2.1;stroke-dasharray:7 9}',
        1,
    )

    old_activate = (
        'function activateRelation(path){activeRelationId=path.id;draft="";sensor.value="";if(path.status==="WITNESSED"&&(path.action==="PERSPECTIVE_TRANSPORT"||path.action==="LOCALITY_TRANSPORT")){navigateRelation(path);return}sensor.focus({preventScroll:true});render()}'
    )
    new_activate = (
        'function activateRelation(path){activeRelationId=path.id;draft="";sensor.value="";'
        'const closureRelation=continuumRelation(active,path);'
        'if(closureRelation?.returned===true&&(path.action==="PERSPECTIVE_TRANSPORT"||path.action==="LOCALITY_TRANSPORT")){navigateRelation(path);return}'
        'sensor.focus({preventScroll:true});render()}'
    )
    if old_activate not in body:
        raise RuntimeError("activateRelation anchor changed")
    body = body.replace(old_activate, new_activate, 1)

    old_fibre = (
        'function activateFibre(fibre){const path=(active?.relative_natural_form_potential_gate?.paths||[]).find(item=>item.target_state_id&&(fibre.member_state_ids||[]).includes(item.target_state_id)&&item.status==="WITNESSED");if(path)activateRelation(path)}'
    )
    new_fibre = (
        'function activateFibre(fibre){const path=(active?.relative_natural_form_potential_gate?.paths||[]).find(item=>item.target_state_id&&(fibre.member_state_ids||[]).includes(item.target_state_id)&&continuumRelation(active,item)?.returned===true);if(path)activateRelation(path)}'
    )
    if old_fibre not in body:
        raise RuntimeError("activateFibre anchor changed")
    body = body.replace(old_fibre, new_fibre, 1)

    old_submit = (
        'const path=activePath(active);if(returning||!active||!path||path.status==="WITNESSED"||!draft.trim())return;returning=true;'
    )
    new_submit = (
        'const path=activePath(active);const closureRelation=path?continuumRelation(active,path):null;'
        'if(returning||!active||!path||closureRelation?.returned===true||!draft.trim())return;returning=true;'
    )
    if old_submit not in body:
        raise RuntimeError("submitReturn anchor changed")
    body = body.replace(old_submit, new_submit, 1)

    render_anchor = (
        'const selected=path.id===activeRelationId;const visual=visualInteraction(active,path);const node=svg("path",{'
    )
    render_replacement = (
        'const selected=path.id===activeRelationId;const visual=visualInteraction(active,path);'
        'const continuum=continuumRelation(active,path);const node=svg("path",{'
    )
    if render_anchor not in body:
        raise RuntimeError("render path anchor changed")
    body = body.replace(render_anchor, render_replacement, 1)

    body = body.replace(
        'stroke:`hsl(${hue} 72% ${path.status==="WITNESSED"?68:62}%)`',
        'stroke:`hsl(${hue} 72% ${continuum?.returned===true?68:62}%)`',
        1,
    )
    body = body.replace(
        '"data-status":path.status',
        '"data-status":continuum?.closure_state||"CONTINUING","data-legacy-status":path.status,"data-returned":continuum?.returned===true,"data-continuing":continuum?.continuing===true',
        1,
    )
    body = body.replace(
        '"data-navigation":path.status==="WITNESSED","data-return-aperture":path.status!=="WITNESSED"',
        '"data-navigation":continuum?.returned===true,"data-continuation-aperture":continuum?.continuing===true,"data-return-aperture":continuum?.continuing===true',
        1,
    )

    old_surface_click = (
        'surface.addEventListener("click",()=>{const open=(active?.relative_natural_form_potential_gate?.paths||[]).find(path=>path.status!=="WITNESSED");if(open)activateRelation(open)});'
    )
    new_surface_click = (
        'surface.addEventListener("click",()=>{const continuing=(active?.relative_natural_form_potential_gate?.paths||[]).find(path=>continuumRelation(active,path)?.continuing===true);if(continuing)activateRelation(continuing)});'
    )
    if old_surface_click not in body:
        raise RuntimeError("surface continuation anchor changed")
    body = body.replace(old_surface_click, new_surface_click, 1)

    root_anchor = '"data-ui-is-relative-user-token-interaction":"true",'
    root_replacement = root_anchor + ''.join((
        '"data-closure-is-continuation-of-all":"true",',
        '"data-published-relation-states":"RETURNED_CONTINUING",',
        '"data-nonreturned-is-continuation":"true",',
    ))
    if root_anchor not in body:
        raise RuntimeError("root continuation anchor changed")
    body = body.replace(root_anchor, root_replacement, 1)

    required = (
        "continuing_translation_closure",
        "continuumRelation(active,path)",
        'data-status\":continuum?.closure_state',
        "data-continuing",
        "data-closure-is-continuation-of-all",
        "RETURNED_CONTINUING",
    )
    if not all(token in body for token in required):
        raise RuntimeError("continuing closure surface was not installed")
    return body


POTENTIAL_GATE_SUPERNET_HTML = _continuing_surface(_BASE_HTML)

__all__ = ["POTENTIAL_GATE_SUPERNET_HTML"]
