"""
Embedding Provider Abstraction.

Task 12.14.3 - Sprint 12.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


# =========================================================
# EXCEPTIONS
# =========================================================


class EmbeddingError(Exception):
    """
    Lỗi chung của Embedding Provider.
    """


# =========================================================
# BASE PROVIDER
# =========================================================


class BaseEmbeddingProvider(ABC):
    """
    Interface chung cho Embedding Provider.

    Provider thực tế có thể là:

        - Ollama
        - Gemini
        - OpenAI
        - Local embedding model

    AssistantService chỉ làm việc với interface này.
    """

    @abstractmethod
    def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Sinh embedding vector từ text.
        """

        raise NotImplementedError

    # =====================================================
    # BATCH
    # =====================================================

    def embed_many(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Sinh embedding cho nhiều text.

        Mặc định gọi embed() tuần tự.

        Provider thực tế có thể override method này
        để sử dụng batch API.
        """

        if not texts:
            return []

        return [
            self.embed(text)
            for text in texts
        ]