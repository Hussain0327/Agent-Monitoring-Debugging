"""Authentication endpoints: register and login."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from vigil_server.dependencies import DBSession  # noqa: TC001
from vigil_server.models.user import User
from vigil_server.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from vigil_server.services.auth_service import (
    create_access_token,
    get_user_by_email,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: DBSession) -> UserResponse:
    """Register a new user account."""
    existing = await get_user_by_email(db, body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.post("/login")
async def login(body: LoginRequest, db: DBSession) -> TokenResponse:
    """Authenticate and return a JWT access token."""
    user = await get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token)
