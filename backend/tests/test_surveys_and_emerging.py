"""Integration tests for P2.1 emerging-risk feed and P2.2 survey workflow."""

import pytest

from app.services.llm import MockProvider, set_llm_for_testing


@pytest.fixture(autouse=True)
def use_mock_llm():
    set_llm_for_testing(MockProvider())
    yield


@pytest.mark.asyncio
async def test_survey_workflow_aggregates_into_culture_scores(client):
    res = await client.post(
        "/api/v1/culture/surveys",
        json={
            "name": "Q2 culture pulse",
            "period": "2026-Q2",
            "questions": [
                {"dimension": "Speak-up", "prompt": "I feel safe raising concerns."},
                {"dimension": "Speak-up", "prompt": "Feedback is taken seriously."},
                {
                    "dimension": "Tone-at-top",
                    "prompt": "Leadership models risk-aware behaviour.",
                },
            ],
        },
    )
    assert res.status_code == 201, res.text
    survey_id = res.json()["id"]

    surveys = (await client.get("/api/v1/culture/surveys")).json()["items"]
    survey = next(s for s in surveys if s["id"] == survey_id)
    q_by_dim: dict[str, list[str]] = {}
    for q in survey["questions"]:
        q_by_dim.setdefault(q["dimension"], []).append(q["id"])

    # Submit while still draft → 400
    res = await client.post(
        f"/api/v1/culture/surveys/{survey_id}/responses",
        json={
            "answers": [
                {"question_id": q_by_dim["Speak-up"][0], "score": 70}
            ]
        },
    )
    assert res.status_code == 400

    await client.post(f"/api/v1/culture/surveys/{survey_id}/open")

    # Two respondents
    for r in (
        {"Speak-up": [80, 70], "Tone-at-top": [60]},
        {"Speak-up": [90, 60], "Tone-at-top": [80]},
    ):
        answers: list[dict] = []
        for dim, scores in r.items():
            for qid, s in zip(q_by_dim[dim], scores, strict=True):
                answers.append({"question_id": qid, "score": s})
        res = await client.post(
            f"/api/v1/culture/surveys/{survey_id}/responses",
            json={"answers": answers},
        )
        assert res.status_code == 201, res.text

    res = await client.post(f"/api/v1/culture/surveys/{survey_id}/close")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["status"] == "closed"
    assert body["dimensions_scored"] == 2
    assert body["responses_total"] == 6  # 2 respondents × 3 questions

    scores = (await client.get("/api/v1/culture")).json()["items"]
    by_dim = {s["dimension"]: s for s in scores}
    # Speak-up answers: 80,70,90,60 → mean 75
    assert by_dim["Speak-up"]["score"] == 75
    # Tone-at-top: 60,80 → mean 70
    assert by_dim["Tone-at-top"]["score"] == 70


@pytest.mark.asyncio
async def test_emerging_synthetic_feed_dedupes(client):
    res = await client.post("/api/v1/emerging/refresh?feed=synthetic&limit=3")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["fetched"] == 3
    assert body["new"] == 3

    # Re-run is idempotent for the synthetic feed
    res = await client.post("/api/v1/emerging/refresh?feed=synthetic&limit=3")
    body = res.json()
    assert body["new"] == 0

    res = await client.get("/api/v1/emerging")
    assert res.json()["total"] == 3
    assert "synthetic" in res.json()["feeds"]
    assert "nvd-cve" in res.json()["feeds"]


@pytest.mark.asyncio
async def test_emerging_rejects_unknown_feed(client):
    res = await client.post("/api/v1/emerging/refresh?feed=does-not-exist")
    assert res.status_code == 400
