"""
14.6 - E2E OCR Complete Journey.

Mục tiêu:
    Kiểm tra toàn bộ hành trình OCR từ Upload
    đến OCR, AI, RAG và Citation.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


# =========================================================
# TEST CONFIGURATION
# =========================================================

client = TestClient(app)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_IMAGE = PROJECT_ROOT / "ocr_runtime_test.png"

RAG_INSTRUCTION = (
    "Hãy xác định nội dung văn bản OCR có liên quan gì "
    "đến chuyển đổi số và trả lời dựa trên các căn cứ "
    "trong Knowledge Base."
)


# =========================================================
# 1. TEST FILE EXISTS
# =========================================================

def test_e2e_ocr_test_file_exists():
    """
    File ảnh dùng cho E2E phải tồn tại.
    """

    assert TEST_IMAGE.exists(), (
        f"Không tìm thấy file test OCR: {TEST_IMAGE}"
    )


# =========================================================
# 2. OCR UPLOAD
# =========================================================

def test_e2e_ocr_upload():
    """
    Bước 2:
    Upload file và thực hiện OCR.
    """

    assert TEST_IMAGE.exists()

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
    assert data["content_type"] == "image/png"
    assert data["file_size"] > 0

    assert isinstance(
        data["text"],
        str,
    )

    assert data["text"].strip()

    assert isinstance(
        data["pages"],
        list,
    )


# =========================================================
# 3. OCR GENERATES TEXT
# =========================================================

def test_e2e_ocr_generates_text():
    """
    Bước 3:
    OCR phải thực sự sinh ra nội dung văn bản.
    """

    assert TEST_IMAGE.exists()

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

    ocr_text = data["text"]

    assert isinstance(
        ocr_text,
        str,
    )

    assert len(ocr_text.strip()) > 0


# =========================================================
# 4. OCR + AI
# =========================================================

def test_e2e_ocr_ai():
    """
    Bước 4:
    OCR phải truyền nội dung sang AI
    và nhận được câu trả lời.
    """

    assert TEST_IMAGE.exists()

    instruction = (
        "Hãy tóm tắt nội dung văn bản OCR."
    )

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
                "instruction": instruction,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["ocr_text"].strip()

    assert data["instruction"] == instruction

    assert isinstance(
        data["answer"],
        str,
    )

    assert data["answer"].strip()

    assert data["metadata"]["pipeline_stage"] == (
        "ocr_ai"
    )


# =========================================================
# 5. OCR + RAG
# =========================================================

def test_e2e_ocr_rag():
    """
    Bước 5:
    OCR phải kết nối được với RAG và Knowledge Base.
    """

    assert TEST_IMAGE.exists()

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
                "instruction": RAG_INSTRUCTION,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["ocr_text"].strip()

    assert data["instruction"] == RAG_INSTRUCTION

    assert data["answer"].strip()

    assert isinstance(
        data["sources"],
        list,
    )

    assert data["sources"]


# =========================================================
# 6. RAG RETRIEVES KNOWLEDGE
# =========================================================

def test_e2e_ocr_rag_retrieves_knowledge():
    """
    Bước 6:
    RAG phải thực sự truy xuất được Knowledge Base.
    """

    assert TEST_IMAGE.exists()

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
                "instruction": RAG_INSTRUCTION,
            },
        )

    assert response.status_code == 200

    data = response.json()

    metadata = data["metadata"]

    assert metadata["pipeline_stage"] == (
        "ocr_rag"
    )

    assert metadata["retrieved_count"] >= 1

    assert metadata["context_count"] >= 1

    assert metadata["source_count"] >= 1


# =========================================================
# 7. CITATION IS GENERATED
# =========================================================

def test_e2e_ocr_rag_citation():
    """
    Bước 7:
    RAG phải tạo citation từ Knowledge Base.
    """

    assert TEST_IMAGE.exists()

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
                "instruction": RAG_INSTRUCTION,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["sources"]

    assert data["metadata"]["citation_count"] >= 1

    assert data["metadata"]["source_count"] == len(
        data["sources"]
    )


# =========================================================
# 8. SOURCE CONTENT IS PRESERVED
# =========================================================

def test_e2e_ocr_rag_source_content():
    """
    Bước 8:
    Nội dung nguồn phải được giữ nguyên trong citation.
    """

    assert TEST_IMAGE.exists()

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
                "instruction": RAG_INSTRUCTION,
            },
        )

    assert response.status_code == 200

    data = response.json()

    sources = data["sources"]

    assert sources

    for source in sources:
        assert source["source"]
        assert source["document_id"]
        assert source["content"]


# =========================================================
# 9. COMPLETE OCR E2E CONTRACT
# =========================================================

def test_e2e_ocr_complete_response_contract():
    """
    Bước 9:
    Response cuối phải đáp ứng đầy đủ contract.
    """

    assert TEST_IMAGE.exists()

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
                "instruction": RAG_INSTRUCTION,
            },
        )

    assert response.status_code == 200

    data = response.json()

    required_fields = {
        "success",
        "filename",
        "content_type",
        "file_size",
        "ocr_text",
        "instruction",
        "answer",
        "sources",
        "metadata",
    }

    assert required_fields.issubset(
        data.keys()
    )

    assert isinstance(
        data["success"],
        bool,
    )

    assert isinstance(
        data["ocr_text"],
        str,
    )

    assert isinstance(
        data["instruction"],
        str,
    )

    assert isinstance(
        data["answer"],
        str,
    )

    assert isinstance(
        data["sources"],
        list,
    )

    assert isinstance(
        data["metadata"],
        dict,
    )


# =========================================================
# 10. INVALID FILE IS REJECTED
# =========================================================

def test_e2e_ocr_invalid_file():
    """
    Bước 10:
    File không được hỗ trợ phải bị từ chối.
    """

    response = client.post(
        "/ocr/upload",
        files={
            "file": (
                "invalid.txt",
                b"invalid content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 415


# =========================================================
# 11. INVALID RAG INSTRUCTION
# =========================================================

def test_e2e_ocr_invalid_rag_instruction():
    """
    Bước 11:
    Instruction rỗng phải bị từ chối.
    """

    assert TEST_IMAGE.exists()

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
                "instruction": "   ",
            },
        )

    assert response.status_code == 400


# =========================================================
# 12. E2E PIPELINE CAN REPEAT
# =========================================================

def test_e2e_ocr_pipeline_can_repeat():
    """
    Bước 12:
    Toàn bộ OCR + RAG pipeline phải chạy được
    nhiều lần trong cùng runtime.
    """

    for _ in range(2):
        assert TEST_IMAGE.exists()

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
                    "instruction": RAG_INSTRUCTION,
                },
            )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is True
        assert data["ocr_text"].strip()
        assert data["answer"].strip()
        assert data["sources"]
        assert data["metadata"]["retrieved_count"] >= 1