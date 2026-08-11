"""
Citation Service
----------------

Quản lý nguồn trích dẫn của Knowledge Base.

Task 12.11.

Mục tiêu:
- Sinh citation từ RetrievedChunk.
- Giữ document_id.
- Giữ source.
- Giữ page_number.
- Giữ chunk_index.
- Sinh citation text ổn định.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.knowledge.retrieval import (
    RetrievedChunk,
)


# =========================================================
# EXCEPTIONS
# =========================================================


class CitationError(Exception):
    """Lỗi chung của Citation Service."""


# =========================================================
# DATA MODEL
# =========================================================


@dataclass
class Citation:
    """
    Một nguồn trích dẫn.
    """

    citation_id: str

    source: str

    score: float

    document_id: str | None = None

    page_number: int | None = None

    chunk_index: int | None = None

    content: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def label(self) -> str:
        """
        Nhãn citation hiển thị cho người dùng.
        """

        parts = [
            self.source
        ]

        if self.page_number is not None:
            parts.append(
                f"trang {self.page_number}"
            )

        if self.chunk_index is not None:
            parts.append(
                f"chunk {self.chunk_index}"
            )

        return " — ".join(parts)


# =========================================================
# CITATION SERVICE
# =========================================================


class CitationService:
    """
    Chuyển RetrievedChunk thành Citation.

    CitationService không chịu trách nhiệm:
    - Retrieval.
    - Embedding.
    - Generation.
    - Vector Store.
    """

    def build(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[Citation]:
        """
        Sinh danh sách citation.
        """

        citations: list[Citation] = []

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):

            citation = self._build_one(
                chunk=chunk,
                index=index,
            )

            citations.append(
                citation
            )

        return citations

    # =====================================================
    # SINGLE CITATION
    # =====================================================

    @staticmethod
    def _build_one(
        chunk: RetrievedChunk,
        index: int,
    ) -> Citation:
        """
        Tạo một citation.
        """

        source = (
            chunk.metadata.get(
                "source"
            )
            or chunk.document_id
            or f"unknown-source-{index}"
        )

        return Citation(
            citation_id=f"citation-{index}",
            source=str(source),
            score=chunk.score,
            document_id=chunk.document_id,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            metadata=dict(
                chunk.metadata
            ),
        )

    # =====================================================
    # FORMAT
    # =====================================================

    def format(
        self,
        citations: list[Citation],
    ) -> str:
        """
        Format citation thành text.

        Ví dụ:

        [1] nghi-quyet-57.pdf — trang 12
        [2] cong-van.docx — trang 4
        """

        if not citations:
            return ""

        lines: list[str] = []

        for citation in citations:

            lines.append(
                f"[{citation.citation_id}] "
                f"{citation.label}"
            )

        return "\n".join(
            lines
        )

    # =====================================================
    # CONTEXT
    # =====================================================

    def build_context_with_citations(
        self,
        chunks: list[RetrievedChunk],
    ) -> str:
        """
        Tạo context có citation marker.

        Ví dụ:

        [citation-1]
        Nội dung...

        [citation-2]
        Nội dung...
        """

        if not chunks:
            return ""

        sections: list[str] = []

        citations = self.build(
            chunks
        )

        for citation in citations:

            sections.append(
                f"[{citation.citation_id}]\n"
                f"{citation.content}"
            )

        return "\n\n".join(
            sections
        )