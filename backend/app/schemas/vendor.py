from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VendorBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    notes: str | None = None
    category: str | None = Field(default=None, max_length=64)
    criticality: int = Field(ge=1, le=5, default=3)
    score: int = Field(ge=0, le=100, default=50)


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    notes: str | None = None
    category: str | None = None
    criticality: int | None = Field(default=None, ge=1, le=5)
    score: int | None = Field(default=None, ge=0, le=100)


class VendorRead(VendorBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    last_assessed_at: datetime | None = None
    ai_rationale: str | None = None
    created_at: datetime
    updated_at: datetime


class VendorList(BaseModel):
    items: list[VendorRead]
    total: int


class ScoreVendorResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    rationale: str
    provider: str
