from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

RiskStatus = Literal[
    "identified", "assessed", "treated", "monitored", "closed", "accepted"
]


class RiskBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str = Field(min_length=1, max_length=64)
    status: RiskStatus = "identified"
    owner: str | None = None
    severity: int = Field(ge=1, le=5, default=3)
    probability: int = Field(ge=1, le=5, default=3)
    velocity: int = Field(ge=1, le=5, default=3)


class RiskCreate(RiskBase):
    pass


class RiskUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1, max_length=64)
    status: RiskStatus | None = None
    owner: str | None = None
    severity: int | None = Field(default=None, ge=1, le=5)
    probability: int | None = Field(default=None, ge=1, le=5)
    velocity: int | None = Field(default=None, ge=1, le=5)


class RiskRead(RiskBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    score: int
    ai_classification: str | None = None
    ai_rationale: str | None = None
    created_at: datetime
    updated_at: datetime


class RiskList(BaseModel):
    items: list[RiskRead]
    total: int
