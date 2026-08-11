"""
12.16.1 - E2E Demo Foundation.

Mục tiêu:
    Kiểm tra nền tảng E2E của Hành Chính AI.

Phạm vi:

    Application
        ↓
    Assistant API
        ↓
    Assistant Runtime
        ↓
    Knowledge / Retrieval
        ↓
    Answer

Task 12.16.1 chưa kiểm tra chi tiết UI.
UI E2E sẽ được triển khai ở các task tiếp theo.

Không thay đổi production code.
"""

from __future__ import annotations

import os


# =========================================================
# TEST ENVIRONMENT
# =========================================================

# Demo mode phải được bật trước khi import app.main.
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


# =========================================================
# 1. APPLICATION BOOTSTRAP
# =========================================================

def test_e2e_application_bootstrap():
    """
    Application phải khởi tạo thành công.
    """

    assert app is not None


# =========================================================
# 2. APPLICATION ROOT
# =========================================================

def test_e2e_application_root():
    """
    Kiểm tra application root.
    """

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "Running"

    assert data["project"]

    assert data["version"]


# =========================================================
# 3. ASSISTANT ENDPOINT
# =========================================================

def test_e2e_assistant_endpoint_exists():
    """
    Assistant endpoint phải tồn tại.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={
            "question": QUESTION,
        },
    )

    assert response.status_code == 200


# =========================================================
# 4. QUESTION ENTERS PIPELINE
# =========================================================

def test_e2e_question_enters_pipeline():
    """
    Câu hỏi phải đi vào Assistant pipeline
    và được giữ lại trong response.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={
            "question": QUESTION,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["question"] == QUESTION


# =========================================================
# 5. ANSWER IS GENERATED
# =========================================================

def test_e2e_answer_is_generated():
    """
    Pipeline phải tạo được answer.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={
            "question": QUESTION,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert isinstance(
        data["answer"],
        str,
    )

    assert data["answer"].strip()


# =========================================================
# 6. CITATION REACHES RESPONSE
# =========================================================

def test_e2e_citation_reaches_response():
    """
    Citation phải đi xuyên suốt pipeline
    và xuất hiện trong HTTP response.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={
            "question": QUESTION,
        },
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
# 7. CITATION SOURCE IS PRESERVED
# =========================================================

def test_e2e_citation_source_is_preserved():
    """
    E2E phải giữ được thông tin nguồn.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={
            "question": QUESTION,
        },
    )

    assert response.status_code == 200

    data = response.json()

    citations = data["citations"]

    assert citations

    citation = citations[0]

    assert citation["source"]

    assert citation["document_id"]

    assert citation["page_number"] is not None

    assert citation["chunk_index"] is not None


# =========================================================
# 8. PIPELINE METADATA
# =========================================================

def test_e2e_pipeline_metadata():
    """
    Response phải giữ metadata của pipeline.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={
            "question": QUESTION,
        },
    )

    assert response.status_code == 200

    data = response.json()

    metadata = data["metadata"]

    assert isinstance(
        metadata,
        dict,
    )

    assert metadata.get(
        "pipeline_stage"
    ) is not None

    assert metadata.get(
        "citation_count"
    ) is not None


# =========================================================
# 9. CITATION COUNT
# =========================================================

def test_e2e_citation_count_matches_response():
    """
    citation_count phải khớp số citation thực tế.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={
            "question": QUESTION,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["metadata"]["citation_count"]
        == len(data["citations"])
    )


# =========================================================
# 10. FINAL E2E FOUNDATION
# =========================================================

def test_e2e_foundation():
    """
    E2E Foundation Gate.

    Xác nhận:

        HTTP
          ↓
        Assistant
          ↓
        Answer
          ↓
        Citation
          ↓
        Metadata
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={
            "question": QUESTION,
        },
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
        == len(data["citations"])
    )