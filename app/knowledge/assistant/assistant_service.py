"""
AI Assistant Service.

Sprint 12
Task 12.14.7 - Citation Integration.

Pipeline:

Question
    ↓
Embedding Provider
    ↓
Retriever
    ↓
Retrieved Chunks
    ↓
Context Builder
    ↓
RAG Service
    ↓
Generation Provider
    ↓
Answer
    ↓
Citation Service
    ↓
Answer + Citations

Backward compatibility:

Task 12.14.3
    Embedding Integration

Task 12.14.4
    Retrieval Integration

Task 12.14.5
    Context Integration

Task 12.14.6
    RAG Integration

Task 12.14.7
    Citation Integration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.knowledge.embedding import (
    BaseEmbeddingProvider,
    EmbeddingError,
)

from app.knowledge.retrieval import (
    RetrievedChunk,
    Retriever,
)

from app.knowledge.context import (
    ContextBuilder,
    RAGContext,
)

from app.knowledge.rag import (
    RAGError,
    RAGResult,
    RAGService,
)

from app.knowledge.citation import (
    Citation,
    CitationService,
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


class AssistantRetrievalError(
    AssistantServiceError
):
    """
    Lỗi trong quá trình Retrieval.
    """


class AssistantContextError(
    AssistantServiceError
):
    """
    Lỗi trong quá trình xây dựng Context.
    """


class AssistantRAGError(
    AssistantServiceError
):
    """
    Lỗi trong quá trình RAG.
    """


class AssistantCitationError(
    AssistantServiceError
):
    """
    Lỗi trong quá trình xây dựng Citation.
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
# SERVICE
# =========================================================


class AssistantService:
    """
    Điều phối nghiệp vụ AI Assistant.

    Pipeline:

        Question
            ↓
        Embedding
            ↓
        Retrieval
            ↓
        Context
            ↓
        RAG
            ↓
        Answer
            ↓
        Citation
            ↓
        Answer + Citations

    Các service chuyên biệt được inject
    từ application layer.
    """

    def __init__(
        self,
        embedding_provider: (
            BaseEmbeddingProvider | None
        ) = None,
        retriever: Retriever | None = None,
        context_builder: (
            ContextBuilder | None
        ) = None,
        rag_service: (
            RAGService | None
        ) = None,
        citation_service: (
            CitationService | None
        ) = None,
    ) -> None:

        self.embedding_provider = (
            embedding_provider
        )

        self.retriever = retriever

        self.context_builder = (
            context_builder
        )

        self.rag_service = (
            rag_service
        )

        self.citation_service = (
            citation_service
            or CitationService()
        )

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
        Kiểm tra Assistant có đủ dependency
        tối thiểu cho Retrieval pipeline hay chưa.

        CitationService và RAGService là các
        dependency bổ sung của pipeline nâng cao.
        """

        return (
            self.embedding_provider is not None
            and self.retriever is not None
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
    # RETRIEVAL
    # =====================================================

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> list[RetrievedChunk]:
        """
        Tạo embedding cho câu hỏi và thực hiện
        semantic retrieval.
        """

        normalized_question = (
            self._validate_question(
                question
            )
        )

        if self.retriever is None:
            raise AssistantServiceError(
                "Retriever chưa được khởi tạo."
            )

        query_vector = (
            self.embed_question(
                normalized_question
            )
        )

        try:
            results = self.retriever.search(
                query_vector=query_vector,
                top_k=top_k,
                score_threshold=score_threshold,
            )

        except Exception as exc:
            raise AssistantRetrievalError(
                "Đã xảy ra lỗi khi tìm kiếm "
                "Knowledge Base."
            ) from exc

        return results

    # =====================================================
    # CONTEXT
    # =====================================================

    def build_context(
        self,
        question: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> RAGContext:
        """
        Tạo RAGContext từ câu hỏi.
        """

        normalized_question = (
            self._validate_question(
                question
            )
        )

        if self.context_builder is None:
            raise AssistantContextError(
                "Context Builder chưa được "
                "khởi tạo."
            )

        chunks = self.retrieve(
            question=normalized_question,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        try:
            context = (
                self.context_builder.build(
                    chunks
                )
            )

        except Exception as exc:
            raise AssistantContextError(
                "Đã xảy ra lỗi khi xây dựng "
                "Context cho RAG."
            ) from exc

        return context

    # =====================================================
    # RAG
    # =====================================================

    def rag(
        self,
        question: str,
    ) -> RAGResult:
        """
        Thực hiện RAG pipeline thông qua
        RAGService.
        """

        normalized_question = (
            self._validate_question(
                question
            )
        )

        if self.rag_service is None:
            raise AssistantRAGError(
                "RAG Service chưa được khởi tạo."
            )

        try:
            result = self.rag_service.ask(
                normalized_question
            )

        except RAGError as exc:
            raise AssistantRAGError(
                "RAG không thể xử lý câu hỏi: "
                f"{exc}"
            ) from exc

        except Exception as exc:
            raise AssistantRAGError(
                "Đã xảy ra lỗi trong quá trình RAG."
            ) from exc

        return result

    # =====================================================
    # CITATION
    # =====================================================

    def build_citations(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[Citation]:
        """
        Sinh Citation từ RetrievedChunk.

        CitationService chịu trách nhiệm:

        - document_id
        - source
        - page_number
        - chunk_index
        - score
        - content
        - citation_id
        """

        if self.citation_service is None:
            raise AssistantCitationError(
                "Citation Service chưa được "
                "khởi tạo."
            )

        try:
            citations = (
                self.citation_service.build(
                    chunks
                )
            )

        except Exception as exc:
            raise AssistantCitationError(
                "Đã xảy ra lỗi khi xây dựng "
                "Citation."
            ) from exc

        return citations

    # =====================================================
    # CITATION FORMAT
    # =====================================================

    def format_citations(
        self,
        citations: list[Citation],
    ) -> str:
        """
        Format danh sách Citation thành text.
        """

        if self.citation_service is None:
            raise AssistantCitationError(
                "Citation Service chưa được "
                "khởi tạo."
            )

        try:
            return self.citation_service.format(
                citations
            )

        except Exception as exc:
            raise AssistantCitationError(
                "Đã xảy ra lỗi khi format "
                "Citation."
            ) from exc

    # =====================================================
    # ANSWER
    # =====================================================

    def answer(
        self,
        question: str,
    ) -> AssistantResponse:
        """
        Điều phối toàn bộ Assistant pipeline.

        Khi có đầy đủ RAG + Citation:

            Question
                ↓
            RAGService
                ↓
            RAGResult
                ↓
            RetrievedChunk
                ↓
            CitationService
                ↓
            AssistantResponse

        Nếu RAGResult không trả sources,
        Assistant sẽ fallback về Retriever
        để bảo đảm Citation vẫn được tạo.

        Nếu chưa có RAGService:

            Question
                ↓
            Embedding
                ↓
            Retrieval
                ↓
            Context
                ↓
            Citation
        """

        normalized_question = (
            self._validate_question(
                question
            )
        )

        # =================================================
        # RAG + CITATION
        # =================================================

        if self.rag_service is not None:

            rag_result = self.rag(
                normalized_question
            )

            # -------------------------------------------------
            # Lấy source từ RAGResult
            # -------------------------------------------------

            citation_chunks = list(
                rag_result.sources or []
            )

            # -------------------------------------------------
            # CITATION FALLBACK
            #
            # Một số RAG implementation có thể sinh answer
            # nhưng không đưa RetrievedChunk vào sources.
            #
            # Khi đó dùng Retriever để lấy lại source,
            # bảo đảm API luôn có citation nếu Knowledge Base
            # có kết quả.
            # -------------------------------------------------

            if (
                not citation_chunks
                and self.retriever is not None
            ):
                try:
                    citation_chunks = (
                        self.retrieve(
                            question=(
                                normalized_question
                            ),
                            top_k=5,
                            score_threshold=0.0,
                        )
                    )

                except AssistantServiceError:
                    # Không làm mất answer đã sinh được.
                    citation_chunks = []

            # -------------------------------------------------
            # BUILD CITATIONS
            # -------------------------------------------------

            citations: list[Citation] = []

            if citation_chunks:
                citations = (
                    self.build_citations(
                        citation_chunks
                    )
                )

            citation_text = ""

            if citations:
                citation_text = (
                    self.format_citations(
                        citations
                    )
                )

            # -------------------------------------------------
            # RESPONSE
            # -------------------------------------------------

            metadata = dict(
                rag_result.metadata
            )

            metadata.update(
                {
                    "pipeline_stage": "citation",
                    "retrieved_count": (
                        metadata.get(
                            "retrieved_count",
                            len(
                                citation_chunks
                            ),
                        )
                    ),
                    "context_count": (
                        metadata.get(
                            "context_count",
                            0,
                        )
                    ),
                    "citation_count": len(
                        citations
                    ),
                    "citation_text": (
                        citation_text
                    ),
                    "rag_result": rag_result,
                }
            )

            return AssistantResponse(
                answer=rag_result.answer,
                query=rag_result.question,
                citations=citations,
                metadata=metadata,
            )

        # =================================================
        # RETRIEVAL FALLBACK
        # =================================================

        query_vector = (
            self.embed_question(
                normalized_question
            )
        )

        if self.retriever is None:
            raise AssistantServiceError(
                "Retriever chưa được khởi tạo."
            )

        try:
            results = self.retriever.search(
                query_vector=query_vector,
                top_k=5,
                score_threshold=0.0,
            )

        except Exception as exc:
            raise AssistantRetrievalError(
                "Đã xảy ra lỗi khi tìm kiếm "
                "Knowledge Base."
            ) from exc

        # =================================================
        # CONTEXT FALLBACK
        # =================================================

        if self.context_builder is not None:

            try:
                context = (
                    self.context_builder.build(
                        results
                    )
                )

            except Exception as exc:
                raise AssistantContextError(
                    "Đã xảy ra lỗi khi xây dựng "
                    "Context cho RAG."
                ) from exc

            # -------------------------------------------------
            # CITATION
            # -------------------------------------------------

            citations: list[Citation] = []

            if results:
                citations = (
                    self.build_citations(
                        results
                    )
                )

            citation_text = ""

            if citations:
                citation_text = (
                    self.format_citations(
                        citations
                    )
                )

            return AssistantResponse(
                answer="",
                query=normalized_question,
                citations=citations,
                metadata={
                    "pipeline_stage": "context",
                    "query_vector": query_vector,
                    "retrieval_count": len(
                        results
                    ),
                    "context": context,
                    "context_text": context.text,
                    "context_document_count": (
                        len(
                            context.documents
                        )
                    ),
                    "citation_count": len(
                        citations
                    ),
                    "citation_text": (
                        citation_text
                    ),
                },
            )

        # =================================================
        # RETRIEVAL ONLY
        # =================================================

        citations: list[Citation] = []

        if results:
            citations = (
                self.build_citations(
                    results
                )
            )

        citation_text = ""

        if citations:
            citation_text = (
                self.format_citations(
                    citations
                )
            )

        return AssistantResponse(
            answer="",
            query=normalized_question,
            citations=citations,
            metadata={
                "pipeline_stage": "retrieval",
                "query_vector": query_vector,
                "retrieval_count": len(
                    results
                ),
                "results": results,
                "citation_count": len(
                    citations
                ),
                "citation_text": citation_text,
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

        if (
            self.rag_service is not None
            and self.citation_service is not None
        ):
            pipeline_stage = "citation"

        elif self.rag_service is not None:
            pipeline_stage = "rag"

        elif self.context_builder is not None:
            pipeline_stage = "context"

        elif (
            self.embedding_provider is not None
            and self.retriever is not None
        ):
            pipeline_stage = "retrieval"

        else:
            pipeline_stage = "not_ready"

        return {
            "ready": self.is_ready(),
            "embedding_provider": (
                self.embedding_provider is not None
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
            "citation_service": (
                self.citation_service is not None
            ),
            "pipeline_stage": pipeline_stage,
        }