from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models.incident import Incident
from app.schemas.incident import (
    IncidentCreate,
    IncidentList,
    IncidentRead,
    IncidentUpdate,
)
from app.services.llm import Message, get_llm
from app.services.risk_ai import SYSTEM_PROMPT

router = APIRouter()


@router.get("", response_model=IncidentList)
async def list_incidents(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> IncidentList:
    rows = (
        await db.execute(select(Incident).order_by(Incident.occurred_at.desc()))
    ).scalars().all()
    total = (
        (await db.execute(select(func.count()).select_from(Incident))).scalar() or 0
    )
    return IncidentList(
        items=[IncidentRead.model_validate(i) for i in rows], total=total
    )


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
async def create_incident(
    payload: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> IncidentRead:
    data = payload.model_dump()
    if data.get("occurred_at") is None:
        data.pop("occurred_at", None)
    incident = Incident(**data)
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return IncidentRead.model_validate(incident)


@router.patch("/{incident_id}", response_model=IncidentRead)
async def update_incident(
    incident_id: UUID,
    payload: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> IncidentRead:
    incident = (
        await db.execute(select(Incident).where(Incident.id == incident_id))
    ).scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="incident not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)
    await db.commit()
    await db.refresh(incident)
    return IncidentRead.model_validate(incident)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    incident = (
        await db.execute(select(Incident).where(Incident.id == incident_id))
    ).scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="incident not found")
    await db.delete(incident)
    await db.commit()


@router.get("/patterns")
async def detect_patterns(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Ask the LLM to find recurring themes across recent incidents."""
    rows = (
        await db.execute(
            select(Incident).order_by(Incident.occurred_at.desc()).limit(50)
        )
    ).scalars().all()
    if not rows:
        return {"patterns": [], "provider": "n/a", "count_analysed": 0}

    lines = [
        f"- [{i.occurred_at.date()}] sev={i.severity} status={i.status}: {i.title}"
        + (f" — {i.description}" if i.description else "")
        for i in rows
    ]
    prompt = (
        "Find recurring themes across the following incident log. "
        "Reply with 3-5 short bullet lines describing the patterns you see "
        "and which risk categories they implicate. Be specific.\n\n"
        + "\n".join(lines)
    )
    llm = get_llm()
    reply = await llm.chat(
        [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=prompt),
        ]
    )
    patterns = [
        line.strip().lstrip("-*•0123456789. )")
        for line in reply.splitlines()
        if line.strip().startswith(("-", "*", "•")) or (
            line.strip()[:2].rstrip(".)").isdigit()
        )
    ][:5]
    return {
        "patterns": patterns or [reply.strip()[:500]],
        "raw": reply,
        "provider": llm.name,
        "count_analysed": len(rows),
    }
