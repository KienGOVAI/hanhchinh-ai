"""
Sprint 16.6.3 - Signature → Export Integration Tests.
"""

import pytest

from app.workflow import (
    WorkflowExportService,
    WorkflowService,
    WorkflowSignatureExportService,
    WorkflowSignatureExportStateError,
    WorkflowSignatureExportValidationError,
    WorkflowSignatureService,
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


@pytest.fixture
def export_service(
    workflow_service: WorkflowService,
) -> WorkflowExportService:
    return WorkflowExportService(
        workflow_service
    )


@pytest.fixture
def integration_service(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
    export_service: WorkflowExportService,
) -> WorkflowSignatureExportService:
    return WorkflowSignatureExportService(
        workflow_service,
        signature_service,
        export_service,
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
        note="Đã phê duyệt.",
    )

    service.update_metadata(
        workflow.workflow_id,
        {
            "draft_file_name": (
                "du_thao_cong_van.docx"
            ),
            "draft_content": (
                "Nội dung văn bản chính thức."
            ),
        },
    )

    return workflow


# ============================================================
# 1. CONTRACT
# ============================================================


def test_integration_service_contract(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
    export_service: WorkflowExportService,
) -> None:
    service = WorkflowSignatureExportService(
        workflow_service,
        signature_service,
        export_service,
    )

    assert service.workflow_service is (
        workflow_service
    )

    assert service.signature_service is (
        signature_service
    )

    assert service.export_service is (
        export_service
    )


# ============================================================
# 2. FULL SIGN → EXPORT PIPELINE
# ============================================================


def test_sign_and_export_pipeline(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    result = integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="officer-001",
        signed_by="leader-001",
        exported_by="system",
        signature_id="SIG-2026-0001",
        file_name="cong_van_final.docx",
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.workflow_id == (
        workflow.workflow_id
    )

    assert result.stage == (
        WorkflowStage.EXPORTED
    )

    assert result.requested_by == (
        "officer-001"
    )

    assert result.signed_by == (
        "leader-001"
    )

    assert result.exported_by == (
        "system"
    )

    assert result.file_name == (
        "cong_van_final.docx"
    )

    assert result.signature_id == (
        "SIG-2026-0001"
    )

    assert stored.stage == (
        WorkflowStage.EXPORTED
    )


# ============================================================
# 3. STATE SEQUENCE
# ============================================================


def test_full_state_sequence(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="officer-001",
        signed_by="leader-001",
        exported_by="system",
        signature_id="SIG-001",
        file_name="final.docx",
    )

    history = workflow_service.history(
        workflow.workflow_id
    )

    assert history[-3].from_stage == (
        WorkflowStage.APPROVED
    )

    assert history[-3].to_stage == (
        WorkflowStage.PENDING_SIGNATURE
    )

    assert history[-2].from_stage == (
        WorkflowStage.PENDING_SIGNATURE
    )

    assert history[-2].to_stage == (
        WorkflowStage.SIGNED
    )

    assert history[-1].from_stage == (
        WorkflowStage.SIGNED
    )

    assert history[-1].to_stage == (
        WorkflowStage.EXPORTED
    )


# ============================================================
# 4. SIGNATURE ACTOR
# ============================================================


def test_signature_actor_is_preserved(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    result = integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="director-001",
        exported_by="system",
        file_name="final.docx",
    )

    assert result.requested_by == (
        "clerk-001"
    )

    assert result.signed_by == (
        "director-001"
    )

    assert result.metadata[
        "signed_by"
    ] == "director-001"


# ============================================================
# 5. EXPORT ACTOR
# ============================================================


def test_export_actor_is_preserved(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    result = integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="director-001",
        exported_by="export-worker",
        file_name="final.docx",
    )

    assert result.exported_by == (
        "export-worker"
    )

    assert result.metadata[
        "exported_by"
    ] == "export-worker"


# ============================================================
# 6. FILE PATH
# ============================================================


def test_export_file_path(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    result = integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="director-001",
        exported_by="system",
        file_name="final.docx",
        file_path="output/final.docx",
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
# 7. CUSTOM METADATA
# ============================================================


def test_integration_metadata_is_preserved(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    result = integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="director-001",
        exported_by="system",
        signature_id="SIG-CUSTOM",
        file_name="final.docx",
        metadata={
            "certificate_serial": "CERT-001",
            "export_format": "docx",
        },
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.metadata[
        "certificate_serial"
    ] == "CERT-001"

    assert result.metadata[
        "export_format"
    ] == "docx"

    assert stored.metadata[
        "certificate_serial"
    ] == "CERT-001"

    assert stored.metadata[
        "export_format"
    ] == "docx"


# ============================================================
# 8. MUST START FROM APPROVED
# ============================================================


def test_pipeline_requires_approved_state(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = workflow_service.create(
        title="Văn bản mới",
        document_type="cong_van",
        created_by="user-001",
    )

    with pytest.raises(
        WorkflowSignatureExportStateError
    ):
        integration_service.sign_and_export(
            workflow.workflow_id,
            requested_by="clerk-001",
            signed_by="director-001",
            exported_by="system",
            file_name="final.docx",
        )


# ============================================================
# 9. ACTOR VALIDATION
# ============================================================


def test_pipeline_requires_valid_actors(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    with pytest.raises(
        WorkflowSignatureExportValidationError
    ):
        integration_service.sign_and_export(
            workflow.workflow_id,
            requested_by=" ",
            signed_by="director-001",
            exported_by="system",
            file_name="final.docx",
        )


# ============================================================
# 10. COMPLETION CHECK
# ============================================================


def test_pipeline_completion(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    assert (
        integration_service.is_completed(
            workflow.workflow_id
        )
        is False
    )

    integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="director-001",
        exported_by="system",
        file_name="final.docx",
    )

    assert (
        integration_service.is_completed(
            workflow.workflow_id
        )
        is True
    )


# ============================================================
# 11. SIGNATURE ID
# ============================================================


def test_signature_id_is_preserved(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    result = integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="director-001",
        exported_by="system",
        signature_id="SIG-ABC-123",
        file_name="final.docx",
    )

    assert result.signature_id == (
        "SIG-ABC-123"
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.metadata[
        "signature_id"
    ] == "SIG-ABC-123"


# ============================================================
# 12. FILE NAME FROM WORKFLOW
# ============================================================


def test_pipeline_uses_workflow_file_name(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    result = integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="director-001",
        exported_by="system",
    )

    assert result.file_name == (
        "du_thao_cong_van.docx"
    )


# ============================================================
# 13. FINAL METADATA
# ============================================================


def test_final_pipeline_metadata(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="director-001",
        exported_by="system",
        signature_id="SIG-FINAL",
        file_name="final.docx",
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.metadata[
        "signature_export_pipeline"
    ] is True

    assert stored.metadata[
        "signature_status"
    ] == "signed"

    assert stored.metadata[
        "export_status"
    ] == "exported"

    assert stored.metadata[
        "requested_by"
    ] == "clerk-001"

    assert stored.metadata[
        "signed_by"
    ] == "director-001"

    assert stored.metadata[
        "exported_by"
    ] == "system"

    assert stored.metadata[
        "signature_id"
    ] == "SIG-FINAL"

    assert stored.metadata[
        "export_file_name"
    ] == "final.docx"