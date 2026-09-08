from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth import get_jwt_service, get_user_service
from app.auth.dependencies import AuthDependencyService
from app.auth.rbac import PermissionDeniedError
from app.auth.rbac_service import RBACService
from app.auth.service import UserService


router = APIRouter(
    prefix="/protected",
    tags=["Protected"],
)


_rbac_service = RBACService()


def get_rbac_service() -> RBACService:
    return _rbac_service


def get_auth_dependency_service() -> AuthDependencyService:
    return AuthDependencyService(
        get_jwt_service(),
        get_rbac_service(),
    )


@router.get("/me")
async def protected_me(
    authorization: str | None = Header(default=None),
) -> dict:
    auth_service = get_auth_dependency_service()

    try:
        user_id = auth_service.get_current_user_id(
            authorization,
        )
    except HTTPException:
        raise

    user_service: UserService = get_user_service()

    try:
        user = user_service.get_user(user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người dùng.",
        ) from exc

    return {
        "success": True,
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role,
        "message": "Protected API truy cập thành công.",
    }


@router.get("/document/read")
async def protected_document_read(
    authorization: str | None = Header(default=None),
) -> dict:
    auth_service = get_auth_dependency_service()

    user_id = auth_service.get_current_user_id(
        authorization,
    )

    rbac_service = get_rbac_service()

    try:
        rbac_service.require_permission(
            user_id,
            "document.read",
        )
    except PermissionDeniedError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        ) from exc

    return {
        "success": True,
        "user_id": user_id,
        "permission": "document.read",
        "message": "Được phép đọc văn bản.",
    }


@router.get("/document/write")
async def protected_document_write(
    authorization: str | None = Header(default=None),
) -> dict:
    auth_service = get_auth_dependency_service()

    user_id = auth_service.get_current_user_id(
        authorization,
    )

    rbac_service = get_rbac_service()

    try:
        rbac_service.require_permission(
            user_id,
            "document.write",
        )
    except PermissionDeniedError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        ) from exc

    return {
        "success": True,
        "user_id": user_id,
        "permission": "document.write",
        "message": "Được phép ghi văn bản.",
    }