"""HTML/JSON chart of the hardware loop. Not the field, not Closure.

Stdlib only. Do not treat serving this page as live two-person Uniface E2E.
"""

from __future__ import annotations

import json
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .api_hardware import HardwareLoopAPI
from .hardware_models import AdmissionKind
from .hardware_store import HardwareStore


def render_json(store: HardwareStore) -> str:
    return json.dumps(store.snapshot(), indent=2, sort_keys=True)


def render_html(store: HardwareStore) -> str:
    snap = store.snapshot()
    rows_adm = []
    for adm in snap.get("admissions", {}).values():
        kind = escape(str(adm.get("kind", "")))
        note = escape(str(adm.get("note", "")))
        rows_adm.append(f"<tr><td>{kind}</td><td>{note}</td></tr>")
    rows_rec = []
    for rec in snap.get("receipts", {}).values():
        rows_rec.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(str(rec.get("decision", ""))),
                escape(str(rec.get("refused_reason", ""))),
                escape(str(rec.get("note", ""))),
            )
        )
    env_blocks = []
    for env in snap.get("envelopes", {}).values():
        env_blocks.append(
            "<pre>{}</pre>".format(
                escape(
                    json.dumps(
                        {
                            "envelope_id": env.get("envelope_id"),
                            "device_id": env.get("device_id"),
                            "source_interaction_ids": env.get("source_interaction_ids"),
                            "participant_ids": env.get("participant_ids"),
                            "agent_ids": env.get("agent_ids"),
                            "selected_metavector": env.get("selected_metavector"),
                            "mapped_control_variables": env.get("mapped_control_variables"),
                            "min_values": env.get("min_values"),
                            "max_values": env.get("max_values"),
                            "duration": env.get("duration"),
                            "expires_at": env.get("expires_at"),
                            "required_approvals": env.get("required_approvals"),
                            "safety_policy_version": env.get("safety_policy_version"),
                            "simulation_result": env.get("simulation_result"),
                            "actuation_receipt_id": env.get("actuation_receipt_id"),
                            "rollback_neutral_state": env.get("rollback_neutral_state"),
                            "command": env.get("command"),
                        },
                        indent=2,
                    )
                )
            )
        )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Hardware closure chart — not Closure</title>
<style>
body{{font-family:system-ui,sans-serif;background:#0d121d;color:#eef3fa;margin:24px;}}
.muted{{color:#aab6c9;}}
pre{{background:#141a27;padding:12px;border-radius:10px;overflow:auto;}}
table{{border-collapse:collapse;width:100%;}}
td,th{{border-bottom:1px solid #303a50;padding:8px;text-align:left;}}
.warn{{border-left:4px solid #e7bd56;padding:8px 12px;background:#1b2334;}}
</style>
</head>
<body>
<h1>Hardware Closure Gateway (chart)</h1>
<p class="warn">This page is a digital chart of a hardware loop, not Closure.
<code>admissible as a network interpretation ≠ authorized as a hardware actuation</code>.
Hardware receives <code>u_t = SafetyEnvelope_D(G_t)</code> only.
First device = simulated low-energy optical ellipse. No real laser, SLM, quantum controller, voltage, magnet, cryo, or fusion.
TRUE is not issued. Not live two-person Uniface E2E.</p>
<p class="muted">Loop: human + AI + sensor → temporary collective constraint → hardware action → physical return → network reintegration → next interaction.</p>
<h2>Admissions</h2>
<table><thead><tr><th>kind</th><th>note</th></tr></thead><tbody>{''.join(rows_adm) or '<tr><td colspan="2">none</td></tr>'}</tbody></table>
<h2>Actuation receipts</h2>
<table><thead><tr><th>decision</th><th>refusal</th><th>note</th></tr></thead><tbody>{''.join(rows_rec) or '<tr><td colspan="3">none</td></tr>'}</tbody></table>
<h2>Safety envelopes</h2>
{''.join(env_blocks) or '<p class="muted">none</p>'}
<p class="muted">{AdmissionKind.NETWORK_INTERPRETATION.value} is not {AdmissionKind.HARDWARE_ACTUATION.value}.</p>
</body>
</html>
"""


class HardwareChartHandler(BaseHTTPRequestHandler):
    api: HardwareLoopAPI

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        store = self.api.store
        if self.path.startswith("/json"):
            body = render_json(store).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
        else:
            body = render_html(store).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(api: HardwareLoopAPI, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    handler = type("BoundHandler", (HardwareChartHandler,), {"api": api})
    return ThreadingHTTPServer((host, port), handler)


if __name__ == "__main__":
    api = HardwareLoopAPI()
    api.run_first_device_loop()
    httpd = serve(api)
    print("hardware chart at http://127.0.0.1:8765  (not Closure, not E2E)")
    httpd.serve_forever()
