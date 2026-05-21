from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.services import demo

router = APIRouter()


@router.get("/status")
async def get_status(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    counts = await demo.status(db)
    return {"is_empty": counts.is_empty, "counts": counts.to_dict()}


@router.post("/seed")
async def seed(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    counts = await demo.seed(db)
    return {"seeded": True, "counts": counts.to_dict()}


@router.post("/clear")
async def clear(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Wipes ALL domain tables — used by the landing-page demo widget."""
    removed = await demo.clear(db)
    return {"cleared": True, "removed": removed.to_dict()}
