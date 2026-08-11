"""
12.16.3 - E2E Assistant Flow.

Mục tiêu:
    Kiểm tra toàn bộ luồng Assistant từ HTTP request
    đến câu trả lời được sinh ra.

Pipeline:

    HTTP Request
        ↓
    /assistant/ask
        ↓
    AssistantService
        ↓
    Embedding
        ↓
    Retriever
        ↓
    ContextBuilder
        ↓
    RAGService
        ↓
    Generation Provider
        ↓
    Answer

Phạm vi:
    - Assistant API
    - Question
    - Embedding / Retrieval integration
    - Answer generation
    - Metadata
    - Basic citation propagation
    - Validation
    - Multiple requests

Citation detail được kiểm tra sâu hơn ở Task 12.16.4.

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
# 1. ASSISTANT ENDPOINT
# =========================================================

def test_e2e_assistant_endpoint():
    """
    Assistant endpoint phải tồn tại
    và xử lý được request hợp lệ.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200


# =========================================================
# 2. REQUEST SUCCESS
# =========================================================

def test_e2e_assistant_success():
    """
    Assistant phải trả success=True.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True


# =========================================================
# 3. QUESTION IS PRESERVED
# =========================================================

def test_e2e_assistant_question():
    """
    Question phải được giữ nguyên
    trong response.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == QUESTION


# =========================================================
# 4. ANSWER EXISTS
# =========================================================

def test_e2e_assistant_answer_exists():
    """
    Assistant phải sinh được answer.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data["answer"],
        str,
    )

    assert data["answer"].strip()


# =========================================================
# 5. ANSWER IS NOT QUESTION
# =========================================================

def test_e2e_assistant_answer_is_generated():
    """
    Answer phải là nội dung được sinh ra,
    không đơn giản là echo question.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    answer = data["answer"].strip()

    assert answer

    assert answer != QUESTION


# =========================================================
# 6. ASSISTANT RETURNS CITATIONS
# =========================================================

def test_e2e_assistant_returns_citations():
    """
    Assistant flow phải giữ được citation
    từ backend pipeline.

    Chi tiết citation contract được kiểm tra
    ở Task 12.16.4.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data["citations"],
        list,
    )

    assert data["citations"]


# =========================================================
# 7. ASSISTANT METADATA
# =========================================================

def test_e2e_assistant_metadata():
    """
    Assistant response phải có metadata.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data["metadata"],
        dict,
    )

    assert data["metadata"]


# =========================================================
# 8. PIPELINE STAGE
# =========================================================

def test_e2e_assistant_pipeline_stage():
    """
    Metadata phải có pipeline_stage.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    metadata = response.json()[
        "metadata"
    ]

    assert metadata.get(
        "pipeline_stage"
    ) is not None


# =========================================================
# 9. RETRIEVAL COUNT
# =========================================================

def test_e2e_assistant_retrieval_count():
    """
    Assistant phải ghi nhận số lượng
    chunk được retrieval.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    metadata = response.json()[
        "metadata"
    ]

    if (
        "retrieval_count"
        in metadata
    ):
        assert isinstance(
            metadata["retrieval_count"],
            int,
        )

        assert (
            metadata["retrieval_count"]
            >= 0
        )


# =========================================================
# 10. CONTEXT COUNT
# =========================================================

def test_e2e_assistant_context_count():
    """
    Assistant phải ghi nhận context count
    nếu metadata được expose.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    metadata = response.json()[
        "metadata"
    ]

    if (
        "context_count"
        in metadata
    ):
        assert isinstance(
            metadata["context_count"],
            int,
        )

        assert (
            metadata["context_count"]
            >= 0
        )


# =========================================================
# 11. CITATION COUNT
# =========================================================

def test_e2e_assistant_citation_count():
    """
    citation_count phải phản ánh số citation
    thực tế trong response.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    metadata = data["metadata"]

    assert (
        metadata.get(
            "citation_count"
        )
        == len(
            data["citations"]
        )
    )


# =========================================================
# 12. RELATED QUESTION
# =========================================================

def test_e2e_assistant_related_question():
    """
    Assistant phải xử lý được câu hỏi
    khác trong cùng Knowledge Base.
    """

    response = ask_assistant(
        RELATED_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert (
        data["question"]
        == RELATED_QUESTION
    )

    assert data["answer"]

    assert data["citations"]


# =========================================================
# 13. RELEVANT ANSWER
# =========================================================

def test_e2e_assistant_relevant_answer():
    """
    Câu hỏi về triển khai chuyển đổi số
    phải nhận được answer có nội dung liên quan.
    """

    response = ask_assistant(
        RELATED_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    answer = data["answer"].lower()

    assert (
        "chuyển đổi số"
        in answer
    )


# =========================================================
# 14. EMPTY QUESTION
# =========================================================

def test_e2e_assistant_empty_question():
    """
    Question rỗng phải bị từ chối.
    """

    response = ask_assistant(
        ""
    )

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 15. WHITESPACE QUESTION
# =========================================================

def test_e2e_assistant_whitespace_question():
    """
    Question chỉ chứa whitespace
    phải bị từ chối.
    """

    response = ask_assistant(
        "   "
    )

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 16. INVALID REQUEST
# =========================================================

def test_e2e_assistant_invalid_request():
    """
    Request thiếu question
    phải bị FastAPI validation.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={},
    )

    assert response.status_code == 422


# =========================================================
# 17. MULTIPLE QUESTIONS
# =========================================================

def test_e2e_assistant_multiple_questions():
    """
    Runtime phải xử lý liên tiếp nhiều câu hỏi.
    """

    questions = [
        QUESTION,
        RELATED_QUESTION,
        QUESTION,
    ]

    for question in questions:
        response = ask_assistant(
            question
        )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is True

        assert data["question"] == question

        assert data["answer"]

        assert data["citations"]


# =========================================================
# 18. RESPONSE CONTRACT
# =========================================================

def test_e2e_assistant_response_contract():
    """
    Kiểm tra API contract của Assistant.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    required_fields = {
        "success",
        "question",
        "answer",
        "citations",
        "metadata",
        "message",
    }

    assert required_fields.issubset(
        data.keys()
    )

    assert isinstance(
        data["success"],
        bool,
    )

    assert isinstance(
        data["question"],
        str,
    )

    assert isinstance(
        data["answer"],
        str,
    )

    assert isinstance(
        data["citations"],
        list,
    )

    assert isinstance(
        data["metadata"],
        dict,
    )

    assert isinstance(
        data["message"],
        str,
    )


# =========================================================
# 19. ANSWER + CITATION CONSISTENCY
# =========================================================

def test_e2e_assistant_answer_citation_consistency():
    """
    Một answer thành công từ Knowledge-backed
    Assistant phải có citation.
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"]

    assert data["citations"]

    assert (
        data["metadata"]["citation_count"]
        > 0
    )


# =========================================================
# 20. ASSISTANT FLOW GATE
# =========================================================

def test_e2e_assistant_flow_gate():
    """
    E2E Assistant Flow Gate.

    Xác nhận toàn bộ luồng:

        HTTP
          ↓
        Assistant
          ↓
        Embedding
          ↓
        Retrieval
          ↓
        Context
          ↓
        RAG
          ↓
        Answer
          ↓
        Citation
          ↓
        Response
    """

    response = ask_assistant(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["question"] == QUESTION

    assert data["answer"]

    assert data["citations"]

    assert data["metadata"]

    assert (
        data["metadata"]["citation_count"]
        == len(
            data["citations"]
        )
    )