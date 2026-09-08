"""
Sprint 16.6.2 - Workflow Export Service Tests.
"""

import pytest

from app.workflow import (
    WorkflowExportService,
    WorkflowExportStateError,
    WorkflowExportValidationError,
    WorkflowService,
    WorkflowSignatureService,
    WorkflowStage,
)


@pytest.fixture
def workflow_service() -> WorkflowService:
    return WorkflowService()


@pytest.fixture
def export_service(
    workflow_service: WorkflowService,
) -> WorkflowExportService:
    return WorkflowExportService(
        workflow_service
    )


def create_signed_workflow(
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
        note="Đã phê duyệt.",
    )

    signature_service = WorkflowSignatureService(
        service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="officer-001",
    )

    signature_service.sign(
        workflow.workflow_id,
        actor="leader-001",
        signature_id="SIG-2026-0001",
    )

    service.update_metadata(
        workflow.workflow_id,
        {
            "draft_file_name": (
                "cong_van_chuyen_doi_so.docx"
            ),
            "draft_content": (
                "Nội dung văn bản đã được duyệt "
                "và ký."
            ),
        },
    )

    return workflow


# ============================================================
# 1. CONTRACT
# ============================================================


def test_export_service_contract(
    workflow_service: WorkflowService,
) -> None:
    service = WorkflowExportService(
        workflow_service
    )

    assert service.workflow_service is (
        workflow_service
    )


# ============================================================
# 2. EXPORT SIGNED WORKFLOW
# ============================================================


def test_export_signed_workflow(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_signed_workflow(
        workflow_service
    )

    result = export_service.export(
        workflow.workflow_id,
        actor="system",
        file_name="cong_van_final.docx",
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.workflow_id == (
        workflow.workflow_id
    )

    assert result.action == "export"

    assert result.stage == (
        WorkflowStage.EXPORTED
    )

    assert result.file_name == (
        "cong_van_final.docx"
    )

    assert stored.stage == (
        WorkflowStage.EXPORTED
    )

    assert stored.metadata[
        "export_status"
    ] == "exported"

    assert stored.metadata[
        "export_file_name"
    ] == "cong_van_final.docx"

    assert stored.metadata[
        "exported_by"
    ] == "system"


# ============================================================
# 3. AUTO FILE NAME FROM DRAFT
# ============================================================


def test_export_uses_draft_file_name(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_signed_workflow(
        workflow_service
    )

    result = export_service.export(
        workflow.workflow_id,
        actor="system",
    )

    assert result.file_name == (
        "cong_van_chuyen_doi_so.docx"
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.metadata[
        "export_file_name"
    ] == "cong_van_chuyen_doi_so.docx"


# ============================================================
# 4. FILE PATH
# ============================================================


def test_export_stores_file_path(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_signed_workflow(
        workflow_service
    )

    result = export_service.export(
        workflow.workflow_id,
        actor="system",
        file_name="final.docx",
        file_path=(
            "output/final.docx"
        ),
    )

    assert result.file_path == (
        "output/final.docx"
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.metadata[
        "export_file_path"
    ] == "output/final.docx"


# ============================================================
# 5. CANNOT EXPORT BEFORE SIGNING
# ============================================================


def test_cannot_export_before_signing(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = workflow_service.create(
        title="Văn bản chưa ký",
        document_type="cong_van",
        created_by="user-001",
    )

    with pytest.raises(
        WorkflowExportStateError
    ):
        export_service.export(
            workflow.workflow_id,
            actor="system",
            file_name="final.docx",
        )


# ============================================================
# 6. DRAFT CONTENT REQUIRED
# ============================================================


def test_export_requires_draft_content(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_signed_workflow(
        workflow_service
    )

    workflow.metadata.pop(
        "draft_content",
        None,
    )

    with pytest.raises(
        WorkflowExportValidationError
    ):
        export_service.export(
            workflow.workflow_id,
            actor="system",
            file_name="final.docx",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.SIGNED
    )


# ============================================================
# 7. FILE NAME REQUIRED
# ============================================================


def test_export_requires_file_name(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_signed_workflow(
        workflow_service
    )

    workflow.metadata.pop(
        "draft_file_name",
        None,
    )

    with pytest.raises(
        WorkflowExportValidationError
    ):
        export_service.export(
            workflow.workflow_id,
            actor="system",
        )


# ============================================================
# 8. FILE NAME VALIDATION
# ============================================================


def test_export_rejects_path_traversal(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_signed_workflow(
        workflow_service
    )

    with pytest.raises(
        WorkflowExportValidationError
    ):
        export_service.export(
            workflow.workflow_id,
            actor="system",
            file_name="../final.docx",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.SIGNED
    )


# ============================================================
# 9. CUSTOM METADATA
# ============================================================


def test_export_metadata(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_signed_workflow(
        workflow_service
    )

    result = export_service.export(
        workflow.workflow_id,
        actor="system",
        file_name="final.docx",
        metadata={
            "export_format": "docx",
            "export_provider": "document_service",
        },
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.metadata[
        "export_format"
    ] == "docx"

    assert result.metadata[
        "export_provider"
    ] == "document_service"

    assert stored.metadata[
        "export_format"
    ] == "docx"

    assert stored.metadata[
        "export_provider"
    ] == "document_service"


# ============================================================
# 10. IS EXPORTED
# ============================================================


def test_is_exported(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_signed_workflow(
        workflow_service
    )

    assert (
        export_service.is_exported(
            workflow.workflow_id
        )
        is False
    )

    export_service.export(
        workflow.workflow_id,
        actor="system",
        file_name="final.docx",
    )

    assert (
        export_service.is_exported(
            workflow.workflow_id
        )
        is True
    )


# ============================================================
# 11. DOUBLE EXPORT PROTECTION
# ============================================================


def test_cannot_export_twice(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_signed_workflow(
        workflow_service
    )

    export_service.export(
        workflow.workflow_id,
        actor="system",
        file_name="final.docx",
    )

    with pytest.raises(
        WorkflowExportStateError
    ):
        export_service.export(
            workflow.workflow_id,
            actor="system",
            file_name="final-2.docx",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.EXPORTED
    )

    assert stored.metadata[
        "export_file_name"
    ] == "final.docx"


# ============================================================
# 12. HISTORY
# ============================================================


def test_export_history_is_preserved(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_signed_workflow(
        workflow_service
    )

    export_service.export(
        workflow.workflow_id,
        actor="system",
        file_name="final.docx",
        note="Xuất văn bản cuối.",
    )

    history = workflow_service.history(
        workflow.workflow_id
    )

    assert len(history) == 7

    event = history[-1]

    assert event.from_stage == (
        WorkflowStage.SIGNED
    )

    assert event.to_stage == (
        WorkflowStage.EXPORTED
    )

    assert event.actor == "system"

    assert event.note == (
        "Xuất văn bản cuối."
    )

    assert event.metadata[
        "export_file_name"
    ] == "final.docx"


# ============================================================
# 13. ACTOR VALIDATION
# ============================================================


def test_export_actor_required(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_signed_workflow(
        workflow_service
    )

    with pytest.raises(
        WorkflowExportValidationError
    ):
        export_service.export(
            workflow.workflow_id,
            actor="   ",
            file_name="final.docx",
        )