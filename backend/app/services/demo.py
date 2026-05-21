"""Seed + clear demo data used by the marketing landing page.

`seed()` inserts an illustrative dataset that exercises every feature
(P0..P2 + RAG) so a visitor can land on /dashboard and see every page
populated. `clear()` deletes ALL rows from the domain tables — it's
intentionally a full reset so the demo button always starts clean.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Assessment,
    Control,
    CultureScore,
    Document,
    EmergingRisk,
    Incident,
    KRI,
    Risk,
    RiskControl,
    Scenario,
    Survey,
    SurveyQuestion,
    SurveyResponse,
    Vendor,
)


@dataclass
class DemoCounts:
    risks: int
    controls: int
    risk_controls: int
    assessments: int
    incidents: int
    kris: int
    scenarios: int
    vendors: int
    emerging: int
    culture: int
    surveys: int
    documents: int

    def to_dict(self) -> dict:
        return self.__dict__

    @property
    def is_empty(self) -> bool:
        return all(v == 0 for v in self.__dict__.values())


async def status(db: AsyncSession) -> DemoCounts:
    async def n(model) -> int:
        return (
            await db.execute(select(func.count()).select_from(model))
        ).scalar() or 0

    return DemoCounts(
        risks=await n(Risk),
        controls=await n(Control),
        risk_controls=await n(RiskControl),
        assessments=await n(Assessment),
        incidents=await n(Incident),
        kris=await n(KRI),
        scenarios=await n(Scenario),
        vendors=await n(Vendor),
        emerging=await n(EmergingRisk),
        culture=await n(CultureScore),
        surveys=await n(Survey),
        documents=await n(Document),
    )


async def clear(db: AsyncSession) -> DemoCounts:
    """Wipe all domain tables. FK cascades handle dependencies."""
    before = await status(db)
    # Tables with no inbound FKs go last; everything else is parent → child.
    # Most cascades are already wired with ondelete=CASCADE, but we delete
    # explicitly so the counts returned reflect what was removed.
    for model in (
        SurveyResponse,
        SurveyQuestion,
        Survey,
        Assessment,
        RiskControl,
        KRI,
        Incident,
        Risk,
        Control,
        Scenario,
        Vendor,
        EmergingRisk,
        CultureScore,
        Document,
    ):
        await db.execute(delete(model))
    await db.commit()
    return before


async def seed(db: AsyncSession) -> DemoCounts:
    """Insert the demo dataset. Safe to call when DB is empty; if you
    want a clean run, call clear() first."""
    now = datetime.now(timezone.utc)

    # --- Controls ----------------------------------------------------------
    ctrl_mfa = Control(
        name="MFA on all admin accounts",
        description="Hardware-backed MFA required for any account with elevated privileges.",
        framework="NIST 800-53",
        control_type="preventive",
        effectiveness=4,
        owner="demo",
    )
    ctrl_siem = Control(
        name="SIEM log review (24/7 SOC)",
        description="Centralised log analysis with anomaly detection.",
        framework="SOC 2",
        control_type="detective",
        effectiveness=4,
        owner="demo",
    )
    ctrl_ir = Control(
        name="Incident response runbook",
        description="Documented playbook for Sev-1 / Sev-2 incidents.",
        framework="ISO 27001",
        control_type="corrective",
        effectiveness=3,
        owner="demo",
    )
    ctrl_multiregion = Control(
        name="Multi-region active-active",
        description="Production traffic load-balanced across us-east-1 and us-west-2.",
        framework="NIST 800-53",
        control_type="preventive",
        effectiveness=5,
        owner="demo",
    )
    db.add_all([ctrl_mfa, ctrl_siem, ctrl_ir, ctrl_multiregion])

    # --- Risks -------------------------------------------------------------
    r_cloud = Risk(
        name="Cloud provider outage",
        description="Loss of AWS us-east-1 availability affecting customer-facing services.",
        category="Operational",
        status="assessed",
        owner="demo",
        severity=4,
        probability=3,
        velocity=4,
    )
    r_breach = Risk(
        name="Customer PII data breach",
        description="Unauthorised exfiltration of customer personal data via insider or external attacker.",
        category="Cybersecurity",
        status="treated",
        owner="demo",
        severity=5,
        probability=3,
        velocity=3,
    )
    r_fx = Risk(
        name="FX volatility on EUR receivables",
        description="EUR/USD swings on ~30% of receivables denominated in EUR.",
        category="Financial",
        status="monitored",
        owner="demo",
        severity=3,
        probability=4,
        velocity=2,
    )
    r_gdpr = Risk(
        name="GDPR enforcement penalty",
        description="Regulator action over data-retention non-compliance.",
        category="Compliance",
        status="identified",
        owner="demo",
        severity=4,
        probability=2,
        velocity=2,
    )
    r_vendor = Risk(
        name="Critical SaaS vendor failure",
        description="Outage at a tier-1 vendor providing SSO / identity for all employees.",
        category="Third-Party",
        status="identified",
        owner="demo",
        severity=4,
        probability=3,
        velocity=5,
    )
    db.add_all([r_cloud, r_breach, r_fx, r_gdpr, r_vendor])
    await db.flush()

    # --- Risk ↔ Control mappings ------------------------------------------
    db.add_all(
        [
            RiskControl(risk_id=r_cloud.id, control_id=ctrl_multiregion.id, effectiveness=5),
            RiskControl(risk_id=r_cloud.id, control_id=ctrl_ir.id, effectiveness=3),
            RiskControl(risk_id=r_breach.id, control_id=ctrl_mfa.id, effectiveness=4),
            RiskControl(risk_id=r_breach.id, control_id=ctrl_siem.id, effectiveness=4),
            RiskControl(risk_id=r_vendor.id, control_id=ctrl_ir.id, effectiveness=3),
        ]
    )

    # --- Assessments -------------------------------------------------------
    db.add(
        Assessment(
            risk_id=r_breach.id,
            kind="qualitative",
            severity=5,
            probability=3,
            assessor="demo",
        )
    )
    # A pre-computed quantitative result so /reports/exposure shows numbers
    # immediately without waiting for a Monte Carlo run.
    db.add(
        Assessment(
            risk_id=r_breach.id,
            kind="quantitative",
            assessor="demo",
            loss_min=50_000,
            loss_mode=500_000,
            loss_max=3_000_000,
            freq_min=0.1,
            freq_max=1.0,
            iterations=10_000,
            loss_p10=88_000,
            loss_p50=320_000,
            loss_p90=911_000,
            loss_mean=419_000,
            curve=[
                {"loss": 9_000, "exceedance_probability": 1.0},
                {"loss": 88_000, "exceedance_probability": 0.9},
                {"loss": 320_000, "exceedance_probability": 0.5},
                {"loss": 911_000, "exceedance_probability": 0.1},
                {"loss": 1_700_000, "exceedance_probability": 0.01},
            ],
        )
    )

    # --- KRIs --------------------------------------------------------------
    db.add_all(
        [
            KRI(
                name="Failed admin logins per hour",
                unit="count",
                current_value=240,
                threshold_warn=100,
                threshold_critical=200,
                direction="above",
                risk_id=r_breach.id,
                owner="demo",
            ),
            KRI(
                name="P99 API latency",
                unit="ms",
                current_value=150,
                threshold_warn=200,
                threshold_critical=400,
                direction="above",
                risk_id=r_cloud.id,
                owner="demo",
            ),
            KRI(
                name="Patch coverage",
                unit="%",
                current_value=78,
                threshold_warn=80,
                threshold_critical=60,
                direction="below",
                owner="demo",
            ),
        ]
    )

    # --- Incidents ---------------------------------------------------------
    db.add_all(
        [
            Incident(
                title="CDN edge timeout — us-east-1",
                description="Traffic stalled 14:02-14:11 UTC; 0.4% of requests affected.",
                severity=3,
                occurred_at=now - timedelta(days=3),
                risk_id=r_cloud.id,
                status="resolved",
            ),
            Incident(
                title="Suspicious admin login attempt",
                description="Account locked after 50 failed attempts from a single IP.",
                severity=4,
                occurred_at=now - timedelta(days=2),
                risk_id=r_breach.id,
                status="investigating",
            ),
            Incident(
                title="Repeat CDN slowdown — same region",
                description="Brief P99 latency spike following a deploy.",
                severity=2,
                occurred_at=now - timedelta(hours=12),
                risk_id=r_cloud.id,
                status="resolved",
            ),
        ]
    )

    # --- Scenario ----------------------------------------------------------
    db.add(
        Scenario(
            name="Severe regional outage + cyber pressure",
            description="Combined operational disruption and elevated cyber attack rate.",
            multipliers={
                "Operational": {"severity": 1.4, "probability": 1.3},
                "Cybersecurity": {"severity": 1.5, "probability": 1.4},
                "Financial": {"severity": 1.2, "probability": 1.1},
                "Third-Party": {"severity": 1.3, "probability": 1.2},
            },
        )
    )

    # --- Vendors -----------------------------------------------------------
    db.add_all(
        [
            Vendor(
                name="Acme Identity SaaS",
                notes="Holds SSO for all internal apps. Disclosed breach in 2025.",
                category="Identity",
                criticality=5,
                score=78,
                last_assessed_at=now - timedelta(days=14),
                ai_rationale="High criticality and recent breach history elevate exposure.",
            ),
            Vendor(
                name="Globex Payment Processor",
                notes="Processes ~40% of customer payments. PCI-DSS Level 1 certified.",
                category="Payments",
                criticality=4,
                score=45,
                last_assessed_at=now - timedelta(days=30),
                ai_rationale="Strong certification but high criticality keeps score elevated.",
            ),
        ]
    )

    # --- Emerging risk signal ---------------------------------------------
    db.add(
        EmergingRisk(
            title="(demo) Critical CVE in widely-used auth library",
            source="demo-feed",
            url="https://example.com/cve-demo",
            summary="A hypothetical critical CVE in a popular OSS auth library used in many SaaS stacks.",
            detected_at=now - timedelta(hours=6),
            impact_score=5,
            status="new",
        )
    )

    # --- Culture score ----------------------------------------------------
    db.add(
        CultureScore(
            period="2026-Q2",
            dimension="Speak-up",
            score=72,
            benchmark=65,
            notes="From employee survey, n=148.",
        )
    )

    # --- Surveys ----------------------------------------------------------
    survey = Survey(
        name="(demo) Q2 risk culture pulse",
        period="2026-Q2",
        description="Quarterly check on speak-up safety and tone-at-top.",
        status="open",
    )
    db.add(survey)
    await db.flush()
    db.add_all(
        [
            SurveyQuestion(
                survey_id=survey.id,
                dimension="Speak-up",
                prompt="I feel safe raising risk concerns.",
                order_index=0,
            ),
            SurveyQuestion(
                survey_id=survey.id,
                dimension="Tone-at-top",
                prompt="Leadership models risk-aware behaviour.",
                order_index=1,
            ),
        ]
    )

    # --- Documents (RAG) --------------------------------------------------
    db.add_all(
        [
            Document(
                title="Vendor onboarding policy",
                source="demo",
                content=(
                    "Tier-1 vendors (those handling production data or "
                    "authentication) must complete a SIG Lite questionnaire, "
                    "provide their latest SOC 2 Type II report, and submit to "
                    "a 90-day re-attestation cycle. Tier-2 vendors require an "
                    "annual attestation."
                ),
            ),
            Document(
                title="Cloud disaster recovery runbook",
                source="demo",
                content=(
                    "For loss of the us-east-1 region, fail over traffic to "
                    "us-west-2 via Route53 health checks. Target RTO is 30 "
                    "minutes; RPO is 5 minutes for transactional data. "
                    "Notify the incident commander before initiating."
                ),
            ),
        ]
    )

    await db.commit()
    return await status(db)
