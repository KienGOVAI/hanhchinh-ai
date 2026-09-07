"""
Conversation Message Domain Model.

Định nghĩa một tin nhắn trong cuộc hội thoại
giữa người dùng và AI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


ConversationRole = Literal[
    "system",
    "user",
    "assistant",
]


@dataclass(slots=True)
class ConversationMessage:
    """
    Đại diện một tin nhắn trong cuộc hội thoại.
    """

    # =====================================================
    # Identity
    # =====================================================

    role: ConversationRole

    content: str

    # =====================================================
    # Metadata
    # =====================================================

    created_at: datetime = field(
        default_factory=datetime.now
    )

    model: str = ""

    provider: str = ""

    tokens: int = 0

    # =====================================================
    # Status
    # =====================================================

    error: bool = False

    # =====================================================
    # Validation
    # =====================================================

    def __post_init__(self) -> None:
        if self.role not in {
            "system",
            "user",
            "assistant",
        }:
            raise ValueError(
                f"Role không hợp lệ: {self.role}"
            )

        if not isinstance(self.content, str):
            raise TypeError(
                "ConversationMessage.content phải là str."
            )

        if not self.content.strip():
            raise ValueError(
                "ConversationMessage.content không được rỗng."
            )

        if self.tokens < 0:
            raise ValueError(
                "tokens không được âm."
            )

    # =====================================================
    # Helpers
    # =====================================================

    def is_user(self) -> bool:
        return self.role == "user"

    def is_assistant(self) -> bool:
        return self.role == "assistant"

    def is_system(self) -> bool:
        return self.role == "system"

    def has_content(self) -> bool:
        return bool(self.content.strip())

    def preview(
        self,
        length: int = 80,
    ) -> str:
        if length <= 0:
            return ""

        text = self.content.strip()

        if len(text) <= length:
            return text

        return text[:length] + "..."