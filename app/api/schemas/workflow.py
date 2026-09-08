"""
Hành Chính AI - Workflow API Schemas.

Sprint 16.3
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.workflow.models import WorkflowStage


# ============================================================
# CREATE
# ============================================================


class WorkflowCreateRequest(BaseModel):
    """
    Request tạo Workflow mới.
    """

    title: str = Field(
        min_length=1,
        max_length=500,
    )

    document_type: str = Field(
        min_length=1,
        max_length=100,
    )

    created_by: str = Field(
        min_length=1,
        max_length=200,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


# ============================================================
# TRANSITION
# ============================================================


class WorkflowTransitionRequest(BaseModel):
    """
    Request chuyển trạng thái Workflow.
    """

    target: WorkflowStage

    actor: str = Field(
        min_length=1,
        max_length=200,
    )

    note: str = Field(
        default="",
        max_length=2000,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


# ============================================================
# EVENT
# ============================================================


class WorkflowEventResponse(BaseModel):
    """
    Một sự kiện Workflow.
    """

    from_stage: WorkflowStage | None

    to_stage: WorkflowStage

    actor: str

    timestamp: datetime

    note: str

    metadata: dict[str, Any]


# ============================================================
# WORKFLOW RESPONSE
# ============================================================


class WorkflowResponse(BaseModel):
    """
    Workflow response.
    """

    success: bool = True

    workflow_id: str

    title: str

    document_type: str

    created_by: str

    stage: WorkflowStage

    created_at: datetime

    updated_at: datetime

    metadata: dict[str, Any]

    event_count: int

    is_completed: bool

    is_rejected: bool


# ============================================================
# LIST RESPONSE
# ============================================================


class WorkflowListResponse(BaseModel):
    """
    Danh sách Workflow.
    """

    success: bool = True

    total: int

    items: list[WorkflowResponse]


# ============================================================
# EVENT RESPONSE
# ============================================================


class WorkflowTransitionResponse(BaseModel):
    """
    Response sau khi chuyển Workflow.
    """

    success: bool = True

    workflow: WorkflowResponse

    event: WorkflowEventResponse


# ============================================================
# HISTORY RESPONSE
# ============================================================


class WorkflowHistoryResponse(BaseModel):
    """
    Lịch sử Workflow.
    """

    success: bool = True

    workflow_id: str

    stage: WorkflowStage

    total: int

    events: list[WorkflowEventResponse]


# ============================================================
# DELETE RESPONSE
# ============================================================


class WorkflowDeleteResponse(BaseModel):
    """
    Response sau khi xóa Workflow.
    """

    success: bool = True

    workflow_id: str

    message: str = (
        "Workflow đã được xóa."
    )