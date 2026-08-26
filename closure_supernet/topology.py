from __future__ import annotations

import hashlib
import math
from collections import defaultdict, deque
from datetime import UTC, datetime
from typing import Any

from .models import Verdict
from .supernet_models import IntegrationLens, IntegrationStage, IntegrationStateCreate, ResourceEnvelope
from .topology_models import (
    CollectiveTraceCreate,
    EventRelationCreate,
    EventReopenCreate,
    EventReturnCreate,
    RigidificationCreate,
    TopologyMode,
)


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _hash_fraction(value: str) -> float:
    raw = hashlib.sha256(value.encode("utf-8")).digest()
    return int.from_bytes(raw[:8], "big") / float(2**64 - 1)


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in values if str(item)))


class _UnionFind:
    def __init__(self, items: list[str]):
        self.parent = {item: item for item in items}
        self.rank = {item: 0 for item in items}

    def find(self, item: str) -> str:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: str, right: str) -> bool:
        a, b = self.find(left), self.find(right)
        if a == b:
            return False
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1
        return True


class SupernetTopologyService:
    """Interactive topology and selector operations over the one Supernet field.

    The service never creates another semantic runtime. It reads and transforms
    ``SupernetIntegrationEvent`` objects through the canonical integrator, then
    produces geometry as a reversible projection lens.
    """

    def __init__(self, runtime: Any):
        self.runtime = runtime

    def capabilities(self) -> dict[str, Any]:
        return {
            "single_continuous_surface": True,
            "canonical_runtime_operation": "integrate",
            "modes": [item.value for item in TopologyMode],
            "direct_manipulation": [
                "integrate",
                "relate",
                "interact",
                "rigidify",
                "determine",
                "return",
                "reopen",
                "collective-trace",
                "focus",
                "zoom",
            ],
            "point_line_loop_return": True,
            "perspective_zoom": True,
            "truth_diagonal": True,
            "metavector_metrics": ["degree", "closeness", "betweenness"],
            "ball_hair": True,
            "zero_infinity_reciprocal_poles": True,
            "light_cone_causality": True,
            "ellipse_mirror": True,
            "shared_architecture": True,
            "anatomy_tree": True,
            "selector_relation_first": True,
            "determination_requires_rigidity": True,
            "determination_issues_truth": False,
            "hardware_simulation_only": True,
        }

    async def create_relation(self, data: EventRelationCreate) -> dict[str, Any]:
        source = self.runtime.supernet_store.get_event(data.source_event_id)
        target = self.runtime.supernet_store.get_event(data.target_event_id)
        exact_text = data.exact_text or (
            f"{source['form_label']} → {target['form_label']}: {data.relation_label}"
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="translation",
                language_label=data.language_label,
                relation_hints=[data.relation_label],
                causal_predecessor_ids=[data.source_event_id],
                parent_event_ids=[data.source_event_id, data.target_event_id],
                affected_perspectives=data.affected_perspectives,
                adapter_label="translation",
                metadata={
                    **data.metadata,
                    "relation_endpoints": [
                        data.source_event_id,
                        data.target_event_id,
                    ],
                    "direction": "bidirectional" if data.bidirectional else "directed",
                    "unitary": data.unitary,
                    "preserves": data.preserves,
                    "transforms": data.transforms,
                    "omitted": data.omitted,
                    "source_event_id": data.source_event_id,
                    "target_event_id": data.target_event_id,
                    "truth_issued": False,
                },
            )
        )
        return {
            "receipt": receipt,
            "relation_event": self.runtime.supernet_store.get_event(receipt["event_id"]),
        }

    async def create_collective_trace(self, data: CollectiveTraceCreate) -> dict[str, Any]:
        for event_id in data.event_ids:
            self.runtime.supernet_store.get_event(event_id)
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=data.exact_text,
                authored_by=data.authored_by,
                form_label=data.form_label,
                language_label=data.language_label,
                relation_hints=_unique([
                    *data.relation_hints,
                    "collective interaction field",
                    "shared architecture trajectory",
                ]),
                causal_predecessor_ids=list(data.event_ids),
                parent_event_ids=list(data.event_ids),
                affected_perspectives=data.affected_perspectives,
                adapter_label="action",
                metadata={
                    **data.metadata,
                    "collective_trace_event_ids": data.event_ids,
                    "quantity_quality_ranking": False,
                    "collective_field": True,
                },
            )
        )
        return {
            "receipt": receipt,
            "collective_event": self.runtime.supernet_store.get_event(receipt["event_id"]),
        }

    def rigidify(self, event_id: str, data: RigidificationCreate) -> dict[str, Any]:
        event = self.runtime.supernet_store.get_event(event_id)
        partial = {str(key): value for key, value in data.partial_input.items()}
        open_sites: list[str] = []
        determined_form: dict[str, str] = {}
        compatibility: dict[str, bool] = {}
        for site, symbols in data.site_admissibility.items():
            fixed = partial.get(site)
            compatible = fixed is None or fixed in symbols
            compatibility[site] = compatible
            if not compatible:
                raise ValueError(
                    f"Partial input at {site} is not admitted by the relation"
                )
            if len(symbols) == 1:
                determined_form[site] = symbols[0]
            else:
                open_sites.append(site)
        receipt = {
            "site_admissibility": data.site_admissibility,
            "partial_input": partial,
            "compatible": compatibility,
            "rigid": not open_sites,
            "open_sites": open_sites,
            "pointwise_relation": True,
            "selector_depends_on_relation": True,
            "selector_is_location_only": False,
            "truth_issued": False,
            "source_event_id": event_id,
        }
        if open_sites:
            result = self.runtime.supernet_integrator.transition(
                event_id,
                IntegrationStateCreate(
                    stage=IntegrationStage.RELATION_SENSED,
                    verdict=Verdict.OPEN,
                    reason=data.reason,
                    actor_id=data.actor_id,
                    rigidity_scope=list(data.site_admissibility),
                    rigidity_receipt=receipt,
                    metadata={
                        **data.metadata,
                        "interactive_rigidification": True,
                        "rigid": False,
                        "open_sites": open_sites,
                        "truth_issued": False,
                    },
                ),
            )
            return {
                **result,
                "rigid": False,
                "open_sites": open_sites,
                "determined_form": None,
                "truth_issued": False,
            }
        path_partition = self._unitary_path_partition(
            determined_form, data.unitary_step
        )
        receipt.update(
            {
                "rigid": True,
                "open_sites": [],
                "unique_at_every_site": True,
                "fill_refines_partial_input": True,
                "fill_is_idempotent": True,
                "natural_form_independent_of_partial_input": True,
            }
        )
        result = self.runtime.supernet_integrator.determine(
            event_id,
            actor_id=data.actor_id,
            rigidity_scope=list(data.site_admissibility),
            rigidity_receipt=receipt,
            determined_form=determined_form,
            unitary_path_partition=path_partition,
            reason=(
                "The interaction-refined relation is rigid; fill reports the "
                "unique natural form without issuing TRUE"
            ),
        )
        return {
            **result,
            "rigid": True,
            "open_sites": [],
            "determined_form": determined_form,
            "unitary_path_partition": path_partition,
            "truth_issued": False,
        }

    async def return_event(self, event_id: str, data: EventReturnCreate) -> dict[str, Any]:
        source = self.runtime.supernet_store.get_event(event_id)
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=data.exact_text,
                authored_by=data.actor_id,
                form_label=data.form_label,
                language_label=data.language_label,
                relation_hints=_unique([
                    *data.relation_hints,
                    "return",
                    "successor potential",
                ]),
                causal_predecessor_ids=[event_id],
                parent_event_ids=[event_id],
                affected_perspectives=data.affected_perspectives,
                evidence_status=data.evidence_status,
                adapter_label="source",
                metadata={
                    **data.metadata,
                    "return_of_event_id": event_id,
                    "return_is_terminal": False,
                    "source_stage": source["current_stage"],
                    "source_verdict": source["current_verdict"],
                },
            )
        )
        returned_event = self.runtime.supernet_store.get_event(receipt["event_id"])
        transition = self.runtime.supernet_integrator.transition(
            event_id,
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The returned form becomes successor potential and remains reopenable",
                actor_id=data.actor_id,
                returned_resource_ids=[returned_event["id"]],
                successor_potential=[
                    {
                        "event_id": returned_event["id"],
                        "form_label": returned_event["form_label"],
                        "exact_source_ids": returned_event["exact_source_ids"],
                    }
                ],
                metadata={
                    "return_event_id": returned_event["id"],
                    "truth_issued": False,
                    "nonterminal": True,
                },
            ),
        )
        return {
            "source_transition": transition,
            "return_receipt": receipt,
            "returned_event": returned_event,
        }

    def reopen(self, event_id: str, data: EventReopenCreate) -> dict[str, Any]:
        self.runtime.supernet_store.get_event(event_id)
        return self.runtime.supernet_integrator.transition(
            event_id,
            IntegrationStateCreate(
                stage=IntegrationStage.REOPENED,
                verdict=Verdict.OPEN,
                reason=data.reason,
                actor_id=data.actor_id,
                successor_potential=[
                    {
                        "reopened_site": site,
                        "status": "OPEN",
                    }
                    for site in data.reopened_sites
                ],
                metadata={
                    **data.metadata,
                    "reopened_sites": data.reopened_sites,
                    "successor_hints": data.successor_hints,
                    "prior_truth_erased": False,
                    "truth_issued": False,
                },
            ),
        )

    def event_context(self, event_id: str, depth: int = 2) -> dict[str, Any]:
        event = self.runtime.supernet_store.get_event(event_id)
        projection = self.projection(
            mode=TopologyMode.FIELD,
            lens=IntegrationLens.ALL,
            focus_event_id=event_id,
        )
        adjacency: dict[str, set[str]] = defaultdict(set)
        for edge in projection["edges"]:
            source, target = edge["source"], edge["target"]
            if source in projection["event_ids"] and target in projection["event_ids"]:
                adjacency[source].add(target)
                adjacency[target].add(source)
        seen = {event_id}
        frontier = {event_id}
        for _ in range(max(0, min(depth, 6))):
            frontier = {
                neighbor
                for node in frontier
                for neighbor in adjacency.get(node, set())
                if neighbor not in seen
            }
            seen.update(frontier)
        nodes = [node for node in projection["nodes"] if node["id"] in seen]
        edges = [
            edge
            for edge in projection["edges"]
            if edge["source"] in seen and edge["target"] in seen
        ]
        occurrences: list[dict[str, Any]] = []
        for occurrence_id in event["exact_source_ids"]:
            try:
                occurrences.append(self.runtime.store.get_occurrence(occurrence_id))
            except KeyError:
                continue
        return {
            "event": event,
            "occurrences": occurrences,
            "nodes": nodes,
            "edges": edges,
            "selector": self._selector_payload(event),
            "metavector": next(
                (node.get("metavector") for node in nodes if node["id"] == event_id),
                None,
            ),
            "source_reverse_index": {
                f"integration:{event_id}": event["exact_source_ids"]
            },
        }

    def projection(
        self,
        *,
        mode: TopologyMode | str = TopologyMode.FIELD,
        lens: IntegrationLens | str = IntegrationLens.ALL,
        focus_event_id: str | None = None,
    ) -> dict[str, Any]:
        mode = TopologyMode(mode)
        lens = IntegrationLens(lens)
        field = self.runtime.supernet_integrator.projection(lens)
        events = field["events"]
        event_ids = {event["id"] for event in events}
        if focus_event_id and focus_event_id not in event_ids:
            try:
                focused = self.runtime.supernet_store.get_event(focus_event_id)
            except KeyError:
                focus_event_id = None
            else:
                events = [*events, focused]
                event_ids.add(focused["id"])
        if not focus_event_id and events:
            focus_event_id = events[-1]["id"]
        nodes = [self._node(event) for event in events]
        edges = self._edges(events, event_ids)
        adjacency = self._adjacency(event_ids, edges)
        components = self._components(sorted(event_ids), adjacency)
        metrics = self._metrics(sorted(event_ids), adjacency)
        loop_edges = self._loop_edges(sorted(event_ids), edges)
        for node in nodes:
            node["metavector"] = metrics.get(
                node["id"],
                {"degree": 0.0, "closeness": 0.0, "betweenness": 0.0},
            )
            node["community"] = next(
                (index for index, component in enumerate(components) if node["id"] in component),
                -1,
            )
        for edge in edges:
            edge["is_loop"] = (edge["source"], edge["target"], edge["kind"]) in loop_edges
        geometry = self._geometry(
            mode,
            nodes,
            edges,
            components,
            adjacency,
            focus_event_id,
        )
        positions = geometry.pop("positions")
        for node in nodes:
            node["position"] = positions.get(node["id"], {"x": 0.0, "y": 0.0})
        projection = {
            "generated_at": utcnow(),
            "mode": mode.value,
            "lens": lens.value,
            "focus_event_id": focus_event_id,
            "event_ids": sorted(event_ids),
            "nodes": nodes,
            "edges": edges,
            "components": [
                {
                    "id": f"component:{index}",
                    "event_ids": component,
                    "size": len(component),
                    "meta_vector": self._component_vector(component, metrics),
                }
                for index, component in enumerate(components)
            ],
            "current_stage": field["current_stage"],
            "lens_counts": field["lens_counts"],
            "stats": {
                **field["stats"],
                "nodes": len(nodes),
                "edges": len(edges),
                "components": len(components),
                "loop_edges": sum(1 for edge in edges if edge["is_loop"]),
                "rigid_events": sum(
                    1 for node in nodes if node["selector"]["rigid"]
                ),
                "open_selector_sites": sum(
                    len(node["selector"]["open_sites"]) for node in nodes
                ),
            },
            "source_reverse_index": field["source_reverse_index"],
            "canonical_runtime_operation": "integrate",
            "subsystems_are_lenses": True,
            "canonical_language": None,
            "truth_issued_by_determination": False,
            **geometry,
        }
        self.runtime.supernet_store.set_state(
            f"topology_projection:{mode.value}:{lens.value}", projection
        )
        return projection

    def _node(self, event: dict[str, Any]) -> dict[str, Any]:
        occurrence = None
        for occurrence_id in event["exact_source_ids"]:
            try:
                occurrence = self.runtime.store.get_occurrence(occurrence_id)
                break
            except KeyError:
                continue
        text = (
            occurrence.get("exact_text", "") if occurrence else str(event["metadata"].get("source_context", ""))
        )
        selector = self._selector_payload(event)
        return {
            "id": event["id"],
            "seq": event["seq"],
            "label": event["form_label"],
            "text": text,
            "authored_by": event["authored_by"],
            "language_label": event["language_label"],
            "adapter_label": event["adapter_label"] or "source",
            "stage": event["current_stage"],
            "verdict": event["current_verdict"],
            "relation_hints": event["relation_hints"],
            "capabilities": event["capabilities"],
            "constraints": event["constraints"],
            "affected_perspectives": event["affected_perspectives"],
            "exact_source_ids": event["exact_source_ids"],
            "parent_event_ids": event["parent_event_ids"],
            "causal_predecessor_ids": event["causal_predecessor_ids"],
            "selector": selector,
            "created_at": event["created_at"],
            "metadata": event["metadata"],
        }

    @staticmethod
    def _selector_payload(event: dict[str, Any]) -> dict[str, Any]:
        latest_receipt: dict[str, Any] | None = None
        determined_form: dict[str, Any] | None = None
        path_partition: dict[str, Any] | None = None
        for state in reversed(event["state_history"]):
            if latest_receipt is None and state.get("rigidity_receipt") is not None:
                latest_receipt = state["rigidity_receipt"]
            if determined_form is None and state.get("determined_form") is not None:
                determined_form = state["determined_form"]
            if path_partition is None and state.get("unitary_path_partition") is not None:
                path_partition = state["unitary_path_partition"]
        receipt = latest_receipt or {}
        return {
            "rigid": bool(receipt.get("rigid")) or determined_form is not None,
            "open_sites": list(receipt.get("open_sites") or []),
            "site_admissibility": dict(receipt.get("site_admissibility") or {}),
            "partial_input": dict(receipt.get("partial_input") or {}),
            "determined_form": determined_form,
            "unitary_path_partition": path_partition,
            "truth_issued": False,
        }

    @staticmethod
    def _edges(events: list[dict[str, Any]], event_ids: set[str]) -> list[dict[str, Any]]:
        seen: set[tuple[str, str, str, str | None]] = set()
        edges: list[dict[str, Any]] = []

        def add(source: str, target: str, kind: str, verdict: str, via: str | None = None) -> None:
            if source not in event_ids or target not in event_ids or source == target:
                return
            key = (source, target, kind, via)
            if key in seen:
                return
            seen.add(key)
            edges.append(
                {
                    "id": hashlib.sha256("|".join(str(item) for item in key).encode()).hexdigest()[:20],
                    "source": source,
                    "target": target,
                    "kind": kind,
                    "verdict": verdict,
                    "via_event_id": via,
                    "directed": True,
                }
            )

        for event in events:
            for parent in event["parent_event_ids"]:
                add(parent, event["id"], "interaction", event["current_verdict"])
            for predecessor in event["causal_predecessor_ids"]:
                add(predecessor, event["id"], "causal", event["current_verdict"])
            endpoints = event["metadata"].get("relation_endpoints") or []
            if len(endpoints) == 2:
                label = (
                    event["relation_hints"][0]
                    if event["relation_hints"]
                    else "translation"
                )
                add(endpoints[0], endpoints[1], label, event["current_verdict"], event["id"])
                if event["metadata"].get("direction") == "bidirectional":
                    add(endpoints[1], endpoints[0], label, event["current_verdict"], event["id"])
        return edges

    @staticmethod
    def _adjacency(event_ids: set[str], edges: list[dict[str, Any]]) -> dict[str, set[str]]:
        adjacency = {event_id: set() for event_id in event_ids}
        for edge in edges:
            adjacency[edge["source"]].add(edge["target"])
            adjacency[edge["target"]].add(edge["source"])
        return adjacency

    @staticmethod
    def _components(event_ids: list[str], adjacency: dict[str, set[str]]) -> list[list[str]]:
        remaining = set(event_ids)
        components: list[list[str]] = []
        while remaining:
            root = min(remaining)
            queue = [root]
            component: list[str] = []
            remaining.remove(root)
            while queue:
                node = queue.pop()
                component.append(node)
                for neighbor in sorted(adjacency.get(node, set())):
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        queue.append(neighbor)
            components.append(sorted(component))
        return components

    @staticmethod
    def _loop_edges(event_ids: list[str], edges: list[dict[str, Any]]) -> set[tuple[str, str, str]]:
        union = _UnionFind(event_ids)
        loops: set[tuple[str, str, str]] = set()
        for edge in sorted(edges, key=lambda item: (item["source"], item["target"], item["kind"])):
            if not union.union(edge["source"], edge["target"]):
                loops.add((edge["source"], edge["target"], edge["kind"]))
        return loops

    @staticmethod
    def _metrics(event_ids: list[str], adjacency: dict[str, set[str]]) -> dict[str, dict[str, float]]:
        n = len(event_ids)
        if not n:
            return {}
        degree = {
            node: len(adjacency.get(node, set())) / max(1, n - 1)
            for node in event_ids
        }
        if n <= 400:
            sources = event_ids
        else:
            sources = sorted(event_ids, key=_hash_fraction)[:128]
        closeness_sum = {node: 0.0 for node in event_ids}
        closeness_seen = {node: 0 for node in event_ids}
        betweenness = {node: 0.0 for node in event_ids}
        for source in sources:
            distance = {source: 0}
            sigma = {node: 0.0 for node in event_ids}
            sigma[source] = 1.0
            predecessors: dict[str, list[str]] = {node: [] for node in event_ids}
            queue: deque[str] = deque([source])
            stack: list[str] = []
            while queue:
                node = queue.popleft()
                stack.append(node)
                for neighbor in adjacency.get(node, set()):
                    if neighbor not in distance:
                        distance[neighbor] = distance[node] + 1
                        queue.append(neighbor)
                    if distance.get(neighbor) == distance[node] + 1:
                        sigma[neighbor] += sigma[node]
                        predecessors[neighbor].append(node)
            total = sum(distance.values())
            source_closeness = (
                (len(distance) - 1) / total if total and len(distance) > 1 else 0.0
            )
            closeness_sum[source] += source_closeness
            closeness_seen[source] += 1
            for reached, d in distance.items():
                if reached == source or not d:
                    continue
                closeness_sum[reached] += 1.0 / d
                closeness_seen[reached] += 1
            dependency = {node: 0.0 for node in event_ids}
            while stack:
                node = stack.pop()
                for predecessor in predecessors[node]:
                    if sigma[node]:
                        dependency[predecessor] += (
                            sigma[predecessor] / sigma[node]
                        ) * (1.0 + dependency[node])
                if node != source:
                    betweenness[node] += dependency[node]
        closeness = {
            node: (closeness_sum[node] / closeness_seen[node] if closeness_seen[node] else 0.0)
            for node in event_ids
        }
        max_close = max(closeness.values(), default=0.0)
        if max_close:
            closeness = {node: value / max_close for node, value in closeness.items()}
        max_between = max(betweenness.values(), default=0.0)
        if max_between:
            betweenness = {node: value / max_between for node, value in betweenness.items()}
        return {
            node: {
                "degree": round(degree[node], 6),
                "closeness": round(closeness[node], 6),
                "betweenness": round(betweenness[node], 6),
                "length": round(0.2 + 0.8 * closeness[node], 6),
                "thickness": round(0.2 + 0.8 * degree[node], 6),
                "angle": round(2 * math.pi * _hash_fraction(node), 6),
                "sampled": n > 400,
            }
            for node in event_ids
        }

    @staticmethod
    def _component_vector(component: list[str], metrics: dict[str, dict[str, float]]) -> dict[str, float]:
        x = y = thickness = 0.0
        for node in component:
            metric = metrics.get(node, {})
            length = float(metric.get("length", 0.0))
            angle = float(metric.get("angle", 0.0))
            x += length * math.cos(angle)
            y += length * math.sin(angle)
            thickness += float(metric.get("thickness", 0.0))
        magnitude = math.hypot(x, y)
        return {
            "x": round(x, 6),
            "y": round(y, 6),
            "magnitude": round(magnitude, 6),
            "angle": round(math.atan2(y, x) if magnitude else 0.0, 6),
            "thickness": round(thickness, 6),
        }

    def _geometry(
        self,
        mode: TopologyMode,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        components: list[list[str]],
        adjacency: dict[str, set[str]],
        focus_event_id: str | None,
    ) -> dict[str, Any]:
        if mode == TopologyMode.ZERO_INFINITY:
            return self._zero_infinity(nodes, adjacency, focus_event_id)
        if mode == TopologyMode.LIGHT_CONE:
            return self._light_cone(nodes, edges, focus_event_id)
        if mode == TopologyMode.ELLIPSE_MIRROR:
            return self._ellipse(nodes, focus_event_id)
        if mode == TopologyMode.TRUTH_DIAGONAL:
            return self._truth_diagonal(nodes, edges, focus_event_id)
        if mode == TopologyMode.SELECTOR:
            return self._selector_geometry(nodes, focus_event_id)
        if mode == TopologyMode.ANATOMY_TREE:
            return self._anatomy_tree(nodes, edges, focus_event_id)
        if mode == TopologyMode.BALL_HAIR:
            return self._ball_hair(nodes, components)
        return self._component_geometry(mode, nodes, components)

    @staticmethod
    def _component_geometry(
        mode: TopologyMode,
        nodes: list[dict[str, Any]],
        components: list[list[str]],
    ) -> dict[str, Any]:
        positions: dict[str, dict[str, float]] = {}
        hulls: list[dict[str, Any]] = []
        trajectories: dict[str, list[str]] = defaultdict(list)
        node_by_id = {node["id"]: node for node in nodes}
        count = max(1, len(components))
        for component_index, component in enumerate(components):
            center_angle = 2 * math.pi * component_index / count
            center_radius = 320.0 if count > 1 else 0.0
            cx = center_radius * math.cos(center_angle)
            cy = center_radius * math.sin(center_angle)
            radius = max(75.0, 34.0 * math.sqrt(max(1, len(component))))
            for index, event_id in enumerate(component):
                if mode == TopologyMode.POINT_LINE_LOOP:
                    angle = index * 2.399963229728653
                    local_radius = 20.0 + 18.0 * math.sqrt(index)
                elif mode == TopologyMode.METAVECTOR:
                    metric = node_by_id[event_id]["metavector"]
                    angle = metric["angle"]
                    local_radius = 55.0 + 170.0 * metric["length"]
                else:
                    angle = 2 * math.pi * index / max(1, len(component))
                    local_radius = radius * (0.35 if len(component) == 1 else 0.72)
                positions[event_id] = {
                    "x": round(cx + local_radius * math.cos(angle), 3),
                    "y": round(cy + local_radius * math.sin(angle), 3),
                }
                trajectories[node_by_id[event_id]["authored_by"]].append(event_id)
            hulls.append(
                {
                    "id": f"shared:{component_index}",
                    "event_ids": component,
                    "cx": round(cx, 3),
                    "cy": round(cy, 3),
                    "radius": round(radius, 3),
                    "kind": "shared-architecture" if mode == TopologyMode.SHARED_ARCHITECTURE else "component",
                }
            )
        return {
            "positions": positions,
            "hulls": hulls,
            "participant_trajectories": dict(trajectories),
            "shared_architecture": {
                "least_field_event_ids": [node["id"] for node in nodes],
                "participant_trajectories": dict(trajectories),
                "imposed_target": False,
            },
        }

    @staticmethod
    def _ball_hair(nodes: list[dict[str, Any]], components: list[list[str]]) -> dict[str, Any]:
        base = SupernetTopologyService._component_geometry(
            TopologyMode.FIELD, nodes, components
        )
        node_by_id = {node["id"]: node for node in nodes}
        hairs: list[dict[str, Any]] = []
        balls: list[dict[str, Any]] = []
        for hull in base["hulls"]:
            balls.append({**hull, "kind": "ball"})
            for event_id in hull["event_ids"]:
                node = node_by_id[event_id]
                if node["verdict"] == "OPEN" or node["stage"] == "REOPENED":
                    position = base["positions"][event_id]
                    angle = math.atan2(position["y"] - hull["cy"], position["x"] - hull["cx"])
                    hairs.append(
                        {
                            "event_id": event_id,
                            "x1": position["x"],
                            "y1": position["y"],
                            "x2": round(position["x"] + 90 * math.cos(angle), 3),
                            "y2": round(position["y"] + 90 * math.sin(angle), 3),
                            "open": True,
                        }
                    )
        base["hulls"] = []
        base.update({"balls": balls, "hairs": hairs})
        return base

    @staticmethod
    def _zero_infinity(
        nodes: list[dict[str, Any]], adjacency: dict[str, set[str]], focus: str | None
    ) -> dict[str, Any]:
        positions: dict[str, dict[str, float]] = {}
        if not nodes:
            return {"positions": positions, "zero_infinity": {}}
        focus = focus or nodes[-1]["id"]
        distance = {focus: 0}
        queue: deque[str] = deque([focus])
        while queue:
            node = queue.popleft()
            for neighbor in adjacency.get(node, set()):
                if neighbor not in distance:
                    distance[neighbor] = distance[node] + 1
                    queue.append(neighbor)
        max_distance = max(distance.values(), default=0)
        outer = max(1, max_distance + 1)
        for node in nodes:
            event_id = node["id"]
            if event_id == focus:
                positions[event_id] = {"x": 0.0, "y": 0.0}
                node["pole"] = "0"
                continue
            d = distance.get(event_id, outer)
            radius = 60.0 + 430.0 * d / outer
            angle = 2 * math.pi * _hash_fraction(event_id)
            positions[event_id] = {
                "x": round(radius * math.cos(angle), 3),
                "y": round(radius * math.sin(angle), 3),
            }
            node["pole"] = "∞" if event_id not in distance else "between"
            node["reciprocal_radius"] = round(1.0 / (1.0 + d), 6)
        return {
            "positions": positions,
            "zero_infinity": {
                "zero_event_id": focus,
                "infinity_event_ids": [node["id"] for node in nodes if node["id"] not in distance],
                "outer_radius": 490.0,
                "poles_are_relational_readings": True,
            },
        }

    @staticmethod
    def _light_cone(
        nodes: list[dict[str, Any]], edges: list[dict[str, Any]], focus: str | None
    ) -> dict[str, Any]:
        positions: dict[str, dict[str, float]] = {}
        if not nodes:
            return {"positions": positions, "light_cone": {}}
        focus = focus or nodes[-1]["id"]
        incoming: dict[str, set[str]] = defaultdict(set)
        outgoing: dict[str, set[str]] = defaultdict(set)
        for edge in edges:
            outgoing[edge["source"]].add(edge["target"])
            incoming[edge["target"]].add(edge["source"])

        def closure(start: str, graph: dict[str, set[str]]) -> dict[str, int]:
            result = {start: 0}
            queue: deque[str] = deque([start])
            while queue:
                current = queue.popleft()
                for neighbor in graph.get(current, set()):
                    if neighbor not in result:
                        result[neighbor] = result[current] + 1
                        queue.append(neighbor)
            return result

        past = closure(focus, incoming)
        future = closure(focus, outgoing)
        concurrent: list[str] = []
        for node in nodes:
            event_id = node["id"]
            angle = 2 * math.pi * _hash_fraction(event_id)
            if event_id == focus:
                positions[event_id] = {"x": 0.0, "y": 0.0}
                node["causal_class"] = "focus"
            elif event_id in past:
                d = past[event_id]
                positions[event_id] = {"x": -110.0 * d, "y": round(85 * math.sin(angle), 3)}
                node["causal_class"] = "past"
            elif event_id in future:
                d = future[event_id]
                positions[event_id] = {"x": 110.0 * d, "y": round(85 * math.sin(angle), 3)}
                node["causal_class"] = "future"
            else:
                concurrent.append(event_id)
                positions[event_id] = {"x": round(40 * math.cos(angle), 3), "y": round(260 * math.sin(angle), 3)}
                node["causal_class"] = "concurrent"
        return {
            "positions": positions,
            "light_cone": {
                "focus_event_id": focus,
                "past_event_ids": sorted(set(past) - {focus}),
                "future_event_ids": sorted(set(future) - {focus}),
                "concurrent_event_ids": concurrent,
                "causal_order_not_delivery_order": True,
            },
        }

    @staticmethod
    def _ellipse(nodes: list[dict[str, Any]], focus: str | None) -> dict[str, Any]:
        positions: dict[str, dict[str, float]] = {}
        if not nodes:
            return {"positions": positions, "ellipse": {}}
        ordered = sorted(nodes, key=lambda node: node["seq"])
        first = focus or ordered[0]["id"]
        second = next((node["id"] for node in reversed(ordered) if node["id"] != first), first)
        a, b = 470.0, 270.0
        c = math.sqrt(a * a - b * b)
        for index, node in enumerate(ordered):
            angle = 2 * math.pi * index / max(1, len(ordered))
            positions[node["id"]] = {
                "x": round(a * math.cos(angle), 3),
                "y": round(b * math.sin(angle), 3),
            }
        positions[first] = {"x": round(-c, 3), "y": 0.0}
        positions[second] = {"x": round(c, 3), "y": 0.0}
        return {
            "positions": positions,
            "ellipse": {
                "a": a,
                "b": b,
                "focus_event_ids": [first, second],
                "return_geometry": "two-focus relational path",
                "physical_law_claimed": False,
            },
        }

    @staticmethod
    def _truth_diagonal(
        nodes: list[dict[str, Any]], edges: list[dict[str, Any]], focus: str | None
    ) -> dict[str, Any]:
        positions: dict[str, dict[str, float]] = {}
        if not nodes:
            return {"positions": positions, "truth_diagonal": {}}
        focus = focus or nodes[-1]["id"]
        incoming = [edge for edge in edges if edge["target"] == focus]
        outgoing = [edge for edge in edges if edge["source"] == focus]
        left = sorted({edge["source"] for edge in incoming})
        right = sorted({edge["target"] for edge in outgoing})
        other = [node["id"] for node in nodes if node["id"] not in {focus, *left, *right}]
        positions[focus] = {"x": 0.0, "y": 0.0}
        for index, event_id in enumerate(left):
            positions[event_id] = {"x": -360.0, "y": (index - (len(left) - 1) / 2) * 100.0}
        for index, event_id in enumerate(right):
            positions[event_id] = {"x": 360.0, "y": (index - (len(right) - 1) / 2) * 100.0}
        for index, event_id in enumerate(other):
            angle = 2 * math.pi * index / max(1, len(other))
            positions[event_id] = {"x": round(520 * math.cos(angle), 3), "y": round(340 * math.sin(angle), 3)}
        focus_node = next(node for node in nodes if node["id"] == focus)
        return {
            "positions": positions,
            "truth_diagonal": {
                "focus_event_id": focus,
                "local_event_ids": left,
                "translated_event_ids": right,
                "determined_form": focus_node["selector"]["determined_form"],
                "residue": focus_node["constraints"],
                "equality_during_translation": True,
                "absolute_language_selected": False,
            },
        }

    @staticmethod
    def _selector_geometry(nodes: list[dict[str, Any]], focus: str | None) -> dict[str, Any]:
        positions: dict[str, dict[str, float]] = {}
        if not nodes:
            return {"positions": positions, "selector": {}}
        focus = focus or nodes[-1]["id"]
        positions[focus] = {"x": 0.0, "y": 0.0}
        for index, node in enumerate(nodes):
            if node["id"] == focus:
                continue
            angle = 2 * math.pi * index / max(1, len(nodes))
            positions[node["id"]] = {"x": round(480 * math.cos(angle), 3), "y": round(320 * math.sin(angle), 3)}
        focus_node = next(node for node in nodes if node["id"] == focus)
        relation = focus_node["selector"]["site_admissibility"]
        site_nodes: list[dict[str, Any]] = []
        symbol_nodes: list[dict[str, Any]] = []
        site_edges: list[dict[str, Any]] = []
        sites = sorted(relation)
        for index, site in enumerate(sites):
            angle = 2 * math.pi * index / max(1, len(sites))
            site_id = f"selector-site:{focus}:{site}"
            site_position = {"x": round(220 * math.cos(angle), 3), "y": round(220 * math.sin(angle), 3)}
            site_nodes.append({"id": site_id, "site": site, "position": site_position, "rigid": len(relation[site]) == 1})
            for symbol_index, symbol in enumerate(relation[site]):
                symbol_id = f"selector-symbol:{focus}:{site}:{symbol_index}"
                offset = (symbol_index - (len(relation[site]) - 1) / 2) * 40
                symbol_position = {"x": round(site_position["x"] + 70 * math.cos(angle) - offset * math.sin(angle), 3), "y": round(site_position["y"] + 70 * math.sin(angle) + offset * math.cos(angle), 3)}
                symbol_nodes.append({"id": symbol_id, "site": site, "symbol": symbol, "position": symbol_position, "selected": focus_node["selector"]["determined_form"] is not None and focus_node["selector"]["determined_form"].get(site) == symbol})
                site_edges.append({"source": site_id, "target": symbol_id, "kind": "admissible"})
        return {
            "positions": positions,
            "selector": {
                **focus_node["selector"],
                "focus_event_id": focus,
                "site_nodes": site_nodes,
                "symbol_nodes": symbol_nodes,
                "site_edges": site_edges,
                "selection_is_forced_when_rigid": True,
                "truth_issued": False,
            },
        }

    @staticmethod
    def _anatomy_tree(
        nodes: list[dict[str, Any]], edges: list[dict[str, Any]], focus: str | None
    ) -> dict[str, Any]:
        positions: dict[str, dict[str, float]] = {}
        if not nodes:
            return {"positions": positions, "anatomy_tree": {}}
        root = focus or nodes[0]["id"]
        outgoing: dict[str, list[str]] = defaultdict(list)
        for edge in edges:
            outgoing[edge["source"]].append(edge["target"])
        depth = {root: 0}
        queue: deque[str] = deque([root])
        while queue:
            current = queue.popleft()
            for neighbor in sorted(outgoing.get(current, [])):
                if neighbor not in depth:
                    depth[neighbor] = depth[current] + 1
                    queue.append(neighbor)
        by_depth: dict[int, list[str]] = defaultdict(list)
        unreachable: list[str] = []
        for node in nodes:
            if node["id"] in depth:
                by_depth[depth[node["id"]]].append(node["id"])
            else:
                unreachable.append(node["id"])
        for level, event_ids in by_depth.items():
            for index, event_id in enumerate(sorted(event_ids)):
                positions[event_id] = {"x": level * 190.0, "y": (index - (len(event_ids) - 1) / 2) * 100.0}
        for index, event_id in enumerate(unreachable):
            positions[event_id] = {"x": -240.0, "y": (index - (len(unreachable) - 1) / 2) * 85.0}
        return {
            "positions": positions,
            "anatomy_tree": {
                "selected_0": root,
                "reaches_all": len(depth) == len(nodes),
                "generated_event_ids": sorted(depth),
                "not_generated_event_ids": unreachable,
                "root_is_selected_not_absolute": True,
            },
        }

    @staticmethod
    def _unitary_path_partition(
        determined_form: dict[str, str], unitary_step: dict[str, str]
    ) -> dict[str, Any]:
        symbols = sorted(set(determined_form.values()))
        step = dict(unitary_step) if unitary_step else {symbol: symbol for symbol in symbols}
        if set(step) != set(symbols) or set(step.values()) != set(symbols):
            raise ValueError(
                "unitary_step must be a bijection of exactly the determined symbol alphabet"
            )
        unvisited = set(symbols)
        classes: list[list[str]] = []
        while unvisited:
            start = min(unvisited)
            orbit: list[str] = []
            current = start
            while current not in orbit:
                orbit.append(current)
                unvisited.discard(current)
                current = step[current]
            classes.append(orbit)
        site_partition: dict[str, list[str]] = defaultdict(list)
        for site, symbol in determined_form.items():
            site_partition[symbol].append(site)
        return {
            "step": step,
            "symbol_orbits": classes,
            "site_partition": dict(site_partition),
            "classes_cover": True,
            "classes_equal_or_disjoint": True,
            "step_closed": True,
            "unique_generated_partition": True,
        }
