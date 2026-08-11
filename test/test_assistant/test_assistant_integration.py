"""
12.14.10 - Assistant Integration Test.

Kiểm tra toàn bộ pipeline:

    Question
        ↓
    Assistant API
        ↓
    AssistantService
        ↓
    Embedding
        ↓
    Retrieval
        ↓
    Context
        ↓
    RAG
        ↓
    Citation
        ↓
    Response

Quan trọng:
- Test này tự bảo đảm Knowledge Demo Data tồn tại.
- Không phụ thuộc thứ tự collection của pytest.
- Không sửa production code chỉ để phục vụ test.
"""

from __future__ import annotations

import os

import pytest

from fastapi.testclient import TestClient


# =========================================================
# TEST ENVIRONMENT
# =========================================================

os.environ["KNOWLEDGE_DEMO_MODE"] = "true"


# =========================================================
# APPLICATION
# =========================================================

from app.main import (
    app,
    knowledge_vector_store,
    seed_knowledge_demo_data,
)


# =========================================================
# TEST FIXTURE
# =========================================================

@pytest.fixture(autouse=True)
def ensure_demo_knowledge():
    """
    Mỗi test Assistant tự bảo đảm Knowledge Demo Data tồn tại.

    Không seed ở module-level để tránh làm bẩn state
    của các test API khác.
    """

    seed_knowledge_demo_data(
        knowledge_vector_store
    )


# =========================================================
# TEST CLIENT
# =========================================================

client = TestClient(app)


# =========================================================
# HELPER
# =========================================================

def ask(
    question: str,
):
    """
    Gửi một câu hỏi tới Assistant API.
    """

    return client.post(
        "/assistant/ask",
        json={
            "question": question,
        },
    )


# =========================================================
# 1. API BASIC
# =========================================================

def test_assistant_api_returns_200():
    """
    API phải xử lý được một câu hỏi hợp lệ.
    """

    response = ask(
        "Chuyển đổi số là gì?"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True


# =========================================================
# 2. QUESTION
# =========================================================

def test_assistant_question_is_preserved():
    """
    Kiểm tra câu hỏi được giữ nguyên trong response.
    """

    question = "Chuyển đổi số là gì?"

    response = ask(question)

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == question


# =========================================================
# 3. ANSWER
# =========================================================

def test_assistant_returns_answer():
    """
    Assistant phải sinh được câu trả lời.
    """

    response = ask(
        "Chuyển đổi số là gì?"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"]

    assert isinstance(
        data["answer"],
        str,
    )


# =========================================================
# 4. CITATIONS
# =========================================================

def test_assistant_returns_citations():
    """
    Assistant phải trả về citation.
    """

    response = ask(
        "Chuyển đổi số là gì?"
    )

    assert response.status_code == 200

    data = response.json()

    citations = data["citations"]

    assert isinstance(
        citations,
        list,
    )

    assert len(citations) >= 1


# =========================================================
# 5. CITATION STRUCTURE
# =========================================================

def test_assistant_citation_structure():
    """
    Citation phải giữ được metadata nguồn.
    """

    response = ask(
        "Chuyển đổi số là gì?"
    )

    assert response.status_code == 200

    data = response.json()

    citations = data["citations"]

    assert citations

    citation = citations[0]

    assert citation["citation_id"]

    assert citation["source"]

    assert citation["score"] is not None

    assert citation["document_id"]

    assert citation["page_number"] is not None

    assert citation["chunk_index"] is not None

    assert citation["content"]

    assert citation["label"]

    assert isinstance(
        citation["metadata"],
        dict,
    )


# =========================================================
# 6. METADATA
# =========================================================

def test_assistant_metadata():
    """
    Response phải có metadata pipeline.
    """

    response = ask(
        "Chuyển đổi số là gì?"
    )

    assert response.status_code == 200

    data = response.json()

    metadata = data["metadata"]

    assert isinstance(
        metadata,
        dict,
    )

    assert (
        metadata.get(
            "pipeline_stage"
        )
        is not None
    )

    assert (
        metadata.get(
            "citation_count"
        )
        is not None
    )

    assert (
        metadata.get(
            "citation_count"
        )
        >= 1
    )


# =========================================================
# 7. RETRIEVAL / RELEVANT CONTENT
# =========================================================

def test_assistant_retrieves_relevant_content():
    """
    Kiểm tra câu hỏi khác có thể lấy được
    nội dung liên quan từ Knowledge Base.
    """

    response = ask(
        "Triển khai chuyển đổi số "
        "cần gắn với những nội dung nào?"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["answer"]

    assert len(
        data["citations"]
    ) >= 1


# =========================================================
# 8. EMPTY QUESTION
# =========================================================

def test_assistant_empty_question():
    """
    Câu hỏi rỗng phải bị từ chối.
    """

    response = ask("")

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 9. WHITESPACE QUESTION
# =========================================================

def test_assistant_whitespace_question():
    """
    Câu hỏi chỉ chứa khoảng trắng
    phải bị từ chối.
    """

    response = ask("   ")

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 10. INVALID REQUEST
# =========================================================

def test_assistant_invalid_request():
    """
    Request thiếu question phải bị từ chối.
    """

    response = client.post(
        "/assistant/ask",
        json={},
    )

    assert response.status_code == 422