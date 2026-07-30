"""
Sentence Transformer Embedding
------------------------------

Embedding implementation sử dụng sentence-transformers.
"""

from typing import List, Optional

from sentence_transformers import SentenceTransformer

from app.knowledge.embedding_service import EmbeddingService


class SentenceTransformerEmbedding(EmbeddingService):
    """
    Embedding Service sử dụng sentence-transformers.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
    ):
        self._model_name = model_name
        self._model: Optional[SentenceTransformer] = None

    # =====================================================

    @property
    def model(self) -> SentenceTransformer:
        """
        Lazy load model.
        """

        if self._model is None:
            self._model = SentenceTransformer(
                self._model_name
            )

        return self._model

    # =====================================================

    def embed_text(
        self,
        text: str,
    ) -> List[float]:

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    # =====================================================

    def embed_documents(
        self,
        documents: List[str],
    ) -> List[List[float]]:

        embeddings = self.model.encode(
            documents,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    # =====================================================

    def dimension(self) -> int:

        return self.model.get_sentence_embedding_dimension()

    # =====================================================

    def model_name(self) -> str:

        return self._model_name