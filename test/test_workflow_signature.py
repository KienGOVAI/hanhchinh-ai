"""
Sprint 16.6.1 - Workflow Signature Service Tests.
"""

import pytest

from app.workflow import (
    WorkflowService,
    WorkflowSignatureService,
    WorkflowSignatureStateError,
    WorkflowSignatureValidationError,
    WorkflowStage,
)


@pytest.fixture
def workflow_service() -> WorkflowService:
    return WorkflowService()


@pytest.fixture
def signature_service(
    workflow_service: WorkflowService,
) -> WorkflowSignatureService:
    return WorkflowSignatureService(
        workflow_service
    )


def create_approved_workflow(
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

    service.transition(
        workflow.workflow_id,
        WorkflowStage.PENDING_APPROVAL,
        actor="officer-001",
    )

    service.transition(
        workflow.workflow_id,
        WorkflowStage.APPROVED,
        actor="manager-001",
        note="Đồng ý phê duyệt.",
    )

    service.update_metadata(
        workflow.workflow_id,
        {
            "draft_file_name": (
                "du_thao_cong_van.docx"
            ),
            "draft_content": (
                "Nội dung văn bản đã được duyệt."
            ),
        },
    )

    return workflow


# ============================================================
# 1. CONTRACT
# ============================================================


def test_signature_service_contract(
    workflow_service: WorkflowService,
) -> None:
    service = WorkflowSignatureService(
        workflow_service
    )

    assert service.workflow_service is (
        workflow_service
    )


# ============================================================
# 2. SUBMIT FOR SIGNATURE
# ============================================================


def test_submit_for_signature(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    result = (
        signature_service.submit_for_signature(
            workflow.workflow_id,
            actor="officer-001",
            note="Trình lãnh đạo ký.",
        )
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.workflow_id == (
        workflow.workflow_id
    )

    assert result.action == (
        "submit_for_signature"
    )

    assert result.stage == (
        WorkflowStage.PENDING_SIGNATURE
    )

    assert stored.stage == (
        WorkflowStage.PENDING_SIGNATURE
    )

    assert stored.metadata[
        "signature_status"
    ] == "pending"

    assert stored.metadata[
        "submitted_for_signature_by"
    ] == "officer-001"


# ============================================================
# 3. SIGN
# ============================================================


def test_sign_workflow(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="officer-001",
    )

    result = signature_service.sign(
        workflow.workflow_id,
        actor="leader-001",
        note="Đã ký văn bản.",
        signature_id="SIG-2026-0001",
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.action == "sign"

    assert result.stage == (
        WorkflowStage.SIGNED
    )

    assert stored.stage == (
        WorkflowStage.SIGNED
    )

    assert stored.metadata[
        "signature_status"
    ] == "signed"

    assert stored.metadata[
        "signed_by"
    ] == "leader-001"

    assert stored.metadata[
        "signature_id"
    ] == "SIG-2026-0001"

    assert stored.metadata[
        "signature_note"
    ] == "Đã ký văn bản."


# ============================================================
# 4. CANNOT SUBMIT BEFORE APPROVAL
# ============================================================


def test_cannot_submit_for_signature_before_approval(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = workflow_service.create(
        title="Hồ sơ mới",
        document_type="cong_van",
        created_by="user-001",
    )

    with pytest.raises(
        WorkflowSignatureStateError
    ):
        signature_service.submit_for_signature(
            workflow.workflow_id,
            actor="officer-001",
        )


# ============================================================
# 5. CANNOT SIGN BEFORE SUBMISSION
# ============================================================


def test_cannot_sign_before_pending_signature(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    with pytest.raises(
        WorkflowSignatureStateError
    ):
        signature_service.sign(
            workflow.workflow_id,
            actor="leader-001",
        )


# ============================================================
# 6. ACTOR VALIDATION
# ============================================================


def test_signature_actor_required(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    with pytest.raises(
        WorkflowSignatureValidationError
    ):
        signature_service.submit_for_signature(
            workflow.workflow_id,
            actor="   ",
        )


# ============================================================
# 7. SIGNATURE ID VALIDATION
# ============================================================


def test_signature_id_cannot_be_blank(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="officer-001",
    )

    with pytest.raises(
        WorkflowSignatureValidationError
    ):
        signature_service.sign(
            workflow.workflow_id,
            actor="leader-001",
            signature_id="   ",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.PENDING_SIGNATURE
    )


# ============================================================
# 8. SIGNATURE METADATA
# ============================================================


def test_signature_metadata(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="officer-001",
    )

    result = signature_service.sign(
        workflow.workflow_id,
        actor="leader-001",
        signature_id="SIG-ABC",
        metadata={
            "certificate_serial": "CERT-001",
            "signature_provider": "internal",
        },
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.metadata[
        "certificate_serial"
    ] == "CERT-001"

    assert result.metadata[
        "signature_provider"
    ] == "internal"

    assert stored.metadata[
        "certificate_serial"
    ] == "CERT-001"

    assert stored.metadata[
        "signature_provider"
    ] == "internal"


# ============================================================
# 9. IS SIGNED
# ============================================================


def test_is_signed(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    assert (
        signature_service.is_signed(
            workflow.workflow_id
        )
        is False
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="officer-001",
    )

    assert (
        signature_service.is_signed(
            workflow.workflow_id
        )
        is False
    )

    signature_service.sign(
        workflow.workflow_id,
        actor="leader-001",
    )

    assert (
        signature_service.is_signed(
            workflow.workflow_id
        )
        is True
    )


# ============================================================
# 10. HISTORY
# ============================================================


def test_signature_history_is_preserved(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="officer-001",
        note="Trình ký.",
    )

    signature_service.sign(
        workflow.workflow_id,
        actor="leader-001",
        note="Đã ký.",
        signature_id="SIG-001",
    )

    history = workflow_service.history(
        workflow.workflow_id
    )

    assert len(history) == 6

    assert history[4].from_stage == (
        WorkflowStage.APPROVED
    )

    assert history[4].to_stage == (
        WorkflowStage.PENDING_SIGNATURE
    )

    assert history[4].actor == (
        "officer-001"
    )

    assert history[5].from_stage == (
        WorkflowStage.PENDING_SIGNATURE
    )

    assert history[5].to_stage == (
        WorkflowStage.SIGNED
    )

    assert history[5].actor == (
        "leader-001"
    )

    assert history[5].metadata[
        "signature_id"
    ] == "SIG-001"


# ============================================================
# 11. SIGNED CHECK
# ============================================================


def test_is_signed_after_signing(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="officer-001",
    )

    signature_service.sign(
        workflow.workflow_id,
        actor="leader-001",
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.SIGNED
    )

    assert signature_service.is_signed(
        workflow.workflow_id
    )


# ============================================================
# 12. DOUBLE SIGN PROTECTION
# ============================================================


def test_cannot_sign_twice(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="officer-001",
    )

    signature_service.sign(
        workflow.workflow_id,
        actor="leader-001",
    )

    with pytest.raises(
        WorkflowSignatureStateError
    ):
        signature_service.sign(
            workflow.workflow_id,
            actor="leader-002",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.SIGNED
    )


# ============================================================
# 13. CUSTOM EVENT METADATA
# ============================================================


def test_signature_event_metadata(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="officer-001",
        metadata={
            "signing_method": "electronic",
        },
    )

    history = workflow_service.history(
        workflow.workflow_id
    )

    event = history[-1]

    assert event.metadata[
        "signing_method"
    ] == "electronic"