"""
12.15.5 - API Regression Test.

Mục tiêu:
    Kiểm tra regression của các API chính
    sau khi hoàn thành Sprint 12.

Phạm vi:

    Health API
        ↓
    Knowledge API
        ↓
    Assistant API
        ↓
    HTTP Response Contract

Các contract được kiểm tra:

    - API tồn tại.
    - HTTP status đúng.
    - Response JSON hợp lệ.
    - Health API hoạt động.
    - Knowledge API hoạt động.
    - Assistant API hoạt động.
    - Request validation hoạt động.
    - Response schema ổn định.
    - Không làm hỏng các API đã hoàn thành.

Task 12.15.5 chỉ kiểm tra API Regression.
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

HEALTH_ENDPOINT = "/health"

KNOWLEDGE_ENDPOINT = "/knowledge/search"

ASSISTANT_ENDPOINT = "/assistant/ask"

QUERY = "Chuyển đổi số"


# =========================================================
# HELPER
# =========================================================

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


# =========================================================
# 1. ROOT API
# =========================================================

def test_root_api():
    """
    Root endpoint phải hoạt động.
    """

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        dict,
    )

    assert data["status"] == "Running"


# =========================================================
# 2. ROOT PROJECT
# =========================================================

def test_root_contains_project():
    """
    Root response phải có thông tin project.
    """

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data.get(
        "project"
    )

    assert data.get(
        "version"
    )


# =========================================================
# 3. HEALTH API
# =========================================================

def test_health_api():
    """
    Health endpoint phải hoạt động.
    """

    response = client.get(
        HEALTH_ENDPOINT
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        dict,
    )


# =========================================================
# 4. HEALTH RESPONSE
# =========================================================

def test_health_response_is_json():
    """
    Health API phải trả JSON hợp lệ.
    """

    response = client.get(
        HEALTH_ENDPOINT
    )

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith(
        "application/json"
    )

    assert isinstance(
        response.json(),
        dict,
    )


# =========================================================
# 5. KNOWLEDGE API
# =========================================================

def test_knowledge_api():
    """
    Knowledge API phải tiếp tục hoạt động
    sau các thay đổi của Sprint 12.
    """

    response = knowledge_search(
        QUERY
    )

    assert response.status_code == 200


# =========================================================
# 6. KNOWLEDGE SUCCESS
# =========================================================

def test_knowledge_api_success():
    """
    Knowledge API phải trả success=True
    với request hợp lệ.
    """

    response = knowledge_search(
        QUERY
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True


# =========================================================
# 7. KNOWLEDGE RESPONSE CONTRACT
# =========================================================

def test_knowledge_response_contract():
    """
    Kiểm tra các field bắt buộc của Knowledge API.
    """

    response = knowledge_search(
        QUERY
    )

    assert response.status_code == 200

    data = response.json()

    required_fields = {
        "success",
        "query",
        "total",
        "results",
        "message",
    }

    assert required_fields.issubset(
        data.keys()
    )


# =========================================================
# 8. KNOWLEDGE RESULTS
# =========================================================

def test_knowledge_results_contract():
    """
    Knowledge results phải là list.
    """

    response = knowledge_search(
        QUERY
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data["results"],
        list,
    )

    assert data["total"] == len(
        data["results"]
    )


# =========================================================
# 9. KNOWLEDGE RESULT STRUCTURE
# =========================================================

def test_knowledge_result_structure():
    """
    Nếu có kết quả, mỗi item phải giữ
    các trường Knowledge contract.
    """

    response = knowledge_search(
        QUERY
    )

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    required_fields = {
        "vector_id",
        "score",
        "content",
        "document_id",
        "chunk_index",
        "page_number",
        "metadata",
    }

    for item in results:
        assert required_fields.issubset(
            item.keys()
        )


# =========================================================
# 10. KNOWLEDGE INVALID REQUEST
# =========================================================

def test_knowledge_invalid_request():
    """
    Knowledge request thiếu field bắt buộc
    phải bị validation.
    """

    response = client.post(
        KNOWLEDGE_ENDPOINT,
        json={},
    )

    assert response.status_code == 422


# =========================================================
# 11. ASSISTANT API
# =========================================================

def test_assistant_api():
    """
    Assistant API phải hoạt động.
    """

    response = assistant_ask(
        QUERY
    )

    assert response.status_code == 200


# =========================================================
# 12. ASSISTANT SUCCESS
# =========================================================

def test_assistant_success():
    """
    Assistant API phải trả success=True.
    """

    response = assistant_ask(
        QUERY
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True


# =========================================================
# 13. ASSISTANT RESPONSE CONTRACT
# =========================================================

def test_assistant_response_contract():
    """
    Kiểm tra root response contract của Assistant.
    """

    response = assistant_ask(
        QUERY
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


# =========================================================
# 14. ASSISTANT QUESTION
# =========================================================

def test_assistant_question_contract():
    """
    Assistant phải giữ query người dùng.
    """

    question = (
        "Chuyển đổi số là gì?"
    )

    response = assistant_ask(
        question
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == question


# =========================================================
# 15. ASSISTANT ANSWER
# =========================================================

def test_assistant_answer_contract():
    """
    Assistant phải trả answer không rỗng.
    """

    response = assistant_ask(
        QUERY
    )

    assert response.status_code == 200

    answer = response.json()["answer"]

    assert isinstance(
        answer,
        str,
    )

    assert answer.strip()


# =========================================================
# 16. ASSISTANT CITATIONS
# =========================================================

def test_assistant_citation_contract():
    """
    Assistant phải trả citation.
    """

    response = assistant_ask(
        QUERY
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert isinstance(
        citations,
        list,
    )

    assert len(citations) >= 1


# =========================================================
# 17. ASSISTANT CITATION STRUCTURE
# =========================================================

def test_assistant_citation_structure():
    """
    Citation phải giữ các field API contract.
    """

    response = assistant_ask(
        QUERY
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
# 18. ASSISTANT METADATA
# =========================================================

def test_assistant_metadata_contract():
    """
    Assistant metadata phải là object.
    """

    response = assistant_ask(
        QUERY
    )

    assert response.status_code == 200

    metadata = response.json()[
        "metadata"
    ]

    assert isinstance(
        metadata,
        dict,
    )


# =========================================================
# 19. ASSISTANT CITATION COUNT
# =========================================================

def test_assistant_citation_count_contract():
    """
    citation_count phải khớp số citation
    thực tế trong response.
    """

    response = assistant_ask(
        QUERY
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["metadata"]["citation_count"]
        == len(data["citations"])
    )


# =========================================================
# 20. ASSISTANT INVALID REQUEST
# =========================================================

def test_assistant_invalid_request():
    """
    Request thiếu question phải bị validation.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={},
    )

    assert response.status_code == 422


# =========================================================
# 21. ASSISTANT EMPTY QUESTION
# =========================================================

def test_assistant_empty_question():
    """
    Question rỗng phải bị từ chối.
    """

    response = assistant_ask(
        ""
    )

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 22. ASSISTANT WHITESPACE QUESTION
# =========================================================

def test_assistant_whitespace_question():
    """
    Question chỉ chứa whitespace
    phải bị từ chối.
    """

    response = assistant_ask(
        "   "
    )

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 23. UNKNOWN API
# =========================================================

def test_unknown_api_returns_404():
    """
    Endpoint không tồn tại phải trả 404.
    """

    response = client.get(
        "/api-that-does-not-exist"
    )

    assert response.status_code == 404


# =========================================================
# 24. KNOWLEDGE_AND_ASSISTANT_COEXIST
# =========================================================

def test_knowledge_and_assistant_coexist():
    """
    Knowledge và Assistant phải cùng hoạt động
    trong một application runtime.
    """

    knowledge_response = knowledge_search(
        QUERY
    )

    assistant_response = assistant_ask(
        QUERY
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
# 25. API_REGRESSION_FINAL_CONTRACT
# =========================================================

def test_api_regression_final_contract():
    """
    Regression tổng hợp:

        Root
        Health
        Knowledge
        Assistant

    đều phải hoạt động trong cùng runtime.
    """

    root = client.get("/")

    health = client.get(
        HEALTH_ENDPOINT
    )

    knowledge = knowledge_search(
        QUERY
    )

    assistant = assistant_ask(
        QUERY
    )

    assert root.status_code == 200

    assert health.status_code == 200

    assert knowledge.status_code == 200

    assert assistant.status_code == 200

    assert root.json()["status"] == "Running"

    assert knowledge.json()["success"] is True

    assert assistant.json()["success"] is True

    assert assistant.json()["answer"]

    assert assistant.json()["citations"]