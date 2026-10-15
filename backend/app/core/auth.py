from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from functools import lru_cache
import httpx
from jose import jwt, JWTError
from jose.utils import base64url_decode
import structlog
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

logger = structlog.get_logger()

security = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class TokenClaims:
    sub: str
    email: Optional[str]
    roles: List[str]
    aud: List[str]
    iss: str
    exp: int
    iat: int
    nonce: Optional[str] = None
    session_state: Optional[str] = None


class OIDCValidator:
    def __init__(self):
        self._jwks: Optional[Dict[str, Any]] = None
        self._jwks_url: Optional[str] = None

    async def _fetch_jwks(self) -> Dict[str, Any]:
        if not settings.oidc_jwks_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OIDC not configured",
            )
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.oidc_jwks_url)
            resp.raise_for_status()
            return resp.json()

    async def get_jwks(self) -> Dict[str, Any]:
        if self._jwks is None or self._jwks_url != settings.oidc_jwks_url:
            self._jwks = await self._fetch_jwks()
            self._jwks_url = settings.oidc_jwks_url
        return self._jwks

    def _get_key(self, kid: str) -> Optional[str]:
        jwks = self._jwks
        if not jwks:
            return None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        return None

    async def validate_token(self, token: str) -> TokenClaims:
        if settings.effective_demo_mode:
            return TokenClaims(
                sub="demo-user",
                email="demo@local",
                roles=["admin", "operator", "viewer"],
                aud=[settings.oidc_client_id or "beacon-station"],
                iss=settings.oidc_issuer_url or "local",
                exp=9999999999,
                iat=0,
                nonce="demo",
            )

        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            if not kid:
                raise JWTError("Missing kid in token header")

            key = self._get_key(kid)
            if not key:
                jwks = await self.get_jwks()
                for k in jwks.get("keys", []):
                    if k.get("kid") == kid:
                        key = jwt.algorithms.RSAAlgorithm.from_jwk(k)
                        break
            if not key:
                raise JWTError(f"Key not found for kid: {kid}")

            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=settings.oidc_client_id,
                issuer=settings.oidc_issuer_url,
                options={"verify_aud": bool(settings.oidc_client_id)},
            )

            roles = claims.get("realm_access", {}).get("roles", [])
            if "offline_access" in roles:
                roles.remove("offline_access")
            if "default-roles-" in str(roles):
                roles = [r for r in roles if not r.startswith("default-roles-")]

            return TokenClaims(
                sub=claims["sub"],
                email=claims.get("email"),
                roles=roles,
                aud=claims.get("aud", []),
                iss=claims["iss"],
                exp=claims["exp"],
                iat=claims["iat"],
                nonce=claims.get("nonce"),
                session_state=claims.get("session_state"),
            )
        except JWTError as e:
            logger.warning("token_validation_failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )


oidc_validator = OIDCValidator()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> TokenClaims:
    if settings.effective_demo_mode and not credentials:
        return TokenClaims(
            sub="demo-user",
            email="demo@local",
            roles=["admin", "operator", "viewer"],
            aud=["beacon-station"],
            iss="local",
            exp=9999999999,
            iat=0,
            nonce="demo",
        )

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await oidc_validator.validate_token(credentials.credentials)


def require_role(*allowed_roles: str):
    async def role_checker(user: TokenClaims = Depends(get_current_user)) -> TokenClaims:
        if not any(role in user.roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {allowed_roles}",
            )
        return user

    return role_checker


class CurrentUser:
    def __init__(self, user: TokenClaims = Depends(get_current_user)):
        self.user = user

    @property
    def id(self) -> str:
        return self.user.sub

    @property
    def email(self) -> Optional[str]:
        return self.user.email

    @property
    def roles(self) -> List[str]:
        return self.user.roles

    def has_role(self, *roles: str) -> bool:
        return any(r in self.user.roles for r in roles)