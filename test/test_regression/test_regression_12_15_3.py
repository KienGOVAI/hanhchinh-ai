"""
12.15.3 - Assistant Regression Test.

Mục tiêu:
    Kiểm tra regression toàn bộ Assistant pipeline
    sau khi hoàn thành Sprint 12.14.

Pipeline:

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
    Answer

Task 12.15.3 chỉ kiểm tra Assistant contract.
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

ASSISTANT_ENDPOINT = "/assistant/ask"

QUESTION = "Chuyển đổi số là gì?"

RELATED_QUESTION = (
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
# 1. ASSISTANT API
# =========================================================

def test_assistant_api_regression():
    """
    Assistant endpoint phải tồn tại và
    xử lý được câu hỏi hợp lệ.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200


# =========================================================
# 2. SUCCESS CONTRACT
# =========================================================

def test_assistant_success_contract():
    """
    Request hợp lệ phải trả success=True.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True


# =========================================================
# 3. QUESTION PRESERVATION
# =========================================================

def test_assistant_question_preservation():
    """
    Assistant phải giữ nguyên câu hỏi
    trong response.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == QUESTION


# =========================================================
# 4. ANSWER EXISTS
# =========================================================

def test_assistant_answer_exists():
    """
    Assistant phải trả về answer.
    """

    response = ask(
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
# 5. ANSWER MUST NOT BE ERROR MESSAGE
# =========================================================

def test_assistant_answer_is_meaningful():
    """
    Answer không được là chuỗi rỗng
    hoặc chỉ chứa whitespace.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    answer = response.json()["answer"]

    assert answer.strip()

    assert len(
        answer.strip()
    ) > 0


# =========================================================
# 6. CITATIONS EXIST
# =========================================================

def test_assistant_citations_exist():
    """
    Assistant phải trả citation
    từ Knowledge Base.
    """

    response = ask(
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
# 7. CITATION DOCUMENT ID
# =========================================================

def test_assistant_citation_document_id():
    """
    Citation phải giữ document_id.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()["citations"]

    assert citations

    for citation in citations:
        assert citation.get(
            "document_id"
        )


# =========================================================
# 8. CITATION SOURCE
# =========================================================

def test_assistant_citation_source():
    """
    Citation phải giữ source.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()["citations"]

    assert citations

    for citation in citations:
        assert citation.get(
            "source"
        )


# =========================================================
# 9. CITATION LOCATION
# =========================================================

def test_assistant_citation_location():
    """
    Citation phải giữ thông tin vị trí
    trong tài liệu:

        page_number
        chunk_index
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()["citations"]

    assert citations

    for citation in citations:
        assert (
            citation.get(
                "page_number"
            )
            is not None
        )

        assert (
            citation.get(
                "chunk_index"
            )
            is not None
        )


# =========================================================
# 10. CITATION CONTENT
# =========================================================

def test_assistant_citation_content():
    """
    Citation phải giữ nội dung chunk.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()["citations"]

    assert citations

    for citation in citations:
        assert citation.get(
            "content"
        )

        assert isinstance(
            citation["content"],
            str,
        )


# =========================================================
# 11. CITATION LABEL
# =========================================================

def test_assistant_citation_label():
    """
    Citation phải có label ổn định
    để frontend hiển thị.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()["citations"]

    assert citations

    for citation in citations:
        assert citation.get(
            "label"
        )

        assert isinstance(
            citation["label"],
            str,
        )


# =========================================================
# 12. CITATION METADATA
# =========================================================

def test_assistant_citation_metadata():
    """
    Citation phải giữ metadata dạng object.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()["citations"]

    assert citations

    for citation in citations:
        assert isinstance(
            citation.get(
                "metadata"
            ),
            dict,
        )


# =========================================================
# 13. PIPELINE METADATA
# =========================================================

def test_assistant_pipeline_metadata():
    """
    Assistant phải trả metadata pipeline.
    """

    response = ask(
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
# 14. CITATION COUNT METADATA
# =========================================================

def test_assistant_citation_count():
    """
    citation_count phải phản ánh số citation
    thực tế trả về.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    citations = data["citations"]

    metadata = data["metadata"]

    assert (
        metadata["citation_count"]
        == len(citations)
    )

    assert metadata["citation_count"] >= 1


# =========================================================
# 15. RETRIEVAL COUNT
# =========================================================

def test_assistant_retrieval_metadata():
    """
    Assistant phải giữ thông tin retrieval
    trong metadata nếu runtime cung cấp.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    metadata = response.json()["metadata"]

    if "retrieved_count" in metadata:
        assert isinstance(
            metadata["retrieved_count"],
            int,
        )

        assert (
            metadata["retrieved_count"]
            >= 0
        )


# =========================================================
# 16. CONTEXT COUNT
# =========================================================

def test_assistant_context_metadata():
    """
    Assistant phải giữ thông tin context
    nếu runtime cung cấp.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    metadata = response.json()["metadata"]

    if "context_count" in metadata:
        assert isinstance(
            metadata["context_count"],
            int,
        )

        assert (
            metadata["context_count"]
            >= 0
        )


# =========================================================
# 17. RELATED QUESTION
# =========================================================

def test_assistant_related_question():
    """
    Assistant phải tiếp tục hoạt động với
    một câu hỏi khác cùng Knowledge Base.
    """

    response = ask(
        RELATED_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["answer"].strip()

    assert isinstance(
        data["citations"],
        list,
    )

    assert len(
        data["citations"]
    ) >= 1


# =========================================================
# 18. EMPTY QUESTION
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
# 19. WHITESPACE QUESTION
# =========================================================

def test_assistant_whitespace_question():
    """
    Câu hỏi chỉ chứa whitespace
    phải bị từ chối.
    """

    response = ask(
        "   "
    )

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 20. INVALID REQUEST
# =========================================================

def test_assistant_invalid_request():
    """
    Request thiếu question
    phải bị FastAPI validation từ chối.
    """

    response = client.post(
        ASSISTANT_ENDPOINT,
        json={},
    )

    assert response.status_code == 422


# =========================================================
# 21. RESPONSE MESSAGE
# =========================================================

def test_assistant_response_message():
    """
    Response phải có message.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert "message" in data

    assert isinstance(
        data["message"],
        str,
    )

    assert data["message"].strip()


# =========================================================
# 22. RESPONSE CONTRACT
# =========================================================

def test_assistant_response_contract():
    """
    Kiểm tra toàn bộ root response contract.
    """

    response = ask(
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
# 23. CITATION ORDER
# =========================================================

def test_assistant_citation_order():
    """
    Citation phải giữ thứ tự retrieval.

    citation-1, citation-2, ...
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()["citations"]

    assert citations

    citation_ids = [
        citation["citation_id"]
        for citation in citations
    ]

    expected_ids = [
        f"citation-{index}"
        for index in range(
            1,
            len(citations) + 1,
        )
    ]

    assert citation_ids == expected_ids


# =========================================================
# 24. MULTIPLE CITATIONS
# =========================================================

def test_assistant_multiple_citations():
    """
    Với Knowledge Demo hiện tại,
    Assistant phải có khả năng trả nhiều nguồn
    khi retrieval lấy được nhiều chunk.
    """

    response = ask(
        QUESTION
    )

    assert response.status_code == 200

    citations = response.json()["citations"]

    assert len(citations) >= 1

    if len(citations) >= 2:
        assert (
            citations[0]["citation_id"]
            != citations[1]["citation_id"]
        )


# =========================================================
# 25. ASSISTANT RESPONSE CONSISTENCY
# =========================================================

def test_assistant_response_consistency():
    """
    Hai request cùng một câu hỏi phải giữ nguyên
    contract response.

    Nội dung answer có thể phụ thuộc Generation Provider,
    nhưng cấu trúc response phải ổn định.
    """

    response_1 = ask(
        QUESTION
    )

    response_2 = ask(
        QUESTION
    )

    assert response_1.status_code == 200

    assert response_2.status_code == 200

    data_1 = response_1.json()

    data_2 = response_2.json()

    assert data_1["success"] is True

    assert data_2["success"] is True

    assert data_1["question"] == data_2["question"]

    assert isinstance(
        data_1["answer"],
        str,
    )

    assert isinstance(
        data_2["answer"],
        str,
    )

    assert isinstance(
        data_1["citations"],
        list,
    )

    assert isinstance(
        data_2["citations"],
        list,
    )

    assert len(
        data_1["citations"]
    ) >= 1

    assert len(
        data_2["citations"]
    ) >= 1