from app.knowledge.citation import (
    CitationService,
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
                "Nội dung về chuyển đổi số."
            ),
            document_id="doc-001",
            chunk_index=0,
            page_number=12,
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
                "Nội dung về chính quyền số."
            ),
            document_id="doc-002",
            chunk_index=3,
            page_number=4,
            metadata={
                "source": (
                    "cong-van.docx"
                )
            },
        ),
    ]


def test_build_citations():

    service = CitationService()

    citations = service.build(
        create_chunks()
    )

    assert len(citations) == 2

    assert (
        citations[0].citation_id
        == "citation-1"
    )

    assert (
        citations[0].source
        == "nghi-quyet-57.pdf"
    )

    assert (
        citations[0].page_number
        == 12
    )

    assert (
        citations[0].chunk_index
        == 0
    )


def test_citation_label():

    service = CitationService()

    citations = service.build(
        create_chunks()
    )

    assert (
        citations[0].label
        == (
            "nghi-quyet-57.pdf"
            " — trang 12"
            " — chunk 0"
        )
    )


def test_format_citations():

    service = CitationService()

    citations = service.build(
        create_chunks()
    )

    result = service.format(
        citations
    )

    assert (
        "[citation-1]"
        in result
    )

    assert (
        "nghi-quyet-57.pdf"
        in result
    )

    assert (
        "trang 12"
        in result
    )

    assert (
        "[citation-2]"
        in result
    )


def test_empty_citations():

    service = CitationService()

    citations = service.build(
        []
    )

    assert citations == []

    assert (
        service.format([])
        == ""
    )


def test_context_with_citations():

    service = CitationService()

    result = (
        service.build_context_with_citations(
            create_chunks()
        )
    )

    assert (
        "[citation-1]"
        in result
    )

    assert (
        "Nội dung về chuyển đổi số."
        in result
    )

    assert (
        "[citation-2]"
        in result
    )

    assert (
        "Nội dung về chính quyền số."
        in result
    )