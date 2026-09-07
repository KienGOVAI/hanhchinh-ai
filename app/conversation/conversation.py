"""
Conversation Domain Model.

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
    # Validation
    # =====================================================

    def __post_init__(self) -> None:
        if not self.conversation_id.strip():
            raise ValueError(
                "conversation_id không được rỗng."
            )

        if not self.user_id.strip():
            raise ValueError(
                "user_id không được rỗng."
            )

        if not self.title.strip():
            raise ValueError(
                "title không được rỗng."
            )

    # =====================================================
    # Public API
    # =====================================================

    def add_message(
        self,
        message: ConversationMessage,
    ) -> None:
        if not isinstance(
            message,
            ConversationMessage,
        ):
            raise TypeError(
                "message phải là ConversationMessage."
            )

        self.messages.append(message)
        self.updated_at = datetime.now()

    def clear(self) -> None:
        self.messages.clear()
        self.updated_at = datetime.now()

    def message_count(self) -> int:
        return len(self.messages)

    def is_empty(self) -> bool:
        return len(self.messages) == 0

    def last_message(
        self,
    ) -> ConversationMessage | None:

        if not self.messages:
            return None

        return self.messages[-1]

    def archive(self) -> None:
        self.archived = True
        self.active = False
        self.updated_at = datetime.now()

    def activate(self) -> None:
        self.archived = False
        self.active = True
        self.updated_at = datetime.now()