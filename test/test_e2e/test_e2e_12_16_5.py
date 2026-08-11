"""
12.16.5 - E2E Error & Validation.

Mục tiêu:
    Kiểm tra khả năng xử lý lỗi và validation
    của Assistant API trong E2E flow.

Phạm vi:

    HTTP Request
        ↓
    Request Validation
        ↓
    Assistant API
        ↓
    Error Handling
        ↓
    HTTP Response

Các nhóm kiểm tra:

    - Empty question
    - Whitespace question
    - Missing question
    - Null question
    - Wrong question type
    - Unknown fields
    - Very long question
    - Repeated invalid requests
    - Runtime recovery
    - Valid request after invalid request

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

VALID_QUESTION = (
    "Chuyển đổi số là gì?"
)


# =========================================================
# HELPER
# =========================================================

def post_assistant(
    payload: dict,
):
    """
    Gửi payload trực tiếp tới Assistant API.
    """

    return client.post(
        ASSISTANT_ENDPOINT,
        json=payload,
    )


def ask(
    question: str,
):
    """
    Gửi một câu hỏi hợp lệ.
    """

    return post_assistant(
        {
            "question": question,
        }
    )


# =========================================================
# 1. EMPTY QUESTION
# =========================================================

def test_e2e_error_empty_question():
    """
    Question rỗng phải bị từ chối.
    """

    response = ask("")

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 2. WHITESPACE QUESTION
# =========================================================

def test_e2e_error_whitespace_question():
    """
    Question chỉ chứa khoảng trắng
    phải bị từ chối.
    """

    response = ask(
        "     "
    )

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 3. NEWLINE QUESTION
# =========================================================

def test_e2e_error_newline_question():
    """
    Question chỉ chứa newline/tab
    phải bị từ chối.
    """

    response = ask(
        "\n\t\n"
    )

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 4. MISSING QUESTION
# =========================================================

def test_e2e_error_missing_question():
    """
    Request thiếu question
    phải bị validation.
    """

    response = post_assistant(
        {}
    )

    assert response.status_code == 422


# =========================================================
# 5. NULL QUESTION
# =========================================================

def test_e2e_error_null_question():
    """
    question=null phải bị validation.
    """

    response = post_assistant(
        {
            "question": None,
        }
    )

    assert response.status_code == 422


# =========================================================
# 6. INTEGER QUESTION
# =========================================================

def test_e2e_error_integer_question():
    """
    question là số phải bị validation.
    """

    response = post_assistant(
        {
            "question": 123,
        }
    )

    assert response.status_code == 422


# =========================================================
# 7. BOOLEAN QUESTION
# =========================================================

def test_e2e_error_boolean_question():
    """
    question là boolean phải bị validation.
    """

    response = post_assistant(
        {
            "question": True,
        }
    )

    assert response.status_code == 422


# =========================================================
# 8. OBJECT QUESTION
# =========================================================

def test_e2e_error_object_question():
    """
    question là object phải bị validation.
    """

    response = post_assistant(
        {
            "question": {
                "text": VALID_QUESTION,
            },
        }
    )

    assert response.status_code == 422


# =========================================================
# 9. ARRAY QUESTION
# =========================================================

def test_e2e_error_array_question():
    """
    question là array phải bị validation.
    """

    response = post_assistant(
        {
            "question": [
                VALID_QUESTION,
            ],
        }
    )

    assert response.status_code == 422


# =========================================================
# 10. UNKNOWN FIELD
# =========================================================

def test_e2e_error_unknown_field():
    """
    Request có field lạ không được làm
    Assistant runtime bị lỗi.

    API có thể:
        - bỏ qua field;
        - hoặc reject request.

    Nhưng không được trả 5xx.
    """

    response = post_assistant(
        {
            "question": VALID_QUESTION,
            "unknown_field": "test",
        }
    )

    assert response.status_code in (
        200,
        400,
        422,
    )


# =========================================================
# 11. VERY LONG QUESTION
# =========================================================

def test_e2e_error_very_long_question():
    """
    Question rất dài phải được xử lý an toàn.

    Không yêu cầu bắt buộc phải reject.
    Điều quan trọng là API không được
    chết runtime.
    """

    question = "A" * 10000

    response = ask(
        question
    )

    assert response.status_code not in (
        500,
        503,
    )


# =========================================================
# 12. SPECIAL CHARACTERS
# =========================================================

def test_e2e_error_special_characters():
    """
    Ký tự đặc biệt không được làm hỏng API.
    """

    question = (
        "<script>alert('test')</script>"
    )

    response = ask(
        question
    )

    assert response.status_code not in (
        500,
        503,
    )


# =========================================================
# 13. UNICODE QUESTION
# =========================================================

def test_e2e_error_unicode_question():
    """
    Unicode tiếng Việt phải được xử lý bình thường.
    """

    response = ask(
        "Chuyển đổi số ở Việt Nam là gì?"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["question"] == (
        "Chuyển đổi số ở Việt Nam là gì?"
    )


# =========================================================
# 14. QUESTION WITH SPACES
# =========================================================

def test_e2e_error_question_with_outer_spaces():
    """
    Question có khoảng trắng đầu/cuối
    phải được normalize an toàn.
    """

    question = (
        "   Chuyển đổi số là gì?   "
    )

    response = ask(
        question
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["question"] == (
        "Chuyển đổi số là gì?"
    )


# =========================================================
# 15. INVALID REQUEST MUST RETURN JSON
# =========================================================

def test_e2e_error_response_is_json():
    """
    Response lỗi phải có JSON response.
    """

    response = post_assistant(
        {}
    )

    assert response.status_code == 422

    assert response.headers[
        "content-type"
    ].startswith(
        "application/json"
    )

    data = response.json()

    assert isinstance(
        data,
        dict,
    )


# =========================================================
# 16. INVALID REQUEST MUST NOT BREAK RUNTIME
# =========================================================

def test_e2e_error_runtime_recovery():
    """
    Sau một request lỗi,
    Assistant vẫn phải xử lý request hợp lệ.
    """

    invalid_response = post_assistant(
        {}
    )

    assert invalid_response.status_code == 422

    valid_response = ask(
        VALID_QUESTION
    )

    assert valid_response.status_code == 200

    data = valid_response.json()

    assert data["success"] is True

    assert data["answer"]


# =========================================================
# 17. MULTIPLE INVALID REQUESTS
# =========================================================

def test_e2e_error_multiple_invalid_requests():
    """
    Runtime phải chịu được nhiều request lỗi
    liên tiếp.
    """

    invalid_payloads = [
        {},
        {
            "question": None,
        },
        {
            "question": "",
        },
        {
            "question": "   ",
        },
        {
            "question": 123,
        },
    ]

    for payload in invalid_payloads:
        response = post_assistant(
            payload
        )

        assert response.status_code in (
            400,
            422,
        )


# =========================================================
# 18. VALID REQUEST AFTER_MULTIPLE_ERRORS
# =========================================================

def test_e2e_error_valid_request_after_multiple_errors():
    """
    Sau nhiều request lỗi liên tiếp,
    runtime vẫn phải hoạt động.
    """

    invalid_payloads = [
        {},
        {
            "question": None,
        },
        {
            "question": "",
        },
        {
            "question": "   ",
        },
        {
            "question": 123,
        },
    ]

    for payload in invalid_payloads:
        response = post_assistant(
            payload
        )

        assert response.status_code in (
            400,
            422,
        )

    response = ask(
        VALID_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["answer"]

    assert data["citations"]


# =========================================================
# 19. VALIDATION RESPONSE CONTRACT
# =========================================================

def test_e2e_error_validation_contract():
    """
    Validation error phải có cấu trúc JSON
    của FastAPI.
    """

    response = post_assistant(
        {}
    )

    assert response.status_code == 422

    data = response.json()

    assert "detail" in data

    assert isinstance(
        data["detail"],
        list,
    )

    assert data["detail"]


# =========================================================
# 20. ERROR & VALIDATION FLOW GATE
# =========================================================

def test_e2e_error_validation_flow_gate():
    """
    E2E Error & Validation Gate.

    Xác nhận:

        Invalid Request
              ↓
        Validation
              ↓
        400 / 422
              ↓
        Runtime vẫn sống
              ↓
        Valid Request
              ↓
        200
              ↓
        Answer
    """

    # -----------------------------------------------------
    # INVALID
    # -----------------------------------------------------

    invalid_response = post_assistant(
        {}
    )

    assert invalid_response.status_code == 422

    invalid_data = (
        invalid_response.json()
    )

    assert "detail" in invalid_data

    # -----------------------------------------------------
    # VALID AFTER INVALID
    # -----------------------------------------------------

    valid_response = ask(
        VALID_QUESTION
    )

    assert valid_response.status_code == 200

    data = valid_response.json()

    assert data["success"] is True

    assert data["question"] == (
        VALID_QUESTION
    )

    assert data["answer"]

    assert data["citations"]

    assert isinstance(
        data["metadata"],
        dict,
    )