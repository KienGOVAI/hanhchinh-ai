"""
Hành Chính AI - Workflow Signature + Export Integration.

Sprint 16.6.3

Integration:

    APPROVED
        ↓
    PENDING_SIGNATURE
        ↓
      SIGNED
        ↓
     EXPORTED

Service này chỉ làm orchestration.
Không thay thế Domain, Signature Service hoặc Export Service.
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
from app.workflow.signature_service import (
    WorkflowSignatureService,
    WorkflowSignatureError,
)
from app.workflow.export_service import (
    WorkflowExportService,
    WorkflowExportError,
)


# ============================================================
# EXCEPTIONS
# ============================================================


class WorkflowSignatureExportError(Exception):
    """
    Lỗi chung của Integration Service.
    """


class WorkflowSignatureExportValidationError(
    WorkflowSignatureExportError
):
    """
    Dữ liệu Integration không hợp lệ.
    """


class WorkflowSignatureExportStateError(
    WorkflowSignatureExportError
):
    """
    Workflow không ở trạng thái phù hợp
    để thực hiện Signature → Export.
    """


# ============================================================
# RESULT
# ============================================================


@dataclass
class WorkflowSignatureExportResult:
    """
    Kết quả của toàn bộ chuỗi:

        Signature → Export
    """

    workflow_id: str

    stage: WorkflowStage

    requested_by: str

    signed_by: str

    exported_by: str

    file_name: str

    file_path: str | None

    signature_id: str | None

    signature_result: Any

    export_result: Any

    metadata: dict[str, Any]


# ============================================================
# SERVICE
# ============================================================


class WorkflowSignatureExportService:
    """
    Orchestrate:

        APPROVED
            ↓
        PENDING_SIGNATURE
            ↓
          SIGNED
            ↓
         EXPORTED
    """

    def __init__(
        self,
        workflow_service: WorkflowService,
        signature_service: WorkflowSignatureService,
        export_service: WorkflowExportService,
    ) -> None:
        if workflow_service is None:
            raise ValueError(
                "workflow_service không được rỗng."
            )

        if signature_service is None:
            raise ValueError(
                "signature_service không được rỗng."
            )

        if export_service is None:
            raise ValueError(
                "export_service không được rỗng."
            )

        self.workflow_service = workflow_service
        self.signature_service = signature_service
        self.export_service = export_service

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def _validate_actor(
        actor: str,
        field_name: str = "actor",
    ) -> str:
        if not isinstance(actor, str):
            raise WorkflowSignatureExportValidationError(
                f"{field_name} phải là chuỗi."
            )

        actor = actor.strip()

        if not actor:
            raise WorkflowSignatureExportValidationError(
                f"{field_name} không được rỗng."
            )

        return actor

    @staticmethod
    def _validate_file_name(
        file_name: str | None,
    ) -> str | None:
        if file_name is None:
            return None

        if not isinstance(file_name, str):
            raise WorkflowSignatureExportValidationError(
                "file_name phải là chuỗi hoặc None."
            )

        file_name = file_name.strip()

        if not file_name:
            return None

        return file_name

    @staticmethod
    def _validate_signature_id(
        signature_id: str | None,
    ) -> str | None:
        if signature_id is None:
            return None

        if not isinstance(signature_id, str):
            raise WorkflowSignatureExportValidationError(
                "signature_id phải là chuỗi hoặc None."
            )

        signature_id = signature_id.strip()

        if not signature_id:
            return None

        return signature_id

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
    # SIGN → EXPORT
    # ========================================================

    def sign_and_export(
        self,
        workflow_id: str,
        *,
        requested_by: str,
        signed_by: str,
        exported_by: str,
        signature_id: str | None = None,
        file_name: str | None = None,
        file_path: str | None = None,
        signature_note: str = "",
        export_note: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowSignatureExportResult:
        """
        Thực hiện toàn bộ chuỗi:

            APPROVED
                ↓
            PENDING_SIGNATURE
                ↓
              SIGNED
                ↓
             EXPORTED
        """

        requested_by = self._validate_actor(
            requested_by,
            "requested_by",
        )

        signed_by = self._validate_actor(
            signed_by,
            "signed_by",
        )

        exported_by = self._validate_actor(
            exported_by,
            "exported_by",
        )

        signature_id = self._validate_signature_id(
            signature_id
        )

        file_name = self._validate_file_name(
            file_name
        )

        # ----------------------------------------------------
        # INITIAL STATE
        # ----------------------------------------------------

        workflow = self.workflow_service.get(
            workflow_id
        )

        if workflow.stage != WorkflowStage.APPROVED:
            raise WorkflowSignatureExportStateError(
                (
                    "Signature → Export chỉ được bắt đầu "
                    "khi Workflow ở trạng thái "
                    f"'{WorkflowStage.APPROVED.value}'. "
                    f"Trạng thái hiện tại: "
                    f"'{workflow.stage.value}'."
                )
            )

        # ----------------------------------------------------
        # SHARED METADATA
        # ----------------------------------------------------

        integration_metadata: dict[str, Any] = {
            "signature_export_pipeline": True,
        }

        if metadata:
            integration_metadata.update(
                metadata
            )

        # ----------------------------------------------------
        # STEP 1: REQUEST SIGNATURE
        # ----------------------------------------------------

        try:
            signature_request_result = (
                self.signature_service.submit_for_signature(
                    workflow_id,
                    actor=requested_by,
                    note=signature_note,
                    metadata=integration_metadata,
                )
            )
        except WorkflowSignatureError as exc:
            raise WorkflowSignatureExportError(
                (
                    "Không thể chuyển Workflow "
                    "sang trạng thái chờ ký."
                )
            ) from exc

        # ----------------------------------------------------
        # STEP 2: SIGN
        # ----------------------------------------------------

        try:
            signature_result = (
                self.signature_service.sign(
                    workflow_id,
                    actor=signed_by,
                    note=signature_note,
                    signature_id=signature_id,
                    metadata=integration_metadata,
                )
            )
        except WorkflowSignatureError as exc:
            raise WorkflowSignatureExportError(
                "Không thể ký Workflow."
            ) from exc

        # ----------------------------------------------------
        # STEP 3: EXPORT
        # ----------------------------------------------------

        try:
            export_result = (
                self.export_service.export(
                    workflow_id,
                    actor=exported_by,
                    file_name=file_name,
                    file_path=file_path,
                    note=export_note,
                    metadata=integration_metadata,
                )
            )
        except WorkflowExportError as exc:
            raise WorkflowSignatureExportError(
                "Workflow đã ký nhưng không thể export."
            ) from exc

        # ----------------------------------------------------
        # FINAL WORKFLOW
        # ----------------------------------------------------

        final_workflow = self.workflow_service.get(
            workflow_id
        )

        if final_workflow.stage != (
            WorkflowStage.EXPORTED
        ):
            raise WorkflowSignatureExportStateError(
                (
                    "Integration hoàn tất nhưng Workflow "
                    "không ở trạng thái EXPORTED."
                )
            )

        final_file_name = (
            export_result.file_name
        )

        final_file_path = (
            export_result.file_path
        )

        final_signature_id = (
            signature_result.metadata.get(
                "signature_id"
            )
        )

        final_metadata: dict[str, Any] = {
            "signature_export_pipeline": True,
            "requested_by": requested_by,
            "signed_by": signed_by,
            "exported_by": exported_by,
            "signature_status": "signed",
            "export_status": "exported",
            "export_file_name": final_file_name,
        }

        if final_file_path:
            final_metadata[
                "export_file_path"
            ] = final_file_path

        if final_signature_id:
            final_metadata[
                "signature_id"
            ] = final_signature_id

        if metadata:
            final_metadata.update(metadata)

        self.workflow_service.update_metadata(
            workflow_id,
            final_metadata,
        )

        return WorkflowSignatureExportResult(
            workflow_id=workflow_id,
            stage=WorkflowStage.EXPORTED,
            requested_by=requested_by,
            signed_by=signed_by,
            exported_by=exported_by,
            file_name=final_file_name,
            file_path=final_file_path,
            signature_id=final_signature_id,
            signature_result=signature_result,
            export_result=export_result,
            metadata=final_metadata,
        )

    # ========================================================
    # PIPELINE CHECK
    # ========================================================

    def is_completed(
        self,
        workflow_id: str,
    ) -> bool:
        """
        Kiểm tra toàn bộ Signature → Export
        đã hoàn thành chưa.
        """

        workflow = self.workflow_service.get(
            workflow_id
        )

        return workflow.stage == (
            WorkflowStage.EXPORTED
        )