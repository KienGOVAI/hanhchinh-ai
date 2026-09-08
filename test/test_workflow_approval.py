"""
Sprint 16.5 - Workflow Approval Service Tests.
"""

import pytest

from app.workflow import (
    WorkflowApprovalService,
    WorkflowApprovalStateError,
    WorkflowApprovalValidationError,
    WorkflowService,
    WorkflowStage,
)


@pytest.fixture
def workflow_service() -> WorkflowService:
    return WorkflowService()


@pytest.fixture
def approval_service(
    workflow_service: WorkflowService,
) -> WorkflowApprovalService:
    return WorkflowApprovalService(
        workflow_service
    )


def create_draft(
    service: WorkflowService,
):
    workflow = service.create(
        title="Công văn chuyển đổi số",
        document_type="cong_van",
        created_by="user-001",
    )

    service.transition(
        workflow.workflow_id,
        WorkflowStage.AI_PROCESSING,
        actor="system",
    )

    service.transition(
        workflow.workflow_id,
        WorkflowStage.DRAFTING,
        actor="ai",
    )

    service.update_metadata(
        workflow.workflow_id,
        {
            "draft_file_name": (
                "du_thao_cong_van.docx"
            ),
            "draft_content": (
                "Nội dung dự thảo."
            ),
        },
    )

    return workflow


# ============================================================
# 1. CONTRACT
# ============================================================


def test_approval_service_contract(
    workflow_service: WorkflowService,
) -> None:
    service = WorkflowApprovalService(
        workflow_service
    )

    assert service.workflow_service is (
        workflow_service
    )


# ============================================================
# 2. SUBMIT
# ============================================================


def test_submit_for_approval(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = create_draft(
        workflow_service
    )

    result = (
        approval_service.submit_for_approval(
            workflow.workflow_id,
            actor="officer-001",
            note="Kính trình lãnh đạo duyệt.",
        )
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.workflow_id == (
        workflow.workflow_id
    )

    assert result.action == (
        "submit_for_approval"
    )

    assert result.stage == (
        WorkflowStage.PENDING_APPROVAL
    )

    assert stored.stage == (
        WorkflowStage.PENDING_APPROVAL
    )

    assert stored.metadata[
        "approval_status"
    ] == "pending"

    assert stored.metadata[
        "submitted_for_approval_by"
    ] == "officer-001"


# ============================================================
# 3. APPROVE
# ============================================================


def test_approve_workflow(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = create_draft(
        workflow_service
    )

    approval_service.submit_for_approval(
        workflow.workflow_id,
        actor="officer-001",
    )

    result = approval_service.approve(
        workflow.workflow_id,
        actor="manager-001",
        note="Đồng ý phê duyệt.",
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.action == "approve"

    assert result.stage == (
        WorkflowStage.APPROVED
    )

    assert stored.stage == (
        WorkflowStage.APPROVED
    )

    assert stored.metadata[
        "approval_status"
    ] == "approved"

    assert stored.metadata[
        "approved_by"
    ] == "manager-001"

    assert stored.metadata[
        "approval_note"
    ] == "Đồng ý phê duyệt."


# ============================================================
# 4. REJECT
# ============================================================


def test_reject_workflow(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = create_draft(
        workflow_service
    )

    approval_service.submit_for_approval(
        workflow.workflow_id,
        actor="officer-001",
    )

    result = approval_service.reject(
        workflow.workflow_id,
        actor="manager-001",
        reason=(
            "Bổ sung căn cứ pháp lý "
            "trước khi trình duyệt."
        ),
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.action == "reject"

    assert result.stage == (
        WorkflowStage.REJECTED
    )

    assert stored.stage == (
        WorkflowStage.REJECTED
    )

    assert stored.metadata[
        "approval_status"
    ] == "rejected"

    assert stored.metadata[
        "rejected_by"
    ] == "manager-001"

    assert stored.metadata[
        "rejection_reason"
    ] == (
        "Bổ sung căn cứ pháp lý "
        "trước khi trình duyệt."
    )


# ============================================================
# 5. RETURN TO DRAFTING
# ============================================================


def test_return_rejected_to_drafting(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = create_draft(
        workflow_service
    )

    approval_service.submit_for_approval(
        workflow.workflow_id,
        actor="officer-001",
    )

    approval_service.reject(
        workflow.workflow_id,
        actor="manager-001",
        reason="Cần bổ sung nội dung.",
    )

    result = (
        approval_service.return_to_drafting(
            workflow.workflow_id,
            actor="officer-001",
            note="Đã bổ sung nội dung theo yêu cầu.",
        )
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.action == (
        "return_to_drafting"
    )

    assert result.stage == (
        WorkflowStage.DRAFTING
    )

    assert stored.stage == (
        WorkflowStage.DRAFTING
    )

    assert stored.metadata[
        "approval_status"
    ] == "revision_required"

    assert stored.metadata[
        "returned_to_drafting_by"
    ] == "officer-001"


# ============================================================
# 6. INVALID SUBMIT
# ============================================================


def test_cannot_submit_non_draft(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = workflow_service.create(
        title="Hồ sơ mới",
        document_type="cong_van",
        created_by="user-001",
    )

    with pytest.raises(
        WorkflowApprovalStateError
    ):
        approval_service.submit_for_approval(
            workflow.workflow_id,
            actor="officer-001",
        )


# ============================================================
# 7. INVALID APPROVE
# ============================================================


def test_cannot_approve_before_submission(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = create_draft(
        workflow_service
    )

    with pytest.raises(
        WorkflowApprovalStateError
    ):
        approval_service.approve(
            workflow.workflow_id,
            actor="manager-001",
        )


# ============================================================
# 8. INVALID REJECT
# ============================================================


def test_cannot_reject_before_submission(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = create_draft(
        workflow_service
    )

    with pytest.raises(
        WorkflowApprovalStateError
    ):
        approval_service.reject(
            workflow.workflow_id,
            actor="manager-001",
            reason="Không đồng ý.",
        )


# ============================================================
# 9. REJECT REQUIRES REASON
# ============================================================


def test_reject_requires_reason(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = create_draft(
        workflow_service
    )

    approval_service.submit_for_approval(
        workflow.workflow_id,
        actor="officer-001",
    )

    with pytest.raises(
        WorkflowApprovalValidationError
    ):
        approval_service.reject(
            workflow.workflow_id,
            actor="manager-001",
            reason="   ",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.PENDING_APPROVAL
    )


# ============================================================
# 10. RETURN REJECTED REQUIRES NOTE
# ============================================================


def test_return_to_drafting_requires_note(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = create_draft(
        workflow_service
    )

    approval_service.submit_for_approval(
        workflow.workflow_id,
        actor="officer-001",
    )

    approval_service.reject(
        workflow.workflow_id,
        actor="manager-001",
        reason="Cần chỉnh sửa.",
    )

    with pytest.raises(
        WorkflowApprovalValidationError
    ):
        approval_service.return_to_drafting(
            workflow.workflow_id,
            actor="officer-001",
            note="   ",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.REJECTED
    )


# ============================================================
# 11. HISTORY
# ============================================================


def test_approval_history_is_preserved(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = create_draft(
        workflow_service
    )

    approval_service.submit_for_approval(
        workflow.workflow_id,
        actor="officer-001",
        note="Trình duyệt.",
    )

    approval_service.reject(
        workflow.workflow_id,
        actor="manager-001",
        reason="Thiếu căn cứ.",
    )

    approval_service.return_to_drafting(
        workflow.workflow_id,
        actor="officer-001",
        note="Đã bổ sung căn cứ.",
    )

    history = workflow_service.history(
        workflow.workflow_id
    )

    assert len(history) == 5

    assert history[2].from_stage == (
        WorkflowStage.DRAFTING
    )

    assert history[2].to_stage == (
        WorkflowStage.PENDING_APPROVAL
    )

    assert history[3].from_stage == (
        WorkflowStage.PENDING_APPROVAL
    )

    assert history[3].to_stage == (
        WorkflowStage.REJECTED
    )

    assert history[4].from_stage == (
        WorkflowStage.REJECTED
    )

    assert history[4].to_stage == (
        WorkflowStage.DRAFTING
    )


# ============================================================
# 12. DOUBLE APPROVAL / REJECTION PROTECTION
# ============================================================


def test_approval_decision_can_only_be_made_once(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = create_draft(
        workflow_service
    )

    approval_service.submit_for_approval(
        workflow.workflow_id,
        actor="officer-001",
    )

    approval_service.approve(
        workflow.workflow_id,
        actor="manager-001",
    )

    with pytest.raises(
        WorkflowApprovalStateError
    ):
        approval_service.approve(
            workflow.workflow_id,
            actor="manager-002",
        )

    with pytest.raises(
        WorkflowApprovalStateError
    ):
        approval_service.reject(
            workflow.workflow_id,
            actor="manager-002",
            reason="Từ chối.",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.APPROVED
    )


# ============================================================
# 13. METADATA
# ============================================================


def test_approval_metadata(
    workflow_service: WorkflowService,
    approval_service: WorkflowApprovalService,
) -> None:
    workflow = create_draft(
        workflow_service
    )

    approval_service.submit_for_approval(
        workflow.workflow_id,
        actor="officer-001",
        metadata={
            "department": "VP",
        },
    )

    history = workflow_service.history(
        workflow.workflow_id
    )

    event = history[-1]

    assert event.metadata[
        "department"
    ] == "VP"