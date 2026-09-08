"""
Sprint 16.6.4 - Workflow Signature → Export Hardening Tests.

Mục tiêu:
- Khóa state transition.
- Không cho ký sai trạng thái.
- Không cho export sai trạng thái.
- Bảo toàn metadata.
- Bảo toàn history.
- Chống double action.
- Kiểm tra Integration pipeline.
"""

import pytest

from app.workflow import (
    WorkflowExportService,
    WorkflowExportStateError,
    WorkflowExportValidationError,
    WorkflowService,
    WorkflowSignatureError,
    WorkflowSignatureExportService,
    WorkflowSignatureExportStateError,
    WorkflowSignatureExportValidationError,
    WorkflowSignatureService,
    WorkflowSignatureStateError,
    WorkflowSignatureValidationError,
    WorkflowStage,
)


# ============================================================
# FIXTURES
# ============================================================


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


# ============================================================
# HELPERS
# ============================================================


def create_workflow(
    service: WorkflowService,
):
    return service.create(
        title="Hồ sơ kiểm thử Workflow 16.6",
        document_type="cong_van",
        created_by="user-001",
    )


def move_to_stage(
    service: WorkflowService,
    workflow_id: str,
    stage: WorkflowStage,
):
    """
    Đưa Workflow đến stage yêu cầu thông qua
    các transition hợp lệ.
    """

    current = service.get(
        workflow_id
    ).stage

    sequence = [
        WorkflowStage.RECEIVED,
        WorkflowStage.AI_PROCESSING,
        WorkflowStage.DRAFTING,
        WorkflowStage.PENDING_APPROVAL,
        WorkflowStage.APPROVED,
        WorkflowStage.PENDING_SIGNATURE,
        WorkflowStage.SIGNED,
        WorkflowStage.EXPORTED,
    ]

    current_index = sequence.index(current)
    target_index = sequence.index(stage)

    actors = {
        WorkflowStage.AI_PROCESSING: "system",
        WorkflowStage.DRAFTING: "ai",
        WorkflowStage.PENDING_APPROVAL: "officer",
        WorkflowStage.APPROVED: "manager",
        WorkflowStage.PENDING_SIGNATURE: "clerk",
        WorkflowStage.SIGNED: "leader",
        WorkflowStage.EXPORTED: "system",
    }

    for next_stage in sequence[
        current_index + 1 : target_index + 1
    ]:
        service.transition(
            workflow_id,
            next_stage,
            actor=actors[next_stage],
        )

    return service.get(
        workflow_id
    )


def create_approved_workflow(
    service: WorkflowService,
):
    workflow = create_workflow(
        service
    )

    move_to_stage(
        service,
        workflow.workflow_id,
        WorkflowStage.APPROVED,
    )

    service.update_metadata(
        workflow.workflow_id,
        {
            "draft_file_name": (
                "du_thao_hardening.docx"
            ),
            "draft_content": (
                "Nội dung văn bản hardening."
            ),
            "business_key": "HS-16-6-TEST",
        },
    )

    return service.get(
        workflow.workflow_id
    )


def create_signed_workflow(
    service: WorkflowService,
):
    workflow = create_approved_workflow(
        service
    )

    signature_service = WorkflowSignatureService(
        service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="clerk-001",
        note="Trình ký.",
    )

    signature_service.sign(
        workflow.workflow_id,
        actor="leader-001",
        signature_id="SIG-HARDENING",
        note="Đã ký.",
    )

    return service.get(
        workflow.workflow_id
    )


# ============================================================
# 1. SIGNATURE SERVICE REJECTS NON-APPROVED
# ============================================================


def test_signature_requires_approved_state(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_workflow(
        workflow_service
    )

    with pytest.raises(
        WorkflowSignatureStateError
    ):
        signature_service.submit_for_signature(
            workflow.workflow_id,
            actor="clerk-001",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.RECEIVED
    )


# ============================================================
# 2. SIGNATURE CANNOT BYPASS PENDING_SIGNATURE
# ============================================================


def test_signature_cannot_bypass_pending_signature(
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

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.APPROVED
    )


# ============================================================
# 3. EXPORT REQUIRES SIGNED
# ============================================================


def test_export_requires_signed_state(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    with pytest.raises(
        WorkflowExportStateError
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
        WorkflowStage.APPROVED
    )


# ============================================================
# 4. EXPORT CANNOT BYPASS SIGNATURE
# ============================================================


def test_export_cannot_bypass_signature(
    workflow_service: WorkflowService,
    export_service: WorkflowExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    history_before = len(
        workflow_service.history(
            workflow.workflow_id
        )
    )

    with pytest.raises(
        WorkflowExportStateError
    ):
        export_service.export(
            workflow.workflow_id,
            actor="system",
            file_name="final.docx",
        )

    history_after = len(
        workflow_service.history(
            workflow.workflow_id
        )
    )

    assert history_after == history_before


# ============================================================
# 5. DOUBLE SIGN IS BLOCKED
# ============================================================


def test_double_sign_is_blocked(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="clerk-001",
    )

    signature_service.sign(
        workflow.workflow_id,
        actor="leader-001",
        signature_id="SIG-001",
    )

    with pytest.raises(
        WorkflowSignatureStateError
    ):
        signature_service.sign(
            workflow.workflow_id,
            actor="leader-002",
            signature_id="SIG-002",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.SIGNED
    )

    assert stored.metadata[
        "signature_id"
    ] == "SIG-001"


# ============================================================
# 6. DOUBLE EXPORT IS BLOCKED
# ============================================================


def test_double_export_is_blocked(
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
# 7. INVALID SIGNATURE ID DOES NOT CHANGE STATE
# ============================================================


def test_invalid_signature_id_does_not_change_state(
    workflow_service: WorkflowService,
    signature_service: WorkflowSignatureService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="clerk-001",
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

    assert stored.metadata[
        "signature_status"
    ] == "pending"


# ============================================================
# 8. MISSING DOCUMENT CONTENT BLOCKS EXPORT
# ============================================================


def test_missing_document_content_blocks_export(
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

    history_before = len(
        workflow_service.history(
            workflow.workflow_id
        )
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

    history_after = len(
        workflow_service.history(
            workflow.workflow_id
        )
    )

    assert stored.stage == (
        WorkflowStage.SIGNED
    )

    assert history_after == history_before


# ============================================================
# 9. METADATA SURVIVES SIGNATURE → EXPORT
# ============================================================


def test_metadata_survives_full_pipeline(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="leader-001",
        exported_by="system",
        signature_id="SIG-META",
        file_name="final.docx",
        metadata={
            "priority": "high",
            "department": "van-phong",
            "source": "workflow-test",
        },
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.metadata[
        "business_key"
    ] == "HS-16-6-TEST"

    assert stored.metadata[
        "priority"
    ] == "high"

    assert stored.metadata[
        "department"
    ] == "van-phong"

    assert stored.metadata[
        "source"
    ] == "workflow-test"

    assert stored.metadata[
        "signature_id"
    ] == "SIG-META"

    assert stored.metadata[
        "export_file_name"
    ] == "final.docx"


# ============================================================
# 10. COMPLETE HISTORY IS PRESERVED
# ============================================================


def test_complete_signature_export_history(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="leader-001",
        exported_by="system",
        signature_id="SIG-HISTORY",
        file_name="final.docx",
    )

    history = workflow_service.history(
        workflow.workflow_id
    )

    assert len(history) == 7

    assert history[-3].from_stage == (
        WorkflowStage.APPROVED
    )

    assert history[-3].to_stage == (
        WorkflowStage.PENDING_SIGNATURE
    )

    assert history[-3].actor == (
        "clerk-001"
    )

    assert history[-2].from_stage == (
        WorkflowStage.PENDING_SIGNATURE
    )

    assert history[-2].to_stage == (
        WorkflowStage.SIGNED
    )

    assert history[-2].actor == (
        "leader-001"
    )

    assert history[-2].metadata[
        "signature_id"
    ] == "SIG-HISTORY"

    assert history[-1].from_stage == (
        WorkflowStage.SIGNED
    )

    assert history[-1].to_stage == (
        WorkflowStage.EXPORTED
    )

    assert history[-1].actor == "system"

    assert history[-1].metadata[
        "export_file_name"
    ] == "final.docx"


# ============================================================
# 11. ACTOR VALIDATION
# ============================================================


def test_all_pipeline_actors_are_required(
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
            requested_by="clerk-001",
            signed_by=" ",
            exported_by="system",
            file_name="final.docx",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.APPROVED
    )


# ============================================================
# 12. PIPELINE MUST FINISH AT EXPORTED
# ============================================================


def test_pipeline_final_state_is_exported(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    result = integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="leader-001",
        exported_by="system",
        file_name="final.docx",
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.stage == (
        WorkflowStage.EXPORTED
    )

    assert stored.stage == (
        WorkflowStage.EXPORTED
    )

    assert integration_service.is_completed(
        workflow.workflow_id
    )


# ============================================================
# 13. INTEGRATION CANNOT RUN TWICE
# ============================================================


def test_integration_cannot_run_twice(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-001",
        signed_by="leader-001",
        exported_by="system",
        signature_id="SIG-FIRST",
        file_name="first.docx",
    )

    with pytest.raises(
        WorkflowSignatureExportStateError
    ):
        integration_service.sign_and_export(
            workflow.workflow_id,
            requested_by="clerk-002",
            signed_by="leader-002",
            exported_by="system",
            signature_id="SIG-SECOND",
            file_name="second.docx",
        )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert stored.stage == (
        WorkflowStage.EXPORTED
    )

    assert stored.metadata[
        "signature_id"
    ] == "SIG-FIRST"

    assert stored.metadata[
        "export_file_name"
    ] == "first.docx"


# ============================================================
# 14. FINAL BUSINESS CONTRACT
# ============================================================


def test_final_signature_export_business_contract(
    workflow_service: WorkflowService,
    integration_service: WorkflowSignatureExportService,
) -> None:
    workflow = create_approved_workflow(
        workflow_service
    )

    result = integration_service.sign_and_export(
        workflow.workflow_id,
        requested_by="clerk-final",
        signed_by="leader-final",
        exported_by="system-final",
        signature_id="SIG-FINAL",
        file_name="van_ban_final.docx",
        file_path="output/van_ban_final.docx",
        signature_note="Đã trình ký.",
        export_note="Đã xuất văn bản.",
        metadata={
            "final_check": True,
        },
    )

    stored = workflow_service.get(
        workflow.workflow_id
    )

    assert result.stage == (
        WorkflowStage.EXPORTED
    )

    assert result.file_name == (
        "van_ban_final.docx"
    )

    assert result.file_path == (
        "output/van_ban_final.docx"
    )

    assert result.signature_id == (
        "SIG-FINAL"
    )

    assert result.metadata[
        "final_check"
    ] is True

    assert stored.metadata[
        "signature_status"
    ] == "signed"

    assert stored.metadata[
        "export_status"
    ] == "exported"

    assert stored.metadata[
        "requested_by"
    ] == "clerk-final"

    assert stored.metadata[
        "signed_by"
    ] == "leader-final"

    assert stored.metadata[
        "exported_by"
    ] == "system-final"

    assert stored.metadata[
        "signature_id"
    ] == "SIG-FINAL"

    assert stored.metadata[
        "export_file_name"
    ] == "van_ban_final.docx"

    assert stored.metadata[
        "export_file_path"
    ] == "output/van_ban_final.docx"