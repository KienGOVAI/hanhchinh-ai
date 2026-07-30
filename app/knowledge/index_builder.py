"""
Index Builder
-------------

Xây dựng toàn bộ Vector Index từ Knowledge Base.
"""

from pathlib import Path
from typing import Optional

from app.knowledge.embedding_pipeline import EmbeddingPipeline
from app.knowledge.faiss_vector_store import FAISSVectorStore
from app.knowledge.knowledge_factory import KnowledgeFactory


class IndexBuilder:

    def __init__(
        self,
        pipeline: EmbeddingPipeline,
        vector_store: Optional[FAISSVectorStore] = None,
    ):

        self.pipeline = pipeline
        self.vector_store = (
            vector_store or FAISSVectorStore()
        )

    # =====================================================

    def build(
        self,
        output_directory: str = "vector_store",
    ) -> FAISSVectorStore:
        """
        Xây dựng toàn bộ Vector Store.
        """

        self.vector_store.clear()

        for definition in KnowledgeFactory.enabled():

            print(
                f"Indexing: {definition.title}"
            )

            chunks = self.pipeline.process(
                definition.knowledge_id
            )

            self.vector_store.add(chunks)

        self.vector_store.save(
            output_directory
        )

        print(
            f"Done. Total vectors: {self.vector_store.count()}"
        )

        return self.vector_store