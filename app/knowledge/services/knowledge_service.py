"""
Knowledge Service
-----------------

Điều phối nghiệp vụ Knowledge Base.

Task 12.12.

Router không trực tiếp xử lý:
- Parser
- Chunker
- Vector Store
- Retriever

Các nghiệp vụ được gom tại Service Layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.knowledge.retrieval import (
    RetrievedChunk,
    Retriever,
)


# =========================================================
# EXCEPTIONS
# =========================================================


class KnowledgeServiceError(Exception):
    """Lỗi chung của Knowledge Service."""


# =========================================================
# RESULT
# =========================================================


@dataclass
class KnowledgeSearchResult:
    """
    Kết quả tìm kiếm Knowledge Base.
    """

    query: str

    results: list[RetrievedChunk]

    total: int

    metadata: dict[str, Any]


# =========================================================
# SERVICE
# =========================================================


class KnowledgeService:
    """
    Service nghiệp vụ Knowledge Base.

    Phiên bản 12.12 tập trung vào Search API.

    Upload/Index Pipeline sẽ được mở rộng
    khi Embedding Provider và persistence
    được tích hợp hoàn chỉnh.
    """

    def __init__(
        self,
        retriever: Retriever,
    ) -> None:

        self.retriever = retriever

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        query: str,
        query_vector: list[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> KnowledgeSearchResult:
        """
        Tìm kiếm Knowledge Base.
        """

        query = query.strip()

        if not query:
            raise KnowledgeServiceError(
                "query không được rỗng."
            )

        if not query_vector:
            raise KnowledgeServiceError(
                "query_vector không được rỗng."
            )

        results = self.retriever.search(
            query_vector=query_vector,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        return KnowledgeSearchResult(
            query=query,
            results=results,
            total=len(results),
            metadata={
                "top_k": top_k,
                "score_threshold": (
                    score_threshold
                ),
            },
        )