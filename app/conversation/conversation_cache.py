"""
Conversation Cache
------------------

Quản lý bộ nhớ tạm của các Conversation.
"""

from app.conversation.conversation import Conversation


class ConversationCache:
    """
    Cache lưu các Conversation đang hoạt động.
    """

    def __init__(self) -> None:

        self._cache: dict[str, Conversation] = {}

    # =====================================================
    # PUBLIC
    # =====================================================

    def set(
        self,
        conversation: Conversation,
    ) -> None:
        """
        Lưu Conversation vào Cache.
        """

        self._cache[
            conversation.conversation_id
        ] = conversation

    def get(
        self,
        conversation_id: str,
    ) -> Conversation | None:
        """
        Lấy Conversation theo ID.
        """

        return self._cache.get(
            conversation_id
        )

    def exists(
        self,
        conversation_id: str,
    ) -> bool:
        """
        Kiểm tra Conversation có tồn tại.
        """

        return conversation_id in self._cache

    def remove(
        self,
        conversation_id: str,
    ) -> None:
        """
        Xóa Conversation khỏi Cache.
        """

        self._cache.pop(
            conversation_id,
            None,
        )

    def clear(self) -> None:
        """
        Xóa toàn bộ Cache.
        """

        self._cache.clear()

    def list(self) -> list[Conversation]:
        """
        Trả về toàn bộ Conversation.
        """

        return list(
            self._cache.values()
        )

    def count(self) -> int:
        """
        Tổng số Conversation.
        """

        return len(self._cache)