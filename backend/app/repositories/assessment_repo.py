from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assessment
from app.repositories.base_repo import BaseRepository


class AssessmentRepository(BaseRepository[Assessment]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Assessment)

    async def list_for_risk(self, risk_id: UUID) -> list[Assessment]:
        stmt = (
            select(Assessment)
            .where(Assessment.risk_id == risk_id)
            .order_by(Assessment.created_at.desc())
        )
        return list((await self.db.execute(stmt)).scalars().all())
