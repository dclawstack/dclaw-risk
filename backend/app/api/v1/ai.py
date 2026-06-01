from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ClassifyRiskRequest,
    ClassifyRiskResponse,
    IdentifyRisksRequest,
    IdentifyRisksResponse,
)
from app.services import risk_ai

router = APIRouter()


@router.post("/risk-chat", response_model=ChatResponse)
@limiter.limit(lambda: settings.rate_limit_ai)
async def risk_chat(
    request: Request,
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChatResponse:
    return await risk_ai.chat(payload.messages, db=db)


@router.post("/identify-risks", response_model=IdentifyRisksResponse)
@limiter.limit(lambda: settings.rate_limit_ai)
async def identify_risks(
    request: Request,
    payload: IdentifyRisksRequest,
    user: User = Depends(get_current_user),
) -> IdentifyRisksResponse:
    return await risk_ai.identify_risks(payload.context, payload.count)


@router.post("/classify-risk", response_model=ClassifyRiskResponse)
@limiter.limit(lambda: settings.rate_limit_ai)
async def classify_risk(
    request: Request,
    payload: ClassifyRiskRequest,
    user: User = Depends(get_current_user),
) -> ClassifyRiskResponse:
    return await risk_ai.classify_risk(payload.name, payload.description)
