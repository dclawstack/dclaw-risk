from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routes import health
from app.api.v1 import (
    ai,
    assessments,
    controls,
    culture,
    demo,
    documents,
    emerging,
    incidents,
    integrations,
    kris,
    reports,
    risks,
    scenarios,
    vendors,
)
from app.api.v1.controls import mapping_router as risk_controls_router
from app.core.config import settings
from app.core.database import init_db
from app.core.rate_limit import limiter


def _is_production(app_env: str) -> bool:
    return app_env.lower() in {"prod", "production"}


def assert_safe_config(s=settings) -> None:
    if _is_production(s.app_env) and s.dev_auth_bypass:
        raise RuntimeError(
            "DEV_AUTH_BYPASS=true is not permitted when APP_ENV=production. "
            "Set DEV_AUTH_BYPASS=false and configure LOGTO_JWKS_URI."
        )


assert_safe_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])

# P0
app.include_router(risks.router, prefix="/api/v1/risks", tags=["risks"])
app.include_router(controls.router, prefix="/api/v1/controls", tags=["controls"])
app.include_router(
    risk_controls_router,
    prefix="/api/v1/risks/{risk_id}/controls",
    tags=["risk-controls"],
)
app.include_router(
    assessments.router,
    prefix="/api/v1/risks/{risk_id}/assessments",
    tags=["assessments"],
)
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(
    documents.router, prefix="/api/v1/documents", tags=["knowledge-base"]
)

# P1
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(kris.router, prefix="/api/v1/kris", tags=["kris"])
app.include_router(
    incidents.router, prefix="/api/v1/incidents", tags=["incidents"]
)
app.include_router(integrations.router, prefix="/api/v1", tags=["integrations"])

# P2
app.include_router(
    scenarios.router, prefix="/api/v1/scenarios", tags=["scenarios"]
)
app.include_router(vendors.router, prefix="/api/v1/vendors", tags=["vendors"])
app.include_router(
    emerging.router, prefix="/api/v1/emerging", tags=["emerging-risk"]
)
app.include_router(culture.router, prefix="/api/v1/culture", tags=["culture"])
app.include_router(demo.router, prefix="/api/v1/demo", tags=["demo"])
