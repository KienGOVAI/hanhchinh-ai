"""
Vector Store Interface
----------------------

Định nghĩa interface chuẩn cho các Vector Store.
"""

from abc import ABC, abstractmethod
from typing import List

from app.knowledge.text_chunk import TextChunk


class VectorStore(ABC):
    """
    Abstract Vector Store.
    """

    @abstractmethod
    def add(
        self,
        chunks: List[TextChunk],
    ) -> None:
        """
        Thêm các TextChunk vào Vector Store.
        """
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        embedding: List[float],
        top_k: int = 5,
    ) -> List[TextChunk]:
        """
        Tìm kiếm các TextChunk gần nhất.
        """
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        directory: str,
    ) -> None:
        """
        Lưu Vector Store xuống đĩa.
        """
        raise NotImplementedError

    @abstractmethod
    def load(
        self,
        directory: str,
    ) -> None:
        """
        Đọc Vector Store từ đĩa.
        """
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """
        Số lượng vector hiện có.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """
        Xóa toàn bộ dữ liệu.
        """
        raise NotImplementedError