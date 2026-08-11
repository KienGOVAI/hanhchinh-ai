from app.knowledge.chunking import (
    Chunker,
)

from app.knowledge.models.parsed_document import (
    ParsedDocument,
    ParsedPage,
)


def test_chunk_document():

    document = ParsedDocument(
        text=(
            "Đoạn thứ nhất.\n\n"
            "Đoạn thứ hai.\n\n"
            "Đoạn thứ ba."
        ),
        source="sample.txt",
        pages=[
            ParsedPage(
                page_number=1,
                text=(
                    "Đoạn thứ nhất.\n\n"
                    "Đoạn thứ hai.\n\n"
                    "Đoạn thứ ba."
                ),
            )
        ],
    )

    chunker = Chunker(
        chunk_size=50,
        chunk_overlap=10,
    )

    chunks = chunker.chunk(
        document,
        document_id="doc-001",
    )

    assert chunks

    assert all(
        chunk.document_id
        == "doc-001"
        for chunk in chunks
    )

    assert (
        chunks[0].chunk_index
        == 0
    )

    assert (
        chunks[0].page_number
        == 1
    )

    assert all(
        chunk.content
        for chunk in chunks
    )


def test_empty_document():

    document = ParsedDocument(
        text="",
        source="empty.txt",
        pages=[],
    )

    chunker = Chunker()

    chunks = chunker.chunk(
        document,
        document_id="doc-empty",
    )

    assert chunks == []


def test_invalid_chunk_size():

    try:
        Chunker(
            chunk_size=0
        )

        assert False

    except ValueError:
        assert True


def test_invalid_overlap():

    try:
        Chunker(
            chunk_size=100,
            chunk_overlap=100,
        )

        assert False

    except ValueError:
        assert True