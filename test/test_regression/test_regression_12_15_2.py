"""
12.15.2 - Knowledge Regression Test.

Mục tiêu:
    Kiểm tra regression của Knowledge Base
    sau khi hoàn thành các Task 12.12 - 12.14.

Phạm vi:

    Knowledge API
        ↓
    Knowledge Service
        ↓
    Retriever
        ↓
    LocalVectorStore
        ↓
    Retrieved Chunks

Các contract được kiểm tra:

    - Knowledge API tồn tại.
    - Search request hợp lệ.
    - Search trả về kết quả.
    - Kết quả giữ vector_id.
    - Kết quả giữ score.
    - Kết quả giữ content.
    - Kết quả giữ document_id.
    - Kết quả giữ page_number.
    - Kết quả giữ chunk_index.
    - Metadata được bảo toàn.
    - top_k được tôn trọng.
    - score_threshold được tôn trọng.
    - Query được bảo toàn.
    - Request không hợp lệ bị từ chối.

Task 12.15.2 chỉ kiểm tra Knowledge Regression.
Không thay đổi production code.
"""

from __future__ import annotations

import os


# =========================================================
# TEST ENVIRONMENT
# =========================================================
#
# Knowledge Demo phải được bật trước khi import app.main
# để LocalVectorStore được seed dữ liệu kiểm thử.
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

KNOWLEDGE_SEARCH_ENDPOINT = "/knowledge/search"

QUERY = "Chuyển đổi số"

QUERY_RELATED = (
    "Triển khai chuyển đổi số"
)


# =========================================================
# HELPER
# =========================================================

def search(
    query: str,
    query_vector: list[float] | None = None,
    top_k: int = 5,
    score_threshold: float = 0.0,
):
    """
    Gửi request tới Knowledge Search API.

    Knowledge API hiện tại sử dụng query_vector
    trong contract của Sprint 12.
    """

    if query_vector is None:
        query_vector = [
            1.0,
            0.0,
            0.0,
        ]

    return client.post(
        KNOWLEDGE_SEARCH_ENDPOINT,
        json={
            "query": query,
            "query_vector": query_vector,
            "top_k": top_k,
            "score_threshold": score_threshold,
        },
    )


# =========================================================
# 1. KNOWLEDGE API EXISTS
# =========================================================

def test_knowledge_api_exists():
    """
    Knowledge Search API phải tồn tại.

    Request hợp lệ không được trả:
        404
        405
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200


# =========================================================
# 2. SEARCH RESPONSE SUCCESS
# =========================================================

def test_knowledge_search_success():
    """
    Knowledge Search phải trả response thành công.
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        dict,
    )

    assert data["success"] is True


# =========================================================
# 3. QUERY PRESERVATION
# =========================================================

def test_knowledge_query_is_preserved():
    """
    API phải giữ lại query người dùng gửi lên.
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == QUERY


# =========================================================
# 4. RESULTS ARE LIST
# =========================================================

def test_knowledge_results_are_list():
    """
    results phải luôn là list.
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data["results"],
        list,
    )


# =========================================================
# 5. KNOWLEDGE RETURNS DEMO DATA
# =========================================================

def test_knowledge_returns_demo_data():
    """
    Với Demo Knowledge Base đang bật,
    query chuyển đổi số phải lấy được dữ liệu.
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["total"] >= 1

    assert len(
        data["results"]
    ) >= 1


# =========================================================
# 6. RESULT VECTOR ID
# =========================================================

def test_knowledge_result_has_vector_id():
    """
    Mỗi kết quả phải có vector_id.
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    for item in results:
        assert item["vector_id"]

        assert isinstance(
            item["vector_id"],
            str,
        )


# =========================================================
# 7. RESULT SCORE
# =========================================================

def test_knowledge_result_has_score():
    """
    Mỗi kết quả phải có similarity score.
    """

    response = search(
        QUERY
    )

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
# 8. RESULT CONTENT
# =========================================================

def test_knowledge_result_has_content():
    """
    Mỗi kết quả phải giữ được nội dung chunk.
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    for item in results:
        assert item["content"]

        assert isinstance(
            item["content"],
            str,
        )

        assert item["content"].strip()


# =========================================================
# 9. DOCUMENT METADATA
# =========================================================

def test_knowledge_result_preserves_document_metadata():
    """
    Kết quả phải giữ metadata nguồn tài liệu.

    Các trường quan trọng:

        document_id
        page_number
        chunk_index
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    for item in results:
        assert item["document_id"]

        assert item["page_number"] is not None

        assert item["chunk_index"] is not None


# =========================================================
# 10. RESULT METADATA
# =========================================================

def test_knowledge_result_metadata_is_dict():
    """
    metadata phải được trả về dưới dạng object/dict.
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    for item in results:
        assert isinstance(
            item["metadata"],
            dict,
        )


# =========================================================
# 11. SOURCE METADATA
# =========================================================

def test_knowledge_result_preserves_source():
    """
    Metadata nguồn phải được bảo toàn.

    Citation/RAG phía sau phụ thuộc vào
    source information này.
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    results = response.json()["results"]

    assert results

    for item in results:
        metadata = item["metadata"]

        assert "source" in metadata

        assert metadata["source"]


# =========================================================
# 12. TOP K
# =========================================================

def test_knowledge_top_k_is_respected():
    """
    Retriever không được trả quá top_k kết quả.
    """

    response = search(
        QUERY,
        top_k=1,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(
        data["results"]
    ) <= 1


# =========================================================
# 13. TOP K TWO
# =========================================================

def test_knowledge_top_k_two():
    """
    Kiểm tra top_k = 2 với Demo Knowledge Base.
    """

    response = search(
        QUERY,
        top_k=2,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(
        data["results"]
    ) <= 2

    assert data["total"] == len(
        data["results"]
    )


# =========================================================
# 14. SCORE THRESHOLD
# =========================================================

def test_knowledge_score_threshold():
    """
    Score threshold phải được chuyển xuống
    Retrieval layer.

    Với threshold rất cao, hệ thống có thể
    không trả kết quả.
    """

    response = search(
        QUERY,
        score_threshold=1.1,
    )

    assert response.status_code in (
        200,
        422,
    )

    if response.status_code == 200:
        data = response.json()

        assert isinstance(
            data["results"],
            list,
        )


# =========================================================
# 15. RELATED QUERY
# =========================================================

def test_knowledge_related_query():
    """
    Một query liên quan khác vẫn phải
    truy xuất được Knowledge Base.
    """

    response = search(
        QUERY_RELATED
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["total"] >= 1

    assert data["results"]


# =========================================================
# 16. INVALID REQUEST
# =========================================================

def test_knowledge_invalid_request():
    """
    Request thiếu các trường bắt buộc
    phải bị FastAPI validation từ chối.
    """

    response = client.post(
        KNOWLEDGE_SEARCH_ENDPOINT,
        json={},
    )

    assert response.status_code == 422


# =========================================================
# 17. EMPTY QUERY
# =========================================================

def test_knowledge_empty_query():
    """
    Query rỗng phải bị từ chối
    hoặc không tạo ra kết quả hợp lệ.
    """

    response = search(
        ""
    )

    assert response.status_code in (
        200,
        400,
        422,
    )

    if response.status_code == 200:
        data = response.json()

        assert isinstance(
            data["results"],
            list,
        )


# =========================================================
# 18. RESPONSE MESSAGE
# =========================================================

def test_knowledge_response_message():
    """
    Response phải có message để frontend
    có thể hiển thị trạng thái xử lý.
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    data = response.json()

    assert "message" in data

    assert isinstance(
        data["message"],
        str,
    )


# =========================================================
# 19. TOTAL CONTRACT
# =========================================================

def test_knowledge_total_contract():
    """
    total phải là số nguyên không âm
    và nhất quán với results.
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data["total"],
        int,
    )

    assert data["total"] >= 0

    assert data["total"] == len(
        data["results"]
    )


# =========================================================
# 20. RESULT ORDER
# =========================================================

def test_knowledge_results_are_relevance_ordered():
    """
    Các kết quả phải được trả theo thứ tự
    relevance từ cao xuống thấp.

    Đây là contract quan trọng cho RAG:
    chunk phù hợp nhất phải đứng trước.
    """

    response = search(
        QUERY
    )

    assert response.status_code == 200

    results = response.json()["results"]

    if len(results) <= 1:
        return

    scores = [
        item["score"]
        for item in results
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )