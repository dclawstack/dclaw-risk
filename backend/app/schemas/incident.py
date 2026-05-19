from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

IncidentStatus = Literal["open", "investigating", "resolved", "closed"]


class IncidentBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    severity: int = Field(ge=1, le=5, default=3)
    occurred_at: datetime | None = None
    risk_id: UUID | None = None
    status: IncidentStatus = "open"


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    severity: int | None = Field(default=None, ge=1, le=5)
    occurred_at: datetime | None = None
    risk_id: UUID | None = None
    status: IncidentStatus | None = None


class IncidentRead(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class IncidentList(BaseModel):
    items: list[IncidentRead]
    total: int
