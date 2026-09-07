from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_IMAGE = PROJECT_ROOT / "ocr_runtime_test.png"


def test_ocr_e2e_upload() -> None:
    assert TEST_IMAGE.exists(), f"Không tìm thấy file test: {TEST_IMAGE}"

    with TEST_IMAGE.open("rb") as file:
        response = client.post(
            "/ocr/upload",
            files={
                "file": (
                    TEST_IMAGE.name,
                    file,
                    "image/png",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["filename"] == TEST_IMAGE.name
    assert isinstance(data["ocr_text"], str)
    assert data["ocr_text"].strip()
    assert isinstance(data["pages"], list)


def test_ocr_e2e_ai() -> None:
    assert TEST_IMAGE.exists(), f"Không tìm thấy file test: {TEST_IMAGE}"

    with TEST_IMAGE.open("rb") as file:
        response = client.post(
            "/ocr/ai",
            files={
                "file": (
                    TEST_IMAGE.name,
                    file,
                    "image/png",
                )
            },
            data={
                "instruction": "Hãy tóm tắt nội dung văn bản OCR."
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["ocr_text"].strip()
    assert data["instruction"] == "Hãy tóm tắt nội dung văn bản OCR."
    assert isinstance(data["answer"], str)
    assert data["answer"].strip()


def test_ocr_e2e_rag() -> None:
    assert TEST_IMAGE.exists(), f"Không tìm thấy file test: {TEST_IMAGE}"

    with TEST_IMAGE.open("rb") as file:
        response = client.post(
            "/ocr/rag",
            files={
                "file": (
                    TEST_IMAGE.name,
                    file,
                    "image/png",
                )
            },
            data={
                "instruction": (
                    "Hãy xác định nội dung văn bản OCR có liên quan gì "
                    "đến chuyển đổi số và trả lời dựa trên các căn cứ "
                    "trong Knowledge Base."
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["ocr_text"].strip()
    assert data["answer"].strip()

    assert isinstance(data["sources"], list)
    assert len(data["sources"]) >= 1

    assert data["metadata"]["pipeline_stage"] == "ocr_rag"
    assert data["metadata"]["retrieved_count"] >= 1
    assert data["metadata"]["context_count"] >= 1
    assert data["metadata"]["citation_count"] >= 1
    assert data["metadata"]["source_count"] >= 1


def test_ocr_e2e_invalid_extension() -> None:
    response = client.post(
        "/ocr/upload",
        files={
            "file": (
                "test.txt",
                b"test",
                "text/plain",
            )
        },
    )

    assert response.status_code == 415


def test_ocr_e2e_empty_instruction() -> None:
    assert TEST_IMAGE.exists(), f"Không tìm thấy file test: {TEST_IMAGE}"

    with TEST_IMAGE.open("rb") as file:
        response = client.post(
            "/ocr/rag",
            files={
                "file": (
                    TEST_IMAGE.name,
                    file,
                    "image/png",
                )
            },
            data={
                "instruction": "   "
            },
        )

    assert response.status_code == 400