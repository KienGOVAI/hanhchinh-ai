"""
Knowledge Chunking Engine
-------------------------

Chia ParsedDocument thành các KnowledgeChunk
để chuẩn bị cho Embedding và Retrieval.
"""

from dataclasses import dataclass
from typing import Any

from app.knowledge.models.parsed_document import (
    ParsedDocument,
    ParsedPage,
)


@dataclass
class KnowledgeChunk:
    """
    Một đoạn nội dung trong Knowledge Base.
    """

    chunk_id: str

    document_id: str

    content: str

    chunk_index: int

    page_number: int | None = None

    section: str | None = None

    chapter: str | None = None

    article: str | None = None

    clause: str | None = None

    point: str | None = None

    token_count: int | None = None

    metadata: dict[str, Any] | None = None


class ChunkingError(Exception):
    """Lỗi chung của Chunking Engine."""


class Chunker:
    """
    Chunking Engine cơ bản.

    Chiến lược hiện tại:
    - Chia theo paragraph.
    - Gộp các paragraph cho đến khi đạt kích thước mục tiêu.
    - Có overlap giữa các chunk.
    - Giữ page_number.
    """

    def __init__(
        self,
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
    ) -> None:

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size phải lớn hơn 0."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap không được âm."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap phải nhỏ hơn chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # =====================================================
    # PUBLIC
    # =====================================================

    def chunk(
        self,
        document: ParsedDocument,
        document_id: str,
    ) -> list[KnowledgeChunk]:
        """
        Chia ParsedDocument thành các KnowledgeChunk.
        """

        if not document_id.strip():
            raise ValueError(
                "document_id không được rỗng."
            )

        if not document.text.strip():
            return []

        chunks: list[KnowledgeChunk] = []

        global_index = 0

        for page in document.pages:

            page_chunks = self._chunk_page(
                page
            )

            for content in page_chunks:

                chunks.append(
                    KnowledgeChunk(
                        chunk_id=(
                            f"{document_id}-"
                            f"{global_index}"
                        ),
                        document_id=document_id,
                        content=content,
                        chunk_index=global_index,
                        page_number=page.page_number,
                        token_count=self._estimate_tokens(
                            content
                        ),
                        metadata={
                            "source": document.source,
                            "format": document.metadata.get(
                                "format"
                            ),
                        },
                    )
                )

                global_index += 1

        return chunks

    # =====================================================
    # PAGE CHUNKING
    # =====================================================

    def _chunk_page(
        self,
        page: ParsedPage,
    ) -> list[str]:
        """
        Chia một trang thành nhiều chunk.
        """

        paragraphs = self._split_paragraphs(
            page.text
        )

        if not paragraphs:
            return []

        chunks: list[str] = []

        current: list[str] = []
        current_length = 0

        for paragraph in paragraphs:

            paragraph_length = len(
                paragraph
            )

            # -----------------------------------------
            # Paragraph quá lớn
            # -----------------------------------------

            if paragraph_length > self.chunk_size:

                if current:
                    chunks.append(
                        "\n\n".join(current)
                    )

                    current = []
                    current_length = 0

                large_chunks = self._split_large_text(
                    paragraph
                )

                chunks.extend(
                    large_chunks
                )

                continue

            # -----------------------------------------
            # Có thể thêm vào chunk hiện tại
            # -----------------------------------------

            additional_length = (
                paragraph_length
                + (
                    2
                    if current
                    else 0
                )
            )

            if (
                current_length
                + additional_length
                <= self.chunk_size
            ):

                current.append(
                    paragraph
                )

                current_length += (
                    additional_length
                )

                continue

            # -----------------------------------------
            # Đạt giới hạn
            # -----------------------------------------

            if current:

                chunks.append(
                    "\n\n".join(current)
                )

            overlap = self._build_overlap(
                current
            )

            current = overlap + [
                paragraph
            ]

            current_length = len(
                "\n\n".join(current)
            )

        if current:

            chunks.append(
                "\n\n".join(current)
            )

        return [
            chunk.strip()
            for chunk in chunks
            if chunk.strip()
        ]

    # =====================================================
    # PARAGRAPH
    # =====================================================

    @staticmethod
    def _split_paragraphs(
        text: str,
    ) -> list[str]:

        return [
            paragraph.strip()
            for paragraph in text.split(
                "\n\n"
            )
            if paragraph.strip()
        ]

    # =====================================================
    # LARGE TEXT
    # =====================================================

    def _split_large_text(
        self,
        text: str,
    ) -> list[str]:
        """
        Chia paragraph quá lớn.

        Ưu tiên cắt theo whitespace thay vì
        cắt giữa một từ.
        """

        words = text.split()

        chunks: list[str] = []

        current_words: list[str] = []
        current_length = 0

        for word in words:

            additional = len(word)

            if current_words:
                additional += 1

            if (
                current_length
                + additional
                <= self.chunk_size
            ):

                current_words.append(
                    word
                )

                current_length += additional

                continue

            if current_words:

                chunks.append(
                    " ".join(
                        current_words
                    )
                )

            overlap_words = (
                self._overlap_words(
                    current_words
                )
            )

            current_words = (
                overlap_words
                + [word]
            )

            current_length = len(
                " ".join(
                    current_words
                )
            )

        if current_words:

            chunks.append(
                " ".join(
                    current_words
                )
            )

        return chunks

    # =====================================================
    # OVERLAP
    # =====================================================

    def _build_overlap(
        self,
        paragraphs: list[str],
    ) -> list[str]:

        if not paragraphs:
            return []

        overlap: list[str] = []
        length = 0

        for paragraph in reversed(
            paragraphs
        ):

            additional = len(
                paragraph
            )

            if overlap:
                additional += 2

            if (
                length
                + additional
                > self.chunk_overlap
            ):
                break

            overlap.insert(
                0,
                paragraph
            )

            length += additional

        return overlap

    def _overlap_words(
        self,
        words: list[str],
    ) -> list[str]:

        if not words:
            return []

        result: list[str] = []
        length = 0

        for word in reversed(words):

            additional = len(word)

            if result:
                additional += 1

            if (
                length
                + additional
                > self.chunk_overlap
            ):
                break

            result.insert(
                0,
                word
            )

            length += additional

        return result

    # =====================================================
    # TOKEN ESTIMATION
    # =====================================================

    @staticmethod
    def _estimate_tokens(
        text: str,
    ) -> int:
        """
        Ước lượng token.

        Chưa dùng tokenizer của model.
        Mục đích hiện tại chỉ để lưu metadata.
        """

        if not text.strip():
            return 0

        return max(
            1,
            len(text) // 4,
        )