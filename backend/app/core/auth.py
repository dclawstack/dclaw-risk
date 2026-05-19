"""Logto JWT auth dependency.

Production path verifies bearer tokens against Logto JWKS.
Dev path (DEV_AUTH_BYPASS=true) returns a stub user so the API is usable
without a Logto tenant configured.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx
import structlog
from fastapi import Depends, HTTPException, Request, status

try:
    from jose import jwt
    from jose.exceptions import JWTError
except ModuleNotFoundError:  # pragma: no cover - fallback when jose isn't installed
    jwt = None  # type: ignore[assignment]

    class JWTError(Exception):  # type: ignore[no-redef]
        pass


from app.core.config import settings

log = structlog.get_logger(__name__)


@dataclass
class User:
    sub: str
    email: str | None = None
    name: str | None = None

    @property
    def is_dev_user(self) -> bool:
        return self.sub == "dev-user"


_DEV_USER = User(sub="dev-user", email="dev@dclaw.local", name="Dev User")


_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    if not settings.logto_jwks_uri:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LOGTO_JWKS_URI not configured",
        )
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(settings.logto_jwks_uri)
        resp.raise_for_status()
        _jwks_cache = resp.json()
    return _jwks_cache


async def _verify_logto_token(token: str) -> User:
    if jwt is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="python-jose not installed; cannot verify JWTs",
        )
    jwks = await _get_jwks()
    try:
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get("kid")
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if key is None:
            raise JWTError("kid not in JWKS")
        claims = jwt.decode(
            token,
            key,
            algorithms=[key.get("alg", "RS256")],
            audience=settings.logto_audience or None,
            issuer=settings.logto_issuer or None,
        )
    except JWTError as e:
        log.info("auth.invalid_token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        ) from e
    return User(
        sub=claims.get("sub", "unknown"),
        email=claims.get("email"),
        name=claims.get("name") or claims.get("username"),
    )


async def get_current_user(request: Request) -> User:
    if settings.dev_auth_bypass:
        return _DEV_USER

    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token"
        )
    token = auth.split(" ", 1)[1].strip()
    return await _verify_logto_token(token)


CurrentUser = Depends(get_current_user)
