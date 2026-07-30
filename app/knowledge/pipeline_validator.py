"""
Knowledge Pipeline Validator
----------------------------

Kiểm tra toàn bộ Embedding Pipeline.
"""

from pathlib import Path
from typing import Dict

from app.knowledge.document_parser import DocumentParser
from app.knowledge.text_chunker import TextChunker
from app.knowledge.embedding_service import EmbeddingService


class PipelineValidator:

    def __init__(
        self,
        embedding_service: EmbeddingService,
    ):

        self.parser = DocumentParser()
        self.chunker = TextChunker()
        self.embedding = embedding_service

    # =====================================================

    def validate(
        self,
        file_path: Path,
    ) -> Dict:

        result = {
            "success": False,
            "text_length": 0,
            "chunk_count": 0,
            "embedding_dimension": 0,
            "errors": [],
        }

        try:

            text = self.parser.parse(file_path)

            result["text_length"] = len(text)

            chunks = self.chunker.chunk(
                knowledge_id="validation",
                text=text,
            )

            result["chunk_count"] = len(chunks)

            if chunks:

                vector = self.embedding.embed_text(
                    chunks[0].text
                )

                result["embedding_dimension"] = len(vector)

            result["success"] = True

        except Exception as ex:

            result["errors"].append(str(ex))

        return result