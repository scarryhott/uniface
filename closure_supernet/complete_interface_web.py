from __future__ import annotations

from .natural_interface_web import NATURAL_SUPERNET_HTML


_COMPLETE_PATCH = r'''
<style>
#perspective,#fieldKind{border:1px solid #30434c;border-radius:10px;background:#081014;padding:9px;color:inherit;min-width:118px}
.sense-row{border:1px solid #2d4049;border-radius:9px;padding:8px;margin:6px 0;background:#081014;font-size:10px;line-height:1.45}
.sense-row strong{display:block;color:#d9e6ea;margin-bottom:3px}.sense-row .open{color:#e0b35a}.sense-row .true{color:#75e0b4}.sense-row .false{color:#ed7b86}
@media(max-width:900px){#perspective,#fieldKind{min-width:90px}}
</style>
<script>
(() => {
  const baseRunAction = runAction;
  const baseRender = render;
  const composer = document.querySelector('.composer');
  const form = document.getElementById('form');
  const perspective = document.createElement('input');
  perspective.id = 'perspective';
  perspective.setAttribute('aria-label','Perspective');
  perspective.placeholder = 'perspective';
  perspective.value = localStorage.getItem('supernet-perspective') || document.getElementById('author').value || 'participant';
  perspective.addEventListener('change', () => localStorage.setItem('supernet-perspective', perspective.value));
  form.insertAdjacentElement('afterend', perspective);

  const field = document.createElement('select');
  field.id = 'fieldKind';
  field.setAttribute('aria-label','Living field');
  const options = [
    ['','AUTO FIELD'],
    ['HUMAN_INTERACTION','HUMAN INTERACTION'],
    ['SLEARN_PERSPECTIVE','SLEARN PERSPECTIVE'],
    ['BLACK_MIRROR_SENSOR','BLACK MIRROR SENSOR'],
    ['TOKENOMIC_AI','TOKENOMIC AI'],
    ['RESOURCE_WORLD','RESOURCE WORLD'],
    ['AGI_SECOND_BRAIN','AGI / SECOND BRAIN'],
    ['PSYCHOPHENOMENAL','PSYCHOPHENOMENAL'],
    ['UNKNOWN_UAP_HYPOTHESIS','UNKNOWN / UAP HYPOTHESIS'],
    ['agent','AGENT'],['resource','RESOURCE'],['hardware','HARDWARE'],['trading','TRADING']
  ];
  for (const [value,label] of options) {
    const opt=document.createElement('option'); opt.value=value; opt.textContent=label; field.append(opt);
  }
  perspective.insertAdjacentElement('afterend', field);

  const sourceBlock = document.getElementById('sources').closest('.block');
  const senseBlock = document.createElement('section');
  senseBlock.className='block'; senseBlock.id='senseBlock';
  senseBlock.innerHTML='<h2>Live relational field</h2><div id="senseRelations"><div class="sense-row">No relational receipt for this focus yet.</div></div>';
  sourceBlock.insertAdjacentElement('afterend', senseBlock);

  const actor = () => document.getElementById('author').value.trim() || 'participant';
  const perspectiveId = () => perspective.value.trim() || actor();
  const sheafKinds = new Set(['HUMAN_INTERACTION','SLEARN_PERSPECTIVE','BLACK_MIRROR_SENSOR','TOKENOMIC_AI','RESOURCE_WORLD','AGI_SECOND_BRAIN','PSYCHOPHENOMENAL','UNKNOWN_UAP_HYPOTHESIS']);

  function relationLabel(item){
    const node=(receipt?.topology?.nodes||[]).find(n=>n.id===item.target_occurrence || n.id===item.source_occurrence);
    return item.relation_type || node?.form_label || item.candidate_relation_id;
  }

  render = function(){
    baseRender();
    const sense=receipt?.sense_depth;
    const target=document.getElementById('senseRelations');
    if(sense?.relations?.length){
      target.innerHTML=sense.relations.map(item=>{
        const verdict=String(item.verdict||'OPEN');
        return `<div class="sense-row"><strong>${esc(relationLabel(item))}</strong><span class="${verdict.toLowerCase()}">${esc(verdict)}</span> · ${esc(item.rationale||'source-reversible relation')}<br><span style="color:#80929c">${esc(item.admission_reason||'awaiting admission')}</span></div>`;
      }).join('');
    } else {
      target.innerHTML='<div class="sense-row">This exact occurrence is preserved; no stronger live relation has been admitted for this focus.</div>';
    }
    if((receipt?.topology?.nodes||[]).length>1 && !document.querySelector('[data-action="collective-trace"]')){
      const button=document.createElement('button'); button.dataset.action='collective-trace'; button.textContent='Collective'; button.onclick=()=>runAction('collective-trace'); document.getElementById('actions').append(button);
    }
  };

  integrate = async function(parent=false){
    const text=document.getElementById('text').value.trim();
    if(!text)return toast('Enter an exact source',true);
    const selected=field.value;
    const body={
      exact_text:text,
      authored_by:actor(),
      form_label:document.getElementById('form').value||'note',
      perspective_id:perspectiveId(),
      parent_event_id:parent&&focus?focus:null,
      lens:sheafKinds.has(selected)?'embodied':(selected||null),
      sheaf:sheafKinds.has(selected)?selected:null,
      affected_perspectives:[perspectiveId()],
      relation_hints:selected?[selected]:[],
      metadata:{black_mirror_offer:true, field_selection:selected||'AUTO'}
    };
    try{
      const result=await api('/supernet/interface/offer',{method:'POST',body:JSON.stringify(body)});
      focus=result.focus_event_id||result.event_id;
      document.getElementById('text').value='';
      toast(parent?'Interaction sensed and returned':'Source sensed into the living field');
      await refresh();
    }catch(error){toast(error.message,true)}
  };

  function chooseNode(message='Choose a related event'){
    const nodes=(receipt?.topology?.nodes||[]).filter(n=>n.id!==focus);
    if(!nodes.length){toast('No second event is present to relate',true);return null}
    const shown=nodes.slice(0,24);
    const menu=shown.map((n,i)=>`${i+1}. ${label(n).slice(0,38)} · ${n.id.slice(0,8)}`).join('\n');
    const raw=prompt(`${message}\n\n${menu}`);
    const index=Number(raw)-1;
    if(!Number.isInteger(index)||index<0||index>=shown.length)return null;
    return shown[index];
  }

  async function relate(){
    if(!focus)return toast('Focus an event first',true);
    const target=chooseNode(); if(!target)return;
    const relation=prompt('Name the relation','OPEN_RELATION'); if(!relation)return;
    const bidirectional=/^y/i.test(prompt('Reciprocal/bidirectional? y/N','N')||'N');
    try{
      const result=await api('/supernet/relations',{method:'POST',body:JSON.stringify({
        source_event_id:focus,target_event_id:target.id,authored_by:actor(),relation_label:relation,
        preserves:['exact sources','direction','source provenance'],affected_perspectives:[perspectiveId()],bidirectional
      })});
      const id=result.relation_event.id;
      await api(`/supernet/events/${id}/sense`,{method:'POST'});
      focus=id; toast('Relation entered Sense'); await refresh();
    }catch(error){toast(error.message,true)}
  }

  async function rigidify(){
    if(!focus)return toast('Focus a relation first',true);
    const sense=receipt?.sense_depth;
    if(sense?.admissible_relations?.length){
      const admissible=sense.admissible_relations;
      const rows=(sense.relations||[]).filter(r=>admissible.includes(r.candidate_relation_id));
      const menu=rows.map((r,i)=>`${i+1}. ${r.relation_type} · ${r.candidate_relation_id.slice(0,8)}`).join('\n');
      const raw=prompt(`Select an admissible relation. If alternatives remain this is recorded as FORCED_ISOLATION, not naturality.\n\n${menu}`);
      const index=Number(raw)-1;if(!Number.isInteger(index)||index<0||index>=rows.length)return;
      try{
        const result=await api('/supernet/interface/selections',{method:'POST',body:JSON.stringify({source_event_id:focus,selected_relation_id:rows[index].candidate_relation_id,authored_by:actor(),perspective_id:perspectiveId()})});
        focus=result.integration_event_id; toast(result.evaluation.state.replaceAll('_',' ')); await refresh();
      }catch(error){toast(error.message,true)}
      return;
    }
    const raw=prompt('Site admissibility as JSON, e.g. {"direction":["relative-east"]}'); if(!raw)return;
    let sites;try{sites=JSON.parse(raw)}catch{return toast('Invalid JSON',true)}
    try{
      const result=await api(`/supernet/events/${focus}/rigidify`,{method:'POST',body:JSON.stringify({actor_id:actor(),site_admissibility:sites,partial_input:{},unitary_step:{}})});
      toast(result.rigid?'Relation rigid; natural form reported':'Relation remains OPEN'); await refresh();
    }catch(error){toast(error.message,true)}
  }

  async function returnReaction(){
    const life=receipt?.turing_being_depth; if(!life?.life_event_id)return toast('No Turing Being occurrence is focused',true);
    const exact=prompt('Exact reactor return'); if(!exact)return;
    try{
      const result=await api(`/network/turing-being/life-events/${life.life_event_id}/return`,{method:'POST',body:JSON.stringify({reaction:{exact_occurrence:exact,source_preserved:true,admitted:true,returned_to_global_hair:true,witness_ids:[]},authored_by:actor(),metadata:{black_mirror_return:true}})});
      focus=result.reaction_event_id||result.integration_event_id;
      if(focus)await api(`/supernet/events/${focus}/sense`,{method:'POST'});
      toast('Reaction returned to global hair 0+'); await refresh();
    }catch(error){toast(error.message,true)}
  }

  async function collective(){
    const nodes=(receipt?.topology?.nodes||[]); if(nodes.length<2)return toast('A collective needs at least two events',true);
    const shown=nodes.slice(0,24); const menu=shown.map((n,i)=>`${i+1}. ${label(n).slice(0,36)}`).join('\n');
    const raw=prompt(`Choose event numbers separated by commas\n\n${menu}`); if(!raw)return;
    const ids=[...new Set(raw.split(',').map(v=>shown[Number(v.trim())-1]?.id).filter(Boolean))]; if(ids.length<2)return toast('Choose at least two events',true);
    const exact=prompt('Exact collective interaction / return'); if(!exact)return;
    try{
      const result=await api('/supernet/interface/collective',{method:'POST',body:JSON.stringify({event_ids:ids,exact_text:exact,authored_by:actor(),perspective_id:perspectiveId(),affected_perspectives:[perspectiveId()]})});
      focus=result.focus_event_id; toast('Collective trajectory entered the same field'); await refresh();
    }catch(error){toast(error.message,true)}
  }

  runAction = async function(action){
    if(action==='relate')return relate();
    if(action==='rigidify')return rigidify();
    if(action==='return-reaction')return returnReaction();
    if(action==='collective-trace')return collective();
    return baseRunAction(action);
  };

  document.getElementById('integrate').onclick=()=>integrate(false);
  document.getElementById('interact').onclick=()=>integrate(true);
  refresh();
})();
</script>
'''


def complete_natural_supernet_html() -> str:
    """One public surface; semantic managers remain materialized lenses underneath."""

    return NATURAL_SUPERNET_HTML.replace("</body>", f"{_COMPLETE_PATCH}</body>")


COMPLETE_NATURAL_SUPERNET_HTML = complete_natural_supernet_html()
