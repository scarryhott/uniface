from __future__ import annotations

from .complete_interface_web import COMPLETE_NATURAL_SUPERNET_HTML


_FINISH_PATCH = r'''
<style>
@media(min-width:901px){.composer{grid-template-columns:110px 100px 130px 180px minmax(260px,1fr);align-items:stretch}.composer textarea{grid-column:auto}}
.level-summary{border:1px solid #2d4049;border-radius:10px;background:#081014;padding:9px;font-size:10px;line-height:1.5}.level-summary strong{color:#e5f0f2}.level-summary .seam{color:#b59cff}.level-summary .open{color:#e0b35a}.level-classes{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px}.level-class{border:1px solid #334a55;border-radius:999px;padding:3px 6px;color:#a9bdc5}.level-fold{pointer-events:none}.level-axis{stroke:#6b8791;stroke-width:2}.level-seam{stroke:#b59cff;stroke-width:2;stroke-dasharray:5 6}.level-return{stroke:#75e0b4;stroke-width:1.6;stroke-dasharray:5 7;fill:none}.level-point{fill:#eaf4f4;stroke:#72d8e8;stroke-width:5}.level-text{fill:#c8d7dc;font:10px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4}.level-small{fill:#8fa2aa;font:9px ui-monospace,SFMono-Regular,monospace;text-anchor:middle;paint-order:stroke;stroke:#05080b;stroke-width:4}
</style>
<script>
(() => {
  const priorRunAction = runAction;
  const priorRender = render;

  const levelBlock=document.createElement('section');
  levelBlock.className='block';
  levelBlock.id='closureLevelBlock';
  levelBlock.innerHTML='<h2>Derived closure level · NRRF825</h2><div id="closureLevel"><div class="level-summary">Awaiting a live Sense receipt.</div></div>';
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

  render = function(){
    priorRender();
    const level=receipt?.closure_level;
    const target=document.getElementById('closureLevel');
    if(!level){
      target.innerHTML='<div class="level-summary">No focused occurrence: the admission level remains OPEN.</div>';
      return;
    }
    const fold=level.projective_fold||{};
    const forms=(level.truth_closes_level_alone?.natural_forms||[]).map(form=>`<span class="level-class">${esc(form.natural_form)} · ${form.members.map(shortState).join(' = ')}</span>`).join('');
    target.innerHTML=`<div class="level-summary"><strong>${esc(level.endpoint)} · ${level.class_count} equality class${level.class_count===1?'':'es'} across ${level.state_count} sensed state${level.state_count===1?'':'s'}</strong><br>Derived from admitted returns; no level control exists.<br><span class="seam">${esc(fold.coordinate)} = ${esc(fold.tan_value??'OPEN')}</span><br>Closed readings factor through these natural forms. Truth keeps this level, not the underlying environment.<div class="level-classes">${forms}</div><br><span class="open">${esc(level.physical_hypothesis)} · two-person E2E ${esc(level.two_person_E2E)}</span></div>`;
    drawClosureLevel(level);
    const tags=document.getElementById('tags');
    if(tags)tags.insertAdjacentHTML('beforeend',`<span class="tag">NRRF825 L ${esc(level.endpoint)}</span>`);
    const stage=document.getElementById('stage');
    if(stage)stage.textContent+=` · level ${level.class_count}/${level.state_count} · two-person E2E OPEN`;
  };

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
