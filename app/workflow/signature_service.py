"""
Hành Chính AI - Workflow Signature Service.

Sprint 16.6.1

Nghiệp vụ:

    APPROVED
        ↓
    PENDING_SIGNATURE
        ↓
      SIGNED

Signature Service chịu trách nhiệm điều phối nghiệp vụ ký.
State transition vẫn do Workflow Domain kiểm soát.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.workflow.models import (
    WorkflowItem,
    WorkflowStage,
)
from app.workflow.service import (
    WorkflowService,
)


# ============================================================
# EXCEPTIONS
# ============================================================


class WorkflowSignatureError(Exception):
    """
    Lỗi chung của Signature Service.
    """


class WorkflowSignatureValidationError(
    WorkflowSignatureError
):
    """
    Dữ liệu yêu cầu ký không hợp lệ.
    """


class WorkflowSignatureStateError(
    WorkflowSignatureError
):
    """
    Workflow đang ở trạng thái không phù hợp
    với nghiệp vụ ký.
    """


# ============================================================
# RESULT
# ============================================================


@dataclass
class WorkflowSignatureResult:
    """
    Kết quả nghiệp vụ ký.
    """

    workflow_id: str

    stage: WorkflowStage

    actor: str

    action: str

    note: str

    event: Any

    metadata: dict[str, Any]


# ============================================================
# SERVICE
# ============================================================


class WorkflowSignatureService:
    """
    Điều phối nghiệp vụ ký Workflow.
    """

    def __init__(
        self,
        workflow_service: WorkflowService,
    ) -> None:
        if workflow_service is None:
            raise ValueError(
                "workflow_service không được rỗng."
            )

        self.workflow_service = (
            workflow_service
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def _validate_actor(
        actor: str,
    ) -> str:
        if not isinstance(
            actor,
            str,
        ):
            raise WorkflowSignatureValidationError(
                "actor phải là chuỗi."
            )

        actor = actor.strip()

        if not actor:
            raise WorkflowSignatureValidationError(
                "actor không được rỗng."
            )

        return actor

    @staticmethod
    def _validate_note(
        note: str,
    ) -> str:
        if not isinstance(
            note,
            str,
        ):
            raise WorkflowSignatureValidationError(
                "note phải là chuỗi."
            )

        return note.strip()

    # ========================================================
    # GET WORKFLOW
    # ========================================================

    def get_workflow(
        self,
        workflow_id: str,
    ) -> WorkflowItem:
        """
        Lấy Workflow hiện tại.
        """

        return self.workflow_service.get(
            workflow_id
        )

    # ========================================================
    # SUBMIT FOR SIGNATURE
    # ========================================================

    def submit_for_signature(
        self,
        workflow_id: str,
        *,
        actor: str,
        note: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowSignatureResult:
        """
        Đưa Workflow đã được phê duyệt
        sang trạng thái chờ ký.

        APPROVED → PENDING_SIGNATURE
        """

        actor = self._validate_actor(
            actor
        )

        note = self._validate_note(
            note
        )

        workflow = self.workflow_service.get(
            workflow_id
        )

        if workflow.stage != WorkflowStage.APPROVED:
            raise WorkflowSignatureStateError(
                (
                    "Chỉ Workflow ở trạng thái "
                    f"'{WorkflowStage.APPROVED.value}' "
                    "mới được chuyển sang chờ ký."
                )
            )

        event = self.workflow_service.transition(
            workflow_id,
            WorkflowStage.PENDING_SIGNATURE,
            actor=actor,
            note=(
                note
                or "Chuyển Workflow sang trạng thái chờ ký."
            ),
            metadata=metadata,
        )

        self.workflow_service.update_metadata(
            workflow_id,
            {
                "signature_status": "pending",
                "submitted_for_signature_by": actor,
                "signature_note": note,
            },
        )

        return WorkflowSignatureResult(
            workflow_id=workflow_id,
            stage=WorkflowStage.PENDING_SIGNATURE,
            actor=actor,
            action="submit_for_signature",
            note=note,
            event=event,
            metadata={
                "signature_status": "pending",
                "submitted_for_signature_by": actor,
            },
        )

    # ========================================================
    # SIGN
    # ========================================================

    def sign(
        self,
        workflow_id: str,
        *,
        actor: str,
        note: str = "",
        signature_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowSignatureResult:
        """
        Thực hiện ký Workflow.

        PENDING_SIGNATURE → SIGNED

        signature_id là mã định danh chữ ký nếu
        hệ thống chữ ký điện tử bên ngoài cung cấp.
        """

        actor = self._validate_actor(
            actor
        )

        note = self._validate_note(
            note
        )

        if signature_id is not None:
            if not isinstance(
                signature_id,
                str,
            ):
                raise WorkflowSignatureValidationError(
                    "signature_id phải là chuỗi."
                )

            signature_id = signature_id.strip()

            if not signature_id:
                raise WorkflowSignatureValidationError(
                    "signature_id không được rỗng."
                )

        workflow = self.workflow_service.get(
            workflow_id
        )

        if workflow.stage != WorkflowStage.PENDING_SIGNATURE:
            raise WorkflowSignatureStateError(
                (
                    "Chỉ Workflow ở trạng thái "
                    f"'{WorkflowStage.PENDING_SIGNATURE.value}' "
                    "mới được ký."
                )
            )

        event_metadata: dict[str, Any] = {}

        if metadata:
            event_metadata.update(
                metadata
            )

        if signature_id:
            event_metadata[
                "signature_id"
            ] = signature_id

        event = self.workflow_service.transition(
            workflow_id,
            WorkflowStage.SIGNED,
            actor=actor,
            note=(
                note
                or "Workflow đã được ký."
            ),
            metadata=event_metadata,
        )

        stored_metadata: dict[str, Any] = {
            "signature_status": "signed",
            "signed_by": actor,
            "signature_note": note,
        }

        if signature_id:
            stored_metadata[
                "signature_id"
            ] = signature_id

        if metadata:
            stored_metadata.update(
                metadata
            )

        self.workflow_service.update_metadata(
            workflow_id,
            stored_metadata,
        )

        return WorkflowSignatureResult(
            workflow_id=workflow_id,
            stage=WorkflowStage.SIGNED,
            actor=actor,
            action="sign",
            note=note,
            event=event,
            metadata=stored_metadata,
        )

    # ========================================================
    # SIGNED CHECK
    # ========================================================

    def is_signed(
        self,
        workflow_id: str,
    ) -> bool:
        """
        Kiểm tra Workflow đã ký hay chưa.
        """

        workflow = self.workflow_service.get(
            workflow_id
        )

        return workflow.stage in (
            WorkflowStage.SIGNED,
            WorkflowStage.EXPORTED,
        )