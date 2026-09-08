from __future__ import annotations

from dataclasses import dataclass, field


class RBACError(Exception):
    """Base exception for RBAC errors."""


class RBACValidationError(RBACError):
    """Raised when RBAC input is invalid."""


class PermissionDeniedError(RBACError):
    """Raised when a user does not have the required permission."""


@dataclass(frozen=True)
class Permission:
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise RBACValidationError("Permission name không được để trống.")

    def normalized_name(self) -> str:
        return self.name.strip().lower()


@dataclass
class Role:
    name: str
    permissions: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise RBACValidationError("Role name không được để trống.")

        self.name = self.name.strip().lower()
        self.permissions = {
            self._normalize_permission(permission)
            for permission in self.permissions
        }

    @staticmethod
    def _normalize_permission(permission: str) -> str:
        if not isinstance(permission, str) or not permission.strip():
            raise RBACValidationError("Permission không được để trống.")
        return permission.strip().lower()

    def add_permission(self, permission: str) -> None:
        self.permissions.add(self._normalize_permission(permission))

    def remove_permission(self, permission: str) -> None:
        self.permissions.discard(self._normalize_permission(permission))

    def has_permission(self, permission: str) -> bool:
        return self._normalize_permission(permission) in self.permissions


@dataclass
class RBACPolicy:
    roles: dict[str, Role] = field(default_factory=dict)
    permissions: dict[str, Permission] = field(default_factory=dict)

    def add_permission(self, permission: Permission) -> Permission:
        if not isinstance(permission, Permission):
            raise RBACValidationError("permission phải là Permission.")

        key = permission.normalized_name()
        self.permissions[key] = permission
        return permission

    def get_permission(self, name: str) -> Permission:
        key = self._normalize_name(name)

        try:
            return self.permissions[key]
        except KeyError as exc:
            raise RBACValidationError(
                f"Permission không tồn tại: {name}"
            ) from exc

    def add_role(self, role: Role) -> Role:
        if not isinstance(role, Role):
            raise RBACValidationError("role phải là Role.")

        self.roles[role.name] = role
        return role

    def get_role(self, name: str) -> Role:
        key = self._normalize_name(name)

        try:
            return self.roles[key]
        except KeyError as exc:
            raise RBACValidationError(
                f"Role không tồn tại: {name}"
            ) from exc

    def grant(self, role_name: str, permission_name: str) -> None:
        role = self.get_role(role_name)
        permission = self.get_permission(permission_name)
        role.add_permission(permission.name)

    def revoke(self, role_name: str, permission_name: str) -> None:
        role = self.get_role(role_name)
        role.remove_permission(permission_name)

    def allows(self, role_name: str, permission_name: str) -> bool:
        role = self.get_role(role_name)
        return role.has_permission(permission_name)

    def require(self, role_name: str, permission_name: str) -> None:
        if not self.allows(role_name, permission_name):
            raise PermissionDeniedError(
                f"Role '{role_name}' không có permission "
                f"'{permission_name}'."
            )

    @staticmethod
    def _normalize_name(value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise RBACValidationError("Tên không được để trống.")
        return value.strip().lower()