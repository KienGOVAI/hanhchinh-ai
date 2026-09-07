"""
Conversation History.

Quản lý lịch sử của một Conversation.
"""

from dataclasses import dataclass

from app.conversation.conversation import Conversation
from app.conversation.conversation_message import (
    ConversationMessage,
)


@dataclass(slots=True)
class ConversationHistory:
    """
    Quản lý lịch sử của một Conversation.
    """

    conversation: Conversation

    max_messages: int = 20

    def __post_init__(self) -> None:
        if self.max_messages <= 0:
            raise ValueError(
                "max_messages phải lớn hơn 0."
            )

    # =====================================================
    # PUBLIC
    # =====================================================

    def add(
        self,
        message: ConversationMessage,
    ) -> None:

        self.conversation.add_message(message)

        self._trim()

    def messages(
        self,
    ) -> list[ConversationMessage]:

        return self.conversation.messages

    def latest(
        self,
        limit: int = 10,
    ) -> list[ConversationMessage]:

        if limit <= 0:
            return []

        return self.conversation.messages[-limit:]

    def clear(self) -> None:
        self.conversation.clear()

    def count(self) -> int:
        return self.conversation.message_count()

    def is_empty(self) -> bool:
        return self.conversation.is_empty()

    def to_prompt(self) -> str:

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

        messages = self.conversation.messages

        if len(messages) <= self.max_messages:
            return

        excess = len(messages) - self.max_messages

        del messages[:excess]