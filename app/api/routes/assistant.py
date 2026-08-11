"""
REST API cho AI Assistant.

Task 12.14.10 - Assistant Integration Test.

Pipeline:

    HTTP Request
        ↓
    Request Validation
        ↓
    AssistantService
        ↓
    Embedding
        ↓
    Retrieval
        ↓
    Context
        ↓
    RAG
        ↓
    Citation
        ↓
    HTTP Response
"""

from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.api.schemas.assistant import (
    AssistantCitation,
    AssistantRequest,
    AssistantResponseSchema,
)

from app.knowledge.assistant import (
    AssistantService,
    AssistantServiceError,
)

from app.knowledge.citation import Citation


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/assistant",
    tags=["Assistant"],
)


# =========================================================
# RUNTIME SERVICE
# =========================================================

_assistant_service: AssistantService | None = None


def configure_assistant_service(
    service: AssistantService,
) -> None:
    """
    Inject AssistantService vào API runtime.
    """

    global _assistant_service

    _assistant_service = service


def get_assistant_service() -> AssistantService:
    """
    Lấy AssistantService hiện tại.

    Nếu runtime chưa được cấu hình,
    API trả HTTP 503.
    """

    if _assistant_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Assistant Service chưa được "
                "khởi tạo trong API runtime."
            ),
        )

    return _assistant_service


# =========================================================
# REQUEST VALIDATION
# =========================================================

def _validate_question(
    request: AssistantRequest,
) -> str:
    """
    Validate và chuẩn hóa câu hỏi.

    Quy tắc:

        ""      → 400
        "   "   → 400
        None    → 422
        str hợp lệ → trả về question.strip()
    """

    question: Any = request.question

    if not isinstance(question, str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="question phải là chuỗi.",
        )

    normalized = question.strip()

    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Câu hỏi không được rỗng.",
        )

    return normalized


# =========================================================
# CITATION CONVERSION
# =========================================================

def _citation_to_schema(
    citation: Any,
) -> AssistantCitation:
    """
    Chuyển Citation domain model sang API schema.

    Không phụ thuộc cứng vào isinstance(Citation)
    để các domain object tương thích vẫn có thể
    được chuyển đổi tại API boundary.
    """

    if isinstance(citation, Citation):
        return AssistantCitation(
            citation_id=citation.citation_id,
            source=citation.source,
            score=citation.score,
            document_id=citation.document_id,
            page_number=citation.page_number,
            chunk_index=citation.chunk_index,
            content=citation.content,
            metadata=dict(citation.metadata),
            label=citation.label,
        )

    # -----------------------------------------------------
    # Generic compatible object
    # -----------------------------------------------------

    citation_id = getattr(
        citation,
        "citation_id",
        None,
    )

    source = getattr(
        citation,
        "source",
        None,
    )

    score = getattr(
        citation,
        "score",
        None,
    )

    document_id = getattr(
        citation,
        "document_id",
        None,
    )

    page_number = getattr(
        citation,
        "page_number",
        None,
    )

    chunk_index = getattr(
        citation,
        "chunk_index",
        None,
    )

    content = getattr(
        citation,
        "content",
        "",
    )

    metadata = getattr(
        citation,
        "metadata",
        {},
    )

    label = getattr(
        citation,
        "label",
        None,
    )

    if citation_id is None:
        raise ValueError(
            "Citation thiếu citation_id."
        )

    if source is None:
        raise ValueError(
            "Citation thiếu source."
        )

    if score is None:
        raise ValueError(
            "Citation thiếu score."
        )

    if label is None:
        label_parts = [str(source)]

        if page_number is not None:
            label_parts.append(
                f"trang {page_number}"
            )

        if chunk_index is not None:
            label_parts.append(
                f"chunk {chunk_index}"
            )

        label = " — ".join(
            label_parts
        )

    if not isinstance(
        metadata,
        dict,
    ):
        metadata = {}

    return AssistantCitation(
        citation_id=str(citation_id),
        source=str(source),
        score=float(score),
        document_id=document_id,
        page_number=page_number,
        chunk_index=chunk_index,
        content=str(content or ""),
        metadata=dict(metadata),
        label=str(label),
    )


# =========================================================
# ASK
# =========================================================

@router.post(
    "/ask",
    response_model=AssistantResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Đặt câu hỏi cho AI Assistant",
)
def ask_assistant(
    request: AssistantRequest,
) -> AssistantResponseSchema:
    """
    Xử lý câu hỏi của người dùng.

    Pipeline:

        Request
            ↓
        Validation
            ↓
        AssistantService.answer()
            ↓
        Citation conversion
            ↓
        Response
    """

    # -----------------------------------------------------
    # 1. REQUEST VALIDATION
    # -----------------------------------------------------

    question = _validate_question(
        request
    )

    # -----------------------------------------------------
    # 2. GET ASSISTANT SERVICE
    # -----------------------------------------------------

    service = get_assistant_service()

    # -----------------------------------------------------
    # 3. ASSISTANT SERVICE
    # -----------------------------------------------------

    try:
        response = service.answer(
            question
        )

    except AssistantServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Đã xảy ra lỗi khi xử lý "
                "AI Assistant."
            ),
        ) from exc

    # -----------------------------------------------------
    # 4. CITATIONS
    # -----------------------------------------------------

    citations: list[
        AssistantCitation
    ] = []

    for citation in (
        response.citations or []
    ):
        try:
            citations.append(
                _citation_to_schema(
                    citation
                )
            )

        except Exception as exc:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Không thể chuyển đổi "
                    "Citation sang API response."
                ),
            ) from exc

    # -----------------------------------------------------
    # 5. METADATA
    # -----------------------------------------------------

    metadata = dict(
        response.metadata or {}
    )

    # API phải phản ánh đúng số citation
    # thực tế trả về.
    metadata["citation_count"] = len(
        citations
    )

    # -----------------------------------------------------
    # 6. RESPONSE
    # -----------------------------------------------------

    return AssistantResponseSchema(
        success=True,
        question=response.query,
        answer=response.answer,
        citations=citations,
        metadata=metadata,
        message=(
            "Assistant xử lý câu hỏi "
            "thành công."
        ),
    )