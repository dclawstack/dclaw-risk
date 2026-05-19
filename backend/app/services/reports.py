"""Risk reporting aggregations.

Pure SQL aggregations + an AI narrative helper. All numbers come from the
database; the LLM only writes prose around them.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assessment, Control, Risk
from app.models.risk import RiskControl
from app.services.llm import LLMProvider, Message, get_llm
from app.services.risk_ai import SYSTEM_PROMPT


@dataclass
class Summary:
    total_risks: int
    by_category: dict[str, int]
    by_status: dict[str, int]
    top_risks: list[dict]
    mean_score: float
    control_coverage_pct: float
    total_controls: int


async def summary(db: AsyncSession, top_n: int = 5) -> Summary:
    risks = (await db.execute(select(Risk))).scalars().all()
    controls_total = (
        (await db.execute(select(func.count()).select_from(Control))).scalar() or 0
    )
    link_rows = (await db.execute(select(RiskControl.risk_id))).scalars().all()
    covered_ids = set(link_rows)

    total = len(risks)
    by_cat = Counter(r.category for r in risks)
    by_status = Counter(r.status for r in risks)
    top = sorted(risks, key=lambda r: r.severity * r.probability, reverse=True)[:top_n]
    mean_score = (
        sum(r.severity * r.probability for r in risks) / total if total else 0.0
    )
    coverage = (
        100.0 * sum(1 for r in risks if r.id in covered_ids) / total if total else 0.0
    )
    return Summary(
        total_risks=total,
        by_category=dict(by_cat),
        by_status=dict(by_status),
        top_risks=[
            {
                "id": str(r.id),
                "name": r.name,
                "category": r.category,
                "score": r.severity * r.probability,
                "status": r.status,
            }
            for r in top
        ],
        mean_score=mean_score,
        control_coverage_pct=coverage,
        total_controls=controls_total,
    )


@dataclass
class Exposure:
    risks_with_quantitative: int
    total_p50: float
    total_p90: float
    total_mean: float
    per_risk: list[dict]


async def exposure(db: AsyncSession) -> Exposure:
    """Aggregate quantitative loss exposure across all risks.

    Uses the most recent quantitative assessment per risk. Sums independent
    losses — naive but standard for an executive headline number.
    """
    subq = (
        select(
            Assessment.risk_id,
            func.max(Assessment.created_at).label("latest"),
        )
        .where(Assessment.kind == "quantitative")
        .group_by(Assessment.risk_id)
        .subquery()
    )
    rows = (
        await db.execute(
            select(Assessment, Risk)
            .join(
                subq,
                (Assessment.risk_id == subq.c.risk_id)
                & (Assessment.created_at == subq.c.latest),
            )
            .join(Risk, Risk.id == Assessment.risk_id)
        )
    ).all()

    per_risk = []
    total_p50 = total_p90 = total_mean = 0.0
    for assessment, risk in rows:
        if assessment.loss_p50 is None:
            continue
        per_risk.append(
            {
                "risk_id": str(risk.id),
                "name": risk.name,
                "category": risk.category,
                "loss_p10": assessment.loss_p10,
                "loss_p50": assessment.loss_p50,
                "loss_p90": assessment.loss_p90,
                "loss_mean": assessment.loss_mean,
            }
        )
        total_p50 += assessment.loss_p50 or 0
        total_p90 += assessment.loss_p90 or 0
        total_mean += assessment.loss_mean or 0

    return Exposure(
        risks_with_quantitative=len(per_risk),
        total_p50=total_p50,
        total_p90=total_p90,
        total_mean=total_mean,
        per_risk=per_risk,
    )


async def narrative(
    db: AsyncSession, provider: LLMProvider | None = None
) -> dict:
    """Generate a board-ready executive narrative grounded in the summary."""
    s = await summary(db, top_n=3)
    e = await exposure(db)
    llm = provider or get_llm()
    facts = (
        f"Total risks: {s.total_risks}. By category: {s.by_category}. "
        f"By status: {s.by_status}. Mean qualitative score: {s.mean_score:.1f}. "
        f"Control coverage: {s.control_coverage_pct:.0f}%. "
        f"Total controls: {s.total_controls}. "
        f"Top risks: {[t['name'] for t in s.top_risks]}. "
        f"Quantified risks: {e.risks_with_quantitative}, "
        f"annualised P50 exposure: ${e.total_p50:,.0f}, "
        f"P90 exposure: ${e.total_p90:,.0f}."
    )
    prompt = (
        "Write a 3-paragraph executive risk briefing for the board. "
        "Use ONLY the facts I provide; do not invent risks, controls, or numbers. "
        "Paragraph 1: posture summary. Paragraph 2: areas of concern. "
        "Paragraph 3: recommended next actions. "
        f"FACTS:\n{facts}"
    )
    text = await llm.chat(
        [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=prompt),
        ]
    )
    return {"narrative": text, "provider": llm.name, "facts": facts}
