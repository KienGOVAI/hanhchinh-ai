"""
Hành Chính AI - Workflow Approval Service.

Sprint 16.5

Nghiệp vụ:

    DRAFTING
        ↓
    PENDING_APPROVAL
        ↓
    ┌──────────────┐
    │              │
    ▼              ▼
 APPROVED       REJECTED
    │              │
    ▼              ▼
PENDING_        DRAFTING
SIGNATURE

Approval Service chỉ điều phối nghiệp vụ duyệt.
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


class WorkflowApprovalError(Exception):
    """
    Lỗi chung của Approval Service.
    """


class WorkflowApprovalValidationError(
    WorkflowApprovalError
):
    """
    Dữ liệu yêu cầu duyệt không hợp lệ.
    """


class WorkflowApprovalStateError(
    WorkflowApprovalError
):
    """
    Workflow đang ở trạng thái không phù hợp
    với nghiệp vụ duyệt.
    """


# ============================================================
# RESULT
# ============================================================


@dataclass
class WorkflowApprovalResult:
    """
    Kết quả nghiệp vụ duyệt.
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


class WorkflowApprovalService:
    """
    Điều phối nghiệp vụ phê duyệt Workflow.
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
            raise WorkflowApprovalValidationError(
                "actor phải là chuỗi."
            )

        actor = actor.strip()

        if not actor:
            raise WorkflowApprovalValidationError(
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
            raise WorkflowApprovalValidationError(
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
        return self.workflow_service.get(
            workflow_id
        )

    # ========================================================
    # SUBMIT FOR APPROVAL
    # ========================================================

    def submit_for_approval(
        self,
        workflow_id: str,
        *,
        actor: str,
        note: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowApprovalResult:
        """
        Đưa bản dự thảo từ DRAFTING
        sang PENDING_APPROVAL.
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

        if workflow.stage != WorkflowStage.DRAFTING:
            raise WorkflowApprovalStateError(
                (
                    "Chỉ Workflow ở trạng thái "
                    f"'{WorkflowStage.DRAFTING.value}' "
                    "mới được gửi duyệt."
                )
            )

        event = self.workflow_service.transition(
            workflow_id,
            WorkflowStage.PENDING_APPROVAL,
            actor=actor,
            note=note or "Gửi bản dự thảo để phê duyệt.",
            metadata=metadata,
        )

        self.workflow_service.update_metadata(
            workflow_id,
            {
                "approval_status": "pending",
                "submitted_for_approval_by": actor,
                "approval_note": note,
            },
        )

        return WorkflowApprovalResult(
            workflow_id=workflow_id,
            stage=WorkflowStage.PENDING_APPROVAL,
            actor=actor,
            action="submit_for_approval",
            note=note,
            event=event,
            metadata={
                "approval_status": "pending",
            },
        )

    # ========================================================
    # APPROVE
    # ========================================================

    def approve(
        self,
        workflow_id: str,
        *,
        actor: str,
        note: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowApprovalResult:
        """
        Phê duyệt Workflow.

        PENDING_APPROVAL → APPROVED
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

        if workflow.stage != WorkflowStage.PENDING_APPROVAL:
            raise WorkflowApprovalStateError(
                (
                    "Chỉ Workflow ở trạng thái "
                    f"'{WorkflowStage.PENDING_APPROVAL.value}' "
                    "mới được phê duyệt."
                )
            )

        event = self.workflow_service.transition(
            workflow_id,
            WorkflowStage.APPROVED,
            actor=actor,
            note=note or "Workflow đã được phê duyệt.",
            metadata=metadata,
        )

        self.workflow_service.update_metadata(
            workflow_id,
            {
                "approval_status": "approved",
                "approved_by": actor,
                "approval_note": note,
            },
        )

        return WorkflowApprovalResult(
            workflow_id=workflow_id,
            stage=WorkflowStage.APPROVED,
            actor=actor,
            action="approve",
            note=note,
            event=event,
            metadata={
                "approval_status": "approved",
                "approved_by": actor,
            },
        )

    # ========================================================
    # REJECT
    # ========================================================

    def reject(
        self,
        workflow_id: str,
        *,
        actor: str,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowApprovalResult:
        """
        Từ chối Workflow.

        PENDING_APPROVAL → REJECTED

        reason bắt buộc phải có.
        """

        actor = self._validate_actor(
            actor
        )

        reason = self._validate_note(
            reason
        )

        if not reason:
            raise WorkflowApprovalValidationError(
                "reason không được rỗng khi từ chối."
            )

        workflow = self.workflow_service.get(
            workflow_id
        )

        if workflow.stage != WorkflowStage.PENDING_APPROVAL:
            raise WorkflowApprovalStateError(
                (
                    "Chỉ Workflow ở trạng thái "
                    f"'{WorkflowStage.PENDING_APPROVAL.value}' "
                    "mới được từ chối."
                )
            )

        event = self.workflow_service.transition(
            workflow_id,
            WorkflowStage.REJECTED,
            actor=actor,
            note=reason,
            metadata=metadata,
        )

        self.workflow_service.update_metadata(
            workflow_id,
            {
                "approval_status": "rejected",
                "rejected_by": actor,
                "rejection_reason": reason,
            },
        )

        return WorkflowApprovalResult(
            workflow_id=workflow_id,
            stage=WorkflowStage.REJECTED,
            actor=actor,
            action="reject",
            note=reason,
            event=event,
            metadata={
                "approval_status": "rejected",
                "rejected_by": actor,
                "rejection_reason": reason,
            },
        )

    # ========================================================
    # RETURN TO DRAFTING
    # ========================================================

    def return_to_drafting(
        self,
        workflow_id: str,
        *,
        actor: str,
        note: str,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowApprovalResult:
        """
        Đưa hồ sơ bị từ chối quay lại DRAFTING.

        REJECTED → DRAFTING
        """

        actor = self._validate_actor(
            actor
        )

        note = self._validate_note(
            note
        )

        if not note:
            raise WorkflowApprovalValidationError(
                "note không được rỗng khi "
                "đưa hồ sơ trở lại soạn thảo."
            )

        workflow = self.workflow_service.get(
            workflow_id
        )

        if workflow.stage != WorkflowStage.REJECTED:
            raise WorkflowApprovalStateError(
                (
                    "Chỉ Workflow ở trạng thái "
                    f"'{WorkflowStage.REJECTED.value}' "
                    "mới được đưa trở lại DRAFTING."
                )
            )

        event = self.workflow_service.transition(
            workflow_id,
            WorkflowStage.DRAFTING,
            actor=actor,
            note=note,
            metadata=metadata,
        )

        self.workflow_service.update_metadata(
            workflow_id,
            {
                "approval_status": "revision_required",
                "returned_to_drafting_by": actor,
                "revision_note": note,
            },
        )

        return WorkflowApprovalResult(
            workflow_id=workflow_id,
            stage=WorkflowStage.DRAFTING,
            actor=actor,
            action="return_to_drafting",
            note=note,
            event=event,
            metadata={
                "approval_status": "revision_required",
                "returned_to_drafting_by": actor,
            },
        )