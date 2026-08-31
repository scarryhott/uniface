from __future__ import annotations

"""Runtime certificate calculus induced by NRRF868.

The runtime does not add a proof-search layer on top of closure.  Returned
interactions produce exactly the certificates admitted by the internal
calculus:

* WITNESSED: a source-preserving translation witness;
* REFUTED: a source-preserving closed-loop witness pricing the relation
  differently;
* OPEN: neither certificate has been returned.

Derivation histories are transport/audit data only.  Their semantic normal
form is one translation certificate, matching ``derive_iff_oneStep``.
"""

import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

REFUTED_STATUS = "REFUTED"
PROTOCOL = "closure.supernet/interactive-derivation-calculus-nrrf868-v1"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def translation_certificate(
    *,
    observer_id: str,
    source_id: str,
    target_id: str,
    relation_id: str,
    source_return_ids: Sequence[str],
) -> dict[str, Any]:
    body = {
        "kind": "TRANSLATION_WITNESS",
        "observer_id": observer_id,
        "source_id": source_id,
        "target_id": target_id,
        "relation_id": relation_id,
        "source_return_ids": list(source_return_ids),
        "one_step_normal_form": True,
        "derivation_depth_semantic": False,
    }
    body["id"] = _digest("derive-translation", body)
    return body


def loop_refutation_certificate(
    *,
    observer_id: str,
    source_id: str,
    target_id: str,
    relation_id: str,
    source_return_ids: Sequence[str],
    loop_witness: Mapping[str, Any],
) -> dict[str, Any]:
    body = {
        "kind": "LOOP_REFUTATION",
        "observer_id": observer_id,
        "source_id": source_id,
        "target_id": target_id,
        "relation_id": relation_id,
        "source_return_ids": list(source_return_ids),
        "closed_itinerary": dict(loop_witness),
        "refutation_is_interactive": True,
    }
    body["id"] = _digest("derive-loop-refutation", body)
    return body


def classify_returned_relation(
    *,
    observer_id: str,
    source_id: str,
    target_id: str,
    relation_id: str,
    source_return_ids: Sequence[str],
    endpoints_source_preserved: bool,
    returned: bool,
    loop_refutation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the unique runtime status licensed by the internal calculus."""
    grounded = bool(observer_id and source_id and target_id and endpoints_source_preserved and source_return_ids)
    if grounded and returned and loop_refutation:
        certificate = loop_refutation_certificate(
            observer_id=observer_id,
            source_id=source_id,
            target_id=target_id,
            relation_id=relation_id,
            source_return_ids=source_return_ids,
            loop_witness=loop_refutation,
        )
        return {
            "status": REFUTED_STATUS,
            "translation_witness": None,
            "loop_refutation": certificate,
            "derivable": False,
            "closure_equal": False,
        }
    if grounded and returned:
        certificate = translation_certificate(
            observer_id=observer_id,
            source_id=source_id,
            target_id=target_id,
            relation_id=relation_id,
            source_return_ids=source_return_ids,
        )
        return {
            "status": WITNESSED_STATUS,
            "translation_witness": certificate,
            "loop_refutation": None,
            "derivable": True,
            "closure_equal": True,
        }
    return {
        "status": OPEN_STATUS,
        "translation_witness": None,
        "loop_refutation": None,
        "derivable": None,
        "closure_equal": None,
    }


def normalize_translation_history(certificates: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    """Collapse a composable witnessed history to one semantic certificate.

    This records the NRRF868 ``derive_iff_oneStep`` runtime consequence.  The
    composition path is retained only as provenance; it does not deepen truth.
    """
    witnessed = [dict(c) for c in certificates if c.get("kind") == "TRANSLATION_WITNESS"]
    if not witnessed:
        return None
    first, last = witnessed[0], witnessed[-1]
    source_ids: list[str] = []
    for item in witnessed:
        source_ids.extend(str(x) for x in item.get("source_return_ids", []) if str(x))
    body = {
        "kind": "TRANSLATION_WITNESS",
        "observer_id": first.get("observer_id"),
        "source_id": first.get("source_id"),
        "target_id": last.get("target_id"),
        "relation_id": _digest("normalized-relation", [c.get("relation_id") for c in witnessed]),
        "source_return_ids": list(dict.fromkeys(source_ids)),
        "one_step_normal_form": True,
        "normalized_from_steps": len(witnessed),
        "derivation_depth_semantic": False,
    }
    body["id"] = _digest("derive-normal-form", body)
    return body


__all__ = [
    "OPEN_STATUS",
    "WITNESSED_STATUS",
    "REFUTED_STATUS",
    "PROTOCOL",
    "classify_returned_relation",
    "translation_certificate",
    "loop_refutation_certificate",
    "normalize_translation_history",
]
