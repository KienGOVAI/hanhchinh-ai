from app.knowledge.assistant import (
    AssistantService,
    AssistantRetrievalError,
)

from app.knowledge.embedding import (
    BaseEmbeddingProvider,
)

from app.knowledge.retrieval import (
    RetrievedChunk,
    Retriever,
)

from app.knowledge.vectorstore import (
    LocalVectorStore,
    VectorRecord,
)


# =========================================================
# FAKE EMBEDDING
# =========================================================


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


# =========================================================
# STORE
# =========================================================


def create_retriever() -> Retriever:

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
                "chunk_index": 0,
                "page_number": 1,
                "content": (
                    "Nội dung chuyển đổi số."
                ),
            },
        )
    )

    store.add(
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
                "content": (
                    "Nội dung khác."
                ),
            },
        )
    )

    return Retriever(
        vector_store=store,
        default_top_k=5,
        score_threshold=0.0,
    )


# =========================================================
# TEST
# =========================================================


def test_retrieval_integration():

    embedding = (
        FakeEmbeddingProvider()
    )

    retriever = create_retriever()

    service = AssistantService(
        embedding_provider=embedding,
        retriever=retriever,
    )

    results = service.retrieve(
        question="chuyển đổi số"
    )

    assert len(results) == 2

    assert isinstance(
        results[0],
        RetrievedChunk,
    )

    assert (
        results[0].vector_id
        == "chunk-001"
    )

    assert (
        results[0].score
        == 1.0
    )


def test_retrieval_integration_top_k():

    service = AssistantService(
        embedding_provider=(
            FakeEmbeddingProvider()
        ),
        retriever=create_retriever(),
    )

    results = service.retrieve(
        question="chuyển đổi số",
        top_k=1,
    )

    assert len(results) == 1

    assert (
        results[0].vector_id
        == "chunk-001"
    )


def test_retrieval_integration_threshold():

    service = AssistantService(
        embedding_provider=(
            FakeEmbeddingProvider()
        ),
        retriever=create_retriever(),
    )

    results = service.retrieve(
        question="chuyển đổi số",
        score_threshold=1.0,
    )

    assert len(results) == 1

    assert (
        results[0].score
        == 1.0
    )


def test_retrieval_not_initialized():

    service = AssistantService(
        embedding_provider=(
            FakeEmbeddingProvider()
        ),
        retriever=None,
    )

    try:
        service.retrieve(
            question="chuyển đổi số"
        )

        assert False

    except Exception as exc:

        assert isinstance(
            exc,
            Exception,
        )


def test_assistant_is_ready():

    service = AssistantService(
        embedding_provider=(
            FakeEmbeddingProvider()
        ),
        retriever=create_retriever(),
    )

    assert service.is_ready() is True


def test_assistant_answer_retrieval():

    service = AssistantService(
        embedding_provider=(
            FakeEmbeddingProvider()
        ),
        retriever=create_retriever(),
    )

    response = service.answer(
        "chuyển đổi số"
    )

    assert (
        response.query
        == "chuyển đổi số"
    )

    assert (
        response.metadata[
            "pipeline_stage"
        ]
        == "retrieval"
    )

    assert (
        response.metadata[
            "retrieval_count"
        ]
        == 2
    )

    assert (
        len(
            response.metadata[
                "results"
            ]
        )
        == 2
    )