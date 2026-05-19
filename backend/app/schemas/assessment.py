from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

AssessmentKind = Literal["qualitative", "quantitative"]


class QualitativeAssessmentCreate(BaseModel):
    kind: Literal["qualitative"] = "qualitative"
    severity: int = Field(ge=1, le=5)
    probability: int = Field(ge=1, le=5)
    assessor: str | None = None


class QuantitativeAssessmentCreate(BaseModel):
    kind: Literal["quantitative"] = "quantitative"
    loss_min: float = Field(ge=0)
    loss_mode: float = Field(ge=0)
    loss_max: float = Field(ge=0)
    freq_min: float = Field(ge=0)
    freq_max: float = Field(ge=0)
    iterations: int = Field(ge=100, le=200_000, default=10_000)
    assessor: str | None = None

    @model_validator(mode="after")
    def check_order(self) -> "QuantitativeAssessmentCreate":
        if not (self.loss_min <= self.loss_mode <= self.loss_max):
            raise ValueError("require loss_min <= loss_mode <= loss_max")
        if self.freq_min > self.freq_max:
            raise ValueError("require freq_min <= freq_max")
        return self


class CurvePoint(BaseModel):
    loss: float
    exceedance_probability: float


class AssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    risk_id: UUID
    kind: AssessmentKind
    assessor: str | None = None

    severity: int | None = None
    probability: int | None = None

    loss_min: float | None = None
    loss_mode: float | None = None
    loss_max: float | None = None
    freq_min: float | None = None
    freq_max: float | None = None
    iterations: int | None = None

    loss_p10: float | None = None
    loss_p50: float | None = None
    loss_p90: float | None = None
    loss_mean: float | None = None
    curve: list[CurvePoint] | None = None

    created_at: datetime
