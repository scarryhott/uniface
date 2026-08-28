from __future__ import annotations

import json
from typing import Any

from .continuation import ContinuationManager
from .continuation_store import ContinuationStore
from .models import Verdict
from .proof_completion import ProofCompletionManager
from .proof_completion_store import ProofCompletionStore
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator
from .supernet_models import IntegrationStage, IntegrationStateCreate


_PATCHED = False


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def install_proof_completion_runtime() -> None:
    """Attach NRRF811 after continuation without replacing any prior field."""

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    # Existing continuation rows keep their schema. The proof link is persisted
    # inside the already-versioned evaluation/metadata fields and exposed as a
    # first-class decoded field.
    original_decode_system = ContinuationStore._decode_system

    def decode_continuation_system(row: Any) -> dict[str, Any]:
        data = original_decode_system(row)
        data["proof_system_id"] = (
            dict(data.get("metadata") or {}).get("proof_system_id")
            or dict(data.get("evaluation") or {}).get("proof_system_id")
        )
        return data

    def link_proof_system(
        self: ContinuationStore,
        system_id: str,
        proof_system_id: str,
        evaluation: dict[str, Any],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        with self._lock:
            self._conn.execute(
                "UPDATE natural_continuation_systems SET evaluation=?,metadata=? WHERE id=?",
                (_json(evaluation), _json(metadata), system_id),
            )
            self._conn.commit()
        return self.get_system(system_id)

    ContinuationStore._decode_system = staticmethod(decode_continuation_system)
    ContinuationStore.link_proof_system = link_proof_system

    original_continuation_create = ContinuationManager.create_system
    original_continuation_capabilities = ContinuationManager.capabilities
    original_continuation_projection = ContinuationManager.projection

    async def create_continuation_with_proof(
        self: ContinuationManager, data: Any
    ) -> dict[str, Any]:
        continuation = await original_continuation_create(self, data)
        proof = await self.runtime.proof_completion.create_from_continuation(
            continuation
        )
        evaluation = dict(continuation["evaluation"])
        proof_evaluation = dict(proof["evaluation"])
        evaluation.update(
            {
                "proof_system_id": proof["id"],
                "rule_is_admits": True,
                "rule_witness_is_derivation_data": True,
                "completion_eq_proof": proof_evaluation[
                    "completion_eq_proof"
                ],
                "balance_relation": proof_evaluation["balance_relation"],
                "balance_class_of": proof_evaluation["balance_class_of"],
                "balance_le_geometry": proof_evaluation[
                    "balance_le_geometry"
                ],
                "balance_eq_geometry": proof_evaluation[
                    "balance_eq_geometry"
                ],
                "balance_equals_geometry_only_when_return_closes": True,
                "geometry_does_not_replace_proof": True,
                "proof_fibre_reopenable": True,
            }
        )
        metadata = {
            **continuation["metadata"],
            "proof_system_id": proof["id"],
            "formal_readings": [
                "NRRF799",
                "NRRF802",
                "NRRF805",
                "NRRF807",
                "NRRF811",
            ],
            "completion_is_proof_truncation": True,
            "canonical_derivation_selected": False,
            "truth_issued": False,
        }
        updated = self.store.link_proof_system(
            continuation["id"], proof["id"], evaluation, metadata
        )
        self.runtime.supernet_integrator.transition(
            continuation["integration_event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason=(
                    "The continuation returns with its NRRF811 proof fibre, "
                    "proposition-level admission and reciprocal balance exposed"
                ),
                actor_id=continuation["authored_by"],
                returned_resource_ids=[
                    continuation["id"],
                    continuation["completion_system_id"],
                    proof["id"],
                ],
                successor_potential=[
                    {
                        "kind": "proof-bearing-natural-continuation",
                        "continuation_system_id": continuation["id"],
                        "proof_system_id": proof["id"],
                        "next_index": continuation["continuation_horizon"] + 1,
                        "canonical_derivation": None,
                    }
                ],
                metadata={
                    "nrrf807": True,
                    "nrrf811": True,
                    "completion_is_proof_truncation": True,
                    "geometry_does_not_replace_proof": True,
                    "truth_issued": False,
                },
            ),
        )
        self.projection()
        return updated

    def continuation_capabilities(self: ContinuationManager) -> dict[str, Any]:
        base = original_continuation_capabilities(self)
        base.update(
            {
                "formal_readings": [
                    "NRRF799",
                    "NRRF802",
                    "NRRF805",
                    "NRRF807",
                    "NRRF811",
                ],
                "every_continuation_has_proof_completion": True,
                "rule_is_admits": True,
                "completion_eq_proof": True,
                "balance_is_mutual_rule": True,
                "balance_le_geometry": True,
                "geometry_does_not_replace_proof": True,
                "proof_fibre_reopenable": True,
            }
        )
        return base

    def continuation_projection(self: ContinuationManager) -> dict[str, Any]:
        projection = original_continuation_projection(self)
        projection["formal_readings"] = [
            "NRRF799",
            "NRRF802",
            "NRRF805",
            "NRRF807",
            "NRRF811",
        ]
        projection["proof_completion_linked"] = True
        projection["stats"]["linked_proof_systems"] = sum(
            int(item.get("proof_system_id") is not None)
            for item in projection["systems"]
        )
        projection["geometry_does_not_replace_proof"] = True
        return projection

    ContinuationManager.create_system = create_continuation_with_proof
    ContinuationManager.capabilities = continuation_capabilities
    ContinuationManager.projection = continuation_projection

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
