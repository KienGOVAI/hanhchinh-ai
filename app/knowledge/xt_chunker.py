"""
Text Chunker
------------

Chia văn bản thành TextChunk.

Hỗ trợ nhiều chế độ:

- character
- paragraph
- legal
"""

import re
from typing import List
from uuid import uuid4

from app.knowledge.text_chunk import TextChunk


class TextChunker:

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        mode: str = "character",
    ):

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap phải nhỏ hơn chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.mode = mode

    # =====================================================

    def chunk(
        self,
        knowledge_id: str,
        text: str,
    ) -> List[TextChunk]:

        if self.mode == "legal":
            return self._chunk_legal(
                knowledge_id,
                text,
            )

        if self.mode == "paragraph":
            return self._chunk_paragraph(
                knowledge_id,
                text,
            )

        return self._chunk_character(
            knowledge_id,
            text,
        )

    # =====================================================
    # CHARACTER
    # =====================================================

    def _chunk_character(
        self,
        knowledge_id,
        text,
    ):

        text = text.strip()

        chunks = []

        position = 0

        index = 1

        while position < len(text):

            end = min(
                position + self.chunk_size,
                len(text),
            )

            if end < len(text):

                newline = text.rfind(
                    "\n",
                    position,
                    end,
                )

                if newline > position:
                    end = newline

            chunk_text = text[position:end].strip()

            if chunk_text:

                chunks.append(
                    self._create_chunk(
                        knowledge_id,
                        chunk_text,
                        index,
                        position,
                        end,
                    )
                )

                index += 1

            if end >= len(text):
                break

            position = max(
                0,
                end - self.chunk_overlap,
            )

        return chunks

    # =====================================================
    # PARAGRAPH
    # =====================================================

    def _chunk_paragraph(
        self,
        knowledge_id,
        text,
    ):

        paragraphs = [
            p.strip()
            for p in text.split("\n\n")
            if p.strip()
        ]

        chunks = []

        start = 0

        for index, paragraph in enumerate(
            paragraphs,
            start=1,
        ):

            end = start + len(paragraph)

            chunks.append(
                self._create_chunk(
                    knowledge_id,
                    paragraph,
                    index,
                    start,
                    end,
                )
            )

            start = end + 2

        return chunks

    # =====================================================
    # LEGAL
    # =====================================================

    def _chunk_legal(
        self,
        knowledge_id,
        text,
    ):

        pattern = (
            r"(?=Điều\s+\d+[\.\:]?)"
        )

        articles = re.split(
            pattern,
            text,
        )

        chunks = []

        start = 0

        index = 1

        for article in articles:

            article = article.strip()

            if not article:
                continue

            end = start + len(article)

            chunks.append(
                self._create_chunk(
                    knowledge_id,
                    article,
                    index,
                    start,
                    end,
                )
            )

            start = end

            index += 1

        return chunks

    # =====================================================

    def _create_chunk(
        self,
        knowledge_id,
        text,
        index,
        start,
        end,
    ):

        return TextChunk(
            chunk_id=str(uuid4()),
            knowledge_id=knowledge_id,
            text=text,
            index=index,
            start=start,
            end=end,
            metadata={},
        )