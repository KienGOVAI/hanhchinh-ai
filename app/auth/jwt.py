from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any


class JWTError(ValueError):
    """Base JWT error."""


class JWTValidationError(JWTError):
    """Raised when a JWT is invalid."""


class JWTExpiredError(JWTError):
    """Raised when a JWT has expired."""


@dataclass(frozen=True)
class JWTSettings:
    secret_key: str
    algorithm: str = "HS256"
    expires_in_seconds: int = 3600


class JWTService:
    """Minimal HS256 JWT service without external dependencies."""

    def __init__(
        self,
        secret_key: str | None = None,
        *,
        algorithm: str = "HS256",
        expires_in_seconds: int = 3600,
    ) -> None:
        resolved_secret = secret_key or os.getenv(
            "HANHCHINH_JWT_SECRET",
            "hanhchinh-ai-development-secret-change-me",
        )

        if not isinstance(resolved_secret, str) or len(resolved_secret) < 16:
            raise JWTValidationError(
                "JWT secret_key phải có ít nhất 16 ký tự."
            )

        if algorithm != "HS256":
            raise JWTValidationError(
                "Chỉ hỗ trợ thuật toán HS256."
            )

        if not isinstance(expires_in_seconds, int):
            raise JWTValidationError(
                "expires_in_seconds phải là số nguyên."
            )

        if expires_in_seconds <= 0:
            raise JWTValidationError(
                "expires_in_seconds phải lớn hơn 0."
            )

        self.settings = JWTSettings(
            secret_key=resolved_secret,
            algorithm=algorithm,
            expires_in_seconds=expires_in_seconds,
        )

    def create_token(
        self,
        *,
        subject: str,
        claims: dict[str, Any] | None = None,
        expires_in_seconds: int | None = None,
    ) -> str:
        if not isinstance(subject, str) or not subject.strip():
            raise JWTValidationError("JWT subject không hợp lệ.")

        ttl = (
            self.settings.expires_in_seconds
            if expires_in_seconds is None
            else expires_in_seconds
        )

        if not isinstance(ttl, int) or ttl <= 0:
            raise JWTValidationError(
                "expires_in_seconds phải lớn hơn 0."
            )

        now = int(time.time())

        payload: dict[str, Any] = {
            "sub": subject.strip(),
            "iat": now,
            "exp": now + ttl,
        }

        if claims:
            if not isinstance(claims, dict):
                raise JWTValidationError("claims phải là dict.")

            payload.update(claims)

        # Security-critical registered claims must not be overridden.
        payload["sub"] = subject.strip()
        payload["iat"] = now
        payload["exp"] = now + ttl

        header = {
            "alg": self.settings.algorithm,
            "typ": "JWT",
        }

        encoded_header = self._encode_json(header)
        encoded_payload = self._encode_json(payload)

        signing_input = f"{encoded_header}.{encoded_payload}"

        signature = self._sign(signing_input)

        return f"{signing_input}.{signature}"

    def decode_token(
        self,
        token: str,
        *,
        verify_exp: bool = True,
    ) -> dict[str, Any]:
        if not isinstance(token, str) or not token.strip():
            raise JWTValidationError("JWT token không hợp lệ.")

        parts = token.split(".")

        if len(parts) != 3:
            raise JWTValidationError(
                "JWT phải có đúng 3 phần."
            )

        encoded_header, encoded_payload, encoded_signature = parts

        try:
            header = self._decode_json(encoded_header)
            payload = self._decode_json(encoded_payload)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise JWTValidationError(
                "JWT header hoặc payload không hợp lệ."
            ) from exc

        if header.get("alg") != self.settings.algorithm:
            raise JWTValidationError(
                "JWT algorithm không được hỗ trợ."
            )

        if header.get("typ") != "JWT":
            raise JWTValidationError(
                "JWT type không hợp lệ."
            )

        signing_input = f"{encoded_header}.{encoded_payload}"
        expected_signature = self._sign(signing_input)

        if not hmac.compare_digest(
            encoded_signature,
            expected_signature,
        ):
            raise JWTValidationError(
                "JWT signature không hợp lệ."
            )

        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise JWTValidationError(
                "JWT thiếu subject hợp lệ."
            )

        exp = payload.get("exp")

        if not isinstance(exp, int):
            raise JWTValidationError(
                "JWT thiếu expiration hợp lệ."
            )

        if verify_exp and int(time.time()) >= exp:
            raise JWTExpiredError("JWT đã hết hạn.")

        return payload

    def validate_token(self, token: str) -> bool:
        try:
            self.decode_token(token)
        except JWTError:
            return False

        return True

    def get_subject(self, token: str) -> str:
        payload = self.decode_token(token)
        return str(payload["sub"])

    def _sign(self, signing_input: str) -> str:
        digest = hmac.new(
            self.settings.secret_key.encode("utf-8"),
            signing_input.encode("ascii"),
            hashlib.sha256,
        ).digest()

        return self._b64encode(digest)

    @staticmethod
    def _encode_json(data: dict[str, Any]) -> str:
        raw = json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        return JWTService._b64encode(raw)

    @staticmethod
    def _decode_json(value: str) -> dict[str, Any]:
        raw = JWTService._b64decode(value)

        data = json.loads(raw.decode("utf-8"))

        if not isinstance(data, dict):
            raise ValueError("JWT JSON phải là object.")

        return data

    @staticmethod
    def _b64encode(value: bytes) -> str:
        return (
            base64.urlsafe_b64encode(value)
            .decode("ascii")
            .rstrip("=")
        )

    @staticmethod
    def _b64decode(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)

        return base64.urlsafe_b64decode(
            f"{value}{padding}".encode("ascii")
        )