from __future__ import annotations

"""Browser realization of one persistent Supernet translation field.

Returned revisions remain exact digital control points, but the visible carrier
flows between them.  The interpolation is presentation-only: it cannot author
truth, Seen equality, natural forms, or returned determination.
"""

from .visualization_metaphor_interface import POTENTIAL_GATE_SUPERNET_HTML as _BASE_HTML


def _continuous_surface(html: str) -> str:
    body = html

    verifier_anchor = (
        'if(full.visualization_metaphor_closure_id!==metaphor.id)return false;'
    )
    verifier = verifier_anchor + r'''
  const continuous=gate.continuous_translation_field;
  if(!isRecord(continuous))return false;
  if(continuous.id!==await digest("continuous-translation-field",withoutId(continuous)))return false;
  if(full.continuous_translation_field_id!==continuous.id)return false;
  if(continuous.persistent_visual_carrier!==true)return false;
  if(continuous.returned_revisions_are_control_points_not_visual_worlds!==true)return false;
  if(continuous.visual_translation_is_continuous_between_returns!==true)return false;
  if(continuous.return_deforms_same_field!==true)return false;
  if(continuous.interpolation_authors_truth!==false||continuous.interpolation_authors_seen!==false)return false;
  if(continuous.interpolation_authors_natural_form!==false||continuous.interpolation_authors_return!==false)return false;
  for(const row of continuous.currents||[]){
    if(!isRecord(row)||row.id!==await digest("continuous-translation-current",withoutId(row)))return false;
    if(row.continuous_between_control_points!==true)return false;
    if(row.interpolation_authors_truth!==false||row.interpolation_authors_seen!==false||row.interpolation_authors_return!==false)return false;
  }'''
    if verifier_anchor not in body:
        raise RuntimeError("continuous translation verifier anchor changed")
    body = body.replace(verifier_anchor, verifier, 1)

    current_fn = r'''function visualizationCurrent(full,path){
  const rows=full?.relative_natural_form_potential_gate?.visualization_metaphor_closure?.currents||[];
  return rows.find(row=>row.path_id===path.id)||null;
}'''
    continuous_fn = current_fn + r'''
function continuousCurrent(full,path){
  const rows=full?.relative_natural_form_potential_gate?.continuous_translation_field?.currents||[];
  return rows.find(row=>row.path_id===path.id)||null;
}
let translationFlowEpoch=0;
let slidePhase=0;
function quadraticNumbers(d){return(String(d||"").match(/-?\d+(?:\.\d+)?/g)||[]).map(Number)}
function quadraticPath(numbers){
  if(numbers.length<6)return null;
  return`M ${numbers[0].toFixed(2)} ${numbers[1].toFixed(2)} Q ${numbers[2].toFixed(2)} ${numbers[3].toFixed(2)} ${numbers[4].toFixed(2)} ${numbers[5].toFixed(2)}`
}
function interpolatePath(fromD,toD,t){
  const a=quadraticNumbers(fromD),b=quadraticNumbers(toD);if(a.length!==b.length||a.length<6)return toD;
  const n=a.map((value,index)=>value+(b[index]-value)*t);return quadraticPath(n)||toD
}
function targetPathD(next,pathId,familyId){
  const geometry=gateGeometry(next),path=geometry.paths.find(item=>item.id===pathId);if(!path)return null;
  const solutions=next?.potential_gate_natural_form_solver?.solutions||[];
  const solution=solutions.find(item=>item.family_id===familyId)||solutions[0];if(!solution)return null;
  return pathD(path.points.map(point=>solvePoint(solution,point)))
}
function flowTranslation(next,path){
  if(!next)return;const epoch=++translationFlowEpoch,root=surface.firstElementChild;
  if(!root){active=next;activeRelationId=null;draft="";sensor.value="";render();return}
  const nodes=[...root.querySelectorAll("[data-potential-gate-path-id]")].map(node=>({
    node,
    from:node.getAttribute("d")||"",
    to:targetPathD(next,node.dataset.potentialGatePathId,node.parentElement?.dataset?.naturalFormFamily||""),
    opacity:Number(node.getAttribute("opacity")||1)
  }));
  const started=performance.now(),duration=720;
  root.dataset.translationFlow="true";root.dataset.translationControlPointFrom=active?.id||"";root.dataset.translationControlPointTo=next.id||"";
  const frame=now=>{
    if(epoch!==translationFlowEpoch)return;const u=Math.max(0,Math.min(1,(now-started)/duration));const t=u*u*(3-2*u);
    for(const item of nodes){
      if(item.to)item.node.setAttribute("d",interpolatePath(item.from,item.to,t));
      else item.node.setAttribute("opacity",String(item.opacity*(1-t)));
    }
    root.dataset.translationPhase=String(t);
    root.style.transform=`scale(${(1+.012*Math.sin(Math.PI*t)).toFixed(5)})`;
    root.style.opacity=String(.92+.08*Math.cos(Math.PI*2*t));
    if(u<1){requestAnimationFrame(frame);return}
    active=next;activeRelationId=null;draft="";sensor.value="";render();
    const fresh=surface.firstElementChild;if(fresh){fresh.dataset.translationFlow="true";fresh.dataset.translationPhase="1";fresh.dataset.translationControlPointTo=next.id||""}
  };
  requestAnimationFrame(frame)
}
function animateCurrentFlow(now){
  slidePhase=(now*.00008)%1;
  const root=surface.firstElementChild;if(root){
    root.dataset.slidePhase=String(slidePhase);
    for(const node of root.querySelectorAll('[data-continuing="true"]')){
      const seed=deterministicUnit(node.dataset.visualizationCurrentId||node.dataset.potentialGatePathId||"");
      node.style.strokeDashoffset=String(-((now*.012)*(0.45+seed))%96);
      node.dataset.currentPhase=String((slidePhase+seed)%1)
    }
  }
  requestAnimationFrame(animateCurrentFlow)
}
requestAnimationFrame(animateCurrentFlow);'''
    if current_fn not in body:
        raise RuntimeError("visualizationCurrent anchor changed")
    body = body.replace(current_fn, continuous_fn, 1)

    start = body.find("function animateTransport(oldRoot,next,path){")
    end = body.find("\n\nasync function navigateRelation", start)
    if start < 0 or end < 0:
        raise RuntimeError("transport function anchor changed")
    body = body[:start] + "function animateTransport(oldRoot,next,path){flowTranslation(next,path)}" + body[end:]

    # The return path used to replace the active scene immediately.  It now
    # flows through the same persistent carrier used by navigation.
    old_return = 'active=next;activeRelationId=null;draft="";sensor.value="";render();'
    if old_return not in body:
        raise RuntimeError("return replacement anchor changed")
    body = body.replace(old_return, 'flowTranslation(next,path);', 1)

    render_anchor = (
        'const continuum=continuumRelation(active,path);const current=visualizationCurrent(active,path);const node=svg("path",{'
    )
    render_replacement = (
        'const continuum=continuumRelation(active,path);const current=visualizationCurrent(active,path);'
        'const flowCurrent=continuousCurrent(active,path);const node=svg("path",{'
    )
    if render_anchor not in body:
        raise RuntimeError("continuous render anchor changed")
    body = body.replace(render_anchor, render_replacement, 1)

    attrs_anchor = '"data-rotation-class-id":current?.rotation_class_id||"",'
    attrs_replacement = attrs_anchor + ''.join((
        '"data-continuous-current-id":flowCurrent?.id||"",',
        '"data-continuous-between-control-points":flowCurrent?.continuous_between_control_points===true,',
        '"data-semantic-control-point":flowCurrent?.semantic_control_point===true,',
    ))
    if attrs_anchor not in body:
        raise RuntimeError("continuous current attributes anchor changed")
    body = body.replace(attrs_anchor, attrs_replacement, 1)

    root_anchor = '"data-crystal-ball-is-local-chart":"true",'
    root_replacement = root_anchor + ''.join((
        '"data-continuous-translation-field":"true",',
        '"data-persistent-visual-carrier":"true",',
        '"data-returned-revisions-are-control-points":"true",',
        '"data-discrete-visual-instance":"false",',
    ))
    if root_anchor not in body:
        raise RuntimeError("continuous root anchor changed")
    body = body.replace(root_anchor, root_replacement, 1)

    required = (
        "continuous_translation_field",
        "flowTranslation(next,path)",
        "requestAnimationFrame(animateCurrentFlow)",
        "data-continuous-current-id",
        "data-persistent-visual-carrier",
        "data-discrete-visual-instance",
        "returned_revisions_are_control_points_not_visual_worlds",
    )
    if not all(token in body for token in required):
        raise RuntimeError("continuous translation field surface was not installed")
    return body


POTENTIAL_GATE_SUPERNET_HTML = _continuous_surface(_BASE_HTML)

__all__ = ["POTENTIAL_GATE_SUPERNET_HTML"]
