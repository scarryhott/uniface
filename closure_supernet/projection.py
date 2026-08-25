from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from .models import BlackMirrorProjection, OpenSeam, ProjectionClass, ProjectionEdge, Verdict
from .store import EventStore


class _UnionFind:
    def __init__(self, values: list[str]):
        self.parent = {value: value for value in values}
        self.rank = {value: 0 for value in values}

    def find(self, value: str) -> str:
        parent = self.parent[value]
        if parent != value:
            self.parent[value] = self.find(parent)
        return self.parent[value]

    def union(self, left: str, right: str) -> None:
        a, b = self.find(left), self.find(right)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1


def _class_id(member_ids: list[str]) -> str:
    return hashlib.sha256("|".join(sorted(member_ids)).encode("utf-8")).hexdigest()[:16]


def build_projection(store: EventStore) -> BlackMirrorProjection:
    occurrences = store.list_occurrences(limit=100_000)
    occurrence_by_id = {row["id"]: row for row in occurrences}
    union = _UnionFind(list(occurrence_by_id))

    interpretations = {row["id"]: row for row in store.list_interpretations(limit=100_000)}
    candidates = {row["id"]: row for row in store.list_candidate_relations(limit=100_000)}
    admissions = store.latest_admissions(limit=100_000)

    for admission in admissions:
        if admission["verdict"] != Verdict.TRUE:
            continue
        interpretation = interpretations.get(admission["interpretation_id"])
        if not interpretation:
            continue
        candidate = candidates.get(interpretation["candidate_relation_id"])
        if not candidate:
            continue
        union.union(candidate["source_occurrence"], candidate["target_occurrence"])

    grouped: dict[str, list[str]] = defaultdict(list)
    for occurrence_id in occurrence_by_id:
        grouped[union.find(occurrence_id)].append(occurrence_id)

    class_by_occurrence: dict[str, str] = {}
    classes: list[ProjectionClass] = []
    source_reverse_index: dict[str, list[str]] = {}

    for member_ids in grouped.values():
        cid = _class_id(member_ids)
        labels: list[str] = []
        operators: set[str] = set()
        statuses: set[str] = set()
        for occurrence_id in sorted(member_ids):
            occurrence = occurrence_by_id[occurrence_id]
            label = occurrence["exact_text"].replace("\n", " ").strip()
            labels.append(label[:120])
            operators.update(str(item["key"]) for item in occurrence["operator_path"])
            statuses.add(occurrence["evidence_status"])
            class_by_occurrence[occurrence_id] = cid
        classes.append(
            ProjectionClass(
                id=cid,
                member_ids=sorted(member_ids),
                labels=labels,
                operators=sorted(operators),
                opacity=max(0, len(member_ids) - 1),
                evidence_statuses=sorted(statuses),
            )
        )
        source_reverse_index[cid] = sorted(member_ids)

    edges: list[ProjectionEdge] = []
    for admission in admissions:
        interpretation = interpretations.get(admission["interpretation_id"])
        if not interpretation:
            continue
        candidate = candidates.get(interpretation["candidate_relation_id"])
        if not candidate:
            continue
        source = class_by_occurrence.get(candidate["source_occurrence"])
        target = class_by_occurrence.get(candidate["target_occurrence"])
        if source is None or target is None:
            continue
        if source == target and admission["verdict"] == Verdict.TRUE:
            continue
        edges.append(
            ProjectionEdge(
                source=source,
                target=target,
                relation_type=candidate["relation_type"],
                verdict=Verdict(admission["verdict"]),
                interpretation_id=interpretation["id"],
            )
        )

    latest_verdict_by_interpretation = {row["interpretation_id"]: row["verdict"] for row in admissions}
    seams = []
    for row in store.list_open_seams(limit=100_000):
        interpretation_id = row.get("metadata", {}).get("interpretation_id")
        if interpretation_id and latest_verdict_by_interpretation.get(interpretation_id) not in {None, Verdict.OPEN}:
            continue
        seams.append(OpenSeam.model_validate(row))
    projection = BlackMirrorProjection(
        generated_at=datetime.now(UTC).isoformat(),
        classes=sorted(classes, key=lambda item: item.id),
        edges=edges,
        open_seams=seams,
        stats={
            **store.stats(),
            "projection_classes": len(classes),
            "projection_edges": len(edges),
            "opacity_total": sum(item.opacity for item in classes),
            "turing_complete_assumed": False,
        },
        source_reverse_index=source_reverse_index,
    )
    return projection
