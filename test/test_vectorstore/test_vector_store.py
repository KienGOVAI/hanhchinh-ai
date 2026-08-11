import pytest

from app.knowledge.vectorstore import (
    LocalVectorStore,
    VectorDimensionError,
    VectorNotFoundError,
    VectorRecord,
)


def test_add_and_count():

    store = LocalVectorStore(
        dimension=3
    )

    store.add(
        VectorRecord(
            vector_id="chunk-001",
            vector=[1.0, 0.0, 0.0],
            metadata={
                "document_id": "doc-001",
            },
        )
    )

    assert store.count() == 1


def test_similarity_search():

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
                },
            ),
            VectorRecord(
                vector_id="chunk-002",
                vector=[0.0, 1.0, 0.0],
                metadata={
                    "document_id": "doc-002",
                },
            ),
            VectorRecord(
                vector_id="chunk-003",
                vector=[0.9, 0.1, 0.0],
                metadata={
                    "document_id": "doc-003",
                },
            ),
        ]
    )

    results = store.search(
        [1.0, 0.0, 0.0],
        top_k=2,
    )

    assert len(results) == 2

    assert (
        results[0].vector_id
        == "chunk-001"
    )

    assert (
        results[1].vector_id
        == "chunk-003"
    )

    assert (
        results[0].score
        > results[1].score
    )


def test_delete():

    store = LocalVectorStore(
        dimension=3
    )

    store.add(
        VectorRecord(
            vector_id="chunk-001",
            vector=[1.0, 0.0, 0.0],
        )
    )

    store.delete(
        "chunk-001"
    )

    assert store.count() == 0


def test_delete_missing_vector():

    store = LocalVectorStore(
        dimension=3
    )

    with pytest.raises(
        VectorNotFoundError
    ):
        store.delete(
            "not-found"
        )


def test_delete_by_document():

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
                },
            ),
            VectorRecord(
                vector_id="chunk-002",
                vector=[0.0, 1.0, 0.0],
                metadata={
                    "document_id": "doc-001",
                },
            ),
            VectorRecord(
                vector_id="chunk-003",
                vector=[0.0, 0.0, 1.0],
                metadata={
                    "document_id": "doc-002",
                },
            ),
        ]
    )

    deleted = store.delete_by_document(
        "doc-001"
    )

    assert deleted == 2
    assert store.count() == 1


def test_dimension_error():

    store = LocalVectorStore(
        dimension=3
    )

    with pytest.raises(
        VectorDimensionError
    ):
        store.add(
            VectorRecord(
                vector_id="chunk-001",
                vector=[
                    1.0,
                    0.0,
                ],
            )
        )


def test_empty_vector_error():

    store = LocalVectorStore()

    with pytest.raises(
        Exception
    ):
        store.add(
            VectorRecord(
                vector_id="chunk-001",
                vector=[],
            )
        )