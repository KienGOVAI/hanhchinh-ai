import pytest

from app.knowledge.rag import (
    EmptyQuestionError,
    RAGService,
)

from app.knowledge.retrieval import (
    Retriever,
)

from app.knowledge.vectorstore import (
    LocalVectorStore,
    VectorRecord,
)


class FakeEmbeddingService:
    """
    Embedding giả dùng cho Unit Test.
    """

    def embed(
        self,
        text: str,
    ) -> list[float]:

        return [
            1.0,
            0.0,
            0.0,
        ]


class FakeGenerationProvider:
    """
    AI Provider giả dùng cho Unit Test.
    """

    def __init__(self):

        self.last_prompt = ""

    def generate(
        self,
        prompt: str,
    ) -> str:

        self.last_prompt = prompt

        return (
            "Theo tài liệu tham khảo, "
            "nội dung phù hợp là triển khai "
            "chuyển đổi số."
        )


class FailingGenerationProvider:

    def generate(
        self,
        prompt: str,
    ) -> str:

        raise RuntimeError(
            "AI Provider lỗi."
        )


def create_rag_service():

    store = LocalVectorStore(
        dimension=3
    )

    store.add_many(
        [
            VectorRecord(
                vector_id="chunk-001",
                vector=[
                    1.0,
                    0.0,
                    0.0,
                ],
                metadata={
                    "document_id": "doc-001",
                    "chunk_index": 0,
                    "page_number": 1,
                    "source": (
                        "nghi-quyet-57.pdf"
                    ),
                    "content": (
                        "Triển khai chuyển đổi số."
                    ),
                },
            ),
            VectorRecord(
                vector_id="chunk-002",
                vector=[
                    0.0,
                    1.0,
                    0.0,
                ],
                metadata={
                    "document_id": "doc-002",
                    "chunk_index": 0,
                    "page_number": 2,
                    "source": (
                        "cong-van.docx"
                    ),
                    "content": (
                        "Văn bản hành chính."
                    ),
                },
            ),
        ]
    )

    retriever = Retriever(
        vector_store=store,
        default_top_k=2,
    )

    embedding_service = (
        FakeEmbeddingService()
    )

    generation_provider = (
        FakeGenerationProvider()
    )

    service = RAGService(
        retriever=retriever,
        embedding_service=(
            embedding_service
        ),
        generation_provider=(
            generation_provider
        ),
        top_k=2,
    )

    return (
        service,
        generation_provider,
    )


def test_rag_ask():

    service, provider = (
        create_rag_service()
    )

    result = service.ask(
        "Chuyển đổi số là gì?"
    )

    assert result.answer

    assert result.question == (
        "Chuyển đổi số là gì?"
    )

    assert len(
        result.sources
    ) == 2

    assert (
        result.sources[0].vector_id
        == "chunk-001"
    )

    assert (
        result.metadata[
            "retrieved_count"
        ]
        == 2
    )

    assert (
        "TÀI LIỆU THAM KHẢO"
        in provider.last_prompt
    )

    assert (
        "Chuyển đổi số"
        in provider.last_prompt
    )


def test_empty_question():

    service, _ = (
        create_rag_service()
    )

    with pytest.raises(
        EmptyQuestionError
    ):
        service.ask("")


def test_whitespace_question():

    service, _ = (
        create_rag_service()
    )

    with pytest.raises(
        EmptyQuestionError
    ):
        service.ask("   ")


def test_rag_with_no_matching_context():

    store = LocalVectorStore(
        dimension=3
    )

    store.add(
        VectorRecord(
            vector_id="chunk-001",
            vector=[
                1.0,
                0.0,
                0.0,
            ],
            metadata={
                "document_id": "doc-001",
                "content": (
                    "Nội dung chuyển đổi số."
                ),
            },
        )
    )

    retriever = Retriever(
        vector_store=store,
        default_top_k=5,
        score_threshold=0.9999,
    )

    service = RAGService(
        retriever=retriever,
        embedding_service=(
            FakeEmbeddingService()
        ),
        generation_provider=(
            FakeGenerationProvider()
        ),
    )

    result = service.ask(
        "Câu hỏi"
    )

    assert result.answer

    assert len(
        result.sources
    ) == 1


def test_generation_error():

    store = LocalVectorStore(
        dimension=3
    )

    store.add(
        VectorRecord(
            vector_id="chunk-001",
            vector=[
                1.0,
                0.0,
                0.0,
            ],
            metadata={
                "document_id": "doc-001",
                "content": (
                    "Nội dung."
                ),
            },
        )
    )

    retriever = Retriever(
        vector_store=store
    )

    service = RAGService(
        retriever=retriever,
        embedding_service=(
            FakeEmbeddingService()
        ),
        generation_provider=(
            FailingGenerationProvider()
        ),
    )

    with pytest.raises(
        Exception
    ):
        service.ask(
            "Câu hỏi"
        )