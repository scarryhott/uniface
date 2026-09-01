from __future__ import annotations

"""Single-surface Supernet interface: visible natural form = interactive closure.

This file intentionally does not import or wrap the legacy renderer. The browser
receives one verified closure contract and derives one family of interactive
relation objects from it. The same SVG path that is visible is the hit target,
navigation path, OPEN return aperture, and WITNESSED transport surface.

Natural-form solutions remain presentation readings of the same source relation;
rendering cannot witness equality. A source-preserving returned interaction is
still the only operation that can refine the closure.
"""

EQUAL_TRANSLATION_SUPERNET_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover,user-scalable=no">
<title></title>
<style>
:root { color-scheme: dark; }
* { box-sizing: border-box; }
html, body { width:100%; height:100%; margin:0; overflow:hidden; background:#020305; }
#supernet-surface { position:fixed; inset:0; overflow:hidden; touch-action:none; outline:none; }
svg { display:block; width:100%; height:100%; }
.closure-relation {
  fill:none;
  stroke-linecap:round;
  vector-effect:non-scaling-stroke;
  pointer-events:stroke;
  cursor:pointer;
}
.closure-relation[data-status="WITNESSED"] { stroke-width:3.2; }
.closure-relation[data-status="OPEN"] { stroke-width:2.1; stroke-dasharray:7 9; }
.closure-relation[data-active="true"] { stroke-width:5.2; }
.closure-fibre {
  fill:rgba(255,255,255,.018);
  vector-effect:non-scaling-stroke;
  pointer-events:all;
  cursor:pointer;
}
.closure-source {
  font:430 12px/1.2 ui-sans-serif,system-ui,sans-serif;
  fill:rgba(248,250,255,.74);
  text-anchor:middle;
  pointer-events:none;
}
.closure-draft {
  font:470 17px/1.25 ui-sans-serif,system-ui,sans-serif;
  fill:rgba(250,252,255,.94);
  text-anchor:middle;
  pointer-events:none;
}
#return-sensor {
  position:fixed;
  width:1px;
  height:1px;
  left:50%;
  top:50%;
  opacity:.001;
  border:0;
  padding:0;
  background:transparent;
  color:transparent;
  caret-color:transparent;
}
</style>
</head>
<body>
<main id="supernet-surface" tabindex="0"></main>
<textarea id="return-sensor" aria-label=""></textarea>
<script>
(() => {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const surface = document.getElementById("supernet-surface");
  const sensor = document.getElementById("return-sensor");
  let active = null;
  let activeRelation = null;
  let draft = "";
  let localHairMillidegrees = 0;
  let dragging = null;
  let returning = false;

  function asText(value) { return value === null || value === undefined ? "" : String(value); }
  function isRecord(value) { return !!value && typeof value === "object" && !Array.isArray(value); }
  function unique(values) { return [...new Set((values || []).map(asText).filter(Boolean))]; }
  function compareCodePoints(left, right) {
    const a = Array.from(asText(left), x => x.codePointAt(0));
    const b = Array.from(asText(right), x => x.codePointAt(0));
    const n = Math.min(a.length, b.length);
    for (let i=0;i<n;i+=1) if (a[i] !== b[i]) return a[i]-b[i];
    return a.length-b.length;
  }
  function stable(value) {
    if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
    if (value && typeof value === "object") {
      return `{${Object.keys(value).sort(compareCodePoints).map(k => `${JSON.stringify(k)}:${stable(value[k])}`).join(",")}}`;
    }
    return JSON.stringify(value);
  }
  async function sha256Hex(text) {
    const bytes = new TextEncoder().encode(text);
    const hash = await crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(hash)].map(x => x.toString(16).padStart(2,"0")).join("");
  }
  async function digest(prefix, value) {
    return `${prefix}:${(await sha256Hex(stable(value))).slice(0,24)}`;
  }
  function withoutId(value) {
    return Object.fromEntries(Object.entries(value || {}).filter(([k]) => k !== "id"));
  }
  function svg(name, attrs={}) {
    const node = document.createElementNS(NS, name);
    for (const [k,v] of Object.entries(attrs)) node.setAttribute(k, String(v));
    return node;
  }
  function clamp(value, lo, hi) { return Math.max(lo, Math.min(hi, value)); }
  function wrapHair(value) {
    let x = value;
    while (x > 180000) x -= 360000;
    while (x < -180000) x += 360000;
    return Math.round(x);
  }
  function phaseWeight(index, count) {
    if (!count) return 0;
    const phase = ((((localHairMillidegrees/1000)%360)+360)%360)/360*count;
    const raw = Math.abs(index-phase);
    const d = Math.min(raw, count-raw);
    if (d >= 2.25) return .045;
    if (d >= 1.25) return .14;
    if (d >= .55) return .40;
    return 1;
  }

  async function contractMatches(contract) {
    if (!isRecord(contract) || !contract.id || !crypto.subtle) return false;
    if (contract.id !== await digest("translational-visualization", withoutId(contract))) return false;
    const atlas = contract.natural_form_atlas;
    const field = contract.local_natural_form_freedom;
    const solver = contract.interactive_natural_form_solver;
    const closure = contract.supernet_closure_certificate;
    if (!isRecord(atlas) || !isRecord(field) || !isRecord(solver) || !isRecord(closure)) return false;
    if (atlas.id !== await digest("natural-form-atlas", withoutId(atlas))) return false;
    if (field.id !== await digest("local-natural-form-freedom", withoutId(field))) return false;
    if (solver.id !== await digest("interactive-natural-form-solver", withoutId(solver))) return false;
    if (closure.id !== await digest("supernet-closure", withoutId(closure))) return false;
    if (solver.protocol !== "SUPERNET-INTERACTIVE-NATURAL-FORM-SOLVER"
        || solver.schema !== "closure.supernet/interactive-natural-form-solver-v1"
        || solver.natural_form_is_interactive_interface_equality_closure !== true
        || solver.natural_form_is_posthoc_visual_template !== false
        || solver.family_switch_present !== false
        || solver.named_geometry_templates_present !== false
        || solver.rendering_can_witness_equality !== false
        || solver.only_return_refines_equality_closure !== true) return false;
    const equality = solver.equality_closure_signature;
    if (!isRecord(equality) || equality.id !== await digest("interactive-equality-closure", withoutId(equality))) return false;
    if (!Array.isArray(solver.solutions) || solver.solution_count !== solver.solutions.length) return false;
    if (!Array.isArray(field.families) || solver.solution_count !== field.families.length) return false;
    for (const solution of solver.solutions) {
      if (!isRecord(solution) || solution.id !== await digest("natural-form-solution", withoutId(solution))) return false;
      if (solution.solver_basis !== "GENERIC_BOUNDED_HARMONIC_EQUALITY_CLOSURE_BASIS"
          || solution.constraints?.rendering_executes_as_equality !== false
          || solution.constraints?.family_name_used_as_geometry_selector !== false
          || solution.constraints?.source_relation_paths_preserved !== true) return false;
    }
    if (closure.supernet_closed !== true
        || closure.interactive_natural_form_solver_id !== solver.id
        || closure.runtime_equality_authority !== "SOURCE_PRESERVING_RETURNED_TRANSLATION"
        || closure.open_relations_are_part_of_closure !== true) return false;
    if (isRecord(closure.checks) && !Object.values(closure.checks).every(v => v === true)) return false;
    if (atlas.visual_resemblance_can_witness_equality !== false
        || atlas.cross_form_equality_requires_returned_translation !== true) return false;
    for (const relation of atlas.translations || []) {
      if (!isRecord(relation) || relation.kind === "IDENTITY") continue;
      if (relation.status === "WITNESSED") {
        if (!Array.isArray(relation.source_return_ids) || !relation.source_return_ids.length
            || relation.source_preserved !== true || relation.closure_commutes !== true
            || relation.return_preserved !== true) return false;
      } else if (relation.executes_as_equality === true) return false;
    }
    const projection = contract.projection || {};
    for (const relation of projection.translations || []) {
      if (relation.executes_as_equality === true && relation.relation_status !== "WITNESSED") return false;
    }
    for (const relation of projection.potentials || []) if (relation.executes_as_equality === true) return false;
    return true;
  }

  function solvePoint(solution, point) {
    const c = solution.coefficients || {};
    let x = (Number(point?.[0] ?? 500)-500)/500;
    let y = (Number(point?.[1] ?? 500)-500)/500;
    const origin = Math.abs(x)<1e-15 && Math.abs(y)<1e-15;
    const sx=(c.stretch_x_milli||1000)/1000, sy=(c.stretch_y_milli||1000)/1000;
    const shx=(c.shear_x_milli||0)/1000, shy=(c.shear_y_milli||0)/1000;
    const u0=sx*x+shx*y, v0=shy*x+sy*y;
    const hair=localHairMillidegrees/1000*Math.PI/180;
    let angle=(c.angle_millidegrees||0)/1000*Math.PI/180;
    angle += hair*(c.hair_coupling_milli||0)/1000;
    const ca=Math.cos(angle), sa=Math.sin(angle);
    const u=ca*u0-sa*v0, v=sa*u0+ca*v0;
    const radius=Math.hypot(u,v), theta=Math.atan2(v,u);
    const phase=(c.phase_millidegrees||0)/1000*Math.PI/180;
    const order=Math.max(1,Number(c.harmonic_order||1));
    const harmonic=Math.sin(order*theta+phase+hair);
    const radial=1+(c.radial_milli||0)/1000*harmonic*Math.min(1,radius);
    const twist=(c.twist_milli||0)/1000*radius*radius;
    const boundary=(c.boundary_gain_milli||1000)/1000;
    const fold=(c.fold_milli||0)/1000*Math.tanh(boundary*u);
    const cross=(c.cross_milli||0)/1000*Math.tanh(boundary*v);
    const aperture=(c.open_aperture_milli||0)/1000;
    const sourcePull=(c.return_pull_milli||0)/1000;
    const gain=(c.role_gain_milli||1000)*(c.distance_gain_milli||1000)/1000000;
    const theta2=theta+twist*Math.min(1.25,radius);
    const rr=clamp(radius*radial,0,1.38);
    let X=gain*(rr*Math.cos(theta2)+fold+aperture*Math.sin((order+1)*theta));
    let Y=gain*(rr*Math.sin(theta2)+cross-sourcePull*Math.cos((order+1)*theta));
    if (origin) { X=0; Y=0; }
    return [clamp(500+420*X,20,980), clamp(500+420*Y,20,980)];
  }

  function stateToFibre(projection) {
    const map = new Map();
    for (const fibre of projection.equality_fibres || []) {
      for (const id of fibre.member_state_ids || []) map.set(asText(id), asText(fibre.id));
    }
    return map;
  }
  function deterministicUnit(text) {
    let h = 2166136261;
    for (const ch of Array.from(asText(text))) { h ^= ch.codePointAt(0); h = Math.imul(h,16777619); }
    return ((h>>>0)%1000000)/1000000;
  }
  function baseGeometry(contract) {
    const projection = contract.projection || {};
    const fibres = [...(projection.equality_fibres || [])].filter(isRecord)
      .sort((a,b)=>compareCodePoints(a.id,b.id));
    const focusId = asText(contract.return_relation?.parent_natural_form_id);
    const positions = new Map();
    const ordered = [...fibres].sort((a,b) => {
      const af=asText(a.id)===focusId?0:1, bf=asText(b.id)===focusId?0:1;
      return af-bf || compareCodePoints(a.id,b.id);
    });
    const peripheral = Math.max(1, ordered.length-(focusId?1:0));
    let k=0;
    for (const fibre of ordered) {
      if (asText(fibre.id)===focusId || (ordered.length===1 && !focusId)) positions.set(asText(fibre.id),[500,500]);
      else {
        const phase=2*Math.PI*k/peripheral-Math.PI/2; k+=1;
        const orbit=Math.min(350,175+Math.max(0,ordered.length-2)*17);
        positions.set(asText(fibre.id),[500+orbit*Math.cos(phase),500+orbit*.72*Math.sin(phase)]);
      }
    }
    const stateMap=stateToFibre(projection);
    const focusFibre=positions.has(focusId)?focusId:(ordered[0]?asText(ordered[0].id):null);
    const focusPoint=focusFibre?positions.get(focusFibre):[500,500];
    function pathBetween(a,b,seed) {
      const dx=b[0]-a[0], dy=b[1]-a[1], len=Math.max(1,Math.hypot(dx,dy));
      const sign=deterministicUnit(seed)<.5?-1:1;
      const bend=Math.min(94,len*(.12+.12*deterministicUnit(seed+"bend")))*sign;
      return [a,[(a[0]+b[0])/2-dy/len*bend,(a[1]+b[1])/2+dx/len*bend],b];
    }
    const relations=[];
    for (const raw of projection.translations || []) {
      const sf=stateMap.get(asText(raw.source_state_id)), tf=stateMap.get(asText(raw.target_state_id));
      if (!positions.has(sf) || !positions.has(tf)) continue;
      relations.push({
        id:asText(raw.id), kind:"TRANSLATION", status:raw.relation_status==="WITNESSED"?"WITNESSED":"OPEN",
        executes_as_equality:raw.executes_as_equality===true,
        source_state_id:asText(raw.source_state_id), target_state_id:asText(raw.target_state_id),
        points:pathBetween(positions.get(sf),positions.get(tf),asText(raw.id)),
      });
    }
    for (const raw of projection.potentials || []) {
      const sf=stateMap.get(asText(raw.source_state_id));
      const tf=stateMap.get(asText(raw.target_state_id));
      const a=positions.get(sf)||focusPoint;
      let b=positions.get(tf);
      if (!b) {
        const phase=2*Math.PI*deterministicUnit(asText(raw.id));
        b=[500+455*Math.cos(phase),500+455*Math.sin(phase)];
      }
      relations.push({
        id:asText(raw.id), kind:"POTENTIAL", status:"OPEN", executes_as_equality:false,
        source_state_id:asText(raw.source_state_id), target_state_id:raw.target_state_id?asText(raw.target_state_id):null,
        points:pathBetween(a,b,asText(raw.id)),
      });
    }
    const rr=contract.return_relation;
    if (isRecord(rr) && rr.id && !relations.some(r=>r.id===asText(rr.id))) {
      const phase=2*Math.PI*deterministicUnit(asText(rr.id));
      const b=[500+470*Math.cos(phase),500+470*Math.sin(phase)];
      relations.push({
        id:asText(rr.id), kind:"RETURN_APERTURE", status:"OPEN", executes_as_equality:false,
        source_state_id:asText(rr.focus_state_id)||null, target_state_id:null,
        points:pathBetween(focusPoint,b,asText(rr.id)), return_relation:true,
      });
    }
    return {fibres,positions,relations,stateMap,focusPoint};
  }
  function quadraticPath(points) {
    return `M ${points[0][0].toFixed(2)} ${points[0][1].toFixed(2)} Q ${points[1][0].toFixed(2)} ${points[1][1].toFixed(2)} ${points[2][0].toFixed(2)} ${points[2][1].toFixed(2)}`;
  }
  function midpoint(points) { return points[1] || points[0] || [500,500]; }
  function sourceTextForFibre(contract, fibre) {
    const states=new Map((contract.projection?.states||[]).map(s=>[asText(s.id),s]));
    const texts=(fibre.member_state_ids||[]).map(id=>asText(states.get(asText(id))?.source_trace)).filter(Boolean);
    return texts.join(" · ").slice(0,180);
  }

  function relationHue(solution) {
    return (((solution.coefficients?.angle_millidegrees||0)/1000)+(localHairMillidegrees/1000)+360)%360;
  }
  function transformedPoints(solution, points) { return points.map(p=>solvePoint(solution,p)); }

  function activateRelation(relation) {
    activeRelation=relation;
    draft="";
    sensor.value="";
    if (relation.status==="WITNESSED" && relation.target_state_id) {
      loadContract(relation.target_state_id);
      return;
    }
    sensor.focus({preventScroll:true});
    render();
  }
  function activateFibre(fibre) {
    const target=(fibre.member_state_ids||[])[0];
    if (target) loadContract(asText(target));
  }

  async function localProjectionCommitment(contract, exactSource) {
    const body={
      contract_id:contract.id,
      closure_equation_system_id:contract.closure_naturality_equations?.id,
      return_relation_id:contract.return_relation?.id,
      perspective_id:contract.perspective_id,
      focus_event_id:contract.focus_event_id ?? null,
      exact_source_return:exactSource,
      local_perspective_hair_millidegrees:localHairMillidegrees,
      reading_kernel:contract.perspective_closure?.kernel || [],
    };
    return digest("local-projection",body);
  }
  async function submitReturn() {
    if (returning || !active || !activeRelation || !draft.trim()) return;
    returning=true;
    try {
      const source=draft.trim();
      const payload={
        return_relation_id:active.return_relation.id,
        perspective_id:active.perspective_id,
        focus_event_id:active.focus_event_id ?? null,
        exact_source_return:source,
        closure_equation_system_id:active.closure_naturality_equations.id,
        local_projection_commitment:await localProjectionCommitment(active,source),
        local_perspective_hair_millidegrees:localHairMillidegrees,
        source_stream:(`natural-form-relation:${activeRelation.id}`).slice(0,240),
      };
      const response=await fetch(`/supernet/interface/projections/${encodeURIComponent(active.id)}/return`,{
        method:"POST", headers:{"content-type":"application/json"}, body:JSON.stringify(payload),
      });
      if (response.status===409) { await loadContract(active.focus_event_id ?? null); return; }
      if (!response.ok) throw new Error(`return:${response.status}`);
      const body=await response.json();
      const successor=body.closure_ui_contract;
      if (!body.returned || !await contractMatches(successor)) throw new Error("unverified-successor");
      active=successor;
      activeRelation=null;
      draft=""; sensor.value="";
      render();
    } finally { returning=false; }
  }

  function render() {
    if (!active) return;
    surface.replaceChildren();
    const root=svg("svg",{
      viewBox:"0 0 1000 1000",
      "data-supernet-equality-surface":"true",
      "data-visible-is-interactive":"true",
      "data-interface-is-natural-form":"true",
      "data-natural-form-is-equality-closure":"true",
      "data-legacy-renderer-substrate":"false",
      "data-contract-id":active.id,
      "data-hair-millidegrees":localHairMillidegrees,
    });
    surface.append(root);
    const geometry=baseGeometry(active);
    const solver=active.interactive_natural_form_solver;
    const solutions=solver.solutions || [];
    solutions.forEach((solution,index)=>{
      const weight=phaseWeight(index,solutions.length);
      if (weight<.04) return;
      const hue=relationHue(solution);
      const role=solution.relative_role;
      const roleOpacity=role==="LOCAL"?.78:role==="GLOBAL"?.46:.22;
      const group=svg("g",{
        opacity:Math.max(.02,weight*roleOpacity),
        "data-natural-form-solution-id":solution.id,
        "data-natural-form-family":solution.family_id,
        "data-relative-role":role,
        "data-presentation-only":"false",
        "data-same-object-visible-and-interactive":"true",
      });
      root.append(group);
      for (const relation of geometry.relations) {
        const points=transformedPoints(solution,relation.points);
        const path=svg("path",{
          d:quadraticPath(points), class:"closure-relation",
          stroke:`hsl(${hue} 72% ${relation.status==="WITNESSED"?68:62}%)`,
          opacity:relation===activeRelation?1:.92,
          "data-closure-relation-id":relation.id,
          "data-status":relation.status,
          "data-equality":relation.executes_as_equality,
          "data-active":relation===activeRelation,
          "data-visible-equals-interaction":"true",
          "data-navigation":relation.status==="WITNESSED",
          "data-return-aperture":relation.status!=="WITNESSED",
          "data-natural-form-solution-id":solution.id,
        });
        path.addEventListener("pointerdown",e=>e.stopPropagation());
        path.addEventListener("click",e=>{ e.stopPropagation(); activateRelation(relation); });
        group.append(path);
        if (relation===activeRelation && draft) {
          const m=midpoint(points);
          const label=svg("text",{x:m[0],y:m[1]-12,class:"closure-draft"});
          label.textContent=draft.slice(0,120);
          group.append(label);
        }
      }
      for (const fibre of geometry.fibres) {
        const base=geometry.positions.get(asText(fibre.id));
        if (!base) continue;
        const [cx,cy]=solvePoint(solution,base);
        const radius=Math.max(8,Math.min(46,11+Math.sqrt((fibre.member_state_ids||[]).length+1)*7));
        const circle=svg("circle",{
          cx,cy,r:radius,class:"closure-fibre",stroke:`hsl(${hue} 62% 72%)`,
          "stroke-width":role==="LOCAL"?2:1.1,
          "data-closure-fibre-id":fibre.id,
          "data-visible-equals-interaction":"true",
          "data-natural-form-solution-id":solution.id,
        });
        circle.addEventListener("pointerdown",e=>e.stopPropagation());
        circle.addEventListener("click",e=>{e.stopPropagation();activateFibre(fibre);});
        group.append(circle);
        const text=sourceTextForFibre(active,fibre);
        if (text && weight>.35) {
          const label=svg("text",{x:cx,y:cy+radius+16,class:"closure-source"});
          label.textContent=text;
          group.append(label);
        }
      }
      if (!geometry.fibres.length) {
        const [cx,cy]=solvePoint(solution,[500,500]);
        group.append(svg("circle",{cx,cy,r:7,class:"closure-fibre",stroke:`hsl(${hue} 62% 72%)`,
          "data-relative-origin":"true","data-visible-equals-interaction":"true"}));
      }
    });
  }

  async function loadContract(focusEventId=null) {
    const perspective=new URLSearchParams(location.search).get("perspective_id") || active?.perspective_id || "perspective";
    const query=new URLSearchParams({perspective_id:perspective});
    if (focusEventId) query.set("focus_event_id",focusEventId);
    const response=await fetch(`/supernet/interface?${query.toString()}`,{cache:"no-store"});
    if (!response.ok) throw new Error(`projection:${response.status}`);
    const contract=(await response.json()).closure_ui_contract;
    if (!await contractMatches(contract)) throw new Error("unverified-contract");
    active=contract; activeRelation=null; draft=""; sensor.value=""; render();
  }

  sensor.addEventListener("input",()=>{ draft=sensor.value; render(); });
  sensor.addEventListener("keydown",e=>{
    if (e.key==="Enter" && !e.shiftKey) { e.preventDefault(); submitReturn(); }
    if (e.key==="Escape") { activeRelation=null; draft=""; sensor.value=""; render(); }
  });

  surface.addEventListener("pointerdown",e=>{
    if (e.target.closest?.(".closure-relation") || e.target.closest?.(".closure-fibre")) return;
    dragging={id:e.pointerId,x:e.clientX,startHair:localHairMillidegrees};
    surface.setPointerCapture?.(e.pointerId);
  });
  surface.addEventListener("pointermove",e=>{
    if (!dragging || dragging.id!==e.pointerId) return;
    localHairMillidegrees=wrapHair(dragging.startHair+(e.clientX-dragging.x)*420);
    render();
  });
  surface.addEventListener("pointerup",e=>{
    if (dragging && dragging.id===e.pointerId) dragging=null;
  });
  surface.addEventListener("dblclick",()=>{
    activeRelation=null; draft=""; sensor.value=""; localHairMillidegrees=0; render();
  });

  loadContract().catch(error=>{
    surface.dataset.open="true";
    surface.dataset.error=asText(error?.message || error);
  });
})();
</script>
</body>
</html>"""

__all__ = ["EQUAL_TRANSLATION_SUPERNET_HTML"]
