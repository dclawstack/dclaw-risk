"""P2.2 Risk Culture — surveys, responses, and auto-aggregated scores."""

from collections import defaultdict
from statistics import mean
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models.culture import CultureScore
from app.models.survey import Survey, SurveyQuestion, SurveyResponse

router = APIRouter()


# ---- Aggregated scores (kept for backwards-compat with /culture from before) ----


class CultureScoreIn(BaseModel):
    period: str = Field(min_length=1, max_length=16)
    dimension: str = Field(min_length=1, max_length=64)
    score: int = Field(ge=0, le=100)
    benchmark: int | None = Field(default=None, ge=0, le=100)
    notes: str | None = None


@router.get("")
async def list_culture_scores(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    rows = (
        await db.execute(
            select(CultureScore).order_by(
                CultureScore.period.desc(), CultureScore.dimension.asc()
            )
        )
    ).scalars().all()
    return {
        "items": [
            {
                "id": str(r.id),
                "period": r.period,
                "dimension": r.dimension,
                "score": r.score,
                "benchmark": r.benchmark,
                "notes": r.notes,
            }
            for r in rows
        ]
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_culture_score(
    payload: CultureScoreIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    row = CultureScore(**payload.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {"id": str(row.id), "period": row.period, "dimension": row.dimension}


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_culture_score(
    score_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    row = (
        await db.execute(select(CultureScore).where(CultureScore.id == score_id))
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="culture score not found")
    await db.delete(row)
    await db.commit()


# ---- Surveys ---------------------------------------------------------------


class SurveyQuestionIn(BaseModel):
    dimension: str = Field(min_length=1, max_length=64)
    prompt: str = Field(min_length=1)
    order_index: int = 0


class SurveyIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    period: str = Field(min_length=1, max_length=16)
    description: str | None = None
    questions: list[SurveyQuestionIn] = Field(default_factory=list)


@router.post("/surveys", status_code=status.HTTP_201_CREATED)
async def create_survey(
    payload: SurveyIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    survey = Survey(
        name=payload.name, period=payload.period, description=payload.description
    )
    db.add(survey)
    await db.flush()
    for q in payload.questions:
        db.add(
            SurveyQuestion(
                survey_id=survey.id,
                dimension=q.dimension,
                prompt=q.prompt,
                order_index=q.order_index,
            )
        )
    await db.commit()
    return {"id": str(survey.id), "name": survey.name, "status": survey.status}


@router.get("/surveys")
async def list_surveys(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    rows = (await db.execute(select(Survey))).scalars().all()
    items = []
    for s in rows:
        qs = (
            await db.execute(
                select(SurveyQuestion)
                .where(SurveyQuestion.survey_id == s.id)
                .order_by(SurveyQuestion.order_index.asc())
            )
        ).scalars().all()
        items.append(
            {
                "id": str(s.id),
                "name": s.name,
                "period": s.period,
                "status": s.status,
                "questions": [
                    {
                        "id": str(q.id),
                        "dimension": q.dimension,
                        "prompt": q.prompt,
                        "order_index": q.order_index,
                    }
                    for q in qs
                ],
            }
        )
    return {"items": items}


@router.post("/surveys/{survey_id}/open")
async def open_survey(
    survey_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    survey = (
        await db.execute(select(Survey).where(Survey.id == survey_id))
    ).scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="survey not found")
    survey.status = "open"
    await db.commit()
    return {"id": str(survey.id), "status": survey.status}


class ResponseIn(BaseModel):
    question_id: UUID
    score: int = Field(ge=0, le=100)


class SubmitSurveyIn(BaseModel):
    respondent_hash: str | None = Field(default=None, max_length=64)
    answers: list[ResponseIn] = Field(min_length=1)


@router.post("/surveys/{survey_id}/responses", status_code=status.HTTP_201_CREATED)
async def submit_response(
    survey_id: UUID,
    payload: SubmitSurveyIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    survey = (
        await db.execute(select(Survey).where(Survey.id == survey_id))
    ).scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="survey not found")
    if survey.status != "open":
        raise HTTPException(
            status_code=400, detail="survey is not open for responses"
        )
    for a in payload.answers:
        db.add(
            SurveyResponse(
                survey_id=survey_id,
                question_id=a.question_id,
                score=a.score,
                respondent_hash=payload.respondent_hash,
            )
        )
    await db.commit()
    return {"survey_id": str(survey_id), "answers_recorded": len(payload.answers)}


@router.post("/surveys/{survey_id}/close")
async def close_survey(
    survey_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Close the survey and aggregate responses into CultureScore rows."""
    survey = (
        await db.execute(select(Survey).where(Survey.id == survey_id))
    ).scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="survey not found")

    questions = {
        q.id: q
        for q in (
            await db.execute(
                select(SurveyQuestion).where(SurveyQuestion.survey_id == survey_id)
            )
        ).scalars().all()
    }
    responses = (
        await db.execute(
            select(SurveyResponse).where(SurveyResponse.survey_id == survey_id)
        )
    ).scalars().all()

    by_dimension: dict[str, list[int]] = defaultdict(list)
    for r in responses:
        q = questions.get(r.question_id)
        if q is None:
            continue
        by_dimension[q.dimension].append(r.score)

    written = 0
    for dimension, scores in by_dimension.items():
        if not scores:
            continue
        avg = int(round(mean(scores)))
        db.add(
            CultureScore(
                period=survey.period,
                dimension=dimension,
                score=avg,
                notes=f"Aggregated from {len(scores)} response(s) in survey '{survey.name}'.",
            )
        )
        written += 1

    survey.status = "closed"
    await db.commit()
    return {
        "id": str(survey_id),
        "status": survey.status,
        "dimensions_scored": written,
        "responses_total": len(responses),
    }


@router.delete("/surveys/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(
    survey_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    survey = (
        await db.execute(select(Survey).where(Survey.id == survey_id))
    ).scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="survey not found")
    await db.delete(survey)
    await db.commit()
