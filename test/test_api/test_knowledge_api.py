from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_knowledge_search_endpoint_exists():
    response = client.post(
        "/knowledge/search",
        json={
            "query": "chuyển đổi số",
            "query_vector": [
                1.0,
                0.0,
                0.0,
            ],
            "top_k": 5,
            "score_threshold": 0.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["query"] == "chuyển đổi số"
    assert data["total"] == 0
    assert data["results"] == []


def test_knowledge_search_validation():
    response = client.post(
        "/knowledge/search",
        json={
            "query": "",
            "query_vector": [],
        },
    )

    assert response.status_code == 422