from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass
from uuid import uuid4


class AuthValidationError(ValueError):
    """Raised when authentication input is invalid."""


class UserNotFoundError(LookupError):
    """Raised when a user does not exist."""


class InvalidPasswordError(ValueError):
    """Raised when the supplied password is incorrect."""


@dataclass(frozen=True)
class User:
    user_id: str
    username: str
    password_hash: str
    is_active: bool = True
    role: str = "user"


class PasswordHasher:
    """Secure password hashing helper."""

    _ITERATIONS = 120_000
    _SALT_BYTES = 16
    _HASH_BYTES = 32

    @classmethod
    def hash(cls, password: str) -> str:
        cls._validate_password(password)

        salt = __import__("secrets").token_bytes(cls._SALT_BYTES)

        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            cls._ITERATIONS,
            dklen=cls._HASH_BYTES,
        )

        return (
            f"pbkdf2_sha256${cls._ITERATIONS}$"
            f"{salt.hex()}${derived_key.hex()}"
        )

    @classmethod
    def verify(cls, password: str, password_hash: str) -> bool:
        if not isinstance(password, str) or not password:
            return False

        if not isinstance(password_hash, str):
            return False

        parts = password_hash.split("$")

        if len(parts) != 4:
            return False

        algorithm, iterations_text, salt_hex, expected_hash_hex = parts

        if algorithm != "pbkdf2_sha256":
            return False

        try:
            iterations = int(iterations_text)
            salt = bytes.fromhex(salt_hex)
            expected_hash = bytes.fromhex(expected_hash_hex)
        except (TypeError, ValueError):
            return False

        if iterations <= 0 or not salt or not expected_hash:
            return False

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=len(expected_hash),
        )

        return hmac.compare_digest(actual_hash, expected_hash)

    @staticmethod
    def _validate_password(password: str) -> None:
        if not isinstance(password, str):
            raise AuthValidationError("Password phải là chuỗi.")

        if len(password) < 8:
            raise AuthValidationError(
                "Password phải có ít nhất 8 ký tự."
            )


class UserService:
    """In-memory user and password service for Sprint 17.2."""

    USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._username_index: dict[str, str] = {}

    def create_user(
        self,
        *,
        username: str,
        password: str,
        role: str = "user",
        is_active: bool = True,
    ) -> User:
        username = self._normalize_username(username)

        if username in self._username_index:
            raise AuthValidationError("Username đã tồn tại.")

        if not isinstance(role, str) or not role.strip():
            raise AuthValidationError("Role không hợp lệ.")

        PasswordHasher._validate_password(password)

        user = User(
            user_id=str(uuid4()),
            username=username,
            password_hash=PasswordHasher.hash(password),
            is_active=is_active,
            role=role.strip(),
        )

        self._users[user.user_id] = user
        self._username_index[user.username] = user.user_id

        return user

    def get_user(self, user_id: str) -> User:
        if not isinstance(user_id, str) or not user_id.strip():
            raise UserNotFoundError("User ID không hợp lệ.")

        user = self._users.get(user_id)

        if user is None:
            raise UserNotFoundError("Không tìm thấy user.")

        return user

    def get_by_username(self, username: str) -> User:
        username = self._normalize_username(username)

        user_id = self._username_index.get(username)

        if user_id is None:
            raise UserNotFoundError("Không tìm thấy user.")

        return self.get_user(user_id)

    def authenticate(
        self,
        *,
        username: str,
        password: str,
    ) -> User:
        user = self.get_by_username(username)

        if not user.is_active:
            raise AuthValidationError("User đang bị khóa.")

        if not PasswordHasher.verify(
            password,
            user.password_hash,
        ):
            raise InvalidPasswordError("Password không đúng.")

        return user

    def update_password(
        self,
        *,
        user_id: str,
        new_password: str,
    ) -> User:
        user = self.get_user(user_id)

        PasswordHasher._validate_password(new_password)

        updated_user = User(
            user_id=user.user_id,
            username=user.username,
            password_hash=PasswordHasher.hash(new_password),
            is_active=user.is_active,
            role=user.role,
        )

        self._users[user.user_id] = updated_user

        return updated_user

    def deactivate(self, user_id: str) -> User:
        user = self.get_user(user_id)

        updated_user = User(
            user_id=user.user_id,
            username=user.username,
            password_hash=user.password_hash,
            is_active=False,
            role=user.role,
        )

        self._users[user.user_id] = updated_user

        return updated_user

    def activate(self, user_id: str) -> User:
        user = self.get_user(user_id)

        updated_user = User(
            user_id=user.user_id,
            username=user.username,
            password_hash=user.password_hash,
            is_active=True,
            role=user.role,
        )

        self._users[user.user_id] = updated_user

        return updated_user

    def exists(self, user_id: str) -> bool:
        return user_id in self._users

    def count(self) -> int:
        return len(self._users)

    def list_users(self) -> list[User]:
        return list(self._users.values())

    def delete_user(self, user_id: str) -> None:
        user = self.get_user(user_id)

        self._users.pop(user.user_id, None)
        self._username_index.pop(user.username, None)

    @classmethod
    def _normalize_username(cls, username: str) -> str:
        if not isinstance(username, str):
            raise AuthValidationError("Username phải là chuỗi.")

        username = username.strip()

        if not cls.USERNAME_PATTERN.fullmatch(username):
            raise AuthValidationError(
                "Username phải dài 3-50 ký tự và chỉ gồm "
                "chữ, số, dấu chấm, gạch dưới hoặc gạch ngang."
            )

        return username.lower()