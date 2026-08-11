"""
RAG Service
-----------

Điều phối Retrieval-Augmented Generation.

Task 12.9:
Question
    ↓
Embedding
    ↓
Retriever
    ↓
Relevant Chunks
    ↓
ContextBuilder
    ↓
Generation Provider
    ↓
Answer
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from app.knowledge.context import (
    ContextBuilder,
)

from app.knowledge.retrieval import (
    RetrievedChunk,
    Retriever,
)


# =========================================================
# EXCEPTIONS
# =========================================================


class RAGError(Exception):
    """Lỗi chung của RAG Service."""


class EmptyQuestionError(RAGError):
    """Câu hỏi rỗng."""


class RAGGenerationError(RAGError):
    """Lỗi khi AI sinh câu trả lời."""


# =========================================================
# AI PROVIDER CONTRACT
# =========================================================


class RAGGenerationProvider(Protocol):
    """
    Contract tối thiểu mà AI Provider
    cần đáp ứng để RAG Service sử dụng.
    """

    def generate(
        self,
        prompt: str,
    ) -> str:
        ...


# =========================================================
# RESULT
# =========================================================


@dataclass
class RAGResult:
    """
    Kết quả của RAG Service.
    """

    question: str

    answer: str

    sources: list[RetrievedChunk] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =========================================================
# RAG SERVICE
# =========================================================


class RAGService:
    """
    Điều phối toàn bộ RAG pipeline.

    RAGService không trực tiếp:
    - lưu vector;
    - search vector database;
    - xây dựng Context thủ công.

    Các nhiệm vụ này thuộc service tương ứng.
    """

    def __init__(
        self,
        retriever: Retriever,
        embedding_service: Any,
        generation_provider: RAGGenerationProvider,
        context_builder: ContextBuilder | None = None,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> None:

        if top_k <= 0:
            raise ValueError(
                "top_k phải lớn hơn 0."
            )

        if not 0.0 <= score_threshold <= 1.0:
            raise ValueError(
                "score_threshold phải nằm "
                "trong khoảng 0.0 đến 1.0."
            )

        self.retriever = retriever

        self.embedding_service = (
            embedding_service
        )

        self.generation_provider = (
            generation_provider
        )

        self.context_builder = (
            context_builder
            or ContextBuilder()
        )

        self.top_k = top_k

        self.score_threshold = (
            score_threshold
        )

    # =====================================================
    # PUBLIC
    # =====================================================

    def ask(
        self,
        question: str,
    ) -> RAGResult:
        """
        Thực hiện toàn bộ RAG pipeline.
        """

        question = question.strip()

        if not question:
            raise EmptyQuestionError(
                "Câu hỏi không được rỗng."
            )

        # -------------------------------------------------
        # EMBEDDING
        # -------------------------------------------------

        query_vector = (
            self._create_embedding(
                question
            )
        )

        # -------------------------------------------------
        # RETRIEVAL
        # -------------------------------------------------

        chunks = self.retriever.search(
            query_vector=query_vector,
            top_k=self.top_k,
            score_threshold=(
                self.score_threshold
            ),
        )

        # -------------------------------------------------
        # CONTEXT BUILDER
        # -------------------------------------------------

        rag_context = (
            self.context_builder.build(
                chunks
            )
        )

        # -------------------------------------------------
        # PROMPT
        # -------------------------------------------------

        prompt = self._build_prompt(
            question=question,
            context=rag_context.text,
        )

        # -------------------------------------------------
        # GENERATION
        # -------------------------------------------------

        answer = self._generate_answer(
            prompt
        )

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        return RAGResult(
            question=question,
            answer=answer,
            sources=chunks,
            metadata={
                "retrieved_count": len(
                    chunks
                ),
                "context_count": len(
                    rag_context.documents
                ),
                "top_k": self.top_k,
                "score_threshold": (
                    self.score_threshold
                ),
            },
        )

    # =====================================================
    # EMBEDDING
    # =====================================================

    def _create_embedding(
        self,
        text: str,
    ) -> list[float]:

        try:

            if not hasattr(
                self.embedding_service,
                "embed",
            ):
                raise RAGError(
                    "EmbeddingService không "
                    "có method embed()."
                )

            vector = (
                self.embedding_service.embed(
                    text
                )
            )

        except RAGError:
            raise

        except Exception as exc:

            raise RAGError(
                "Không thể tạo query embedding."
            ) from exc

        if not vector:

            raise RAGError(
                "EmbeddingService trả về "
                "vector rỗng."
            )

        return vector

    # =====================================================
    # PROMPT
    # =====================================================

    @staticmethod
    def _build_prompt(
        question: str,
        context: str,
    ) -> str:
        """
        Tạo prompt cho AI Provider.

        Prompt nâng cao sẽ được tiếp tục
        hoàn thiện ở các Task sau.
        """

        return f"""
Bạn là trợ lý AI hỗ trợ tra cứu
văn bản hành chính.

Hãy trả lời câu hỏi dựa trên
nguồn tài liệu được cung cấp.

Nếu tài liệu không đủ thông tin,
hãy nói rõ rằng không tìm thấy
thông tin phù hợp.

Không tự bịa thông tin.

=== TÀI LIỆU THAM KHẢO ===

{context}

=== CÂU HỎI ===

{question}

=== TRẢ LỜI ===
""".strip()

    # =====================================================
    # GENERATION
    # =====================================================

    def _generate_answer(
        self,
        prompt: str,
    ) -> str:

        try:

            answer = (
                self.generation_provider.generate(
                    prompt
                )
            )

        except Exception as exc:

            raise RAGGenerationError(
                "AI Provider không thể "
                "sinh câu trả lời."
            ) from exc

        if not isinstance(
            answer,
            str,
        ):

            raise RAGGenerationError(
                "AI Provider phải trả về str."
            )

        answer = answer.strip()

        if not answer:

            raise RAGGenerationError(
                "AI Provider trả về "
                "câu trả lời rỗng."
            )

        return answer