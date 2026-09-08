from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.workflow import get_workflow_service
from app.workflow.models import WorkflowStage
from app.workflow.approval_service import WorkflowApprovalService
from app.workflow.signature_service import WorkflowSignatureService
from app.workflow.export_service import WorkflowExportService
from app.workflow.signature_export_service import (
    WorkflowSignatureExportService,
)


# ============================================================
# TEST HELPERS
# ============================================================


def create_workflow():
    service = get_workflow_service()

    workflow = service.create(
        title="E2E Sprint 16.7",
        document_type="cong_van",
        created_by="e2e-test",
        metadata={
            "test": "16.7",
        },
    )

    return service, workflow


# ============================================================
# 16.7.1 — FULL WORKFLOW E2E
# ============================================================


def test_16_7_1_full_workflow_e2e():
    service, workflow = create_workflow()

    assert workflow.stage == WorkflowStage.RECEIVED

    service.transition(
        workflow.workflow_id,
        WorkflowStage.AI_PROCESSING,
        actor="ai",
        note="AI processing",
    )

    service.transition(
        workflow.workflow_id,
        WorkflowStage.DRAFTING,
        actor="ai",
        note="Draft created",
    )

    approval_service = WorkflowApprovalService(
        workflow_service=service
    )

    approval_service.submit_for_approval(
        workflow.workflow_id,
        actor="officer",
        note="Submit draft",
    )

    approval_service.approve(
        workflow.workflow_id,
        actor="leader",
        note="Approved",
    )

    signature_service = WorkflowSignatureService(
        workflow_service=service
    )

    signature_service.submit_for_signature(
        workflow.workflow_id,
        actor="system",
        note="Ready for signature",
    )

    signature_service.sign(
        workflow.workflow_id,
        actor="leader",
        signature_id="SIG-E2E-001",
        note="Signed",
    )

    workflow = service.get(workflow.workflow_id)

    assert workflow.stage == WorkflowStage.SIGNED


# ============================================================
# 16.7.2 — API / OPENAPI CONTRACT
# ============================================================


def test_16_7_2_workflow_api_contract():
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi = response.json()
    paths = openapi.get("paths", {})

    expected_paths = {
        "/workflow",
        "/workflow/{workflow_id}",
        "/workflow/{workflow_id}/transition",
        "/workflow/{workflow_id}/history",
    }

    missing = expected_paths - set(paths.keys())

    assert not missing, (
        f"Workflow OpenAPI routes missing: {sorted(missing)}"
    )

    assert "post" in paths["/workflow"]
    assert "get" in paths["/workflow"]

    assert "get" in paths["/workflow/{workflow_id}"]
    assert "delete" in paths["/workflow/{workflow_id}"]

    assert (
        "post"
        in paths["/workflow/{workflow_id}/transition"]
    )

    assert (
        "get"
        in paths["/workflow/{workflow_id}/history"]
    )


# ============================================================
# 16.7.3 — SERVICES EXPORTED
# ============================================================


def test_16_7_3_workflow_services_are_exported():
    from app.workflow import (
        WorkflowAIService,
        WorkflowApprovalService,
        WorkflowExportService,
        WorkflowSignatureExportService,
        WorkflowSignatureService,
        WorkflowService,
    )

    assert WorkflowService is not None
    assert WorkflowAIService is not None
    assert WorkflowApprovalService is not None
    assert WorkflowSignatureService is not None
    assert WorkflowExportService is not None
    assert WorkflowSignatureExportService is not None


# ============================================================
# 16.7.4 — FINAL BUSINESS CONTRACT
# ============================================================


def test_16_7_4_final_business_contract():
    service, workflow = create_workflow()

    service.transition(
        workflow.workflow_id,
        WorkflowStage.AI_PROCESSING,
        actor="ai",
        note="AI processing",
    )

    service.transition(
        workflow.workflow_id,
        WorkflowStage.DRAFTING,
        actor="ai",
        note="Draft created",
    )

    service.update_metadata(
        workflow.workflow_id,
        {
            "draft_content": "Nội dung văn bản E2E",
            "draft_file_name": "e2e_workflow.docx",
        },
    )

    approval_service = WorkflowApprovalService(
        workflow_service=service
    )

    approval_service.submit_for_approval(
        workflow.workflow_id,
        actor="officer",
    )

    approval_service.approve(
        workflow.workflow_id,
        actor="leader",
    )

    signature_export_service = WorkflowSignatureExportService(
        workflow_service=service,
        signature_service=WorkflowSignatureService(
            workflow_service=service
        ),
        export_service=WorkflowExportService(
            workflow_service=service
        ),
    )

    result = signature_export_service.sign_and_export(
        workflow_id=workflow.workflow_id,
        requested_by="officer",
        signed_by="leader",
        exported_by="system",
        signature_id="SIG-FINAL-001",
        file_name="e2e_workflow.docx",
    )

    final_workflow = service.get(workflow.workflow_id)

    assert result is not None
    assert final_workflow.stage == WorkflowStage.EXPORTED

    history = service.history(workflow.workflow_id)

    assert history

    # History records transitions, so RECEIVED is the
    # starting state rather than a to_stage transition.
    assert history[0].from_stage == WorkflowStage.RECEIVED
    assert history[0].to_stage == WorkflowStage.AI_PROCESSING

    stages = [event.to_stage for event in history]

    assert WorkflowStage.AI_PROCESSING in stages
    assert WorkflowStage.DRAFTING in stages
    assert WorkflowStage.PENDING_APPROVAL in stages
    assert WorkflowStage.APPROVED in stages
    assert WorkflowStage.PENDING_SIGNATURE in stages
    assert WorkflowStage.SIGNED in stages
    assert WorkflowStage.EXPORTED in stages