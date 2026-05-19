from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.services import reports

router = APIRouter()


@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    s = await reports.summary(db)
    return {
        "total_risks": s.total_risks,
        "by_category": s.by_category,
        "by_status": s.by_status,
        "top_risks": s.top_risks,
        "mean_score": round(s.mean_score, 2),
        "control_coverage_pct": round(s.control_coverage_pct, 1),
        "total_controls": s.total_controls,
    }


@router.get("/exposure")
async def get_exposure(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    e = await reports.exposure(db)
    return {
        "risks_with_quantitative": e.risks_with_quantitative,
        "total_p50": e.total_p50,
        "total_p90": e.total_p90,
        "total_mean": e.total_mean,
        "per_risk": e.per_risk,
    }


@router.post("/narrative")
async def post_narrative(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return await reports.narrative(db)
