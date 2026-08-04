"""
Conversation History
--------------------

Quản lý lịch sử hội thoại.
"""

from dataclasses import dataclass, field

from app.conversation.conversation import Conversation
from app.conversation.conversation_message import ConversationMessage


@dataclass(slots=True)
class ConversationHistory:
    """
    Quản lý lịch sử của một Conversation.
    """

    conversation: Conversation

    max_messages: int = 20

    # =====================================================
    # PUBLIC
    # =====================================================

    def add(
        self,
        message: ConversationMessage,
    ) -> None:
        """
        Thêm một message.
        """

        self.conversation.add_message(message)

        self._trim()

    def messages(
        self,
    ) -> list[ConversationMessage]:
        """
        Trả về toàn bộ lịch sử.
        """

        return self.conversation.messages

    def latest(
        self,
        limit: int = 10,
    ) -> list[ConversationMessage]:
        """
        Lấy N message gần nhất.
        """

        if limit <= 0:
            return []

        return self.conversation.messages[-limit:]

    def clear(self) -> None:
        """
        Xóa toàn bộ lịch sử.
        """

        self.conversation.clear()

    def count(self) -> int:
        """
        Tổng số message.
        """

        return self.conversation.message_count()

    def is_empty(self) -> bool:
        """
        Kiểm tra lịch sử rỗng.
        """

        return self.conversation.is_empty()

    def to_prompt(self) -> str:
        """
        Chuyển lịch sử thành Prompt.
        """

        if self.is_empty():
            return ""

        lines: list[str] = []

        for message in self.conversation.messages:

            role = message.role.upper()

            lines.append(
                f"{role}: {message.content}"
            )

        return "\n\n".join(lines)

    # =====================================================
    # PRIVATE
    # =====================================================

    def _trim(self) -> None:
        """
        Giới hạn số lượng message.
        """

        messages = self.conversation.messages

        if len(messages) <= self.max_messages:
            return

        excess = len(messages) - self.max_messages

        del messages[:excess]