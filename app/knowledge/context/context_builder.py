"""
Context Builder
---------------

Xây dựng Context có cấu trúc từ các RetrievedChunk
để cung cấp cho RAG Service.

Task 12.10.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.knowledge.retrieval import RetrievedChunk


# =========================================================
# EXCEPTIONS
# =========================================================


class ContextBuilderError(Exception):
    """Lỗi chung của ContextBuilder."""


# =========================================================
# RESULT
# =========================================================


@dataclass
class ContextDocument:
    """
    Một nguồn tài liệu trong Context.
    """

    source_id: str

    content: str

    score: float

    document_id: str | None = None

    page_number: int | None = None

    chunk_index: int | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class RAGContext:
    """
    Context hoàn chỉnh truyền cho AI.
    """

    text: str

    documents: list[ContextDocument] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =========================================================
# CONTEXT BUILDER
# =========================================================


class ContextBuilder:
    """
    Xây dựng context từ RetrievedChunk.

    Trách nhiệm:

    - Chuẩn hóa source.
    - Giữ thứ tự relevance.
    - Giữ metadata.
    - Giới hạn số lượng chunk.
    - Sinh context text.
    """

    def __init__(
        self,
        max_chunks: int = 5,
    ) -> None:

        if max_chunks <= 0:
            raise ValueError(
                "max_chunks phải lớn hơn 0."
            )

        self.max_chunks = max_chunks

    # =====================================================
    # PUBLIC
    # =====================================================

    def build(
        self,
        chunks: list[RetrievedChunk],
    ) -> RAGContext:
        """
        Xây dựng RAGContext.
        """

        if not chunks:
            return RAGContext(
                text=(
                    "Không tìm thấy tài liệu "
                    "liên quan trong Knowledge Base."
                ),
                documents=[],
                metadata={
                    "document_count": 0,
                    "chunk_count": 0,
                },
            )

        selected_chunks = chunks[
            : self.max_chunks
        ]

        documents: list[
            ContextDocument
        ] = []

        for index, chunk in enumerate(
            selected_chunks,
            start=1,
        ):

            content = chunk.content.strip()

            if not content:
                continue

            source_id = (
                self._get_source_id(
                    chunk,
                    index,
                )
            )

            documents.append(
                ContextDocument(
                    source_id=source_id,
                    content=content,
                    score=chunk.score,
                    document_id=(
                        chunk.document_id
                    ),
                    page_number=(
                        chunk.page_number
                    ),
                    chunk_index=(
                        chunk.chunk_index
                    ),
                    metadata=dict(
                        chunk.metadata
                    ),
                )
            )

        text = self._build_text(
            documents
        )

        return RAGContext(
            text=text,
            documents=documents,
            metadata={
                "document_count": len(
                    documents
                ),
                "chunk_count": len(
                    documents
                ),
                "max_chunks": self.max_chunks,
            },
        )

    # =====================================================
    # SOURCE
    # =====================================================

    @staticmethod
    def _get_source_id(
        chunk: RetrievedChunk,
        index: int,
    ) -> str:

        source = chunk.metadata.get(
            "source"
        )

        if source:
            return str(source)

        if chunk.document_id:
            return chunk.document_id

        return f"source-{index}"

    # =====================================================
    # TEXT
    # =====================================================

    @staticmethod
    def _build_text(
        documents: list[ContextDocument],
    ) -> str:

        if not documents:

            return (
                "Không tìm thấy nội dung "
                "hợp lệ trong Knowledge Base."
            )

        sections: list[str] = []

        for index, document in enumerate(
            documents,
            start=1,
        ):

            location = (
                ContextBuilder._format_location(
                    document
                )
            )

            sections.append(
                f"[Nguồn {index}: "
                f"{document.source_id}"
                f"{location}]\n"
                f"{document.content}"
            )

        return "\n\n".join(
            sections
        )

    # =====================================================
    # LOCATION
    # =====================================================

    @staticmethod
    def _format_location(
        document: ContextDocument,
    ) -> str:

        if document.page_number is not None:

            return (
                f" - Trang "
                f"{document.page_number}"
            )

        if document.chunk_index is not None:

            return (
                f" - Chunk "
                f"{document.chunk_index}"
            )

        return ""