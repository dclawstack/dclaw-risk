from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryMultiplier(BaseModel):
    severity: float = Field(ge=0)
    probability: float = Field(ge=0)


class ScenarioBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    multipliers: dict[str, CategoryMultiplier] = Field(default_factory=dict)


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    multipliers: dict[str, CategoryMultiplier] | None = None


class ScenarioRead(ScenarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class ScenarioList(BaseModel):
    items: list[ScenarioRead]
    total: int


class StressTestRow(BaseModel):
    risk_id: UUID
    name: str
    category: str
    baseline_score: int
    projected_severity: float
    projected_probability: float
    projected_score: float


class StressTestResponse(BaseModel):
    scenario_id: UUID
    baseline_total: int
    projected_total: float
    delta_pct: float
    rows: list[StressTestRow]


class GenerateScenarioRequest(BaseModel):
    context: str = Field(min_length=1)


class GenerateScenarioResponse(BaseModel):
    name: str
    description: str
    multipliers: dict[str, CategoryMultiplier]
    provider: str
