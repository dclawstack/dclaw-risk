from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "DClaw Risk"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_risk"
    cors_origins: str = "*"

    class Config:
        env_prefix = "RISK_"

settings = Settings()
