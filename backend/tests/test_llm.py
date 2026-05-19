"""Tests for the LLM provider abstraction.

Mostly checks the fallback chain logic with stand-in providers — no real LLM
calls. The actual OllamaProvider / OpenRouterProvider are integration-only and
not exercised here.
"""

import pytest

from app.services.llm import FallbackProvider, Message, MockProvider


class FailingProvider:
    name = "failing"

    async def chat(self, messages):  # noqa: ARG002
        raise RuntimeError("intentional")


@pytest.mark.asyncio
async def test_mock_provider_echoes_user_text():
    mock = MockProvider()
    reply = await mock.chat([Message(role="user", content="hello world")])
    assert "hello world" in reply


@pytest.mark.asyncio
async def test_fallback_uses_first_success():
    chain = FallbackProvider([FailingProvider(), MockProvider()])
    reply = await chain.chat([Message(role="user", content="abc")])
    assert "abc" in reply


@pytest.mark.asyncio
async def test_fallback_raises_when_all_fail():
    chain = FallbackProvider([FailingProvider(), FailingProvider()])
    with pytest.raises(RuntimeError):
        await chain.chat([Message(role="user", content="x")])
