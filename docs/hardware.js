/**
 * Public hardware closure gateway (chart, not Closure).
 * Mirrors closure_supernet/api_hardware.py + hardware_gateway.py + device_twin.py
 * so a visitor can RUN the simulated optical-ellipse loop in the browser.
 *
 * admissible as a network interpretation ≠ authorized as a hardware actuation
 * Hardware receives u_t = SafetyEnvelope_D(G_t) only.
 * No real laser / SLM / quantum / voltage / magnet / cryo / fusion.
 * TRUE is not issued. Not two-person Uniface E2E.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.UnifaceHardware = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const SAFETY_POLICY_VERSION = "hardware-safety-v1-simulated-optical";
  const OPTICAL_RHO_D = {
    r: ["path", "delay", "gain", "translation"],
    i: ["phase", "polarization"],
    hair: ["perturbation_directions"],
    ball: ["bounded_optical_envelope"],
    ellipse: ["mirror_geometry", "phase_transfer_geometry"],
    metavector: ["phase", "intensity", "orientation"],
  };
  const OPTICAL_BOUNDS = {
    path: [0, 1], delay: [0, 1], gain: [0, 1], translation: [-1, 1],
    phase: [-1, 1], polarization: [0, 1], perturbation_directions: [0, 1],
    bounded_optical_envelope: [0, 1], mirror_geometry: [0, 1],
    phase_transfer_geometry: [0, 1], intensity: [0, 1], orientation: [-1, 1],
  };
  const NEUTRAL = Object.fromEntries(Object.keys(OPTICAL_BOUNDS).map((k) => [k, 0]));
  const Refusal = {
    NO_ADMISSION: "no_admission",
    EXPIRED: "expired",
    REVOKED: "revoked",
    UNDEFINED_FORM: "undefined_form_OPEN",
    RAW_AI_PROPOSAL_ALONE: "raw_ai_proposal_alone",
    NETWORK_INTERPRETATION_IS_NOT_ACTUATION: "admissible_interpretation_neq_authorized_actuation",
    MISSING_APPROVALS: "missing_approvals",
    DEVICE_CLOSED: "device_CLOSED_institutional_review_only",
    SIMULATION_FAILED: "simulation_failed",
    UNBOUNDED: "unbounded",
    PUBLIC_CONSENSUS: "undifferentiated_public_consensus",
    NOT_TEMPORARY: "constraint_not_temporary",
    MISSING_ENVELOPE: "missing_safety_envelope",
  };
  const AdmissionKind = {
    NETWORK_INTERPRETATION: "admissible_as_network_interpretation",
    HARDWARE_ACTUATION: "authorized_as_hardware_actuation",
  };
  const ActuationDecision = { ACTUATED: "actuated", REFUSED: "refused" };
  const Origin = { HUMAN: "human", AUTONOMOUS_AI: "autonomous_ai", SENSOR: "sensor", COLLECTIVE: "collective" };

  function nid(prefix) {
    const hex = (typeof crypto !== "undefined" && crypto.randomUUID)
      ? crypto.randomUUID().replace(/-/g, "").slice(0, 12)
      : Math.random().toString(16).slice(2, 14);
    return prefix + "-" + hex;
  }
  function nowIso(clock) { return new Date(clock.now()).toISOString(); }

  class FrozenClock {
    constructor(t) { this.t = t instanceof Date ? t.getTime() : t; }
    now() { return this.t; }
    advance(ms) { this.t += ms; }
  }
  class UtcClock { now() { return Date.now(); } }

  class HardwareLoopAPI {
    constructor(clock) {
      this.clock = clock || new UtcClock();
      this.seq = 0;
      this.store = {
        devices: {}, participants: {}, interactions: {}, proposals: {},
        constraints: {}, envelopes: {}, admissions: {}, receipts: {},
        returns: {}, reopenings: {},
      };
      this.twin = null;
      this.state = Object.assign({}, NEUTRAL);
    }
    nextSeq() { this.seq += 1; return this.seq; }
    registerFirstDevice() {
      const device = {
        device_id: "optical-ellipse-sim-1",
        kind: "simulated_low_energy_optical_ellipse",
        status: "simulated",
        simulated: true,
        real_laser: false, real_slm: false, real_quantum_controller: false,
        real_voltage: false, real_magnet: false, real_cryo: false, real_fusion: false,
        institutional_review_only: false,
        safety_policy_version: SAFETY_POLICY_VERSION,
        sensor_channels: [{ channel_id: "optical-ellipse-sim-1-photometry", kind: "photometry" }],
        note: "FIRST DEVICE = simulated low-energy optical ellipse. Chart, not Closure.",
      };
      this.store.devices[device.device_id] = device;
      this.twin = device;
      this.state = Object.assign({}, NEUTRAL);
      return device;
    }
    addHuman(id) { this.store.participants[id] = { participant_id: id, kind: "human" }; return id; }
    addAutonomousAi(id) { this.store.participants[id] = { participant_id: id, kind: "autonomous_ai" }; return id; }
    _interact(origin, actorId, forms, controls, extra) {
      extra = extra || {};
      const item = {
        interaction_id: nid("ix"), origin, actor_id: actorId,
        device_id: this.twin.device_id,
        natural_forms: forms.map((s) => ({ symbol: s })),
        requested_controls: Object.assign({}, controls || {}),
        at: nowIso(this.clock),
        raw_ai_output: !!extra.raw_ai_output,
        undifferentiated_public_consensus: !!extra.undifferentiated_public_consensus,
        sequence: this.nextSeq(),
      };
      this.store.interactions[item.interaction_id] = item;
      return item;
    }
    humanInteract(id, forms, controls) { return this._interact(Origin.HUMAN, id, forms, controls); }
    aiInteract(id, forms, controls, raw) { return this._interact(Origin.AUTONOMOUS_AI, id, forms, controls, { raw_ai_output: !!raw }); }
    sensorInteract() {
      return this._interact(Origin.SENSOR, this.twin.sensor_channels[0].channel_id, ["ellipse"], {});
    }
    _mapped(forms) {
      const defined = {};
      const open = [];
      forms.forEach((f) => {
        const targets = OPTICAL_RHO_D[f.symbol];
        if (!targets) { open.push(f.symbol); return; }
        targets.forEach((name) => { defined[name] = OPTICAL_BOUNDS[name]; });
      });
      return { defined, open };
    }
    _allForms(ixs) {
      const out = [];
      ixs.forEach((ix) => ix.natural_forms.forEach((f) => out.push(f)));
      return out;
    }
    _mergeControls(ixs) {
      const out = {};
      ixs.forEach((ix) => Object.assign(out, ix.requested_controls));
      return out;
    }
    proposeFrom(ixs, origin, authorId, raw) {
      const prop = {
        proposal_id: nid("prop"), origin, author_id: authorId,
        device_id: this.twin.device_id,
        natural_forms: this._allForms(ixs),
        requested_controls: this._mergeControls(ixs),
        source_interaction_ids: ixs.map((x) => x.interaction_id),
        created_at: nowIso(this.clock),
        raw_ai_output: !!raw,
        sequence: this.nextSeq(),
      };
      this.store.proposals[prop.proposal_id] = prop;
      return prop;
    }
    proposeRawAi(agentId, forms, controls) {
      const ix = this.aiInteract(agentId, forms, controls, true);
      return this.proposeFrom([ix], Origin.AUTONOMOUS_AI, agentId, true);
    }
    synthesize(ixs, durationMs) {
      if (!ixs.length) throw { reason: Refusal.NO_ADMISSION };
      if (ixs.some((x) => x.undifferentiated_public_consensus)) throw { reason: Refusal.PUBLIC_CONSENSUS };
      const humans = [];
      const agents = [];
      ixs.forEach((ix) => {
        if (ix.origin === Origin.HUMAN && humans.indexOf(ix.actor_id) < 0) humans.push(ix.actor_id);
        if (ix.origin === Origin.AUTONOMOUS_AI && agents.indexOf(ix.actor_id) < 0) agents.push(ix.actor_id);
      });
      if (!humans.length && agents.length) throw { reason: Refusal.RAW_AI_PROPOSAL_ALONE };
      if (humans.length < 2) throw { reason: Refusal.MISSING_APPROVALS };
      if (!(durationMs > 0)) throw { reason: Refusal.NOT_TEMPORARY };
      const { defined, open } = this._mapped(this._allForms(ixs));
      const requested = this._mergeControls(ixs);
      const G_t = {};
      Object.keys(requested).forEach((name) => {
        if (!defined[name]) return;
        const v = requested[name], lo = defined[name][0], hi = defined[name][1];
        if (v < lo || v > hi) throw { reason: Refusal.UNBOUNDED };
        G_t[name] = v;
      });
      if (!Object.keys(G_t).length) throw { reason: Refusal.UNDEFINED_FORM };
      const constraint = {
        constraint_id: nid("Gt"), device_id: this.twin.device_id, G_t,
        source_interaction_ids: ixs.map((x) => x.interaction_id),
        participant_ids: humans, agent_ids: agents,
        expires_at: this.clock.now() + durationMs, duration_ms: durationMs,
        temporary: true, device_relative: true, bounded: true, source_reversible: true,
        time_limited: true, revocable: true, causally_ordered: true,
        safety_policy_version: SAFETY_POLICY_VERSION,
        open_unmapped_forms: open, sequence: this.nextSeq(),
      };
      this.store.constraints[constraint.constraint_id] = constraint;
      return constraint;
    }
    simulateAndWrap(constraint, approvals) {
      const predicted = {};
      let passed = true;
      Object.keys(constraint.G_t).forEach((name) => {
        const b = OPTICAL_BOUNDS[name];
        const v = constraint.G_t[name];
        if (!b || v < b[0] || v > b[1] || (name === "intensity" && v > 1)) passed = false;
        else predicted[name] = v;
      });
      if (!Object.keys(predicted).length) passed = false;
      const sim = { run_id: nid("sim"), passed, predicted_return: predicted, energy_bound_ok: passed, summary: passed ? "bounds ok; simulated low-energy optical ellipse" : "failed" };
      const mapped = Object.keys(constraint.G_t);
      const envelope = {
        envelope_id: nid("env"), device_id: this.twin.device_id,
        source_interaction_ids: constraint.source_interaction_ids,
        participant_ids: constraint.participant_ids, agent_ids: constraint.agent_ids,
        selected_metavector: {
          phase: constraint.G_t.phase, intensity: constraint.G_t.intensity, orientation: constraint.G_t.orientation,
        },
        mapped_control_variables: mapped,
        min_values: Object.fromEntries(mapped.map((k) => [k, OPTICAL_BOUNDS[k][0]])),
        max_values: Object.fromEntries(mapped.map((k) => [k, OPTICAL_BOUNDS[k][1]])),
        duration_ms: constraint.duration_ms, expires_at: constraint.expires_at,
        required_approvals: approvals.slice(), approvals: approvals.slice(),
        safety_policy_version: SAFETY_POLICY_VERSION, simulation_result: sim,
        actuation_receipt_id: null, rollback_neutral_state: Object.assign({}, NEUTRAL),
        constraint_id: constraint.constraint_id, revoked: false,
        command: "u_t=SafetyEnvelope_D(G_t)", chart_not_closure: true, sequence: this.nextSeq(),
      };
      this.store.envelopes[envelope.envelope_id] = envelope;
      return envelope;
    }
    admitAsNetworkInterpretation(proposal, durationMs) {
      const adm = {
        admission_id: nid("adm-interp"), proposal_id: proposal.proposal_id,
        kind: AdmissionKind.NETWORK_INTERPRETATION, envelope_id: null,
        admitted_at: nowIso(this.clock), expires_at: this.clock.now() + durationMs,
        revoked: false, sequence: this.nextSeq(),
        note: "admissible as a network interpretation ≠ authorized as a hardware actuation",
      };
      this.store.admissions[adm.admission_id] = adm;
      return adm;
    }
    admitForActuation(proposal, envelope) {
      const reason = this._precheck(envelope, proposal, null);
      if (reason) return this._refuse(reason, envelope.device_id, envelope.envelope_id, null);
      const adm = {
        admission_id: nid("adm-act"), proposal_id: proposal.proposal_id,
        kind: AdmissionKind.HARDWARE_ACTUATION, envelope_id: envelope.envelope_id,
        admitted_at: nowIso(this.clock), expires_at: envelope.expires_at,
        revoked: false, sequence: this.nextSeq(),
        note: "authorized as a hardware actuation under SafetyEnvelope_D; not Closure",
      };
      this.store.admissions[adm.admission_id] = adm;
      return adm;
    }
    _precheck(envelope, proposal, admission) {
      const t = this.clock.now();
      if (envelope.revoked || (admission && admission.revoked)) return Refusal.REVOKED;
      if (t >= envelope.expires_at || (admission && t >= admission.expires_at)) return Refusal.EXPIRED;
      if (!envelope.mapped_control_variables || !envelope.mapped_control_variables.length) return Refusal.UNDEFINED_FORM;
      const req = envelope.required_approvals || [];
      const got = envelope.approvals || [];
      if (req.some((id) => got.indexOf(id) < 0)) return Refusal.MISSING_APPROVALS;
      const humanN = got.filter((id) => this.store.participants[id] && this.store.participants[id].kind === "human").length;
      if (humanN < 2) return Refusal.MISSING_APPROVALS;
      if (proposal && proposal.raw_ai_output && !(envelope.participant_ids && envelope.participant_ids.length)) return Refusal.RAW_AI_PROPOSAL_ALONE;
      if (!(envelope.participant_ids && envelope.participant_ids.length)) return Refusal.RAW_AI_PROPOSAL_ALONE;
      if (!envelope.simulation_result || !envelope.simulation_result.passed) return Refusal.SIMULATION_FAILED;
      return null;
    }
    _refuse(reason, deviceId, envelopeId, admissionId) {
      const receipt = {
        receipt_id: nid("refused"), envelope_id: envelopeId || null, device_id: deviceId,
        decision: ActuationDecision.REFUSED, refused_reason: reason, applied_controls: {},
        at: nowIso(this.clock), simulated: true, admission_id: admissionId || null,
        sequence: this.nextSeq(), note: "refused: " + reason + "; chart not Closure",
      };
      this.store.receipts[receipt.receipt_id] = receipt;
      return receipt;
    }
    actuate(admissionId, proposalId) {
      const deviceId = this.twin.device_id;
      if (!admissionId) {
        const prop = proposalId ? this.store.proposals[proposalId] : null;
        if (prop && (prop.raw_ai_output || prop.origin === Origin.AUTONOMOUS_AI)) {
          return this._refuse(Refusal.RAW_AI_PROPOSAL_ALONE, prop.device_id, null, null);
        }
        return this._refuse(Refusal.NO_ADMISSION, deviceId, null, null);
      }
      const admission = this.store.admissions[admissionId];
      if (!admission) return this._refuse(Refusal.NO_ADMISSION, deviceId, null, null);
      if (admission.kind !== AdmissionKind.HARDWARE_ACTUATION) {
        return this._refuse(Refusal.NETWORK_INTERPRETATION_IS_NOT_ACTUATION, deviceId, null, admission.admission_id);
      }
      if (!admission.envelope_id) return this._refuse(Refusal.MISSING_ENVELOPE, deviceId, null, admission.admission_id);
      const envelope = this.store.envelopes[admission.envelope_id];
      if (!envelope) return this._refuse(Refusal.MISSING_ENVELOPE, deviceId, admission.envelope_id, admission.admission_id);
      const proposal = this.store.proposals[admission.proposal_id];
      const reason = this._precheck(envelope, proposal, admission);
      if (reason) return this._refuse(reason, envelope.device_id, envelope.envelope_id, admission.admission_id);
      const constraint = this.store.constraints[envelope.constraint_id];
      const applied = {};
      Object.keys(constraint.G_t).forEach((name) => {
        const v = constraint.G_t[name];
        const lo = envelope.min_values[name], hi = envelope.max_values[name];
        if (lo == null || hi == null) return;
        if (v >= lo && v <= hi) { this.state[name] = v; applied[name] = v; }
      });
      const receipt = {
        receipt_id: nid("act"), envelope_id: envelope.envelope_id, device_id: envelope.device_id,
        decision: ActuationDecision.ACTUATED, refused_reason: null, applied_controls: applied,
        at: nowIso(this.clock), simulated: true, admission_id: admission.admission_id,
        sequence: this.nextSeq(),
        note: "actuated from SafetyEnvelope_D(G_t); simulated optical ellipse; not Closure",
      };
      this.store.receipts[receipt.receipt_id] = receipt;
      envelope.actuation_receipt_id = receipt.receipt_id;
      return receipt;
    }
    physicalReturn(receipt) {
      const envelope = receipt.envelope_id ? this.store.envelopes[receipt.envelope_id] : null;
      const phys = {
        return_id: nid("ret"), receipt_id: receipt.receipt_id, device_id: receipt.device_id,
        sensor_readings: {
          photometry: this.state.intensity || 0,
          phase_return: this.state.phase || 0,
          orientation_return: this.state.orientation || 0,
          bounded_optical_envelope: this.state.bounded_optical_envelope || 0,
        },
        source_reversible: true, reintegrates_to_network: true,
        source_interaction_ids: envelope ? envelope.source_interaction_ids : [],
        at: nowIso(this.clock), simulated: true, sequence: this.nextSeq(),
        note: "physical-style return from simulated optical ellipse; not a real chamber",
      };
      this.store.returns[phys.return_id] = phys;
      return phys;
    }
    reintegrate(phys) {
      const nxt = this._interact(Origin.COLLECTIVE, "network", [], {});
      const reopening = {
        reopening_id: nid("reopen"), return_id: phys.return_id,
        next_interaction_id: nxt.interaction_id, cycle_index: 1, sequence: this.nextSeq(),
        note: "reopened network cycle; TRUE not issued; chart not Closure",
      };
      this.store.reopenings[reopening.reopening_id] = reopening;
      return reopening;
    }
    revoke(admissionId) {
      const adm = this.store.admissions[admissionId];
      adm.revoked = true;
      if (adm.envelope_id) this.store.envelopes[adm.envelope_id].revoked = true;
      return adm;
    }
    synthesizeAdmitActuate(ixs, approvals, durationMs, originAuthor) {
      let constraint;
      try { constraint = this.synthesize(ixs, durationMs); }
      catch (exc) {
        const prop = this.proposeFrom(ixs, ixs.length > 1 ? Origin.COLLECTIVE : ixs[0].origin, originAuthor, exc.reason === Refusal.RAW_AI_PROPOSAL_ALONE);
        let receipt = this.actuate(null, prop.proposal_id);
        if (receipt.refused_reason !== exc.reason) receipt = this._refuse(exc.reason, this.twin.device_id, null, null);
        return { constraint: null, envelope: null, admission: null, receipt };
      }
      const proposal = this.proposeFrom(ixs, Origin.COLLECTIVE, originAuthor);
      const envelope = this.simulateAndWrap(constraint, approvals);
      const admitted = this.admitForActuation(proposal, envelope);
      if (admitted.decision === ActuationDecision.REFUSED) {
        return { constraint, envelope, admission: null, receipt: admitted };
      }
      return { constraint, envelope, admission: admitted, receipt: this.actuate(admitted.admission_id) };
    }
    runFirstDeviceLoop() {
      const device = this.registerFirstDevice();
      this.addHuman("human-a"); this.addHuman("human-b"); this.addAutonomousAi("ai-1");
      const ixA = this.humanInteract("human-a", ["r", "ellipse"], { path: 0.2, gain: 0.1, mirror_geometry: 0.4 });
      const ixB = this.humanInteract("human-b", ["i", "metavector"], { phase: 0.15, intensity: 0.2, orientation: 0.05 });
      const ixAi = this.aiInteract("ai-1", ["ball"], { bounded_optical_envelope: 0.5 });
      const ixSense = this.sensorInteract();
      const out = this.synthesizeAdmitActuate([ixA, ixB, ixAi, ixSense], ["human-a", "human-b"], 5 * 60 * 1000, "human-a");
      let phys = null, reopening = null;
      if (out.receipt.decision === ActuationDecision.ACTUATED) {
        phys = this.physicalReturn(out.receipt);
        reopening = this.reintegrate(phys);
      }
      return {
        device, interactions: [ixA, ixB, ixAi, ixSense],
        constraint: out.constraint, envelope: out.envelope, admission: out.admission,
        receipt: out.receipt, physical_return: phys, reopening,
      };
    }
    snapshot() {
      return {
        chart_not_closure: true, TRUE_issued: false,
        command: "u_t=SafetyEnvelope_D(G_t)",
        interpretation_neq_actuation: true,
        real_laser: false, real_quantum: false, real_fusion: false,
        store: this.store,
      };
    }
  }

  function runRefusals() {
    const results = {};
    const a = new HardwareLoopAPI();
    a.registerFirstDevice(); a.addHuman("human-a");
    const ix = a.humanInteract("human-a", ["r"], { path: 0.2 });
    const prop = a.proposeFrom([ix], Origin.HUMAN, "human-a");
    results.no_admission = a.actuate(null, prop.proposal_id);

    const clock = new FrozenClock(Date.now());
    const b = new HardwareLoopAPI(clock);
    b.registerFirstDevice(); b.addHuman("human-a"); b.addHuman("human-b"); b.addAutonomousAi("ai-1");
    const ixs = [
      b.humanInteract("human-a", ["r"], { path: 0.2 }),
      b.humanInteract("human-b", ["i"], { phase: 0.1 }),
      b.aiInteract("ai-1", ["ball"], { bounded_optical_envelope: 0.3 }),
    ];
    const first = b.synthesizeAdmitActuate(ixs, ["human-a", "human-b"], 60 * 1000, "human-a");
    clock.advance(2 * 60 * 1000);
    results.expired = b.actuate(first.admission.admission_id);

    const c = new HardwareLoopAPI();
    c.registerFirstDevice(); c.addHuman("human-a"); c.addHuman("human-b"); c.addAutonomousAi("ai-1");
    const ixs2 = [
      c.humanInteract("human-a", ["ellipse"], { mirror_geometry: 0.4 }),
      c.humanInteract("human-b", ["metavector"], { intensity: 0.2, phase: 0.1, orientation: 0 }),
      c.aiInteract("ai-1", ["hair"], { perturbation_directions: 0.1 }),
    ];
    const ok = c.synthesizeAdmitActuate(ixs2, ["human-a", "human-b"], 5 * 60 * 1000, "human-a");
    c.revoke(ok.admission.admission_id);
    results.revoked = c.actuate(ok.admission.admission_id);

    const d = new HardwareLoopAPI();
    d.registerFirstDevice(); d.addHuman("human-a"); d.addHuman("human-b");
    results.undefined_form = d.synthesizeAdmitActuate([
      d.humanInteract("human-a", ["voltage"], { voltage: 12 }),
      d.humanInteract("human-b", ["money"], { money: 1 }),
    ], ["human-a", "human-b"], 5 * 60 * 1000, "human-a").receipt;

    const e = new HardwareLoopAPI();
    e.registerFirstDevice(); e.addAutonomousAi("ai-1");
    const raw = e.proposeRawAi("ai-1", ["metavector"], { phase: 0.9, intensity: 0.9, orientation: 0 });
    results.raw_ai = e.actuate(null, raw.proposal_id);
    return results;
  }

  return {
    HardwareLoopAPI, FrozenClock, Refusal, AdmissionKind, ActuationDecision, Origin,
    OPTICAL_RHO_D, SAFETY_POLICY_VERSION, runRefusals,
  };
});
