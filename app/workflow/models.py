"""
Hành Chính AI - Workflow Domain Models.

Sprint 16.1

Workflow nghiệp vụ:

    RECEIVED
        ↓
    AI_PROCESSING
        ↓
    DRAFTING
        ↓
    PENDING_APPROVAL
        ↓
    APPROVED
        ↓
    PENDING_SIGNATURE
        ↓
    SIGNED
        ↓
    EXPORTED

Nhánh từ chối:

    PENDING_APPROVAL
        ↓
    REJECTED
        ↓
    DRAFTING
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


# ============================================================
# EXCEPTIONS
# ============================================================


class WorkflowTransitionError(Exception):
    """
    Lỗi khi thực hiện chuyển trạng thái Workflow không hợp lệ.
    """


# ============================================================
# WORKFLOW STAGE
# ============================================================


class WorkflowStage(str, Enum):
    """
    Các trạng thái trong vòng đời Workflow.

    Business flow:

        RECEIVED
            ↓
        AI_PROCESSING
            ↓
        DRAFTING
            ↓
        PENDING_APPROVAL
            ↓
        APPROVED
            ↓
        PENDING_SIGNATURE
            ↓
        SIGNED
            ↓
        EXPORTED
    """

    RECEIVED = "received"

    AI_PROCESSING = "ai_processing"

    DRAFTING = "drafting"

    PENDING_APPROVAL = "pending_approval"

    APPROVED = "approved"

    PENDING_SIGNATURE = "pending_signature"

    SIGNED = "signed"

    EXPORTED = "exported"

    REJECTED = "rejected"


# ============================================================
# WORKFLOW EVENT
# ============================================================


@dataclass(frozen=True)
class WorkflowEvent:
    """
    Một sự kiện chuyển trạng thái Workflow.
    """

    from_stage: WorkflowStage | None

    to_stage: WorkflowStage

    actor: str

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    note: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# WORKFLOW TRANSITIONS
# ============================================================


_ALLOWED_TRANSITIONS: dict[
    WorkflowStage,
    set[WorkflowStage],
] = {
    WorkflowStage.RECEIVED: {
        WorkflowStage.AI_PROCESSING,
    },

    WorkflowStage.AI_PROCESSING: {
        WorkflowStage.DRAFTING,
    },

    WorkflowStage.DRAFTING: {
        WorkflowStage.PENDING_APPROVAL,
    },

    WorkflowStage.PENDING_APPROVAL: {
        WorkflowStage.APPROVED,
        WorkflowStage.REJECTED,
    },

    WorkflowStage.REJECTED: {
        WorkflowStage.DRAFTING,
    },

    WorkflowStage.APPROVED: {
        WorkflowStage.PENDING_SIGNATURE,
    },

    WorkflowStage.PENDING_SIGNATURE: {
        WorkflowStage.SIGNED,
    },

    WorkflowStage.SIGNED: {
        WorkflowStage.EXPORTED,
    },

    WorkflowStage.EXPORTED: set(),
}


# ============================================================
# WORKFLOW ITEM
# ============================================================


@dataclass
class WorkflowItem:
    """
    Đối tượng nghiệp vụ trung tâm của Workflow.

    Đây là một hồ sơ/văn bản đang đi qua quy trình:

        Tiếp nhận
            ↓
        AI
            ↓
        Soạn
            ↓
        Duyệt
            ↓
        Ký
            ↓
        Xuất
    """

    title: str

    document_type: str

    created_by: str

    workflow_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    stage: WorkflowStage = WorkflowStage.RECEIVED

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    events: list[WorkflowEvent] = field(
        default_factory=list
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    def __post_init__(self) -> None:
        self.title = self._validate_text(
            self.title,
            "title",
        )

        self.document_type = self._validate_text(
            self.document_type,
            "document_type",
        )

        self.created_by = self._validate_text(
            self.created_by,
            "created_by",
        )

        if not isinstance(
            self.stage,
            WorkflowStage,
        ):
            raise TypeError(
                "stage phải là WorkflowStage."
            )

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
    # STATUS
    # ========================================================

    @property
    def is_completed(self) -> bool:
        """
        Workflow đã hoàn tất khi văn bản được xuất.
        """

        return self.stage == WorkflowStage.EXPORTED

    @property
    def is_rejected(self) -> bool:
        """
        Workflow đang ở trạng thái bị từ chối.
        """

        return self.stage == WorkflowStage.REJECTED

    # ========================================================
    # TRANSITION
    # ========================================================

    def can_transition(
        self,
        target: WorkflowStage,
    ) -> bool:
        """
        Kiểm tra có thể chuyển sang target hay không.
        """

        if not isinstance(
            target,
            WorkflowStage,
        ):
            raise TypeError(
                "target phải là WorkflowStage."
            )

        return target in _ALLOWED_TRANSITIONS.get(
            self.stage,
            set(),
        )

    def transition(
        self,
        target: WorkflowStage,
        *,
        actor: str,
        note: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowEvent:
        """
        Chuyển Workflow sang trạng thái mới.

        Mọi chuyển trạng thái đều được ghi vào events.
        """

        actor = self._validate_text(
            actor,
            "actor",
        )

        if not isinstance(
            target,
            WorkflowStage,
        ):
            raise TypeError(
                "target phải là WorkflowStage."
            )

        if not self.can_transition(target):
            raise WorkflowTransitionError(
                (
                    "Không thể chuyển Workflow "
                    f"từ '{self.stage.value}' "
                    f"sang '{target.value}'."
                )
            )

        event = WorkflowEvent(
            from_stage=self.stage,
            to_stage=target,
            actor=actor,
            note=note.strip(),
            metadata=dict(metadata or {}),
        )

        self.stage = target
        self.updated_at = event.timestamp
        self.events.append(event)

        return event

    # ========================================================
    # CONVENIENCE METHODS
    # ========================================================

    def start_ai(
        self,
        *,
        actor: str,
        note: str = "",
    ) -> WorkflowEvent:
        return self.transition(
            WorkflowStage.AI_PROCESSING,
            actor=actor,
            note=note,
        )

    def start_drafting(
        self,
        *,
        actor: str,
        note: str = "",
    ) -> WorkflowEvent:
        return self.transition(
            WorkflowStage.DRAFTING,
            actor=actor,
            note=note,
        )

    def submit_for_approval(
        self,
        *,
        actor: str,
        note: str = "",
    ) -> WorkflowEvent:
        return self.transition(
            WorkflowStage.PENDING_APPROVAL,
            actor=actor,
            note=note,
        )

    def approve(
        self,
        *,
        actor: str,
        note: str = "",
    ) -> WorkflowEvent:
        return self.transition(
            WorkflowStage.APPROVED,
            actor=actor,
            note=note,
        )

    def reject(
        self,
        *,
        actor: str,
        note: str = "",
    ) -> WorkflowEvent:
        return self.transition(
            WorkflowStage.REJECTED,
            actor=actor,
            note=note,
        )

    def submit_for_signature(
        self,
        *,
        actor: str,
        note: str = "",
    ) -> WorkflowEvent:
        return self.transition(
            WorkflowStage.PENDING_SIGNATURE,
            actor=actor,
            note=note,
        )

    def sign(
        self,
        *,
        actor: str,
        note: str = "",
    ) -> WorkflowEvent:
        return self.transition(
            WorkflowStage.SIGNED,
            actor=actor,
            note=note,
        )

    def export(
        self,
        *,
        actor: str,
        note: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowEvent:
        return self.transition(
            WorkflowStage.EXPORTED,
            actor=actor,
            note=note,
            metadata=metadata,
        )