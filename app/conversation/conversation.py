"""
Conversation Model
------------------

Định nghĩa một phiên hội thoại với AI.
"""

from dataclasses import dataclass, field
from datetime import datetime

from app.conversation.conversation_message import (
    ConversationMessage,
)


@dataclass(slots=True)
class Conversation:
    """
    Đại diện một cuộc hội thoại.
    """

    # =====================================================
    # Identity
    # =====================================================

    conversation_id: str

    user_id: str = "anonymous"

    title: str = "Cuộc hội thoại mới"

    # =====================================================
    # Messages
    # =====================================================

    messages: list[ConversationMessage] = field(
        default_factory=list
    )

    # =====================================================
    # Time
    # =====================================================

    created_at: datetime = field(
        default_factory=datetime.now
    )

    updated_at: datetime = field(
        default_factory=datetime.now
    )

    # =====================================================
    # Status
    # =====================================================

    active: bool = True

    archived: bool = False

    # =====================================================
    # Public API
    # =====================================================

    def add_message(
        self,
        message: ConversationMessage,
    ) -> None:
        """
        Thêm một message vào cuộc hội thoại.
        """

        self.messages.append(message)

        self.updated_at = datetime.now()

    def clear(self) -> None:
        """
        Xóa toàn bộ lịch sử hội thoại.
        """

        self.messages.clear()

        self.updated_at = datetime.now()

    def message_count(self) -> int:
        """
        Tổng số message.
        """

        return len(self.messages)

    def is_empty(self) -> bool:
        """
        Kiểm tra hội thoại rỗng.
        """

        return len(self.messages) == 0

    def last_message(self) -> ConversationMessage | None:
        """
        Lấy message mới nhất.
        """

        if not self.messages:
            return None

        return self.messages[-1]