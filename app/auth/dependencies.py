from __future__ import annotations

from typing import Callable

from fastapi import HTTPException, status

from app.auth.jwt import JWTExpiredError, JWTService, JWTValidationError
from app.auth.rbac import PermissionDeniedError, RBACValidationError
from app.auth.rbac_service import RBACService


class AuthDependencyService:
    """
    FastAPI-facing authentication and authorization helpers.

    JWTService validates the bearer token.
    RBACService validates roles and permissions.
    """

    def __init__(
        self,
        jwt_service: JWTService,
        rbac_service: RBACService,
    ) -> None:
        self.jwt_service = jwt_service
        self.rbac_service = rbac_service

    def get_current_user_id(
        self,
        authorization: str | None,
    ) -> str:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Thiếu Authorization header.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        parts = authorization.strip().split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header không hợp lệ.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = parts[1]

        try:
            payload = self.jwt_service.decode_token(token)
        except JWTExpiredError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token đã hết hạn.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        except (JWTValidationError, ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        subject = payload.get("sub")

        if not isinstance(subject, str) or not subject.strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không chứa user hợp lệ.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return subject

    def require_permission(
        self,
        permission_name: str,
    ) -> Callable:
        if (
            not isinstance(permission_name, str)
            or not permission_name.strip()
        ):
            raise ValueError(
                "permission_name không được để trống."
            )

        async def dependency(
            authorization: str | None = None,
        ) -> str:
            user_id = self.get_current_user_id(
                authorization
            )

            try:
                self.rbac_service.require_permission(
                    user_id,
                    permission_name,
                )
            except (
                RBACValidationError,
                PermissionDeniedError,
            ) as exc:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bạn không có quyền thực hiện thao tác này.",
                ) from exc

            return user_id

        return dependency

    def require_role(
        self,
        role_name: str,
    ) -> Callable:
        if (
            not isinstance(role_name, str)
            or not role_name.strip()
        ):
            raise ValueError(
                "role_name không được để trống."
            )

        async def dependency(
            authorization: str | None = None,
        ) -> str:
            user_id = self.get_current_user_id(
                authorization
            )

            try:
                self.rbac_service.require_role(
                    user_id,
                    role_name,
                )
            except (
                RBACValidationError,
                PermissionDeniedError,
            ) as exc:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bạn không có quyền thực hiện thao tác này.",
                ) from exc

            return user_id

        return dependency