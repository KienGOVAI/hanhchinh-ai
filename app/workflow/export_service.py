"""
Hành Chính AI - Workflow Export Service.

Sprint 16.6.2

Nghiệp vụ:

    SIGNED
        ↓
    EXPORTED

Export Service chịu trách nhiệm:
- Kiểm tra Workflow đã ký.
- Kiểm tra dữ liệu văn bản đã tồn tại.
- Xác định tên file xuất cuối.
- Ghi nhận thông tin export.
- Chuyển Workflow SIGNED → EXPORTED.

State transition vẫn do Workflow Domain kiểm soát.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from pathlib import Path

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


class WorkflowExportError(Exception):
    """
    Lỗi chung của Export Service.
    """


class WorkflowExportValidationError(
    WorkflowExportError
):
    """
    Dữ liệu export không hợp lệ.
    """


class WorkflowExportStateError(
    WorkflowExportError
):
    """
    Workflow đang ở trạng thái không phù hợp
    với nghiệp vụ export.
    """


# ============================================================
# RESULT
# ============================================================


@dataclass
class WorkflowExportResult:
    """
    Kết quả nghiệp vụ export.
    """

    workflow_id: str
    stage: WorkflowStage
    actor: str
    action: str
    file_name: str
    file_path: str | None
    note: str
    event: Any
    metadata: dict[str, Any]


# ============================================================
# SERVICE
# ============================================================


class WorkflowExportService:
    """
    Điều phối nghiệp vụ xuất văn bản sau khi ký.
    """

    def __init__(
        self,
        workflow_service: WorkflowService,
    ) -> None:
        if workflow_service is None:
            raise ValueError(
                "workflow_service không được rỗng."
            )

        self.workflow_service = workflow_service

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def _validate_actor(
        actor: str,
    ) -> str:
        if not isinstance(actor, str):
            raise WorkflowExportValidationError(
                "actor phải là chuỗi."
            )

        actor = actor.strip()

        if not actor:
            raise WorkflowExportValidationError(
                "actor không được rỗng."
            )

        return actor

    @staticmethod
    def _validate_file_name(
        file_name: str,
    ) -> str:
        if not isinstance(file_name, str):
            raise WorkflowExportValidationError(
                "file_name phải là chuỗi."
            )

        file_name = file_name.strip()

        if not file_name:
            raise WorkflowExportValidationError(
                "file_name không được rỗng."
            )

        # Không cho phép path traversal.
        path = Path(file_name)

        if path.name != file_name:
            raise WorkflowExportValidationError(
                "file_name chỉ được chứa tên file, "
                "không được chứa đường dẫn."
            )

        return file_name

    @staticmethod
    def _validate_file_path(
        file_path: str | None,
    ) -> str | None:
        if file_path is None:
            return None

        if not isinstance(file_path, str):
            raise WorkflowExportValidationError(
                "file_path phải là chuỗi hoặc None."
            )

        file_path = file_path.strip()

        if not file_path:
            return None

        return file_path

    @staticmethod
    def _validate_note(
        note: str,
    ) -> str:
        if not isinstance(note, str):
            raise WorkflowExportValidationError(
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
        """
        Lấy Workflow hiện tại.
        """

        return self.workflow_service.get(
            workflow_id
        )

    # ========================================================
    # EXPORT
    # ========================================================

    def export(
        self,
        workflow_id: str,
        *,
        actor: str,
        file_name: str | None = None,
        file_path: str | None = None,
        note: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowExportResult:
        """
        Xuất văn bản đã ký.

        SIGNED → EXPORTED

        file_name:
            Tên file cuối cùng được xuất.

        file_path:
            Đường dẫn file nếu file đã được tạo/lưu
            bởi tầng document/export bên ngoài.

        Lưu ý:
            Service này quản lý nghiệp vụ Workflow Export.
            Việc sinh bytes DOCX/PDF thực tế sẽ được
            Integration Service kết nối ở Sprint 16.6.3.
        """

        actor = self._validate_actor(actor)
        note = self._validate_note(note)
        file_path = self._validate_file_path(file_path)

        workflow = self.workflow_service.get(
            workflow_id
        )

        # ----------------------------------------------------
        # STATE CHECK
        # ----------------------------------------------------

        if workflow.stage != WorkflowStage.SIGNED:
            raise WorkflowExportStateError(
                (
                    "Chỉ Workflow ở trạng thái "
                    f"'{WorkflowStage.SIGNED.value}' "
                    "mới được export."
                )
            )

        # ----------------------------------------------------
        # FILE NAME
        # ----------------------------------------------------

        if file_name is None:
            file_name = workflow.metadata.get(
                "draft_file_name"
            )

        if not file_name:
            raise WorkflowExportValidationError(
                (
                    "Không xác định được file_name. "
                    "Workflow phải có draft_file_name "
                    "hoặc truyền file_name khi export."
                )
            )

        file_name = self._validate_file_name(
            file_name
        )

        # ----------------------------------------------------
        # DOCUMENT VALIDATION
        # ----------------------------------------------------

        draft_content = workflow.metadata.get(
            "draft_content"
        )

        if not draft_content:
            raise WorkflowExportValidationError(
                (
                    "Workflow chưa có draft_content. "
                    "Không thể export văn bản rỗng."
                )
            )

        # ----------------------------------------------------
        # EVENT METADATA
        # ----------------------------------------------------

        event_metadata: dict[str, Any] = {
            "export_file_name": file_name,
        }

        if file_path:
            event_metadata[
                "export_file_path"
            ] = file_path

        if metadata:
            event_metadata.update(metadata)

        # ----------------------------------------------------
        # STATE TRANSITION
        # ----------------------------------------------------

        event = self.workflow_service.transition(
            workflow_id,
            WorkflowStage.EXPORTED,
            actor=actor,
            note=(
                note
                or "Workflow đã được xuất."
            ),
            metadata=event_metadata,
        )

        # ----------------------------------------------------
        # WORKFLOW METADATA
        # ----------------------------------------------------

        stored_metadata: dict[str, Any] = {
            "export_status": "exported",
            "export_file_name": file_name,
            "exported_by": actor,
            "export_note": note,
        }

        if file_path:
            stored_metadata[
                "export_file_path"
            ] = file_path

        if metadata:
            stored_metadata.update(metadata)

        self.workflow_service.update_metadata(
            workflow_id,
            stored_metadata,
        )

        return WorkflowExportResult(
            workflow_id=workflow_id,
            stage=WorkflowStage.EXPORTED,
            actor=actor,
            action="export",
            file_name=file_name,
            file_path=file_path,
            note=note,
            event=event,
            metadata=stored_metadata,
        )

    # ========================================================
    # EXPORTED CHECK
    # ========================================================

    def is_exported(
        self,
        workflow_id: str,
    ) -> bool:
        """
        Kiểm tra Workflow đã export hay chưa.
        """

        workflow = self.workflow_service.get(
            workflow_id
        )

        return workflow.stage == WorkflowStage.EXPORTED