from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models.vendor import Vendor
from app.schemas.vendor import (
    ScoreVendorResponse,
    VendorCreate,
    VendorList,
    VendorRead,
    VendorUpdate,
)
from app.services.risk_ai import score_vendor as ai_score_vendor

router = APIRouter()


@router.get("", response_model=VendorList)
async def list_vendors(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> VendorList:
    rows = (
        await db.execute(select(Vendor).order_by(Vendor.score.desc()))
    ).scalars().all()
    total = (
        (await db.execute(select(func.count()).select_from(Vendor))).scalar() or 0
    )
    return VendorList(
        items=[VendorRead.model_validate(v) for v in rows], total=total
    )


@router.post("", response_model=VendorRead, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    payload: VendorCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> VendorRead:
    v = Vendor(**payload.model_dump())
    db.add(v)
    await db.commit()
    await db.refresh(v)
    return VendorRead.model_validate(v)


@router.patch("/{vendor_id}", response_model=VendorRead)
async def update_vendor(
    vendor_id: UUID,
    payload: VendorUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> VendorRead:
    v = (
        await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    ).scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="vendor not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(v, field, value)
    await db.commit()
    await db.refresh(v)
    return VendorRead.model_validate(v)


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    v = (
        await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    ).scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="vendor not found")
    await db.delete(v)
    await db.commit()


@router.post("/{vendor_id}/ai-score", response_model=VendorRead)
async def ai_score(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> VendorRead:
    v = (
        await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    ).scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="vendor not found")
    result: ScoreVendorResponse = await ai_score_vendor(
        name=v.name,
        notes=v.notes,
        category=v.category,
        criticality=v.criticality,
    )
    v.score = result.score
    v.ai_rationale = result.rationale
    v.last_assessed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(v)
    return VendorRead.model_validate(v)
