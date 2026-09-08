from __future__ import annotations

from app.auth.rbac import (
    Permission,
    PermissionDeniedError,
    RBACPolicy,
    RBACValidationError,
    Role,
)


class RBACService:
    """
    Application service for role-based access control.

    The service owns an RBACPolicy and maintains user -> role
    assignments in memory.
    """

    def __init__(self, policy: RBACPolicy | None = None) -> None:
        self.policy = policy or RBACPolicy()
        self._user_roles: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Permission management
    # ------------------------------------------------------------------

    def create_permission(
        self,
        name: str,
        description: str = "",
    ) -> Permission:
        permission = Permission(
            name=name,
            description=description,
        )
        return self.policy.add_permission(permission)

    def get_permission(self, name: str) -> Permission:
        return self.policy.get_permission(name)

    def list_permissions(self) -> list[Permission]:
        return list(self.policy.permissions.values())

    # ------------------------------------------------------------------
    # Role management
    # ------------------------------------------------------------------

    def create_role(
        self,
        name: str,
        permissions: set[str] | None = None,
    ) -> Role:
        role = Role(
            name=name,
            permissions=permissions or set(),
        )

        for permission_name in role.permissions:
            self.policy.get_permission(permission_name)

        return self.policy.add_role(role)

    def get_role(self, name: str) -> Role:
        return self.policy.get_role(name)

    def list_roles(self) -> list[Role]:
        return list(self.policy.roles.values())

    def grant_permission(
        self,
        role_name: str,
        permission_name: str,
    ) -> None:
        self.policy.grant(
            role_name,
            permission_name,
        )

    def revoke_permission(
        self,
        role_name: str,
        permission_name: str,
    ) -> None:
        self.policy.revoke(
            role_name,
            permission_name,
        )

    # ------------------------------------------------------------------
    # User -> Role assignment
    # ------------------------------------------------------------------

    def assign_role(
        self,
        user_id: str,
        role_name: str,
    ) -> Role:
        user_key = self._normalize_user_id(user_id)
        role = self.policy.get_role(role_name)

        self._user_roles[user_key] = role.name

        return role

    def remove_role(
        self,
        user_id: str,
    ) -> None:
        user_key = self._normalize_user_id(user_id)
        self._user_roles.pop(user_key, None)

    def get_user_role(
        self,
        user_id: str,
    ) -> Role:
        user_key = self._normalize_user_id(user_id)

        role_name = self._user_roles.get(user_key)

        if role_name is None:
            raise RBACValidationError(
                f"User chưa được gán role: {user_id}"
            )

        return self.policy.get_role(role_name)

    def has_role(
        self,
        user_id: str,
        role_name: str,
    ) -> bool:
        try:
            role = self.get_user_role(user_id)
        except RBACValidationError:
            return False

        return role.name == self._normalize_role_name(role_name)

    # ------------------------------------------------------------------
    # Authorization
    # ------------------------------------------------------------------

    def has_permission(
        self,
        user_id: str,
        permission_name: str,
    ) -> bool:
        try:
            role = self.get_user_role(user_id)
            return role.has_permission(permission_name)
        except RBACValidationError:
            return False

    def require_permission(
        self,
        user_id: str,
        permission_name: str,
    ) -> None:
        role = self.get_user_role(user_id)

        if not role.has_permission(permission_name):
            raise PermissionDeniedError(
                f"User '{user_id}' không có permission "
                f"'{permission_name}'."
            )

    def require_role(
        self,
        user_id: str,
        role_name: str,
    ) -> None:
        if not self.has_role(user_id, role_name):
            raise PermissionDeniedError(
                f"User '{user_id}' không có role "
                f"'{role_name}'."
            )

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def get_user_roles(self) -> dict[str, str]:
        return dict(self._user_roles)

    def clear(self) -> None:
        self.policy.roles.clear()
        self.policy.permissions.clear()
        self._user_roles.clear()

    @staticmethod
    def _normalize_user_id(user_id: str) -> str:
        if not isinstance(user_id, str) or not user_id.strip():
            raise RBACValidationError(
                "user_id không được để trống."
            )

        return user_id.strip()

    @staticmethod
    def _normalize_role_name(role_name: str) -> str:
        if not isinstance(role_name, str) or not role_name.strip():
            raise RBACValidationError(
                "role_name không được để trống."
            )

        return role_name.strip().lower()