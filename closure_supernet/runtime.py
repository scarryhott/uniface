from __future__ import annotations

import asyncio
import hashlib
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .agents import (
    AdmissionAgent,
    InboxSensorAgent,
    InterpretationAgent,
    MoralAuditAgent,
    ProjectionAgent,
    ReopeningAgent,
    RuleReviewAgent,
    UnderstandingAgent,
)
from .axiometry import extract_exact_symbols, extract_operator_path
from .config import RuntimeConfig
from .integration_store import IntegrationStore
from .integrations import DigitalIntegrationManager
from .living_network import LivingNetworkManager
from .living_store import LivingNetworkStore
from .models import OccurrenceCreate, RuntimeCycleResult, RuntimeStatus
from .policy import AdmissionPolicy
from .projection import build_projection
from .providers import build_provider
from .reopening_network import IteratedReopeningManager
from .reopening_store import ReopeningStore
from .store import EventStore


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


class ClosureSupernetRuntime:
    """Autonomous, bounded, living Closure Supernet.

    The runtime senses exact sources, public living interactions and configured
    digital interfaces; proposes and interprets relations; applies admission;
    reintegrates returned consequences; iterates admissible reopening families;
    projects current topology; and reopens incomplete relations. Original
    occurrences are never mutated and finite stability is never called a final
    moral core.
    """

    def __init__(self, config: RuntimeConfig | None = None):
        self.config = config or RuntimeConfig()
        self.config.ensure_directories()
        self.store = EventStore(self.config.database_path)
        self.integration_store = IntegrationStore(self.config.database_path)
        self.living_store = LivingNetworkStore(self.config.database_path)
        self.iterated_reopening_store = ReopeningStore(self.config.database_path)
        self.provider = build_provider(self.config)
        self.inbox = InboxSensorAgent(self.config, self.store)
        self.understanding = UnderstandingAgent(self.config, self.store)
        self.interpretation = InterpretationAgent(self.store, self.provider)
        self.admission = AdmissionAgent(self.store, AdmissionPolicy(self.config))
        self.reopening = ReopeningAgent(self.store)
        self.moral_audit = MoralAuditAgent(self.store)
        self.rule_review = RuleReviewAgent(self.config, self.store)
        self.projection = ProjectionAgent(self.store)
        self.integrations = DigitalIntegrationManager(
            self.config, self.store, self.integration_store, self.ingest
        )
        self.living = LivingNetworkManager(self.store, self.living_store, self.ingest)
        self.iterated_reopening = IteratedReopeningManager(
            self.config,
            self.store,
            self.living_store,
            self.iterated_reopening_store,
            self.ingest,
        )
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()
        self._cycle_lock = asyncio.Lock()

    async def ingest(self, data: OccurrenceCreate) -> dict[str, Any]:
        path = extract_operator_path(data.exact_text)
        symbols = extract_exact_symbols(data.exact_text, path)
        return self.store.create_occurrence(data, symbols, path)

    async def bootstrap_markdown(self, root: Path | None = None) -> int:
        root = Path(root or self.config.bootstrap_root)
        count = 0
        for path in sorted(root.rglob("*.md")):
            if any(part.startswith(".") for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
            source_location = str(path.resolve())
            if self.store.occurrence_exists_by_checksum(checksum, source_location):
                continue
            await self.ingest(
                OccurrenceCreate(
                    exact_text=text,
                    source_id="repository-bootstrap",
                    source_location=source_location,
                    source_context=f"Imported from {path.name}",
                    metadata={"bootstrap": True},
                )
            )
            count += 1
        return count

    async def cycle(self) -> RuntimeCycleResult:
        async with self._cycle_lock:
            cycle_id = str(uuid.uuid4())
            started_at = utcnow()
            self.store.append_event("RUNTIME_CYCLE_STARTED", "runtime_cycle", cycle_id, {})
            result = RuntimeCycleResult(
                cycle_id=cycle_id, started_at=started_at, finished_at=started_at
            )

            pull_runs = await self.integrations.poll_enabled()
            result.integration_pulled = sum(run.pulled for run in pull_runs)
            result.integration_runs = len(pull_runs)
            result.integration_errors = sum(run.errors for run in pull_runs)
            result.ingested = self.inbox.run() + result.integration_pulled

            if self.config.agentic_reintegration_enabled:
                result.living_reintegrations = self.living.reintegrate()
            if self.config.iterated_reopening_enabled:
                result.reopening_rounds = (
                    self.iterated_reopening.advance_active_processes(
                        self.config.reopening_processes_per_cycle
                    )
                )

            result.candidates = self.understanding.run()
            result.interpretations = await self.interpretation.run()
            result.admissions = self.admission.run()
            result.living_decisions_applied = self.living.apply_reintegration_decisions()
            result.open_seams = self.reopening.run() + self.moral_audit.run()
            result.rule_proposals = self.rule_review.run()

            projection = self.projection.run()
            result.projection_classes = len(projection["classes"])
            result.projection_edges = len(projection["edges"])

            reopening_projection = self.iterated_reopening.projection()
            reopening_stats = reopening_projection["stats"]
            result.reopening_families = int(reopening_stats["families"])
            result.reopening_processes = int(reopening_stats["processes"])
            result.reopening_active_processes = int(
                reopening_stats["active_processes"]
            )
            result.reopening_order_assessments = int(
                reopening_stats["order_assessments"]
            )
            result.reopening_moral_connections = int(
                reopening_stats["moral_connections"]
            )

            living_projection = self.living.field_projection(projection)
            living_projection["iterated_reopening"] = reopening_projection
            living_projection["stats"].update(
                {
                    "reopening_families": reopening_stats["families"],
                    "reopening_rounds": reopening_stats["rounds"],
                    "active_reopening_processes": reopening_stats[
                        "active_processes"
                    ],
                    "meaning_changing_reorders": reopening_stats[
                        "meaning_changing_reorders"
                    ],
                    "residue_moral_connections": reopening_stats[
                        "moral_connections"
                    ],
                    "final_core_state_available": False,
                }
            )
            living_projection["source_reverse_index"].update(
                reopening_projection["source_reverse_index"]
            )
            self.living_store.set_state("living_field_projection", living_projection)
            living_stats = living_projection["stats"]
            result.living_participants = int(living_stats["participants"])
            result.living_problems = int(living_stats["problems"])
            result.living_interactions = int(living_stats["interactions"])
            result.living_actions = int(living_stats["actions"])
            result.living_returns = int(living_stats["returns"])
            result.living_open_reintegration = int(
                living_stats["open_reintegration"]
            )

            push_runs = await self.integrations.push_enabled(
                {
                    **projection,
                    "living_field": {
                        "stats": living_projection["stats"],
                        "source_reverse_index": living_projection[
                            "source_reverse_index"
                        ],
                        "iterated_reopening": {
                            "stats": reopening_stats,
                            "source_reverse_index": reopening_projection[
                                "source_reverse_index"
                            ],
                        },
                        "nonterminal": True,
                    },
                }
            )
            result.integration_pushed = sum(run.pushed for run in push_runs)
            result.integration_runs += len(push_runs)
            result.integration_errors += sum(run.errors for run in push_runs)

            result.finished_at = utcnow()
            cycle_count = int(self.store.get_state("cycle_count", 0)) + 1
            self.store.set_state("cycle_count", cycle_count)
            self.store.set_state("last_cycle", result.model_dump(mode="json"))
            self.store.append_event(
                "RUNTIME_CYCLE_FINISHED",
                "runtime_cycle",
                cycle_id,
                result.model_dump(mode="json"),
            )
            return result

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._stop.clear()
        if self.config.bootstrap_repository:
            await self.bootstrap_markdown()
        self._task = asyncio.create_task(
            self._run_loop(), name="closure-supernet-autonomy"
        )
        self.store.append_event(
            "AUTONOMY_STARTED",
            "runtime",
            "closure-supernet",
            {"interval": self.config.autonomy_interval_seconds},
        )

    async def _run_loop(self) -> None:
        while not self._stop.is_set():
            try:
                await self.cycle()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.store.append_event(
                    "AUTONOMY_ERROR",
                    "runtime",
                    "closure-supernet",
                    {"type": type(exc).__name__, "message": str(exc)},
                )
                self.store.create_open_seam(
                    None,
                    None,
                    f"Autonomous cycle error: {type(exc).__name__}: {exc}",
                    {"runtime": True},
                )
            try:
                await asyncio.wait_for(
                    self._stop.wait(), timeout=self.config.autonomy_interval_seconds
                )
            except TimeoutError:
                continue

    async def stop(self) -> None:
        if not self._running:
            return
        self._stop.set()
        if self._task:
            await self._task
        self._task = None
        self._running = False
        self.store.append_event("AUTONOMY_STOPPED", "runtime", "closure-supernet", {})

    def status(self) -> RuntimeStatus:
        recent_runs = self.integration_store.list_runs(limit=1000)
        living_stats = self.living_store.stats()
        reintegration = self.living_store.list_reintegration_proposals(
            limit=100_000
        )
        reopening_stats = self.iterated_reopening_store.stats()
        return RuntimeStatus(
            running=self._running,
            cycle_count=int(self.store.get_state("cycle_count", 0)),
            last_cycle=self.store.get_state("last_cycle"),
            autonomy_interval_seconds=self.config.autonomy_interval_seconds,
            llm_mode=self.config.llm_mode,
            enabled_integrations=len(
                self.integration_store.list_integrations(enabled_only=True)
            ),
            integration_errors=sum(
                1 for row in recent_runs if row["status"] == "ERROR"
            ),
            living_participants=living_stats["participants"],
            living_problems=living_stats["problems"],
            living_actions=living_stats["actions"],
            living_open_reintegration=sum(
                1 for item in reintegration if item["current_status"] == "OPEN"
            ),
            reopening_families=reopening_stats["families"],
            reopening_rounds=reopening_stats["rounds"],
            reopening_active_processes=reopening_stats["active_processes"],
            reopening_order_assessments=reopening_stats["order_assessments"],
            reopening_moral_connections=reopening_stats["moral_connections"],
            public_interface_enabled=self.config.public_interface_enabled,
            agentic_reintegration_enabled=self.config.agentic_reintegration_enabled,
            iterated_reopening_enabled=self.config.iterated_reopening_enabled,
            turing_complete_assumed=False,
        )

    def black_mirror(self) -> dict[str, Any]:
        projection = self.store.get_state("black_mirror_projection")
        if projection is None:
            projection = build_projection(self.store).model_dump(mode="json")
        return projection

    def living_field(self) -> dict[str, Any]:
        projection = self.living_store.get_state("living_field_projection")
        if projection is None:
            projection = self.living.field_projection(self.black_mirror())
            reopening = self.iterated_reopening.projection()
            projection["iterated_reopening"] = reopening
            projection["stats"].update(
                {
                    "reopening_families": reopening["stats"]["families"],
                    "reopening_rounds": reopening["stats"]["rounds"],
                    "active_reopening_processes": reopening["stats"][
                        "active_processes"
                    ],
                    "meaning_changing_reorders": reopening["stats"][
                        "meaning_changing_reorders"
                    ],
                    "residue_moral_connections": reopening["stats"][
                        "moral_connections"
                    ],
                    "final_core_state_available": False,
                }
            )
            projection["source_reverse_index"].update(
                reopening["source_reverse_index"]
            )
        return projection

    def close(self) -> None:
        self.iterated_reopening_store.close()
        self.living_store.close()
        self.integration_store.close()
        self.store.close()
