from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from .models import EvidenceStatus, Verdict
from .natural_interface_models import NaturalChartKind, NaturalInterfaceAdmissionCreate
from .supernet_models import (
    IntegrationLens,
    IntegrationStage,
    IntegrationStateCreate,
    ResourceEnvelope,
)
from .topology_models import TopologyMode

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in values if str(item)))


class NaturalInterfaceManager:
    """Select the least sufficient Black Mirror chart from existing receipts.

    The selector does not infer a new truth relation or a canonical pixel layout.
    It chooses one chart *kind* uniquely under a declared precedence: use the
    most specific relation already proved by the focused event, expose every
    lower proof/source fibre, and hide every semantic layer whose prerequisite
    receipt is absent.
    """

    def __init__(self, runtime: "ClosureSupernetRuntime"):
        self.runtime = runtime

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_readings": [
                "NRRF790",
                "NRRF799",
                "NRRF805",
                "NRRF807",
                "NRRF811",
            ],
            "legacy_chart_is_admitted_closure_reading": False,
            "legacy_chart_is_transport_only": True,
            "semantic_interface_receipt": "visual_closure.interface_natural_form",
            "chart_kind_selected_from_existing_receipts": True,
            "natural_form_unique_under_declared_contract": True,
            "canonical_pixel_layout_selected": False,
            "source_fibre_reopenable": True,
            "interaction_lifts_to_supernet_event": True,
            "internal_external_gated_by_translational_truth": True,
            "geometry_does_not_replace_rule_or_proof": True,
            "proof_completion_balance_depth_available": True,
            "open_relations_render_as_open": True,
            "manual_rechart_available_at": "/supernet/classic",
            "determination_issues_truth": False,
        }

    def _events(self) -> list[dict[str, Any]]:
        return self.runtime.supernet_store.events_after(0, 20_000)

    def _focus_event(
        self,
        events: list[dict[str, Any]],
        focus_event_id: str | None,
        perspective_id: str | None,
    ) -> dict[str, Any] | None:
        if focus_event_id is not None:
            return self.runtime.supernet_store.get_event(focus_event_id)
        eligible = [
            event
            for event in events
            if str(event.get("adapter_label") or "") != "natural_interface"
        ]
        if perspective_id:
            relative = [
                event
                for event in eligible
                if event.get("authored_by") == perspective_id
                or perspective_id in event.get("affected_perspectives", [])
                or event.get("perspective_id") == perspective_id
            ]
            if relative:
                eligible = relative
        return max(eligible or events, key=lambda item: int(item["seq"])) if events else None

    def _source_fibre(self, event: dict[str, Any] | None) -> list[dict[str, Any]]:
        if event is None:
            return []
        result: list[dict[str, Any]] = []
        for occurrence_id in event.get("exact_source_ids", []):
            try:
                occurrence = self.runtime.store.get_occurrence(occurrence_id)
            except KeyError:
                result.append(
                    {
                        "id": occurrence_id,
                        "exact_text": None,
                        "source_available": False,
                    }
                )
                continue
            result.append(
                {
                    "id": occurrence["id"],
                    "source_id": occurrence["source_id"],
                    "exact_text": occurrence["exact_text"],
                    "exact_symbols": occurrence["exact_symbols"],
                    "operator_path": occurrence["operator_path"],
                    "source_location": occurrence.get("source_location"),
                    "source_context": occurrence.get("source_context"),
                    "evidence_status": occurrence.get("evidence_status"),
                    "source_available": True,
                }
            )
        return result

    def _proof_context(self, event: dict[str, Any] | None) -> dict[str, Any] | None:
        if event is None or not hasattr(self.runtime, "proof_completion_store"):
            return None
        metadata = event.get("metadata", {})
        system_id = metadata.get("proof_system_id")
        if system_id:
            try:
                system = self.runtime.proof_completion_store.get_system(system_id)
                receipts = self.runtime.proof_completion_store.list_receipts(
                    20_000, system_id=system_id
                )
                return {"system": system, "receipts": receipts}
            except KeyError:
                pass
        for system in self.runtime.proof_completion_store.list_systems(20_000):
            if event["id"] in {
                system.get("integration_event_id"),
                system.get("source_event_id"),
            }:
                return {
                    "system": system,
                    "receipts": self.runtime.proof_completion_store.list_receipts(
                        20_000, system_id=system["id"]
                    ),
                }
        for receipt in self.runtime.proof_completion_store.list_receipts(20_000):
            if receipt.get("integration_event_id") == event["id"]:
                try:
                    system = self.runtime.proof_completion_store.get_system(
                        receipt["system_id"]
                    )
                except KeyError:
                    return None
                return {
                    "system": system,
                    "receipts": self.runtime.proof_completion_store.list_receipts(
                        20_000, system_id=system["id"]
                    ),
                }
        return None

    def _continuation_context(
        self, event: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        if event is None or not hasattr(self.runtime, "continuation_store"):
            return None
        metadata = event.get("metadata", {})
        system_id = metadata.get("continuation_system_id")
        if system_id:
            try:
                return self.runtime.continuation_store.get_system(system_id)
            except KeyError:
                pass
        for system in self.runtime.continuation_store.list_systems(20_000):
            if event["id"] in {
                system.get("integration_event_id"),
                system.get("source_event_id"),
            }:
                return system
        return None

    def _life_context(self, event: dict[str, Any] | None) -> dict[str, Any] | None:
        if event is None or not hasattr(self.runtime, "turing_being_store"):
            return None
        metadata = event.get("metadata", {})
        life_id = metadata.get("life_event_id") or metadata.get(
            "turing_being_life_event_id"
        )
        if life_id:
            try:
                return self.runtime.turing_being_store.get_life_event(life_id)
            except KeyError:
                pass
        for life in self.runtime.turing_being_store.list_life_events(20_000):
            if event["id"] in {
                life.get("integration_event_id"),
                life.get("reaction_event_id"),
            }:
                return life
        return None

    @staticmethod
    def _determination(event: dict[str, Any] | None) -> dict[str, Any] | None:
        if event is None:
            return None
        for state in reversed(event.get("state_history", [])):
            if state.get("stage") == "DETERMINED":
                return state
        return None

    @staticmethod
    def _adapter(event: dict[str, Any] | None) -> str:
        if event is None:
            return ""
        return str(event.get("adapter_label") or "").lower().replace("-", "_")

    def _select_chart(
        self,
        event: dict[str, Any] | None,
        *,
        proof: dict[str, Any] | None,
        continuation: dict[str, Any] | None,
        life: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if event is None:
            return {
                "kind": NaturalChartKind.EMPTY_FIELD.value,
                "topology_mode": TopologyMode.FIELD.value,
                "lens": IntegrationLens.ALL.value,
                "title": "Open field",
                "axiometric_reading": "No point has entered; the interface remains an open admission surface.",
                "required_layers": ["integrate"],
                "hidden_until_receipt": [],
                "available_actions": ["integrate"],
                "selection_reason": "No event exists, so no stronger geometry is admissible.",
                "alternative_admissible_charts": [],
            }

        adapter = self._adapter(event)
        metadata = event.get("metadata", {})
        stage = str(event.get("current_stage"))
        determined = self._determination(event)
        selected_kind = metadata.get("natural_chart_kind") if adapter == "natural_interface" else None
        alternatives: list[str] = []

        if selected_kind in {item.value for item in NaturalChartKind}:
            kind = NaturalChartKind(selected_kind)
            reason = "This event preserves a previously admitted natural-interface selection."
        elif adapter == "turing_being" or life is not None and adapter not in {"proof", "continuation"}:
            kind = NaturalChartKind.TURING_BEING
            reason = "The focused relation is an executor–reactor life occurrence, so 0↔∞ precedes downstream hand, rule, or proof charts."
        elif adapter == "proof" or proof is not None and adapter != "continuation":
            kind = NaturalChartKind.PROOF_BALANCE
            reason = "Finite derivation data exists, so the interface must expose proof → admission → balance → meta abstraction."
        elif adapter == "continuation" or continuation is not None:
            kind = NaturalChartKind.RULE_GEOMETRY
            reason = "A natural continuation exists; directed rule lineage and generated geometry must remain simultaneously visible."
        elif adapter == "selector" or determined and determined.get("rigidity_receipt", {}).get("site_admissibility"):
            kind = NaturalChartKind.OPEN_SELECTOR
            reason = "The focused event carries an admissibility relation, so branching or rigidity is the current natural form."
        elif adapter == "embodied" or len(event.get("affected_perspectives", [])) > 1 or "collective" in event.get("form_label", "").lower():
            kind = NaturalChartKind.SHARED_ARCHITECTURE
            reason = "Several participant trajectories are explicitly related, so their least shared field is the sufficient chart."
        elif stage in {"RETURNED", "REOPENED"}:
            kind = NaturalChartKind.RETURN_BALL_HAIR
            reason = "A bounded return exists while successor potential remains OPEN, forcing a ball–hair return chart."
        elif event.get("parent_event_ids") or event.get("causal_predecessor_ids"):
            kind = NaturalChartKind.RULE_GEOMETRY
            reason = "Directed lineage exists, so a point-only chart would hide an admitted translation path."
        else:
            kind = NaturalChartKind.SOURCE_POINT
            reason = "One exact occurrence is present without a stronger relation receipt, so one source point is sufficient."

        if proof is not None and kind != NaturalChartKind.PROOF_BALANCE:
            alternatives.append(NaturalChartKind.PROOF_BALANCE.value)
        if continuation is not None and kind != NaturalChartKind.RULE_GEOMETRY:
            alternatives.append(NaturalChartKind.RULE_GEOMETRY.value)
        if life is not None and kind != NaturalChartKind.TURING_BEING:
            alternatives.append(NaturalChartKind.TURING_BEING.value)

        mapping: dict[NaturalChartKind, tuple[TopologyMode, IntegrationLens, str, list[str]]] = {
            NaturalChartKind.EMPTY_FIELD: (TopologyMode.FIELD, IntegrationLens.ALL, "Open field", ["integrate"]),
            NaturalChartKind.SOURCE_POINT: (TopologyMode.POINT_LINE_LOOP, IntegrationLens.ALL, "Exact source point", ["source", "interaction"]),
            NaturalChartKind.OPEN_SELECTOR: (TopologyMode.SELECTOR, IntegrationLens.SELECTOR, "Open natural-form selector", ["admissibility", "open alternatives", "rigidity"]),
            NaturalChartKind.TURING_BEING: (TopologyMode.ZERO_INFINITY, IntegrationLens.TURING_BEING, "Turing Being 0↔∞", ["global hair 0", "local ball ∞", "returned hair 0+", "translational truth"]),
            NaturalChartKind.RULE_GEOMETRY: (TopologyMode.POINT_LINE_LOOP, IntegrationLens.CONTINUATION, "Rule / geometry continuation", ["directed rule", "geometry fold", "meeting witness"]),
            NaturalChartKind.PROOF_BALANCE: (TopologyMode.TRUTH_DIAGONAL, IntegrationLens.PROOF, "Proof / completion / balance", ["Deriv", "Admits", "Balance", "MetaAbs"]),
            NaturalChartKind.RETURN_BALL_HAIR: (TopologyMode.BALL_HAIR, IntegrationLens.ALL, "Return ball / open hair", ["bounded return", "successor potential", "reopening"]),
            NaturalChartKind.SHARED_ARCHITECTURE: (TopologyMode.SHARED_ARCHITECTURE, IntegrationLens.EMBODIED, "Shared architecture", ["participant trajectories", "collective relation", "least shared field"]),
        }
        mode, lens, title, layers = mapping[kind]
        semantic_complete = bool(
            life
            and life.get("translational_truth_receipt", {}).get("complete") is True
        )
        hidden: list[str] = []
        if kind == NaturalChartKind.TURING_BEING and not semantic_complete:
            hidden.extend(["internal", "external", "semantic hand", "actual/potential"])
        if proof is None:
            hidden.append("proof fibre")
        actions = ["integrate", "interact", "relate"]
        if kind == NaturalChartKind.OPEN_SELECTOR:
            actions.append("rigidify")
        if kind == NaturalChartKind.TURING_BEING and not semantic_complete:
            actions.append("return-reaction")
        if stage not in {"RETURNED", "REOPENED"}:
            actions.append("return")
        actions.append("reopen")
        return {
            "kind": kind.value,
            "topology_mode": mode.value,
            "lens": lens.value,
            "title": title,
            "axiometric_reading": reason,
            "required_layers": layers,
            "hidden_until_receipt": _unique(hidden),
            "available_actions": _unique(actions),
            "selection_reason": reason,
            "alternative_admissible_charts": _unique(alternatives),
            "minimal_sufficient": True,
            "natural_form_unique_under_declared_contract": True,
            "canonical_pixel_layout_selected": False,
        }

    def select(
        self,
        *,
        focus_event_id: str | None = None,
        perspective_id: str | None = None,
    ) -> dict[str, Any]:
        events = self._events()
        event = self._focus_event(events, focus_event_id, perspective_id)
        proof = self._proof_context(event)
        continuation = self._continuation_context(event)
        life = self._life_context(event)
        chart = self._select_chart(
            event,
            proof=proof,
            continuation=continuation,
            life=life,
        )
        mode = TopologyMode(chart["topology_mode"])
        lens = IntegrationLens(chart["lens"])
        try:
            topology = self.runtime.topology.projection(
                mode=mode,
                lens=lens,
                focus_event_id=event["id"] if event else None,
            )
            if event and event["id"] not in topology.get("event_ids", []):
                raise ValueError("natural lens filtered its own focus")
        except (KeyError, ValueError):
            topology = self.runtime.topology.projection(
                mode=mode,
                lens=IntegrationLens.ALL,
                focus_event_id=event["id"] if event else None,
            )
            chart["lens_fallback"] = IntegrationLens.ALL.value

        determination = self._determination(event)
        proof_summary = None
        if proof is not None:
            evaluation = proof["system"]["evaluation"]
            proof_summary = {
                "system_id": proof["system"]["id"],
                "completion_eq_proof": evaluation.get("completion_eq_proof"),
                "balance_classes": evaluation.get("balance_classes", []),
                "geometry_classes": evaluation.get("geometry_classes", []),
                "known_derivations": evaluation.get("known_shortest_derivations", 0),
                "receipts": proof["receipts"],
                "canonical_derivation": None,
                "proof_fibre_reopenable": True,
            }
        continuation_summary = None
        if continuation is not None:
            continuation_summary = {
                "system_id": continuation["id"],
                "origin": continuation["origin"],
                "continuation_prefix": continuation["evaluation"].get(
                    "continuation_prefix", []
                ),
                "rule_eq_geometry": continuation["evaluation"].get(
                    "rule_eq_geometry"
                ),
                "geometry_only_pairs": continuation["evaluation"].get(
                    "geometry_only_pairs", []
                ),
                "proof_system_id": continuation.get("metadata", {}).get(
                    "proof_system_id"
                ),
            }
        life_summary = None
        if life is not None:
            life_summary = {
                "life_event_id": life["id"],
                "global_hair_zero": life["global_hair_zero"],
                "local_ball_infinity": life["local_ball_infinity"],
                "translational_truth_receipt": life[
                    "translational_truth_receipt"
                ],
                "derived_relations": life.get("derived_relations"),
                "reopening_potential": life.get("reopening_potential"),
            }
        return {
            "generated_at": topology.get("generated_at"),
            "focus_event": event,
            "source_fibre": self._source_fibre(event),
            "natural_chart": chart,
            "topology": topology,
            "proof_depth": proof_summary,
            "continuation_depth": continuation_summary,
            "turing_being_depth": life_summary,
            "determination_depth": determination,
            "admission_receipt": {
                "ui_admitted": False,
                "legacy_chart_transport_only": True,
                "semantic_interface_receipt": (
                    "visual_closure.interface_natural_form"
                ),
                "source_preserved": True,
                "source_fibre_reopenable": True,
                "interaction_lifts_to_supernet_event": True,
                "semantic_prerequisites_respected": True,
                "minimal_sufficient_chart": True,
                "natural_chart_selected": True,
                "canonical_pixel_layout_selected": False,
                "truth_issued": False,
            },
            "selection_contract": [
                "preserve every exact source",
                "never display a semantic layer before its receipt",
                "show the strongest specific relation of the focused event",
                "retain every lower proof and source fibre",
                "choose no extra chart layer without a relation witness",
                "lift every interface action to the canonical Supernet integrator",
            ],
            "canonical_runtime_operation": "integrate",
            "truth_issued": False,
        }

    async def admit(
        self, data: NaturalInterfaceAdmissionCreate
    ) -> dict[str, Any]:
        receipt = self.select(
            focus_event_id=data.focus_event_id,
            perspective_id=data.perspective_id,
        )
        focus = receipt["focus_event"]
        parent_ids = [focus["id"]] if focus else []
        chart = receipt["natural_chart"]
        integrated = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=_stable(
                    {
                        "natural_supernet_interface": chart,
                        "focus_event_id": focus["id"] if focus else None,
                        "admission_receipt": receipt["admission_receipt"],
                        "reason": data.reason,
                    }
                ),
                authored_by=data.authored_by,
                form_label="legacy interface presentation return",
                language_label="Black Mirror closure reading",
                source_id="natural-supernet-interface",
                perspective_id=data.perspective_id,
                capabilities=[
                    "render the least sufficient closure chart",
                    "reopen every visible class to its source and proof fibre",
                    "return every interface action through the canonical integrator",
                ],
                constraints=[
                    "no semantic layer before its receipt",
                    "no canonical pixel layout",
                    "no truth verdict from chart selection",
                ],
                relation_hints=[
                    "natural interface",
                    "Black Mirror",
                    chart["kind"],
                    chart["topology_mode"],
                ],
                causal_predecessor_ids=parent_ids,
                parent_event_ids=parent_ids,
                affected_perspectives=_unique(
                    [data.perspective_id] if data.perspective_id else []
                ),
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="natural_interface",
                metadata={
                    **data.metadata,
                    "natural_chart_kind": chart["kind"],
                    "natural_topology_mode": chart["topology_mode"],
                    "natural_lens": chart["lens"],
                    "focus_event_id": focus["id"] if focus else None,
                    "ui_admitted": False,
                    "legacy_chart_transport_only": True,
                    "canonical_pixel_layout_selected": False,
                    "truth_issued": False,
                },
            )
        )
        event_id = integrated["event_id"]
        self.runtime.supernet_integrator.determine(
            event_id,
            actor_id=data.authored_by,
            rigidity_scope=[
                "source preservation",
                "semantic prerequisite gating",
                "least sufficient chart selection",
                "interaction return",
                "fibre reopening",
            ],
            rigidity_receipt={
                **receipt["admission_receipt"],
                "selection_contract": receipt["selection_contract"],
                "natural_form_unique_under_declared_contract": True,
            },
            determined_form={
                "natural_chart": chart,
                "focus_event_id": focus["id"] if focus else None,
                "canonical_pixel_layout": None,
            },
            unitary_path_partition={
                "path": [
                    "living field",
                    "receipt audit",
                    "minimal natural chart",
                    "local interaction",
                    "canonical Supernet return",
                ],
                "chart_kind": chart["kind"],
                "topology_mode": chart["topology_mode"],
                "proof_fibre_reopenable": True,
            },
            reason="The current closure receipts leave exactly one minimal sufficient chart kind",
        )
        self.runtime.supernet_integrator.transition(
            event_id,
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The admitted interface returns as the next local Black Mirror appearance",
                actor_id=data.authored_by,
                returned_resource_ids=[event_id],
                successor_potential=[
                    {
                        "kind": "natural-interface-rechart",
                        "focus_event_id": focus["id"] if focus else None,
                        "chart_kind": chart["kind"],
                        "reselect_after_next_event": True,
                    }
                ],
                metadata={
                    "natural_interface": True,
                    "canonical_pixel_layout_selected": False,
                    "truth_issued": False,
                },
            ),
        )
        return {
            "event": self.runtime.supernet_store.get_event(event_id),
            "interface_receipt": receipt,
            "truth_issued": False,
        }
