"""
Knowledge API Schemas
---------------------

Schema request/response cho Knowledge API.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# =========================================================
# SEARCH REQUEST
# =========================================================


class KnowledgeSearchRequest(
    BaseModel
):
    """
    Request tìm kiếm Knowledge Base.
    """

    query: str = Field(
        ...,
        min_length=1,
        description="Câu hỏi hoặc nội dung cần tìm",
    )

    query_vector: list[float] = Field(
        ...,
        min_length=1,
        description="Vector embedding của query",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Số lượng kết quả tối đa",
    )

    score_threshold: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Ngưỡng similarity",
    )


# =========================================================
# RESULT
# =========================================================


class KnowledgeSearchItem(
    BaseModel
):
    """
    Một kết quả Knowledge Search.
    """

    vector_id: str

    score: float

    content: str

    document_id: str | None = None

    chunk_index: int | None = None

    page_number: int | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


# =========================================================
# RESPONSE
# =========================================================


class KnowledgeSearchResponse(
    BaseModel
):
    """
    Response của Knowledge Search API.
    """

    success: bool = True

    query: str

    total: int

    results: list[
        KnowledgeSearchItem
    ]

    message: str = (
        "Tìm kiếm thành công."
    )