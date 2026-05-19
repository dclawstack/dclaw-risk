from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)


class SuggestedAction(BaseModel):
    title: str
    detail: str | None = None


class ChatResponse(BaseModel):
    reply: str
    suggested_actions: list[SuggestedAction] = []
    provider: str


class IdentifyRisksRequest(BaseModel):
    context: str = Field(
        min_length=1,
        description="Free-text project / system context to mine for risks",
    )
    count: int = Field(default=5, ge=1, le=20)


class IdentifiedRisk(BaseModel):
    name: str
    category: str
    severity: int = Field(ge=1, le=5)
    probability: int = Field(ge=1, le=5)
    rationale: str | None = None


class IdentifyRisksResponse(BaseModel):
    risks: list[IdentifiedRisk]
    provider: str


class ClassifyRiskRequest(BaseModel):
    name: str
    description: str | None = None


class ClassifyRiskResponse(BaseModel):
    category: str
    severity: int = Field(ge=1, le=5)
    probability: int = Field(ge=1, le=5)
    rationale: str
    provider: str
