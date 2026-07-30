"""
Semantic Search
---------------

Tìm kiếm ngữ nghĩa trên Vector Store.
"""

from typing import List

from app.knowledge.embedding_service import EmbeddingService
from app.knowledge.text_chunk import TextChunk
from app.knowledge.vector_store import VectorStore


class SemanticSearch:

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_service: EmbeddingService,
    ):

        self.vector_store = vector_store
        self.embedding_service = embedding_service

    # =====================================================

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[TextChunk]:
        """
        Tìm kiếm theo câu hỏi.
        """

        embedding = self.embedding_service.embed_text(
            query
        )

        return self.vector_store.search(
            embedding,
            top_k=top_k,
        )