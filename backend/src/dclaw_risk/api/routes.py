from fastapi import APIRouter
from datetime import datetime
from uuid import uuid4
import random
from dclaw_risk.models import RiskAssessment, RiskCreate

router = APIRouter()

@router.post("/assessments", response_model=RiskAssessment)
async def create_item(payload: RiskCreate):
    return RiskAssessment(
        id=str(uuid4()),
        name=payload.name,
        category=payload.category,
        severity=random.randint(1, 5),
        probability=random.randint(1, 5),
        mitigation_status="planned",
        owner="Risk Committee",
        created_at=datetime.utcnow(),
    )

@router.get("/assessments/{assessment_id}/mitigations")
async def get_item(assessment_id: str):
    return [{"action": "Implement controls", "owner": "IT"}, {"action": "Purchase insurance", "owner": "Finance"}, {"action": "Train staff", "owner": "HR"}]
