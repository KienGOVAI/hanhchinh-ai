from __future__ import annotations

from dataclasses import dataclass

from app.auth.dependencies import AuthDependencyService
from app.auth.jwt import JWTService
from app.auth.rbac_service import RBACService
from app.auth.service import UserService


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    username: str
    role: str


class AuthIntegrationService:
    """
    Integrates UserService, JWTService, and RBACService
    into one authentication and authorization boundary.
    """

    def __init__(
        self,
        user_service: UserService,
        jwt_service: JWTService,
        rbac_service: RBACService,
    ) -> None:
        self.user_service = user_service
        self.jwt_service = jwt_service
        self.rbac_service = rbac_service

        self.dependencies = AuthDependencyService(
            jwt_service,
            rbac_service,
        )

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> AuthenticatedUser:
        user = self.user_service.authenticate(
            username=username,
            password=password,
        )

        return AuthenticatedUser(
            user_id=user.user_id,
            username=user.username,
            role=user.role,
        )

    def issue_token(
        self,
        user: AuthenticatedUser,
    ) -> str:
        return self.jwt_service.create_token(
            subject=user.user_id,
            claims={
                "username": user.username,
                "role": user.role,
            },
        )

    def authenticate_and_issue_token(
        self,
        username: str,
        password: str,
    ) -> tuple[AuthenticatedUser, str]:
        user = self.authenticate(
            username,
            password,
        )

        token = self.issue_token(user)

        return user, token

    def get_authenticated_user(
        self,
        authorization: str | None,
    ) -> AuthenticatedUser:
        user_id = self.dependencies.get_current_user_id(
            authorization,
        )

        user = self.user_service.get_user(user_id)

        return AuthenticatedUser(
            user_id=user.user_id,
            username=user.username,
            role=user.role,
        )

    def has_permission(
        self,
        authorization: str | None,
        permission_name: str,
    ) -> bool:
        user = self.get_authenticated_user(
            authorization,
        )

        return self.rbac_service.has_permission(
            user.user_id,
            permission_name,
        )

    def require_permission(
        self,
        authorization: str | None,
        permission_name: str,
    ) -> AuthenticatedUser:
        user = self.get_authenticated_user(
            authorization,
        )

        self.rbac_service.require_permission(
            user.user_id,
            permission_name,
        )

        return user

    def require_role(
        self,
        authorization: str | None,
        role_name: str,
    ) -> AuthenticatedUser:
        user = self.get_authenticated_user(
            authorization,
        )

        self.rbac_service.require_role(
            user.user_id,
            role_name,
        )

        return user
