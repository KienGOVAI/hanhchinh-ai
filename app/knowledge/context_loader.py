"""
Knowledge Context Loader
------------------------

Xây dựng PromptContext từ nhiều nguồn dữ liệu.
"""

from app.builders.prompt_context import PromptContext
from app.knowledge.models import KnowledgeCollection


class ContextLoader:
    """
    Xây dựng PromptContext.
    """

    def load(
        self,
        *,
        context: str = "",
        knowledge: KnowledgeCollection | None = None,
        memory: str = "",
    ) -> PromptContext:
        """
        Tạo PromptContext hoàn chỉnh.
        """

        return PromptContext(
            context=context.strip(),
            knowledge=self._build_knowledge(
                knowledge
            ),
            memory=memory.strip(),
        )

    # =====================================================
    # PRIVATE
    # =====================================================

    def _build_knowledge(
        self,
        collection: KnowledgeCollection | None,
    ) -> str:
        """
        Ghép toàn bộ Knowledge thành chuỗi.
        """

        if (
            collection is None
            or collection.is_empty()
        ):
            return ""

        parts: list[str] = []

        for document in collection.documents:

            if document.is_empty:
                continue

            parts.append(
                f"# FILE: {document.file_name}"
            )

            parts.append(document.content)

            parts.append("")

        return "\n".join(parts).strip()