"""
Knowledge Models
----------------

Các model dùng trong Knowledge Engine.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class KnowledgeDocument:
    """
    Đại diện cho một tài liệu tri thức.
    """

    source: Path

    title: str

    content: str

    category: str = ""

    tags: list[str] = field(default_factory=list)

    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def file_name(self) -> str:
        """
        Tên file.
        """

        return self.source.name

    @property
    def extension(self) -> str:
        """
        Phần mở rộng file.
        """

        return self.source.suffix.lower()

    @property
    def size(self) -> int:
        """
        Độ dài nội dung.
        """

        return len(self.content)

    @property
    def is_empty(self) -> bool:
        """
        Kiểm tra tài liệu rỗng.
        """

        return not self.content.strip()


@dataclass(slots=True)
class KnowledgeCollection:
    """
    Danh sách tài liệu tri thức.
    """

    documents: list[KnowledgeDocument] = field(
        default_factory=list
    )

    def add(
        self,
        document: KnowledgeDocument,
    ) -> None:
        """
        Thêm tài liệu.
        """

        self.documents.append(document)

    def extend(
        self,
        documents: list[KnowledgeDocument],
    ) -> None:
        """
        Thêm nhiều tài liệu.
        """

        self.documents.extend(documents)

    def is_empty(self) -> bool:
        """
        Không có tài liệu.
        """

        return len(self.documents) == 0

    def total_documents(self) -> int:
        """
        Tổng số tài liệu.
        """

        return len(self.documents)

    def total_characters(self) -> int:
        """
        Tổng số ký tự.
        """

        return sum(
            document.size
            for document in self.documents
        )