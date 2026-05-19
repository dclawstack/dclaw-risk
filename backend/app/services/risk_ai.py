"""Risk-domain AI helpers built on top of the LLM provider abstraction.

Three capabilities:
  - chat:     conversational copilot aware of the user's current risks
  - identify: extract candidate risks from a free-text project description
  - classify: suggest category + 1-5 severity/probability for a single risk

The LLM is asked to return JSON; we extract the first JSON object/array we can
find and fall back to a deterministic baseline if parsing fails. That keeps the
endpoint usable even when only the MockProvider is available.
"""

from __future__ import annotations

import json
import re
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Risk
from app.schemas.ai import (
    ChatMessage,
    ChatResponse,
    ClassifyRiskResponse,
    IdentifiedRisk,
    IdentifyRisksResponse,
    SuggestedAction,
)
from app.services.llm import LLMProvider, Message, get_llm

log = structlog.get_logger(__name__)

SYSTEM_PROMPT = (
    "You are the DClaw Risk Copilot, an expert ERM analyst. "
    "Help the user identify, assess, mitigate, and monitor enterprise risks. "
    "Be specific and actionable. Reply concisely (<= 200 words) unless asked for detail. "
    "When the user asks for suggestions, prefer concrete next actions."
)

CATEGORIES = (
    "Operational",
    "Financial",
    "Legal",
    "Reputational",
    "Cybersecurity",
    "Strategic",
    "Compliance",
    "Third-Party",
)


def _extract_json(text: str) -> Any | None:
    """Pull the first JSON value (object or array) out of an LLM response."""
    match = re.search(r"(\{.*\}|\[.*\])", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


async def _risk_context_snippet(db: AsyncSession, limit: int = 20) -> str:
    rows = (
        await db.execute(
            select(Risk).order_by(Risk.created_at.desc()).limit(limit)
        )
    ).scalars().all()
    if not rows:
        return "The user has no risks in the register yet."
    lines = [
        f"- {r.name} [{r.category}] severity={r.severity} probability={r.probability} status={r.status}"
        for r in rows
    ]
    return "Current top risks in the register:\n" + "\n".join(lines)


async def chat(
    messages: list[ChatMessage],
    db: AsyncSession,
    provider: LLMProvider | None = None,
) -> ChatResponse:
    llm = provider or get_llm()
    context = await _risk_context_snippet(db)

    convo: list[Message] = [
        Message(role="system", content=SYSTEM_PROMPT),
        Message(role="system", content=context),
    ]
    convo.extend(Message(role=m.role, content=m.content) for m in messages)  # type: ignore[arg-type]

    reply = await llm.chat(convo)

    suggested = _extract_suggested_actions(reply)
    return ChatResponse(reply=reply, suggested_actions=suggested, provider=llm.name)


def _extract_suggested_actions(reply: str) -> list[SuggestedAction]:
    """Pull bullet/numbered lines out of a reply as suggested actions."""
    actions: list[SuggestedAction] = []
    for line in reply.splitlines():
        stripped = line.strip()
        m = re.match(r"^(?:[-*•]|\d+[.)])\s+(.{4,200})$", stripped)
        if m:
            actions.append(SuggestedAction(title=m.group(1).strip()))
        if len(actions) >= 5:
            break
    return actions


async def identify_risks(
    context: str, count: int, provider: LLMProvider | None = None
) -> IdentifyRisksResponse:
    llm = provider or get_llm()
    prompt = (
        f"Given the following project / system context, propose {count} distinct "
        "enterprise risks. Reply with a JSON array of objects, each with keys: "
        "name (string), category (one of "
        f"{list(CATEGORIES)}), severity (1-5 int), probability (1-5 int), "
        "rationale (1-2 sentences). Output JSON only.\n\nCONTEXT:\n"
        f"{context}"
    )
    raw = await llm.chat(
        [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=prompt),
        ]
    )
    parsed = _extract_json(raw)
    risks: list[IdentifiedRisk] = []
    if isinstance(parsed, list):
        for item in parsed[:count]:
            try:
                risks.append(IdentifiedRisk.model_validate(item))
            except Exception as e:  # pragma: no cover - defensive
                log.warning("ai.identify.bad_item", error=str(e), item=item)

    if not risks:
        risks = _fallback_identify(context, count)

    return IdentifyRisksResponse(risks=risks, provider=llm.name)


def _fallback_identify(context: str, count: int) -> list[IdentifiedRisk]:
    """Deterministic stand-in when the LLM response can't be parsed."""
    seeds = [
        ("Operational continuity gap", "Operational", 4, 3),
        ("Vendor concentration", "Third-Party", 3, 3),
        ("Data breach exposure", "Cybersecurity", 5, 3),
        ("Regulatory change impact", "Compliance", 3, 4),
        ("Key-person dependency", "Operational", 4, 2),
        ("Foreign-exchange volatility", "Financial", 3, 3),
        ("Reputational backlash", "Reputational", 4, 2),
        ("Strategic mis-execution", "Strategic", 4, 3),
    ]
    return [
        IdentifiedRisk(
            name=name,
            category=cat,
            severity=sev,
            probability=prob,
            rationale=f"Inferred from context summary ({len(context)} chars).",
        )
        for name, cat, sev, prob in seeds[:count]
    ]


async def score_vendor(
    name: str,
    notes: str | None,
    category: str | None,
    criticality: int,
    provider: LLMProvider | None = None,
):
    """Suggest a 0-100 risk score for a third-party vendor with rationale."""
    from app.schemas.vendor import ScoreVendorResponse

    llm = provider or get_llm()
    prompt = (
        "Score the following third-party vendor on a 0-100 risk scale "
        "(0 = trivial / well-controlled, 100 = critical exposure). "
        "Reply with a single JSON object: "
        "{score: int 0-100, rationale: 1-2 sentences}. JSON only.\n\n"
        f"VENDOR: {name}\nCATEGORY: {category or '(unspecified)'}\n"
        f"CRITICALITY: {criticality}/5\nNOTES: {notes or '(none)'}"
    )
    raw = await llm.chat(
        [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=prompt),
        ]
    )
    parsed = _extract_json(raw)
    if isinstance(parsed, dict):
        try:
            score = int(parsed.get("score", 50))
            score = max(0, min(100, score))
            return ScoreVendorResponse(
                score=score,
                rationale=str(parsed.get("rationale", ""))[:1000],
                provider=llm.name,
            )
        except Exception as e:  # pragma: no cover - defensive
            log.warning("ai.score_vendor.bad_response", error=str(e))

    return ScoreVendorResponse(
        score=20 + criticality * 12,
        rationale=f"Heuristic fallback based on criticality {criticality}/5.",
        provider=llm.name,
    )


async def generate_scenario(
    context: str, provider: LLMProvider | None = None
):
    """Use the LLM to produce a stress-test scenario from a free-text context."""
    from app.schemas.scenario import CategoryMultiplier, GenerateScenarioResponse

    llm = provider or get_llm()
    prompt = (
        "Generate a what-if risk scenario for an enterprise risk manager. "
        "Reply with a single JSON object with keys: name (string), "
        "description (1-2 sentences), multipliers (object mapping category "
        f"name to {{severity: float, probability: float}}). Use categories "
        f"from {list(CATEGORIES)}. Multipliers should be between 0.5 and 2.0. "
        "JSON only.\n\nCONTEXT:\n" + context
    )
    raw = await llm.chat(
        [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=prompt),
        ]
    )
    parsed = _extract_json(raw)
    if isinstance(parsed, dict) and isinstance(parsed.get("multipliers"), dict):
        try:
            mults = {
                cat: CategoryMultiplier(**vals)
                for cat, vals in parsed["multipliers"].items()
                if isinstance(vals, dict)
            }
            return GenerateScenarioResponse(
                name=str(parsed.get("name", "Generated Scenario"))[:255],
                description=str(parsed.get("description", "")),
                multipliers=mults,
                provider=llm.name,
            )
        except Exception as e:  # pragma: no cover - defensive
            log.warning("ai.generate_scenario.bad_response", error=str(e))

    return GenerateScenarioResponse(
        name="Recession scenario",
        description="Deterministic fallback when the LLM response can't be parsed.",
        multipliers={
            "Financial": CategoryMultiplier(severity=1.4, probability=1.3),
            "Operational": CategoryMultiplier(severity=1.2, probability=1.1),
        },
        provider=llm.name,
    )


async def classify_risk(
    name: str, description: str | None, provider: LLMProvider | None = None
) -> ClassifyRiskResponse:
    llm = provider or get_llm()
    prompt = (
        "Classify the following risk. Output a single JSON object with keys: "
        f"category (one of {list(CATEGORIES)}), severity (1-5 int), "
        "probability (1-5 int), rationale (1-2 sentences). JSON only.\n\n"
        f"RISK NAME: {name}\nDESCRIPTION: {description or '(none)'}"
    )
    raw = await llm.chat(
        [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=prompt),
        ]
    )
    parsed = _extract_json(raw)
    if isinstance(parsed, dict):
        try:
            return ClassifyRiskResponse(
                category=str(parsed.get("category", "Operational")),
                severity=int(parsed.get("severity", 3)),
                probability=int(parsed.get("probability", 3)),
                rationale=str(parsed.get("rationale", "")),
                provider=llm.name,
            )
        except Exception as e:  # pragma: no cover - defensive
            log.warning("ai.classify.bad_response", error=str(e))

    return ClassifyRiskResponse(
        category="Operational",
        severity=3,
        probability=3,
        rationale=f"Heuristic fallback for '{name}'.",
        provider=llm.name,
    )
