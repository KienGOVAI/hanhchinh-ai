"""
Sprint 16.1 - Workflow Domain Tests.
"""

from app.workflow import (
    WorkflowItem,
    WorkflowStage,
    WorkflowTransitionError,
)


def create_workflow() -> WorkflowItem:
    return WorkflowItem(
        title="Công văn về chuyển đổi số",
        document_type="cong_van",
        created_by="system",
    )


def test_workflow_starts_at_received() -> None:
    workflow = create_workflow()

    assert workflow.stage == WorkflowStage.RECEIVED
    assert workflow.is_completed is False
    assert workflow.is_rejected is False
    assert workflow.events == []


def test_full_workflow_can_complete() -> None:
    workflow = create_workflow()

    workflow.start_ai(actor="system")
    assert workflow.stage == WorkflowStage.AI_PROCESSING

    workflow.start_drafting(actor="ai")
    assert workflow.stage == WorkflowStage.DRAFTING

    workflow.submit_for_approval(actor="officer")
    assert workflow.stage == WorkflowStage.PENDING_APPROVAL

    workflow.approve(actor="manager")
    assert workflow.stage == WorkflowStage.APPROVED

    workflow.submit_for_signature(actor="officer")
    assert workflow.stage == WorkflowStage.PENDING_SIGNATURE

    workflow.sign(actor="leader")
    assert workflow.stage == WorkflowStage.SIGNED

    workflow.export(
        actor="system",
        metadata={
            "filename": "cong_van.docx",
        },
    )

    assert workflow.stage == WorkflowStage.EXPORTED
    assert workflow.is_completed is True
    assert len(workflow.events) == 7


def test_rejection_can_return_to_drafting() -> None:
    workflow = create_workflow()

    workflow.start_ai(actor="system")
    workflow.start_drafting(actor="ai")
    workflow.submit_for_approval(actor="officer")

    workflow.reject(
        actor="manager",
        note="Cần bổ sung căn cứ pháp lý.",
    )

    assert workflow.stage == WorkflowStage.REJECTED
    assert workflow.is_rejected is True

    workflow.start_drafting(
        actor="officer",
        note="Đã bổ sung căn cứ.",
    )

    assert workflow.stage == WorkflowStage.DRAFTING


def test_invalid_transition_is_rejected() -> None:
    workflow = create_workflow()

    try:
        workflow.approve(actor="manager")
        raise AssertionError(
            "Workflow không được phép bỏ qua các bước."
        )
    except WorkflowTransitionError:
        pass

    assert workflow.stage == WorkflowStage.RECEIVED


def test_export_cannot_be_repeated() -> None:
    workflow = create_workflow()

    workflow.start_ai(actor="system")
    workflow.start_drafting(actor="ai")
    workflow.submit_for_approval(actor="officer")
    workflow.approve(actor="manager")
    workflow.submit_for_signature(actor="officer")
    workflow.sign(actor="leader")
    workflow.export(actor="system")

    assert workflow.is_completed is True
    assert workflow.can_transition(
        WorkflowStage.EXPORTED
    ) is False


def test_workflow_events_record_history() -> None:
    workflow = create_workflow()

    workflow.start_ai(
        actor="system",
        note="AI bắt đầu xử lý.",
    )

    event = workflow.events[-1]

    assert event.from_stage == WorkflowStage.RECEIVED
    assert event.to_stage == WorkflowStage.AI_PROCESSING
    assert event.actor == "system"
    assert event.note == "AI bắt đầu xử lý."

    assert workflow.updated_at == event.timestamp