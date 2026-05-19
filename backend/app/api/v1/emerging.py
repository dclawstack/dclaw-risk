"""P2.1 Emerging Risk endpoints — backed by a pluggable feed reader."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models.emerging import EmergingRisk
from app.services.emerging import (
    available_feeds,
    fetch_signals,
    synthetic_signal,
)

router = APIRouter()


@router.get("")
async def list_emerging(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    rows = (
        await db.execute(
            select(EmergingRisk).order_by(EmergingRisk.detected_at.desc())
        )
    ).scalars().all()
    total = (
        (await db.execute(select(func.count()).select_from(EmergingRisk))).scalar()
        or 0
    )
    items = [
        {
            "id": str(r.id),
            "title": r.title,
            "source": r.source,
            "url": r.url,
            "summary": r.summary,
            "detected_at": r.detected_at.isoformat(),
            "impact_score": r.impact_score,
            "status": r.status,
        }
        for r in rows
    ]
    return {"items": items, "total": total, "feeds": available_feeds()}


@router.post("/refresh")
async def refresh_feed(
    feed: str = "nvd-cve",
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Pull fresh signals from the named feed and persist new ones.

    De-dupes on (source, title): re-running this is safe and incremental.
    """
    try:
        signals = await fetch_signals(feed=feed, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"feed fetch failed: {e}"
        )

    sources = {sig.source for sig in signals}
    seen = (
        await db.execute(
            select(EmergingRisk.source, EmergingRisk.title).where(
                EmergingRisk.source.in_(sources) if sources else False
            )
        )
    ).all()
    seen_keys = {(s, t) for s, t in seen}

    new = 0
    for sig in signals:
        key = (sig.source, sig.title)
        if key in seen_keys:
            continue
        row = EmergingRisk(
            title=sig.title,
            source=sig.source,
            url=sig.url,
            summary=sig.summary,
            detected_at=sig.detected_at,
            impact_score=sig.impact_score,
        )
        db.add(row)
        new += 1
    await db.commit()
    return {"feed": feed, "fetched": len(signals), "new": new}


@router.post("/sample")
async def seed_sample(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    sig = synthetic_signal()
    row = EmergingRisk(
        title=sig.title,
        source=sig.source,
        url=sig.url,
        summary=sig.summary,
        detected_at=sig.detected_at,
        impact_score=sig.impact_score,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {"id": str(row.id), "title": row.title, "status": row.status}
