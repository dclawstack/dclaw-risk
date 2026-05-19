from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models import Risk
from app.models.scenario import Scenario
from app.schemas.scenario import (
    GenerateScenarioRequest,
    GenerateScenarioResponse,
    ScenarioCreate,
    ScenarioList,
    ScenarioRead,
    ScenarioUpdate,
    StressTestResponse,
    StressTestRow,
)
from app.services.risk_ai import generate_scenario as ai_generate_scenario

router = APIRouter()


@router.get("", response_model=ScenarioList)
async def list_scenarios(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ScenarioList:
    rows = (await db.execute(select(Scenario))).scalars().all()
    total = (
        (await db.execute(select(func.count()).select_from(Scenario))).scalar() or 0
    )
    return ScenarioList(
        items=[ScenarioRead.model_validate(s) for s in rows], total=total
    )


@router.post("", response_model=ScenarioRead, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    payload: ScenarioCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ScenarioRead:
    s = Scenario(
        name=payload.name,
        description=payload.description,
        multipliers={k: v.model_dump() for k, v in payload.multipliers.items()},
    )
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return ScenarioRead.model_validate(s)


@router.get("/{scenario_id}", response_model=ScenarioRead)
async def get_scenario(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ScenarioRead:
    s = (
        await db.execute(select(Scenario).where(Scenario.id == scenario_id))
    ).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="scenario not found")
    return ScenarioRead.model_validate(s)


@router.patch("/{scenario_id}", response_model=ScenarioRead)
async def update_scenario(
    scenario_id: UUID,
    payload: ScenarioUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ScenarioRead:
    s = (
        await db.execute(select(Scenario).where(Scenario.id == scenario_id))
    ).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="scenario not found")
    data = payload.model_dump(exclude_unset=True)
    if "multipliers" in data and data["multipliers"] is not None:
        data["multipliers"] = {
            k: v if isinstance(v, dict) else v.model_dump()
            for k, v in data["multipliers"].items()
        }
    for field, value in data.items():
        setattr(s, field, value)
    await db.commit()
    await db.refresh(s)
    return ScenarioRead.model_validate(s)


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    s = (
        await db.execute(select(Scenario).where(Scenario.id == scenario_id))
    ).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="scenario not found")
    await db.delete(s)
    await db.commit()


@router.post("/{scenario_id}/stress-test", response_model=StressTestResponse)
async def stress_test(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StressTestResponse:
    scenario = (
        await db.execute(select(Scenario).where(Scenario.id == scenario_id))
    ).scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="scenario not found")

    risks = (await db.execute(select(Risk))).scalars().all()
    rows: list[StressTestRow] = []
    baseline_total = 0
    projected_total = 0.0
    for r in risks:
        baseline = r.severity * r.probability
        mult = scenario.multipliers.get(r.category) or {}
        sev_m = float(mult.get("severity", 1.0))
        prob_m = float(mult.get("probability", 1.0))
        proj_sev = min(5.0, r.severity * sev_m)
        proj_prob = min(5.0, r.probability * prob_m)
        proj_score = proj_sev * proj_prob
        baseline_total += baseline
        projected_total += proj_score
        rows.append(
            StressTestRow(
                risk_id=r.id,
                name=r.name,
                category=r.category,
                baseline_score=baseline,
                projected_severity=round(proj_sev, 2),
                projected_probability=round(proj_prob, 2),
                projected_score=round(proj_score, 2),
            )
        )
    delta_pct = (
        100.0 * (projected_total - baseline_total) / baseline_total
        if baseline_total
        else 0.0
    )
    return StressTestResponse(
        scenario_id=scenario_id,
        baseline_total=baseline_total,
        projected_total=round(projected_total, 2),
        delta_pct=round(delta_pct, 1),
        rows=rows,
    )


@router.post("/generate", response_model=GenerateScenarioResponse)
async def generate(
    payload: GenerateScenarioRequest,
    user: User = Depends(get_current_user),
) -> GenerateScenarioResponse:
    return await ai_generate_scenario(payload.context)
