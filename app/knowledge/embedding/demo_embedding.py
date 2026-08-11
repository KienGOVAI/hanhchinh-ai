"""
Demo Embedding Provider.

Task 12.14.9 - Assistant Runtime - Layer 1.

Provider kiểm thử Integration với Knowledge Demo.

Knowledge Demo hiện sử dụng vector 3 chiều:

    [1.0, 0.0, 0.0]

Provider này cố ý trả về vector cùng dimension
để kiểm thử toàn bộ Assistant Runtime.

KHÔNG sử dụng cho Production.
"""

from __future__ import annotations

from app.knowledge.embedding.embedding_provider import (
    BaseEmbeddingProvider,
)


class DemoEmbeddingProvider(BaseEmbeddingProvider):
    """
    Embedding Provider dùng cho Integration Demo.

    Mục tiêu:

        Question
            ↓
        DemoEmbeddingProvider
            ↓
        [1.0, 0.0, 0.0]
            ↓
        Retriever
            ↓
        Knowledge Demo
    """

    DIMENSION = 3

    def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Sinh vector demo cố định.

        Provider này không thực hiện semantic embedding
        thực tế.

        Chỉ dùng để kiểm thử Integration Pipeline.
        """

        if not isinstance(text, str):
            raise ValueError(
                "text phải là chuỗi."
            )

        normalized = text.strip()

        if not normalized:
            raise ValueError(
                "text không được rỗng."
            )

        return [
            1.0,
            0.0,
            0.0,
        ]

    def embed_many(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Sinh embedding cho nhiều text.
        """

        if not texts:
            return []

        return [
            self.embed(text)
            for text in texts
        ]