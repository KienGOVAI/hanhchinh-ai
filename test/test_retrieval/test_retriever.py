import pytest

from app.knowledge.retrieval import (
    InvalidRetrievalQueryError,
    Retriever,
)

from app.knowledge.vectorstore import (
    LocalVectorStore,
    VectorRecord,
)


def create_store():

    store = LocalVectorStore(
        dimension=3
    )

    store.add_many(
        [
            VectorRecord(
                vector_id="chunk-001",
                vector=[1.0, 0.0, 0.0],
                metadata={
                    "document_id": "doc-001",
                    "chunk_index": 0,
                    "page_number": 1,
                    "content": (
                        "Nội dung chuyển đổi số."
                    ),
                },
            ),
            VectorRecord(
                vector_id="chunk-002",
                vector=[0.0, 1.0, 0.0],
                metadata={
                    "document_id": "doc-002",
                    "chunk_index": 0,
                    "page_number": 2,
                    "content": (
                        "Nội dung văn bản hành chính."
                    ),
                },
            ),
            VectorRecord(
                vector_id="chunk-003",
                vector=[0.9, 0.1, 0.0],
                metadata={
                    "document_id": "doc-001",
                    "chunk_index": 1,
                    "page_number": 3,
                    "content": (
                        "Triển khai chuyển đổi số."
                    ),
                },
            ),
        ]
    )

    return store


def test_retriever_search():

    store = create_store()

    retriever = Retriever(
        vector_store=store,
        default_top_k=2,
    )

    results = retriever.search(
        query_vector=[
            1.0,
            0.0,
            0.0,
        ]
    )

    assert len(results) == 2

    assert (
        results[0].vector_id
        == "chunk-001"
    )

    assert (
        results[0].content
        == "Nội dung chuyển đổi số."
    )

    assert (
        results[0].document_id
        == "doc-001"
    )


def test_score_threshold():

    store = create_store()

    retriever = Retriever(
        vector_store=store,
        default_top_k=10,
        score_threshold=0.997,
    )

    results = retriever.search(
        query_vector=[
            1.0,
            0.0,
            0.0,
        ]
    )

    assert len(results) == 1

    assert (
        results[0].vector_id
        == "chunk-001"
    )


def test_search_document():

    store = create_store()

    retriever = Retriever(
        vector_store=store,
        default_top_k=10,
    )

    results = retriever.search_document(
        query_vector=[
            1.0,
            0.0,
            0.0,
        ],
        document_id="doc-001",
    )

    assert results

    assert all(
        result.document_id
        == "doc-001"
        for result in results
    )


def test_empty_query():

    store = create_store()

    retriever = Retriever(
        vector_store=store
    )

    with pytest.raises(
        InvalidRetrievalQueryError
    ):
        retriever.search([])


def test_invalid_top_k():

    store = create_store()

    retriever = Retriever(
        vector_store=store
    )

    with pytest.raises(
        ValueError
    ):
        retriever.search(
            query_vector=[
                1.0,
                0.0,
                0.0,
            ],
            top_k=0,
        )


def test_invalid_threshold():

    store = create_store()

    with pytest.raises(
        ValueError
    ):
        Retriever(
            vector_store=store,
            score_threshold=1.5,
        )