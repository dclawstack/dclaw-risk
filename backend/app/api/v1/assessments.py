from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models import Assessment
from app.repositories.assessment_repo import AssessmentRepository
from app.repositories.risk_repo import RiskRepository
from app.schemas import (
    AssessmentRead,
    QualitativeAssessmentCreate,
    QuantitativeAssessmentCreate,
)
from app.services.fair_calculator import FairInputs, simulate

router = APIRouter()


@router.get("", response_model=list[AssessmentRead])
async def list_assessments_for_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[AssessmentRead]:
    repo = AssessmentRepository(db)
    rows = await repo.list_for_risk(risk_id)
    return [AssessmentRead.model_validate(r) for r in rows]


@router.post(
    "/qualitative",
    response_model=AssessmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_qualitative(
    risk_id: UUID,
    payload: QualitativeAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AssessmentRead:
    risk = await RiskRepository(db).get_by_id(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="risk not found")

    assessment = Assessment(
        risk_id=risk_id,
        kind="qualitative",
        severity=payload.severity,
        probability=payload.probability,
        assessor=payload.assessor,
    )
    # Sync the headline score on the risk so the register stays current.
    risk.severity = payload.severity
    risk.probability = payload.probability
    if risk.status == "identified":
        risk.status = "assessed"

    assessment = await AssessmentRepository(db).create(assessment)
    return AssessmentRead.model_validate(assessment)


@router.post(
    "/quantitative",
    response_model=AssessmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_quantitative(
    risk_id: UUID,
    payload: QuantitativeAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AssessmentRead:
    risk = await RiskRepository(db).get_by_id(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="risk not found")

    result = simulate(
        FairInputs(
            loss_min=payload.loss_min,
            loss_mode=payload.loss_mode,
            loss_max=payload.loss_max,
            freq_min=payload.freq_min,
            freq_max=payload.freq_max,
            iterations=payload.iterations,
        )
    )

    assessment = Assessment(
        risk_id=risk_id,
        kind="quantitative",
        assessor=payload.assessor,
        loss_min=payload.loss_min,
        loss_mode=payload.loss_mode,
        loss_max=payload.loss_max,
        freq_min=payload.freq_min,
        freq_max=payload.freq_max,
        iterations=payload.iterations,
        loss_p10=result.p10,
        loss_p50=result.p50,
        loss_p90=result.p90,
        loss_mean=result.mean,
        curve=result.curve,
    )
    if risk.status == "identified":
        risk.status = "assessed"

    assessment = await AssessmentRepository(db).create(assessment)
    return AssessmentRead.model_validate(assessment)
