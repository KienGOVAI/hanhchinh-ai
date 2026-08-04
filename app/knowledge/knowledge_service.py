"""
Knowledge Service
-----------------

Điều phối toàn bộ Knowledge Engine.
"""

from pathlib import Path

from app.builders.prompt_context import PromptContext
from app.knowledge.cache import KnowledgeCache
from app.knowledge.context_loader import ContextLoader
from app.knowledge.markdown_loader import MarkdownLoader
from app.knowledge.models import KnowledgeCollection


class KnowledgeService:
    """
    Service điều phối Knowledge Base.
    """

    KNOWLEDGE_ROOT = Path("knowledge")

    def __init__(self):

        self.cache = KnowledgeCache()

        self.context_loader = ContextLoader()

        self.markdown_loader = MarkdownLoader(
            self.KNOWLEDGE_ROOT
        )

    # =====================================================
    # PUBLIC
    # =====================================================

    def build_context(
        self,
        *,
        context: str = "",
        memory: str = "",
    ) -> PromptContext:
        """
        Xây dựng PromptContext từ Knowledge.
        """

        collection = self.load()

        return self.context_loader.load(
            context=context,
            knowledge=collection,
            memory=memory,
        )

    def load(self) -> KnowledgeCollection:
        """
        Lấy toàn bộ Knowledge.

        Nếu đã có Cache thì dùng Cache.
        """

        if self.cache.is_loaded():

            return self.cache.get()

        collection = self.markdown_loader.load()

        self.cache.set(collection)

        return collection

    def reload(self) -> KnowledgeCollection:
        """
        Xóa Cache và đọc lại Knowledge.
        """

        self.cache.clear()

        return self.load()

    def clear_cache(self) -> None:
        """
        Xóa toàn bộ Cache.
        """

        self.cache.clear()

    def statistics(self) -> dict:
        """
        Thống kê Knowledge Base.
        """

        collection = self.load()

        return {
            "documents": collection.total_documents(),
            "characters": collection.total_characters(),
            "cached": self.cache.is_loaded(),
        }