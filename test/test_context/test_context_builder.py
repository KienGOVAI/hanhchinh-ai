import pytest

from app.knowledge.context import (
    ContextBuilder,
)

from app.knowledge.retrieval import (
    RetrievedChunk,
)


def create_chunks():

    return [
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
                    "nghi-quyet-57.pdf"
                )
            },
        ),
        RetrievedChunk(
            vector_id="chunk-002",
            score=0.9,
            content=(
                "Triển khai chính quyền số."
            ),
            document_id="doc-001",
            chunk_index=1,
            page_number=2,
            metadata={
                "source": (
                    "nghi-quyet-57.pdf"
                )
            },
        ),
        RetrievedChunk(
            vector_id="chunk-003",
            score=0.8,
            content=(
                "Dữ liệu số."
            ),
            document_id="doc-002",
            chunk_index=0,
            page_number=3,
            metadata={
                "source": (
                    "cong-van.docx"
                )
            },
        ),
    ]


def test_build_context():

    builder = ContextBuilder(
        max_chunks=3
    )

    context = builder.build(
        create_chunks()
    )

    assert context.text

    assert len(
        context.documents
    ) == 3

    assert (
        context.documents[0].source_id
        == "nghi-quyet-57.pdf"
    )

    assert (
        "Nội dung chuyển đổi số."
        in context.text
    )

    assert (
        "Trang 1"
        in context.text
    )


def test_max_chunks():

    builder = ContextBuilder(
        max_chunks=2
    )

    context = builder.build(
        create_chunks()
    )

    assert len(
        context.documents
    ) == 2

    assert (
        "Dữ liệu số."
        not in context.text
    )


def test_empty_chunks():

    builder = ContextBuilder()

    context = builder.build([])

    assert (
        context.documents
        == []
    )

    assert (
        context.metadata[
            "chunk_count"
        ]
        == 0
    )

    assert (
        "Không tìm thấy"
        in context.text
    )


def test_invalid_max_chunks():

    with pytest.raises(
        ValueError
    ):
        ContextBuilder(
            max_chunks=0
        )


def test_chunk_without_source():

    chunk = RetrievedChunk(
        vector_id="chunk-001",
        score=1.0,
        content="Nội dung.",
        document_id="doc-001",
        chunk_index=5,
        metadata={},
    )

    builder = ContextBuilder()

    context = builder.build(
        [chunk]
    )

    assert (
        context.documents[0].source_id
        == "doc-001"
    )

    assert (
        "Chunk 5"
        in context.text
    )