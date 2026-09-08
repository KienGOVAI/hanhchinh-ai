"""
Hành Chính AI - Workflow Service.

Sprint 16.2

Workflow Service chịu trách nhiệm điều phối các WorkflowItem.

Domain model:
    app.workflow.models

Service:
    create
    get
    list
    transition
    history
    count
    delete

Workflow:

    RECEIVED
        ↓
    AI_PROCESSING
        ↓
    DRAFTING
        ↓
    PENDING_APPROVAL
        ├── APPROVED
        │      ↓
        │  PENDING_SIGNATURE
        │      ↓
        │    SIGNED
        │      ↓
        │   EXPORTED
        │
        └── REJECTED
               ↓
            DRAFTING
"""

from __future__ import annotations

from typing import Any

from app.workflow.models import (
    WorkflowEvent,
    WorkflowItem,
    WorkflowStage,
)


class WorkflowService:
    """
    Service điều phối Workflow.

    Hiện tại sử dụng in-memory storage giống mô hình
    ConversationService hiện có.

    Persistence/database sẽ được xử lý ở các Sprint sau.
    """

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowItem] = {}

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def _validate_text(
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} phải là chuỗi."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} không được rỗng."
            )

        return normalized

    # ========================================================
    # CREATE
    # ========================================================

    def create(
        self,
        *,
        title: str,
        document_type: str,
        created_by: str,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowItem:
        """
        Tạo một Workflow mới.

        Workflow luôn bắt đầu ở RECEIVED.
        """

        workflow = WorkflowItem(
            title=self._validate_text(
                title,
                "title",
            ),
            document_type=self._validate_text(
                document_type,
                "document_type",
            ),
            created_by=self._validate_text(
                created_by,
                "created_by",
            ),
            metadata=dict(metadata or {}),
        )

        self._workflows[
            workflow.workflow_id
        ] = workflow

        return workflow

    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
        workflow_id: str,
    ) -> WorkflowItem:
        """
        Lấy Workflow theo ID.

        Không tồn tại → ValueError.
        """

        workflow_id = self._validate_text(
            workflow_id,
            "workflow_id",
        )

        workflow = self._workflows.get(
            workflow_id
        )

        if workflow is None:
            raise ValueError(
                f"Không tìm thấy Workflow "
                f"'{workflow_id}'."
            )

        return workflow

    # ========================================================
    # EXISTS
    # ========================================================

    def exists(
        self,
        workflow_id: str,
    ) -> bool:
        """
        Kiểm tra Workflow có tồn tại hay không.
        """

        if not isinstance(
            workflow_id,
            str,
        ):
            return False

        workflow_id = workflow_id.strip()

        if not workflow_id:
            return False

        return workflow_id in self._workflows

    # ========================================================
    # LIST
    # ========================================================

    def list(
        self,
        *,
        stage: WorkflowStage | None = None,
    ) -> list[WorkflowItem]:
        """
        Liệt kê Workflow.

        Nếu stage được truyền vào thì chỉ trả về
        các Workflow ở trạng thái đó.
        """

        if stage is not None and not isinstance(
            stage,
            WorkflowStage,
        ):
            raise TypeError(
                "stage phải là WorkflowStage "
                "hoặc None."
            )

        workflows = list(
            self._workflows.values()
        )

        if stage is not None:
            workflows = [
                workflow
                for workflow in workflows
                if workflow.stage == stage
            ]

        return workflows

    # ========================================================
    # COUNT
    # ========================================================

    def count(
        self,
        *,
        stage: WorkflowStage | None = None,
    ) -> int:
        """
        Đếm số Workflow.

        Có thể đếm toàn bộ hoặc theo stage.
        """

        return len(
            self.list(stage=stage)
        )

    # ========================================================
    # TRANSITION
    # ========================================================

    def transition(
        self,
        workflow_id: str,
        target: WorkflowStage,
        *,
        actor: str,
        note: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowEvent:
        """
        Chuyển trạng thái Workflow.

        Service chịu trách nhiệm tìm Workflow.
        Domain chịu trách nhiệm kiểm tra transition hợp lệ.
        """

        workflow = self.get(
            workflow_id
        )

        return workflow.transition(
            target,
            actor=actor,
            note=note,
            metadata=metadata,
        )

    # ========================================================
    # HISTORY
    # ========================================================

    def history(
        self,
        workflow_id: str,
    ) -> list[WorkflowEvent]:
        """
        Lấy lịch sử chuyển trạng thái.

        Trả về bản sao list để bên ngoài không thể
        trực tiếp sửa lịch sử nội bộ.
        """

        workflow = self.get(
            workflow_id
        )

        return list(
            workflow.events
        )

    # ========================================================
    # UPDATE METADATA
    # ========================================================

    def update_metadata(
        self,
        workflow_id: str,
        metadata: dict[str, Any],
    ) -> WorkflowItem:
        """
        Cập nhật metadata của Workflow.
        """

        workflow = self.get(
            workflow_id
        )

        if not isinstance(
            metadata,
            dict,
        ):
            raise TypeError(
                "metadata phải là dict."
            )

        workflow.metadata.update(
            metadata
        )

        return workflow

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        workflow_id: str,
    ) -> WorkflowItem:
        """
        Xóa Workflow khỏi service.

        Không tồn tại → ValueError.
        """

        workflow = self.get(
            workflow_id
        )

        del self._workflows[
            workflow.workflow_id
        ]

        return workflow

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(self) -> None:
        """
        Xóa toàn bộ Workflow trong service.

        Chủ yếu phục vụ test/runtime reset.
        """

        self._workflows.clear()