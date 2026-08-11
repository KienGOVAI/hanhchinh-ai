"""
12.15.7 - Regression Final Test.

Mục tiêu:
    Regression cuối Sprint 12.15.

Phạm vi:

    Foundation
        ↓
    Knowledge
        ↓
    Assistant
        ↓
    Citation
        ↓
    API
        ↓
    Final Runtime

Task 12.15.7 là bài kiểm tra tổng hợp cuối Sprint.

Không thay đổi production code.
"""

from __future__ import annotations

import os


# =========================================================
# TEST ENVIRONMENT
# =========================================================

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
# TEST CLIENT
# =========================================================

client = TestClient(app)


# =========================================================
# CONSTANTS
# =========================================================

KNOWLEDGE_ENDPOINT = "/knowledge/search"

ASSISTANT_ENDPOINT = "/assistant/ask"

QUESTION = "Chuyển đổi số là gì?"

RELATED_QUESTION = (
    "Triển khai chuyển đổi số "
    "cần gắn với những nội dung nào?"
)


# =========================================================
# HELPERS
# =========================================================

def knowledge_search(
    query: str,
):
    """
    Gửi request tới Knowledge API.
    """

    return client.post(
        KNOWLEDGE_ENDPOINT,
        json={
            "query": query,
            "query_vector": [
                1.0,
                0.0,
                0.0,
            ],
            "top_k": 5,
            "score_threshold": 0.0,
        },
    )


def assistant_ask(
    question: str,
):
    """
    Gửi request tới Assistant API.
    """

    return client.post(
        ASSISTANT_ENDPOINT,
        json={
            "question": question,
        },
    )


# =========================================================
# 1. APPLICATION STARTUP
# =========================================================

def test_final_application_startup():
    """
    Application phải được import và khởi tạo thành công.
    """

    assert app is not None


# =========================================================
# 2. ROOT
# =========================================================

def test_final_root():
    """
    Root endpoint phải hoạt động.
    """

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "Running"

    assert data["project"]

    assert data["version"]


# =========================================================
# 3. HEALTH
# =========================================================

def test_final_health():
    """
    Health endpoint phải hoạt động.
    """

    response = client.get("/health")

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        dict,
    )


# =========================================================
# 4. KNOWLEDGE API
# =========================================================

def test_final_knowledge_api():
    """
    Knowledge API phải hoạt động.
    """

    response = knowledge_search(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["results"]

    assert data["total"] >= 1


# =========================================================
# 5. KNOWLEDGE RESULT CONTRACT
# =========================================================

def test_final_knowledge_result_contract():
    """
    Knowledge result phải giữ đầy đủ metadata.
    """

    response = knowledge_search(
        QUESTION
    )

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    for item in results:
        assert item["vector_id"]

        assert item["score"] is not None

        assert item["content"]

        assert item["document_id"]

        assert item["page_number"] is not None

        assert item["chunk_index"] is not None

        assert isinstance(
            item["metadata"],
            dict,
        )


# =========================================================
# 6. KNOWLEDGE TOP K
# =========================================================

def test_final_knowledge_top_k():
    """
    Knowledge phải tôn trọng top_k.
    """

    response = client.post(
        KNOWLEDGE_ENDPOINT,
        json={
            "query": QUESTION,
            "query_vector": [
                1.0,
                0.0,
                0.0,
            ],
            "top_k": 1,
            "score_threshold": 0.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(
        data["results"]
    ) <= 1


# =========================================================
# 7. ASSISTANT API
# =========================================================

def test_final_assistant_api():
    """
    Assistant API phải hoạt động.
    """

    response = assistant_ask(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["question"] == QUESTION

    assert data["answer"]


# =========================================================
# 8. ASSISTANT CITATIONS
# =========================================================

def test_final_assistant_citations():
    """
    Assistant phải trả citation.
    """

    response = assistant_ask(
        QUESTION
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
# 9. CITATION CONTRACT
# =========================================================

def test_final_citation_contract():
    """
    Citation cuối pipeline phải giữ đầy đủ
    thông tin nguồn.
    """

    response = assistant_ask(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()["citations"]

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

        assert citation["citation_id"]

        assert citation["source"]

        assert citation["document_id"]

        assert citation["content"]

        assert citation["label"]

        assert isinstance(
            citation["metadata"],
            dict,
        )


# =========================================================
# 10. CITATION COUNT
# =========================================================

def test_final_citation_count():
    """
    citation_count phải khớp số citation thực tế.
    """

    response = assistant_ask(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["metadata"]["citation_count"]
        == len(data["citations"])
    )


# =========================================================
# 11. ASSISTANT METADATA
# =========================================================

def test_final_assistant_metadata():
    """
    Assistant phải trả metadata pipeline.
    """

    response = assistant_ask(
        QUESTION
    )

    assert response.status_code == 200

    metadata = response.json()["metadata"]

    assert isinstance(
        metadata,
        dict,
    )

    assert metadata.get(
        "pipeline_stage"
    ) is not None


# =========================================================
# 12. RELATED QUESTION
# =========================================================

def test_final_related_question():
    """
    Assistant phải xử lý được câu hỏi khác
    trong cùng Knowledge Base.
    """

    response = assistant_ask(
        RELATED_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["answer"]

    assert data["citations"]


# =========================================================
# 13. EMPTY QUESTION
# =========================================================

def test_final_empty_question():
    """
    Câu hỏi rỗng phải bị từ chối.
    """

    response = assistant_ask("")

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 14. WHITESPACE QUESTION
# =========================================================

def test_final_whitespace_question():
    """
    Câu hỏi whitespace phải bị từ chối.
    """

    response = assistant_ask(
        "   "
    )

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 15. INVALID ASSISTANT REQUEST
# =========================================================

def test_final_invalid_assistant_request():
    """
    Request thiếu question phải bị validation.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={},
    )

    assert response.status_code == 422


# =========================================================
# 16. INVALID KNOWLEDGE REQUEST
# =========================================================

def test_final_invalid_knowledge_request():
    """
    Request thiếu Knowledge fields phải bị validation.
    """

    response = client.post(
        KNOWLEDGE_ENDPOINT,
        json={},
    )

    assert response.status_code == 422


# =========================================================
# 17. API COEXISTENCE
# =========================================================

def test_final_api_coexistence():
    """
    Knowledge và Assistant phải cùng hoạt động
    trong một runtime.
    """

    knowledge_response = knowledge_search(
        QUESTION
    )

    assistant_response = assistant_ask(
        QUESTION
    )

    assert (
        knowledge_response.status_code
        == 200
    )

    assert (
        assistant_response.status_code
        == 200
    )

    assert (
        knowledge_response.json()["success"]
        is True
    )

    assert (
        assistant_response.json()["success"]
        is True
    )


# =========================================================
# 18. RESPONSE JSON CONTRACT
# =========================================================

def test_final_response_json_contract():
    """
    Assistant response phải giữ nguyên
    API contract cuối Sprint.
    """

    response = assistant_ask(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert set(
        [
            "success",
            "question",
            "answer",
            "citations",
            "metadata",
            "message",
        ]
    ).issubset(
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
# 19. MULTIPLE REQUESTS
# =========================================================

def test_final_multiple_requests():
    """
    Runtime phải xử lý liên tiếp nhiều request.
    """

    questions = [
        QUESTION,
        RELATED_QUESTION,
        QUESTION,
    ]

    for question in questions:
        response = assistant_ask(
            question
        )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is True

        assert data["answer"]

        assert data["citations"]


# =========================================================
# 20. UNKNOWN ROUTE
# =========================================================

def test_final_unknown_route():
    """
    Route không tồn tại phải trả 404,
    không được làm application crash.
    """

    response = client.get(
        "/this-route-does-not-exist"
    )

    assert response.status_code == 404


# =========================================================
# 21. FINAL REGRESSION GATE
# =========================================================

def test_final_regression_gate():
    """
    Cổng kiểm định cuối Sprint 12.15.

    Kiểm tra đồng thời:

        Root
        Health
        Knowledge
        Assistant
        Citation
    """

    root = client.get("/")

    health = client.get("/health")

    knowledge = knowledge_search(
        QUESTION
    )

    assistant = assistant_ask(
        QUESTION
    )

    assert root.status_code == 200

    assert health.status_code == 200

    assert knowledge.status_code == 200

    assert assistant.status_code == 200

    assert root.json()["status"] == "Running"

    assert knowledge.json()["success"] is True

    assert knowledge.json()["results"]

    assert assistant.json()["success"] is True

    assert assistant.json()["answer"]

    assert assistant.json()["citations"]

    assert (
        assistant.json()["metadata"][
            "citation_count"
        ]
        == len(
            assistant.json()["citations"]
        )
    )