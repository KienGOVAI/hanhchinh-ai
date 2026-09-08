"""
Hành Chính AI - Workflow API.

Sprint 16.3

HTTP API:

    POST   /workflow
    GET    /workflow
    GET    /workflow/{workflow_id}
    POST   /workflow/{workflow_id}/transition
    GET    /workflow/{workflow_id}/history
    DELETE /workflow/{workflow_id}
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from app.api.schemas.workflow import (
    WorkflowCreateRequest,
    WorkflowDeleteResponse,
    WorkflowEventResponse,
    WorkflowHistoryResponse,
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowTransitionRequest,
    WorkflowTransitionResponse,
)

from app.workflow import (
    WorkflowItem,
    WorkflowService,
    WorkflowStage,
)


# ============================================================
# ROUTER
# ============================================================


router = APIRouter(
    prefix="/workflow",
    tags=["Workflow"],
)


# ============================================================
# RUNTIME SERVICE
# ============================================================


_workflow_service = WorkflowService()


def get_workflow_service() -> WorkflowService:
    """
    Lấy WorkflowService runtime hiện tại.
    """

    return _workflow_service


# ============================================================
# SERIALIZATION HELPERS
# ============================================================


def _workflow_response(
    workflow: WorkflowItem,
) -> WorkflowResponse:
    """
    Chuyển WorkflowItem thành API response.
    """

    return WorkflowResponse(
        success=True,
        workflow_id=workflow.workflow_id,
        title=workflow.title,
        document_type=workflow.document_type,
        created_by=workflow.created_by,
        stage=workflow.stage,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        metadata=dict(
            workflow.metadata
        ),
        event_count=len(
            workflow.events
        ),
        is_completed=workflow.is_completed,
        is_rejected=workflow.is_rejected,
    )


def _event_response(
    event,
) -> WorkflowEventResponse:
    """
    Chuyển WorkflowEvent thành API response.
    """

    return WorkflowEventResponse(
        from_stage=event.from_stage,
        to_stage=event.to_stage,
        actor=event.actor,
        timestamp=event.timestamp,
        note=event.note,
        metadata=dict(
            event.metadata
        ),
    )


# ============================================================
# CREATE
# ============================================================


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow(
    request: WorkflowCreateRequest,
) -> WorkflowResponse:
    """
    Tạo Workflow mới.

    Workflow mới luôn bắt đầu ở RECEIVED.
    """

    try:
        workflow = (
            get_workflow_service().create(
                title=request.title,
                document_type=request.document_type,
                created_by=request.created_by,
                metadata=request.metadata,
            )
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return _workflow_response(
        workflow
    )


# ============================================================
# LIST
# ============================================================


@router.get(
    "",
    response_model=WorkflowListResponse,
)
def list_workflows(
    stage: WorkflowStage | None = Query(
        default=None,
    ),
) -> WorkflowListResponse:
    """
    Liệt kê Workflow.

    Có thể lọc theo stage.
    """

    try:
        workflows = (
            get_workflow_service().list(
                stage=stage,
            )
        )

    except TypeError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return WorkflowListResponse(
        success=True,
        total=len(workflows),
        items=[
            _workflow_response(
                workflow
            )
            for workflow in workflows
        ],
    )


# ============================================================
# GET
# ============================================================


@router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
)
def get_workflow(
    workflow_id: str,
) -> WorkflowResponse:
    """
    Lấy một Workflow theo ID.
    """

    try:
        workflow = (
            get_workflow_service().get(
                workflow_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return _workflow_response(
        workflow
    )


# ============================================================
# TRANSITION
# ============================================================


@router.post(
    "/{workflow_id}/transition",
    response_model=WorkflowTransitionResponse,
)
def transition_workflow(
    workflow_id: str,
    request: WorkflowTransitionRequest,
) -> WorkflowTransitionResponse:
    """
    Chuyển Workflow sang trạng thái mới.
    """

    try:
        event = (
            get_workflow_service().transition(
                workflow_id,
                request.target,
                actor=request.actor,
                note=request.note,
                metadata=request.metadata,
            )
        )

        workflow = (
            get_workflow_service().get(
                workflow_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        from app.workflow import (
            WorkflowTransitionError,
        )

        if isinstance(
            exc,
            WorkflowTransitionError,
        ):
            raise HTTPException(
                status_code=409,
                detail=str(exc),
            ) from exc

        raise

    return WorkflowTransitionResponse(
        success=True,
        workflow=_workflow_response(
            workflow
        ),
        event=_event_response(
            event
        ),
    )


# ============================================================
# HISTORY
# ============================================================


@router.get(
    "/{workflow_id}/history",
    response_model=WorkflowHistoryResponse,
)
def workflow_history(
    workflow_id: str,
) -> WorkflowHistoryResponse:
    """
    Lấy lịch sử chuyển trạng thái.
    """

    try:
        service = get_workflow_service()

        workflow = service.get(
            workflow_id
        )

        events = service.history(
            workflow_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return WorkflowHistoryResponse(
        success=True,
        workflow_id=workflow.workflow_id,
        stage=workflow.stage,
        total=len(events),
        events=[
            _event_response(event)
            for event in events
        ],
    )


# ============================================================
# DELETE
# ============================================================


@router.delete(
    "/{workflow_id}",
    response_model=WorkflowDeleteResponse,
)
def delete_workflow(
    workflow_id: str,
) -> WorkflowDeleteResponse:
    """
    Xóa Workflow.
    """

    try:
        workflow = (
            get_workflow_service().delete(
                workflow_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return WorkflowDeleteResponse(
        success=True,
        workflow_id=workflow.workflow_id,
    )