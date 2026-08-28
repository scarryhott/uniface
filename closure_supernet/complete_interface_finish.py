from __future__ import annotations

from .complete_interface_web import COMPLETE_NATURAL_SUPERNET_HTML


_FINISH_PATCH = r'''
<style>
@media(min-width:901px){.composer{grid-template-columns:110px 100px 130px 180px minmax(260px,1fr);align-items:stretch}.composer textarea{grid-column:auto}}
</style>
<script>
(() => {
  const priorRunAction = runAction;

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
