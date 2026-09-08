"""
Sprint 16.2 - Workflow Service Tests.
"""

import pytest

from app.workflow import (
    WorkflowService,
    WorkflowStage,
    WorkflowTransitionError,
)


@pytest.fixture
def service() -> WorkflowService:
    return WorkflowService()


def create_workflow(
    service: WorkflowService,
):
    return service.create(
        title="Công văn chuyển đổi số",
        document_type="cong_van",
        created_by="user-001",
    )


def test_create_workflow(
    service: WorkflowService,
) -> None:
    workflow = create_workflow(
        service
    )

    assert workflow.workflow_id
    assert workflow.title == (
        "Công văn chuyển đổi số"
    )
    assert workflow.document_type == (
        "cong_van"
    )
    assert workflow.created_by == (
        "user-001"
    )
    assert workflow.stage == (
        WorkflowStage.RECEIVED
    )

    assert service.exists(
        workflow.workflow_id
    )

    assert service.count() == 1


def test_get_and_list_workflow(
    service: WorkflowService,
) -> None:
    workflow_1 = service.create(
        title="Công văn 01",
        document_type="cong_van",
        created_by="user-001",
    )

    workflow_2 = service.create(
        title="Tờ trình 02",
        document_type="to_trinh",
        created_by="user-002",
    )

    assert service.get(
        workflow_1.workflow_id
    ) is workflow_1

    assert service.get(
        workflow_2.workflow_id
    ) is workflow_2

    workflows = service.list()

    assert len(workflows) == 2
    assert workflow_1 in workflows
    assert workflow_2 in workflows

    assert service.count() == 2

    assert service.count(
        stage=WorkflowStage.RECEIVED
    ) == 2


def test_transition_workflow(
    service: WorkflowService,
) -> None:
    workflow = create_workflow(
        service
    )

    event = service.transition(
        workflow.workflow_id,
        WorkflowStage.AI_PROCESSING,
        actor="system",
        note="AI bắt đầu xử lý.",
    )

    assert event.from_stage == (
        WorkflowStage.RECEIVED
    )
    assert event.to_stage == (
        WorkflowStage.AI_PROCESSING
    )
    assert event.actor == "system"

    assert workflow.stage == (
        WorkflowStage.AI_PROCESSING
    )

    assert service.count(
        stage=WorkflowStage.AI_PROCESSING
    ) == 1


def test_full_workflow_through_service(
    service: WorkflowService,
) -> None:
    workflow = create_workflow(
        service
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
        actor="officer",
    )

    service.transition(
        workflow.workflow_id,
        WorkflowStage.APPROVED,
        actor="manager",
    )

    service.transition(
        workflow.workflow_id,
        WorkflowStage.PENDING_SIGNATURE,
        actor="officer",
    )

    service.transition(
        workflow.workflow_id,
        WorkflowStage.SIGNED,
        actor="leader",
    )

    service.transition(
        workflow.workflow_id,
        WorkflowStage.EXPORTED,
        actor="system",
        metadata={
            "filename": "cong_van.docx",
        },
    )

    assert workflow.stage == (
        WorkflowStage.EXPORTED
    )

    assert workflow.is_completed is True

    assert service.count() == 1

    assert service.count(
        stage=WorkflowStage.EXPORTED
    ) == 1


def test_rejected_workflow_returns_to_drafting(
    service: WorkflowService,
) -> None:
    workflow = create_workflow(
        service
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
        actor="officer",
    )

    service.transition(
        workflow.workflow_id,
        WorkflowStage.REJECTED,
        actor="manager",
        note="Thiếu căn cứ pháp lý.",
    )

    assert workflow.stage == (
        WorkflowStage.REJECTED
    )

    service.transition(
        workflow.workflow_id,
        WorkflowStage.DRAFTING,
        actor="officer",
        note="Đã bổ sung căn cứ.",
    )

    assert workflow.stage == (
        WorkflowStage.DRAFTING
    )


def test_history_is_recorded(
    service: WorkflowService,
) -> None:
    workflow = create_workflow(
        service
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

    history = service.history(
        workflow.workflow_id
    )

    assert len(history) == 2

    assert history[0].from_stage == (
        WorkflowStage.RECEIVED
    )

    assert history[0].to_stage == (
        WorkflowStage.AI_PROCESSING
    )

    assert history[1].from_stage == (
        WorkflowStage.AI_PROCESSING
    )

    assert history[1].to_stage == (
        WorkflowStage.DRAFTING
    )


def test_invalid_transition_and_missing_workflow(
    service: WorkflowService,
) -> None:
    workflow = create_workflow(
        service
    )

    with pytest.raises(
        WorkflowTransitionError
    ):
        service.transition(
            workflow.workflow_id,
            WorkflowStage.APPROVED,
            actor="manager",
        )

    with pytest.raises(ValueError):
        service.get(
            "workflow-does-not-exist"
        )

    with pytest.raises(ValueError):
        service.history(
            "workflow-does-not-exist"
        )


def test_metadata_and_delete(
    service: WorkflowService,
) -> None:
    workflow = service.create(
        title="Công văn metadata",
        document_type="cong_van",
        created_by="user-001",
        metadata={
            "priority": "high",
        },
    )

    assert workflow.metadata["priority"] == "high"

    service.update_metadata(
        workflow.workflow_id,
        {
            "department": "VP",
            "year": 2026,
        },
    )

    assert workflow.metadata["department"] == "VP"
    assert workflow.metadata["year"] == 2026

    deleted = service.delete(
        workflow.workflow_id
    )

    assert deleted is workflow
    assert service.exists(
        workflow.workflow_id
    ) is False

    assert service.count() == 0

    with pytest.raises(ValueError):
        service.delete(
            workflow.workflow_id
        )