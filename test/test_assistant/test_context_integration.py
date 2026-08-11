from app.knowledge.assistant import (
    AssistantService,
)

from app.knowledge.embedding import (
    BaseEmbeddingProvider,
)

from app.knowledge.context import (
    ContextBuilder,
    RAGContext,
)

from app.knowledge.retrieval import (
    RetrievedChunk,
)


class FakeEmbeddingProvider(
    BaseEmbeddingProvider
):

    def embed(
        self,
        text: str,
    ) -> list[float]:

        return [
            1.0,
            0.0,
            0.0,
        ]


class FakeRetriever:

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> list[RetrievedChunk]:

        chunks = [
            RetrievedChunk(
                vector_id="chunk-001",
                score=1.0,
                content=(
                    "Nội dung chuyển đổi số."
                ),
                document_id="doc-001",
                chunk_index=0,
                page_number=1,
                metadata={
                    "source": (
                        "Nghị quyết chuyển đổi số"
                    ),
                },
            ),
            RetrievedChunk(
                vector_id="chunk-002",
                score=0.9,
                content=(
                    "Triển khai chuyển đổi số."
                ),
                document_id="doc-001",
                chunk_index=1,
                page_number=2,
                metadata={
                    "source": (
                        "Kế hoạch chuyển đổi số"
                    ),
                },
            ),
        ]

        return [
            chunk
            for chunk in chunks[:top_k]
            if chunk.score >= score_threshold
        ]


def create_service() -> AssistantService:

    return AssistantService(
        embedding_provider=(
            FakeEmbeddingProvider()
        ),
        retriever=FakeRetriever(),
        context_builder=ContextBuilder(
            max_chunks=5
        ),
    )


def test_context_integration():

    service = create_service()

    context = service.build_context(
        question="chuyển đổi số"
    )

    assert isinstance(
        context,
        RAGContext,
    )

    assert len(
        context.documents
    ) == 2

    assert (
        context.metadata[
            "document_count"
        ]
        == 2
    )


def test_context_contains_source():

    service = create_service()

    context = service.build_context(
        question="chuyển đổi số"
    )

    assert (
        context.documents[0].source_id
        == "Nghị quyết chuyển đổi số"
    )


def test_context_contains_content():

    service = create_service()

    context = service.build_context(
        question="chuyển đổi số"
    )

    assert (
        "Nội dung chuyển đổi số."
        in context.text
    )


def test_context_preserves_score():

    service = create_service()

    context = service.build_context(
        question="chuyển đổi số"
    )

    assert (
        context.documents[0].score
        == 1.0
    )

    assert (
        context.documents[1].score
        == 0.9
    )


def test_context_top_k():

    service = create_service()

    context = service.build_context(
        question="chuyển đổi số",
        top_k=1,
    )

    assert len(
        context.documents
    ) == 1

    assert (
        context.documents[0].source_id
        == "Nghị quyết chuyển đổi số"
    )


def test_answer_returns_context():

    service = create_service()

    response = service.answer(
        "chuyển đổi số"
    )

    assert (
        response.metadata[
            "pipeline_stage"
        ]
        == "context"
    )

    assert (
        response.metadata[
            "context_document_count"
        ]
        == 2
    )

    assert (
        response.metadata[
            "context_text"
        ]
    )

    assert len(
        response.citations
    ) == 2