"""
Base Knowledge Loader
---------------------

Định nghĩa interface chung cho tất cả Knowledge Loader.

Các Loader tương lai:

- MarkdownLoader
- PdfLoader
- DocxLoader
- SQLiteLoader
- VectorLoader
"""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseKnowledgeLoader(ABC):
    """
    Interface chung cho mọi Knowledge Loader.
    """

    def __init__(self, root: Path):

        self.root = root

    @abstractmethod
    def load(self) -> str:
        """
        Đọc toàn bộ tri thức.

        Returns
        -------
        str
            Nội dung tri thức.
        """
        raise NotImplementedError

    @abstractmethod
    def supports(self) -> tuple[str, ...]:
        """
        Trả về danh sách phần mở rộng được hỗ trợ.

        Ví dụ:

            (".md",)

            (".pdf",)

            (".docx",)
        """
        raise NotImplementedError

    def exists(self) -> bool:
        """
        Kiểm tra thư mục Knowledge tồn tại.
        """

        return self.root.exists()

    def is_empty(self) -> bool:
        """
        Kiểm tra thư mục có dữ liệu hay không.
        """

        if not self.exists():
            return True

        return not any(self.root.iterdir())