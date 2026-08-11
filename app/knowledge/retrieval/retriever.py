"""
Knowledge Retriever
-------------------

Tìm kiếm các Knowledge Chunk liên quan
dựa trên vector similarity.

Task 12.8.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.knowledge.vectorstore import (
    BaseVectorStore,
    VectorSearchResult,
)


# =========================================================
# EXCEPTIONS
# =========================================================


class RetrievalError(Exception):
    """Lỗi chung của Retriever."""


class InvalidRetrievalQueryError(
    RetrievalError
):
    """Query không hợp lệ."""


# =========================================================
# DATA MODEL
# =========================================================


@dataclass
class RetrievedChunk:
    """
    Chunk được Retriever trả về.
    """

    vector_id: str

    score: float

    content: str

    document_id: str | None = None

    chunk_index: int | None = None

    page_number: int | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =========================================================
# RETRIEVER
# =========================================================


class Retriever:
    """
    Semantic Retriever.

    Retriever nhận query vector và sử dụng
    VectorStore để tìm các vector gần nhất.
    """

    def __init__(
        self,
        vector_store: BaseVectorStore,
        default_top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> None:

        if default_top_k <= 0:
            raise ValueError(
                "default_top_k phải lớn hơn 0."
            )

        if not 0.0 <= score_threshold <= 1.0:
            raise ValueError(
                "score_threshold phải nằm "
                "trong khoảng 0.0 đến 1.0."
            )

        self.vector_store = vector_store

        self.default_top_k = default_top_k

        self.score_threshold = (
            score_threshold
        )

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        query_vector: list[float],
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> list[RetrievedChunk]:
        """
        Tìm các Chunk liên quan bằng query vector.
        """

        if not query_vector:
            raise InvalidRetrievalQueryError(
                "query_vector không được rỗng."
            )

        effective_top_k = (
            top_k
            if top_k is not None
            else self.default_top_k
        )

        if effective_top_k <= 0:
            raise ValueError(
                "top_k phải lớn hơn 0."
            )

        effective_threshold = (
            score_threshold
            if score_threshold is not None
            else self.score_threshold
        )

        if not (
            0.0
            <= effective_threshold
            <= 1.0
        ):
            raise ValueError(
                "score_threshold phải nằm "
                "trong khoảng 0.0 đến 1.0."
            )

        results = self.vector_store.search(
            query_vector=query_vector,
            top_k=effective_top_k,
        )

        retrieved: list[
            RetrievedChunk
        ] = []

        for result in results:

            if (
                result.score
                < effective_threshold
            ):
                continue

            chunk = self._to_retrieved_chunk(
                result
            )

            retrieved.append(
                chunk
            )

        return retrieved

    # =====================================================
    # FILTER BY DOCUMENT
    # =====================================================

    def search_document(
        self,
        query_vector: list[float],
        document_id: str,
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> list[RetrievedChunk]:
        """
        Tìm kiếm và chỉ giữ Chunk thuộc
        một Document.

        Filtering hiện được thực hiện
        sau VectorStore search.
        """

        if not document_id.strip():
            raise ValueError(
                "document_id không được rỗng."
            )

        results = self.search(
            query_vector=query_vector,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        return [
            result
            for result in results
            if result.document_id
            == document_id
        ]

    # =====================================================
    # CONVERSION
    # =====================================================

    @staticmethod
    def _to_retrieved_chunk(
        result: VectorSearchResult,
    ) -> RetrievedChunk:
        """
        Chuyển VectorSearchResult thành
        RetrievedChunk.
        """

        metadata = dict(
            result.metadata
        )

        content = str(
            metadata.get(
                "content",
                "",
            )
        )

        document_id = metadata.get(
            "document_id"
        )

        chunk_index = metadata.get(
            "chunk_index"
        )

        page_number = metadata.get(
            "page_number"
        )

        return RetrievedChunk(
            vector_id=result.vector_id,
            score=result.score,
            content=content,
            document_id=document_id,
            chunk_index=chunk_index,
            page_number=page_number,
            metadata=metadata,
        )