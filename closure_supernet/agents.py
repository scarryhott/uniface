from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .axiometry import extract_exact_symbols, extract_operator_path, jaccard, operator_keys
from .config import RuntimeConfig
from .models import OccurrenceCreate, OccurrenceStatus, RelationType, RuleState, RuleVersionCreate, Verdict
from .policy import AdmissionPolicy
from .providers import InterpretationProvider
from .projection import build_projection
from .store import EventStore


class InboxSensorAgent:
    name = "inbox-sensor"

    def __init__(self, config: RuntimeConfig, store: EventStore):
        self.config = config
        self.store = store

    def run(self) -> int:
        count = 0
        for path in sorted(self.config.inbox_dir.rglob("*")):
            if not path.is_file() or path.suffix.casefold() not in {".md", ".txt", ".jsonl"}:
                continue
            if path.suffix.casefold() == ".jsonl":
                count += self._ingest_jsonl(path)
            else:
                text = path.read_text(encoding="utf-8")
                checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
                source_location = str(path.resolve())
                if self.store.occurrence_exists_by_checksum(checksum, source_location):
                    continue
                self._create(text, source_id="inbox", source_location=source_location)
                count += 1
        return count

    def _ingest_jsonl(self, path: Path) -> int:
        count = 0
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            text = str(payload["exact_text"])
            source_location = f"{path.resolve()}:{line_number}"
            checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if self.store.occurrence_exists_by_checksum(checksum, source_location):
                continue
            self._create(
                text,
                source_id=str(payload.get("source_id", "inbox-jsonl")),
                source_location=source_location,
                source_context=payload.get("source_context"),
                metadata=payload.get("metadata") or {},
            )
            count += 1
        return count

    def _create(
        self,
        text: str,
        source_id: str,
        source_location: str | None,
        source_context: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        path = extract_operator_path(text)
        symbols = extract_exact_symbols(text, path)
        return self.store.create_occurrence(
            OccurrenceCreate(
                exact_text=text,
                source_id=source_id,
                source_location=source_location,
                source_context=source_context,
                status=OccurrenceStatus.ORIGINAL_NOTE,
                metadata=metadata or {},
            ),
            symbols,
            path,
        )


class UnderstandingAgent:
    name = "understanding-agent"

    def __init__(self, config: RuntimeConfig, store: EventStore):
        self.config = config
        self.store = store

    def run(self) -> int:
        occurrences = self.store.list_occurrences(limit=100_000)
        created = 0
        for index, source in enumerate(occurrences):
            proposals: list[tuple[float, str, dict[str, Any], str]] = []
            for target in occurrences[:index]:
                relation_type, score, rationale = self._classify(source, target)
                if relation_type is None:
                    continue
                proposals.append((score, relation_type, target, rationale))
            proposals.sort(key=lambda item: (-item[0], item[2]["id"]))
            for score, relation_type, target, rationale in proposals[: self.config.max_candidates_per_occurrence]:
                _row, was_created = self.store.create_candidate_relation(
                    source["id"],
                    target["id"],
                    relation_type,
                    score,
                    rationale,
                    proposed_by=self.name,
                )
                created += int(was_created)
        return created

    def _classify(self, source: dict[str, Any], target: dict[str, Any]) -> tuple[str | None, float, str]:
        if source["exact_text"] == target["exact_text"]:
            return RelationType.SAME_LITERAL_EQUATION, 1.0, "Exact source text matches; occurrences remain distinct and source-reversible"

        source_keys = operator_keys(source["operator_path"])
        target_keys = operator_keys(target["operator_path"])
        overlap = set(source_keys) & set(target_keys)
        semantic = jaccard(source["exact_text"], target["exact_text"])

        if source_keys and source_keys == target_keys:
            source_lexemes = [item["lexeme"] for item in source["operator_path"]]
            target_lexemes = [item["lexeme"] for item in target["operator_path"]]
            if source_lexemes != target_lexemes:
                return RelationType.NOTATIONAL_VARIANT, 0.97, "The literal lexemes differ while the indexed axiometric operator path is equal"
            return RelationType.SAME_OPERATOR_PATH, 0.95, "The notes enact the same ordered source-axiometric operator path"

        if source_keys and source_keys == list(reversed(target_keys)):
            return RelationType.INVERSE_PATH, 0.91, "The indexed operator path is reversed; this is a candidate inverse, not an established equivalence"

        if overlap:
            score = min(0.89, 0.55 + 0.09 * len(overlap) + 0.15 * semantic)
            return RelationType.MODEL_SUGGESTED_RELATION, score, f"Shared source operators: {', '.join(sorted(overlap))}; interpretation remains OPEN"

        if semantic >= self.config.semantic_threshold:
            return RelationType.MODEL_SUGGESTED_RELATION, semantic, "Semantic neighborhood only; no operator equivalence is asserted"

        return None, 0.0, ""


class InterpretationAgent:
    name = "interpretation-agent"
    engine_version = "interpretation-v1"

    def __init__(self, store: EventStore, provider: InterpretationProvider):
        self.store = store
        self.provider = provider

    async def run(self) -> int:
        created = 0
        for candidate in self.store.uninterpreted_candidates(limit=500):
            source = self.store.get_occurrence(candidate["source_occurrence"])
            target = self.store.get_occurrence(candidate["target_occurrence"])
            source_keys = operator_keys(source["operator_path"])
            target_keys = operator_keys(target["operator_path"])
            common_keys = sorted(set(source_keys) & set(target_keys))
            source_only = sorted(set(source_keys) - set(target_keys))
            target_only = sorted(set(target_keys) - set(source_keys))

            payload: dict[str, Any] = {
                "candidate_relation_id": candidate["id"],
                "source_operator_path": source["operator_path"],
                "target_operator_path": target["operator_path"],
                "preserved_structure": common_keys,
                "transformed_structure": [
                    *(f"source-only:{key}" for key in source_only),
                    *(f"target-only:{key}" for key in target_only),
                ],
                "omitted_or_hidden_structure": [
                    "The exact source occurrences are not reconstructed from a projected relation",
                    "Semantic or operator-path resemblance does not by itself prove identical meaning",
                ],
                "frame_and_scope": f"{candidate['relation_type']} proposed within the source-preserving axiometric index",
                "reverse_path": [source["id"], target["id"]],
                "affected_perspectives": sorted({source["source_id"], target["source_id"]}),
                "formal_scope": "No machine-checked equivalence is inferred unless an explicit FORMALIZES witness is attached",
                "empirical_scope": "No physical, social, or moral fact is inferred from formal or semantic similarity",
                "reopening": "Retain both occurrences and reopen the relation for author confirmation, proof, contradiction, or alternate interpretation",
                "generated_by": self.name,
                "status": "INTERPRETED_RELATION",
            }
            provider_payload = await self.provider.interpret(source, target, candidate)
            if provider_payload:
                for key in (
                    "preserved_structure",
                    "transformed_structure",
                    "omitted_or_hidden_structure",
                    "frame_and_scope",
                    "affected_perspectives",
                    "formal_scope",
                    "empirical_scope",
                    "reopening",
                ):
                    if key in provider_payload and provider_payload[key]:
                        payload[key] = provider_payload[key]
                payload["generated_by"] = f"{self.name}+{self.provider.name}"

            _row, was_created = self.store.create_interpretation(payload, self.engine_version)
            created += int(was_created)
        return created


class AdmissionAgent:
    name = "admission-agent"

    def __init__(self, store: EventStore, policy: AdmissionPolicy):
        self.store = store
        self.policy = policy

    def run(self) -> int:
        created = 0
        version = self.store.active_rule_version()
        for interpretation in self.store.unadmitted_interpretations(version, limit=500):
            candidate = self.store.get_candidate_relation(interpretation["candidate_relation_id"])
            source = self.store.get_occurrence(candidate["source_occurrence"])
            target = self.store.get_occurrence(candidate["target_occurrence"])
            result = self.policy.evaluate(candidate, interpretation, source, target)
            _row, was_created = self.store.create_admission(
                interpretation["id"], result.verdict, result.checks, result.reason, version, self.name
            )
            created += int(was_created)
        return created


class ReopeningAgent:
    name = "reopening-agent"

    def __init__(self, store: EventStore):
        self.store = store

    def run(self) -> int:
        interpretations = {row["id"]: row for row in self.store.list_interpretations(limit=100_000)}
        candidates = {row["id"]: row for row in self.store.list_candidate_relations(limit=100_000)}
        created = 0
        for admission in self.store.latest_admissions(limit=100_000):
            if admission["verdict"] != Verdict.OPEN:
                continue
            interpretation = interpretations.get(admission["interpretation_id"])
            if not interpretation:
                continue
            candidate = candidates.get(interpretation["candidate_relation_id"])
            if not candidate:
                continue
            _seam, was_created = self.store.create_open_seam(
                candidate["source_occurrence"],
                candidate["target_occurrence"],
                admission["reason"],
                metadata={
                    "interpretation_id": interpretation["id"],
                    "relation_type": candidate["relation_type"],
                    "reopening": interpretation["reopening"],
                },
            )
            created += int(was_created)
        return created


class MoralAuditAgent:
    name = "moral-audit-agent"

    def __init__(self, store: EventStore):
        self.store = store

    def run(self) -> int:
        created = 0
        candidates = {row["id"]: row for row in self.store.list_candidate_relations(limit=100_000)}
        for interpretation in self.store.list_interpretations(limit=100_000):
            if interpretation["affected_perspectives"]:
                continue
            candidate = candidates[interpretation["candidate_relation_id"]]
            _seam, was_created = self.store.create_open_seam(
                candidate["source_occurrence"],
                candidate["target_occurrence"],
                "Affected perspectives were not retained; projection cannot claim moral completeness",
                metadata={"interpretation_id": interpretation["id"], "audit": self.name},
            )
            created += int(was_created)
        return created


class RuleReviewAgent:
    name = "rule-review-agent"

    def __init__(self, config: RuntimeConfig, store: EventStore):
        self.config = config
        self.store = store

    def run(self) -> int:
        seams = self.store.list_open_seams(limit=100_000)
        counts = Counter(seam["reason"] for seam in seams)
        existing = self.store.list_rules()
        existing_reasons = {rule["reason_for_change"] for rule in existing}
        created = 0
        for reason, count in counts.items():
            if count < 5:
                continue
            proposal_reason = f"Repeated OPEN seam ({count} occurrences): {reason}"
            if proposal_reason in existing_reasons:
                continue
            rule = self.store.create_rule_version(
                RuleVersionCreate(
                    rule_id="source-preserving-admission",
                    parent_version=self.store.active_rule_version(),
                    exact_rule_text=(
                        "Proposed additive review: preserve the constitutional source rules while adding an explicit "
                        f"review path for repeated seam: {reason}"
                    ),
                    reason_for_change=proposal_reason,
                    state=RuleState.PROPOSED,
                    metadata={"generated_by": self.name, "seam_count": count},
                )
            )
            created += 1
            if self.config.auto_activate_rule_proposals:
                self.store.activate_rule(rule["id"])
        return created


class ProjectionAgent:
    name = "projection-agent"

    def __init__(self, store: EventStore):
        self.store = store

    def run(self) -> dict[str, Any]:
        projection = build_projection(self.store)
        payload = projection.model_dump(mode="json")
        self.store.set_state("black_mirror_projection", payload)
        self.store.append_event(
            "PROJECTION_REBUILT",
            "projection",
            projection.generated_at,
            {"classes": len(projection.classes), "edges": len(projection.edges), "open_seams": len(projection.open_seams)},
        )
        return payload
