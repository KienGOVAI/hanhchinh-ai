"""
Hành Chính AI - Workflow AI Service.

Sprint 16.4

Pipeline:

    Workflow RECEIVED
        ↓
    AI_PROCESSING
        ↓
    AssistantService
        ↓
    Document Generation
        ↓
    DRAFTING

Service này đóng vai trò orchestrator giữa:

    Workflow
        +
    Assistant
        +
    Document

Không thay thế AssistantService hoặc DocumentService.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from app.workflow.models import (
    WorkflowItem,
    WorkflowStage,
)
from app.workflow.service import WorkflowService


# ============================================================
# EXCEPTIONS
# ============================================================


class WorkflowAIError(Exception):
    """
    Lỗi chung của Workflow AI Service.
    """


class WorkflowAIValidationError(
    WorkflowAIError
):
    """
    Dữ liệu Workflow AI không hợp lệ.
    """


class WorkflowAIProcessingError(
    WorkflowAIError
):
    """
    Lỗi trong quá trình AI xử lý Workflow.
    """


class WorkflowDocumentError(
    WorkflowAIError
):
    """
    Lỗi trong quá trình tạo bản dự thảo.
    """


# ============================================================
# RESULT
# ============================================================


@dataclass
class WorkflowAIResult:
    """
    Kết quả của Workflow AI Processing.

    Bao gồm:
        - AI answer
        - citations
        - document file
        - document content
        - metadata
    """

    workflow_id: str

    ai_answer: str

    citations: list[Any] = field(
        default_factory=list
    )

    document_file_name: str = ""

    document_content: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SERVICE
# ============================================================


class WorkflowAIService:
    """
    Orchestrator:

        Workflow
            ↓
        Assistant
            ↓
        Document
            ↓
        Workflow DRAFTING
    """

    def __init__(
        self,
        workflow_service: WorkflowService,
        assistant_service: Any,
        document_generator: Callable[
            [Any],
            Any,
        ],
    ) -> None:
        if workflow_service is None:
            raise ValueError(
                "workflow_service không được rỗng."
            )

        if assistant_service is None:
            raise ValueError(
                "assistant_service không được rỗng."
            )

        if not callable(document_generator):
            raise TypeError(
                "document_generator phải là callable."
            )

        self.workflow_service = (
            workflow_service
        )

        self.assistant_service = (
            assistant_service
        )

        self.document_generator = (
            document_generator
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def _validate_text(
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise WorkflowAIValidationError(
                f"{field_name} phải là chuỗi."
            )

        normalized = value.strip()

        if not normalized:
            raise WorkflowAIValidationError(
                f"{field_name} không được rỗng."
            )

        return normalized

    # ========================================================
    # BUILD AI REQUEST
    # ========================================================

    def _build_ai_question(
        self,
        workflow: WorkflowItem,
        instruction: str,
    ) -> str:
        """
        Xây dựng câu hỏi gửi cho Assistant.

        Giữ nguyên ngữ cảnh nghiệp vụ của Workflow.
        """

        return (
            "Xử lý hồ sơ hành chính sau và "
            "đề xuất nội dung dự thảo.\n\n"
            f"Loại văn bản: "
            f"{workflow.document_type}\n"
            f"Tiêu đề: {workflow.title}\n\n"
            f"Yêu cầu:\n{instruction}"
        )

    # ========================================================
    # BUILD DOCUMENT REQUEST
    # ========================================================

    def _build_document_request(
        self,
        workflow: WorkflowItem,
        ai_answer: str,
    ) -> Any:
        """
        Tạo DocumentRequest tương thích với
        Document Service hiện tại.
        """

        from app.schemas.document import (
            DocumentRequest,
        )

        return DocumentRequest(
            provider="ollama",
            type=workflow.document_type,
            title=workflow.title,
            prompt=(
                "Soạn văn bản hành chính hoàn chỉnh "
                "dựa trên yêu cầu và nội dung AI "
                "đã xử lý dưới đây.\n\n"
                f"YÊU CẦU:\n"
                f"{workflow.metadata.get('workflow_instruction', '')}"
                "\n\n"
                f"NỘI DUNG AI:\n"
                f"{ai_answer}"
            ),
            content=ai_answer,
        )

    # ========================================================
    # PROCESS
    # ========================================================

    def process_and_draft(
        self,
        workflow_id: str,
        *,
        instruction: str,
        actor: str = "system",
    ) -> WorkflowAIResult:
        """
        Thực hiện:

            RECEIVED
                ↓
            AI_PROCESSING
                ↓
            AI
                ↓
            Document
                ↓
            DRAFTING

        Nếu bất kỳ bước AI/Document nào lỗi,
        Workflow sẽ không bị đánh dấu DRAFTING.
        """

        instruction = self._validate_text(
            instruction,
            "instruction",
        )

        actor = self._validate_text(
            actor,
            "actor",
        )

        workflow = self.workflow_service.get(
            workflow_id
        )

        if workflow.stage != WorkflowStage.RECEIVED:
            raise WorkflowAIProcessingError(
                (
                    "Workflow phải ở trạng thái "
                    f"'{WorkflowStage.RECEIVED.value}' "
                    "để bắt đầu AI processing."
                )
            )

        # ----------------------------------------------------
        # Lưu yêu cầu nghiệp vụ
        # ----------------------------------------------------

        self.workflow_service.update_metadata(
            workflow_id,
            {
                "workflow_instruction": instruction,
            },
        )

        # ----------------------------------------------------
        # RECEIVED → AI_PROCESSING
        # ----------------------------------------------------

        self.workflow_service.transition(
            workflow_id,
            WorkflowStage.AI_PROCESSING,
            actor=actor,
            note="Bắt đầu AI xử lý Workflow.",
        )

        # ----------------------------------------------------
        # AI PROCESSING
        # ----------------------------------------------------

        try:
            ai_response = (
                self.assistant_service.answer(
                    self._build_ai_question(
                        workflow,
                        instruction,
                    )
                )
            )

        except Exception as exc:
            raise WorkflowAIProcessingError(
                "AI xử lý Workflow thất bại."
            ) from exc

        ai_answer = getattr(
            ai_response,
            "answer",
            None,
        )

        if not isinstance(
            ai_answer,
            str,
        ) or not ai_answer.strip():
            raise WorkflowAIProcessingError(
                "AI không trả về nội dung hợp lệ."
            )

        citations = list(
            getattr(
                ai_response,
                "citations",
                [],
            )
            or []
        )

        ai_metadata = dict(
            getattr(
                ai_response,
                "metadata",
                {},
            )
            or {}
        )

        # ----------------------------------------------------
        # BUILD DOCUMENT REQUEST
        # ----------------------------------------------------

        document_request = (
            self._build_document_request(
                workflow,
                ai_answer,
            )
        )

        # ----------------------------------------------------
        # DOCUMENT GENERATION
        # ----------------------------------------------------

        try:
            document_response = (
                self.document_generator(
                    document_request
                )
            )

        except Exception as exc:
            raise WorkflowDocumentError(
                "Không thể tạo bản dự thảo văn bản."
            ) from exc

        document_file_name = getattr(
            document_response,
            "file_name",
            "",
        )

        document_content = getattr(
            document_response,
            "content",
            "",
        )

        if not isinstance(
            document_content,
            str,
        ) or not document_content.strip():
            raise WorkflowDocumentError(
                "Document Service không trả về "
                "nội dung dự thảo hợp lệ."
            )

        # ----------------------------------------------------
        # SAVE WORKFLOW RESULT
        # ----------------------------------------------------

        self.workflow_service.update_metadata(
            workflow_id,
            {
                "ai_answer": ai_answer,
                "ai_citations": citations,
                "ai_metadata": ai_metadata,
                "draft_file_name": (
                    document_file_name
                ),
                "draft_content": (
                    document_content
                ),
            },
        )

        # ----------------------------------------------------
        # AI_PROCESSING → DRAFTING
        # ----------------------------------------------------

        self.workflow_service.transition(
            workflow_id,
            WorkflowStage.DRAFTING,
            actor=actor,
            note="AI xử lý và tạo bản dự thảo thành công.",
            metadata={
                "draft_file_name": (
                    document_file_name
                ),
                "citation_count": len(
                    citations
                ),
            },
        )

        return WorkflowAIResult(
            workflow_id=workflow_id,
            ai_answer=ai_answer,
            citations=citations,
            document_file_name=(
                document_file_name
            ),
            document_content=(
                document_content
            ),
            metadata={
                "workflow_stage": (
                    WorkflowStage.DRAFTING.value
                ),
                "citation_count": len(
                    citations
                ),
                "ai_metadata": ai_metadata,
            },
        )