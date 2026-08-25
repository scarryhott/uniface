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
from .models import OccurrenceCreate, RuntimeCycleResult, RuntimeStatus
from .policy import AdmissionPolicy
from .providers import build_provider
from .projection import build_projection
from .store import EventStore


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


class ClosureSupernetRuntime:
    """Autonomous but bounded Closure Supernet.

    It continuously senses source occurrences, proposes relations, builds
    source-reversible interpretations, applies constitutional admission rules,
    projects current topology, and reopens incomplete relations. It never
    mutates an original occurrence and never assumes terminal closure.
    """

    def __init__(self, config: RuntimeConfig | None = None):
        self.config = config or RuntimeConfig()
        self.config.ensure_directories()
        self.store = EventStore(self.config.database_path)
        self.provider = build_provider(self.config)
        self.inbox = InboxSensorAgent(self.config, self.store)
        self.understanding = UnderstandingAgent(self.config, self.store)
        self.interpretation = InterpretationAgent(self.store, self.provider)
        self.admission = AdmissionAgent(self.store, AdmissionPolicy(self.config))
        self.reopening = ReopeningAgent(self.store)
        self.moral_audit = MoralAuditAgent(self.store)
        self.rule_review = RuleReviewAgent(self.config, self.store)
        self.projection = ProjectionAgent(self.store)
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()
        self._cycle_lock = asyncio.Lock()

    async def ingest(self, data: OccurrenceCreate) -> dict[str, Any]:
        path = extract_operator_path(data.exact_text)
        symbols = extract_exact_symbols(data.exact_text, path)
        occurrence = self.store.create_occurrence(data, symbols, path)
        return occurrence

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
            result = RuntimeCycleResult(cycle_id=cycle_id, started_at=started_at, finished_at=started_at)
            result.ingested = self.inbox.run()
            result.candidates = self.understanding.run()
            result.interpretations = await self.interpretation.run()
            result.admissions = self.admission.run()
            result.open_seams = self.reopening.run() + self.moral_audit.run()
            result.rule_proposals = self.rule_review.run()
            projection = self.projection.run()
            result.projection_classes = len(projection["classes"])
            result.projection_edges = len(projection["edges"])
            result.finished_at = utcnow()
            cycle_count = int(self.store.get_state("cycle_count", 0)) + 1
            self.store.set_state("cycle_count", cycle_count)
            self.store.set_state("last_cycle", result.model_dump(mode="json"))
            self.store.append_event("RUNTIME_CYCLE_FINISHED", "runtime_cycle", cycle_id, result.model_dump(mode="json"))
            return result

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._stop.clear()
        if self.config.bootstrap_repository:
            await self.bootstrap_markdown()
        self._task = asyncio.create_task(self._run_loop(), name="closure-supernet-autonomy")
        self.store.append_event("AUTONOMY_STARTED", "runtime", "closure-supernet", {"interval": self.config.autonomy_interval_seconds})

    async def _run_loop(self) -> None:
        while not self._stop.is_set():
            try:
                await self.cycle()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.store.append_event("AUTONOMY_ERROR", "runtime", "closure-supernet", {"type": type(exc).__name__, "message": str(exc)})
                self.store.create_open_seam(None, None, f"Autonomous cycle error: {type(exc).__name__}: {exc}", {"runtime": True})
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.config.autonomy_interval_seconds)
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
        return RuntimeStatus(
            running=self._running,
            cycle_count=int(self.store.get_state("cycle_count", 0)),
            last_cycle=self.store.get_state("last_cycle"),
            autonomy_interval_seconds=self.config.autonomy_interval_seconds,
            llm_mode=self.config.llm_mode,
            turing_complete_assumed=False,
        )

    def black_mirror(self) -> dict[str, Any]:
        projection = self.store.get_state("black_mirror_projection")
        if projection is None:
            projection = build_projection(self.store).model_dump(mode="json")
        return projection

    def close(self) -> None:
        self.store.close()
