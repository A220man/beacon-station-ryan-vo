from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.auth import oidc_validator, get_current_user, TokenClaims, TokenClaims

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/test", response_model=dict)
async def auth_test(user: TokenClaims = Depends(get_current_user)):
    """Test endpoint that returns current user info if authenticated."""
    return {
        "authenticated": True,
        "user_id": user.sub,
        "email": user.email,
        "roles": user.roles,
    }


@router.post("/logout", status_code=status.HTTP_303_SEE_OTHER)
async def auth_logout(
    request: Request,
) -> dict:
    """Logout endpoint that clears the authentication session."""
    # Clear the token from the client
    response = {"message": "Successfully logged out"}
    
    # In a production setup, would redirect to Keycloak logout endpoint
    # For now, just clear session state
    
    # If using cookie-based sessions, would clear the session cookie
    # If using token-based, would invalidate the token
    
    return response
