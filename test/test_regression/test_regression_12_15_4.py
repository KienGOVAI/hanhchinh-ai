"""
12.15.4 - Citation Regression Test.

Mục tiêu:
    Kiểm tra regression của Citation layer
    sau khi hoàn thành Sprint 12.14.

Pipeline được kiểm tra:

    RetrievedChunk
        ↓
    CitationService
        ↓
    Citation
        ↓
    Citation Formatting
        ↓
    Context With Citations

Các contract chính:

    - CitationService tạo citation.
    - citation_id ổn định.
    - source được giữ nguyên.
    - score được giữ nguyên.
    - document_id được giữ nguyên.
    - page_number được giữ nguyên.
    - chunk_index được giữ nguyên.
    - content được giữ nguyên.
    - metadata được giữ nguyên.
    - label được tạo ổn định.
    - format() hoạt động ổn định.
    - build_context_with_citations() hoạt động.
    - Danh sách rỗng được xử lý an toàn.

Task 12.15.4 chỉ kiểm tra Citation Regression.
Không thay đổi production code.
"""

from __future__ import annotations

from app.knowledge.citation import (
    Citation,
    CitationService,
)
from app.knowledge.retrieval import (
    RetrievedChunk,
)


# =========================================================
# HELPERS
# =========================================================

def create_chunk(
    *,
    vector_id: str = "chunk-001",
    score: float = 0.95,
    content: str = "Nội dung tài liệu.",
    document_id: str = "doc-001",
    page_number: int = 12,
    chunk_index: int = 3,
    source: str = "nghi-quyet-57.pdf",
) -> RetrievedChunk:
    """
    Tạo RetrievedChunk dùng cho regression test.
    """

    return RetrievedChunk(
        vector_id=vector_id,
        score=score,
        content=content,
        document_id=document_id,
        page_number=page_number,
        chunk_index=chunk_index,
        metadata={
            "source": source,
            "document_name": source,
        },
    )


def create_service() -> CitationService:
    """
    Tạo CitationService.
    """

    return CitationService()


# =========================================================
# 1. SERVICE CREATION
# =========================================================

def test_citation_service_can_be_created():
    """
    CitationService phải khởi tạo được.
    """

    service = create_service()

    assert isinstance(
        service,
        CitationService,
    )


# =========================================================
# 2. BUILD EMPTY
# =========================================================

def test_citation_build_empty():
    """
    build([]) phải trả list rỗng.
    """

    service = create_service()

    citations = service.build([])

    assert isinstance(
        citations,
        list,
    )

    assert citations == []


# =========================================================
# 3. BUILD ONE
# =========================================================

def test_citation_build_one():
    """
    Một RetrievedChunk phải tạo được
    một Citation.
    """

    service = create_service()

    chunk = create_chunk()

    citations = service.build(
        [chunk]
    )

    assert len(citations) == 1

    citation = citations[0]

    assert isinstance(
        citation,
        Citation,
    )


# =========================================================
# 4. CITATION ID
# =========================================================

def test_citation_id_is_stable():
    """
    Citation đầu tiên phải có ID citation-1.
    """

    service = create_service()

    chunk = create_chunk()

    citations = service.build(
        [chunk]
    )

    assert citations[0].citation_id == "citation-1"


# =========================================================
# 5. MULTIPLE CITATION IDS
# =========================================================

def test_multiple_citation_ids_are_sequential():
    """
    Nhiều citation phải được đánh số tuần tự.
    """

    service = create_service()

    chunks = [
        create_chunk(
            vector_id="chunk-001",
        ),
        create_chunk(
            vector_id="chunk-002",
        ),
        create_chunk(
            vector_id="chunk-003",
        ),
    ]

    citations = service.build(
        chunks
    )

    assert [
        citation.citation_id
        for citation in citations
    ] == [
        "citation-1",
        "citation-2",
        "citation-3",
    ]


# =========================================================
# 6. SOURCE
# =========================================================

def test_citation_preserves_source():
    """
    Citation phải giữ source.
    """

    service = create_service()

    chunk = create_chunk(
        source="nghi-quyet-57.pdf",
    )

    citation = service.build(
        [chunk]
    )[0]

    assert citation.source == (
        "nghi-quyet-57.pdf"
    )


# =========================================================
# 7. SCORE
# =========================================================

def test_citation_preserves_score():
    """
    Citation phải giữ similarity score.
    """

    service = create_service()

    chunk = create_chunk(
        score=0.8765,
    )

    citation = service.build(
        [chunk]
    )[0]

    assert citation.score == 0.8765


# =========================================================
# 8. DOCUMENT ID
# =========================================================

def test_citation_preserves_document_id():
    """
    Citation phải giữ document_id.
    """

    service = create_service()

    chunk = create_chunk(
        document_id="document-57",
    )

    citation = service.build(
        [chunk]
    )[0]

    assert citation.document_id == (
        "document-57"
    )


# =========================================================
# 9. PAGE NUMBER
# =========================================================

def test_citation_preserves_page_number():
    """
    Citation phải giữ page_number.
    """

    service = create_service()

    chunk = create_chunk(
        page_number=25,
    )

    citation = service.build(
        [chunk]
    )[0]

    assert citation.page_number == 25


# =========================================================
# 10. CHUNK INDEX
# =========================================================

def test_citation_preserves_chunk_index():
    """
    Citation phải giữ chunk_index.
    """

    service = create_service()

    chunk = create_chunk(
        chunk_index=7,
    )

    citation = service.build(
        [chunk]
    )[0]

    assert citation.chunk_index == 7


# =========================================================
# 11. CONTENT
# =========================================================

def test_citation_preserves_content():
    """
    Citation phải giữ nguyên content.
    """

    content = (
        "Chuyển đổi số là nhiệm vụ "
        "trọng tâm của cải cách hành chính."
    )

    service = create_service()

    chunk = create_chunk(
        content=content,
    )

    citation = service.build(
        [chunk]
    )[0]

    assert citation.content == content


# =========================================================
# 12. METADATA
# =========================================================

def test_citation_preserves_metadata():
    """
    Citation phải giữ metadata của chunk.
    """

    service = create_service()

    chunk = create_chunk()

    citation = service.build(
        [chunk]
    )[0]

    assert isinstance(
        citation.metadata,
        dict,
    )

    assert citation.metadata["source"] == (
        "nghi-quyet-57.pdf"
    )

    assert citation.metadata["document_name"] == (
        "nghi-quyet-57.pdf"
    )


# =========================================================
# 13. LABEL SOURCE
# =========================================================

def test_citation_label_contains_source():
    """
    label phải chứa source.
    """

    service = create_service()

    chunk = create_chunk(
        source="ke-hoach-cds.pdf",
    )

    citation = service.build(
        [chunk]
    )[0]

    assert (
        "ke-hoach-cds.pdf"
        in citation.label
    )


# =========================================================
# 14. LABEL PAGE
# =========================================================

def test_citation_label_contains_page():
    """
    label phải chứa số trang khi có page_number.
    """

    service = create_service()

    chunk = create_chunk(
        page_number=18,
    )

    citation = service.build(
        [chunk]
    )[0]

    assert (
        "trang 18"
        in citation.label
    )


# =========================================================
# 15. LABEL CHUNK
# =========================================================

def test_citation_label_contains_chunk():
    """
    label phải chứa chunk index khi có.
    """

    service = create_service()

    chunk = create_chunk(
        chunk_index=4,
    )

    citation = service.build(
        [chunk]
    )[0]

    assert (
        "chunk 4"
        in citation.label
    )


# =========================================================
# 16. LABEL FORMAT
# =========================================================

def test_citation_label_format():
    """
    Kiểm tra format label ổn định.
    """

    service = create_service()

    chunk = create_chunk(
        source="van-ban.pdf",
        page_number=12,
        chunk_index=3,
    )

    citation = service.build(
        [chunk]
    )[0]

    assert citation.label == (
        "van-ban.pdf — trang 12 — chunk 3"
    )


# =========================================================
# 17. FORMAT EMPTY
# =========================================================

def test_citation_format_empty():
    """
    format([]) phải trả chuỗi rỗng.
    """

    service = create_service()

    result = service.format([])

    assert result == ""


# =========================================================
# 18. FORMAT ONE
# =========================================================

def test_citation_format_one():
    """
    format() phải tạo citation text.
    """

    service = create_service()

    chunk = create_chunk(
        source="nghi-quyet-57.pdf",
        page_number=12,
    )

    citations = service.build(
        [chunk]
    )

    result = service.format(
        citations
    )

    assert result

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


# =========================================================
# 19. FORMAT MULTIPLE
# =========================================================

def test_citation_format_multiple():
    """
    format() phải giữ thứ tự citation.
    """

    service = create_service()

    chunks = [
        create_chunk(
            vector_id="chunk-001",
            source="document-a.pdf",
            page_number=1,
        ),
        create_chunk(
            vector_id="chunk-002",
            source="document-b.pdf",
            page_number=5,
        ),
    ]

    citations = service.build(
        chunks
    )

    result = service.format(
        citations
    )

    assert "[citation-1]" in result

    assert "[citation-2]" in result

    first_position = result.index(
        "[citation-1]"
    )

    second_position = result.index(
        "[citation-2]"
    )

    assert (
        first_position
        < second_position
    )


# =========================================================
# 20. CONTEXT EMPTY
# =========================================================

def test_citation_context_empty():
    """
    Context có citation với chunks rỗng
    phải trả chuỗi rỗng.
    """

    service = create_service()

    result = (
        service.build_context_with_citations(
            []
        )
    )

    assert result == ""


# =========================================================
# 21. CONTEXT ONE
# =========================================================

def test_citation_context_one():
    """
    Context phải chứa citation marker
    và content.
    """

    service = create_service()

    chunk = create_chunk(
        content="Nội dung kiểm thử citation.",
    )

    result = (
        service.build_context_with_citations(
            [chunk]
        )
    )

    assert result

    assert (
        "[citation-1]"
        in result
    )

    assert (
        "Nội dung kiểm thử citation."
        in result
    )


# =========================================================
# 22. CONTEXT MULTIPLE
# =========================================================

def test_citation_context_multiple():
    """
    Context nhiều chunk phải giữ thứ tự.
    """

    service = create_service()

    chunks = [
        create_chunk(
            vector_id="chunk-001",
            content="Nội dung thứ nhất.",
        ),
        create_chunk(
            vector_id="chunk-002",
            content="Nội dung thứ hai.",
        ),
    ]

    result = (
        service.build_context_with_citations(
            chunks
        )
    )

    assert "[citation-1]" in result

    assert "[citation-2]" in result

    assert (
        "Nội dung thứ nhất."
        in result
    )

    assert (
        "Nội dung thứ hai."
        in result
    )

    first_position = result.index(
        "[citation-1]"
    )

    second_position = result.index(
        "[citation-2]"
    )

    assert (
        first_position
        < second_position
    )


# =========================================================
# 23. CONTEXT CONTENT ORDER
# =========================================================

def test_citation_context_preserves_content_order():
    """
    Nội dung chunk phải xuất hiện
    đúng thứ tự citation.
    """

    service = create_service()

    chunks = [
        create_chunk(
            vector_id="chunk-001",
            content="FIRST-CONTENT",
        ),
        create_chunk(
            vector_id="chunk-002",
            content="SECOND-CONTENT",
        ),
    ]

    result = (
        service.build_context_with_citations(
            chunks
        )
    )

    first_position = result.index(
        "FIRST-CONTENT"
    )

    second_position = result.index(
        "SECOND-CONTENT"
    )

    assert (
        first_position
        < second_position
    )


# =========================================================
# 24. CITATION TYPE
# =========================================================

def test_citation_result_type():
    """
    build() phải trả đúng domain model Citation.
    """

    service = create_service()

    chunks = [
        create_chunk(),
        create_chunk(
            vector_id="chunk-002",
        ),
    ]

    citations = service.build(
        chunks
    )

    assert all(
        isinstance(
            citation,
            Citation,
        )
        for citation in citations
    )


# =========================================================
# 25. CITATION_COUNT
# =========================================================

def test_citation_count_matches_chunks():
    """
    Số citation phải bằng số RetrievedChunk
    đầu vào.
    """

    service = create_service()

    chunks = [
        create_chunk(
            vector_id="chunk-001",
        ),
        create_chunk(
            vector_id="chunk-002",
        ),
        create_chunk(
            vector_id="chunk-003",
        ),
    ]

    citations = service.build(
        chunks
    )

    assert len(citations) == len(
        chunks
    )