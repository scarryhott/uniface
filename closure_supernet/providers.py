from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import httpx

from .config import RuntimeConfig


class InterpretationProvider(ABC):
    name = "provider"

    @abstractmethod
    async def interpret(self, source: dict[str, Any], target: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any] | None:
        raise NotImplementedError


class NoopProvider(InterpretationProvider):
    name = "deterministic"

    async def interpret(self, source: dict[str, Any], target: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any] | None:
        return None


class OpenAICompatibleProvider(InterpretationProvider):
    """Optional OpenAI-compatible interpretation provider.

    The provider is a derived chart. Its response never overwrites sources and
    remains subject to the same admission policy as deterministic witnesses.
    """

    name = "openai-compatible"

    def __init__(self, config: RuntimeConfig):
        if not config.llm_api_key:
            raise ValueError("CLOSURE_LLM_API_KEY or OPENAI_API_KEY is required")
        self.base_url = config.llm_base_url.rstrip("/")
        self.api_key = config.llm_api_key
        self.model = config.llm_model
        self.timeout = config.request_timeout_seconds

    async def interpret(self, source: dict[str, Any], target: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any] | None:
        system = (
            "You are an interpretation assistant inside a source-preserving closure supernetwork. "
            "Do not normalize the author's notation. Return JSON only with keys preserved_structure, "
            "transformed_structure, omitted_or_hidden_structure, frame_and_scope, affected_perspectives, "
            "formal_scope, empirical_scope, reopening. Treat uncertain equivalence as OPEN."
        )
        user = {
            "candidate": candidate,
            "source": {"id": source["id"], "exact_text": source["exact_text"], "operator_path": source["operator_path"]},
            "target": {"id": target["id"], "exact_text": target["exact_text"], "operator_path": target["operator_path"]},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)


def build_provider(config: RuntimeConfig) -> InterpretationProvider:
    if config.llm_mode.casefold() in {"compatible", "openai", "on"}:
        return OpenAICompatibleProvider(config)
    return NoopProvider()
