from __future__ import annotations

"""Browser surface for the full relative natural-form potential gate.

The page is one physical aperture.  Every visible path is the corresponding
Supernet gate path: a perspectival transport, locality transport, or OPEN
return extension.  There is no independent page/navigation ontology.
"""

POTENTIAL_GATE_SUPERNET_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover,user-scalable=no">
<title></title>
<style>
:root{color-scheme:dark}
*{box-sizing:border-box}
html,body{width:100%;height:100%;margin:0;overflow:hidden;background:#020305}
#translational-mirror{position:fixed;inset:0;overflow:hidden;touch-action:none;outline:none}
svg{display:block;width:100%;height:100%}
.gate-path{fill:none;stroke-linecap:round;vector-effect:non-scaling-stroke;pointer-events:stroke;cursor:pointer}
.gate-path[data-status="WITNESSED"]{stroke-width:3.2}
.gate-path[data-status="OPEN"]{stroke-width:2.1;stroke-dasharray:7 9}
.gate-path[data-active="true"]{stroke-width:5.4}
.gate-locality{fill:rgba(255,255,255,.018);vector-effect:non-scaling-stroke;pointer-events:all;cursor:pointer}
.gate-label{font:430 12px/1.2 ui-sans-serif,system-ui,sans-serif;fill:rgba(248,250,255,.72);text-anchor:middle;pointer-events:none}
.gate-draft{font:470 17px/1.25 ui-sans-serif,system-ui,sans-serif;fill:rgba(250,252,255,.94);text-anchor:middle;pointer-events:none}
</style>
</head>
<body>
<main id="translational-mirror"></main>
<script>
(()=>{
"use strict";
const NS="http://www.w3.org/2000/svg";
const surface=document.getElementById("translational-mirror");
const sensor=document.createElement("textarea");
sensor.id="return-sensor";sensor.setAttribute("aria-label","");
sensor.autocomplete="off";sensor.autocapitalize="sentences";sensor.spellcheck=true;
Object.assign(sensor.style,{position:"fixed",width:"1px",height:"1px",left:"50%",top:"50%",opacity:".001",border:"0",padding:"0",background:"transparent",color:"transparent",caretColor:"transparent"});
document.body.append(sensor);

const BASE_BASIS="GENERIC_BOUNDED_HARMONIC_EQUALITY_CLOSURE_BASIS";
const RELATION_PROVENANCE_PREFIX="natural-form-relation:";
let active=null;
let activeRelationId=null;
let draft="";
let localHairMillidegrees=0;
let localZoomMilli=1000;
let dragging=null;
let returning=false;
let navigating=false;

function asText(v){return v===null||v===undefined?"":String(v)}
function isRecord(v){return !!v&&typeof v==="object"&&!Array.isArray(v)}
function unique(v){return [...new Set((v||[]).map(asText).filter(Boolean))]}
function compareCodePoints(a,b){const x=Array.from(asText(a),c=>c.codePointAt(0)),y=Array.from(asText(b),c=>c.codePointAt(0));for(let i=0;i<Math.min(x.length,y.length);i+=1)if(x[i]!==y[i])return x[i]-y[i];return x.length-y.length}
function stable(v){if(Array.isArray(v))return`[${v.map(stable).join(",")}]`;if(v&&typeof v==="object")return`{${Object.keys(v).sort(compareCodePoints).map(k=>`${JSON.stringify(k)}:${stable(v[k])}`).join(",")}}`;return JSON.stringify(v)}
async function sha256Hex(text){const hash=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(text));return[...new Uint8Array(hash)].map(x=>x.toString(16).padStart(2,"0")).join("")}
async function digest(prefix,value){return`${prefix}:${(await sha256Hex(stable(value))).slice(0,24)}`}
function withoutId(value){return Object.fromEntries(Object.entries(value||{}).filter(([key])=>key!=="id"))}
function svg(name,attrs={}){const node=document.createElementNS(NS,name);for(const[k,v]of Object.entries(attrs))node.setAttribute(k,String(v));return node}
function clamp(v,lo,hi){return Math.max(lo,Math.min(hi,v))}
function wrapHair(v){let x=v;while(x>180000)x-=360000;while(x<-180000)x+=360000;return Math.round(x)}

async function contractMatches(full){
  if(!isRecord(full)||!crypto.subtle)return false;
  if(full.protocol!=="SUPERNET-FULL-POTENTIAL-GATE-CLOSURE"||full.schema!=="closure.supernet/full-potential-gate-closure-v1")return false;
  if(full.id!==await digest("full-supernet-potential-gate",withoutId(full)))return false;
  const closure=full.closure_ui_contract,gate=full.relative_natural_form_potential_gate,nav=full.navigation_context,solver=full.potential_gate_natural_form_solver;
  if(!isRecord(closure)||!isRecord(gate)||!isRecord(nav)||!isRecord(solver))return false;
  if(closure.id!==await digest("translational-visualization",withoutId(closure)))return false;
  if(gate.id!==await digest("relative-natural-form-potential-gate",withoutId(gate)))return false;
  if(nav.id!==await digest("perspectival-navigation",withoutId(nav)))return false;
  if(solver.id!==await digest("potential-gate-natural-form-solver",withoutId(solver)))return false;
  if(full.navigation_context.id!==gate.navigation_context?.id||solver.gate_id!==gate.id||full.truth_invariant_id!==gate.truth_invariant_id)return false;
  if(full.supernet_is_relative_natural_form_potential_gate!==true||full.ui_is_local_natural_form_of_gate!==true||full.equality_closure_is_not_the_whole_supernet!==true)return false;
  if(gate.relative_natural_form_potential_gate!==true||gate.supernet_is_not_isolated_equality_condition!==true||gate.witnessed_truth_plus_open_potential!==true)return false;
  if(gate.navigation_relocalises_without_refining_truth!==true||gate.only_source_preserving_return_refines_truth!==true||gate.selection_authors_truth!==false||gate.rendering_authors_truth!==false)return false;
  if(nav.current_perspective_id!==full.perspective_id||nav.current_focus_event_id!==(full.focus_event_id??null)||nav.truth_invariant_id!==full.truth_invariant_id||nav.navigation_refines_truth!==false)return false;
  if(!Array.isArray(gate.paths)||!Array.isArray(gate.localities)||!Array.isArray(gate.family_potentials))return false;
  for(const path of gate.paths){
    if(!isRecord(path)||path.id!==await digest("potential-gate-path",withoutId(path)))return false;
    if(!["WITNESSED","OPEN"].includes(path.status)||path.selection_executes_as_equality!==false||path.navigation_changes_truth!==false)return false;
    if(path.status==="WITNESSED"&&(!Array.isArray(path.source_return_ids)||!path.source_return_ids.length||path.source_preserved!==true))return false;
  }
  for(const solution of solver.solutions||[]){
    if(solution.id!==await digest("potential-gate-natural-form-solution",withoutId(solution)))return false;
    if(solution.gate_id!==gate.id||solution.constraints?.rendering_executes_as_equality!==false||solution.constraints?.selection_executes_as_equality!==false)return false;
  }
  const certificate=closure.supernet_closure_certificate;
  if(!isRecord(certificate)||certificate.supernet_closed!==true||certificate.runtime_equality_authority!=="SOURCE_PRESERVING_RETURNED_TRANSLATION")return false;
  return true;
}

function phaseWeight(index,count){if(!count)return 0;const phase=(((((localHairMillidegrees/1000)%360)+360)%360)/360)*count;const raw=Math.abs(index-phase),d=Math.min(raw,count-raw);if(d>=2.25)return.045;if(d>=1.25)return.14;if(d>=.55)return.4;return 1}
function solvePoint(solution,point){
  const c=solution.coefficients||{};let x=(Number(point?.[0]??500)-500)/500,y=(Number(point?.[1]??500)-500)/500;
  const origin=Math.abs(x)<1e-15&&Math.abs(y)<1e-15,sx=(c.stretch_x_milli||1000)/1000,sy=(c.stretch_y_milli||1000)/1000,shx=(c.shear_x_milli||0)/1000,shy=(c.shear_y_milli||0)/1000;
  const u0=sx*x+shx*y,v0=shy*x+sy*y,hair=localHairMillidegrees/1000*Math.PI/180;
  let angle=((c.angle_millidegrees||0)+(c.gate_phase_millidegrees||0))/1000*Math.PI/180;angle+=hair*(c.hair_coupling_milli||0)/1000;
  const ca=Math.cos(angle),sa=Math.sin(angle),u=ca*u0-sa*v0,v=sa*u0+ca*v0,radius=Math.hypot(u,v),theta=Math.atan2(v,u),phase=(c.phase_millidegrees||0)/1000*Math.PI/180;
  const order=Math.max(1,Number(c.maze_harmonic_order||c.harmonic_order||1)),harmonic=Math.sin(order*theta+phase+hair),radial=1+(c.radial_milli||0)/1000*harmonic*Math.min(1,radius);
  const twist=((c.twist_milli||0)+(c.navigation_holonomy_milli||0))/1000*radius*radius,boundary=(c.boundary_gain_milli||1000)/1000;
  const fold=(c.fold_milli||0)/1000*Math.tanh(boundary*u),cross=(c.cross_milli||0)/1000*Math.tanh(boundary*v),aperture=((c.open_aperture_milli||0)+(c.potential_aperture_milli||0))/1000,sourcePull=((c.return_pull_milli||0)+(c.returned_pull_milli||0))/1000;
  const gain=(c.role_gain_milli||1000)*(c.distance_gain_milli||1000)/1000000,theta2=theta+twist*Math.min(1.25,radius),rr=clamp(radius*radial,0,1.38);
  let X=gain*(rr*Math.cos(theta2)+fold+aperture*Math.sin((order+1)*theta)),Y=gain*(rr*Math.sin(theta2)+cross-sourcePull*Math.cos((order+1)*theta));if(origin){X=0;Y=0}
  const zoom=Math.max(.05,localZoomMilli/1000);return[clamp(500+420*zoom*X,20,980),clamp(500+420*zoom*Y,20,980)]
}

function deterministicUnit(text){let h=2166136261;for(const ch of Array.from(asText(text))){h^=ch.codePointAt(0);h=Math.imul(h,16777619)}return((h>>>0)%1000000)/1000000}
function gateGeometry(full){
  const gate=full.relative_natural_form_potential_gate,closure=full.closure_ui_contract,projection=closure.projection||{};
  const positions=new Map(),current=asText(gate.active_perspective_id),perspectives=(gate.localities||[]).filter(x=>x.kind==="PERSPECTIVE").sort((a,b)=>compareCodePoints(a.perspective_id,b.perspective_id));
  positions.set(`p:${current}`,[500,500]);let pi=0;for(const locality of perspectives){const p=asText(locality.perspective_id);if(p===current)continue;const phase=2*Math.PI*pi/Math.max(1,perspectives.length-1)-Math.PI/2;pi+=1;positions.set(`p:${p}`,[500+245*Math.cos(phase),500+180*Math.sin(phase)])}
  const fibres=(projection.equality_fibres||[]).filter(isRecord).sort((a,b)=>compareCodePoints(a.id,b.id));const stateFibre=new Map();for(const f of fibres)for(const id of f.member_state_ids||[])stateFibre.set(asText(id),asText(f.id));
  fibres.forEach((f,index)=>{const phase=2*Math.PI*index/Math.max(1,fibres.length)-Math.PI/2;positions.set(`f:${asText(f.id)}`,[500+390*Math.cos(phase),500+285*Math.sin(phase)])});
  function pointFor(path,source){
    const perspective=asText(source?path.source_perspective_id:path.target_perspective_id);const state=asText(source?path.source_state_id:path.target_state_id);const fibre=stateFibre.get(state);
    if(path.action==="PERSPECTIVE_TRANSPORT"&&positions.has(`p:${perspective}`))return positions.get(`p:${perspective}`);
    if(fibre&&positions.has(`f:${fibre}`))return positions.get(`f:${fibre}`);
    if(source)return positions.get(`p:${current}`)||[500,500];
    const phase=2*Math.PI*deterministicUnit(path.id);return[500+475*Math.cos(phase),500+475*Math.sin(phase)]
  }
  function curve(path){const a=pointFor(path,true),b=pointFor(path,false),dx=b[0]-a[0],dy=b[1]-a[1],len=Math.max(1,Math.hypot(dx,dy)),sign=deterministicUnit(path.id)<.5?-1:1,bend=Math.min(96,len*(.13+.11*deterministicUnit(path.id+"bend")))*sign;return[a,[(a[0]+b[0])/2-dy/len*bend,(a[1]+b[1])/2+dx/len*bend],b]}
  return{gate,closure,positions,fibres,stateFibre,paths:(gate.paths||[]).map(path=>({...path,points:curve(path)}))}
}
function pathD(points){return`M ${points[0][0].toFixed(2)} ${points[0][1].toFixed(2)} Q ${points[1][0].toFixed(2)} ${points[1][1].toFixed(2)} ${points[2][0].toFixed(2)} ${points[2][1].toFixed(2)}`}
function midpoint(points){return points[1]||points[0]||[500,500]}
function activePath(full){return(full.relative_natural_form_potential_gate.paths||[]).find(path=>path.id===activeRelationId)||null}
function relationHue(solution){return(((solution.coefficients?.angle_millidegrees||0)+(solution.coefficients?.gate_phase_millidegrees||0))/1000+localHairMillidegrees/1000+360)%360}

function animateTransport(oldRoot,next,path){
  const direction=path?.target_perspective_id&&path.target_perspective_id!==path.source_perspective_id?1:-1;
  if(oldRoot?.animate)oldRoot.animate([{opacity:1,transform:"translate(0,0) scale(1)"},{opacity:.08,transform:`translate(${direction*44}px,0) scale(1.04)`}],{duration:220,easing:"ease-in",fill:"forwards"});
  setTimeout(()=>{active=next;activeRelationId=null;draft="";sensor.value="";render();const root=surface.firstElementChild;if(root?.animate)root.animate([{opacity:.08,transform:`translate(${-direction*44}px,0) scale(.96)`},{opacity:1,transform:"translate(0,0) scale(1)"}],{duration:260,easing:"ease-out"})},190)
}

async function navigateRelation(path){
  if(navigating||!active)return;navigating=true;
  try{
    const response=await fetch(`/supernet/potential-gates/${encodeURIComponent(active.id)}/navigate`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({relation_id:path.id,perspective_id:active.perspective_id,focus_event_id:active.focus_event_id??null,navigation_context:active.navigation_context})});
    if(response.status===409){await loadInitial();return}if(!response.ok)throw new Error(`navigate:${response.status}`);
    const body=await response.json(),next=body.supernet_potential_gate;if(!body.navigated||body.truth_refined||!await contractMatches(next))throw new Error("unverified-navigation");
    const url=new URL(location.href);url.searchParams.set("perspective_id",next.perspective_id);if(next.focus_event_id)url.searchParams.set("focus_event_id",next.focus_event_id);else url.searchParams.delete("focus_event_id");history.pushState({gate:next},"",url);
    animateTransport(surface.firstElementChild,next,path);
  }finally{navigating=false}
}
function activateRelation(path){activeRelationId=path.id;draft="";sensor.value="";if(path.status==="WITNESSED"&&(path.action==="PERSPECTIVE_TRANSPORT"||path.action==="LOCALITY_TRANSPORT")){navigateRelation(path);return}sensor.focus({preventScroll:true});render()}
function activateFibre(fibre){const path=(active?.relative_natural_form_potential_gate?.paths||[]).find(item=>item.target_state_id&&(fibre.member_state_ids||[]).includes(item.target_state_id)&&item.status==="WITNESSED");if(path)activateRelation(path)}

async function submitReturn(){
  const path=activePath(active);if(returning||!active||!path||path.status==="WITNESSED"||!draft.trim())return;returning=true;
  try{
    const response=await fetch(`/supernet/potential-gates/${encodeURIComponent(active.id)}/return`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({relation_id:path.id,perspective_id:active.perspective_id,focus_event_id:active.focus_event_id??null,navigation_context:active.navigation_context,exact_source_return:draft.trim(),local_perspective_hair_millidegrees:localHairMillidegrees,local_perspective_zoom_milli:localZoomMilli})});
    if(response.status===409){await loadInitial();return}if(!response.ok)throw new Error(`return:${response.status}`);
    const body=await response.json(),next=body.supernet_potential_gate;if(!body.returned||!await contractMatches(next))throw new Error("unverified-return");
    active=next;activeRelationId=null;draft="";sensor.value="";render();
  }finally{returning=false}
}

function render(){
  if(!active)return;surface.replaceChildren();const geometry=gateGeometry(active),gate=geometry.gate,solver=active.potential_gate_natural_form_solver,solutions=solver.solutions||[];
  const root=svg("svg",{viewBox:"0 0 1000 1000","data-supernet-equality-surface":"true","data-relative-natural-form-potential-gate":"true","data-visible-is-interactive":"true","data-visible-equals-interaction":"true","data-same-object-visible-and-interactive":"true","data-interface-is-natural-form":"true","data-natural-form-is-equality-closure":"false","data-equality-is-local-gate-constraint":"true","data-legacy-renderer-substrate":"false","data-presentation-only":"false","data-perspective-id":active.perspective_id,"data-navigation-depth":active.navigation_context.depth,"data-truth-invariant-id":active.truth_invariant_id,"data-hair-millidegrees":localHairMillidegrees,"data-zoom-milli":localZoomMilli});surface.append(root);
  solutions.forEach((solution,index)=>{const weight=phaseWeight(index,solutions.length);if(weight<.04)return;const hue=relationHue(solution),role=solution.relative_role,roleOpacity=role==="LOCAL"?.78:role==="GLOBAL"?.46:.22;const group=svg("g",{opacity:Math.max(.025,weight*roleOpacity),"data-natural-form-family":solution.family_id,"data-gate-solution-id":solution.id,"data-same-object-visible-and-interactive":"true"});root.append(group);
    for(const path of geometry.paths){const points=path.points.map(point=>solvePoint(solution,point));const selected=path.id===activeRelationId;const node=svg("path",{d:pathD(points),class:"gate-path closure-relation",stroke:`hsl(${hue} 72% ${path.status==="WITNESSED"?68:62}%)`,opacity:selected?1:.9,"data-closure-relation-id":path.id,"data-potential-gate-path-id":path.id,"data-status":path.status,"data-action":path.action,"data-active":selected,"data-visible-equals-interaction":"true","data-navigation":path.status==="WITNESSED","data-return-aperture":path.status!=="WITNESSED"});node.addEventListener("pointerdown",event=>event.stopPropagation());node.addEventListener("click",event=>{event.stopPropagation();activateRelation(path)});group.append(node);if(selected&&draft){const m=midpoint(points),label=svg("text",{x:m[0],y:m[1]-12,class:"gate-draft"});label.textContent=draft.slice(0,140);group.append(label)}}
    for(const fibre of geometry.fibres){const base=geometry.positions.get(`f:${asText(fibre.id)}`);if(!base)continue;const[cx,cy]=solvePoint(solution,base),radius=Math.max(8,Math.min(42,10+Math.sqrt((fibre.member_state_ids||[]).length+1)*7)),circle=svg("circle",{cx,cy,r:radius,class:"gate-locality closure-fibre",stroke:`hsl(${hue} 62% 72%)`,"data-closure-fibre-id":fibre.id,"data-visible-equals-interaction":"true"});circle.addEventListener("pointerdown",event=>event.stopPropagation());circle.addEventListener("click",event=>{event.stopPropagation();activateFibre(fibre)});group.append(circle)}
    for(const locality of gate.localities||[]){if(locality.kind!=="PERSPECTIVE")continue;const base=geometry.positions.get(`p:${asText(locality.perspective_id)}`);if(!base)continue;const[cx,cy]=solvePoint(solution,base),circle=svg("circle",{cx,cy,r:locality.current?12:8,class:"gate-locality",stroke:`hsl(${hue} 68% 76%)`,"data-perspective-locality":locality.perspective_id,"data-current-perspective":locality.current});group.append(circle);if(weight>.55){const label=svg("text",{x:cx,y:cy+24,class:"gate-label"});label.textContent=locality.current?"·":asText(locality.perspective_id).slice(0,40);group.append(label)}}
  });
}

async function loadInitial(){const query=new URLSearchParams();query.set("perspective_id",new URL(location.href).searchParams.get("perspective_id")||active?.perspective_id||"perspective");const focus=new URL(location.href).searchParams.get("focus_event_id");if(focus)query.set("focus_event_id",focus);const response=await fetch(`/supernet/potential-gate?${query}`);if(!response.ok)throw new Error(`gate:${response.status}`);const body=await response.json(),next=body.supernet_potential_gate;if(!await contractMatches(next))throw new Error("unverified-gate");active=next;activeRelationId=null;render()}

surface.addEventListener("pointerdown",event=>{if(event.target!==surface&&event.target.tagName!=="svg")return;dragging={x:event.clientX,hair:localHairMillidegrees};surface.setPointerCapture?.(event.pointerId)});
surface.addEventListener("pointermove",event=>{if(!dragging)return;localHairMillidegrees=wrapHair(dragging.hair+(event.clientX-dragging.x)*420);render()});
surface.addEventListener("pointerup",()=>{dragging=null});
surface.addEventListener("wheel",event=>{event.preventDefault();localZoomMilli=Math.round(clamp(localZoomMilli*Math.exp(-event.deltaY*.0015),50,100000));render()},{passive:false});
surface.addEventListener("click",()=>{const open=(active?.relative_natural_form_potential_gate?.paths||[]).find(path=>path.status!=="WITNESSED");if(open)activateRelation(open)});
sensor.addEventListener("input",()=>{draft=sensor.value;render()});
sensor.addEventListener("keydown",event=>{if(event.key==="Enter"&&!event.shiftKey){event.preventDefault();submitReturn()}else if(event.key==="Escape"){draft="";sensor.value="";activeRelationId=null;render()}});
window.addEventListener("popstate",async event=>{const gate=event.state?.gate;if(gate&&await contractMatches(gate)){active=gate;activeRelationId=null;render()}else loadInitial().catch(error=>surface.dataset.error=asText(error?.message||error))});
loadInitial().catch(error=>surface.dataset.error=asText(error?.message||error));
})();
</script>
</body>
</html>"""

__all__ = ["POTENTIAL_GATE_SUPERNET_HTML"]
