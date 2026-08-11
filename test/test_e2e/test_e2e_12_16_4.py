"""
12.16.4 - E2E Citation Flow.

Mục tiêu:
    Kiểm tra toàn bộ luồng Citation từ Retrieval
    đến HTTP Response.

Pipeline:

    RetrievedChunk
        ↓
    CitationService
        ↓
    Citation
        ↓
    AssistantService
        ↓
    Assistant API
        ↓
    AssistantCitation
        ↓
    JSON Response

Phạm vi:
    - Citation generation
    - citation_id
    - source
    - score
    - document_id
    - page_number
    - chunk_index
    - content
    - metadata
    - label
    - citation_count
    - citation consistency

Không thay đổi production code.
"""

from __future__ import annotations

import os


# =========================================================
# TEST ENVIRONMENT
# =========================================================

# Phải bật trước khi import app.main.
os.environ["KNOWLEDGE_DEMO_MODE"] = "true"


# =========================================================
# FASTAPI
# =========================================================

from fastapi.testclient import TestClient


# =========================================================
# APPLICATION
# =========================================================

from app.main import app


# =========================================================
# CLIENT
# =========================================================

client = TestClient(app)


# =========================================================
# CONSTANTS
# =========================================================

ASSISTANT_ENDPOINT = "/assistant/ask"

QUESTION = "Chuyển đổi số là gì?"

RELATED_QUESTION = (
    "Triển khai chuyển đổi số "
    "cần gắn với những nội dung nào?"
)


# =========================================================
# HELPER
# =========================================================

def ask_assistant(
    question: str,
):
    """
    Gửi câu hỏi tới Assistant API.
    """

    return client.post(
        ASSISTANT_ENDPOINT,
        json={
            "question": question,
        },
    )


# =========================================================
# 1. CITATION RESPONSE EXISTS
# =========================================================

def test_e2e_citation_response_exists():
    """
    Assistant response phải có citations.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert "citations" in data

    assert isinstance(
        data["citations"],
        list,
    )

    assert data["citations"]


# =========================================================
# 2. CITATION ID
# =========================================================

def test_e2e_citation_id():
    """
    Citation phải có citation_id ổn định.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        assert citation["citation_id"]

        assert isinstance(
            citation["citation_id"],
            str,
        )

        assert citation[
            "citation_id"
        ].startswith(
            "citation-"
        )


# =========================================================
# 3. SOURCE
# =========================================================

def test_e2e_citation_source():
    """
    Citation phải giữ source.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        assert citation["source"]

        assert isinstance(
            citation["source"],
            str,
        )


# =========================================================
# 4. SCORE
# =========================================================

def test_e2e_citation_score():
    """
    Citation phải giữ similarity score.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        assert citation["score"] is not None

        assert isinstance(
            citation["score"],
            (int, float),
        )


# =========================================================
# 5. DOCUMENT ID
# =========================================================

def test_e2e_citation_document_id():
    """
    Citation phải giữ document_id.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        assert citation["document_id"]

        assert isinstance(
            citation["document_id"],
            str,
        )


# =========================================================
# 6. PAGE NUMBER
# =========================================================

def test_e2e_citation_page_number():
    """
    Citation phải giữ page_number.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        assert (
            citation["page_number"]
            is not None
        )

        assert isinstance(
            citation["page_number"],
            int,
        )


# =========================================================
# 7. CHUNK INDEX
# =========================================================

def test_e2e_citation_chunk_index():
    """
    Citation phải giữ chunk_index.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        assert (
            citation["chunk_index"]
            is not None
        )

        assert isinstance(
            citation["chunk_index"],
            int,
        )


# =========================================================
# 8. CONTENT
# =========================================================

def test_e2e_citation_content():
    """
    Citation phải giữ nội dung chunk nguồn.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        assert citation["content"]

        assert isinstance(
            citation["content"],
            str,
        )


# =========================================================
# 9. METADATA
# =========================================================

def test_e2e_citation_metadata():
    """
    Citation phải giữ metadata nguồn.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        assert isinstance(
            citation["metadata"],
            dict,
        )


# =========================================================
# 10. LABEL
# =========================================================

def test_e2e_citation_label():
    """
    Citation phải có label hiển thị ổn định.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        label = citation["label"]

        assert label

        assert isinstance(
            label,
            str,
        )

        assert citation["source"] in label


# =========================================================
# 11. LABEL CONTAINS PAGE
# =========================================================

def test_e2e_citation_label_contains_page():
    """
    Label phải phản ánh page_number
    khi page_number tồn tại.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        page_number = citation[
            "page_number"
        ]

        if page_number is not None:
            assert (
                f"trang {page_number}"
                in citation["label"]
            )


# =========================================================
# 12. LABEL CONTAINS CHUNK
# =========================================================

def test_e2e_citation_label_contains_chunk():
    """
    Label phải phản ánh chunk_index
    khi chunk_index tồn tại.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        chunk_index = citation[
            "chunk_index"
        ]

        if chunk_index is not None:
            assert (
                f"chunk {chunk_index}"
                in citation["label"]
            )


# =========================================================
# 13. CITATION COUNT
# =========================================================

def test_e2e_citation_count():
    """
    citation_count phải bằng số citation
    thực tế trong response.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    citations = data["citations"]

    citation_count = data[
        "metadata"
    ].get(
        "citation_count"
    )

    assert citation_count is not None

    assert citation_count == len(
        citations
    )


# =========================================================
# 14. CITATION IDs ARE UNIQUE
# =========================================================

def test_e2e_citation_ids_are_unique():
    """
    Các citation_id trong cùng response
    không được trùng nhau.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    citation_ids = [
        citation["citation_id"]
        for citation in citations
    ]

    assert len(
        citation_ids
    ) == len(
        set(citation_ids)
    )


# =========================================================
# 15. CITATION SOURCE IS NOT EMPTY
# =========================================================

def test_e2e_citation_source_is_not_empty():
    """
    Không citation nào được phép thiếu source.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        assert citation[
            "source"
        ].strip()


# =========================================================
# 16. CITATION DOCUMENT SOURCE CONSISTENCY
# =========================================================

def test_e2e_citation_document_source_consistency():
    """
    document_id và source phải cùng tồn tại.

    Citation có document_id thì không được
    mất source.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    for citation in citations:
        if citation["document_id"]:
            assert citation["source"]


# =========================================================
# 17. SECOND QUESTION CITATIONS
# =========================================================

def test_e2e_second_question_citations():
    """
    Citation phải tiếp tục hoạt động
    với một câu hỏi khác.
    """

    response = ask_assistant(
        RELATED_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["answer"]

    assert data["citations"]

    assert (
        data["metadata"]["citation_count"]
        == len(
            data["citations"]
        )
    )


# =========================================================
# 18. CITATION CONTENT RELEVANCE
# =========================================================

def test_e2e_citation_content_relevance():
    """
    Citation phải chứa nội dung liên quan
    tới câu hỏi.
    """

    response = ask_assistant(
        RELATED_QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    citation_content = " ".join(
        citation["content"]
        for citation in citations
    ).lower()

    assert (
        "chuyển đổi số"
        in citation_content
    )


# =========================================================
# 19. CITATION RESPONSE CONTRACT
# =========================================================

def test_e2e_citation_response_contract():
    """
    Kiểm tra đầy đủ API contract của Citation.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    required_fields = {
        "citation_id",
        "source",
        "score",
        "document_id",
        "page_number",
        "chunk_index",
        "content",
        "metadata",
        "label",
    }

    for citation in citations:
        assert required_fields.issubset(
            citation.keys()
        )


# =========================================================
# 20. CITATION FLOW GATE
# =========================================================

def test_e2e_citation_flow_gate():
    """
    E2E Citation Flow Gate.

    Xác nhận toàn bộ luồng:

        RetrievedChunk
              ↓
        CitationService
              ↓
        Citation
              ↓
        AssistantService
              ↓
        API Schema
              ↓
        JSON Response
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    citations = data["citations"]

    assert citations

    for citation in citations:
        assert citation["citation_id"]

        assert citation["source"]

        assert citation["score"] is not None

        assert citation["document_id"]

        assert citation["page_number"] is not None

        assert citation["chunk_index"] is not None

        assert citation["content"]

        assert isinstance(
            citation["metadata"],
            dict,
        )

        assert citation["label"]

    assert (
        data["metadata"]["citation_count"]
        == len(citations)
    )