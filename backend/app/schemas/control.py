from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ControlType = Literal["preventive", "detective", "corrective", "compensating"]


class ControlBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    framework: str | None = Field(default=None, max_length=64)
    control_type: ControlType = "preventive"
    effectiveness: int = Field(ge=1, le=5, default=3)
    owner: str | None = None


class ControlCreate(ControlBase):
    pass


class ControlUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    framework: str | None = Field(default=None, max_length=64)
    control_type: ControlType | None = None
    effectiveness: int | None = Field(default=None, ge=1, le=5)
    owner: str | None = None


class ControlRead(ControlBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class ControlList(BaseModel):
    items: list[ControlRead]
    total: int


class RiskControlMap(BaseModel):
    control_id: UUID
    effectiveness: int = Field(ge=1, le=5, default=3)
