"""
REST API cho Knowledge Base.

Task 12.12.

Router chỉ chịu trách nhiệm:
- Nhận request.
- Validate request thông qua Pydantic schema.
- Gọi KnowledgeService.
- Chuyển kết quả Service thành API Response.
- Chuyển lỗi nghiệp vụ thành HTTP status.

Router không trực tiếp xử lý:
- Parser
- Chunker
- Embedding
- Vector Store
- Retriever
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.knowledge.services.knowledge_service import (
    KnowledgeService,
    KnowledgeServiceError,
)

from app.schemas.knowledge import (
    KnowledgeSearchItem,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)


router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)


# ============================================================
# SERVICE RUNTIME
# ============================================================

_knowledge_service: KnowledgeService | None = None


def configure_knowledge_service(
    service: KnowledgeService,
) -> None:
    """
    Đăng ký KnowledgeService cho API runtime.

    Application layer chịu trách nhiệm khởi tạo
    Retriever / VectorStore và truyền Service vào đây.
    """

    global _knowledge_service

    _knowledge_service = service


def get_knowledge_service() -> KnowledgeService | None:
    """
    Lấy KnowledgeService hiện tại.

    Không ném HTTPException tại đây.

    Lý do:
    FastAPI resolve dependency trước khi endpoint
    xử lý request body. Nếu ném 503 tại dependency,
    request không hợp lệ sẽ nhận 503 thay vì 422.

    Endpoint sẽ kiểm tra Service sau khi Pydantic
    đã hoàn tất validation.
    """

    return _knowledge_service


# ============================================================
# SEARCH
# ============================================================

@router.post(
    "/search",
    response_model=KnowledgeSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Tìm kiếm Knowledge Base",
)
def search_knowledge(
    request: KnowledgeSearchRequest,
    service: KnowledgeService | None = Depends(
        get_knowledge_service
    ),
) -> KnowledgeSearchResponse:
    """
    Tìm kiếm Knowledge Base.

    Luồng:

        Request
          ↓
        Pydantic validation
          ↓
        KnowledgeService
          ↓
        Retriever
          ↓
        VectorStore
          ↓
        KnowledgeSearchResponse
    """

    # ========================================================
    # SERVICE AVAILABILITY
    # ========================================================

    if service is None:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "Knowledge Service chưa được "
                "khởi tạo trong API runtime."
            ),
        )

    # ========================================================
    # BUSINESS SEARCH
    # ========================================================

    try:
        result = service.search(
            query=request.query,
            query_vector=request.query_vector,
            top_k=request.top_k,
            score_threshold=(
                request.score_threshold
            ),
        )

    except KnowledgeServiceError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Đã xảy ra lỗi khi tìm kiếm "
                "Knowledge Base."
            ),
        ) from exc

    # ========================================================
    # MAP SERVICE RESULT → API RESPONSE
    # ========================================================

    items = [
        KnowledgeSearchItem(
            vector_id=item.vector_id,
            score=item.score,
            content=item.content,
            document_id=item.document_id,
            chunk_index=item.chunk_index,
            page_number=item.page_number,
            metadata=item.metadata,
        )
        for item in result.results
    ]

    return KnowledgeSearchResponse(
        success=True,
        query=result.query,
        total=result.total,
        results=items,
        message="Tìm kiếm thành công.",
    )