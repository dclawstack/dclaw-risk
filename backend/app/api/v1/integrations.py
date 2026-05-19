"""P1.4 Compliance integration — proxies to DClaw Compliance, falls back to
a deterministic fixture in mock-mode so the unified view always has data.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models import Control
from app.schemas import ControlRead
from app.services.compliance import (
    fetch_compliance_library,
    join_with_local,
    push_local_controls,
)

router = APIRouter()


@router.get("/compliance/library")
async def compliance_library(
    user: User = Depends(get_current_user),
) -> dict:
    """Frameworks + requirements from the Compliance app (or fixture)."""
    result = await fetch_compliance_library()
    return {"mock": result.mock, "source": result.source, **result.data}


@router.get("/compliance/unified-view")
async def unified_view(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Join compliance requirements with our local controls library."""
    library_result = await fetch_compliance_library()
    controls = (await db.execute(select(Control))).scalars().all()
    local = [ControlRead.model_validate(c).model_dump(mode="json") for c in controls]
    rows = join_with_local(library_result.data, local)
    total = len(rows)
    covered = sum(1 for r in rows if r["covered"])
    return {
        "mock": library_result.mock,
        "source": library_result.source,
        "totals": {
            "requirements": total,
            "covered": covered,
            "uncovered": total - covered,
            "coverage_pct": round(100.0 * covered / total, 1) if total else 0.0,
        },
        "rows": rows,
    }


@router.post("/compliance/sync")
async def sync_compliance(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Push local controls to DClaw Compliance.

    Mock-mode returns a success envelope without round-tripping.
    """
    controls = (await db.execute(select(Control))).scalars().all()
    payload = [
        ControlRead.model_validate(c).model_dump(mode="json") for c in controls
    ]
    result = await push_local_controls(payload)
    return {"mock": result.mock, "source": result.source, **result.data}
