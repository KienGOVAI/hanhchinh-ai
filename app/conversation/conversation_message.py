"""
Conversation Message
--------------------

Định nghĩa một tin nhắn trong cuộc hội thoại.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ConversationMessage:
    """
    Đại diện một tin nhắn trong cuộc hội thoại.
    """

    # =====================================================
    # Identity
    # =====================================================

    role: str

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
    # Helpers
    # =====================================================

    def is_user(self) -> bool:
        """
        Kiểm tra message của người dùng.
        """

        return self.role == "user"

    def is_assistant(self) -> bool:
        """
        Kiểm tra message của AI.
        """

        return self.role == "assistant"

    def is_system(self) -> bool:
        """
        Kiểm tra System Prompt.
        """

        return self.role == "system"

    def has_content(self) -> bool:
        """
        Kiểm tra nội dung có rỗng không.
        """

        return bool(
            self.content.strip()
        )

    def preview(
        self,
        length: int = 80,
    ) -> str:
        """
        Trả về nội dung rút gọn.
        """

        text = self.content.strip()

        if len(text) <= length:
            return text

        return text[:length] + "..."