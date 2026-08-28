from __future__ import annotations

from typing import Any

from .proof_completion import ProofCompletionManager
from .proof_completion_store import ProofCompletionStore
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_proof_completion_runtime() -> None:
    """Attach NRRF811 after continuation without replacing any prior field."""

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_infer_adapter = SupernetIntegrator._infer_adapter
    original_capabilities = SupernetIntegrator.capabilities

    def infer_adapter(form_label: str, metadata: dict[str, Any]) -> str:
        explicit = str(metadata.get("adapter_label") or "").lower()
        text = " ".join(
            [
                explicit,
                str(form_label),
                str(metadata.get("source_kind", "")),
                str(metadata.get("kind", "")),
                str(metadata.get("formal_reading", "")),
                " ".join(str(item) for item in metadata.get("formal_readings", [])),
            ]
        ).lower()
        if (
            explicit == "proof"
            or "nrrf811" in text
            or "proof completion" in text
            or "meta abstraction" in text
            or "deriv" in text
            or "relative balance" in text
        ):
            return "proof"
        return original_infer_adapter(form_label, metadata)

    def capabilities(self: SupernetIntegrator) -> dict[str, Any]:
        base = original_capabilities(self)
        base.update(
            {
                "proof_completion_available": True,
                "proof_is_finite_derivation_data": True,
                "completion_is_nonempty_proof": True,
                "completion_eq_proof": True,
                "meta_abstraction_forgets_path_not_conclusion": True,
                "truth_admission_is_closure_operator": True,
                "relative_balance_is_mutual_admission": True,
                "completion_object_is_balance_quotient": True,
                "proof_completion_links_continuation": True,
                "proof_completion_links_turing_being": True,
                "balance_le_geometry": True,
                "balance_equals_geometry_only_when_return_closes": True,
                "black_mirror_reopens_completion_to_proof_fibre": True,
                "geometry_does_not_replace_proof": True,
                "canonical_derivation_selected": False,
                "determination_issues_truth": False,
            }
        )
        return base

    SupernetIntegrator._infer_adapter = staticmethod(infer_adapter)
    SupernetIntegrator.capabilities = capabilities

    original_init = ClosureSupernetRuntime.__init__
    original_cycle = ClosureSupernetRuntime.cycle
    original_status = ClosureSupernetRuntime.status
    original_black_mirror = ClosureSupernetRuntime.black_mirror
    original_living_field = ClosureSupernetRuntime.living_field
    original_close = ClosureSupernetRuntime.close

    def init(self: ClosureSupernetRuntime, config=None) -> None:
        original_init(self, config)
        self.proof_completion_store = ProofCompletionStore(self.config.database_path)
        self.proof_completion = ProofCompletionManager(
            self, self.proof_completion_store
        )
        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            proof = self.proof_completion.projection()
            projection["proof_completion_meta_abstraction"] = {
                "stats": proof["stats"],
                "source_reverse_index": proof["source_reverse_index"],
                "formal_readings": proof["formal_readings"],
                "completion_is_proof_truncation": True,
                "proof_fibres_remain_reopenable": True,
                "balance_is_mutual_admission": True,
                "geometry_does_not_replace_proof": True,
                "canonical_derivation_selected": False,
                "truth_issued": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.proof_completion.projection()
        stats = projection["stats"]
        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["proof_completion_meta_abstraction"] = projection
        living.setdefault("stats", {}).update(
            {
                "proof_systems": stats["systems"],
                "proof_receipts": stats["receipts"],
                "derivation_receipts": stats["derivations"],
                "admission_receipts": stats["admissions"],
                "balance_receipts": stats["balances"],
                "completion_eq_proof_systems": stats[
                    "completion_eq_proof_systems"
                ],
                "proof_linked_continuations": stats["linked_continuations"],
                "proof_linked_turing_beings": stats["linked_turing_beings"],
                "geometry_does_not_replace_proof": True,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            projection["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        payload = result.model_dump(mode="json")
        payload["proof_completion"] = stats
        self.store.set_state("last_cycle", payload)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["proof_completion"] = self.proof_completion_store.stats()
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def proof_completion_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.proof_completion_store.get_state(
            "proof_completion_field_projection"
        )
        return (
            self.proof_completion.projection()
            if projection is None
            else projection
        )

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "proof_completion_meta_abstraction" not in projection:
            proof = self.proof_completion_field()
            projection["proof_completion_meta_abstraction"] = {
                "stats": proof["stats"],
                "source_reverse_index": proof["source_reverse_index"],
                "completion_is_proof_truncation": True,
                "proof_fibres_remain_reopenable": True,
                "geometry_does_not_replace_proof": True,
                "truth_issued": False,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "proof_completion_meta_abstraction" not in projection:
            proof = self.proof_completion_field()
            projection["proof_completion_meta_abstraction"] = proof
            projection.setdefault("source_reverse_index", {}).update(
                proof["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "proof_completion_store"):
            self.proof_completion_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.proof_completion_field = proof_completion_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_proof_completion_runtime()
