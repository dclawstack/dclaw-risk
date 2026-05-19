"""Integration tests for RAG retrieval + Copilot RAG augmentation + P1.4
mock-mode Compliance integration.
"""

import pytest

from app.services.llm import MockProvider, set_llm_for_testing


@pytest.fixture(autouse=True)
def use_mock_llm():
    set_llm_for_testing(MockProvider())
    yield


@pytest.mark.asyncio
async def test_document_crud_and_search(client):
    res = await client.post(
        "/api/v1/documents",
        json={
            "title": "Backup policy",
            "content": "All production databases are backed up nightly with seven-day retention.",
            "source": "internal-wiki",
        },
    )
    assert res.status_code == 201, res.text

    res = await client.post(
        "/api/v1/documents",
        json={
            "title": "Incident response runbook",
            "content": "On a Sev-1 cloud outage, escalate to the on-call SRE and engage the incident commander.",
        },
    )
    assert res.status_code == 201

    res = await client.get("/api/v1/documents")
    assert res.json()["total"] == 2

    res = await client.get("/api/v1/documents/search?q=backup retention")
    assert res.status_code == 200, res.text
    hits = res.json()["hits"]
    assert len(hits) >= 1
    assert "Backup policy" == hits[0]["title"]

    res = await client.get("/api/v1/documents/search?q=cloud outage")
    hits = res.json()["hits"]
    assert hits[0]["title"] == "Incident response runbook"


@pytest.mark.asyncio
async def test_copilot_chat_uses_rag(client):
    """Ensure the Copilot's chat call doesn't crash when documents are present
    and that retrieved snippets do not break the response shape."""
    await client.post(
        "/api/v1/documents",
        json={
            "title": "Vendor onboarding",
            "content": "Critical vendors must complete a SIG questionnaire before contract.",
        },
    )
    res = await client.post(
        "/api/v1/ai/risk-chat",
        json={
            "messages": [{"role": "user", "content": "How do we onboard vendors?"}]
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["provider"] == "mock"
    assert isinstance(body["reply"], str)


@pytest.mark.asyncio
async def test_compliance_mock_mode_returns_unified_view(client):
    # Seed a couple of controls that match common requirement types
    await client.post(
        "/api/v1/controls",
        json={"name": "MFA on admin accounts", "control_type": "preventive"},
    )
    await client.post(
        "/api/v1/controls",
        json={"name": "SIEM log review", "control_type": "detective"},
    )

    res = await client.get("/api/v1/compliance/unified-view")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["mock"] is True
    assert body["totals"]["requirements"] > 0
    # At least some requirements should be covered by our two controls
    assert body["totals"]["covered"] > 0
    assert body["totals"]["uncovered"] > 0
    # Each row carries the framework + requirement
    sample = body["rows"][0]
    assert "framework" in sample
    assert "requirement" in sample
    assert "covered" in sample

    res = await client.post("/api/v1/compliance/sync")
    assert res.status_code == 200
    body = res.json()
    assert body["mock"] is True
    assert body["mock_acknowledged"] is True
