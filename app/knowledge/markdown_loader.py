"""
Markdown Knowledge Loader
-------------------------

Đọc toàn bộ file Markdown trong Knowledge Base.
"""

from pathlib import Path

from app.knowledge.base_loader import BaseKnowledgeLoader
from app.knowledge.file_scanner import FileScanner
from app.knowledge.models import (
    KnowledgeCollection,
    KnowledgeDocument,
)


class MarkdownLoader(BaseKnowledgeLoader):
    """
    Loader đọc toàn bộ file Markdown.
    """

    def supports(self) -> tuple[str, ...]:
        """
        Các phần mở rộng được hỗ trợ.
        """

        return (".md",)

    def load(self) -> KnowledgeCollection:
        """
        Đọc toàn bộ Knowledge Markdown.

        Returns
        -------
        KnowledgeCollection
        """

        collection = KnowledgeCollection()

        if not self.exists():
            return collection

        scanner = FileScanner(self.root)

        files = scanner.scan(
            self.supports()
        )

        for file in files:

            document = self._read_document(file)

            if document is not None:
                collection.add(document)

        return collection

    # =====================================================
    # PRIVATE
    # =====================================================

    def _read_document(
        self,
        file: Path,
    ) -> KnowledgeDocument | None:
        """
        Đọc một file Markdown.
        """

        try:

            content = file.read_text(
                encoding="utf-8"
            ).strip()

            if not content:
                return None

            return KnowledgeDocument(
                source=file,
                title=file.stem.replace("_", " ").title(),
                content=content,
                category=file.parent.name,
            )

        except Exception:

            return None