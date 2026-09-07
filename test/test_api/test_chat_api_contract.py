"""
Sprint 13.2.1 - Chat API Contract

Kiểm tra HTTP contract của Assistant / Chat API.

Endpoint hiện tại:

    POST /assistant/ask

Phạm vi:

- API route tồn tại
- Request validation
- AssistantService.answer() integration
- Response contract
- Metadata
- Citations
- Service unavailable
- Không gọi Ollama / RAG thật
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app.api.routes.assistant as assistant_route
from app.main import app


# ============================================================
# TEST CLIENT
# ============================================================

client = TestClient(app)


# ============================================================
# FAKE ASSISTANT SERVICE
# ============================================================


class FakeAssistantService:
    """
    Fake AssistantService.

    Quan trọng:
    AssistantService thật sử dụng public method:

        answer(question)

    Không phải:

        ask(question)
    """

    def __init__(
        self,
        *,
        answer: str = (
            "Chuyển đổi số là quá trình ứng dụng "
            "công nghệ số vào quản lý và cung cấp "
            "dịch vụ công."
        ),
        citations=None,
        metadata=None,
    ):
        self.answer_text = answer
        self.citations = (
            list(citations)
            if citations is not None
            else []
        )
        self.metadata = (
            dict(metadata)
            if metadata is not None
            else {}
        )

        self.last_question = None

    def answer(
        self,
        question: str,
    ):
        """
        Khớp chính xác với AssistantService.answer().
        """

        self.last_question = question

        return SimpleNamespace(
            answer=self.answer_text,
            query=question,
            citations=self.citations,
            metadata=dict(self.metadata),
        )


# ============================================================
# FIXTURE
# ============================================================


@pytest.fixture
def fake_service():
    """
    Inject FakeAssistantService vào API runtime.
    """

    original = assistant_route._assistant_service

    service = FakeAssistantService()

    assistant_route.configure_assistant_service(
        service
    )

    yield service

    # Khôi phục runtime ban đầu.
    assistant_route._assistant_service = original


# ============================================================
# 13.2.1.1
# API ROUTE IS REACHABLE
# ============================================================


def test_chat_api_route_is_reachable(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={
            "question": "Chuyển đổi số là gì?"
        },
    )

    assert response.status_code == 200


# ============================================================
# 13.2.1.2
# VALID REQUEST
# ============================================================


def test_chat_api_accepts_valid_request(
    fake_service,
):
    question = "Chuyển đổi số ở cấp xã là gì?"

    response = client.post(
        "/assistant/ask",
        json={
            "question": question
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True

    assert body["question"] == question

    assert isinstance(
        body["answer"],
        str,
    )

    assert body["answer"]

    assert (
        fake_service.last_question
        == question
    )


# ============================================================
# 13.2.1.3
# RESPONSE CONTRACT
# ============================================================


def test_chat_api_response_contract(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={
            "question": "Hãy giải thích RAG."
        },
    )

    assert response.status_code == 200

    body = response.json()

    required_fields = {
        "success",
        "question",
        "answer",
        "citations",
        "metadata",
        "message",
    }

    assert required_fields.issubset(
        body.keys()
    )

    assert isinstance(
        body["success"],
        bool,
    )

    assert isinstance(
        body["question"],
        str,
    )

    assert isinstance(
        body["answer"],
        str,
    )

    assert isinstance(
        body["citations"],
        list,
    )

    assert isinstance(
        body["metadata"],
        dict,
    )

    assert isinstance(
        body["message"],
        str,
    )


# ============================================================
# 13.2.1.4
# EMPTY QUESTION
# ============================================================


def test_chat_api_rejects_empty_question(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={
            "question": ""
        },
    )

    assert response.status_code == 422


# ============================================================
# 13.2.1.5
# WHITESPACE QUESTION
# ============================================================


def test_chat_api_rejects_whitespace_question(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={
            "question": "   "
        },
    )

    assert response.status_code == 400


# ============================================================
# 13.2.1.6
# MISSING QUESTION
# ============================================================


def test_chat_api_rejects_missing_question(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={},
    )

    assert response.status_code == 422


# ============================================================
# 13.2.1.7
# INVALID QUESTION TYPE
# ============================================================


def test_chat_api_rejects_invalid_question_type(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={
            "question": 12345
        },
    )

    assert response.status_code == 422


# ============================================================
# 13.2.1.8
# QUESTION IS NORMALIZED
# ============================================================


def test_chat_api_normalizes_question(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={
            "question": (
                "   Chuyển đổi số là gì?   "
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["question"]
        == "Chuyển đổi số là gì?"
    )

    assert (
        fake_service.last_question
        == "Chuyển đổi số là gì?"
    )


# ============================================================
# 13.2.1.9
# METADATA CONTRACT
# ============================================================


def test_chat_api_metadata_contract(
    fake_service,
):
    fake_service.metadata = {
        "provider": "ollama",
        "model": "qwen3:8b",
        "retrieval_count": 2,
    }

    response = client.post(
        "/assistant/ask",
        json={
            "question": "RAG là gì?"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(
        body["metadata"],
        dict,
    )

    assert (
        body["metadata"]["provider"]
        == "ollama"
    )

    assert (
        body["metadata"]["model"]
        == "qwen3:8b"
    )

    assert (
        body["metadata"]["retrieval_count"]
        == 2
    )

    assert (
        body["metadata"]["citation_count"]
        == 0
    )


# ============================================================
# 13.2.1.10
# SERVICE RESPONSE IS MAPPED
# ============================================================


def test_chat_api_maps_service_response(
    fake_service,
):
    expected_answer = (
        "Đây là câu trả lời từ AssistantService."
    )

    fake_service.answer_text = (
        expected_answer
    )

    response = client.post(
        "/assistant/ask",
        json={
            "question": "Hỏi thử."
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["answer"]
        == expected_answer
    )

    assert (
        body["question"]
        == "Hỏi thử."
    )


# ============================================================
# 13.2.1.11
# CITATION LIST IS RETURNED
# ============================================================


def test_chat_api_returns_citations(
    fake_service,
):
    citation = SimpleNamespace(
        citation_id="cit-001",
        source="Nghị quyết 57-NQ/TW",
        score=0.95,
        document_id="doc-001",
        page_number=3,
        chunk_index=1,
        content=(
            "Chuyển đổi số là nhiệm vụ quan trọng."
        ),
        metadata={
            "document_name": (
                "Nghị quyết 57-NQ/TW"
            )
        },
        label=(
            "Nghị quyết 57-NQ/TW — trang 3"
        ),
    )

    fake_service.citations = [citation]

    response = client.post(
        "/assistant/ask",
        json={
            "question": "Nghị quyết 57 nói gì?"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["citations"]) == 1

    returned = body["citations"][0]

    assert (
        returned["citation_id"]
        == "cit-001"
    )

    assert (
        returned["source"]
        == "Nghị quyết 57-NQ/TW"
    )

    assert returned["score"] == 0.95

    assert (
        returned["document_id"]
        == "doc-001"
    )

    assert returned["page_number"] == 3

    assert returned["chunk_index"] == 1

    assert (
        returned["content"]
        == "Chuyển đổi số là nhiệm vụ quan trọng."
    )

    assert (
        returned["metadata"]["document_name"]
        == "Nghị quyết 57-NQ/TW"
    )


# ============================================================
# 13.2.1.12
# CITATION COUNT IS CORRECT
# ============================================================


def test_chat_api_citation_count_is_correct(
    fake_service,
):
    citations = []

    for index in range(3):
        citations.append(
            SimpleNamespace(
                citation_id=f"cit-{index}",
                source=f"Document {index}",
                score=0.9,
                document_id=f"doc-{index}",
                page_number=index + 1,
                chunk_index=index,
                content=f"Content {index}",
                metadata={},
                label=f"Document {index}",
            )
        )

    fake_service.citations = citations

    response = client.post(
        "/assistant/ask",
        json={
            "question": "Tra cứu tài liệu."
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["citations"]) == 3

    assert (
        body["metadata"]["citation_count"]
        == 3
    )


# ============================================================
# 13.2.1.13
# SERVICE UNAVAILABLE CONTRACT
# ============================================================


def test_chat_api_returns_503_when_service_missing(
    fake_service,
):
    original = (
        assistant_route._assistant_service
    )

    try:
        assistant_route._assistant_service = None

        response = client.post(
            "/assistant/ask",
            json={
                "question": (
                    "Test service unavailable."
                )
            },
        )

        assert response.status_code == 503

        body = response.json()

        assert "detail" in body

    finally:
        assistant_route._assistant_service = (
            original
        )


# ============================================================
# 13.2.1.14
# UNKNOWN ROUTE
# ============================================================


def test_unknown_chat_route_returns_404(
    fake_service,
):
    response = client.post(
        "/assistant/chat",
        json={
            "question": "Test."
        },
    )

    assert response.status_code == 404


# ============================================================
# 13.2.1.15
# FINAL CHAT API CONTRACT
# ============================================================


def test_final_chat_api_contract(
    fake_service,
):
    fake_service.answer_text = (
        "Hành Chính AI hỗ trợ cán bộ "
        "tra cứu và xử lý thông tin hành chính."
    )

    response = client.post(
        "/assistant/ask",
        json={
            "question": (
                "Hãy giới thiệu Hành Chính AI."
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    # --------------------------------------------------------
    # HTTP CONTRACT
    # --------------------------------------------------------

    assert body["success"] is True

    # --------------------------------------------------------
    # REQUEST → RESPONSE
    # --------------------------------------------------------

    assert (
        body["question"]
        == "Hãy giới thiệu Hành Chính AI."
    )

    # --------------------------------------------------------
    # AI ANSWER
    # --------------------------------------------------------

    assert body["answer"]

    assert (
        "Hành Chính AI"
        in body["answer"]
    )

    # --------------------------------------------------------
    # STRUCTURED RESPONSE
    # --------------------------------------------------------

    assert isinstance(
        body["citations"],
        list,
    )

    assert isinstance(
        body["metadata"],
        dict,
    )

    assert isinstance(
        body["message"],
        str,
    )

    # --------------------------------------------------------
    # METADATA CONTRACT
    # --------------------------------------------------------

    assert (
        "citation_count"
        in body["metadata"]
    )

    assert (
        body["metadata"]["citation_count"]
        == len(body["citations"])
    )

    # --------------------------------------------------------
    # SERVICE RECEIVED NORMALIZED QUESTION
    # --------------------------------------------------------

    assert (
        fake_service.last_question
        == "Hãy giới thiệu Hành Chính AI."
    )