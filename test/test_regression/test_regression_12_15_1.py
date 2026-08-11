"""
12.15.1 - Regression Test Foundation.

Mục tiêu:
    Kiểm tra các contract nền tảng của Hành Chính AI
    sau khi hoàn thành Sprint 12.14.

Pipeline:

    Application
        ↓
    Knowledge Runtime
        ↓
    Assistant Runtime
        ↓
    Assistant API
        ↓
    Answer
        ↓
    Citation

Task 12.15.1 chỉ tập trung vào các regression contract
cơ bản và không thay đổi production code.
"""

from __future__ import annotations

import os


# =========================================================
# TEST ENVIRONMENT
# =========================================================
#
# main.py khởi tạo Knowledge Runtime ngay khi import.
# Vì vậy phải bật Demo Mode trước khi import app.main.
#

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

ASSISTANT_ENDPOINT = "/assistant/ask"

VALID_QUESTION = "Chuyển đổi số là gì?"

SECOND_VALID_QUESTION = (
    "Triển khai chuyển đổi số "
    "cần gắn với những nội dung nào?"
)


# =========================================================
# HELPER
# =========================================================

def ask(question: str):
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
# 1. APPLICATION IMPORT
# =========================================================

def test_regression_application_import():
    """
    Application phải được import thành công.

    Đây là regression gate cơ bản:
    nếu app.main không import được thì
    toàn bộ hệ thống không thể khởi động.
    """

    assert app is not None


# =========================================================
# 2. HOME ENDPOINT
# =========================================================

def test_regression_home_endpoint():
    """
    Home endpoint phải hoạt động bình thường.
    """

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        dict,
    )

    assert data.get("project")

    assert data.get("status") == "Running"

    assert data.get("version")


# =========================================================
# 3. ASSISTANT API AVAILABILITY
# =========================================================

def test_regression_assistant_api_available():
    """
    Assistant API phải được đăng ký trong application.

    Một request hợp lệ không được trả về:
        - 404
        - 405
        - 503
    """

    response = ask(
        VALID_QUESTION
    )

    assert response.status_code == 200


# =========================================================
# 4. QUESTION CONTRACT
# =========================================================

def test_regression_assistant_question_contract():
    """
    Assistant phải giữ nguyên câu hỏi người dùng
    trong response.
    """

    response = ask(
        VALID_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert (
        data["question"]
        == VALID_QUESTION
    )


# =========================================================
# 5. ANSWER CONTRACT
# =========================================================

def test_regression_assistant_answer_contract():
    """
    Assistant phải trả về answer dạng chuỗi
    và không được rỗng.
    """

    response = ask(
        VALID_QUESTION
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
# 6. CITATION CONTRACT
# =========================================================

def test_regression_assistant_citation_contract():
    """
    Assistant phải trả về citation.

    Citation phải giữ được các metadata quan trọng
    từ Knowledge Base.
    """

    response = ask(
        VALID_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    citations = data.get(
        "citations"
    )

    assert isinstance(
        citations,
        list,
    )

    assert len(citations) >= 1

    citation = citations[0]

    assert citation.get(
        "citation_id"
    )

    assert citation.get(
        "source"
    )

    assert citation.get(
        "score"
    ) is not None

    assert citation.get(
        "document_id"
    )

    assert citation.get(
        "page_number"
    ) is not None

    assert citation.get(
        "chunk_index"
    ) is not None

    assert citation.get(
        "content"
    )

    assert citation.get(
        "label"
    )

    assert isinstance(
        citation.get(
            "metadata"
        ),
        dict,
    )


# =========================================================
# 7. METADATA / PIPELINE CONTRACT
# =========================================================

def test_regression_assistant_metadata_contract():
    """
    Response phải có metadata pipeline.

    Regression test đảm bảo các tầng:
        Retrieval
        Context
        RAG
        Citation

    vẫn được phản ánh trong response metadata.
    """

    response = ask(
        VALID_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    metadata = data.get(
        "metadata"
    )

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
# 8. KNOWLEDGE RELEVANCE CONTRACT
# =========================================================

def test_regression_assistant_knowledge_relevance():
    """
    Một câu hỏi khác phải tiếp tục truy xuất
    được nội dung phù hợp từ Knowledge Base.

    Đây là regression quan trọng cho pipeline:

        Question
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
    """

    response = ask(
        SECOND_VALID_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert isinstance(
        data["answer"],
        str,
    )

    assert data["answer"].strip()

    citations = data.get(
        "citations"
    )

    assert isinstance(
        citations,
        list,
    )

    assert len(citations) >= 1


# =========================================================
# 9. EMPTY QUESTION VALIDATION
# =========================================================

def test_regression_empty_question():
    """
    Câu hỏi rỗng phải bị từ chối.

    API hợp lệ:
        400 hoặc 422.
    """

    response = ask("")

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 10. WHITESPACE QUESTION VALIDATION
# =========================================================

def test_regression_whitespace_question():
    """
    Câu hỏi chỉ chứa khoảng trắng
    phải bị từ chối.

    Không được để request này đi vào
    Assistant Runtime.
    """

    response = ask(
        "   "
    )

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 11. INVALID REQUEST VALIDATION
# =========================================================

def test_regression_invalid_request():
    """
    Request thiếu trường question
    phải bị FastAPI validation từ chối.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={},
    )

    assert response.status_code == 422


# =========================================================
# 12. RESPONSE CONTRACT
# =========================================================

def test_regression_assistant_response_contract():
    """
    Kiểm tra contract tổng thể của Assistant Response.
    """

    response = ask(
        VALID_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    # -----------------------------------------------------
    # ROOT FIELDS
    # -----------------------------------------------------

    assert "success" in data

    assert "question" in data

    assert "answer" in data

    assert "citations" in data

    assert "metadata" in data

    assert "message" in data

    # -----------------------------------------------------
    # TYPES
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CONTENT
    # -----------------------------------------------------

    assert data["success"] is True

    assert data["question"].strip()

    assert data["answer"].strip()

    assert data["citations"]

    assert data["message"].strip()