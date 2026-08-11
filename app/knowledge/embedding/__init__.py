"""
Embedding Layer.

Task 12.14.3 - Sprint 12.

Cung cấp abstraction cho Embedding Provider.
"""

from app.knowledge.embedding.embedding_provider import (
    BaseEmbeddingProvider,
    EmbeddingError,
)

from app.knowledge.embedding.demo_embedding import (
    DemoEmbeddingProvider,
)

__all__ = [
    "BaseEmbeddingProvider",
    "EmbeddingError",
    "DemoEmbeddingProvider",
]