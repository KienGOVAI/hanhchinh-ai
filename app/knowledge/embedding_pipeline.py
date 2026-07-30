"""
Embedding Pipeline
------------------

Pipeline tạo embedding từ nguồn tri thức.
"""

from typing import List

from app.knowledge.knowledge_loader import KnowledgeLoader
from app.knowledge.document_parser import DocumentParser
from app.knowledge.text_chunker import TextChunker
from app.knowledge.embedding_service import EmbeddingService
from app.knowledge.text_chunk import TextChunk


class EmbeddingPipeline:

    def __init__(
        self,
        embedding_service: EmbeddingService,
        chunker: TextChunker = None,
        parser: DocumentParser = None,
        loader: KnowledgeLoader = None,
    ):

        self.loader = loader or KnowledgeLoader()
        self.parser = parser or DocumentParser()
        self.chunker = chunker or TextChunker()
        self.embedding_service = embedding_service

    # =====================================================

    def process(
        self,
        knowledge_id: str,
    ) -> List[TextChunk]:
        """
        Xử lý toàn bộ pipeline.
        """

        path = self.loader.get_path(knowledge_id)

        text = self.parser.parse(path)

        chunks = self.chunker.chunk(
            knowledge_id,
            text,
        )

        embeddings = self.embedding_service.embed_documents(
            [chunk.text for chunk in chunks]
        )

        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding

        return chunks