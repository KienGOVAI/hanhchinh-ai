"""
Authentication Domain
---------------------

Sprint 17.1 - Authentication Domain.

Domain model cho:
    - User
    - Role
    - UserStatus
    - Authentication validation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


# ============================================================
# ENUMS
# ============================================================


class UserStatus(str, Enum):
    """
    Trạng thái tài khoản người dùng.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"


class UserRole(str, Enum):
    """
    Vai trò người dùng trong hệ thống.
    """

    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"


# ============================================================
# EXCEPTIONS
# ============================================================


class AuthenticationError(Exception):
    """
    Lỗi chung của Authentication Domain.
    """


class AuthenticationValidationError(
    AuthenticationError
):
    """
    Dữ liệu Authentication không hợp lệ.
    """


# ============================================================
# USER
# ============================================================


@dataclass
class User:
    """
    Người dùng của hệ thống Hành Chính AI.

    Domain chưa xử lý:
        - Password hashing
        - JWT
        - Database
        - HTTP

    Các phần trên sẽ được triển khai ở
    các sprint/sub-step tiếp theo.
    """

    username: str
    password_hash: str
    role: UserRole = UserRole.STAFF
    user_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    full_name: str = ""
    status: UserStatus = UserStatus.ACTIVE
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.username = self._validate_username(
            self.username
        )

        self.password_hash = (
            self._validate_password_hash(
                self.password_hash
            )
        )

        if not isinstance(self.role, UserRole):
            try:
                self.role = UserRole(self.role)
            except (TypeError, ValueError) as exc:
                raise AuthenticationValidationError(
                    "role không hợp lệ."
                ) from exc

        if not isinstance(self.status, UserStatus):
            try:
                self.status = UserStatus(self.status)
            except (TypeError, ValueError) as exc:
                raise AuthenticationValidationError(
                    "status không hợp lệ."
                ) from exc

        if not isinstance(self.user_id, str):
            raise AuthenticationValidationError(
                "user_id phải là chuỗi."
            )

        self.user_id = self.user_id.strip()

        if not self.user_id:
            raise AuthenticationValidationError(
                "user_id không được để trống."
            )

        if not isinstance(self.full_name, str):
            raise AuthenticationValidationError(
                "full_name phải là chuỗi."
            )

        self.full_name = self.full_name.strip()

        if not isinstance(self.metadata, dict):
            raise AuthenticationValidationError(
                "metadata phải là dict."
            )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    @staticmethod
    def _validate_username(
        username: str,
    ) -> str:
        if not isinstance(username, str):
            raise AuthenticationValidationError(
                "username phải là chuỗi."
            )

        normalized = username.strip()

        if not normalized:
            raise AuthenticationValidationError(
                "username không được để trống."
            )

        if len(normalized) < 3:
            raise AuthenticationValidationError(
                "username phải có ít nhất 3 ký tự."
            )

        if len(normalized) > 100:
            raise AuthenticationValidationError(
                "username không được vượt quá 100 ký tự."
            )

        if any(character.isspace() for character in normalized):
            raise AuthenticationValidationError(
                "username không được chứa khoảng trắng."
            )

        return normalized

    @staticmethod
    def _validate_password_hash(
        password_hash: str,
    ) -> str:
        if not isinstance(password_hash, str):
            raise AuthenticationValidationError(
                "password_hash phải là chuỗi."
            )

        normalized = password_hash.strip()

        if not normalized:
            raise AuthenticationValidationError(
                "password_hash không được để trống."
            )

        return normalized

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    def is_active(self) -> bool:
        """
        Kiểm tra tài khoản có đang hoạt động hay không.
        """

        return self.status == UserStatus.ACTIVE

    def is_locked(self) -> bool:
        """
        Kiểm tra tài khoản có bị khóa hay không.
        """

        return self.status == UserStatus.LOCKED

    def activate(self) -> None:
        """
        Kích hoạt tài khoản.
        """

        self.status = UserStatus.ACTIVE

    def deactivate(self) -> None:
        """
        Vô hiệu hóa tài khoản.
        """

        self.status = UserStatus.INACTIVE

    def lock(self) -> None:
        """
        Khóa tài khoản.
        """

        self.status = UserStatus.LOCKED

    # --------------------------------------------------------
    # ROLE
    # --------------------------------------------------------

    def has_role(
        self,
        role: UserRole,
    ) -> bool:
        """
        Kiểm tra user có đúng role hay không.
        """

        if not isinstance(role, UserRole):
            try:
                role = UserRole(role)
            except (TypeError, ValueError):
                return False

        return self.role == role

    def change_role(
        self,
        role: UserRole,
    ) -> None:
        """
        Thay đổi role của user.
        """

        if not isinstance(role, UserRole):
            try:
                role = UserRole(role)
            except (TypeError, ValueError) as exc:
                raise AuthenticationValidationError(
                    "role không hợp lệ."
                ) from exc

        self.role = role

    # --------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Chuyển User thành dictionary an toàn cho domain.

        Password hash vẫn được giữ trong domain object,
        nhưng không đưa vào dữ liệu public.
        """

        return {
            "user_id": self.user_id,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role.value,
            "status": self.status.value,
            "metadata": dict(self.metadata),
        }