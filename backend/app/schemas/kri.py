from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Direction = Literal["above", "below"]
KRIStatus = Literal["ok", "warn", "critical"]


class KRIBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    unit: str = Field(default="count", max_length=32)
    current_value: float = 0.0
    threshold_warn: float
    threshold_critical: float
    direction: Direction = "above"
    risk_id: UUID | None = None
    owner: str | None = None


class KRICreate(KRIBase):
    pass


class KRIUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    unit: str | None = None
    current_value: float | None = None
    threshold_warn: float | None = None
    threshold_critical: float | None = None
    direction: Direction | None = None
    risk_id: UUID | None = None
    owner: str | None = None


class KRIRead(KRIBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: KRIStatus
    created_at: datetime
    updated_at: datetime


class KRIList(BaseModel):
    items: list[KRIRead]
    total: int
