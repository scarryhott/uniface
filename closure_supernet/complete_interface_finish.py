from __future__ import annotations

from .complete_interface_web import COMPLETE_NATURAL_SUPERNET_HTML


_FINISH_PATCH = r'''
<style>
@media(min-width:901px){.composer{grid-template-columns:110px 100px 150px minmax(300px,1fr);align-items:stretch}.composer textarea{grid-column:auto}}
.level-summary{border:1px solid #2d4049;border-radius:10px;background:#081014;padding:9px;font-size:10px;line-height:1.5}.level-summary strong{color:#e5f0f2}.level-summary .seam{color:#b59cff}.level-summary .open{color:#e0b35a}.level-classes{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px}.level-class{border:1px solid #334a55;border-radius:999px;padding:3px 6px;color:#a9bdc5}.level-fold{pointer-events:none}.level-axis{stroke:#6b8791;stroke-width:2}.level-seam{stroke:#b59cff;stroke-width:2;stroke-dasharray:5 6}.level-return{stroke:#75e0b4;stroke-width:1.6;stroke-dasharray:5 7;fill:none}.level-point{fill:#eaf4f4;stroke:#72d8e8;stroke-width:5}.level-text{fill:#c8d7dc;font:10px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4}.level-small{fill:#8fa2aa;font:9px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4}.closure-class-ring{fill:none;stroke-width:3;stroke-opacity:.72;pointer-events:none}.closure-translation{fill:none;stroke-width:3;stroke-opacity:.9;marker-end:url(#arrow);pointer-events:none}.closure-memory{stroke-dasharray:4 5}.closure-unit{fill:#071015;stroke:#75e0b4;stroke-width:2;pointer-events:none}.closure-unit-text,.closure-next-text{fill:#d9e7eb;font:9px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4;pointer-events:none}.closure-next{fill:none;stroke:#75e0b4;stroke-width:2;stroke-dasharray:6 6;pointer-events:none}.closure-operational{color:#75e0b4}.closure-open{color:#e0b35a}
</style>
<script>
(() => {
  const priorRunAction = runAction;
  const priorRender = render;

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
    if(!level)return;
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
    if(!closure?.visual_network)return;
    const visual=closure.visual_network;
    const world=document.getElementById('world');
    const topology=receipt?.topology||{};
    const positions=positionMap(topology);
    const nodes=visual.nodes||[];
    nodes.forEach((node,index)=>{
      if(!positions[node.id]){
        const angle=2*Math.PI*index/Math.max(1,nodes.length);
        positions[node.id]={x:300*Math.cos(angle),y:210*Math.sin(angle)};
      }
    });
    const classes=visual.natural_form_classes||[];
    const classByEvent={};
    classes.forEach((unit,index)=>(unit.member_event_ids||[]).forEach(id=>classByEvent[id]=index));
    for(const edge of visual.edges||[]){
      const a=positions[edge.source],b=positions[edge.target];if(!a||!b)continue;
      const remembered=Number(edge.slearn_memory_before||0)>0;
      world.append(svg('path',{d:`M ${a.x} ${a.y} L ${b.x} ${b.y}`,class:`closure-translation ${remembered?'closure-memory':''}`,stroke:edge.admitted?'#75e0b4':'#ed7b86','data-relation':edge.relation_type}));
      const tx=(a.x+b.x)/2,ty=(a.y+b.y)/2-9;
      const edgeLabel=svg('text',{x:tx,y:ty,class:'closure-next-text'});edgeLabel.textContent=`AI · ${edge.relation_type}${remembered?' · SLEARN':''}`;world.append(edgeLabel);
    }
    for(const node of nodes){
      const p=positions[node.id];if(!p)continue;
      const classIndex=classByEvent[node.id]??0;
      world.append(svg('circle',{cx:p.x,cy:p.y,r:node.focus?42:33,class:'closure-class-ring',stroke:`hsl(${(classIndex*97+175)%360} 68% 67%)`}));
      const form=svg('text',{x:p.x,y:p.y+(node.focus?53:44),class:'closure-unit-text'});form.textContent=node.natural_form||'OPEN';world.append(form);
    }
    classes.forEach((unit,index)=>{
      const members=(unit.member_event_ids||[]).map(id=>positions[id]).filter(Boolean);if(!members.length)return;
      const x=members.reduce((sum,p)=>sum+p.x,0)/members.length;
      const y=members.reduce((sum,p)=>sum+p.y,0)/members.length-54;
      world.append(svg('circle',{cx:x,cy:y,r:12,class:'closure-unit'}));
      const token=svg('text',{x,y:y+3,class:'closure-unit-text'});token.textContent=`R${index}`;world.append(token);
    });
    const focusNode=nodes.find(node=>node.focus);const p=focusNode&&positions[focusNode.id];
    if(p){
      const next=closure.network_return?.next_operation;
      world.append(svg('path',{d:`M ${p.x-28} ${p.y+28} C ${p.x-115} ${p.y+120} ${p.x+115} ${p.y+120} ${p.x+28} ${p.y+28}`,class:'closure-next'}));
      const nextLabel=svg('text',{x:p.x,y:p.y+108,class:'closure-next-text'});nextLabel.textContent=`RETURN → ${next?.label||'next Sense'}`;world.append(nextLabel);
    }
  }

  render = function(){
    priorRender();
    const level=receipt?.closure_level;
    const closure=receipt?.visual_closure;
    const target=document.getElementById('closureLevel');
    if(!level){
      target.innerHTML='<div class="level-summary">No focused occurrence: the admission level remains OPEN.</div>';
      return;
    }
    const fold=level.projective_fold||{};
    const forms=(level.truth_closes_level_alone?.natural_forms||[]).map(form=>`<span class="level-class">${esc(form.natural_form)} · ${form.members.map(shortState).join(' = ')}</span>`).join('');
    const status=closure?.operational_closure||{};
    target.innerHTML=`<div class="level-summary"><strong>${esc(level.endpoint)} · ${level.class_count} equality class${level.class_count===1?'':'es'} across ${level.state_count} sensed state${level.state_count===1?'':'s'}</strong><br>Derived from admitted returns; no level control exists.<br><span class="seam">${esc(fold.coordinate)} = ${esc(fold.tan_value??'OPEN')}</span><br><span class="closure-operational">Mirror ${status.black_mirror_sensed?'✓':'OPEN'} · SLEARN ${status.slearn_memory_committed?'✓':'OPEN'} · AI ${status.ai_translation_executed?'✓':'OPEN'} · resources ${closure?.tokenomic?.resource_unit_count??0} · visual ${status.visual_network_derived?'✓':'OPEN'} · return ${status.network_return_open?'OPEN':'missing'}</span><div class="level-classes">${forms}</div><br><span class="open">${esc(level.physical_hypothesis)} · two-person E2E ${esc(level.two_person_E2E)}</span></div>`;
    drawUnifiedClosure(closure);
    drawClosureLevel(level);
    const tags=document.getElementById('tags');
    if(tags)tags.insertAdjacentHTML('beforeend',`<span class="tag">NRRF825 L ${esc(level.endpoint)}</span>`);
    if(tags&&closure){
      const memory=closure.slearn?.memory_receipts_after??0;
      const units=closure.tokenomic?.resource_unit_count??0;
      tags.insertAdjacentHTML('beforeend',`<span class="tag">BLACK MIRROR</span><span class="tag">SLEARN ${memory}</span><span class="tag">AI ${esc(closure.ai_translation?.selection_state||'OPEN')}</span><span class="tag">RESOURCE ${units}</span>`);
    }
    const stage=document.getElementById('stage');
    if(stage)stage.textContent+=` · visual closure ${closure?.id?.slice(0,8)||'OPEN'} · level ${level.class_count}/${level.state_count} · two-person E2E OPEN`;
    const next=closure?.network_return?.next_operation;
    continueButton.textContent=next?.label||'Continue closure';
    continueButton.dataset.action=next?.action||'interact';
    continueButton.disabled=!closure;
    if(closure)document.getElementById('chartTitle').textContent=`Visual translational closure · ${document.getElementById('chartTitle').textContent}`;
  };

  continueButton.onclick=()=>runAction(continueButton.dataset.action||'interact');

  refresh = async function(){
    try{
      const params=new URLSearchParams();
      if(focus)params.set('focus_event_id',focus);
      const p=document.getElementById('perspective')?.value?.trim();
      if(p)params.set('perspective_id',p);
      receipt=await api('/supernet/interface?'+params);
      focus=receipt.focus_event?.id||null;
      render();
      document.getElementById('liveText').textContent='live';
    }catch(error){
      toast(error.message,true);
      document.getElementById('liveText').textContent='offline';
    }
  };

  const perspective=document.getElementById('perspective');
  if(perspective){
    perspective.addEventListener('change',()=>{
      localStorage.setItem('supernet-perspective',perspective.value);
      focus=null;
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
