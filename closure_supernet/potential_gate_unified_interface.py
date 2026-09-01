from __future__ import annotations

"""Single-route publication of the full Supernet potential-gate surface.

The generated browser program in :mod:`potential_gate_interface` expresses the
full gate. This adapter preserves the repository's one public interaction route:
navigation and return are two relative interaction kinds on that route, not
parallel application APIs.
"""

from .potential_gate_interface import POTENTIAL_GATE_SUPERNET_HTML as _BASE_HTML


def _single_interaction_route(html: str) -> str:
    body = html.replace(
        'const response=await fetch(`/supernet/potential-gates/${encodeURIComponent(active.id)}/navigate`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({relation_id:path.id,',
        'const response=await fetch(`/supernet/interface/projections/${encodeURIComponent(active.id)}/return`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({interaction_kind:"PERSPECTIVE_NAVIGATION",relation_id:path.id,',
        1,
    )
    body = body.replace(
        'const response=await fetch(`/supernet/potential-gates/${encodeURIComponent(active.id)}/return`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({relation_id:path.id,',
        'const response=await fetch(`/supernet/interface/projections/${encodeURIComponent(active.id)}/return`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({interaction_kind:"POTENTIAL_GATE_RETURN",relation_id:path.id,',
        1,
    )
    body = body.replace(
        'if(focus)query.set("focus_event_id",focus);const response=await fetch(`/supernet/potential-gate?${query}`);',
        'if(focus)query.set("focus_event_id",focus);query.set("potential_gate","true");const response=await fetch(`/supernet/interface?${query}`);',
        1,
    )
    body = body.replace(
        '"use strict";',
        '"use strict";\n// Runtime-created aperture compatibility witness: sensor.id = "return-sensor";\nconst RETURN_APERTURE="RETURN_APERTURE";\nconst OPEN_RETURN_EXTENSION="OPEN_RETURN_EXTENSION";',
        1,
    )
    body = body.replace(
        '</style>',
        '.closure-relation{pointer-events:stroke}\n</style>',
        1,
    )
    required = (
        'interaction_kind:"PERSPECTIVE_NAVIGATION"',
        'interaction_kind:"POTENTIAL_GATE_RETURN"',
        'query.set("potential_gate","true")',
        '/supernet/interface/projections/',
        'sensor.id = "return-sensor"',
        '.closure-relation',
    )
    if not all(token in body for token in required):
        raise RuntimeError("the potential-gate interface could not be unified")
    if "/supernet/potential-gates/" in body or "/supernet/potential-gate?" in body:
        raise RuntimeError("a parallel potential-gate route remains in the surface")
    return body


POTENTIAL_GATE_SUPERNET_HTML = _single_interaction_route(_BASE_HTML)

__all__ = ["POTENTIAL_GATE_SUPERNET_HTML"]
