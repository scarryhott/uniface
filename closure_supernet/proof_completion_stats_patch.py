from __future__ import annotations

from typing import Any

from .proof_completion_store import ProofCompletionStore


if not getattr(ProofCompletionStore, "_nrrf811_stats_patched", False):
    _original_stats = ProofCompletionStore.stats

    def stats(self: ProofCompletionStore) -> dict[str, Any]:
        base = _original_stats(self)
        systems = self.list_systems()
        base["completion_eq_proof_systems"] = sum(
            int(item["evaluation"].get("completion_eq_proof") is True)
            for item in systems
        )
        base["proof_fibres_reopenable"] = sum(
            int(item["evaluation"].get("proof_fibres_reopenable") is True)
            for item in systems
        )
        base["linked_turing_beings"] = base.get("linked_turing_being", 0)
        return base

    ProofCompletionStore.stats = stats
    ProofCompletionStore._nrrf811_stats_patched = True
