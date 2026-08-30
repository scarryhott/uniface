from __future__ import annotations

from .complete_interface_web import COMPLETE_NATURAL_SUPERNET_HTML


_FINISH_PATCH = r'''
<style>
@media(min-width:901px){.composer{grid-template-columns:110px 150px 130px 170px minmax(300px,1fr);align-items:stretch}.composer textarea{grid-column:auto}}
.composer select,.composer input{border:1px solid #30434c;border-radius:10px;background:#081014;padding:9px;color:inherit;min-width:0}
.coordination-block{background:linear-gradient(180deg,#0b141a,#081014)}.coordination-intent{border:1px solid #354b56;border-radius:11px;padding:10px;background:#060b0f;margin-bottom:9px}.coordination-intent strong{display:block;font-size:12px;color:#e7f0f3}.coordination-intent p{margin:5px 0 0;color:#a7bac2;font-size:10px;line-height:1.45;white-space:pre-wrap}.coordination-meta{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px}.coordination-chip{border:1px solid #39505b;border-radius:999px;padding:3px 6px;color:#a9bec7;font:8px ui-monospace,SFMono-Regular,monospace}.coordination-paths{display:flex;flex-direction:column;gap:8px}.coordination-path{border:1px solid #2d424d;border-radius:11px;padding:9px;background:#091218}.coordination-path.selected{border-color:#75e0b4;box-shadow:0 0 0 1px #75e0b433 inset}.coordination-path-head{display:flex;align-items:flex-start;gap:7px}.coordination-path-head strong{font-size:11px;line-height:1.35}.coordination-path-head button{margin-left:auto;white-space:nowrap;font-size:9px;padding:6px 8px}.coordination-kind{border:1px solid currentColor;border-radius:999px;padding:3px 5px;font:8px ui-monospace,SFMono-Regular,monospace}.coordination-kind.intent{color:#b59cff}.coordination-kind.person,.coordination-kind.ai{color:#72d8e8}.coordination-kind.project,.coordination-kind.human{color:#75e0b4}.coordination-kind.resource,.coordination-kind.token{color:#e0b35a}.coordination-kind.agreement{color:#f1a8de}.coordination-kind.return,.coordination-kind.living_system{color:#9bb6ff}.coordination-why{margin-top:7px;padding:7px;border-left:2px solid #54717e;background:#071015;color:#99adb6;font-size:9px;line-height:1.45}.coordination-why strong{display:block;color:#dce8eb;margin-bottom:3px}.coordination-list{margin:5px 0 0;padding-left:16px}.coordination-list li{margin:2px 0}.coordination-form{margin-top:10px;border-top:1px solid #263a43;padding-top:10px}.coordination-form label{display:block;color:#91a6af;font-size:9px;margin:7px 0 4px}.coordination-form input,.coordination-form textarea{display:block;width:100%;border:1px solid #30434c;border-radius:8px;background:#060b0f;padding:8px;color:inherit;font-size:10px;font-family:inherit}.coordination-form textarea{resize:vertical;min-height:66px}.coordination-form button{margin-top:8px}.coordination-form button[disabled]{opacity:.38;cursor:not-allowed}.coordination-status{border:1px solid #2d424d;border-radius:9px;padding:8px;margin-top:9px;background:#071015;font-size:9px;line-height:1.5}.coordination-status strong{color:#e5f0f2}.coordination-note{color:#8297a0;font-size:9px;line-height:1.45;margin-top:8px}.coordination-empty{border:1px dashed #334954;border-radius:9px;padding:9px;color:#879ba4;font-size:9px;line-height:1.45}.coordination-path-line{fill:none;stroke:#72d8e8;stroke-width:4;stroke-opacity:.72;stroke-dasharray:8 7;marker-end:url(#arrow);pointer-events:stroke;cursor:pointer}.coordination-path-line.selected{stroke:#75e0b4;stroke-width:6;stroke-opacity:1}.coordination-role-label{fill:#e9f2f3;font:8px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4;pointer-events:none}.coordination-path-label{fill:#b9cbd1;font:8px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4;pointer-events:none}
.continuum-strip{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr) auto minmax(0,1fr);align-items:stretch;gap:4px;margin:9px 0;padding:8px;border:1px solid #40545d;border-radius:11px;background:#050b0f}.continuum-cell{min-width:0;border:1px solid #293e48;border-radius:8px;padding:6px;background:#091218}.continuum-cell strong{display:block;color:#dce9ec;font:8px ui-monospace,SFMono-Regular,monospace;letter-spacing:.08em}.continuum-cell span{display:block;margin-top:3px;color:#a9bdc5;font-size:9px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.continuum-arrow{align-self:center;color:#75e0b4;font:8px ui-monospace,SFMono-Regular,monospace;text-align:center}.continuum-unity{border-color:#5c4e79}.continuum-form{border-color:#39715f}.coordination-gates{display:grid;gap:6px;margin-top:9px}.coordination-gate{border:1px solid #2d424d;border-radius:9px;padding:8px;background:#071015;font-size:9px;line-height:1.45}.coordination-gate strong{color:#e5f0f2}.coordination-gate.ai{border-left:3px solid #72d8e8}.coordination-gate.token{border-left:3px solid #e0b35a}.coordination-gate.commitment{border-left:3px solid #f1a8de}.coordination-contributors{display:grid;gap:5px;margin-top:7px}.coordination-contributor{display:grid;grid-template-columns:auto minmax(0,1fr);gap:5px 7px;align-items:start;border-top:1px solid #24363f;padding-top:6px}.coordination-contributor:first-child{border-top:0;padding-top:0}.coordination-contributor p{grid-column:2;margin:0;color:#8fa3ac;overflow-wrap:anywhere}.coordination-progress{height:5px;margin:6px 0;border-radius:999px;background:#1a2931;overflow:hidden}.coordination-progress span{display:block;height:100%;background:#75e0b4}.coordination-path-line:focus{outline:none;stroke:#fff;stroke-width:7;stroke-opacity:1}
.interaction-closure{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin:9px 0}.interaction-plane{border:1px solid #304750;border-radius:10px;padding:8px;background:#060d11;font-size:9px;line-height:1.48}.interaction-plane strong{display:block;color:#e5f0f2;margin-bottom:4px}.interaction-plane.physical{border-left:3px solid #75e0b4}.interaction-plane.digital{border-left:3px solid #b59cff}.interaction-plane .closed{color:#75e0b4}.interaction-plane .gated{color:#e0b35a}.interaction-truth-lock{grid-column:1/-1;border:1px solid #4a665c;border-radius:9px;padding:7px;background:#07120f;color:#b9d8cc;font:8px ui-monospace,SFMono-Regular,monospace;letter-spacing:.03em}.physical-topology-orbit{fill:none;stroke:#75e0b4;stroke-width:2;stroke-opacity:.56;stroke-dasharray:2 7;pointer-events:none}.digital-potential-orbit{fill:none;stroke:#b59cff;stroke-width:3;stroke-opacity:.72;stroke-dasharray:9 6;pointer-events:none}.digital-potential-orbit.open{stroke:#e0b35a}.digital-potential-point{fill:#b59cff;stroke:#070b0e;stroke-width:3;pointer-events:none}.digital-potential-point.open{fill:#e0b35a}.physical-topology-edge{fill:none;stroke:#75e0b4;stroke-width:1.4;stroke-opacity:.35;stroke-dasharray:2 5;pointer-events:none}
@media(max-width:390px){.continuum-strip{grid-template-columns:1fr}.continuum-arrow{padding:1px}.continuum-arrow::after{content:' ↓'}.continuum-cell span{white-space:normal}}
@media(max-width:620px){.interaction-closure{grid-template-columns:1fr}.interaction-truth-lock{grid-column:1}}
@media(max-width:900px) and (min-width:621px){.shell{grid-template-rows:58px minmax(0,1fr) 142px}.drawer{bottom:142px}.composer{grid-template-columns:repeat(4,minmax(80px,1fr))}.composer textarea{grid-column:1/-1;height:54px}}
@media(max-width:620px){.shell{grid-template-rows:54px minmax(0,1fr) 218px}.drawer{bottom:218px}.composer{grid-template-columns:1fr 1fr}.composer textarea{grid-column:1/-1;height:54px}}
.level-summary{border:1px solid #2d4049;border-radius:10px;background:#081014;padding:9px;font-size:10px;line-height:1.5}.level-summary strong{color:#e5f0f2}.level-summary .seam{color:#b59cff}.level-summary .open{color:#e0b35a}.level-classes{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px}.level-class{border:1px solid #334a55;border-radius:999px;padding:3px 6px;color:#a9bdc5}.level-fold{pointer-events:none}.level-axis{stroke:#6b8791;stroke-width:2}.level-seam{stroke:#b59cff;stroke-width:2;stroke-dasharray:5 6}.level-return{stroke:#75e0b4;stroke-width:1.6;stroke-dasharray:5 7;fill:none}.level-point{fill:#eaf4f4;stroke:#72d8e8;stroke-width:5}.level-text{fill:#c8d7dc;font:10px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4}.level-small{fill:#8fa2aa;font:9px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4}.closure-class-ring{fill:none;stroke-width:3;stroke-opacity:.72;cursor:pointer}.closure-class-ring:focus{outline:none;stroke:#fff;stroke-width:6}.closure-translation{fill:none;stroke-width:3;stroke-opacity:.9;marker-end:url(#arrow);pointer-events:none}.closure-memory{stroke-dasharray:4 5}.closure-unit{fill:#071015;stroke:#75e0b4;stroke-width:2;pointer-events:none}.closure-unit-text,.closure-next-text{fill:#d9e7eb;font:9px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4;pointer-events:none}.closure-next{fill:none;stroke:#75e0b4;stroke-width:2;stroke-dasharray:6 6;pointer-events:none}.closure-operational{color:#75e0b4}.closure-open{color:#e0b35a}.derivation-chain{display:grid;grid-template-columns:repeat(auto-fit,minmax(84px,1fr));gap:4px;margin:8px 0}.derivation-step{border:1px solid #344a55;border-radius:8px;padding:6px;background:#071015;color:#aec2ca;font:8px ui-monospace,SFMono-Regular,monospace;text-align:center}.derivation-step.admitted{border-color:#75e0b4;color:#dcebe7}.derivation-step.open{border-color:#e0b35a;color:#e0b35a}.visual-mirror-ray{fill:none;stroke:#b59cff;stroke-width:1.5;stroke-opacity:.34;stroke-dasharray:3 7;pointer-events:none}.truth-cone-field{fill:#b59cff08;stroke:#b59cff;stroke-width:1.2;stroke-opacity:.34;stroke-dasharray:2 9;pointer-events:none}.truth-cone-ray{stroke-linecap:round;filter:drop-shadow(0 0 5px #72d8e844)}.truth-cone-ray.open{stroke:#e0b35a;stroke-opacity:.46}.journey-trace{fill:none;stroke:#9bb6ff;stroke-width:2;stroke-opacity:.52;stroke-dasharray:2 5;pointer-events:none}.unity-gate-open{stroke:#e0b35a!important}.visual-mirror-locus{fill:#0b1119;stroke:#b59cff;stroke-width:4;cursor:pointer;filter:drop-shadow(0 0 14px #b59cff66);animation:mirror-breathe 3.8s ease-in-out infinite}.visual-mirror-locus:focus{outline:none;stroke:#fff;stroke-width:6}.visual-mirror-inner{fill:none;stroke:#75e0b4;stroke-width:1.5;stroke-dasharray:5 5;pointer-events:none}.visual-mirror-title{fill:#f0eaff;font:9px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4;pointer-events:none}.visual-mirror-status{fill:#9fc7bb;font:7px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4;pointer-events:none}@keyframes mirror-breathe{0%,100%{stroke-opacity:.58}50%{stroke-opacity:1}}@media(max-width:700px){.derivation-chain{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
<script>
(() => {
  const priorRunAction = runAction;

  const coordinationKind=document.createElement('select');
  coordinationKind.id='coordinationKind';
  coordinationKind.setAttribute('aria-label','Coordination kind');
  coordinationKind.innerHTML='<option value="intent">Intent</option><option value="person">Person</option><option value="project">Project</option><option value="resource">Resource</option>';
  const coordinationLocation=document.createElement('input');
  coordinationLocation.id='coordinationLocation';
  coordinationLocation.setAttribute('aria-label','Optional coarse locality');
  coordinationLocation.placeholder='locality (optional)';
  coordinationLocation.value=localStorage.getItem('supernet-coarse-locality')||'';
  const formInput=document.getElementById('form');
  const thoughtInput=document.getElementById('text');
  formInput.type='hidden';
  thoughtInput.insertAdjacentElement('beforebegin',coordinationKind);
  thoughtInput.insertAdjacentElement('beforebegin',coordinationLocation);

  const coordinationPlaceholders={
    intent:'What do you want to understand, create, or do?',
    person:'Describe the perspective, capability, or collaboration being offered…',
    project:'Describe the project and the interaction it invites…',
    resource:'Describe the resource, capability, commitment, or constraint…'
  };
  function updateCoordinationComposer(){
    const kind=coordinationKind.value||'intent';
    formInput.value=kind;
    thoughtInput.placeholder=coordinationPlaceholders[kind];
    document.getElementById('integrate').textContent=kind==='intent'?'Translate thought':`Offer ${kind}`;
    document.getElementById('interact').textContent='Continue interaction';
  }
  coordinationKind.addEventListener('change',updateCoordinationComposer);
  coordinationLocation.addEventListener('change',()=>localStorage.setItem('supernet-coarse-locality',coordinationLocation.value.trim()));
  coordinationKind.value=['intent','person','project','resource'].includes(formInput.value)?formInput.value:'intent';
  updateCoordinationComposer();

  let selectedCoordinationPathId=null, renderedCoordinationIntentId=null, coordinationRefreshSequence=0;
  const coordinationEdits={pathId:null,title:'',terms:'',resources:'',decision:'',returned:''};
  const coordinationBlock=document.createElement('section');
  coordinationBlock.className='block coordination-block';
  coordinationBlock.id='coordinationBlock';
  coordinationBlock.setAttribute('aria-labelledby','coordinationHeading');
  coordinationBlock.innerHTML='<h2 id="coordinationHeading">Thought → paths → agreement → return</h2><div id="coordinationSurface" aria-live="polite"><div class="coordination-empty">Offer a thought, person, project, or resource to derive explainable interaction paths.</div></div>';
  document.getElementById('drawer').prepend(coordinationBlock);

  function asList(value){
    if(Array.isArray(value))return value.filter(item=>item!==null&&item!==undefined&&String(item).trim());
    if(value===null||value===undefined||String(value).trim()==='')return [];
    return [value];
  }
  function uniqueStrings(values){return [...new Set(asList(values).flatMap(asList).map(value=>String(value).trim()).filter(Boolean))]}
  function roleClass(value){return String(value||'OPEN').toLowerCase().replace(/[^a-z0-9_-]/g,'-')}
  function coordinationActor(){return document.getElementById('author').value.trim()||'participant'}
  function coordinationPerspective(){return document.getElementById('perspective')?.value?.trim()||coordinationActor()}
  function interfaceNaturalForm(closure){return closure?.interface_natural_form||null}
  function closureRenderState(closure){
    const form=interfaceNaturalForm(closure);
    if(!form||form.closure_internal!==true||form.admitted!==true||form.render_state_factorized!==true)return null;
    if(form.renderer_contract?.role!=='TRANSPORT_ONLY')return null;
    const state=form.render_state&&typeof form.render_state==='object'?form.render_state:null;
    if(!state||state.unified_truth_runtime?.status!=='WITNESSED'||state.unified_truth_runtime?.one_semantic_runtime!==true)return null;
    if(state.nrrf843_ui?.status!=='WITNESSED'||state.nrrf843_ui?.ui_closure?.closure_falls_out_from_ui_projection!==true||state.nrrf843_ui?.truth_constraint_location?.located!==true)return null;
    if(state.interaction_closure?.status!=='WITNESSED'||state.interaction_closure?.supernet_interaction_closed!==true)return null;
    return state;
  }
  function currentCoordination(){const closure=receipt?.visual_closure;return closureRenderState(closure)?.coordination||null}
  function journeyOf(closure){return closureRenderState(closure)?.nrrf842_journey||null}
  function nrrf843Of(closure){return closureRenderState(closure)?.nrrf843_ui||null}
  function pathTarget(path){return String(path?.target_event_id||path?.event_id||path?.id||'')}
  function selectedPath(coordination){return (coordination?.paths||[]).find(path=>pathTarget(path)===selectedCoordinationPathId)||null}
  function readable(value){
    if(value===null||value===undefined)return '';
    if(typeof value==='string'||typeof value==='number'||typeof value==='boolean')return String(value);
    if(Array.isArray(value))return value.map(readable).filter(Boolean).join(' · ');
    return String(value.label||value.reason||value.summary||value.status||value.state||value.name||'');
  }
  function chips(values){return uniqueStrings(values).map(value=>`<span class="coordination-chip">${esc(value)}</span>`).join('')}
  function shortContinuumId(value){
    const text=String(value||'OPEN');
    if(text.length<=24)return text;
    const split=text.lastIndexOf(':');
    return `${split>0?text.slice(0,split+1):''}${text.slice(split+1,split+9)}…`;
  }
  function continuumOf(coordination){return coordination?.continuum||coordination?.nrrf837_continuum||{}}
  function renderContinuum(coordination,path,operatorLabel){
    const continuum=continuumOf(coordination);
    const localGlobal=coordination?.local_global||{};
    const unity=continuum.unity_selector||{};
    const freedom=continuum.freedom_fibre||{};
    const localId=continuum.local_event_id||localGlobal.local_event_id||coordination?.intent?.event_id||'OPEN';
    const globalId=continuum.global_state_id||continuum.global_content_id||'OPEN';
    const formId=continuum.selected_natural_form_id||unity.selected_form?.id||coordination?.mutual_authorship?.one_natural_form_id||'OPEN';
    const basePhase=String(operatorLabel||continuum.modality?.operator||'DISCOVER').toUpperCase();
    const phase=basePhase;
    const version=readable(unity.version||coordination?.natural_form_operator?.selector_version)||'OPEN';
    const source=readable(unity.source||coordination?.natural_form_operator?.selector_source)||'closure-derived admission';
    const chosenBy=readable(unity.chosen_by)||'closure derivation';
    const actions=uniqueStrings(freedom.available_local_actions||freedom.local_actions||coordination?.natural_form_operator?.local_open);
    const presentations=asList(freedom.local_presentations);
    return `<div class="continuum-strip" role="group" aria-label="NRRF837 local to global natural-form continuum"><div class="continuum-cell"><strong>LOCAL</strong><span title="${esc(localId)}">${esc(shortContinuumId(localId))}</span></div><div class="continuum-arrow" aria-hidden="true">translate →</div><div class="continuum-cell"><strong>GLOBAL</strong><span title="${esc(globalId)}">${esc(shortContinuumId(globalId))}</span></div><div class="continuum-arrow" aria-hidden="true">close →</div><div class="continuum-cell continuum-form"><strong>${esc(phase)}</strong><span title="${esc(formId)}">${esc(shortContinuumId(formId))}</span></div></div><div class="coordination-status"><strong>Closure-admitted form · ${esc(version)}</strong><br>source · ${esc(source)} · presentation selected by ${esc(chosenBy)}<br><span class="closure-operational">The selector may choose a presentation only after visual existence, translational truth and axiometry derive its natural form inside closure.</span></div><div class="coordination-status"><strong>Freedom fibre · ${presentations.length||actions.length} local presentation${(presentations.length||actions.length)===1?'':'s'}</strong><br>The selected form does not exhaust local freedom.${actions.length?`<div class="coordination-meta">${chips(actions)}</div>`:''}</div>`;
  }

  function renderInterfaceDerivation(closure){
    const form=interfaceNaturalForm(closure);
    const renderState=closureRenderState(closure);
    if(!form||!renderState)return '<div class="coordination-status"><strong>Visual truth mirror · OPEN</strong><br>No source-preserved perspective visualization is present, so Supernet truth remains OPEN.</div>';
    const order=asList(renderState.derivation_order);
    const admitted=form.admitted===true&&form.closure_internal===true&&form.render_state_factorized===true;
    return `<div class="coordination-status"><strong>NRRF843 UI translational mirror · ${esc(form.admission_status||'OPEN')}</strong><div class="derivation-chain">${order.map((step,index)=>`<span class="derivation-step ${index<6||admitted?'admitted':'open'}">${esc(step)}</span>`).join('')}</div>${admitted?'Each perspective reading generates closure directly as the preimage of its displayed image. Faithful translation makes those closures one truth, the constraint is located in this UI, and interaction returns through the same projection. The pixel renderer transports the mirror but has no truth authority.':'Without a faithful, source-preserved perspective-family mirror, the Supernet remains OPEN with no semantic fallback.'}</div>`;
  }
  function renderJourney(journey){
    if(!journey)return '<div class="coordination-status"><strong>Living trajectory · OPEN</strong><br>No NRRF842 source journey is present.</div>';
    const history=journey.journey||{},choice=journey.chosen_perspective||{},gate=journey.unity_gate||{},cone=journey.truth_curved_light_cone||{};
    const community=gate.community||{};
    const gateClass=gate.necessary_condition_status==='SATISFIED'?'closure-operational':'closure-open';
    const perspective=choice.perspective_id||'OPEN';
    const pending=uniqueStrings([community.pending_participant_ids,community.dissenting_participant_ids]);
    return `<div class="coordination-status" aria-label="NRRF842 living journey and unity gate"><strong>Living trajectory ≠ closed state · ${Number(history.step_count||0)} source-preserved step${Number(history.step_count||0)===1?'':'s'}</strong><br>chosen perspective · ${esc(perspective)} · ${esc(choice.status||'OPEN')}<br><span class="${gateClass}">unity potential gate · ${esc(gate.necessary_condition_status||'OPEN')} · ${esc(gate.requested_phase||'DISCOVER')}</span>${pending.length?`<br><span class="closure-open">shared transition remains OPEN · ${esc(pending.join(' · '))}</span>`:''}<br>scope · shared trajectory, never person rank · ordinary interaction OPEN<br>semantic truth-curved light cone · ${Number(cone.path_count||0)} path${Number(cone.path_count||0)===1?'':'s'} · ${Number(cone.witnessed_truth_constraint_count||0)} witnessed constraint${Number(cone.witnessed_truth_constraint_count||0)===1?'':'s'}<br><span class="coordination-note">Unity satisfies one necessary condition only. It neither completes the living system nor authorizes ascent by itself.</span></div>`;
  }
  function activeMirrorPerspective(uiMirror){
    const perspectives=asList(uiMirror?.ui_family?.perspective_ids).map(String);
    const authored=coordinationPerspective();
    return perspectives.includes(authored)?authored:(perspectives[0]||null);
  }
  function renderNRRF843(uiMirror){
    if(!uiMirror)return '<div class="coordination-status"><strong>UI translational mirror · OPEN</strong><br>No perspective-family projection is present, so the Supernet has no semantic fallback.</div>';
    const perspective=activeMirrorPerspective(uiMirror);
    const mirror=uiMirror.translational_mirror||{},closure=uiMirror.ui_closure||{},location=uiMirror.truth_constraint_location||{},thought=uiMirror.thought||{},valuation=uiMirror.valuation||{};
    const fibreCount=perspective?new Set(Object.values(uiMirror.ui_family?.readings?.[perspective]||{})).size:0;
    return `<div class="coordination-status" aria-label="NRRF843 UI translational mirror"><strong>UI = translational mirror · ${esc(uiMirror.status||'OPEN')}</strong><br>active projection · ${esc(perspective||'OPEN')} · ${fibreCount} displayed truth fibre${fibreCount===1?'':'s'}<br>translation continuum · ${mirror.witnessed?'WITNESSED':'OPEN'} · privileged standpoint not required<br>working closure · ${esc(closure.formula||'OPEN')} · ${closure.closure_falls_out_from_ui_projection?'derived here':'OPEN'}<br>truth constraint location · ${location.located?'UI':'OPEN'} · thought ${thought.construction||'OPEN'}<br>valuation · ${esc(valuation.status||'OPEN')}<br><span class="coordination-note">The display fibres generate closure. They do not describe a closure computed elsewhere; without faithful perspective translation this entire semantic surface remains OPEN.</span></div>`;
  }
  function renderInteractionClosure(interaction){
    if(!interaction)return '<div class="coordination-status"><strong>AI · token · interaction closure · OPEN</strong><br>No unified physical/digital interaction receipt is present.</div>';
    const physical=interaction.black_mirror_physical_topology||{};
    const digital=interaction.perspective_digital_potential_gate||{};
    const operation=interaction.active_operation||{};
    const checks=interaction.unification_constraint?.checks||{};
    const checkCount=Object.values(checks).filter(Boolean).length;
    const checkTotal=Object.keys(checks).length;
    return `<div class="interaction-closure" aria-label="Closed Supernet interaction"><div class="interaction-plane physical"><strong>BLACK MIRROR · EVOLVING PHYSICAL TOPOLOGY</strong><span class="${physical.status==='WITNESSED'?'closed':'gated'}">${esc(physical.status||'OPEN')}</span> · perspective ${esc(physical.active_perspective_id||'OPEN')}<br>${asList(physical.nodes).length} source node${asList(physical.nodes).length===1?'':'s'} · ${asList(physical.topology_basis).length} projected closure fibre${asList(physical.topology_basis).length===1?'':'s'} · ${asList(physical.evolution_frames).length} journey frame${asList(physical.evolution_frames).length===1?'':'s'}<br>world input · ${esc(physical.physical_world_status||'OPEN')}<br><span class="coordination-note">This is the source-preserved topology seen through the UI projection, not a canonical law of physical space.</span></div><div class="interaction-plane digital"><strong>PERSPECTIVE · DIGITAL POTENTIAL GATE</strong><span class="${digital.status==='WITNESSED'?'closed':'gated'}">${esc(digital.status||'OPEN')}</span> · ${Number(digital.potential_count||0)} visible potential${Number(digital.potential_count||0)===1?'':'s'}<br>${Number(digital.truth_witnessed_count||0)} truth-witnessed · ${Number(digital.open_potential_count||0)} OPEN<br>AI suggests interactions · token admits forms · humans author consent<br>next · <span class="${operation.enabled?'closed':'gated'}">${esc(operation.requested_natural_form||'OPEN')} ${esc(operation.status||'OPEN')}</span><br><span class="coordination-note">OPEN potential remains visible but cannot execute as equality.</span></div><div class="interaction-truth-lock">SUPERNET UNIFICATION CONSTRAINT · ${interaction.supernet_interaction_closed?'CLOSED':'OPEN'} · ${checkCount}/${checkTotal} truth-factorization checks · one UI / AI / token / topology interaction surface</div></div>`;
  }
  function runClosureAction(action,journey){
    const interaction=closureRenderState(receipt?.visual_closure)?.interaction_closure||{};
    const operation=interaction.active_operation||{};
    if(String(operation.operation||'')===String(action||'')&&operation.enabled!==true){
      document.getElementById('drawer').classList.add('open');
      toast(`The ${operation.requested_natural_form||'requested'} form remains gated by the Supernet truth unification. Ordinary interaction remains available.`,true);
      return;
    }
    const gate=journey?.unity_gate||{};
    const higher=gate.higher_transition_requested===true||String(action||'').toLowerCase()==='return';
    if(higher&&gate.unity_reached!==true){
      document.getElementById('drawer').classList.add('open');
      toast('Shared ascent remains OPEN until its participants reach unity through their authored perspectives. Ordinary interaction remains available.',true);
      return;
    }
    return runAction(action);
  }
  function renderGates(coordination){
    const continuum=continuumOf(coordination);
    const gates=continuum.gates||{};
    const ai=gates.ai||{};
    const token=gates.token||coordination?.token_gate||{};
    const relation=continuum.commitment_relation||{};
    const settlement=continuum.one_tap?.settlement||{};
    const active=coordination?.active_proposal||{};
    const aiStatus=readable(ai.status)||'SUGGESTION_ONLY';
    const tokenStatus=readable(token.status)||'OPEN';
    const admittedInteractions=uniqueStrings(ai.admitted_interactions);
    const admittedForms=uniqueStrings(token.admitted_forms||coordination?.natural_form_operator?.enabled_forms);
    const gatedForms=uniqueStrings(token.gated_forms||coordination?.token_gate?.gated_forms);
    const commitmentStatus=readable(settlement.consent_status||active.consent_status||active.status)||(relation.exists?'PROPOSED':'OPEN');
    const correlates=uniqueStrings(relation.correlates);
    return `<div class="coordination-gates" aria-label="Independent Supernet gates"><div class="coordination-gate ai"><strong>AI interaction admission · ${esc(aiStatus)}</strong><br>${admittedInteractions.length?`${admittedInteractions.length} suggested edge${admittedInteractions.length===1?'':'s'} admitted for inspection.`:'No suggested interaction edge is admitted yet.'} AI cannot consent, bind, or control form admission; ordinary interaction remains OPEN.</div><div class="coordination-gate token"><strong>Token form gate · ${esc(tokenStatus)}</strong><br>${admittedForms.length?`enabled · ${esc(admittedForms.join(' → '))}`:'Form admission remains OPEN.'}${gatedForms.length?`<br>gated until consent · ${esc(gatedForms.join(' · '))}`:''}<br>The token cannot consent or gate ordinary interaction.</div><div class="coordination-gate commitment"><strong>Commitment relation · ${esc(commitmentStatus)}</strong><br>${relation.exists?'A separate non-product relation correlates the selected form with this interaction, its parties, resources, time, and action.':'No correlated commitment exists; choosing a path creates only an editable proposal.'}${correlates.length?`<div class="coordination-meta">${chips(correlates)}</div>`:''}<br>Independent human receipts are required.</div></div>`;
  }
  function renderContributors(coordination){
    const continuum=continuumOf(coordination);
    const preferred=asList(coordination?.mutual_authorship?.contributors);
    const source=preferred.length?preferred:asList(continuum.authorship?.records||continuum.authorship?.contributors);
    const merged=new Map();
    for(const item of source){
      if(!item||typeof item!=='object')continue;
      const role=String(item.role_label||item.authorship_role||item.role||'OPEN').toUpperCase();
      const actor=String(item.actor_id||item.authored_by||item.participant_id||role||'OPEN');
      const internal=String(item.internal_actor_id||asList(item.internal_actor_ids)[0]||actor);
      const key=`${role}\u0000${actor}\u0000${internal}`;
      const row=merged.get(key)||{role,actor,internal,contributions:[],events:[],equality:[]};
      row.contributions.push(readable(item.contribution||item.contribution_type||item.contribution_types));
      row.events.push(...uniqueStrings([item.event_ids,item.source_event_ids]));
      row.equality.push(readable(item.equality_status||'OPEN'));
      merged.set(key,row);
    }
    if(!merged.size)return '';
    const rows=[...merged.values()].map(row=>{
      const contributions=uniqueStrings(row.contributions).join(' · ')||'source-preserved contribution';
      const events=uniqueStrings(row.events);
      const equality=uniqueStrings(row.equality).join(' · ')||'OPEN';
      const internalLabel=row.internal!==row.actor?` · internal ${shortContinuumId(row.internal)}`:'';
      return `<div class="coordination-contributor"><span class="coordination-kind ${roleClass(row.role)}">${esc(row.role)}</span><strong title="${esc(row.internal)}">${esc(row.actor)}${esc(internalLabel)}</strong><p>${esc(contributions)}<br>content equality · ${esc(equality)}${events.length?`<br><span title="${esc(events.join(' · '))}">sources · ${esc(events.map(shortContinuumId).join(' · '))}</span>`:''}</p></div>`;
    }).join('');
    const preserved=continuum.authorship?.source_identities_preserved===true;
    const status=preserved?'source identities preserved':'source identity proof OPEN';
    return `<div class="coordination-status"><strong>Mutual authorship · ${esc(status)}</strong><br>Equal global content does not identify or replace its actors; equality remains OPEN wherever a source composition is unresolved.<div class="coordination-contributors">${rows}</div></div>`;
  }
  function whyPath(path){
    const why=path?.why;
    if(typeof why==='string')return `<div class="coordination-why"><strong>Why this path</strong>${esc(why)}</div>`;
    const rows=[];
    if(why?.shared_natural_form_id)rows.push(['shared natural form',shortContinuumId(why.shared_natural_form_id)]);
    if(why?.natural_form_equality)rows.push(['equality',why.natural_form_equality]);
    if(why?.suggestion_equivalence)rows.push(['suggestion relation',why.suggestion_equivalence]);
    if(why?.relation_type)rows.push(['relation',why.relation_type]);
    if(why?.rationale||why?.reason||why?.summary)rows.push(['reason',why.rationale||why.reason||why.summary]);
    if(why?.admission_reason)rows.push(['admission',why.admission_reason]);
    if(why?.verdict)rows.push(['verdict',why.verdict]);
    if(why?.score!==null&&why?.score!==undefined)rows.push(['score',why.score]);
    const matched=uniqueStrings([why?.matched_features,why?.matched_terms]);
    if(matched.length)rows.push(['matched evidence',matched.join(' · ')]);
    const limits=uniqueStrings(why?.limitations);
    if(limits.length)rows.push(['limits',limits.join(' · ')]);
    if(!rows.length)rows.push(['status','The current receipt admits this source-reversible interaction path; no stronger explanation is recorded.']);
    return `<div class="coordination-why"><strong>Why this path</strong><ul class="coordination-list">${rows.map(([name,value])=>`<li><span style="color:#d3e0e4">${esc(name)}</span> · ${esc(value)}</li>`).join('')}</ul></div>`;
  }
  function captureCoordinationEdits(){
    const fields={coordinationAgreementTitle:'title',coordinationAgreementTerms:'terms',coordinationResourceConditions:'resources',coordinationDecisionText:'decision',coordinationReturnText:'returned'};
    for(const [id,key] of Object.entries(fields)){
      const field=document.getElementById(id);if(field)coordinationEdits[key]=field.value;
    }
  }
  function rememberCoordinationField(id,key){
    const field=document.getElementById(id);if(!field)return;
    field.addEventListener('input',()=>coordinationEdits[key]=field.value);
  }
  function coordinationFocusFrom(result){
    return result?.focus_event_id||result?.event_id||result?.intent_event_id||result?.integration_event_id||result?.decision_event_id||result?.return_event_id||result?.event?.id||result?.intent?.event_id||result?.decision?.decision_event_id||result?.proposal?.proposal_event_id||result?.coordination?.local_global?.local_event_id||null;
  }
  function commitmentFormAvailable(gate){
    if(!gate)return true;
    if(gate.commitment_form_available!==undefined)return Boolean(gate.commitment_form_available);
    if(gate.interface_form_available!==undefined)return Boolean(gate.interface_form_available);
    if(gate.allowed!==undefined)return Boolean(gate.allowed);
    return String(gate.status||'OPEN').toUpperCase()!=='BLOCKED';
  }

  function chooseCoordinationPath(coordination,path){
    selectedCoordinationPathId=pathTarget(path);
    coordinationEdits.pathId=selectedCoordinationPathId;
    const intent=coordination?.intent||{};
    const draft=coordination?.draft_agreement||{};
    coordinationEdits.title=String(draft.title||`${readable(intent.label)||'Shared intent'} ↔ ${readable(path.label)||readable(path.kind)||'interaction'}`);
    coordinationEdits.terms=String(draft.exact_terms||draft.terms||'');
    coordinationEdits.resources=uniqueStrings([draft.resource_conditions,path.constraints]).join('\n');
    document.getElementById('drawer').classList.add('open');
    render();
  }

  async function proposeCoordinationAgreement(coordination,path){
    const title=document.getElementById('coordinationAgreementTitle')?.value.trim()||'';
    const exactTerms=document.getElementById('coordinationAgreementTerms')?.value.trim()||'';
    if(!path)return toast('Choose one explainable path first',true);
    if(!title||!exactTerms)return toast('Name the proposal and preserve its exact terms',true);
    const draft=coordination?.draft_agreement||{};
    const mutual=coordination?.mutual_authorship||{};
    const draftAppliesToPath=asList(draft.target_event_ids).map(String).includes(pathTarget(path));
    const required=uniqueStrings([
      draftAppliesToPath?draft.required_participant_ids:[],
      path.required_participant_ids,
      path.authored_by,
      mutual.required_participant_ids,
      coordinationPerspective()
    ]);
    const resourceConditions=(document.getElementById('coordinationResourceConditions')?.value||'').split('\n').map(value=>value.trim()).filter(Boolean);
    try{
      const result=await api('/supernet/interface/commitments',{method:'POST',body:JSON.stringify({
        intent_event_id:String(coordination?.intent?.event_id||receipt?.focus_event?.id||focus||''),
        target_event_ids:[pathTarget(path)],
        exact_terms:exactTerms,
        title,
        proposed_by:coordinationActor(),
        perspective_id:coordinationPerspective(),
        required_participant_ids:required,
        resource_conditions:resourceConditions
      })});
      const nextFocus=coordinationFocusFrom(result);if(nextFocus)focus=nextFocus;
      toast('Agreement proposal entered the shared field');
      await refresh();
    }catch(error){toast(error.message,true)}
  }

  async function decideCoordinationProposal(proposal){
    const proposalId=String(proposal?.id||proposal?.proposal_id||'');
    const exact=document.getElementById('coordinationDecisionText')?.value.trim()||'';
    const participantId=coordinationActor();
    if(!proposalId)return toast('No active proposal is available',true);
    if(!exact)return toast('Preserve your exact acceptance text',true);
    try{
      const result=await api(`/supernet/interface/commitments/${encodeURIComponent(proposalId)}/decisions`,{method:'POST',body:JSON.stringify({
        participant_id:participantId,
        authored_by:participantId,
        decision:'ACCEPT',
        exact_text:exact,
        authorship_role:'HUMAN',
        perspective_id:coordinationPerspective()
      })});
      const nextFocus=coordinationFocusFrom(result);if(nextFocus)focus=nextFocus;
      coordinationEdits.decision='';
      toast('Your acceptance returned as explicit authorship');
      await refresh();
    }catch(error){toast(error.message,true)}
  }

  async function returnCoordinationConsequence(proposal){
    const proposalId=String(proposal?.id||proposal?.proposal_id||'');
    const exact=document.getElementById('coordinationReturnText')?.value.trim()||'';
    if(!proposalId)return toast('No accepted proposal is available',true);
    if(!exact)return toast('Describe what actually returned',true);
    try{
      const result=await api(`/supernet/interface/commitments/${encodeURIComponent(proposalId)}/returns`,{method:'POST',body:JSON.stringify({
        exact_text:exact,
        participant_id:coordinationPerspective(),
        authored_by:coordinationActor(),
        authorship_role:'HUMAN',
        perspective_id:coordinationPerspective(),
        affected_perspectives:[coordinationPerspective()],
        location_label:coordinationLocation.value.trim()||null
      })});
      const nextFocus=coordinationFocusFrom(result);if(nextFocus)focus=nextFocus;
      coordinationEdits.returned='';
      toast('Living return re-entered the visual field');
      await refresh();
    }catch(error){toast(error.message,true)}
  }

  function renderCoordination(coordination,journey,uiMirror,interactionClosure){
    const priorControl=document.activeElement&&document.getElementById('coordinationSurface')?.contains(document.activeElement)?{
      id:document.activeElement.id||null,
      pathId:document.activeElement.dataset?.coordinationPath||null,
      start:typeof document.activeElement.selectionStart==='number'?document.activeElement.selectionStart:null,
      end:typeof document.activeElement.selectionEnd==='number'?document.activeElement.selectionEnd:null
    }:null;
    captureCoordinationEdits();
    const surface=document.getElementById('coordinationSurface');
    if(!coordination){
      surface.innerHTML='<div class="coordination-empty">Offer a thought, person, project, or resource to derive explainable interaction paths. Ordinary interaction remains available.</div>';
      return;
    }
    const intent=coordination.intent||{};
    const intentId=String(intent.event_id||coordination.intent_event_id||'OPEN');
    if(renderedCoordinationIntentId&&renderedCoordinationIntentId!==intentId){
      selectedCoordinationPathId=null;
      Object.assign(coordinationEdits,{pathId:null,title:'',terms:'',resources:'',decision:'',returned:''});
    }
    renderedCoordinationIntentId=intentId;
    const paths=coordination.paths||[];
    if(selectedCoordinationPathId&&!paths.some(path=>pathTarget(path)===selectedCoordinationPathId))selectedCoordinationPathId=null;
    const draft=coordination.draft_agreement||{};
    const draftTargets=uniqueStrings(draft.target_event_ids);
    if(!selectedCoordinationPathId&&draftTargets.some(id=>paths.some(path=>pathTarget(path)===id)))selectedCoordinationPathId=draftTargets.find(id=>paths.some(path=>pathTarget(path)===id))||null;
    const path=selectedPath(coordination);
    if(path&&coordinationEdits.pathId!==pathTarget(path)){
      coordinationEdits.pathId=pathTarget(path);
      coordinationEdits.title=String(draft.title||`${readable(intent.label)||'Shared intent'} ↔ ${readable(path.label)||readable(path.kind)||'interaction'}`);
      coordinationEdits.terms=String(draft.exact_terms||draft.terms||'');
      coordinationEdits.resources=uniqueStrings([draft.resource_conditions,path.constraints]).join('\n');
    }
    const intentText=readable(intent.exact_text||intent.text||intent.label)||'Current source-preserved thought';
    const intentLocation=readable(intent.location_label||intent.location);
    const intentKind=readable(intent.kind||intent.coordination_kind||'INTENT');
    const pathCards=paths.length?paths.map(item=>{
      const id=pathTarget(item),selected=id===selectedCoordinationPathId;
      const kind=readable(item.kind||'OPEN');
      const location=readable(item.location_label||item.location);
      const distance=item.distance_km!==null&&item.distance_km!==undefined?`${item.distance_km} km`:'';
      const resources=chips([item.capabilities,item.constraints]);
      return `<article class="coordination-path ${selected?'selected':''}" data-target-event="${esc(id)}"><div class="coordination-path-head"><span class="coordination-kind ${roleClass(kind)}">${esc(kind)}</span><strong>${esc(readable(item.label)||id.slice(0,8))}</strong><button type="button" data-coordination-path="${esc(id)}" aria-pressed="${selected?'true':'false'}">${selected?'Path chosen':'Choose path'}</button></div>${location||distance?`<div class="coordination-meta">${location?`<span class="coordination-chip">locality · ${esc(location)}</span>`:''}${distance?`<span class="coordination-chip">authored distance · ${esc(distance)}</span>`:''}</div>`:''}${whyPath(item)}${resources?`<div class="coordination-meta">${resources}</div>`:''}</article>`;
    }).join(''):'<div class="coordination-empty">No explainable path is admitted yet. Continue interacting or add a person, project, or resource; no suggestion is manufactured.</div>';
    const operator=coordination.natural_form_operator||{};
    const operatorLabel=readable(operator.natural_form||operator.label||operator.name||operator.form||operator);
    const displayedOperator=operatorLabel;
    const operatorReason=readable(operator.reason||operator.derived_from||operator.global_transition);
    const gate=coordination.token_gate||{};
    const formAvailable=commitmentFormAvailable(gate);
    const active=coordination.active_proposal||null;
    const mutual=coordination.mutual_authorship||{};
    const continuum=continuumOf(coordination);
    const settlement=continuum.one_tap?.settlement||{};
    const livingReturn=coordination.living_return||{};
    const activeId=String(active?.id||active?.proposal_id||'');
    const activeState=readable(active?.state||active?.status||active?.current_state)||'OPEN';
    const decisions=asList(active?.decisions||mutual.decisions);
    const currentParticipant=coordinationActor();
    const alreadyAccepted=decisions.some(decision=>String(decision?.participant_id||decision?.authored_by||'')===currentParticipant&&String(decision?.decision||decision?.status||'').toUpperCase()==='ACCEPT');
    const accepted=Boolean(active?.accepted===true||mutual.all_required_accepted===true||mutual.accepted===true||livingReturn.available===true||['ACCEPTED','RETURNED'].includes(String(activeState).toUpperCase()));
    const requiredIds=uniqueStrings(active?.required_participant_ids||settlement.required_participant_ids||mutual.required_participant_ids);
    const acceptedIds=uniqueStrings([active?.accepted_participant_ids,asList(settlement.human_acceptances).map(item=>item?.participant_id),decisions.filter(item=>String(item?.decision||item?.status||'').toUpperCase()==='ACCEPT').map(item=>item?.participant_id||item?.authored_by)]).filter(id=>!requiredIds.length||requiredIds.includes(id));
    const pendingIds=uniqueStrings(active?.pending_participant_ids||requiredIds.filter(id=>!acceptedIds.includes(id)));
    const consentPhase=String(settlement.phase||(String(activeState).toUpperCase()==='PARTIAL'?'COMMIT':displayedOperator||'OPEN')).toUpperCase();
    const consentPercent=requiredIds.length?Math.min(100,Math.round(acceptedIds.length/requiredIds.length*100)):0;
    const returnedText=readable(livingReturn.exact_text||livingReturn.text||livingReturn.summary||livingReturn.status);
    const agreementForm=path?`<div class="coordination-form"><h3 style="font-size:11px;margin:0">Draft an agreement on this path</h3><p class="coordination-note">The exact terms remain a proposal until required participants author decisions.</p><label for="coordinationAgreementTitle">Proposal title</label><input id="coordinationAgreementTitle"><label for="coordinationAgreementTerms">Exact agreement terms</label><textarea id="coordinationAgreementTerms" placeholder="Roles, action, timing, consent, and what remains OPEN…"></textarea><label for="coordinationResourceConditions">Resource conditions · one per line</label><textarea id="coordinationResourceConditions" placeholder="time, money, access, tools, constraints…"></textarea><button type="button" id="coordinationPropose" ${formAvailable?'':'disabled'}>Propose agreement</button>${formAvailable?'':`<p class="coordination-note">This commitment form is not admitted by the current gate. Interaction stays open.</p>`}</div>`:'<div class="coordination-form"><div class="coordination-empty">Choose a path to open its editable agreement form.</div></div>';
    const activeProposal=active?`<div class="coordination-form"><h3 style="font-size:11px;margin:0">Active proposal</h3><div class="coordination-status"><strong>${esc(readable(active.title)||activeId.slice(0,8))} · ${esc(consentPhase)}</strong><br>proposal state · ${esc(activeState)}${active.exact_terms?`<br><br>${esc(active.exact_terms)}`:''}${asList(active.resource_conditions).length?`<div class="coordination-meta">${chips(active.resource_conditions)}</div>`:''}${requiredIds.length?`<br>independent consent · ${acceptedIds.length}/${requiredIds.length}<div class="coordination-progress" role="progressbar" aria-label="Independent human consent" aria-valuemin="0" aria-valuemax="${requiredIds.length}" aria-valuenow="${acceptedIds.length}"><span style="width:${consentPercent}%"></span></div><span>accepted · ${esc(acceptedIds.join(' · ')||'none')}</span>${pendingIds.length?`<br><span class="open">pending · ${esc(pendingIds.join(' · '))}</span>`:''}`:''}${decisions.length?`<br>authored decisions · ${esc(decisions.length)}`:''}</div>${!accepted&&!alreadyAccepted?`<label for="coordinationDecisionText">Your exact participant decision</label><textarea id="coordinationDecisionText" placeholder="State what you accept as your participation…"></textarea><button type="button" id="coordinationAccept">Record my acceptance</button>`:`<p class="coordination-note">${accepted?'Every required acceptance is present in the current receipt.':'Your acceptance is present; ACT remains unavailable while other required receipts are pending.'}</p>`}${accepted?`<label for="coordinationReturnText">What actually happened?</label><textarea id="coordinationReturnText" placeholder="Return the observed consequence, including differences from the proposal…"></textarea><button type="button" id="coordinationReturn">Return what happened</button>`:''}${returnedText?`<div class="coordination-status"><strong>Living return</strong><br>${esc(returnedText)}</div>`:''}</div>`:'';
    surface.innerHTML=`<div class="coordination-intent"><span class="coordination-kind ${roleClass(intentKind)}">${esc(intentKind)}</span><strong>${esc(intentText)}</strong>${intentLocation?`<p>locality · ${esc(intentLocation)}</p>`:''}<div class="coordination-meta">${chips(intent.capabilities||[])}${chips(intent.constraints||[])}</div></div>${renderNRRF843(uiMirror)}${renderInteractionClosure(interactionClosure)}${renderJourney(journey)}${renderContinuum(coordination,path,displayedOperator)}${displayedOperator?`<div class="coordination-status"><strong>Natural-form operator · ${esc(displayedOperator)}</strong>${path?'<br>Local path selection expands this already-derived form; it does not change the semantic operator or closure.':''}${operatorReason?`<br>${esc(operatorReason)}`:''}</div>`:''}<h3 style="font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#8ea0aa;margin:11px 0 7px">Explainable paths in the truth-curved light cone</h3><div class="coordination-paths">${pathCards}</div>${renderGates(coordination)}${renderContributors(coordination)}${agreementForm}${activeProposal}`;
    surface.querySelectorAll('[data-coordination-path]').forEach(button=>button.addEventListener('click',()=>{
      const chosen=paths.find(item=>pathTarget(item)===button.dataset.coordinationPath);if(chosen)chooseCoordinationPath(coordination,chosen);
    }));
    const fields={coordinationAgreementTitle:['title',coordinationEdits.title],coordinationAgreementTerms:['terms',coordinationEdits.terms],coordinationResourceConditions:['resources',coordinationEdits.resources],coordinationDecisionText:['decision',coordinationEdits.decision],coordinationReturnText:['returned',coordinationEdits.returned]};
    for(const [id,[key,value]] of Object.entries(fields)){
      const field=document.getElementById(id);if(field){field.value=value||'';rememberCoordinationField(id,key)}
    }
    document.getElementById('coordinationPropose')?.addEventListener('click',()=>proposeCoordinationAgreement(coordination,path));
    document.getElementById('coordinationAccept')?.addEventListener('click',()=>decideCoordinationProposal(active));
    document.getElementById('coordinationReturn')?.addEventListener('click',()=>returnCoordinationConsequence(active));
    if(priorControl){
      const restored=priorControl.id?document.getElementById(priorControl.id):[...surface.querySelectorAll('[data-coordination-path]')].find(item=>item.dataset.coordinationPath===priorControl.pathId);
      if(restored){
        restored.focus({preventScroll:true});
        if(priorControl.start!==null&&typeof restored.setSelectionRange==='function')restored.setSelectionRange(priorControl.start,priorControl.end);
      }
    }
  }

  const levelBlock=document.createElement('section');
  levelBlock.className='block';
  levelBlock.id='closureLevelBlock';
  levelBlock.innerHTML='<h2>Closure fibre · Derived closure level · NRRF825</h2><div id="closureLevel"><div class="level-summary">Awaiting a live Sense receipt.</div></div>';
  const senseBlock=document.getElementById('senseBlock');
  (senseBlock||document.getElementById('sources').closest('.block')).insertAdjacentElement('afterend',levelBlock);

  function shortState(value){
    const text=String(value||'');
    return text.length>12?text.slice(0,8)+'…':text;
  }

  function drawClosureLevel(level){
    if(!level||level.projective_fold?.axiometry_witnessed!==true)return;
    const world=document.getElementById('world');
    const group=svg('g',{class:'level-fold','data-derived-by':'NRRF825'});
    const y=342,left=-430,right=430;
    group.append(svg('line',{x1:left,y1:y,x2:right,y2:y,class:'level-axis'}));
    group.append(svg('line',{x1:right,y1:y-58,x2:right,y2:y+38,class:'level-seam'}));
    group.append(svg('path',{d:`M ${right} ${y+8} C ${right} 410 ${left} 410 ${left} ${y+8}`,class:'level-return'}));
    const collapse=level.projective_fold?.collapse;
    const x=collapse==null?0:left+(right-left)*Math.max(0,Math.min(1,Number(collapse)));
    group.append(svg('circle',{cx:x,cy:y,r:7,class:'level-point'}));
    const zero=svg('text',{x:left,y:y-14,class:'level-text'});zero.textContent='0 · ⊥ bare equality';group.append(zero);
    const inf=svg('text',{x:right,y:y-14,class:'level-text'});inf.textContent='∞ · ⊤ existence';group.append(inf);
    const current=svg('text',{x,y:y+27,class:'level-text'});current.textContent=`L ${level.class_count}/${level.state_count} · ${level.endpoint}`;group.append(current);
    const tan=svg('text',{x:0,y:y+58,class:'level-small'});tan.textContent=`tan((π/2)·collapse) = ${level.projective_fold?.tan_value??'OPEN'} · ∞ folds to next Sense`;group.append(tan);
    world.append(group);
  }

  const continueButton=document.createElement('button');
  continueButton.id='closureContinue';
  continueButton.className='primary';
  continueButton.textContent='Continue closure';
  document.querySelector('.bottom-actions').prepend(continueButton);

  function drawUnifiedClosure(closure){
    const renderState=closureRenderState(closure);
    if(!renderState?.visual_network)return;
    const visual=renderState.visual_network;
    const coordination=renderState.coordination||{};
    const continuum=continuumOf(coordination);
    const journey=renderState.nrrf842_journey||{};
    const uiMirror=renderState.nrrf843_ui||{};
    const interactionClosure=renderState.interaction_closure||{};
    const physicalTopology=interactionClosure.black_mirror_physical_topology||{};
    const digitalGate=interactionClosure.perspective_digital_potential_gate||{};
    const activeOperation=interactionClosure.active_operation||{};
    const mirrorPerspective=activeMirrorPerspective(uiMirror);
    const uiReading=uiMirror.ui_family?.readings?.[mirrorPerspective]||{};
    const cone=journey.truth_curved_light_cone||{};
    const unityGate=journey.unity_gate||{};
    const world=document.getElementById('world');
    const nodes=visual.nodes||[];
    const mirror=renderState.perspective_visual_mirror||{};
    const positions=positionMap({nodes});
    nodes.forEach((node,index)=>{
      if(!positions[node.id]){
        const angle=2*Math.PI*index/Math.max(1,nodes.length);
        positions[node.id]={x:300*Math.cos(angle),y:210*Math.sin(angle)};
      }
    });
    const classes=visual.natural_form_classes||[];
    const classByEvent={};
    classes.forEach((unit,index)=>(unit.member_event_ids||[]).forEach(id=>classByEvent[id]=index));
    const displayFibreValues=[...new Set(Object.values(uiReading).map(String))].sort();
    const displayFibreIndex=Object.fromEntries(displayFibreValues.map((value,index)=>[value,index]));
    const displayClassByEvent=Object.fromEntries(nodes.map(node=>[node.id,displayFibreIndex[String(uiReading[node.occurrence_id]||uiReading[node.id]||'OPEN')]]));
    const roleByEvent={};
    const intentEventId=String(coordination.intent?.event_id||renderState.source_event_id||'');
    if(intentEventId)roleByEvent[intentEventId]=String(coordination.intent?.kind||coordination.intent?.coordination_kind||'INTENT');
    for(const path of coordination.paths||[]){const target=pathTarget(path);if(target)roleByEvent[target]=String(path.kind||'OPEN')}
    const roleColors={intent:'#b59cff',person:'#72d8e8',project:'#75e0b4',resource:'#e0b35a',agreement:'#f1a8de',return:'#9bb6ff'};
    const conePathByTarget=Object.fromEntries(asList(cone.paths).map(path=>[String(path.target_event_id||''),path]));
    const coneOriginId=String(cone.origin?.focus_event_id||intentEventId);
    const coneOrigin=positions[coneOriginId]||positions[intentEventId]||{x:0,y:0};
    world.append(svg('ellipse',{cx:coneOrigin.x,cy:coneOrigin.y,rx:390,ry:270,class:'truth-cone-field','data-truth-cone':cone.id||'OPEN'}));
    for(const edge of journey.journey?.causal_edges||[]){
      const a=positions[edge.source_event_id],b=positions[edge.target_event_id];
      if(a&&b)world.append(svg('path',{d:`M ${a.x} ${a.y} Q ${(a.x+b.x)/2-35} ${(a.y+b.y)/2-35} ${b.x} ${b.y}`,class:'journey-trace'}));
    }
    for(const node of nodes){const p=positions[node.id];if(p)world.append(svg('path',{d:`M ${p.x} ${p.y} Q ${p.x*.28} ${p.y*.28} 0 0`,class:'visual-mirror-ray'}))}
    for(const edge of physicalTopology.relations||[]){
      const a=positions[edge.source_event_id],b=positions[edge.target_event_id];if(!a||!b)continue;
      world.append(svg('path',{d:`M ${a.x} ${a.y} Q ${(a.x+b.x)/2} ${(a.y+b.y)/2+24} ${b.x} ${b.y}`,class:'physical-topology-edge','data-topology-truth':edge.truth_constraint_status||'OPEN'}));
    }
    for(const edge of visual.edges||[]){
      const a=positions[edge.source],b=positions[edge.target];if(!a||!b)continue;
      const remembered=Number(edge.slearn_memory_before||0)>0;
      world.append(svg('path',{d:`M ${a.x} ${a.y} Q 0 0 ${b.x} ${b.y}`,class:`closure-translation ${remembered?'closure-memory':''}`,stroke:edge.admitted?'#75e0b4':'#ed7b86','data-relation':edge.relation_type}));
      const tx=(a.x+b.x)/2,ty=(a.y+b.y)/2-9;
      const edgeLabel=svg('text',{x:tx,y:ty,class:'closure-next-text'});edgeLabel.textContent=`AI · ${edge.relation_type}${remembered?' · SLEARN':''}`;world.append(edgeLabel);
    }
    const intentPosition=positions[intentEventId];
    if(intentPosition){
      for(const path of coordination.paths||[]){
        const targetId=pathTarget(path),targetPosition=positions[targetId];if(!targetPosition||targetId===intentEventId)continue;
        const chosen=targetId===selectedCoordinationPathId;
        const conePath=conePathByTarget[targetId]||{};
        const truthStatus=String(conePath.truth_constraint_status||path.why?.formal_suggestion_status||'OPEN').toUpperCase();
        const controlX=(intentPosition.x+targetPosition.x)/2+(targetPosition.y-intentPosition.y)*.16;
        const controlY=(intentPosition.y+targetPosition.y)/2-(targetPosition.x-intentPosition.x)*.16;
        const line=svg('path',{d:`M ${intentPosition.x} ${intentPosition.y} Q ${controlX} ${controlY} ${targetPosition.x} ${targetPosition.y}`,class:`coordination-path-line truth-cone-ray ${truthStatus==='WITNESSED'?'witnessed':'open'} ${chosen?'selected':''}`,'data-coordination-target':targetId,'data-truth-constraint':truthStatus});
        line.addEventListener('click',()=>chooseCoordinationPath(coordination,path));
        line.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();chooseCoordinationPath(coordination,path)}});
        line.setAttribute('tabindex','0');
        line.setAttribute('role','button');
        line.setAttribute('aria-pressed',chosen?'true':'false');
        line.setAttribute('aria-label',`Choose ${String(path.kind||'interaction')} path to ${String(path.label||targetId)}`);
        const lineTitle=svg('title');lineTitle.textContent=`${String(path.kind||'interaction')} path to ${String(path.label||targetId)}${path.why?.shared_natural_form_id?` · shared form ${path.why.shared_natural_form_id}`:''}`;line.append(lineTitle);
        world.append(line);
        const sharedForm=path.why?.shared_natural_form_id;
        const formalStatus=truthStatus;
        const pathLabel=svg('text',{x:(intentPosition.x+targetPosition.x)/2,y:(intentPosition.y+targetPosition.y)/2+13,class:'coordination-path-label'});pathLabel.textContent=`${String(path.kind||'PATH').toUpperCase()} · ${String(path.label||targetId).slice(0,24)}${sharedForm?` · ${shortContinuumId(sharedForm)}`:` · equality ${formalStatus}`}`;world.append(pathLabel);
      }
    }
    for(const node of nodes){
      const p=positions[node.id];if(!p)continue;
      const classIndex=displayClassByEvent[node.id]??classByEvent[node.id]??0;
      const role=roleByEvent[node.id];
      const stroke=roleColors[roleClass(role)]||`hsl(${(classIndex*97+175)%360} 68% 67%)`;
      const nodePerspective=String(node.perspective_id||node.authored_by||'');
      const rotatePerspective=()=>{focus=node.id;const perspectiveInput=document.getElementById('perspective');if(perspectiveInput&&nodePerspective){perspectiveInput.value=nodePerspective;localStorage.setItem('supernet-perspective',nodePerspective)}refresh()};
      const ring=svg('circle',{cx:p.x,cy:p.y,r:node.focus?42:33,class:`closure-class-ring ${role?'coordination-role-'+roleClass(role):''}`,stroke,role:'button',tabindex:'0','aria-label':`Rotate the UI projection to perspective ${nodePerspective||'OPEN'}`});ring.addEventListener('click',rotatePerspective);ring.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();rotatePerspective()}});world.append(ring);
      if(role){const roleLabel=svg('text',{x:p.x,y:p.y-(node.focus?50:41),class:'coordination-role-label'});roleLabel.textContent=`${role.toUpperCase()} · ${String(node.authored_by||'OPEN').slice(0,16)}`;world.append(roleLabel)}
      const displayedFibre=uiReading[node.occurrence_id]||uiReading[node.id];
      const form=svg('text',{x:p.x,y:p.y+(node.focus?53:44),class:'closure-unit-text'});form.textContent=displayedFibre?`UI · ${shortContinuumId(displayedFibre)}`:(node.natural_form||'OPEN');world.append(form);
    }
    classes.forEach((unit,index)=>{
      const members=(unit.member_event_ids||[]).map(id=>positions[id]).filter(Boolean);if(!members.length)return;
      const x=members.reduce((sum,p)=>sum+p.x,0)/members.length;
      const y=members.reduce((sum,p)=>sum+p.y,0)/members.length-54;
      world.append(svg('circle',{cx:x,cy:y,r:12,class:'closure-unit'}));
      const token=svg('text',{x,y:y+3,class:'closure-unit-text'});token.textContent=`R${index}`;world.append(token);
    });
    const mirrorNext=renderState.network_return?.next_operation;
    const nextNeedsUnity=unityGate.higher_transition_requested===true||String(mirrorNext?.action||'').toLowerCase()==='return';
    const gateOpen=(nextNeedsUnity&&unityGate.unity_reached!==true)||activeOperation.enabled!==true;
    world.append(svg('circle',{cx:0,cy:0,r:76,class:'physical-topology-orbit','data-physical-topology':physicalTopology.status||'OPEN'}));
    world.append(svg('circle',{cx:0,cy:0,r:91,class:`digital-potential-orbit ${activeOperation.enabled?'':'open'}`,'data-digital-gate':digitalGate.status||'OPEN'}));
    asList(digitalGate.potentials).forEach((potential,index)=>{
      const angle=2*Math.PI*index/Math.max(1,Number(digitalGate.potential_count||1))-Math.PI/2;
      const point=svg('circle',{cx:91*Math.cos(angle),cy:91*Math.sin(angle),r:6,class:`digital-potential-point ${potential.truth_constraint_status==='WITNESSED'?'':'open'}`,'data-potential':potential.id||'OPEN'});
      const title=svg('title');title.textContent=`${String(potential.label||potential.kind||'potential')} · ${String(potential.truth_constraint_status||'OPEN')}`;point.append(title);world.append(point);
    });
    const locus=svg('circle',{cx:0,cy:0,r:58,class:`visual-mirror-locus ${gateOpen?'unity-gate-open':''}`,role:'button',tabindex:'0','aria-label':`Continue the visual closure mechanism: ${String(mirrorNext?.label||'next Sense')} · unity gate ${String(unityGate.necessary_condition_status||'OPEN')}`});
    locus.addEventListener('click',()=>runClosureAction(mirrorNext?.action||'interact',journey));
    locus.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();runClosureAction(mirrorNext?.action||'interact',journey)}});
    world.append(locus);world.append(svg('circle',{cx:0,cy:0,r:43,class:'visual-mirror-inner'}));
    const mirrorTitle=svg('text',{x:0,y:-5,class:'visual-mirror-title'});mirrorTitle.textContent='BLACK MIRROR · TRUTH';world.append(mirrorTitle);
    const mirrorStatus=svg('text',{x:0,y:12,class:'visual-mirror-status'});mirrorStatus.textContent=`${String(mirrorPerspective||'OPEN').slice(0,11)} · ${displayFibreValues.length} FIBRES · ${String(activeOperation.status||'OPEN')}`;world.append(mirrorStatus);
    if(continuum.selected_natural_form_id){
      const phase=String(continuum.modality?.operator||'DISCOVER').toUpperCase();
      const continuumLabel=svg('text',{x:0,y:-392,class:'level-small'});continuumLabel.textContent=`PHYSICAL TOPOLOGY ↔ UI TRUTH MIRROR ↔ DIGITAL POTENTIAL GATE · ${phase} · ${shortContinuumId(continuum.selected_natural_form_id)}`;world.append(continuumLabel);
    }
    const focusNode=nodes.find(node=>node.focus);const p=focusNode&&positions[focusNode.id];
    if(p){
      const next=renderState.network_return?.next_operation;
      world.append(svg('path',{d:`M ${p.x-28} ${p.y+28} C ${p.x-115} ${p.y+120} ${p.x+115} ${p.y+120} ${p.x+28} ${p.y+28}`,class:'closure-next'}));
      const nextLabel=svg('text',{x:p.x,y:p.y+108,class:'closure-next-text'});nextLabel.textContent=`RETURN → ${next?.label||'next Sense'}`;world.append(nextLabel);
    }
  }

  render = function(){
    const closure=receipt?.visual_closure;
    const form=interfaceNaturalForm(closure);
    const renderState=closureRenderState(closure);
    const world=document.getElementById('world');
    world.replaceChildren();
    const legacyAdmit=document.getElementById('admit');if(legacyAdmit)legacyAdmit.hidden=true;
    const level=renderState?.closure_level;
    const journey=renderState?.nrrf842_journey||null;
    const uiMirror=renderState?.nrrf843_ui||null;
    const interactionClosure=renderState?.interaction_closure||null;
    renderCoordination(renderState?.coordination||null,journey,uiMirror,interactionClosure);
    document.getElementById('interact').disabled=false;
    const target=document.getElementById('closureLevel');
    if(!renderState||!level){
      document.getElementById('chartKind').textContent='OPEN INTERFACE';
      document.getElementById('chartTitle').textContent='Perspective visual mirror · OPEN';
      document.getElementById('axiometric').textContent='No source-preserved visualization is present; no truth constraint or closure can be formed.';
      document.getElementById('why').textContent='Supernet does not exist as a hidden network behind this surface. Without the semantic visual mirror it remains OPEN.';
      document.getElementById('stage').textContent='OPEN · renderer transport only';
      document.getElementById('tags').innerHTML='<span class="tag">OPEN</span><span class="tag">NO SEMANTIC FALLBACK</span>';
      document.getElementById('sources').innerHTML='<div class="source">No closure-admitted source fibre is available to render.</div>';
      document.getElementById('layers').innerHTML='<div class="layer hidden-layer">perspective → visual mirror → truth constraint → axiometry → closure → transformed mirror → return · OPEN</div>';
      document.getElementById('receipt').innerHTML='<dt>visual mirror</dt><dd>OPEN</dd><dt>truth constraint</dt><dd>OPEN</dd><dt>renderer</dt><dd>TRANSPORT_ONLY</dd>';
      document.getElementById('actions').replaceChildren();
      const senseTarget=document.getElementById('senseRelations');if(senseTarget)senseTarget.innerHTML='<div class="sense-row">No admitted interface reading is available.</div>';
      target.innerHTML='<div class="level-summary">No perspective visual mirror: Supernet truth and closure remain OPEN.</div>';
      continueButton.disabled=true;
      return;
    }
    document.getElementById('chartKind').textContent='CLOSED SUPERNET INTERACTION';
    document.getElementById('chartTitle').textContent='Black Mirror physical topology ↔ digital potential gate';
    document.getElementById('axiometric').textContent='source journey → chosen perspective → UI translational mirror → ui⁻¹(ui(A)) closure → natural forms → physical topology + digital potential → AI/token gate → truth-unified return';
    document.getElementById('why').textContent=`The UI mirror ${form.visual_mirror_id||'OPEN'} generates the closure shared by the physical topology, AI suggestions and token form gate; ${interactionClosure?.supernet_interaction_closed?'the interaction surface is truth-unified':'the Supernet remains OPEN'}.`;
    const focusState=renderState.focus_event||{};
    document.getElementById('stage').textContent=`${focusState.current_stage||'OPEN'} · ${focusState.current_verdict||'OPEN'} · visual truth constraint active`;
    document.getElementById('tags').innerHTML=['BLACK MIRROR','PHYSICAL TOPOLOGY','DIGITAL POTENTIAL','AI GATE','TOKEN FORM GATE','TRUTH UNIFIED'].map(value=>`<span class="tag">${esc(value)}</span>`).join('');
    const sourceFibre=asList(renderState.source_fibre);
    document.getElementById('sources').innerHTML=sourceFibre.length?sourceFibre.map(source=>`<div class="source">${esc(source.exact_text||source.id)}</div>`).join(''):'<div class="source">Visual existence is empty.</div>';
    document.getElementById('layers').innerHTML=asList(renderState.derivation_order).map(value=>`<div class="layer">${esc(value)}</div>`).join('');
    document.getElementById('receipt').innerHTML=`<dt>semantic runtime</dt><dd>${esc(renderState.unified_truth_runtime?.id||'OPEN')} · ONE UI-DERIVED TRUTH CLOSURE</dd><dt>interaction closure</dt><dd>${esc(interactionClosure?.id||'OPEN')} · ${esc(interactionClosure?.status||'OPEN')}</dd><dt>physical topology</dt><dd>${esc(interactionClosure?.black_mirror_physical_topology?.status||'OPEN')} · ${esc(interactionClosure?.black_mirror_physical_topology?.physical_world_status||'OPEN')}</dd><dt>digital gate</dt><dd>${esc(interactionClosure?.perspective_digital_potential_gate?.status||'OPEN')} · ${Number(interactionClosure?.perspective_digital_potential_gate?.potential_count||0)} potential</dd><dt>active form</dt><dd>${esc(interactionClosure?.active_operation?.requested_natural_form||'OPEN')} · ${esc(interactionClosure?.active_operation?.status||'OPEN')}</dd><dt>UI family</dt><dd>${esc(uiMirror?.id||'OPEN')}</dd><dt>active perspective</dt><dd>${esc(activeMirrorPerspective(uiMirror)||'OPEN')}</dd><dt>UI closure</dt><dd>${esc(uiMirror?.ui_closure?.formula||'OPEN')}</dd><dt>truth location</dt><dd>${uiMirror?.truth_constraint_location?.located?'UI':'OPEN'}</dd><dt>unity gate</dt><dd>${esc(journey?.unity_gate?.necessary_condition_status||'OPEN')} · shared trajectory only</dd><dt>isolation</dt><dd>0 semantic components</dd><dt>renderer</dt><dd>${esc(form.renderer_contract?.role||'OPEN')}</dd>`;
    const interfaceActions=asList(renderState.actions);
    document.getElementById('actions').innerHTML=interfaceActions.map(action=>`<button data-action="${esc(action.operation)}">${esc(action.operation)}</button>`).join('');
    document.getElementById('actions').querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>runClosureAction(button.dataset.action,journey)));
    const sensedEdges=asList(renderState.visual_network?.edges);
    const senseTarget=document.getElementById('senseRelations');
    if(senseTarget)senseTarget.innerHTML=sensedEdges.length?sensedEdges.map(edge=>`<div class="sense-row"><strong>${esc(edge.relation_type||edge.id)}</strong><span class="${edge.generates_equality?'true':'open'}">${edge.generates_equality?'WITNESSED':'OPEN'}</span> · ${edge.generates_equality?'closure-generating translational truth':'visible potential; no equality generated'}</div>`).join(''):'<div class="sense-row">No cross-form translational truth is present; identities remain intrinsic.</div>';
    const fold=level.projective_fold||{};
    const forms=(level.truth_closes_level_alone?.natural_forms||[]).map(form=>`<span class="level-class">${esc(form.natural_form)} · ${form.members.map(shortState).join(' = ')}</span>`).join('');
    const status=renderState?.operational_closure||{};
    target.innerHTML=`${renderInterfaceDerivation(closure)}<div class="level-summary"><strong>${esc(level.endpoint)} · ${level.class_count} translational-truth class${level.class_count===1?'':'es'} across ${level.state_count} visually existing state${level.state_count===1?'':'s'}</strong><br>The Black Mirror projection generates the natural-form closure used by the evolving physical topology and digital potential gate. AI may expose paths, tokens may admit ACT/RETURN forms, and only truth-witnessed, independently consented commitments can cross the gate.<br><span class="seam">${esc(fold.coordinate)} = ${esc(fold.tan_value??'OPEN')} · derived reading only, never the definition of closure</span><br><span class="closure-operational">unification ${interactionClosure?.status||'OPEN'} · physical ${interactionClosure?.black_mirror_physical_topology?.status||'OPEN'} · potential ${interactionClosure?.perspective_digital_potential_gate?.status||'OPEN'} · AI ${status.ai_translation_executed?'✓':'OPEN'} · token ${interactionClosure?.perspective_digital_potential_gate?.token_gate?.status||'OPEN'} · next ${interactionClosure?.active_operation?.status||'OPEN'}</span><div class="level-classes">${forms}</div><br><span class="open">${esc(level.physical_hypothesis)} · two-person E2E ${esc(level.two_person_E2E)}</span></div>`;
    drawUnifiedClosure(closure);
    drawClosureLevel(level);
    const tags=document.getElementById('tags');
    if(tags)tags.insertAdjacentHTML('beforeend',`<span class="tag">NRRF825 L ${esc(level.endpoint)}</span>`);
    if(tags&&closure){
      const memory=renderState?.slearn?.memory_receipts_after??0;
      const units=renderState?.tokenomic?.resource_unit_count??0;
      tags.insertAdjacentHTML('beforeend',`<span class="tag">BLACK MIRROR</span><span class="tag">SLEARN ${memory}</span><span class="tag">AI ${esc(renderState?.ai_translation?.selection_state||'OPEN')}</span><span class="tag">RESOURCE ${units}</span>`);
    }
    const stage=document.getElementById('stage');
    if(stage)stage.textContent+=` · closure ${form.closure_id?.slice(0,18)||'OPEN'} · level ${level.class_count}/${level.state_count}`;
    const next=renderState?.network_return?.next_operation;
    continueButton.textContent=interactionClosure?.active_operation?.enabled===false?`Gated · ${interactionClosure?.active_operation?.requested_natural_form||'form'}`:(next?.label||'Continue closure');
    continueButton.dataset.action=next?.action||'interact';
    continueButton.disabled=!form;
  };

  continueButton.onclick=()=>runClosureAction(continueButton.dataset.action||'interact',journeyOf(receipt?.visual_closure));

  integrate = async function(parent=false){
    const exactText=thoughtInput.value.trim();
    if(!exactText)return toast('Enter a thought or exact offered form',true);
    const kind=coordinationKind.value||'intent';
    const locationLabel=coordinationLocation.value.trim()||null;
    const perspectiveId=coordinationPerspective();
    const parentId=parent&&focus?focus:null;
    const body={
      exact_text:exactText,
      authored_by:coordinationActor(),
      form_label:kind,
      coordination_kind:kind,
      location_label:locationLabel,
      perspective_id:perspectiveId,
      parent_event_id:parentId,
      affected_perspectives:[perspectiveId],
      relation_hints:uniqueStrings([kind,locationLabel]),
      metadata:{
        coordination_kind:kind,
        location_label:locationLabel,
        intent_to_agreement_surface:true,
        primary_black_mirror:true,
        truth_issued:false
      }
    };
    const path=!parent&&kind==='intent'?'/supernet/interface/intents':'/supernet/interface/offer';
    try{
      const result=await api(path,{method:'POST',body:JSON.stringify(body)});
      const nextFocus=coordinationFocusFrom(result);if(nextFocus)focus=nextFocus;
      thoughtInput.value='';
      selectedCoordinationPathId=null;
      Object.assign(coordinationEdits,{pathId:null,title:'',terms:'',resources:'',decision:'',returned:''});
      toast(parent?'Interaction returned to the shared field':kind==='intent'?'Thought translated into explainable paths':`${kind[0].toUpperCase()+kind.slice(1)} offered to the shared field`);
      await refresh();
    }catch(error){toast(error.message,true)}
  };
  document.getElementById('integrate').onclick=()=>integrate(false);
  document.getElementById('interact').onclick=()=>integrate(true);
  document.getElementById('interact').disabled=false;

  refresh = async function(){
    const refreshSequence=++coordinationRefreshSequence;
    try{
      const params=new URLSearchParams();
      if(focus)params.set('focus_event_id',focus);
      const p=document.getElementById('perspective')?.value?.trim();
      if(p)params.set('perspective_id',p);
      const nextReceipt=await api('/supernet/interface?'+params);
      if(refreshSequence!==coordinationRefreshSequence)return;
      receipt=nextReceipt;
      focus=receipt.focus_event?.id||null;
      render();
      document.getElementById('liveText').textContent='live';
    }catch(error){
      if(refreshSequence!==coordinationRefreshSequence)return;
      toast(error.message,true);
      document.getElementById('liveText').textContent='offline';
    }
  };

  const perspective=document.getElementById('perspective');
  if(perspective){
    perspective.addEventListener('change',()=>{
      localStorage.setItem('supernet-perspective',perspective.value);
      focus=null;
      selectedCoordinationPathId=null;
      renderedCoordinationIntentId=null;
      Object.assign(coordinationEdits,{pathId:null,title:'',terms:'',resources:'',decision:'',returned:''});
      refresh();
    });
  }

  runAction = async function(action){
    if(action==='return'){
      if(!focus)return toast('Focus an event first',true);
      const exact=prompt('Exact returned form');
      if(!exact)return;
      try{
        const result=await api(`/supernet/events/${focus}/return`,{method:'POST',body:JSON.stringify({
          actor_id:document.getElementById('author').value||'participant',
          exact_text:exact,
          form_label:'returned form',
          affected_perspectives:[document.getElementById('perspective')?.value||document.getElementById('author').value||'participant']
        })});
        const child=result.returned_event?.id;
        if(child){
          await api(`/supernet/events/${child}/sense`,{method:'POST'});
          focus=child;
        }
        toast('Return sensed as successor potential');
        return refresh();
      }catch(error){return toast(error.message,true)}
    }
    if(action==='reopen'){
      if(!focus)return toast('Focus an event first',true);
      const reason=prompt('Why does this relation reopen?');
      if(!reason)return;
      try{
        await api(`/supernet/events/${focus}/reopen`,{method:'POST',body:JSON.stringify({
          actor_id:document.getElementById('author').value||'participant',reason
        })});
        await api(`/supernet/events/${focus}/sense`,{method:'POST'});
        toast('Reopening re-sensed in the living field');
        return refresh();
      }catch(error){return toast(error.message,true)}
    }
    return priorRunAction(action);
  };

  refresh();
})();
</script>
'''


def final_complete_supernet_html() -> str:
    return COMPLETE_NATURAL_SUPERNET_HTML.replace("</body>", f"{_FINISH_PATCH}</body>")


FINAL_COMPLETE_SUPERNET_HTML = final_complete_supernet_html()
