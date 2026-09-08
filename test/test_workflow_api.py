"""
Sprint 16.3 - Workflow API Tests.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.workflow import (
    get_workflow_service,
)


@pytest.fixture(autouse=True)
def reset_workflow_service():
    """
    Reset in-memory Workflow trước mỗi test.
    """

    service = get_workflow_service()
    service.clear()

    yield

    service.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def create_workflow(
    client: TestClient,
) -> str:
    response = client.post(
        "/workflow",
        json={
            "title": "Công văn chuyển đổi số",
            "document_type": "cong_van",
            "created_by": "user-001",
            "metadata": {
                "priority": "high",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["success"] is True
    assert data["stage"] == "received"

    return data["workflow_id"]


def test_create_workflow(
    client: TestClient,
) -> None:
    workflow_id = create_workflow(
        client
    )

    assert workflow_id


def test_get_workflow(
    client: TestClient,
) -> None:
    workflow_id = create_workflow(
        client
    )

    response = client.get(
        f"/workflow/{workflow_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["workflow_id"] == workflow_id
    assert data["title"] == (
        "Công văn chuyển đổi số"
    )
    assert data["stage"] == "received"
    assert data["event_count"] == 0


def test_list_workflow(
    client: TestClient,
) -> None:
    create_workflow(client)
    create_workflow(client)

    response = client.get(
        "/workflow"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_transition_workflow(
    client: TestClient,
) -> None:
    workflow_id = create_workflow(
        client
    )

    response = client.post(
        f"/workflow/{workflow_id}/transition",
        json={
            "target": "ai_processing",
            "actor": "system",
            "note": "AI bắt đầu xử lý.",
            "metadata": {
                "engine": "assistant",
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert (
        data["workflow"]["stage"]
        == "ai_processing"
    )

    assert (
        data["event"]["from_stage"]
        == "received"
    )

    assert (
        data["event"]["to_stage"]
        == "ai_processing"
    )

    assert (
        data["event"]["actor"]
        == "system"
    )


def test_full_workflow_api(
    client: TestClient,
) -> None:
    workflow_id = create_workflow(
        client
    )

    stages = [
        (
            "ai_processing",
            "system",
        ),
        (
            "drafting",
            "ai",
        ),
        (
            "pending_approval",
            "officer",
        ),
        (
            "approved",
            "manager",
        ),
        (
            "pending_signature",
            "officer",
        ),
        (
            "signed",
            "leader",
        ),
        (
            "exported",
            "system",
        ),
    ]

    for target, actor in stages:
        response = client.post(
            f"/workflow/{workflow_id}/transition",
            json={
                "target": target,
                "actor": actor,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["workflow"]["stage"]
            == target
        )

    final_response = client.get(
        f"/workflow/{workflow_id}"
    )

    assert (
        final_response.status_code
        == 200
    )

    final_data = final_response.json()

    assert (
        final_data["stage"]
        == "exported"
    )

    assert (
        final_data["is_completed"]
        is True
    )

    assert (
        final_data["event_count"]
        == 7
    )


def test_history_api(
    client: TestClient,
) -> None:
    workflow_id = create_workflow(
        client
    )

    client.post(
        f"/workflow/{workflow_id}/transition",
        json={
            "target": "ai_processing",
            "actor": "system",
        },
    )

    client.post(
        f"/workflow/{workflow_id}/transition",
        json={
            "target": "drafting",
            "actor": "ai",
        },
    )

    response = client.get(
        f"/workflow/{workflow_id}/history"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["workflow_id"] == workflow_id
    assert data["stage"] == "drafting"
    assert data["total"] == 2
    assert len(data["events"]) == 2

    assert (
        data["events"][0]["to_stage"]
        == "ai_processing"
    )

    assert (
        data["events"][1]["to_stage"]
        == "drafting"
    )


def test_invalid_transition_returns_409(
    client: TestClient,
) -> None:
    workflow_id = create_workflow(
        client
    )

    response = client.post(
        f"/workflow/{workflow_id}/transition",
        json={
            "target": "approved",
            "actor": "manager",
        },
    )

    assert response.status_code == 409


def test_missing_workflow_returns_404(
    client: TestClient,
) -> None:
    response = client.get(
        "/workflow/not-found"
    )

    assert response.status_code == 404

    response = client.get(
        "/workflow/not-found/history"
    )

    assert response.status_code == 404

    response = client.delete(
        "/workflow/not-found"
    )

    assert response.status_code == 404


def test_delete_workflow(
    client: TestClient,
) -> None:
    workflow_id = create_workflow(
        client
    )

    response = client.delete(
        f"/workflow/{workflow_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert (
        data["workflow_id"]
        == workflow_id
    )

    response = client.get(
        f"/workflow/{workflow_id}"
    )

    assert response.status_code == 404


def test_filter_by_stage(
    client: TestClient,
) -> None:
    workflow_id_1 = create_workflow(
        client
    )

    workflow_id_2 = create_workflow(
        client
    )

    client.post(
        f"/workflow/{workflow_id_1}/transition",
        json={
            "target": "ai_processing",
            "actor": "system",
        },
    )

    response = client.get(
        "/workflow?stage=ai_processing"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert (
        data["items"][0]["workflow_id"]
        == workflow_id_1
    )

    response = client.get(
        "/workflow?stage=received"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert (
        data["items"][0]["workflow_id"]
        == workflow_id_2
    )