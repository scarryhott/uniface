from __future__ import annotations

import inspect
from typing import Any

from . import live_sense, visual_closure
from .live_sense import LiveSenseManager
from .natural_interface_runtime import CompleteNaturalInterfaceManager
from .nrrf837 import attach_continuum_to_visual_receipt


_PATCHED = False
_UI_MARKER = "nrrf837ContinuumBlock"


_NRRF837_UI_PATCH = r'''
<style>
.nrrf837-block{background:linear-gradient(180deg,#10131b,#080d12);border-color:#4b4269}.nrrf837-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}.nrrf837-card{border:1px solid #3c4554;border-radius:9px;background:#070c11;padding:8px;min-width:0}.nrrf837-card strong{display:block;color:#edf1f6;font-size:10px;margin-bottom:4px}.nrrf837-card span,.nrrf837-card p{color:#9eadb8;font-size:9px;line-height:1.45;margin:0;overflow-wrap:anywhere}.nrrf837-flow{display:flex;align-items:center;gap:5px;flex-wrap:wrap;margin:8px 0}.nrrf837-node{border:1px solid #6a5f8f;border-radius:999px;padding:4px 7px;color:#d8cef5;font:9px ui-monospace,SFMono-Regular,monospace}.nrrf837-arrow{color:#72828b}.nrrf837-audits{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px}.nrrf837-audit{border:1px solid #3b4b54;border-radius:999px;padding:3px 6px;color:#a9bbc3;font:8px ui-monospace,SFMono-Regular,monospace}.nrrf837-audit.pass{border-color:#4d8f76;color:#83ddb8}.nrrf837-audit.open{border-color:#8f7148;color:#e0b35a}.nrrf837-note{margin-top:8px;border-left:2px solid #806fac;background:#0a0d14;padding:7px;color:#9cabb4;font-size:9px;line-height:1.45}.nrrf837-empty{border:1px dashed #4a4560;border-radius:9px;padding:9px;color:#8794a0;font-size:9px;line-height:1.45}
@media(max-width:620px){.nrrf837-grid{grid-template-columns:1fr}}
</style>
<script>
(() => {
  const markerId='nrrf837ContinuumBlock';
  if(document.getElementById(markerId))return;
  const block=document.createElement('section');
  block.className='block nrrf837-block';
  block.id=markerId;
  block.innerHTML='<h2>NRRF837 · local ↔ global continuum</h2><div id="nrrf837ContinuumSurface"><div class="nrrf837-empty">The active Sense has not yet produced a finite continuum receipt.</div></div>';
  const coordination=document.getElementById('coordinationBlock');
  const drawer=document.getElementById('drawer');
  if(coordination)coordination.insertAdjacentElement('afterend',block);else if(drawer)drawer.prepend(block);

  function safe(value){
    return String(value===null||value===undefined?'':value)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;').replace(/'/g,'&#039;');
  }
  function list(value){return Array.isArray(value)?value:[]}
  function continuum(){
    const visual=(typeof receipt!=='undefined'&&receipt)?receipt.visual_closure:null;
    return visual?.coordination?.continuum||visual?.nrrf837_continuum||null;
  }
  function audit(label,value){
    const state=value===true?'pass':'open';
    return `<span class="nrrf837-audit ${state}">${safe(label)} · ${value===true?'PASS':'OPEN'}</span>`;
  }
  function renderContinuum(){
    const surface=document.getElementById('nrrf837ContinuumSurface');
    if(!surface)return;
    const data=continuum();
    if(!data||!data.structure){
      surface.innerHTML='<div class="nrrf837-empty">The active Sense has not yet produced a finite continuum receipt.</div>';
      return;
    }
    const structure=data.structure||{};
    const active=data.active_form||{};
    const audits=data.audits||{};
    const gates=data.gates||{};
    const suggestion=data.suggestion_relation||{};
    const unity=structure.unity||{};
    const localCount=list(structure.local_monoid?.active_generator_ids).length;
    const globalCount=list(structure.global_monoid?.active_state_ids).length;
    const sameFormCount=list(suggestion.natural_form_path_ids).length;
    const openCount=list(suggestion.open_ai_candidate_path_ids).length;
    const relational=gates.relational_policy_layer_required===true;
    surface.innerHTML=`
      <div class="nrrf837-flow"><span class="nrrf837-node">L · ${localCount} local</span><span class="nrrf837-arrow">compose →</span><span class="nrrf837-node">G · ${globalCount} global</span><span class="nrrf837-arrow">form →</span><span class="nrrf837-node">U · ${list(unity.selected_local_ids).length} selected</span></div>
      <div class="nrrf837-grid">
        <div class="nrrf837-card"><strong>Active natural form</strong><span>${safe(active.natural_form_label||'OPEN')} · freedom ${safe(active.freedom_range_size||0)}</span><p>local ${safe(active.local_id||'unresolved')} → ${safe(active.selected_natural_form_local_id||'unresolved')}</p></div>
        <div class="nrrf837-card"><strong>Suggestion equality</strong><span>${sameFormCount} shared-form path${sameFormCount===1?'':'s'} · ${openCount} open AI candidate${openCount===1?'':'s'}</span><p>Only shared natural forms are admitted as NRRF837 equivalences.</p></div>
        <div class="nrrf837-card"><strong>Gate boundary</strong><span>${safe(gates.independent_joint_gate?.shape||'OPEN')} independent gate</span><p>${relational?'A correlated commitment is handled by the relational policy layer.':'No non-product commitment constraint is active.'}</p></div>
        <div class="nrrf837-card"><strong>Unity policy</strong><span>explicit declaration or source-preserving default</span><p>Unity is product/governance data; it is not derived from the network.</p></div>
      </div>
      <div class="nrrf837-audits">
        ${audit('M²=M',audits.modality_idempotent)}
        ${audit('Fix(M)=U',audits.fixed_points_exactly_unity)}
        ${audit('M equality=G equality',audits.modality_equality_iff_global_equality)}
        ${audit('one U per freedom',audits.unity_intersects_each_freedom_range_once)}
      </div>
      <div class="nrrf837-note">Finite runtime audit of the active receipt. Lean supplies the abstract theorem; this interface makes its current compose, form, modality, freedom ranges, authorship condition, and product-gate limitation inspectable. No economic value or truth is issued.</div>`;
  }

  if(typeof render==='function'){
    const priorNRRF837Render=render;
    render=function(){priorNRRF837Render();renderContinuum();};
  }
  renderContinuum();
})();
</script>
'''


def _inject_ui(html: str) -> str:
    if _UI_MARKER in html:
        return html
    if "</body>" in html:
        return html.replace("</body>", f"{_NRRF837_UI_PATCH}</body>")
    return f"{html}{_NRRF837_UI_PATCH}"


def _enforce_agreement_natural_form_witness(
    receipt: dict[str, Any],
) -> dict[str, Any]:
    """Keep agreement uniqueness OPEN unless the proposal is a fixed form.

    A proposal event being present is not by itself a witness that it is the
    selected member of its active freedom range. The live receipt may expose
    `unique_under_declared_unity = True` only when every active local source of
    that proposal is already fixed by the declared modality.
    """

    coordination = receipt.get("coordination", {})
    continuum = coordination.get("continuum", {})
    agreement = continuum.get("agreement_modality", {})
    proposal_event_id = agreement.get("selected_agreement_event_id")
    if not proposal_event_id:
        agreement["selected_agreement_local_ids"] = []
        agreement["selected_agreement_in_active_continuum"] = False
        agreement["selected_agreement_is_fixed_natural_form"] = False
        agreement["unique_under_declared_unity"] = False
        agreement["uniqueness_status"] = "OPEN_NO_PROPOSAL_EVENT"
        return receipt

    rows = [
        row
        for row in continuum.get("local_presentations", [])
        if str(row.get("event_id") or "") == str(proposal_event_id)
    ]
    local_ids = [str(row["local_id"]) for row in rows if row.get("local_id")]
    in_active_continuum = bool(local_ids)
    fixed = in_active_continuum and all(
        row.get("is_natural_form") is True for row in rows
    )
    agreement["selected_agreement_local_ids"] = local_ids
    agreement["selected_agreement_in_active_continuum"] = in_active_continuum
    agreement["selected_agreement_is_fixed_natural_form"] = fixed
    agreement["unique_under_declared_unity"] = fixed
    agreement["uniqueness_status"] = (
        "WITNESSED_FIXED_NATURAL_FORM"
        if fixed
        else (
            "OPEN_NOT_SELECTED_BY_UNITY"
            if in_active_continuum
            else "OPEN_OUTSIDE_ACTIVE_CONTINUUM"
        )
    )
    return receipt


def install_nrrf837_runtime() -> None:
    """Attach NRRF837 to the existing Sense receipt.

    The patch enriches the one existing visual-closure receipt. It does not
    introduce a second event field, selector, ledger, truth authority, or
    settlement path. The closure-only UI contract is the sole source of
    primary-interface instances, so this compatibility installer never patches
    browser HTML.
    """

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_build = visual_closure.build_visual_closure_receipt
    build_signature = inspect.signature(original_build)

    def build_visual_closure_receipt(*args: Any, **kwargs: Any) -> dict[str, Any]:
        bound = build_signature.bind(*args, **kwargs)
        bound.apply_defaults()
        receipt = original_build(*args, **kwargs)
        values = bound.arguments
        enriched = attach_continuum_to_visual_receipt(
            receipt,
            event=values["event"],
            field_events=values["field_events"],
            field_occurrences=values["field_occurrences"],
            relation_receipts=values["relation_receipts"],
            closure_level=values["closure_level"],
        )
        return _enforce_agreement_natural_form_witness(enriched)

    visual_closure.build_visual_closure_receipt = build_visual_closure_receipt
    # live_sense imported the function directly, so update that reference too.
    live_sense.build_visual_closure_receipt = build_visual_closure_receipt

    original_live_capabilities = LiveSenseManager.capabilities

    def live_capabilities(self: LiveSenseManager) -> dict[str, Any]:
        base = original_live_capabilities(self)
        base.update(
            {
                "nrrf837_continuum_derived_in_same_visual_receipt": True,
                "active_compose_form_modality_tables_exposed": True,
                "finite_modality_audited": True,
                "unity_selector_is_extra_product_data": True,
                "authorship_identity_requires_natural_forms": True,
                "same_global_noncanonical_authorship_not_collapsed": True,
                "agreement_uniqueness_requires_fixed_natural_form": True,
                "independent_ai_token_gates_factor_as_product": True,
                "correlated_constraints_require_relational_policy": True,
                "economic_value_claimed": False,
                "truth_issued_by_nrrf837_runtime": False,
            }
        )
        return base

    LiveSenseManager.capabilities = live_capabilities

    original_interface_capabilities = CompleteNaturalInterfaceManager.capabilities

    def interface_capabilities(
        self: CompleteNaturalInterfaceManager,
    ) -> dict[str, Any]:
        base = original_interface_capabilities(self)
        base.update(
            {
                "nrrf837_continuum_on_primary_surface": True,
                "local_global_freedom_range_visible": True,
                "natural_form_selector_policy_visible": True,
                "same_form_suggestion_explanation_visible": True,
                "canonical_authorship_condition_visible": True,
                "agreement_fixpoint_condition_visible": True,
                "non_product_gate_limit_visible": True,
                "unity_not_derived_from_network": True,
                "no_economic_or_value_claim": True,
            }
        )
        return base

    CompleteNaturalInterfaceManager.capabilities = interface_capabilities
