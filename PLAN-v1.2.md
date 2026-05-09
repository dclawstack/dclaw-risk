# DClaw Risk — v1.2 Feature Roadmap

> Based on: Y Combinator vertical SaaS principles, trending GitHub repos (openfair, riskquant), AI product research (RiskLens, LogicGate, MetricStream, ServiceNow GRC)

## Pre-Flight Checklist

- [ ] `frontend/package-lock.json` committed after any `npm install` / dependency change
- [ ] `frontend/next-env.d.ts` exists and is committed
- [ ] `docker-compose.yml` healthchecks correct
- [ ] `frontend/Dockerfile` declares `ARG NEXT_PUBLIC_API_URL` before `RUN npm run build`

## v1.0 Feature Inventory (Current)

- [ ] Risk register CRUD
- [ ] Risk assessment scoring
- [ ] Basic heat maps
- [ ] Mitigation tracking
- [ ] Real backend CRUD (no mocks)
- [ ] Docker + Helm deployment
- [ ] Alembic migrations
- [ ] Backend tests

---

## v1.2 Roadmap

### P0 — Must Have (Ship in v1.0, demo-ready)

#### 1. AI Risk Copilot (Risk Analyst)
**Description:** AI assistant that identifies risks, suggests mitigations, and predicts risk exposure. "What are the top 5 risks for our cloud migration project?"
- **AI Angle:** Risk identification from project data. Mitigation suggestion. Exposure prediction.
- **Backend:** `/api/v1/ai/risk-chat` endpoint. Risk analysis pipeline.
- **Frontend:** Chat with risk context. Risk dashboard with AI insights.
- **Files:** `backend/app/services/risk_ai.py`, `frontend/src/components/risk-copilot.tsx`

#### 2. Quantitative Risk Scoring (FAIR)
**Description:** Factor Analysis of Information Risk methodology for quantitative risk assessment.
- **Backend:** FAIR calculator with Monte Carlo simulation.
- **Frontend:** Risk quantification wizard. Loss exceedance curve.
- **Files:** `backend/app/services/fair_calculator.py`

#### 3. Risk Heat Maps & Visualization
**Description:** Interactive risk matrices with drill-down. Multiple dimensions (impact × likelihood × velocity).
- **Backend:** Risk aggregation engine.
- **Frontend:** Interactive heat map with filters. Trend overlay.
- **Files:** `frontend/src/app/risks/heat-map.tsx`

#### 4. Risk Register & Workflow
**Description:** Full risk lifecycle: identify → assess → treat → monitor → close.
- **Backend:** Risk workflow with approval gates.
- **Frontend:** Risk register with status pipeline.
- **Files:** `backend/app/services/risk_workflow.py`

### P1 — Should Have (v1.1–1.2)

#### 5. AI Risk Prediction & Trending
**Description:** AI analyzes historical data to predict emerging risks and trends.
- **AI Angle:** Time-series analysis + anomaly detection for risk indicators.
- **Backend:** Risk prediction models.
- **Frontend:** Risk forecast dashboard.

#### 6. Scenario Analysis & Stress Testing
**Description:** Model scenarios and stress tests to evaluate risk resilience.
- **Backend:** Scenario modeling engine.
- **Frontend:** Scenario builder with impact visualization.

#### 7. Control Effectiveness Assessment
**Description:** Track control performance and map to risk mitigation.
- **Backend:** Control-Risk mapping with effectiveness scoring.
- **Frontend:** Control effectiveness dashboard.

#### 8. Risk Reporting & Dashboards
**Description:** Executive and operational risk reports with KPIs and trends.
- **Backend:** Report builder with risk KPIs.
- **Frontend:** Customizable dashboards. Executive summary generator.

### P2 — Could Have (v1.3+)

#### 9. Third-Party Risk Scoring
**Description:** Aggregate risk scores from vendor assessments and external threat intel.

#### 10. AI Threat Intelligence Integration
**Description:** Auto-correlate threat intelligence with organizational risk posture.

#### 11. Real-Time Risk Monitoring
**Description:** Continuous risk indicator monitoring with automated alerting.

#### 12. Risk-Adjusted Project Portfolio
**Description:** Portfolio view of all projects with aggregate risk exposure.

---

## Implementation Priority

1. **Week 1–2:** AI Risk Copilot (P0.1) + FAIR Scoring (P0.2)
2. **Week 3–4:** Heat Maps (P0.3) + Risk Register (P0.4)
3. **Week 5–6:** Risk Prediction (P1.5) + Scenario Analysis (P1.6)
4. **Week 7–8:** Control Assessment (P1.7) + Risk Reporting (P1.8)
