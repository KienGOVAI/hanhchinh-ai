"""
Sprint 13.2.2 - Chat API -> AssistantService Integration

Mục tiêu:

    HTTP
      ↓
    /assistant/ask
      ↓
    AssistantService.answer()
      ↓
    AssistantResponse
      ↓
    API Response

Không chạy Ollama.
Không chạy Embedding thật.
Không chạy RAG thật.
Không chạy Knowledge Base thật.

Dùng Fake AssistantService để kiểm tra integration contract
giữa FastAPI route và AssistantService.
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app.api.routes.assistant as assistant_route
from app.knowledge.assistant.assistant_service import (
    AssistantServiceError,
)
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
    Fake implementation của AssistantService.

    Contract thật:

        service.answer(question)

    trả:

        AssistantResponse(
            answer=...,
            query=...,
            citations=...,
            metadata=...,
        )
    """

    def __init__(
        self,
        *,
        answer: str = (
            "Chuyển đổi số là quá trình ứng dụng "
            "công nghệ số vào hoạt động quản lý "
            "và cung cấp dịch vụ."
        ),
        citations=None,
        metadata=None,
    ) -> None:

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

        self.call_count = 0
        self.last_question = None

        self.error = None

    # --------------------------------------------------------
    # REAL SERVICE CONTRACT
    # --------------------------------------------------------

    def answer(
        self,
        question: str,
    ):
        """
        Khớp với AssistantService.answer().
        """

        self.call_count += 1
        self.last_question = question

        if self.error is not None:
            raise self.error

        return SimpleNamespace(
            answer=self.answer_text,
            query=question,
            citations=list(self.citations),
            metadata=dict(self.metadata),
        )


# ============================================================
# FIXTURE
# ============================================================


@pytest.fixture
def fake_service():
    """
    Inject FakeAssistantService vào Assistant API runtime.
    """

    original_service = (
        assistant_route._assistant_service
    )

    service = FakeAssistantService()

    assistant_route.configure_assistant_service(
        service
    )

    yield service

    assistant_route._assistant_service = (
        original_service
    )


# ============================================================
# 13.2.2.1
# API CALLS ASSISTANT SERVICE
# ============================================================


def test_api_calls_assistant_service(
    fake_service,
):
    question = "Chuyển đổi số là gì?"

    response = client.post(
        "/assistant/ask",
        json={
            "question": question,
        },
    )

    assert response.status_code == 200

    assert fake_service.call_count == 1

    assert (
        fake_service.last_question
        == question
    )


# ============================================================
# 13.2.2.2
# API PASSES NORMALIZED QUESTION
# ============================================================


def test_api_passes_normalized_question_to_service(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={
            "question": (
                "   Chuyển đổi số ở cấp xã là gì?   "
            ),
        },
    )

    assert response.status_code == 200

    assert (
        fake_service.last_question
        == "Chuyển đổi số ở cấp xã là gì?"
    )


# ============================================================
# 13.2.2.3
# SERVICE ANSWER IS MAPPED
# ============================================================


def test_service_answer_is_mapped_to_api_response(
    fake_service,
):
    expected_answer = (
        "Đây là nội dung được sinh bởi "
        "AssistantService."
    )

    fake_service.answer_text = (
        expected_answer
    )

    response = client.post(
        "/assistant/ask",
        json={
            "question": "Hỏi thử.",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["answer"]
        == expected_answer
    )


# ============================================================
# 13.2.2.4
# SERVICE QUERY IS MAPPED
# ============================================================


def test_service_query_is_mapped(
    fake_service,
):
    question = "RAG là gì?"

    response = client.post(
        "/assistant/ask",
        json={
            "question": question,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["question"]
        == question
    )

    assert (
        fake_service.last_question
        == question
    )


# ============================================================
# 13.2.2.5
# SERVICE METADATA IS MAPPED
# ============================================================


def test_service_metadata_is_mapped(
    fake_service,
):
    fake_service.metadata = {
        "provider": "ollama",
        "model": "qwen3:8b",
        "pipeline_stage": "citation",
        "retrieved_count": 5,
    }

    response = client.post(
        "/assistant/ask",
        json={
            "question": "RAG hoạt động thế nào?",
        },
    )

    assert response.status_code == 200

    body = response.json()

    metadata = body["metadata"]

    assert (
        metadata["provider"]
        == "ollama"
    )

    assert (
        metadata["model"]
        == "qwen3:8b"
    )

    assert (
        metadata["pipeline_stage"]
        == "citation"
    )

    assert (
        metadata["retrieved_count"]
        == 5
    )


# ============================================================
# 13.2.2.6
# SERVICE CITATIONS ARE MAPPED
# ============================================================


def test_service_citations_are_mapped(
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
            "Chuyển đổi số là nhiệm vụ "
            "quan trọng."
        ),
        metadata={
            "document_name": (
                "Nghị quyết 57-NQ/TW"
            ),
        },
        label=(
            "Nghị quyết 57-NQ/TW — trang 3"
        ),
    )

    fake_service.citations = [
        citation
    ]

    response = client.post(
        "/assistant/ask",
        json={
            "question": (
                "Nghị quyết 57 nói gì?"
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(
        body["citations"]
    ) == 1

    returned = body["citations"][0]

    assert (
        returned["citation_id"]
        == "cit-001"
    )

    assert (
        returned["source"]
        == "Nghị quyết 57-NQ/TW"
    )

    assert (
        returned["score"]
        == 0.95
    )

    assert (
        returned["document_id"]
        == "doc-001"
    )

    assert (
        returned["page_number"]
        == 3
    )

    assert (
        returned["chunk_index"]
        == 1
    )

    assert (
        returned["metadata"][
            "document_name"
        ]
        == "Nghị quyết 57-NQ/TW"
    )

    assert (
        body["metadata"][
            "citation_count"
        ]
        == 1
    )


# ============================================================
# 13.2.2.7
# MULTIPLE CITATIONS ARE PRESERVED
# ============================================================


def test_multiple_citations_are_preserved(
    fake_service,
):
    citations = []

    for index in range(5):
        citations.append(
            SimpleNamespace(
                citation_id=f"cit-{index}",
                source=f"Document {index}",
                score=0.90 - index * 0.01,
                document_id=f"doc-{index}",
                page_number=index + 1,
                chunk_index=index,
                content=f"Content {index}",
                metadata={
                    "document_name": (
                        f"Document {index}"
                    ),
                },
                label=f"Document {index}",
            )
        )

    fake_service.citations = citations

    response = client.post(
        "/assistant/ask",
        json={
            "question": (
                "Tra cứu nhiều tài liệu."
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(
        body["citations"]
    ) == 5

    assert (
        body["metadata"][
            "citation_count"
        ]
        == 5
    )

    for index, citation in enumerate(
        body["citations"]
    ):
        assert (
            citation["citation_id"]
            == f"cit-{index}"
        )

        assert (
            citation["document_id"]
            == f"doc-{index}"
        )


# ============================================================
# 13.2.2.8
# EMPTY CITATIONS ARE VALID
# ============================================================


def test_empty_citations_are_valid(
    fake_service,
):
    fake_service.citations = []

    response = client.post(
        "/assistant/ask",
        json={
            "question": (
                "Câu hỏi không có nguồn."
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["citations"] == []

    assert (
        body["metadata"][
            "citation_count"
        ]
        == 0
    )


# ============================================================
# 13.2.2.9
# INVALID REQUEST DOES NOT CALL SERVICE
# ============================================================


def test_invalid_request_does_not_call_service(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={
            "question": "   ",
        },
    )

    assert response.status_code == 400

    assert (
        fake_service.call_count
        == 0
    )


# ============================================================
# 13.2.2.10
# MISSING QUESTION DOES NOT CALL SERVICE
# ============================================================


def test_missing_question_does_not_call_service(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={},
    )

    assert response.status_code == 422

    assert (
        fake_service.call_count
        == 0
    )


# ============================================================
# 13.2.2.11
# INVALID QUESTION TYPE DOES NOT CALL SERVICE
# ============================================================


def test_invalid_question_type_does_not_call_service(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={
            "question": 123,
        },
    )

    assert response.status_code == 422

    assert (
        fake_service.call_count
        == 0
    )


# ============================================================
# 13.2.2.12
# SERVICE CALLED ONLY ONCE
# ============================================================


def test_service_is_called_only_once(
    fake_service,
):
    response = client.post(
        "/assistant/ask",
        json={
            "question": "Một câu hỏi.",
        },
    )

    assert response.status_code == 200

    assert (
        fake_service.call_count
        == 1
    )


# ============================================================
# 13.2.2.13
# SERVICE RESPONSE PRESERVES ANSWER
# ============================================================


def test_service_response_preserves_answer(
    fake_service,
):
    fake_service.answer_text = (
        "Hành Chính AI hỗ trợ cán bộ "
        "văn phòng trong công tác hành chính."
    )

    response = client.post(
        "/assistant/ask",
        json={
            "question": (
                "Hành Chính AI dùng để làm gì?"
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["answer"]
        == fake_service.answer_text
    )

    assert body["success"] is True


# ============================================================
# 13.2.2.14
# SERVICE ERROR IS NOT SILENTLY IGNORED
# ============================================================


def test_assistant_service_error_is_handled(
    fake_service,
):
    fake_service.error = (
        AssistantServiceError(
            "Lỗi Assistant Service."
        )
    )

    response = client.post(
        "/assistant/ask",
        json={
            "question": "Test service error.",
        },
    )

    assert response.status_code >= 400

    body = response.json()

    assert (
        "detail"
        in body
    )


# ============================================================
# 13.2.2.15
# FINAL SERVICE INTEGRATION GATE
# ============================================================


def test_final_chat_service_integration_gate(
    fake_service,
):
    question = (
        "Hãy giới thiệu Hành Chính AI "
        "và khả năng hỗ trợ cán bộ."
    )

    fake_service.answer_text = (
        "Hành Chính AI là trợ lý AI "
        "hỗ trợ cán bộ tra cứu, xử lý "
        "thông tin hành chính và khai thác "
        "nguồn tài liệu."
    )

    fake_service.metadata = {
        "provider": "ollama",
        "model": "qwen3:8b",
        "pipeline_stage": "citation",
        "retrieved_count": 3,
    }

    response = client.post(
        "/assistant/ask",
        json={
            "question": question,
        },
    )

    assert response.status_code == 200

    body = response.json()

    # --------------------------------------------------------
    # HTTP
    # --------------------------------------------------------

    assert body["success"] is True

    # --------------------------------------------------------
    # SERVICE CALL
    # --------------------------------------------------------

    assert (
        fake_service.call_count
        == 1
    )

    assert (
        fake_service.last_question
        == question
    )

    # --------------------------------------------------------
    # ANSWER
    # --------------------------------------------------------

    assert (
        body["answer"]
        == fake_service.answer_text
    )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    assert (
        body["metadata"]["provider"]
        == "ollama"
    )

    assert (
        body["metadata"]["model"]
        == "qwen3:8b"
    )

    assert (
        body["metadata"]["pipeline_stage"]
        == "citation"
    )

    assert (
        body["metadata"]["retrieved_count"]
        == 3
    )

    # --------------------------------------------------------
    # CITATION CONTRACT
    # --------------------------------------------------------

    assert isinstance(
        body["citations"],
        list,
    )

    assert (
        body["metadata"][
            "citation_count"
        ]
        == len(body["citations"])
    )