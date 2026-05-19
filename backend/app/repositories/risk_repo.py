from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Risk
from app.repositories.base_repo import BaseRepository


class RiskRepository(BaseRepository[Risk]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Risk)

    async def list_filtered(
        self,
        *,
        category: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Risk], int]:
        stmt = select(Risk).order_by(Risk.created_at.desc())
        count_stmt = select(func.count()).select_from(Risk)
        if category:
            stmt = stmt.where(Risk.category == category)
            count_stmt = count_stmt.where(Risk.category == category)
        if status:
            stmt = stmt.where(Risk.status == status)
            count_stmt = count_stmt.where(Risk.status == status)
        stmt = stmt.limit(limit).offset(offset)
        items = list((await self.db.execute(stmt)).scalars().all())
        total = (await self.db.execute(count_stmt)).scalar() or 0
        return items, total

    async def get_with_controls(self, risk_id: UUID) -> Risk | None:
        stmt = (
            select(Risk)
            .where(Risk.id == risk_id)
            .options(selectinload(Risk.controls))
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()
