from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class RuntimeConfig:
    database_path: Path = Path(os.getenv("CLOSURE_DB_PATH", "runtime_data/closure_supernet.db"))
    inbox_dir: Path = Path(os.getenv("CLOSURE_INBOX_DIR", "runtime_data/inbox"))
    autonomy_enabled: bool = _bool("CLOSURE_AUTONOMY_ENABLED", True)
    autonomy_interval_seconds: float = float(os.getenv("CLOSURE_AUTONOMY_INTERVAL_SECONDS", "5"))
    bootstrap_repository: bool = _bool("CLOSURE_BOOTSTRAP_REPOSITORY", False)
    bootstrap_root: Path = Path(os.getenv("CLOSURE_BOOTSTRAP_ROOT", "."))
    max_candidates_per_occurrence: int = int(os.getenv("CLOSURE_MAX_CANDIDATES", "8"))
    semantic_threshold: float = float(os.getenv("CLOSURE_SEMANTIC_THRESHOLD", "0.24"))
    auto_admit_same_operator_path: bool = _bool("CLOSURE_AUTO_ADMIT_OPERATOR_PATH", False)
    auto_activate_rule_proposals: bool = _bool("CLOSURE_AUTO_ACTIVATE_RULES", False)
    llm_mode: str = os.getenv("CLOSURE_LLM_MODE", "off")
    llm_base_url: str = os.getenv("CLOSURE_LLM_BASE_URL", "https://api.openai.com/v1")
    llm_api_key: str | None = os.getenv("CLOSURE_LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    llm_model: str = os.getenv("CLOSURE_LLM_MODEL", "gpt-5-mini")
    request_timeout_seconds: float = float(os.getenv("CLOSURE_LLM_TIMEOUT_SECONDS", "45"))

    # The field is deliberately not assumed Turing complete. Digital computation
    # is one derived chart and local halts reopen into later runtime cycles.
    turing_complete_assumed: bool = False

    def ensure_directories(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
