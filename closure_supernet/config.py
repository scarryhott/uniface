from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _csv(name: str, default: str = "") -> tuple[str, ...]:
    value = os.getenv(name, default)
    return tuple(item.strip() for item in value.split(",") if item.strip())


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

    integration_http_timeout_seconds: float = float(
        os.getenv("CLOSURE_INTEGRATION_HTTP_TIMEOUT_SECONDS", "30")
    )
    integration_max_items_per_cycle: int = int(
        os.getenv("CLOSURE_INTEGRATION_MAX_ITEMS", "500")
    )
    integration_user_agent: str = os.getenv(
        "CLOSURE_INTEGRATION_USER_AGENT", "closure-supernet/2.1"
    )
    integration_allow_private_networks: bool = _bool(
        "CLOSURE_INTEGRATION_ALLOW_PRIVATE_NETWORKS", False
    )

    public_interface_enabled: bool = _bool("CLOSURE_PUBLIC_INTERFACE_ENABLED", True)
    public_development_mode: bool = _bool("CLOSURE_PUBLIC_DEVELOPMENT_MODE", True)
    agentic_reintegration_enabled: bool = _bool(
        "CLOSURE_AGENTIC_REINTEGRATION_ENABLED", True
    )
    public_default_visibility: str = os.getenv(
        "CLOSURE_PUBLIC_DEFAULT_VISIBILITY", "PUBLIC"
    )

    iterated_reopening_enabled: bool = _bool(
        "CLOSURE_ITERATED_REOPENING_ENABLED", True
    )
    reopening_processes_per_cycle: int = int(
        os.getenv("CLOSURE_REOPENING_PROCESSES_PER_CYCLE", "16")
    )
    reopening_powerset_limit: int = int(
        os.getenv("CLOSURE_REOPENING_POWERSET_LIMIT", "10")
    )

    translation_field_enabled: bool = _bool(
        "CLOSURE_TRANSLATION_FIELD_ENABLED", True
    )

    resource_protocol_enabled: bool = _bool(
        "CLOSURE_RESOURCE_PROTOCOL_ENABLED", True
    )
    resource_reintegrations_per_cycle: int = int(
        os.getenv("CLOSURE_RESOURCE_REINTEGRATIONS_PER_CYCLE", "32")
    )
    resource_stages_retained: int = int(
        os.getenv("CLOSURE_RESOURCE_STAGES_RETAINED", "1000")
    )

    relative_equality_enabled: bool = _bool(
        "CLOSURE_RELATIVE_EQUALITY_ENABLED", True
    )
    equality_translation_scan_limit: int = int(
        os.getenv("CLOSURE_EQUALITY_TRANSLATION_SCAN_LIMIT", "2000")
    )
    equality_pairs_per_cycle: int = int(
        os.getenv("CLOSURE_EQUALITY_PAIRS_PER_CYCLE", "128")
    )

    hardware_closure_enabled: bool = _bool(
        "CLOSURE_HARDWARE_CLOSURE_ENABLED", True
    )
    hardware_reintegrations_per_cycle: int = int(
        os.getenv("CLOSURE_HARDWARE_REINTEGRATIONS_PER_CYCLE", "16")
    )
    hardware_constraint_ttl_seconds: int = int(
        os.getenv("CLOSURE_HARDWARE_CONSTRAINT_TTL_SECONDS", "3600")
    )
    hardware_auto_synthesize: bool = _bool(
        "CLOSURE_HARDWARE_AUTO_SYNTHESIZE", False
    )
    hardware_simulation_only: bool = True
    hardware_allow_direct_physical_actuation: bool = False

    # NRRF780 is an evaluator/simulator lens. No environment variable can
    # enable brokerage connectivity or direct market-order execution.
    trading_enabled: bool = _bool("CLOSURE_TRADING_ENABLED", True)
    trading_simulation_only: bool = True
    trading_allow_direct_market_execution: bool = False
    trading_brokerage_connected: bool = False

    environment: str = os.getenv("CLOSURE_ENVIRONMENT", "development").strip().lower()
    service_role: str = os.getenv("CLOSURE_SERVICE_ROLE", "all").strip().lower()
    public_base_url: str | None = os.getenv("CLOSURE_PUBLIC_BASE_URL") or None
    auth_mode: str = os.getenv("CLOSURE_AUTH_MODE", "open").strip().lower()
    auth_api_keys_json: str = os.getenv("CLOSURE_AUTH_API_KEYS_JSON", "{}")
    auth_jwt_secret: str | None = os.getenv("CLOSURE_AUTH_JWT_SECRET") or None
    auth_jwks_url: str | None = os.getenv("CLOSURE_AUTH_JWKS_URL") or None
    auth_issuer: str | None = os.getenv("CLOSURE_AUTH_ISSUER") or None
    auth_audience: str | None = os.getenv("CLOSURE_AUTH_AUDIENCE") or None
    auth_jwt_algorithms: tuple[str, ...] = _csv(
        "CLOSURE_AUTH_JWT_ALGORITHMS", "RS256,HS256"
    )
    session_secret: str | None = os.getenv("CLOSURE_SESSION_SECRET") or None
    session_ttl_seconds: int = int(os.getenv("CLOSURE_SESSION_TTL_SECONDS", "43200"))
    allow_anonymous_read: bool = _bool("CLOSURE_ALLOW_ANONYMOUS_READ", True)
    allow_anonymous_write: bool = _bool("CLOSURE_ALLOW_ANONYMOUS_WRITE", False)
    allow_self_registration: bool = _bool("CLOSURE_ALLOW_SELF_REGISTRATION", False)
    public_only_mode: bool = _bool("CLOSURE_PUBLIC_ONLY_MODE", True)
    trusted_hosts: tuple[str, ...] = _csv(
        "CLOSURE_TRUSTED_HOSTS", "localhost,127.0.0.1,testserver"
    )
    cors_origins: tuple[str, ...] = _csv("CLOSURE_CORS_ORIGINS", "")
    rate_limit_read_per_minute: int = int(
        os.getenv("CLOSURE_RATE_LIMIT_READ_PER_MINUTE", "300")
    )
    rate_limit_write_per_minute: int = int(
        os.getenv("CLOSURE_RATE_LIMIT_WRITE_PER_MINUTE", "60")
    )
    max_request_bytes: int = int(os.getenv("CLOSURE_MAX_REQUEST_BYTES", "2097152"))
    content_security_policy: str = os.getenv(
        "CLOSURE_CONTENT_SECURITY_POLICY",
        "default-src 'self'; connect-src 'self' ws: wss:; img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'",
    )
    backup_dir: Path = Path(os.getenv("CLOSURE_BACKUP_DIR", "runtime_data/backups"))
    backup_keep: int = int(os.getenv("CLOSURE_BACKUP_KEEP", "30"))

    turing_complete_assumed: bool = False

    def ensure_directories(self) -> None:
        if self.environment not in {"development", "test", "production"}:
            raise ValueError("CLOSURE_ENVIRONMENT must be development, test, or production")
        if self.service_role not in {"all", "web", "worker"}:
            raise ValueError("CLOSURE_SERVICE_ROLE must be all, web, or worker")
        if self.hardware_constraint_ttl_seconds < 1:
            raise ValueError("CLOSURE_HARDWARE_CONSTRAINT_TTL_SECONDS must be positive")
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
