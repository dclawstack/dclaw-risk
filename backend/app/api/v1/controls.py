from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models import Control, Risk
from app.models.risk import RiskControl
from app.repositories.control_repo import ControlRepository
from app.repositories.risk_repo import RiskRepository
from app.schemas import (
    ControlCreate,
    ControlList,
    ControlRead,
    ControlUpdate,
    RiskControlMap,
)
from app.schemas.risk import RiskRead

router = APIRouter()


@router.get("/gap-analysis")
async def gap_analysis(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Two-sided gap analysis between risks and controls.

    Returns risks with no mapped controls (uncovered) and controls mapped to
    no risks (unused). Useful for the executive dashboard and for the Copilot
    to recommend control investments.
    """
    risks = (await db.execute(select(Risk))).scalars().all()
    controls = (await db.execute(select(Control))).scalars().all()
    links = (await db.execute(select(RiskControl))).scalars().all()

    covered_risk_ids = {l.risk_id for l in links}
    used_control_ids = {l.control_id for l in links}

    uncovered_risks = [
        RiskRead.model_validate(r).model_dump(mode="json")
        for r in risks
        if r.id not in covered_risk_ids
    ]
    unused_controls = [
        ControlRead.model_validate(c).model_dump(mode="json")
        for c in controls
        if c.id not in used_control_ids
    ]
    return {
        "uncovered_risks": uncovered_risks,
        "unused_controls": unused_controls,
        "totals": {
            "risks": len(risks),
            "controls": len(controls),
            "links": len(links),
            "uncovered_risks": len(uncovered_risks),
            "unused_controls": len(unused_controls),
        },
    }


@router.get("", response_model=ControlList)
async def list_controls(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ControlList:
    items, total = await ControlRepository(db).list_all(limit=limit, offset=offset)
    return ControlList(
        items=[ControlRead.model_validate(c) for c in items], total=total
    )


@router.post("", response_model=ControlRead, status_code=status.HTTP_201_CREATED)
async def create_control(
    payload: ControlCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ControlRead:
    control = Control(**payload.model_dump())
    control = await ControlRepository(db).create(control)
    return ControlRead.model_validate(control)


@router.get("/{control_id}", response_model=ControlRead)
async def get_control(
    control_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ControlRead:
    control = await ControlRepository(db).get_by_id(control_id)
    if not control:
        raise HTTPException(status_code=404, detail="control not found")
    return ControlRead.model_validate(control)


@router.patch("/{control_id}", response_model=ControlRead)
async def update_control(
    control_id: UUID,
    payload: ControlUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ControlRead:
    repo = ControlRepository(db)
    control = await repo.get_by_id(control_id)
    if not control:
        raise HTTPException(status_code=404, detail="control not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(control, field, value)
    await db.commit()
    await db.refresh(control)
    return ControlRead.model_validate(control)


@router.delete("/{control_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_control(
    control_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    repo = ControlRepository(db)
    control = await repo.get_by_id(control_id)
    if not control:
        raise HTTPException(status_code=404, detail="control not found")
    await repo.delete(control)


# --- Risk <-> Control mapping (mounted under /api/v1/risks/{risk_id}/controls) ---

mapping_router = APIRouter()


@mapping_router.get("", response_model=list[ControlRead])
async def list_controls_for_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ControlRead]:
    risk = await RiskRepository(db).get_by_id(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="risk not found")
    rows = await db.execute(
        select(Control)
        .join(RiskControl, RiskControl.control_id == Control.id)
        .where(RiskControl.risk_id == risk_id)
        .order_by(Control.name)
    )
    return [ControlRead.model_validate(c) for c in rows.scalars().all()]


@mapping_router.post("", response_model=list[ControlRead], status_code=status.HTTP_201_CREATED)
async def map_control_to_risk(
    risk_id: UUID,
    payload: RiskControlMap,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ControlRead]:
    risk = await RiskRepository(db).get_by_id(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="risk not found")
    control = await ControlRepository(db).get_by_id(payload.control_id)
    if not control:
        raise HTTPException(status_code=404, detail="control not found")

    exists = await db.execute(
        select(RiskControl).where(
            RiskControl.risk_id == risk_id, RiskControl.control_id == control.id
        )
    )
    link = exists.scalar_one_or_none()
    if link:
        link.effectiveness = payload.effectiveness
    else:
        db.add(
            RiskControl(
                risk_id=risk_id,
                control_id=control.id,
                effectiveness=payload.effectiveness,
            )
        )
    await db.commit()

    rows = await db.execute(
        select(Control)
        .join(RiskControl, RiskControl.control_id == Control.id)
        .where(RiskControl.risk_id == risk_id)
        .order_by(Control.name)
    )
    return [ControlRead.model_validate(c) for c in rows.scalars().all()]


@mapping_router.delete(
    "/{control_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def unmap_control_from_risk(
    risk_id: UUID,
    control_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    await db.execute(
        delete(RiskControl).where(
            RiskControl.risk_id == risk_id, RiskControl.control_id == control_id
        )
    )
    await db.commit()
