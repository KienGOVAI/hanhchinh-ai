"""
Conversation Service
--------------------

Điều phối toàn bộ Conversation Engine.
"""

from uuid import uuid4

from app.conversation.conversation import Conversation
from app.conversation.conversation_cache import ConversationCache
from app.conversation.conversation_history import ConversationHistory
from app.conversation.conversation_message import ConversationMessage


class ConversationService:
    """
    Service quản lý Conversation.
    """

    def __init__(self):

        self.cache = ConversationCache()

    # =====================================================
    # CONVERSATION
    # =====================================================

    def create(
        self,
        title: str = "Cuộc hội thoại mới",
        user_id: str = "anonymous",
    ) -> Conversation:
        """
        Tạo Conversation mới.
        """

        conversation = Conversation(
            conversation_id=str(uuid4()),
            title=title,
            user_id=user_id,
        )

        self.cache.set(conversation)

        return conversation

    def get(
        self,
        conversation_id: str,
    ) -> Conversation:
        """
        Lấy Conversation.
        """

        conversation = self.cache.get(
            conversation_id
        )

        if conversation is None:
            raise ValueError(
                f"Không tìm thấy Conversation '{conversation_id}'."
            )

        return conversation

    def delete(
        self,
        conversation_id: str,
    ) -> None:
        """
        Xóa Conversation.
        """

        self.cache.remove(
            conversation_id
        )

    # =====================================================
    # MESSAGE
    # =====================================================

    def add_user_message(
        self,
        conversation_id: str,
        content: str,
    ) -> None:
        """
        Thêm User Message.
        """

        self._history(
            conversation_id
        ).add(
            ConversationMessage(
                role="user",
                content=content,
            )
        )

    def add_assistant_message(
        self,
        conversation_id: str,
        content: str,
        *,
        provider: str = "",
        model: str = "",
        tokens: int = 0,
    ) -> None:
        """
        Thêm Assistant Message.
        """

        self._history(
            conversation_id
        ).add(
            ConversationMessage(
                role="assistant",
                content=content,
                provider=provider,
                model=model,
                tokens=tokens,
            )
        )

    def add_system_message(
        self,
        conversation_id: str,
        content: str,
    ) -> None:
        """
        Thêm System Message.
        """

        self._history(
            conversation_id
        ).add(
            ConversationMessage(
                role="system",
                content=content,
            )
        )

    # =====================================================
    # HISTORY
    # =====================================================

    def history(
        self,
        conversation_id: str,
    ) -> ConversationHistory:
        """
        Trả về ConversationHistory.
        """

        return self._history(
            conversation_id
        )

    def prompt(
        self,
        conversation_id: str,
    ) -> str:
        """
        Sinh Prompt từ lịch sử.
        """

        return self._history(
            conversation_id
        ).to_prompt()

    def clear(
        self,
        conversation_id: str,
    ) -> None:
        """
        Xóa lịch sử.
        """

        self._history(
            conversation_id
        ).clear()

    # =====================================================
    # CACHE
    # =====================================================

    def count(self) -> int:
        """
        Tổng số Conversation.
        """

        return self.cache.count()

    def list(self) -> list[Conversation]:
        """
        Danh sách Conversation.
        """

        return self.cache.list()

    # =====================================================
    # PRIVATE
    # =====================================================

    def _history(
        self,
        conversation_id: str,
    ) -> ConversationHistory:
        """
        Lấy History của Conversation.
        """

        return ConversationHistory(
            self.get(conversation_id)
        )