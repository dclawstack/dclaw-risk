"""Tests for the AI Copilot endpoint, with a stubbed LLM provider."""

import pytest

from app.services.llm import MockProvider, set_llm_for_testing


@pytest.fixture(autouse=True)
def use_mock_llm():
    set_llm_for_testing(MockProvider())
    yield


@pytest.mark.asyncio
async def test_risk_chat_returns_provider(client):
    res = await client.post(
        "/api/v1/ai/risk-chat",
        json={"messages": [{"role": "user", "content": "What are my top risks?"}]},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["provider"] == "mock"
    assert isinstance(body["reply"], str)
    assert isinstance(body["suggested_actions"], list)


@pytest.mark.asyncio
async def test_identify_risks_returns_baseline(client):
    res = await client.post(
        "/api/v1/ai/identify-risks",
        json={"context": "Migrating ERP to cloud", "count": 3},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["provider"] == "mock"
    assert len(body["risks"]) == 3
    for r in body["risks"]:
        assert 1 <= r["severity"] <= 5
        assert 1 <= r["probability"] <= 5


@pytest.mark.asyncio
async def test_classify_risk_returns_fallback(client):
    res = await client.post(
        "/api/v1/ai/classify-risk",
        json={"name": "Vendor data leak", "description": "third-party SaaS"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["provider"] == "mock"
    assert 1 <= body["severity"] <= 5
    assert 1 <= body["probability"] <= 5
