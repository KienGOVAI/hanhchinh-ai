"""
AI Assistant Service.

Task 12.14.3 - Embedding Integration.

Luồng hiện tại:

Question
    -> Embedding Provider
    -> Query Vector

Các bước Retriever / Context / RAG
sẽ được tích hợp ở các task tiếp theo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from app.knowledge.embedding import (
    BaseEmbeddingProvider,
    EmbeddingError,
)


# =========================================================
# EXCEPTIONS
# =========================================================


class AssistantServiceError(Exception):
    """
    Lỗi chung của AI Assistant Service.
    """


class InvalidAssistantQuestionError(
    AssistantServiceError
):
    """
    Câu hỏi không hợp lệ.
    """


class AssistantEmbeddingError(
    AssistantServiceError
):
    """
    Lỗi trong quá trình tạo embedding.
    """


# =========================================================
# RESPONSE
# =========================================================


@dataclass
class AssistantResponse:
    """
    Kết quả trả về của AI Assistant.
    """

    answer: str

    query: str

    citations: list[Any] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =========================================================
# DEPENDENCY PROTOCOLS
# =========================================================


class RetrieverProtocol(Protocol):
    """
    Interface tối thiểu cho Retriever.
    """

    def search(
        self,
        query_vector: list[float],
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> list[Any]:
        ...


class ContextBuilderProtocol(Protocol):
    """
    Interface tối thiểu cho ContextBuilder.
    """

    def build(
        self,
        chunks: list[Any],
    ) -> Any:
        ...


class RAGServiceProtocol(Protocol):
    """
    Interface tối thiểu cho RAG Service.
    """

    def ask(
        self,
        question: str,
        context: Any,
    ) -> str:
        ...


# =========================================================
# SERVICE
# =========================================================


class AssistantService:
    """
    Điều phối nghiệp vụ AI Assistant.

    Task 12.14.3 tích hợp Embedding Provider.

    Pipeline hiện tại:

        Question
            ↓
        EmbeddingProvider
            ↓
        Query Vector

    Retriever / ContextBuilder / RAGService
    sẽ được tích hợp ở các task tiếp theo.
    """

    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider | None = None,
        retriever: RetrieverProtocol | None = None,
        context_builder: ContextBuilderProtocol | None = None,
        rag_service: RAGServiceProtocol | None = None,
    ) -> None:

        self.embedding_provider = (
            embedding_provider
        )

        self.retriever = retriever

        self.context_builder = (
            context_builder
        )

        self.rag_service = rag_service

    # =====================================================
    # VALIDATION
    # =====================================================

    @staticmethod
    def _validate_question(
        question: str,
    ) -> str:
        """
        Chuẩn hóa và kiểm tra câu hỏi.
        """

        if not isinstance(
            question,
            str,
        ):
            raise InvalidAssistantQuestionError(
                "question phải là chuỗi."
            )

        normalized = question.strip()

        if not normalized:
            raise InvalidAssistantQuestionError(
                "question không được rỗng."
            )

        return normalized

    # =====================================================
    # STATUS
    # =====================================================

    def is_ready(self) -> bool:
        """
        Kiểm tra Assistant đã có Embedding Provider.

        Ở Task 12.14.3, Assistant được xem là
        sẵn sàng cho bước Embedding khi provider tồn tại.

        Retriever / Context / RAG chưa bắt buộc
        ở giai đoạn này.
        """

        return (
            self.embedding_provider
            is not None
        )

    # =====================================================
    # EMBEDDING
    # =====================================================

    def embed_question(
        self,
        question: str,
    ) -> list[float]:
        """
        Sinh query vector từ câu hỏi.

        Đây là điểm tích hợp trực tiếp giữa
        AssistantService và Embedding Provider.
        """

        normalized_question = (
            self._validate_question(
                question
            )
        )

        if self.embedding_provider is None:
            raise AssistantServiceError(
                "Embedding Provider chưa được "
                "khởi tạo."
            )

        try:
            vector = (
                self.embedding_provider.embed(
                    normalized_question
                )
            )

        except EmbeddingError as exc:
            raise AssistantEmbeddingError(
                f"Không thể tạo embedding: {exc}"
            ) from exc

        except Exception as exc:
            raise AssistantEmbeddingError(
                "Đã xảy ra lỗi khi tạo embedding."
            ) from exc

        if not vector:
            raise AssistantEmbeddingError(
                "Embedding Provider trả về "
                "vector rỗng."
            )

        return vector

    # =====================================================
    # ANSWER
    # =====================================================

    def answer(
        self,
        question: str,
    ) -> AssistantResponse:
        """
        Điểm vào chính của AI Assistant.

        Task 12.14.3:

            Question
                ↓
            Embedding
                ↓
            Query Vector

        Chưa thực hiện Retrieval / RAG.
        """

        normalized_question = (
            self._validate_question(
                question
            )
        )

        query_vector = (
            self.embed_question(
                normalized_question
            )
        )

        return AssistantResponse(
            answer="",
            query=normalized_question,
            citations=[],
            metadata={
                "query_vector": query_vector,
                "pipeline_stage": "embedding",
            },
        )

    # =====================================================
    # STATUS
    # =====================================================

    def get_status(
        self,
    ) -> dict[str, Any]:
        """
        Trả về trạng thái của Assistant.
        """

        return {
            "ready": self.is_ready(),
            "embedding_provider": (
                self.embedding_provider
                is not None
            ),
            "retriever": (
                self.retriever is not None
            ),
            "context_builder": (
                self.context_builder is not None
            ),
            "rag_service": (
                self.rag_service is not None
            ),
        }