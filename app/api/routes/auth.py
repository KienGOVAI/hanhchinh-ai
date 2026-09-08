from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.auth.jwt import JWTService, JWTValidationError
from app.auth.service import (
    AuthValidationError,
    InvalidPasswordError,
    UserNotFoundError,
    UserService,
)
from app.schemas.auth import LoginRequest, LoginResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


_user_service = UserService()
_jwt_service = JWTService()


def get_user_service() -> UserService:
    return _user_service


def get_jwt_service() -> JWTService:
    return _jwt_service


def configure_auth_services(
    user_service: UserService,
    jwt_service: JWTService,
) -> None:
    global _user_service
    global _jwt_service

    _user_service = user_service
    _jwt_service = jwt_service


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(request: LoginRequest) -> LoginResponse:
    try:
        user = _user_service.authenticate(
            username=request.username,
            password=request.password,
        )

    except (
        UserNotFoundError,
        InvalidPasswordError,
        AuthValidationError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username hoặc password không đúng.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    try:
        token = _jwt_service.create_token(
            subject=user.user_id,
            claims={
                "username": user.username,
                "role": user.role,
            },
        )

    except JWTValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo access token.",
        ) from exc

    return LoginResponse(
        success=True,
        access_token=token,
        token_type="bearer",
        expires_in=_jwt_service.settings.expires_in_seconds,
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        message="Đăng nhập thành công.",
    )