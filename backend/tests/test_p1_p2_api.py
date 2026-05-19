"""Integration tests for P1/P2 endpoints."""

import pytest

from app.services.llm import MockProvider, set_llm_for_testing


@pytest.fixture(autouse=True)
def use_mock_llm():
    set_llm_for_testing(MockProvider())
    yield


@pytest.mark.asyncio
async def test_kri_lifecycle_and_breach_status(client):
    res = await client.post(
        "/api/v1/kris",
        json={
            "name": "Failed logins per hour",
            "unit": "count",
            "current_value": 150,
            "threshold_warn": 100,
            "threshold_critical": 200,
            "direction": "above",
        },
    )
    assert res.status_code == 201, res.text
    kri = res.json()
    assert kri["status"] == "warn"

    res = await client.patch(
        f"/api/v1/kris/{kri['id']}", json={"current_value": 250}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "critical"

    res = await client.get("/api/v1/kris/breaches")
    assert res.status_code == 200
    body = res.json()
    assert body["critical"] == 1
    assert body["warn"] == 0
    assert body["total"] == 1


@pytest.mark.asyncio
async def test_incident_crud_and_patterns(client):
    res = await client.post(
        "/api/v1/incidents",
        json={"title": "CDN outage", "severity": 4},
    )
    assert res.status_code == 201, res.text
    res = await client.post(
        "/api/v1/incidents",
        json={"title": "Repeated CDN slowdown", "severity": 3},
    )
    assert res.status_code == 201

    res = await client.get("/api/v1/incidents")
    assert res.json()["total"] == 2

    res = await client.get("/api/v1/incidents/patterns")
    assert res.status_code == 200
    body = res.json()
    assert body["count_analysed"] == 2
    assert body["provider"] == "mock"


@pytest.mark.asyncio
async def test_scenario_create_and_stress_test(client):
    # Need at least one risk to stress
    risk_id = (
        await client.post(
            "/api/v1/risks",
            json={
                "name": "FX exposure",
                "category": "Financial",
                "severity": 3,
                "probability": 3,
            },
        )
    ).json()["id"]

    res = await client.post(
        "/api/v1/scenarios",
        json={
            "name": "Severe recession",
            "multipliers": {
                "Financial": {"severity": 1.5, "probability": 1.4},
                "Operational": {"severity": 1.2, "probability": 1.0},
            },
        },
    )
    assert res.status_code == 201, res.text
    scenario_id = res.json()["id"]

    res = await client.post(f"/api/v1/scenarios/{scenario_id}/stress-test")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["baseline_total"] == 9  # 3*3
    assert body["projected_total"] > 9  # multipliers > 1 → bigger
    assert len(body["rows"]) == 1
    row = body["rows"][0]
    assert row["risk_id"] == risk_id


@pytest.mark.asyncio
async def test_vendor_lifecycle(client):
    res = await client.post(
        "/api/v1/vendors",
        json={"name": "Acme SaaS", "category": "SaaS", "criticality": 4},
    )
    assert res.status_code == 201, res.text
    vid = res.json()["id"]

    res = await client.post(f"/api/v1/vendors/{vid}/ai-score")
    assert res.status_code == 200, res.text
    body = res.json()
    assert 0 <= body["score"] <= 100
    assert body["last_assessed_at"] is not None


@pytest.mark.asyncio
async def test_reports_summary_and_exposure(client):
    # Empty case
    res = await client.get("/api/v1/reports/summary")
    assert res.status_code == 200, res.text
    assert res.json()["total_risks"] == 0

    # Create + populate
    rid = (
        await client.post(
            "/api/v1/risks",
            json={"name": "A", "category": "Operational", "severity": 4, "probability": 3},
        )
    ).json()["id"]
    cid = (
        await client.post(
            "/api/v1/controls", json={"name": "Ctl", "control_type": "preventive"}
        )
    ).json()["id"]
    await client.post(
        f"/api/v1/risks/{rid}/controls",
        json={"control_id": cid, "effectiveness": 4},
    )
    await client.post(
        f"/api/v1/risks/{rid}/assessments/quantitative",
        json={
            "kind": "quantitative",
            "loss_min": 100,
            "loss_mode": 1000,
            "loss_max": 10000,
            "freq_min": 0.1,
            "freq_max": 1.0,
            "iterations": 500,
        },
    )

    s = (await client.get("/api/v1/reports/summary")).json()
    assert s["total_risks"] == 1
    assert s["control_coverage_pct"] == 100.0

    e = (await client.get("/api/v1/reports/exposure")).json()
    assert e["risks_with_quantitative"] == 1
    assert e["total_p90"] > 0


@pytest.mark.asyncio
async def test_gap_analysis(client):
    # Uncovered risk
    await client.post(
        "/api/v1/risks", json={"name": "Lonely risk", "category": "Operational"}
    )
    # Unused control
    await client.post(
        "/api/v1/controls",
        json={"name": "Lonely control", "control_type": "detective"},
    )

    res = await client.get("/api/v1/controls/gap-analysis")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["totals"]["uncovered_risks"] == 1
    assert body["totals"]["unused_controls"] == 1


@pytest.mark.asyncio
async def test_risk_trend(client):
    rid = (
        await client.post(
            "/api/v1/risks",
            json={"name": "Trended", "category": "Operational"},
        )
    ).json()["id"]
    # Two qualitative assessments → expect 2 trend points
    for sev in (2, 4):
        await client.post(
            f"/api/v1/risks/{rid}/assessments/qualitative",
            json={"kind": "qualitative", "severity": sev, "probability": 3},
        )
    res = await client.get(f"/api/v1/risks/{rid}/trend")
    assert res.status_code == 200, res.text
    body = res.json()
    assert len(body["qualitative"]) == 2
