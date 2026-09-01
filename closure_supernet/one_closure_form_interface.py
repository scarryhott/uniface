from __future__ import annotations

"""Browser projection of the one Supernet closure form.

The DOM no longer chooses semantics independently from the gate's component
objects. It resolves each visible relation through `supernet_closure_form` and
uses that one record for opener/UI/interaction, AI-token phase, crystal-ball
current identity and return-vs-navigation behavior.
"""

from .continuous_translation_interface import POTENTIAL_GATE_SUPERNET_HTML as _BASE_HTML


def _one_form_surface(html: str) -> str:
    body = html

    verifier_anchor = 'if(full.continuous_translation_field_id!==continuous.id)return false;'
    verifier = verifier_anchor + r'''
  const closureForm=full.supernet_closure_form;
  if(!isRecord(closureForm))return false;
  if(closureForm.id!==await digest("supernet-one-closure-form",withoutId(closureForm)))return false;
  if(full.supernet_closure_form_id!==closureForm.id)return false;
  if(full.published_semantic_carrier!=="SUPERNET_CLOSURE_FORM")return false;
  if(closureForm.opener_ui_interaction_are_one_form!==true)return false;
  if(closureForm.crystal_ball_slide_ai_token_are_one_form!==true)return false;
  if(closureForm.single_published_semantic_carrier!==true)return false;
  if(closureForm.persistent_visual_carrier!==true)return false;
  for(const row of closureForm.interactions||[]){
    if(!isRecord(row)||row.id!==await digest("supernet-closure-interaction",withoutId(row)))return false;
    if(row.opener_is_this_form!==true||row.ui_is_this_form!==true)return false;
    if(row.interaction_is_translation_of_this_form!==true)return false;
    if(row.return_is_determination_of_this_form!==true)return false;
    if(!["AI_CONTINUING","TOKEN_RETURNED"].includes(row.ai_token_phase))return false;
  }'''
    if verifier_anchor not in body:
        raise RuntimeError("one-form verifier anchor changed")
    body = body.replace(verifier_anchor, verifier, 1)

    current_anchor = r'''function continuousCurrent(full,path){
  const rows=full?.relative_natural_form_potential_gate?.continuous_translation_field?.currents||[];
  return rows.find(row=>row.path_id===path.id)||null;
}'''
    one_form_fn = current_anchor + r'''
function closureInteraction(full,path){
  const rows=full?.supernet_closure_form?.interactions||[];
  return rows.find(row=>row.path_id===path.id)||null;
}'''
    if current_anchor not in body:
        raise RuntimeError("one-form interaction anchor changed")
    body = body.replace(current_anchor, one_form_fn, 1)

    activate_old = (
        'const closureRelation=continuumRelation(active,path);'
        'if(closureRelation?.returned===true&&(path.action==="PERSPECTIVE_TRANSPORT"||path.action==="LOCALITY_TRANSPORT")){navigateRelation(path);return}'
    )
    activate_new = (
        'const oneForm=closureInteraction(active,path);'
        'if(oneForm?.ai_token_phase==="TOKEN_RETURNED"&&(path.action==="PERSPECTIVE_TRANSPORT"||path.action==="LOCALITY_TRANSPORT")){navigateRelation(path);return}'
    )
    if activate_old not in body:
        raise RuntimeError("one-form activate anchor changed")
    body = body.replace(activate_old, activate_new, 1)

    submit_old = (
        'const path=activePath(active);const closureRelation=path?continuumRelation(active,path):null;'
        'if(returning||!active||!path||closureRelation?.returned===true||!draft.trim())return;returning=true;'
    )
    submit_new = (
        'const path=activePath(active);const oneForm=path?closureInteraction(active,path):null;'
        'if(returning||!active||!path||oneForm?.ai_token_phase==="TOKEN_RETURNED"||!draft.trim())return;returning=true;'
    )
    if submit_old not in body:
        raise RuntimeError("one-form submit anchor changed")
    body = body.replace(submit_old, submit_new, 1)

    render_anchor = (
        'const continuum=continuumRelation(active,path);const current=visualizationCurrent(active,path);'
        'const flowCurrent=continuousCurrent(active,path);const node=svg("path",{'
    )
    render_new = (
        'const continuum=continuumRelation(active,path);const current=visualizationCurrent(active,path);'
        'const flowCurrent=continuousCurrent(active,path);const oneForm=closureInteraction(active,path);const node=svg("path",{'
    )
    if render_anchor not in body:
        raise RuntimeError("one-form render anchor changed")
    body = body.replace(render_anchor, render_new, 1)

    attrs_anchor = '"data-semantic-control-point":flowCurrent?.semantic_control_point===true,'
    attrs_new = attrs_anchor + ''.join((
        '"data-supernet-closure-interaction-id":oneForm?.id||"",',
        '"data-ai-token-phase":oneForm?.ai_token_phase||"AI_CONTINUING",',
        '"data-one-closure-form":"true",',
        '"data-opener-ui-interaction-one-form":oneForm?.opener_is_this_form===true&&oneForm?.ui_is_this_form===true,',
    ))
    if attrs_anchor not in body:
        raise RuntimeError("one-form relation attrs anchor changed")
    body = body.replace(attrs_anchor, attrs_new, 1)

    root_anchor = '"data-discrete-visual-instance":"false",'
    root_new = root_anchor + ''.join((
        '"data-published-semantic-carrier":"SUPERNET_CLOSURE_FORM",',
        '"data-supernet-closure-form-id":active?.supernet_closure_form_id||"",',
        '"data-opener-ui-interaction-one-form":"true",',
        '"data-crystal-ball-slide-ai-token-one-form":"true",',
    ))
    if root_anchor not in body:
        raise RuntimeError("one-form root anchor changed")
    body = body.replace(root_anchor, root_new, 1)

    required = (
        "supernet_closure_form",
        "closureInteraction(active,path)",
        "AI_CONTINUING",
        "TOKEN_RETURNED",
        "data-supernet-closure-form-id",
        "data-opener-ui-interaction-one-form",
        "data-crystal-ball-slide-ai-token-one-form",
    )
    if not all(token in body for token in required):
        raise RuntimeError("one Supernet closure form surface was not installed")
    return body


POTENTIAL_GATE_SUPERNET_HTML = _one_form_surface(_BASE_HTML)

__all__ = ["POTENTIAL_GATE_SUPERNET_HTML"]
