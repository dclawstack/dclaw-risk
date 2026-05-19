"""Integration tests for the risk register API."""

import pytest


@pytest.mark.asyncio
async def test_risk_crud(client):
    # initial list is empty
    res = await client.get("/api/v1/risks")
    assert res.status_code == 200
    assert res.json() == {"items": [], "total": 0}

    # create
    payload = {
        "name": "Cloud provider outage",
        "category": "Operational",
        "severity": 4,
        "probability": 3,
    }
    res = await client.post("/api/v1/risks", json=payload)
    assert res.status_code == 201, res.text
    created = res.json()
    assert created["name"] == "Cloud provider outage"
    assert created["score"] == 12
    risk_id = created["id"]

    # get
    res = await client.get(f"/api/v1/risks/{risk_id}")
    assert res.status_code == 200
    assert res.json()["id"] == risk_id

    # update
    res = await client.patch(
        f"/api/v1/risks/{risk_id}", json={"severity": 5, "status": "assessed"}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["severity"] == 5
    assert body["status"] == "assessed"
    assert body["score"] == 15

    # filter
    res = await client.get("/api/v1/risks?status=assessed")
    assert res.status_code == 200
    assert res.json()["total"] == 1

    # delete
    res = await client.delete(f"/api/v1/risks/{risk_id}")
    assert res.status_code == 204
    res = await client.get(f"/api/v1/risks/{risk_id}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_qualitative_assessment(client):
    res = await client.post(
        "/api/v1/risks",
        json={"name": "Data leak", "category": "Cybersecurity"},
    )
    risk_id = res.json()["id"]

    res = await client.post(
        f"/api/v1/risks/{risk_id}/assessments/qualitative",
        json={"kind": "qualitative", "severity": 5, "probability": 4},
    )
    assert res.status_code == 201, res.text
    assert res.json()["severity"] == 5

    # risk should now be "assessed"
    risk = (await client.get(f"/api/v1/risks/{risk_id}")).json()
    assert risk["status"] == "assessed"
    assert risk["severity"] == 5
    assert risk["probability"] == 4


@pytest.mark.asyncio
async def test_quantitative_assessment_returns_curve(client):
    res = await client.post(
        "/api/v1/risks",
        json={"name": "FX volatility", "category": "Financial"},
    )
    risk_id = res.json()["id"]

    res = await client.post(
        f"/api/v1/risks/{risk_id}/assessments/quantitative",
        json={
            "kind": "quantitative",
            "loss_min": 1000,
            "loss_mode": 10000,
            "loss_max": 100000,
            "freq_min": 0.1,
            "freq_max": 1.0,
            "iterations": 1000,
        },
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["loss_p10"] <= body["loss_p50"] <= body["loss_p90"]
    assert isinstance(body["curve"], list)
    assert len(body["curve"]) > 10


@pytest.mark.asyncio
async def test_control_mapping(client):
    risk_id = (
        await client.post(
            "/api/v1/risks",
            json={"name": "Insider threat", "category": "Cybersecurity"},
        )
    ).json()["id"]
    control_id = (
        await client.post(
            "/api/v1/controls",
            json={"name": "DLP scanning", "control_type": "detective"},
        )
    ).json()["id"]

    res = await client.post(
        f"/api/v1/risks/{risk_id}/controls",
        json={"control_id": control_id, "effectiveness": 4},
    )
    assert res.status_code == 201, res.text
    mapped = res.json()
    assert len(mapped) == 1
    assert mapped[0]["id"] == control_id

    res = await client.get(f"/api/v1/risks/{risk_id}/controls")
    assert res.status_code == 200
    assert len(res.json()) == 1

    res = await client.delete(f"/api/v1/risks/{risk_id}/controls/{control_id}")
    assert res.status_code == 204
    assert (await client.get(f"/api/v1/risks/{risk_id}/controls")).json() == []
