from __future__ import annotations

import uuid
from typing import Any

from .reopening_models import ReopeningFamilyCreate
from .reopening_store import ReopeningStore, _json, utcnow


def create_family(
    self: ReopeningStore,
    data: ReopeningFamilyCreate,
    *,
    variants: list[dict[str, Any]],
    remaining_star_ids: list[str],
    closure_verified: bool,
) -> dict[str, Any]:
    """Insert one family and its eight-column variant rows atomically."""
    family_id = str(uuid.uuid4())
    created_at = utcnow()
    with self._lock:
        self._conn.execute(
            "INSERT INTO reopening_families VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                family_id,
                data.problem_id,
                data.name,
                data.created_by,
                _json(data.assumption_occurrence_ids),
                str(data.mode),
                _json([rule.model_dump(mode="json") for rule in data.closure_rules]),
                _json(remaining_star_ids),
                int(closure_verified),
                _json(data.metadata),
                created_at,
            ),
        )
        for index, variant in enumerate(variants):
            self._conn.execute(
                "INSERT INTO reopening_variants VALUES(?,?,?,?,?,?,?,?)",
                (
                    str(uuid.uuid4()),
                    family_id,
                    variant["label"],
                    _json(variant["held_occurrence_ids"]),
                    _json(variant["closure_occurrence_ids"]),
                    index,
                    _json(variant.get("metadata") or {}),
                    created_at,
                ),
            )
        self._conn.commit()
    return self.get_family(family_id)


# The repository already uses this explicit specialization pattern for the
# living-store interaction insertion. Keep the source store readable while the
# public runtime schema is being stabilized.
ReopeningStore.create_family = create_family
