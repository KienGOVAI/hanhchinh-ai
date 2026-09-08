"""
Sprint 16.4 - Workflow + AI + Document Tests.
"""

from dataclasses import dataclass
from typing import Any

import pytest

from app.workflow import (
    WorkflowAIProcessingError,
    WorkflowAIService,
    WorkflowDocumentError,
    WorkflowService,
    WorkflowStage,
)


# ============================================================
# FAKE AI
# ============================================================


@dataclass
class FakeAIResponse:
    answer: str

    citations: list[Any]

    metadata: dict[str, Any]


class FakeAssistantService:
    """
    Fake Assistant để test orchestration
    mà không gọi AI thật.
    """

    def __init__(
        self,
        answer: str = (
            "Dự thảo nội dung về "
            "chuyển đổi số."
        ),
    ) -> None:
        self.answer_text = answer
        self.questions: list[str] = []

    def answer(
        self,
        question: str,
    ) -> FakeAIResponse:
        self.questions.append(
            question
        )

        return FakeAIResponse(
            answer=self.answer_text,
            citations=[
                {
                    "source": "demo-source",
                    "score": 0.95,
                }
            ],
            metadata={
                "pipeline_stage": "citation",
            },
        )


# ============================================================
# FAKE DOCUMENT
# ============================================================


@dataclass
class FakeDocumentResponse:
    file_name: str

    content: str


class FakeDocumentGenerator:
    """
    Fake Document Service.
    """

    def __init__(
        self,
        content: str = (
            "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n\n"
            "Dự thảo công văn về chuyển đổi số."
        ),
    ) -> None:
        self.content = content
        self.requests: list[Any] = []

    def __call__(
        self,
        request: Any,
    ) -> FakeDocumentResponse:
        self.requests.append(
            request
        )

        return FakeDocumentResponse(
            file_name="du_thao_cong_van.docx",
            content=self.content,
        )


# ============================================================
# FIXTURE
# ============================================================


@pytest.fixture
def workflow_service() -> WorkflowService:
    return WorkflowService()


@pytest.fixture
def assistant_service() -> FakeAssistantService:
    return FakeAssistantService()


@pytest.fixture
def document_generator() -> FakeDocumentGenerator:
    return FakeDocumentGenerator()


@pytest.fixture
def workflow_ai_service(
    workflow_service: WorkflowService,
    assistant_service: FakeAssistantService,
    document_generator: FakeDocumentGenerator,
) -> WorkflowAIService:
    return WorkflowAIService(
        workflow_service=workflow_service,
        assistant_service=assistant_service,
        document_generator=document_generator,
    )


def create_workflow(
    service: WorkflowService,
):
    return service.create(
        title="Công văn chuyển đổi số",
        document_type="cong_van",
        created_by="user-001",
    )


# ============================================================
# TEST 1
# ============================================================


def test_service_contract(
    workflow_service: WorkflowService,
    assistant_service: FakeAssistantService,
    document_generator: FakeDocumentGenerator,
) -> None:
    service = WorkflowAIService(
        workflow_service=workflow_service,
        assistant_service=assistant_service,
        document_generator=document_generator,
    )

    assert service.workflow_service is (
        workflow_service
    )

    assert service.assistant_service is (
        assistant_service
    )

    assert service.document_generator is (
        document_generator
    )


# ============================================================
# TEST 2
# ============================================================


def test_process_and_draft_full_pipeline(
    workflow_service: WorkflowService,
    workflow_ai_service: WorkflowAIService,
) -> None:
    workflow = create_workflow(
        workflow_service
    )

    result = (
        workflow_ai_service.process_and_draft(
            workflow.workflow_id,
            instruction=(
                "Soạn công văn triển khai "
                "chuyển đổi số."
            ),
        )
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.workflow_id == (
        workflow.workflow_id
    )

    assert result.ai_answer

    assert result.citations

    assert result.document_file_name == (
        "du_thao_cong_van.docx"
    )

    assert result.document_content

    assert stored.stage == (
        WorkflowStage.DRAFTING
    )

    assert stored.metadata[
        "workflow_instruction"
    ] == (
        "Soạn công văn triển khai "
        "chuyển đổi số."
    )

    assert stored.metadata[
        "ai_answer"
    ] == result.ai_answer

    assert stored.metadata[
        "draft_file_name"
    ] == "du_thao_cong_van.docx"

    assert stored.metadata[
        "draft_content"
    ] == result.document_content

    assert len(
        stored.events
    ) == 2


# ============================================================
# TEST 3
# ============================================================


def test_ai_receives_workflow_context(
    workflow_service: WorkflowService,
    assistant_service: FakeAssistantService,
    document_generator: FakeDocumentGenerator,
) -> None:
    workflow = create_workflow(
        workflow_service
    )

    service = WorkflowAIService(
        workflow_service=workflow_service,
        assistant_service=assistant_service,
        document_generator=document_generator,
    )

    service.process_and_draft(
        workflow.workflow_id,
        instruction=(
            "Nêu nhiệm vụ triển khai "
            "trong năm 2026."
        ),
    )

    assert len(
        assistant_service.questions
    ) == 1

    question = (
        assistant_service.questions[0]
    )

    assert "cong_van" in question
    assert "Công văn chuyển đổi số" in question
    assert (
        "Nêu nhiệm vụ triển khai "
        "trong năm 2026."
        in question
    )


# ============================================================
# TEST 4
# ============================================================


def test_document_receives_ai_content(
    workflow_service: WorkflowService,
    assistant_service: FakeAssistantService,
    document_generator: FakeDocumentGenerator,
) -> None:
    workflow = create_workflow(
        workflow_service
    )

    service = WorkflowAIService(
        workflow_service=workflow_service,
        assistant_service=assistant_service,
        document_generator=document_generator,
    )

    service.process_and_draft(
        workflow.workflow_id,
        instruction="Soạn công văn.",
    )

    assert len(
        document_generator.requests
    ) == 1

    request = (
        document_generator.requests[0]
    )

    assert request.type == "cong_van"

    assert request.title == (
        "Công văn chuyển đổi số"
    )

    assert (
        "Dự thảo nội dung về "
        "chuyển đổi số."
        in request.prompt
    )

    assert request.content == (
        "Dự thảo nội dung về "
        "chuyển đổi số."
    )


# ============================================================
# TEST 5
# ============================================================


def test_invalid_initial_stage_is_rejected(
    workflow_service: WorkflowService,
    workflow_ai_service: WorkflowAIService,
) -> None:
    workflow = create_workflow(
        workflow_service
    )

    workflow_service.transition(
        workflow.workflow_id,
        WorkflowStage.AI_PROCESSING,
        actor="system",
    )

    with pytest.raises(
        WorkflowAIProcessingError
    ):
        workflow_ai_service.process_and_draft(
            workflow.workflow_id,
            instruction="Soạn công văn.",
        )

    assert workflow.stage == (
        WorkflowStage.AI_PROCESSING
    )


# ============================================================
# TEST 6
# ============================================================


def test_empty_instruction_is_rejected(
    workflow_service: WorkflowService,
    workflow_ai_service: WorkflowAIService,
) -> None:
    workflow = create_workflow(
        workflow_service
    )

    with pytest.raises(
        Exception
    ):
        workflow_ai_service.process_and_draft(
            workflow.workflow_id,
            instruction="   ",
        )

    assert workflow.stage == (
        WorkflowStage.RECEIVED
    )


# ============================================================
# TEST 7
# ============================================================


def test_ai_failure_does_not_reach_drafting(
    workflow_service: WorkflowService,
    document_generator: FakeDocumentGenerator,
) -> None:

    class FailingAssistant:
        def answer(
            self,
            question: str,
        ):
            raise RuntimeError(
                "AI unavailable"
            )

    workflow = create_workflow(
        workflow_service
    )

    service = WorkflowAIService(
        workflow_service=workflow_service,
        assistant_service=FailingAssistant(),
        document_generator=document_generator,
    )

    with pytest.raises(
        WorkflowAIProcessingError
    ):
        service.process_and_draft(
            workflow.workflow_id,
            instruction="Soạn công văn.",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.AI_PROCESSING
    )

    assert (
        "draft_content"
        not in stored.metadata
    )


# ============================================================
# TEST 8
# ============================================================


def test_document_failure_does_not_reach_drafting(
    workflow_service: WorkflowService,
    assistant_service: FakeAssistantService,
) -> None:

    def failing_document_generator(
        request: Any,
    ):
        raise RuntimeError(
            "Document generation failed"
        )

    workflow = create_workflow(
        workflow_service
    )

    service = WorkflowAIService(
        workflow_service=workflow_service,
        assistant_service=assistant_service,
        document_generator=(
            failing_document_generator
        ),
    )

    with pytest.raises(
        WorkflowDocumentError
    ):
        service.process_and_draft(
            workflow.workflow_id,
            instruction="Soạn công văn.",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.AI_PROCESSING
    )

    assert (
        "draft_content"
        not in stored.metadata
    )


# ============================================================
# TEST 9
# ============================================================


def test_citations_and_ai_metadata_are_preserved(
    workflow_service: WorkflowService,
    assistant_service: FakeAssistantService,
    document_generator: FakeDocumentGenerator,
) -> None:
    workflow = create_workflow(
        workflow_service
    )

    service = WorkflowAIService(
        workflow_service=workflow_service,
        assistant_service=assistant_service,
        document_generator=document_generator,
    )

    result = service.process_and_draft(
        workflow.workflow_id,
        instruction="Soạn công văn.",
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert len(
        result.citations
    ) == 1

    assert stored.metadata[
        "ai_citations"
    ] == result.citations

    assert stored.metadata[
        "ai_metadata"
    ] == {
        "pipeline_stage": "citation"
    }


# ============================================================
# TEST 10
# ============================================================


def test_result_metadata_reports_drafting(
    workflow_service: WorkflowService,
    workflow_ai_service: WorkflowAIService,
) -> None:
    workflow = create_workflow(
        workflow_service
    )

    result = (
        workflow_ai_service.process_and_draft(
            workflow.workflow_id,
            instruction="Soạn công văn.",
        )
    )

    assert result.metadata[
        "workflow_stage"
    ] == "drafting"

    assert result.metadata[
        "citation_count"
    ] == 1