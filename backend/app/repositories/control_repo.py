from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Control
from app.repositories.base_repo import BaseRepository


class ControlRepository(BaseRepository[Control]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Control)
