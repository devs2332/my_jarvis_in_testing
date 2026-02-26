"""
Authentication API endpoints.
"""

import uuid
from fastapi import APIRouter, HTTPException, status

from server.app.dependencies import DBSession, CurrentUser
from server.app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshRequest, UserResponse,
)
from server.app.services.auth_service import (
    register_user, login_user, refresh_tokens, AuthenticationError,
)
from server.app.core.security import verify_refresh_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(request: RegisterRequest, db: DBSession):
    """Register a new user account."""
    try:
        user, access_token, refresh_token = await register_user(
            db, request.email, request.password, request.full_name,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: DBSession):
    """Authenticate and get access tokens."""
    try:
        user, access_token, refresh_token = await login_user(
            db, request.email, request.password,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e),
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest, db: DBSession):
    """Refresh access token using a valid refresh token."""
    payload = verify_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = uuid.UUID(payload["sub"])
    access_token, refresh_token = await refresh_tokens(db, user_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: CurrentUser):
    """Get the current authenticated user's profile."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
    )
