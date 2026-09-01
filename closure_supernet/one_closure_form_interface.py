from __future__ import annotations

"""Browser execution of one Supernet closure form and NRRF892 slide identity.

Every visible relation executes ``SUPERNET_TRANSLATE``. Where the current
interaction lies in the NRRF892 vision-chart domain, the browser verifies that
its translation-truth orbit and vision-crystal orbit are the same identifier.
The server's content-addressed translation receipt is then consumed as the
visible trajectory; no second browser transition is allowed.
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
  if(full.translation_operator!=="SUPERNET_TRANSLATE")return false;
  if(full.runtime_identity_id!==closureForm.runtime_identity_id)return false;
  if(full.runtime_identity_is_translational_truth!==true||closureForm.runtime_identity_is_translational_truth!==true)return false;
  if(full.vision_slide_operator!=="VISION_SLIDE_TRANS"||closureForm.vision_slide_operator!=="VISION_SLIDE_TRANS")return false;
  if(closureForm.translation_operator!=="SUPERNET_TRANSLATE")return false;
  if(closureForm.opener_ui_interaction_are_one_form!==true)return false;
  if(closureForm.crystal_ball_slide_ai_token_are_one_form!==true)return false;
  if(closureForm.single_published_semantic_carrier!==true)return false;
  if(closureForm.persistent_visual_carrier!==true)return false;
  if(closureForm.browser_transition_is_runtime_transition!==true)return false;
  if(closureForm.state_transition_is_visual_transition!==true)return false;
  if(closureForm.single_transition_operator!==true)return false;
  if(closureForm.rotationless_fold_claimed!==false)return false;
  if(closureForm.separate_navigation_operator!==false||closureForm.separate_return_operator!==false)return false;
  for(const row of closureForm.interactions||[]){
    if(!isRecord(row)||row.id!==await digest("supernet-closure-interaction",withoutId(row)))return false;
    if(row.runtime_identity_id!==closureForm.runtime_identity_id||row.runtime_identity_is_translational_truth!==true)return false;
    if(row.opener_is_this_form!==true||row.ui_is_this_form!==true)return false;
    if(row.interaction_is_translation_of_this_form!==true)return false;
    if(row.return_is_determination_of_this_form!==true)return false;
    if(row.translation_operator!=="SUPERNET_TRANSLATE"||row.vision_slide_operator!=="VISION_SLIDE_TRANS")return false;
    if(row.browser_transition_is_runtime_transition!==true)return false;
    if(row.separate_navigation_operator!==false||row.separate_return_operator!==false)return false;
    if(!["AI_CONTINUING","TOKEN_RETURNED"].includes(row.ai_token_phase))return false;
    const vision=row.nrrf892_vision_bridge;
    if(!isRecord(vision)||vision.id!==await digest("nrrf892-runtime-vision-bridge",withoutId(vision)))return false;
    if(vision.translation_truth_orbit_id!==row.translation_truth_orbit_id)return false;
    if(vision.vision_crystal_orbit_id!==row.vision_crystal_orbit_id)return false;
    if(vision.rotationless_fold_claimed!==false)return false;
    if(vision.vision_chart_admitted===true){
      if(vision.vision_crystal_orbit_id!==vision.translation_truth_orbit_id)return false;
      if(vision.supernet_translate_is_vision_slide!==true||row.supernet_translate_is_vision_slide!==true)return false;
      if(vision.slide_is_closure_family_member!==true)return false;
      if(vision.slide_gravitational_ratio?.num!==1||vision.slide_gravitational_ratio?.den!==1)return false;
    }else if(vision.vision_crystal_orbit_id!==null)return false;
  }'''
    if verifier_anchor not in body:
        raise RuntimeError("one-form verifier anchor changed")
    body = body.replace(verifier_anchor, verifier, 1)

    current_anchor = r'''function continuousCurrent(full,path){
  const rows=full?.relative_natural_form_potential_gate?.continuous_translation_field?.currents||[];
  return rows.find(row=>row.path_id===path.id)||null;
}'''
    one_form_fn = current_anchor + r'''
const LEGACY_INTERACTION_VOCABULARY_COMPATIBILITY_ONLY=["PERSPECTIVE_NAVIGATION","POTENTIAL_GATE_RETURN","OPEN_RETURN_EXTENSION"];
function closureInteraction(full,path){
  const rows=full?.supernet_closure_form?.interactions||[];
  return rows.find(row=>row.path_id===path.id)||null;
}
async function translationMatches(translation,source,next,path){
  const oneForm=closureInteraction(source,path);
  if(!isRecord(translation)||!isRecord(oneForm)||!isRecord(next))return false;
  if(translation.id!==await digest("supernet-translate",withoutId(translation)))return false;
  if(translation.schema!=="closure.supernet/supernet-translate-v1")return false;
  if(translation.operator!=="SUPERNET_TRANSLATE"||translation.vision_slide_operator!=="VISION_SLIDE_TRANS")return false;
  if(translation.relation_id!==path.id)return false;
  if(translation.source_gate_id!==source.id||translation.target_gate_id!==next.id)return false;
  if(translation.source_closure_form_id!==source.supernet_closure_form_id)return false;
  if(translation.target_closure_form_id!==next.supernet_closure_form_id)return false;
  if(translation.source_interaction_id!==oneForm.id)return false;
  if(translation.source_ai_token_phase!==oneForm.ai_token_phase)return false;
  if(translation.runtime_identity_is_translational_truth!==true)return false;
  if(translation.source_runtime_identity_id!==source.runtime_identity_id)return false;
  if(translation.target_runtime_identity_id!==next.runtime_identity_id)return false;
  if(translation.source_translation_truth_orbit_id!==oneForm.translation_truth_orbit_id)return false;
  if(translation.source_vision_crystal_orbit_id!==oneForm.vision_crystal_orbit_id)return false;
  if(translation.token_continuation_source_orbit_id!==oneForm.translation_truth_orbit_id)return false;
  if(translation.truth_refined===false){
    if(translation.runtime_identity_preserved!==true||translation.translational_truth_preserved!==true)return false;
    if(translation.source_runtime_identity_id!==translation.target_runtime_identity_id)return false;
  }
  if(oneForm.nrrf892_vision_bridge?.vision_chart_admitted===true){
    if(translation.supernet_translate_is_vision_slide!==true)return false;
    if(translation.source_vision_crystal_orbit_id!==translation.source_translation_truth_orbit_id)return false;
  }
  if(translation.runtime_state_change_is_this_translation!==true)return false;
  if(translation.browser_trajectory_is_this_translation!==true)return false;
  if(translation.semantic_transition_is_visual_transition!==true)return false;
  if(translation.separate_navigation_operator!==false||translation.separate_return_operator!==false)return false;
  return true
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
        '"data-translation-operator":oneForm?.translation_operator||"",',
        '"data-runtime-identity-id":oneForm?.runtime_identity_id||"",',
        '"data-translation-truth-orbit-id":oneForm?.translation_truth_orbit_id||"",',
        '"data-vision-crystal-orbit-id":oneForm?.vision_crystal_orbit_id||"",',
        '"data-vision-slide-operator":oneForm?.vision_slide_operator||"",',
        '"data-vision-chart-admitted":oneForm?.nrrf892_vision_bridge?.vision_chart_admitted===true,',
        '"data-one-closure-form":"true",',
        '"data-browser-transition-is-runtime-transition":oneForm?.browser_transition_is_runtime_transition===true,',
        '"data-opener-ui-interaction-one-form":oneForm?.opener_is_this_form===true&&oneForm?.ui_is_this_form===true,',
    ))
    if attrs_anchor not in body:
        raise RuntimeError("one-form relation attrs anchor changed")
    body = body.replace(attrs_anchor, attrs_new, 1)

    root_anchor = '"data-discrete-visual-instance":"false",'
    root_new = root_anchor + ''.join((
        '"data-published-semantic-carrier":"SUPERNET_CLOSURE_FORM",',
        '"data-supernet-closure-form-id":active?.supernet_closure_form_id||"",',
        '"data-runtime-identity-id":active?.runtime_identity_id||"",',
        '"data-runtime-identity-is-translational-truth":"true",',
        '"data-translation-operator":"SUPERNET_TRANSLATE",',
        '"data-vision-slide-operator":"VISION_SLIDE_TRANS",',
        '"data-browser-transition-is-runtime-transition":"true",',
        '"data-state-transition-is-visual-transition":"true",',
        '"data-opener-ui-interaction-one-form":"true",',
        '"data-crystal-ball-slide-ai-token-one-form":"true",',
    ))
    if root_anchor not in body:
        raise RuntimeError("one-form root anchor changed")
    body = body.replace(root_anchor, root_new, 1)

    flow_signature = 'function flowTranslation(next,path){'
    if flow_signature not in body:
        raise RuntimeError("one-form translation-flow signature changed")
    body = body.replace(flow_signature, 'function flowTranslation(next,path,translation){', 1)
    flow_dataset = 'root.dataset.translationFlow="true";root.dataset.translationControlPointFrom=active?.id||"";root.dataset.translationControlPointTo=next.id||"";'
    if flow_dataset not in body:
        raise RuntimeError("one-form translation-flow dataset anchor changed")
    body = body.replace(
        flow_dataset,
        flow_dataset + 'root.dataset.translationReceiptId=translation?.id||"";root.dataset.translationOperator=translation?.operator||"";root.dataset.runtimeIdentityId=translation?.source_runtime_identity_id||"";root.dataset.translationTruthOrbitId=translation?.source_translation_truth_orbit_id||"";root.dataset.visionCrystalOrbitId=translation?.source_vision_crystal_orbit_id||"";root.dataset.visionSlideOperator=translation?.vision_slide_operator||"";root.dataset.tokenContinuationSourceOrbitId=translation?.token_continuation_source_orbit_id||"";',
        1,
    )
    flow_finish = 'active=next;activeRelationId=null;draft="";sensor.value="";render();'
    if flow_finish not in body:
        raise RuntimeError("one-form translation-flow completion anchor changed")
    body = body.replace(
        flow_finish,
        'const keep=translation?.source_gate_id===translation?.target_gate_id&&translation?.source_ai_token_phase==="AI_CONTINUING";active=next;activeRelationId=keep?path?.id:null;if(!keep){draft="";sensor.value=""}render();if(keep)sensor.focus({preventScroll:true});',
        1,
    )

    nav_start = body.find('async function navigateRelation(path){')
    activate_start = body.find('function activateRelation(path){', nav_start)
    fibre_start = body.find('function activateFibre', activate_start)
    if nav_start < 0 or activate_start < 0 or fibre_start < 0:
        raise RuntimeError("one-form legacy navigation block changed")
    translate_block = r'''async function translateClosureForm(path,exactSource=""){
  if(navigating||returning||!active||!path)return;
  const source=active,oneForm=closureInteraction(source,path);if(!oneForm)return;
  navigating=true;returning=true;
  try{
    const response=await fetch(`/supernet/interface/projections/${encodeURIComponent(source.id)}/return`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({relation_id:path.id,perspective_id:source.perspective_id,focus_event_id:source.focus_event_id??null,navigation_context:source.navigation_context,source_closure_form_id:source.supernet_closure_form_id,source_interaction_id:oneForm.id,exact_source_return:String(exactSource||"").trim(),local_perspective_hair_millidegrees:localHairMillidegrees,local_perspective_zoom_milli:localZoomMilli})});
    if(response.status===409){await loadInitial();return}if(!response.ok)throw new Error(`translate:${response.status}`);
    const payload=await response.json(),next=payload.supernet_potential_gate,translation=payload.translation;
    if(!payload.translated||payload.operator!=="SUPERNET_TRANSLATE"||!await contractMatches(next)||!await translationMatches(translation,source,next,path))throw new Error("unverified-supernet-translation");
    const url=new URL(location.href);url.searchParams.set("perspective_id",next.perspective_id);if(next.focus_event_id)url.searchParams.set("focus_event_id",next.focus_event_id);else url.searchParams.delete("focus_event_id");
    if(translation.target_gate_id!==translation.source_gate_id)history.pushState({gate:next},"",url);
    flowTranslation(next,path,translation)
  }finally{navigating=false;returning=false}
}
function activateRelation(path){activeRelationId=path.id;draft="";sensor.value="";translateClosureForm(path,"").catch(error=>surface.dataset.error=asText(error?.message||error))}
'''
    body = body[:nav_start] + translate_block + body[fibre_start:]

    submit_start = body.find('async function submitReturn(){')
    render_start = body.find('\n\nfunction render(){', submit_start)
    if submit_start < 0 or render_start < 0:
        raise RuntimeError("one-form legacy return block changed")
    submit_block = r'''async function translateActiveReturn(){
  const path=activePath(active),oneForm=path?closureInteraction(active,path):null;
  if(!active||!path||!oneForm||oneForm.ai_token_phase==="TOKEN_RETURNED"||!draft.trim())return;
  await translateClosureForm(path,draft.trim())
}'''
    body = body[:submit_start] + submit_block + body[render_start:]
    if 'submitReturn()' not in body:
        raise RuntimeError("one-form return key handler changed")
    body = body.replace('submitReturn()', 'translateActiveReturn()', 1)

    required = (
        "supernet_closure_form",
        "SUPERNET_TRANSLATE",
        "VISION_SLIDE_TRANS",
        "runtime_identity_is_translational_truth",
        "translation_truth_orbit_id",
        "vision_crystal_orbit_id",
        "translationMatches(translation,source,next,path)",
        "/supernet/interface/projections/${encodeURIComponent(source.id)}/return",
        "flowTranslation(next,path,translation)",
        "data-supernet-closure-form-id",
        "data-runtime-identity-id",
        "data-translation-truth-orbit-id",
        "data-vision-crystal-orbit-id",
        "data-vision-slide-operator",
        "data-browser-transition-is-runtime-transition",
        "data-opener-ui-interaction-one-form",
        "data-crystal-ball-slide-ai-token-one-form",
    )
    if not all(token in body for token in required):
        raise RuntimeError("one Supernet translation surface was not installed")
    if 'async function navigateRelation(path)' in body or 'async function submitReturn()' in body:
        raise RuntimeError("separate browser transition operators remain")
    return body


POTENTIAL_GATE_SUPERNET_HTML = _one_form_surface(_BASE_HTML)

__all__ = ["POTENTIAL_GATE_SUPERNET_HTML"]
