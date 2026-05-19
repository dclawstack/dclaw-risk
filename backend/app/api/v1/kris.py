from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models.kri import KRI
from app.schemas.kri import KRICreate, KRIList, KRIRead, KRIUpdate

router = APIRouter()


@router.get("", response_model=KRIList)
async def list_kris(
    risk_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> KRIList:
    stmt = select(KRI).order_by(KRI.created_at.desc())
    if risk_id is not None:
        stmt = stmt.where(KRI.risk_id == risk_id)
    items = list((await db.execute(stmt)).scalars().all())
    total = (
        (await db.execute(select(func.count()).select_from(KRI))).scalar() or 0
    )
    return KRIList(
        items=[KRIRead.model_validate(k) for k in items], total=total
    )


@router.post("", response_model=KRIRead, status_code=status.HTTP_201_CREATED)
async def create_kri(
    payload: KRICreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> KRIRead:
    kri = KRI(**payload.model_dump())
    db.add(kri)
    await db.commit()
    await db.refresh(kri)
    return KRIRead.model_validate(kri)


@router.patch("/{kri_id}", response_model=KRIRead)
async def update_kri(
    kri_id: UUID,
    payload: KRIUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> KRIRead:
    kri = (
        await db.execute(select(KRI).where(KRI.id == kri_id))
    ).scalar_one_or_none()
    if not kri:
        raise HTTPException(status_code=404, detail="KRI not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(kri, field, value)
    await db.commit()
    await db.refresh(kri)
    return KRIRead.model_validate(kri)


@router.delete("/{kri_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kri(
    kri_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    kri = (
        await db.execute(select(KRI).where(KRI.id == kri_id))
    ).scalar_one_or_none()
    if not kri:
        raise HTTPException(status_code=404, detail="KRI not found")
    await db.delete(kri)
    await db.commit()


@router.get("/breaches")
async def list_breaches(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    rows = (await db.execute(select(KRI))).scalars().all()
    breaches = [
        KRIRead.model_validate(k).model_dump(mode="json")
        for k in rows
        if k.status != "ok"
    ]
    return {
        "total": len(breaches),
        "critical": sum(1 for k in rows if k.status == "critical"),
        "warn": sum(1 for k in rows if k.status == "warn"),
        "items": breaches,
    }
