"""
Embedding Service
-----------------

Interface thống nhất cho các Embedding Model.
"""

from abc import ABC, abstractmethod
from typing import List


class EmbeddingService(ABC):
    """
    Abstract Embedding Service.
    """

    @abstractmethod
    def embed_text(
        self,
        text: str,
    ) -> List[float]:
        """
        Sinh embedding cho một đoạn văn.
        """
        raise NotImplementedError

    @abstractmethod
    def embed_documents(
        self,
        documents: List[str],
    ) -> List[List[float]]:
        """
        Sinh embedding cho nhiều đoạn văn.
        """
        raise NotImplementedError

    @abstractmethod
    def dimension(self) -> int:
        """
        Trả về số chiều embedding.
        """
        raise NotImplementedError

    @abstractmethod
    def model_name(self) -> str:
        """
        Tên embedding model.
        """
        raise NotImplementedError