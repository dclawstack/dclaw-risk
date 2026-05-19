"""LLM provider abstraction.

Default: Ollama (local). Fallback: OpenRouter (cloud).
Falls back when the default provider raises any exception so a developer can
demo this offline (Ollama running) or online (OPENROUTER_API_KEY set) without
code changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

import httpx
import structlog

from app.core.config import settings

log = structlog.get_logger(__name__)

Role = Literal["system", "user", "assistant"]


@dataclass
class Message:
    role: Role
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


class LLMProvider(Protocol):
    name: str

    async def chat(self, messages: list[Message]) -> str: ...


class OllamaProvider:
    name = "ollama"

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.llm_request_timeout_s

    async def chat(self, messages: list[Message]) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data.get("message", {}).get("content", "").strip()


class OpenRouterProvider:
    name = "openrouter"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model or settings.openrouter_model
        self.base_url = (base_url or settings.openrouter_base_url).rstrip("/")
        self.timeout = timeout or settings.llm_request_timeout_s

    async def chat(self, messages: list[Message]) -> str:
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


class MockProvider:
    """Deterministic provider used in tests and when no real provider works."""

    name = "mock"

    async def chat(self, messages: list[Message]) -> str:
        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        )
        return f"[mock-llm] echo: {last_user[:200]}"


class FallbackProvider:
    """Tries providers in order; returns the first successful response."""

    def __init__(self, providers: list[LLMProvider]) -> None:
        if not providers:
            raise ValueError("at least one provider required")
        self.providers = providers

    @property
    def name(self) -> str:
        return "+".join(p.name for p in self.providers)

    async def chat(self, messages: list[Message]) -> str:
        last_err: Exception | None = None
        for provider in self.providers:
            try:
                return await provider.chat(messages)
            except Exception as e:
                log.warning(
                    "llm.provider_failed", provider=provider.name, error=str(e)
                )
                last_err = e
        raise RuntimeError(
            f"all LLM providers failed; last error: {last_err}"
        ) from last_err


def build_default_provider() -> LLMProvider:
    """Construct the production fallback chain.

    Order: Ollama → OpenRouter (if API key set) → Mock.
    Mock is included so the API stays usable in environments without LLMs.
    """
    chain: list[LLMProvider] = [OllamaProvider()]
    if settings.openrouter_api_key:
        chain.append(OpenRouterProvider())
    chain.append(MockProvider())
    return FallbackProvider(chain)


_default: LLMProvider | None = None


def get_llm() -> LLMProvider:
    global _default
    if _default is None:
        _default = build_default_provider()
    return _default


def set_llm_for_testing(provider: LLMProvider) -> None:
    global _default
    _default = provider
