"""
Document API
------------

API sinh và tải văn bản.
"""

from pathlib import Path

from fastapi import (
    APIRouter,
    HTTPException,
    Path as PathParam,
    status,
)
from fastapi.responses import FileResponse

from app.schemas.document import (
    DocumentRequest,
    DocumentResponse,
)
from app.services.document_service import (
    generate_document,
)

router = APIRouter(
    prefix="/document",
    tags=["Document"],
)


# =====================================================
# GENERATE DOCUMENT
# =====================================================

@router.post(
    "/generate",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Sinh văn bản bằng AI",
    description=(
        "Sinh văn bản hành chính bằng AI "
        "và hỗ trợ Conversation Session."
    ),
)
def create_document(
    request: DocumentRequest,
) -> DocumentResponse:
    """
    Sinh văn bản hành chính.
    """

    try:

        return generate_document(
            request,
        )

    except Exception as ex:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex),
        )


# =====================================================
# DOWNLOAD
# =====================================================

@router.get(
    "/download/{filename}",
    summary="Tải văn bản Word",
    description="Tải file Word đã sinh.",
)
def download_document(
    filename: str = PathParam(
        ...,
        min_length=1,
        description="Tên file Word",
    ),
):
    """
    Download Word Document.
    """

    filename = Path(filename).name

    file_path = Path("output") / filename

    if not file_path.exists():

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy file.",
        )

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.wordprocessingml.document"
        ),
    )


# =====================================================
# HEALTH CHECK
# =====================================================

@router.get(
    "/health",
    summary="Kiểm tra Document Service",
)
def health():
    """
    Kiểm tra trạng thái Document API.
    """

    return {
        "success": True,
        "service": "Document API",
        "status": "running",
    }