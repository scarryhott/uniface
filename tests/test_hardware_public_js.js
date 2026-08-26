#!/usr/bin/env node
/** Verify the public JS gateway matches the Python loop contract. */
const hw = require("../docs/hardware.js");
const assert = require("assert");

const api = new hw.HardwareLoopAPI();
const out = api.runFirstDeviceLoop();
assert.strictEqual(out.device.kind, "simulated_low_energy_optical_ellipse");
assert.strictEqual(out.device.real_laser, false);
assert.strictEqual(out.device.real_quantum_controller, false);
assert.strictEqual(out.device.real_fusion, false);
assert.ok(out.constraint);
assert.ok(out.constraint.G_t.path !== undefined);
assert.ok(out.constraint.G_t.phase !== undefined);
assert.ok(out.constraint.G_t.bounded_optical_envelope !== undefined);
assert.strictEqual(out.envelope.command, "u_t=SafetyEnvelope_D(G_t)");
assert.strictEqual(out.admission.kind, hw.AdmissionKind.HARDWARE_ACTUATION);
assert.strictEqual(out.receipt.decision, hw.ActuationDecision.ACTUATED);
assert.ok(out.physical_return.source_reversible);
assert.ok(out.reopening.next_interaction_id);

const interpProp = api.proposeFrom([out.interactions[0]], hw.Origin.HUMAN, "human-a");
const interp = api.admitAsNetworkInterpretation(interpProp, 5 * 60 * 1000);
assert.strictEqual(interp.kind, hw.AdmissionKind.NETWORK_INTERPRETATION);
const blocked = api.actuate(interp.admission_id);
assert.strictEqual(blocked.decision, hw.ActuationDecision.REFUSED);
assert.strictEqual(blocked.refused_reason, hw.Refusal.NETWORK_INTERPRETATION_IS_NOT_ACTUATION);

const r = hw.runRefusals();
assert.strictEqual(r.no_admission.refused_reason, hw.Refusal.NO_ADMISSION);
assert.strictEqual(r.expired.refused_reason, hw.Refusal.EXPIRED);
assert.strictEqual(r.revoked.refused_reason, hw.Refusal.REVOKED);
assert.strictEqual(r.undefined_form.refused_reason, hw.Refusal.UNDEFINED_FORM);
assert.strictEqual(r.raw_ai.refused_reason, hw.Refusal.RAW_AI_PROPOSAL_ALONE);

console.log("public hardware.js loop + refusals OK");
