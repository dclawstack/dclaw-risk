from pydantic import BaseModel
from datetime import datetime
from typing import List

class RiskAssessment(BaseModel):
    id: str
    name: str
    category: str
    severity: int
    probability: int
    mitigation_status: str
    owner: str
    created_at: datetime

class RiskCreate(BaseModel):
    name: str
    category: str
