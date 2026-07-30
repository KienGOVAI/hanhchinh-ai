"""
Citation Builder
----------------

Xây dựng danh sách nguồn trích dẫn từ các TextChunk.
"""

from typing import List

from app.knowledge.text_chunk import TextChunk


class CitationBuilder:

    def build(
        self,
        chunks: List[TextChunk],
    ) -> str:
        """
        Sinh danh sách nguồn trích dẫn.
        """

        if not chunks:
            return ""

        lines = []

        seen = set()

        number = 1

        for chunk in chunks:

            metadata = chunk.metadata or {}

            knowledge = metadata.get(
                "knowledge",
                chunk.knowledge_id,
            )

            chapter = metadata.get(
                "chapter"
            )

            article = metadata.get(
                "article"
            )

            clause = metadata.get(
                "clause"
            )

            citation = knowledge

            if chapter:
                citation += f" | Chương {chapter}"

            if article:
                citation += f" | Điều {article}"

            if clause:
                citation += f" | Khoản {clause}"

            if citation in seen:
                continue

            seen.add(citation)

            lines.append(
                f"[{number}] {citation}"
            )

            number += 1

        return "\n".join(lines)