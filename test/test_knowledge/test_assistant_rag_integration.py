"""
Integration tests for AssistantService + RAG.

Sprint 13.4.1
Chat + RAG Integration

Mục tiêu:
    Question
        ↓
    AssistantService
        ↓
    RAGService
        ↓
    RAGResult
        ↓
    Retrieved Sources
        ↓
    CitationService
        ↓
    AssistantResponse

Không sử dụng model AI thật.
Toàn bộ dependency được mock bằng fake objects để
test đúng contract của pipeline.
"""

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from app.knowledge.assistant.assistant_service import (
    AssistantResponse,
    AssistantService,
)


# =========================================================
# FAKE RAG RESULT
# =========================================================


@dataclass
class FakeRAGResult:
    """
    Kết quả giả lập từ RAGService.
    """

    question: str
    answer: str
    sources: list
    metadata: dict


# =========================================================
# FAKE RAG SERVICE
# =========================================================


class FakeRAGService:
    """
    Fake RAGService dùng cho integration test.
    """

    def __init__(
        self,
        answer: str = "Đây là câu trả lời từ RAG.",
        sources: list | None = None,
        metadata: dict | None = None,
    ):
        self.answer = answer
        self.sources = sources or []
        self.metadata = metadata or {}

        self.called = False
        self.last_question = None

    def ask(
        self,
        question: str,
    ) -> FakeRAGResult:
        self.called = True
        self.last_question = question

        return FakeRAGResult(
            question=question,
            answer=self.answer,
            sources=self.sources,
            metadata=dict(self.metadata),
        )


# =========================================================
# FAKE CITATION SERVICE
# =========================================================


class FakeCitationService:
    """
    Fake CitationService.

    Chuyển RetrievedChunk thành Citation giả lập.
    """

    def __init__(self):
        self.build_called = False
        self.format_called = False
        self.last_chunks = None
        self.last_citations = None

    def build(
        self,
        chunks: list,
    ) -> list:
        self.build_called = True
        self.last_chunks = chunks

        citations = []

        for index, chunk in enumerate(chunks):
            citations.append(
                SimpleNamespace(
                    citation_id=f"cit-{index + 1}",
                    source=getattr(
                        chunk,
                        "source",
                        f"Document {index + 1}",
                    ),
                    score=getattr(
                        chunk,
                        "score",
                        0.9,
                    ),
                    document_id=getattr(
                        chunk,
                        "document_id",
                        f"doc-{index + 1}",
                    ),
                    page_number=getattr(
                        chunk,
                        "page_number",
                        index + 1,
                    ),
                    chunk_index=getattr(
                        chunk,
                        "chunk_index",
                        index,
                    ),
                    content=getattr(
                        chunk,
                        "content",
                        "",
                    ),
                    metadata=getattr(
                        chunk,
                        "metadata",
                        {},
                    ),
                    label=getattr(
                        chunk,
                        "label",
                        f"Document {index + 1}",
                    ),
                )
            )

        self.last_citations = citations

        return citations

    def format(
        self,
        citations: list,
    ) -> str:
        self.format_called = True

        return "\n".join(
            citation.label
            for citation in citations
        )


# =========================================================
# FAKE EMBEDDING PROVIDER
# =========================================================


class FakeEmbeddingProvider:
    """
    Fake embedding provider.

    RAGService thật trong test có thể yêu cầu embedding,
    nhưng AssistantService chỉ cần dependency này khi
    chạy các fallback path.
    """

    def __init__(self):
        self.called = False
        self.last_text = None

    def embed(
        self,
        text: str,
    ) -> list[float]:
        self.called = True
        self.last_text = text

        return [
            0.1,
            0.2,
            0.3,
        ]


# =========================================================
# FAKE RETRIEVER
# =========================================================


class FakeRetriever:
    """
    Fake Retriever dùng cho fallback citation.
    """

    def __init__(
        self,
        results: list | None = None,
    ):
        self.results = results or []

        self.called = False
        self.last_query_vector = None
        self.last_top_k = None
        self.last_score_threshold = None

    def search(
        self,
        query_vector,
        top_k: int,
        score_threshold: float,
    ) -> list:
        self.called = True
        self.last_query_vector = query_vector
        self.last_top_k = top_k
        self.last_score_threshold = score_threshold

        return self.results


# =========================================================
# HELPERS
# =========================================================


def make_chunk(
    *,
    source: str = "Nghị quyết 57-NQ/TW",
    score: float = 0.95,
    document_id: str = "doc-001",
    page_number: int = 3,
    chunk_index: int = 1,
    content: str = "Chuyển đổi số là nhiệm vụ quan trọng.",
):
    """
    Tạo RetrievedChunk-compatible object.
    """

    return SimpleNamespace(
        source=source,
        score=score,
        document_id=document_id,
        page_number=page_number,
        chunk_index=chunk_index,
        content=content,
        metadata={
            "document_name": source,
        },
        label=(
            f"{source} — trang {page_number}"
        ),
    )


def make_service(
    *,
    rag_service=None,
    citation_service=None,
    retriever=None,
    embedding_provider=None,
):
    """
    Tạo AssistantService phục vụ test.
    """

    return AssistantService(
        embedding_provider=(
            embedding_provider
            or FakeEmbeddingProvider()
        ),
        retriever=retriever,
        context_builder=None,
        rag_service=rag_service,
        citation_service=(
            citation_service
            or FakeCitationService()
        ),
    )


# =========================================================
# TEST 1
# =========================================================


def test_rag_service_is_called():
    """
    AssistantService.answer() phải gọi RAGService
    khi RAGService được cấu hình.
    """

    rag_service = FakeRAGService(
        answer="Câu trả lời từ RAG."
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "Chuyển đổi số là gì?"
    )

    assert rag_service.called is True

    assert (
        rag_service.last_question
        == "Chuyển đổi số là gì?"
    )

    assert isinstance(
        result,
        AssistantResponse,
    )


# =========================================================
# TEST 2
# =========================================================


def test_rag_answer_is_returned():
    """
    Answer trong RAGResult phải được trả nguyên vẹn
    trong AssistantResponse.
    """

    rag_service = FakeRAGService(
        answer=(
            "Chuyển đổi số là quá trình ứng dụng "
            "công nghệ số vào hoạt động quản lý."
        )
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "Chuyển đổi số là gì?"
    )

    assert (
        result.answer
        == (
            "Chuyển đổi số là quá trình ứng dụng "
            "công nghệ số vào hoạt động quản lý."
        )
    )


# =========================================================
# TEST 3
# =========================================================


def test_question_is_normalized_before_rag():
    """
    Question phải được strip trước khi truyền vào RAG.
    """

    rag_service = FakeRAGService()

    service = make_service(
        rag_service=rag_service,
    )

    service.answer(
        "   Chuyển đổi số là gì?   "
    )

    assert (
        rag_service.last_question
        == "Chuyển đổi số là gì?"
    )


# =========================================================
# TEST 4
# =========================================================


def test_rag_sources_are_converted_to_citations():
    """
    Sources từ RAGResult phải được chuyển thành Citation.
    """

    chunks = [
        make_chunk(
            source="Nghị quyết 57-NQ/TW",
            document_id="doc-001",
            page_number=3,
            chunk_index=1,
        ),
        make_chunk(
            source="Nghị quyết 71/NQ-CP",
            document_id="doc-002",
            page_number=5,
            chunk_index=2,
        ),
    ]

    rag_service = FakeRAGService(
        answer="Câu trả lời có căn cứ.",
        sources=chunks,
    )

    citation_service = FakeCitationService()

    service = make_service(
        rag_service=rag_service,
        citation_service=citation_service,
    )

    result = service.answer(
        "Chính sách chuyển đổi số?"
    )

    assert citation_service.build_called is True

    assert len(result.citations) == 2

    assert (
        result.citations[0].citation_id
        == "cit-1"
    )

    assert (
        result.citations[1].citation_id
        == "cit-2"
    )


# =========================================================
# TEST 5
# =========================================================


def test_rag_metadata_is_preserved():
    """
    Metadata từ RAGResult phải được giữ lại.
    """

    metadata = {
        "retrieved_count": 3,
        "context_count": 2,
        "top_k": 5,
        "score_threshold": 0.4,
    }

    rag_service = FakeRAGService(
        answer="Kết quả RAG.",
        metadata=metadata,
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "RAG là gì?"
    )

    assert (
        result.metadata[
            "retrieved_count"
        ]
        == 3
    )

    assert (
        result.metadata[
            "context_count"
        ]
        == 2
    )

    assert (
        result.metadata["top_k"]
        == 5
    )

    assert (
        result.metadata[
            "score_threshold"
        ]
        == 0.4
    )


# =========================================================
# TEST 6
# =========================================================


def test_citation_count_matches_sources():
    """
    citation_count phải đúng bằng số Citation thực tế.
    """

    chunks = [
        make_chunk(
            source="Document 1",
            document_id="doc-1",
        ),
        make_chunk(
            source="Document 2",
            document_id="doc-2",
        ),
        make_chunk(
            source="Document 3",
            document_id="doc-3",
        ),
    ]

    rag_service = FakeRAGService(
        answer="Kết quả.",
        sources=chunks,
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "Tra cứu tài liệu."
    )

    assert len(result.citations) == 3

    assert (
        result.metadata[
            "citation_count"
        ]
        == 3
    )


# =========================================================
# TEST 7
# =========================================================


def test_empty_rag_sources_returns_empty_citations():
    """
    RAG không có sources thì Assistant vẫn trả answer,
    nhưng citations phải rỗng.
    """

    rag_service = FakeRAGService(
        answer="Không tìm thấy tài liệu phù hợp.",
        sources=[],
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "Một câu hỏi không có nguồn."
    )

    assert (
        result.answer
        == "Không tìm thấy tài liệu phù hợp."
    )

    assert result.citations == []

    assert (
        result.metadata[
            "citation_count"
        ]
        == 0
    )


# =========================================================
# TEST 8
# =========================================================


def test_rag_pipeline_stage_is_citation():
    """
    Khi RAG + Citation hoàn chỉnh,
    pipeline_stage phải là citation.
    """

    rag_service = FakeRAGService(
        answer="Kết quả RAG.",
        sources=[
            make_chunk(),
        ],
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "Hãy tra cứu nghị quyết."
    )

    assert (
        result.metadata[
            "pipeline_stage"
        ]
        == "citation"
    )


# =========================================================
# TEST 9
# =========================================================


def test_citation_format_is_generated():
    """
    CitationService.format() phải được gọi khi
    RAG trả về sources.
    """

    rag_service = FakeRAGService(
        answer="Kết quả RAG.",
        sources=[
            make_chunk(
                source="Nghị quyết 57-NQ/TW"
            ),
        ],
    )

    citation_service = FakeCitationService()

    service = make_service(
        rag_service=rag_service,
        citation_service=citation_service,
    )

    result = service.answer(
        "Nghị quyết 57 nói gì?"
    )

    assert citation_service.format_called is True

    assert (
        "Nghị quyết 57-NQ/TW"
        in result.metadata[
            "citation_text"
        ]
    )


# =========================================================
# TEST 10
# =========================================================


def test_rag_result_is_stored_in_metadata():
    """
    AssistantResponse.metadata phải giữ reference
    tới RAGResult theo contract hiện tại.
    """

    rag_service = FakeRAGService(
        answer="Kết quả RAG.",
        sources=[
            make_chunk(),
        ],
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "RAG là gì?"
    )

    assert "rag_result" in result.metadata

    rag_result = result.metadata[
        "rag_result"
    ]

    assert rag_result.answer == "Kết quả RAG."

    assert (
        rag_result.question
        == "RAG là gì?"
    )


# =========================================================
# TEST 11
# =========================================================


def test_rag_response_query_matches_question():
    """
    Query trong AssistantResponse phải khớp
    với question đã chuẩn hóa.
    """

    rag_service = FakeRAGService(
        answer="Câu trả lời."
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "   RAG là gì?   "
    )

    assert (
        result.query
        == "RAG là gì?"
    )


# =========================================================
# TEST 12
# =========================================================


def test_rag_sources_preserve_document_information():
    """
    Citation phải giữ được các thông tin nguồn:
    document_id, page_number, chunk_index.
    """

    chunk = make_chunk(
        source="Nghị quyết 57-NQ/TW",
        document_id="doc-057",
        page_number=12,
        chunk_index=7,
    )

    rag_service = FakeRAGService(
        answer="Kết quả.",
        sources=[chunk],
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "Nghị quyết 57."
    )

    citation = result.citations[0]

    assert (
        citation.document_id
        == "doc-057"
    )

    assert (
        citation.page_number
        == 12
    )

    assert (
        citation.chunk_index
        == 7
    )


# =========================================================
# TEST 13
# =========================================================


def test_rag_sources_preserve_score():
    """
    Score của RetrievedChunk phải được giữ trong Citation.
    """

    chunk = make_chunk(
        score=0.987,
    )

    rag_service = FakeRAGService(
        answer="Kết quả.",
        sources=[chunk],
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "Tra cứu."
    )

    citation = result.citations[0]

    assert citation.score == pytest.approx(
        0.987
    )


# =========================================================
# TEST 14
# =========================================================


def test_rag_sources_preserve_content():
    """
    Nội dung chunk phải được giữ trong Citation.
    """

    content = (
        "Chuyển đổi số là nhiệm vụ "
        "trọng tâm của Chính phủ."
    )

    chunk = make_chunk(
        content=content,
    )

    rag_service = FakeRAGService(
        answer="Kết quả.",
        sources=[chunk],
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "Chuyển đổi số."
    )

    assert (
        result.citations[0].content
        == content
    )


# =========================================================
# TEST 15
# =========================================================


def test_rag_sources_preserve_metadata():
    """
    Metadata của chunk phải được giữ trong Citation.
    """

    chunk = make_chunk()

    chunk.metadata = {
        "document_name": "Nghị quyết 57-NQ/TW",
        "category": "phap_ly",
        "year": 2025,
    }

    rag_service = FakeRAGService(
        answer="Kết quả.",
        sources=[chunk],
    )

    service = make_service(
        rag_service=rag_service,
    )

    result = service.answer(
        "Tra cứu văn bản."
    )

    metadata = (
        result.citations[0].metadata
    )

    assert (
        metadata["document_name"]
        == "Nghị quyết 57-NQ/TW"
    )

    assert (
        metadata["category"]
        == "phap_ly"
    )

    assert metadata["year"] == 2025