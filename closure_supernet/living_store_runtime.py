from __future__ import annotations

import uuid
from typing import Any

from .living_models import InteractionCreate
from .living_store import LivingNetworkStore, _json, utcnow
from .models import Verdict


class RuntimeLivingNetworkStore(LivingNetworkStore):
    """Runtime store specialization.

    Kept separate so the first persistent schema remains readable while the
    executable interaction insertion is tested independently. It can be folded
    back into ``LivingNetworkStore`` after the public interface stabilizes.
    """

    def create_interaction(
        self,
        data: InteractionCreate,
        occurrence_id: str,
        *,
        verdict: Verdict = Verdict.OPEN,
        reason: str = "A solution is constituted by this interaction; settlement remains provisional",
    ) -> dict[str, Any]:
        self.get_participant(data.author_id)
        self.get_problem(data.from_problem_id)
        target_problem_id = data.to_problem_id or data.from_problem_id
        self.get_problem(target_problem_id)
        if data.source_perspective_id:
            self.get_perspective(data.source_perspective_id)
        if data.target_perspective_id:
            self.get_perspective(data.target_perspective_id)
        interaction_id = str(uuid.uuid4())
        receipt_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_interactions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    interaction_id,
                    occurrence_id,
                    data.from_problem_id,
                    target_problem_id,
                    data.author_id,
                    str(data.kind),
                    data.source_perspective_id,
                    data.target_perspective_id,
                    _json(data.affected_perspectives),
                    _json(data.preserves),
                    _json(data.transforms),
                    _json(data.omits),
                    data.parent_interaction_id,
                    str(data.visibility),
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.execute(
                "INSERT INTO living_solution_receipts VALUES(?,?,?,?,?,?,?)",
                (
                    receipt_id,
                    interaction_id,
                    data.from_problem_id,
                    target_problem_id,
                    str(verdict),
                    reason,
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_interaction(interaction_id)
