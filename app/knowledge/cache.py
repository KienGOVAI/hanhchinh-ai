"""
Knowledge Cache
---------------

Cache nội dung Knowledge trong bộ nhớ.
"""

from app.knowledge.models import (
    KnowledgeCollection,
)


class KnowledgeCache:
    """
    Cache dữ liệu Knowledge.
    """

    def __init__(self):

        self._collection = KnowledgeCollection()

        self._loaded = False

    # =====================================================
    # PUBLIC
    # =====================================================

    def is_loaded(self) -> bool:
        """
        Đã nạp Knowledge hay chưa.
        """

        return self._loaded

    def get(self) -> KnowledgeCollection:
        """
        Lấy toàn bộ Knowledge.
        """

        return self._collection

    def set(
        self,
        collection: KnowledgeCollection,
    ) -> None:
        """
        Lưu Knowledge vào Cache.
        """

        self._collection = collection

        self._loaded = True

    def clear(self) -> None:
        """
        Xóa Cache.
        """

        self._collection = KnowledgeCollection()

        self._loaded = False

    def count(self) -> int:
        """
        Tổng số tài liệu.
        """

        return self._collection.total_documents()