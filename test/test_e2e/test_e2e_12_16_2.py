"""
12.16.2 - E2E Knowledge Flow.

Mục tiêu:
    Kiểm tra toàn bộ luồng Knowledge từ HTTP API
    tới Retrieval và trả kết quả về client.

Pipeline:

    HTTP Request
        ↓
    Knowledge API
        ↓
    Query Vector
        ↓
    Retriever
        ↓
    Relevant Chunks
        ↓
    Knowledge Response

Phạm vi:
    - Knowledge API
    - Query validation
    - Retrieval
    - Top-K
    - Score threshold
    - Source metadata
    - Relevant content

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

KNOWLEDGE_ENDPOINT = "/knowledge/search"

QUERY = "Chuyển đổi số"

QUERY_VECTOR = [
    1.0,
    0.0,
    0.0,
]


# =========================================================
# HELPER
# =========================================================

def search_knowledge(
    query: str = QUERY,
    query_vector: list[float] | None = None,
    top_k: int = 5,
    score_threshold: float = 0.0,
):
    """
    Gửi request tới Knowledge API.
    """

    if query_vector is None:
        query_vector = QUERY_VECTOR

    return client.post(
        KNOWLEDGE_ENDPOINT,
        json={
            "query": query,
            "query_vector": query_vector,
            "top_k": top_k,
            "score_threshold": score_threshold,
        },
    )


# =========================================================
# 1. KNOWLEDGE ENDPOINT
# =========================================================

def test_e2e_knowledge_endpoint():
    """
    Knowledge endpoint phải tồn tại
    và xử lý request hợp lệ.
    """

    response = search_knowledge()

    assert response.status_code == 200


# =========================================================
# 2. RESPONSE SUCCESS
# =========================================================

def test_e2e_knowledge_response_success():
    """
    Knowledge API phải trả success=True.
    """

    response = search_knowledge()

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True


# =========================================================
# 3. QUERY IS PRESERVED
# =========================================================

def test_e2e_knowledge_query_is_preserved():
    """
    Query gửi lên phải được giữ trong response.
    """

    query = "Chuyển đổi số"

    response = search_knowledge(
        query=query
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == query


# =========================================================
# 4. RESULTS ARE RETURNED
# =========================================================

def test_e2e_knowledge_returns_results():
    """
    Knowledge Base phải trả được kết quả.
    """

    response = search_knowledge()

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data["results"],
        list,
    )

    assert len(
        data["results"]
    ) >= 1


# =========================================================
# 5. TOTAL MATCHES RESULTS
# =========================================================

def test_e2e_knowledge_total_matches_results():
    """
    total phải phản ánh số kết quả thực tế.
    """

    response = search_knowledge()

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == len(
        data["results"]
    )


# =========================================================
# 6. RESULT CONTENT
# =========================================================

def test_e2e_knowledge_result_contains_content():
    """
    Mỗi result phải có nội dung chunk.
    """

    response = search_knowledge()

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    for item in results:
        assert item["content"]

        assert isinstance(
            item["content"],
            str,
        )


# =========================================================
# 7. RESULT VECTOR ID
# =========================================================

def test_e2e_knowledge_result_contains_vector_id():
    """
    Mỗi result phải giữ vector_id.
    """

    response = search_knowledge()

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    for item in results:
        assert item["vector_id"]


# =========================================================
# 8. RESULT SCORE
# =========================================================

def test_e2e_knowledge_result_contains_score():
    """
    Mỗi result phải có similarity score.
    """

    response = search_knowledge()

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    for item in results:
        assert item["score"] is not None

        assert isinstance(
            item["score"],
            (int, float),
        )


# =========================================================
# 9. DOCUMENT METADATA
# =========================================================

def test_e2e_knowledge_document_metadata():
    """
    Retrieval phải giữ metadata tài liệu.
    """

    response = search_knowledge()

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    for item in results:
        assert item["document_id"]

        assert item["page_number"] is not None

        assert item["chunk_index"] is not None


# =========================================================
# 10. SOURCE METADATA
# =========================================================

def test_e2e_knowledge_source_metadata():
    """
    Metadata phải chứa source.
    """

    response = search_knowledge()

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    for item in results:
        metadata = item["metadata"]

        assert isinstance(
            metadata,
            dict,
        )

        assert (
            metadata.get("source")
            or item["document_id"]
        )


# =========================================================
# 11. TOP K = 1
# =========================================================

def test_e2e_knowledge_top_k_one():
    """
    top_k=1 phải giới hạn tối đa một kết quả.
    """

    response = search_knowledge(
        top_k=1
    )

    assert response.status_code == 200

    data = response.json()

    assert len(
        data["results"]
    ) <= 1


# =========================================================
# 12. TOP K = 2
# =========================================================

def test_e2e_knowledge_top_k_two():
    """
    top_k=2 phải giới hạn tối đa hai kết quả.
    """

    response = search_knowledge(
        top_k=2
    )

    assert response.status_code == 200

    data = response.json()

    assert len(
        data["results"]
    ) <= 2


# =========================================================
# 13. SCORE THRESHOLD
# =========================================================

def test_e2e_knowledge_score_threshold():
    """
    Score threshold phải được áp dụng.
    """

    response = search_knowledge(
        score_threshold=0.9
    )

    assert response.status_code == 200

    data = response.json()

    for item in data["results"]:
        assert (
            item["score"] >= 0.9
        )


# =========================================================
# 14. RELEVANT CONTENT
# =========================================================

def test_e2e_knowledge_relevant_content():
    """
    Query chuyển đổi số phải lấy được
    nội dung liên quan.
    """

    response = search_knowledge(
        query="Chuyển đổi số"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["results"]

    contents = " ".join(
        item["content"]
        for item in data["results"]
    ).lower()

    assert "chuyển đổi số" in contents


# =========================================================
# 15. SECOND KNOWLEDGE QUERY
# =========================================================

def test_e2e_knowledge_second_query():
    """
    Knowledge API phải xử lý được một query khác.
    """

    response = search_knowledge(
        query=(
            "Triển khai chuyển đổi số"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["results"]


# =========================================================
# 16. INVALID REQUEST
# =========================================================

def test_e2e_knowledge_invalid_request():
    """
    Request thiếu trường bắt buộc
    phải bị validation.
    """

    response = client.post(
        KNOWLEDGE_ENDPOINT,
        json={},
    )

    assert response.status_code == 422


# =========================================================
# 17. EMPTY QUERY
# =========================================================

def test_e2e_knowledge_empty_query():
    """
    Query rỗng phải bị từ chối.
    """

    response = search_knowledge(
        query=""
    )

    assert response.status_code in (
        400,
        422,
    )


# =========================================================
# 18. EMPTY QUERY VECTOR
# =========================================================

def test_e2e_knowledge_empty_query_vector():
    """
    Query vector rỗng phải bị từ chối
    hoặc không tạo được kết quả hợp lệ.
    """

    response = search_knowledge(
        query_vector=[]
    )

    assert response.status_code in (
        400,
        422,
        500,
    )


# =========================================================
# 19. KNOWLEDGE RESPONSE CONTRACT
# =========================================================

def test_e2e_knowledge_response_contract():
    """
    Kiểm tra API contract cuối của Knowledge.
    """

    response = search_knowledge()

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

    assert isinstance(
        data["success"],
        bool,
    )

    assert isinstance(
        data["query"],
        str,
    )

    assert isinstance(
        data["total"],
        int,
    )

    assert isinstance(
        data["results"],
        list,
    )

    assert isinstance(
        data["message"],
        str,
    )


# =========================================================
# 20. KNOWLEDGE FLOW GATE
# =========================================================

def test_e2e_knowledge_flow_gate():
    """
    E2E Knowledge Flow Gate.

    Xác nhận toàn bộ luồng:

        HTTP
          ↓
        Knowledge API
          ↓
        Retrieval
          ↓
        Relevant Chunks
          ↓
        Metadata
          ↓
        Response
    """

    response = search_knowledge(
        query=QUERY,
        top_k=5,
        score_threshold=0.0,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["query"] == QUERY

    assert data["results"]

    assert data["total"] >= 1

    for item in data["results"]:
        assert item["vector_id"]

        assert item["content"]

        assert item["score"] is not None

        assert item["document_id"]

        assert item["page_number"] is not None

        assert item["chunk_index"] is not None

        assert isinstance(
            item["metadata"],
            dict,
        )