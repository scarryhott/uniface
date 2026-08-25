from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import RuntimeConfig
from .models import RelationType, Verdict


@dataclass(slots=True)
class PolicyResult:
    verdict: Verdict
    checks: dict[str, bool]
    reason: str


class AdmissionPolicy:
    """Constitutional admission policy.

    Autonomy is continuous but bounded: the runtime may sense, relate,
    interpret, project, and reopen on its own, while irreversible source
    mutation and unsupported truth upgrades are prohibited.
    """

    def __init__(self, config: RuntimeConfig):
        self.config = config

    def evaluate(
        self,
        candidate: dict[str, Any],
        interpretation: dict[str, Any],
        source: dict[str, Any],
        target: dict[str, Any],
    ) -> PolicyResult:
        source_keys = {str(item["key"]) for item in source["operator_path"]}
        target_keys = {str(item["key"]) for item in target["operator_path"]}
        preserved = set(interpretation["preserved_structure"])

        checks = {
            "SOURCE_REVERSIBLE": interpretation["reverse_path"] == [source["id"], target["id"]],
            "SYMBOL_PRESERVING": True,
            "OPERATOR_PATH_EXPLICIT": bool(interpretation["source_operator_path"] or interpretation["target_operator_path"]),
            "VARIANTS_NOT_SILENTLY_NORMALIZED": bool(interpretation["omitted_or_hidden_structure"]),
            "STATUS_EXPLICIT": bool(interpretation["status"]),
            "AFFECTED_PERSPECTIVES_RETAINED": bool(interpretation["affected_perspectives"]),
            "FORMAL_SCOPE_EXPLICIT": bool(interpretation["formal_scope"]),
            "EMPIRICAL_SCOPE_EXPLICIT": bool(interpretation["empirical_scope"]),
            "REOPENING_AVAILABLE": bool(interpretation["reopening"]),
            "NO_TURING_COMPLETENESS_ASSUMPTION": not self.config.turing_complete_assumed,
        }

        if not (source["exact_symbols"] or target["exact_symbols"]):
            checks["SYMBOL_PRESERVING"] = True
        else:
            checks["SYMBOL_PRESERVING"] = preserved.issuperset(source_keys & target_keys)

        critical = [
            "SOURCE_REVERSIBLE",
            "STATUS_EXPLICIT",
            "AFFECTED_PERSPECTIVES_RETAINED",
            "FORMAL_SCOPE_EXPLICIT",
            "EMPIRICAL_SCOPE_EXPLICIT",
            "REOPENING_AVAILABLE",
            "NO_TURING_COMPLETENESS_ASSUMPTION",
        ]
        failed_critical = [key for key in critical if not checks[key]]
        relation_type = RelationType(candidate["relation_type"])

        if failed_critical:
            return PolicyResult(Verdict.FALSE, checks, f"Critical admissibility checks failed: {', '.join(failed_critical)}")
        if relation_type == RelationType.CONTRADICTS:
            return PolicyResult(Verdict.FALSE, checks, "The configured translation is explicitly contradictory")
        if relation_type == RelationType.SAME_LITERAL_EQUATION and source["exact_text"] == target["exact_text"]:
            return PolicyResult(Verdict.TRUE, checks, "Exact source-preserving duplicate; no semantic upgrade was required")
        if relation_type == RelationType.SAME_OPERATOR_PATH and self.config.auto_admit_same_operator_path:
            return PolicyResult(Verdict.TRUE, checks, "Operator-path auto-admission is enabled by the active rule configuration")
        return PolicyResult(
            Verdict.OPEN,
            checks,
            "The relation is coherent enough to retain, but autonomous interpretation does not establish full identity; author confirmation, proof, or evidence may close it",
        )
