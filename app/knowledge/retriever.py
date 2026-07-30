"""
Retriever
---------

Chuẩn bị context cho LLM.
"""

from typing import List

from app.knowledge.semantic_search import SemanticSearch
from app.knowledge.text_chunk import TextChunk


class Retriever:

    def __init__(
        self,
        semantic_search: SemanticSearch,
    ):
        self.semantic_search = semantic_search

    # =====================================================

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        max_context_length: int = 6000,
    ) -> List[TextChunk]:
        """
        Lấy các chunk phù hợp nhất và giới hạn
        tổng độ dài context.
        """

        chunks = self.semantic_search.search(
            query=query,
            top_k=top_k,
        )

        results = []

        current_length = 0

        for chunk in chunks:

            length = len(chunk.text)

            if current_length + length > max_context_length:
                break

            results.append(chunk)

            current_length += length

        return results

    # =====================================================

    def build_context(
        self,
        query: str,
        top_k: int = 5,
        max_context_length: int = 6000,
    ) -> str:
        """
        Sinh context để đưa vào Prompt.
        """

        chunks = self.retrieve(
            query=query,
            top_k=top_k,
            max_context_length=max_context_length,
        )

        context = []

        for i, chunk in enumerate(chunks, start=1):

            context.append(
                f"[Tài liệu {i}]"
            )

            context.append(chunk.text)

            context.append("")

        return "\n".join(context)