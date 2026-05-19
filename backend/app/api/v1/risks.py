from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models import Assessment, Risk
from app.repositories.risk_repo import RiskRepository
from app.schemas import RiskCreate, RiskList, RiskRead, RiskUpdate

router = APIRouter()


@router.get("", response_model=RiskList)
async def list_risks(
    category: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RiskList:
    repo = RiskRepository(db)
    items, total = await repo.list_filtered(
        category=category, status=status_filter, limit=limit, offset=offset
    )
    return RiskList(items=[RiskRead.model_validate(r) for r in items], total=total)


@router.post("", response_model=RiskRead, status_code=status.HTTP_201_CREATED)
async def create_risk(
    payload: RiskCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RiskRead:
    repo = RiskRepository(db)
    risk = Risk(**payload.model_dump())
    risk = await repo.create(risk)
    return RiskRead.model_validate(risk)


@router.get("/{risk_id}", response_model=RiskRead)
async def get_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RiskRead:
    risk = await RiskRepository(db).get_by_id(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="risk not found")
    return RiskRead.model_validate(risk)


@router.patch("/{risk_id}", response_model=RiskRead)
async def update_risk(
    risk_id: UUID,
    payload: RiskUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RiskRead:
    repo = RiskRepository(db)
    risk = await repo.get_by_id(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="risk not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(risk, field, value)
    await db.commit()
    await db.refresh(risk)
    return RiskRead.model_validate(risk)


@router.delete("/{risk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    repo = RiskRepository(db)
    risk = await repo.get_by_id(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="risk not found")
    await repo.delete(risk)


@router.get("/{risk_id}/trend")
async def risk_trend(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Time-series of risk score derived from the assessment history.

    Each qualitative assessment contributes a (timestamp, severity*probability)
    point. Quantitative assessments contribute (timestamp, loss_mean) on a
    second series so the UI can chart either qualitative score or annualised
    loss exposure over time.
    """
    risk = await RiskRepository(db).get_by_id(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="risk not found")

    rows = (
        await db.execute(
            select(Assessment)
            .where(Assessment.risk_id == risk_id)
            .order_by(Assessment.created_at.asc())
        )
    ).scalars().all()

    qualitative = [
        {
            "at": a.created_at.isoformat(),
            "score": (a.severity or 0) * (a.probability or 0),
        }
        for a in rows
        if a.kind == "qualitative" and a.severity and a.probability
    ]
    quantitative = [
        {"at": a.created_at.isoformat(), "loss_mean": a.loss_mean}
        for a in rows
        if a.kind == "quantitative" and a.loss_mean is not None
    ]
    return {
        "risk_id": str(risk_id),
        "current_score": risk.severity * risk.probability,
        "qualitative": qualitative,
        "quantitative": quantitative,
    }
