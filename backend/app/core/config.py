from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    app_name: str = "DClaw Risk"
    app_env: str = "dev"
    debug: bool = True

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_risk"
    )

    cors_origins: list[str] = ["http://localhost:3092"]

    # Auth (Logto)
    logto_issuer: str = ""
    logto_jwks_uri: str = ""
    logto_audience: str = ""
    dev_auth_bypass: bool = True

    # DClaw Compliance integration (P1.4). Empty URL → mock-mode fixture.
    compliance_base_url: str = ""
    compliance_mock_mode: bool = True

    # LLM providers
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    openrouter_api_key: str = ""
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    llm_request_timeout_s: float = 60.0


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
