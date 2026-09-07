"""
OCR API Routes
==============

Sprint 14.3:
    OCR Upload API

Sprint 14.4:
    OCR + AI
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.ocr.ai import (
    EmptyOCRTextError,
    InvalidOCRDocumentError,
    OCRAIInstructionError,
    OCRAIServiceError,
)
from app.ocr.base import (
    EmptyOCRResultError,
    FileReadError,
    InvalidFileError,
    UnsupportedFileTypeError,
)
from app.ocr.rag import OCRRAGInstructionError
from app.ocr.engine import PaddleOCREngine
from app.ocr.runtime import get_ocr_ai_service
from app.schemas.ocr import OCRUploadResponse
from app.schemas.ocr_ai import OCRAIResponseSchema
from app.schemas.ocr_rag import OCRRAGResponseSchema

router = APIRouter(
    prefix="/ocr",
    tags=["OCR"],
)


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
    ".pdf",
}


ocr_engine = PaddleOCREngine(
    lang="vi",
)


def _validate_filename(
    filename: str | None,
) -> Path:
    """Kiá»ƒm tra tÃªn vÃ  extension cá»§a file upload."""

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File upload khÃ´ng cÃ³ tÃªn.",
        )

    path = Path(filename)

    if not path.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TÃªn file khÃ´ng há»£p lá»‡.",
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "Äá»‹nh dáº¡ng file chÆ°a Ä‘Æ°á»£c há»— trá»£: "
                f"{extension or '(khÃ´ng cÃ³ extension)'}."
            ),
        )

    return path


def _save_upload_file(
    file: UploadFile,
    filename: Path,
) -> tuple[Path, int]:
    """LÆ°u UploadFile vÃ o temporary file."""

    suffix = filename.suffix.lower()

    temporary_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    )

    temporary_path = Path(
        temporary_file.name,
    )

    try:
        with temporary_file:
            shutil.copyfileobj(
                file.file,
                temporary_file,
            )

        file_size = temporary_path.stat().st_size

        return temporary_path, file_size

    except Exception:
        try:
            temporary_path.unlink(
                missing_ok=True,
            )
        except Exception:
            pass

        raise


@router.post(
    "/upload",
    response_model=OCRUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload file Ä‘á»ƒ thá»±c hiá»‡n OCR",
)
def upload_ocr_file(
    file: UploadFile,
) -> OCRUploadResponse:
    """
    Upload file áº£nh/PDF vÃ  thá»±c hiá»‡n OCR.

    Pipeline:

        UploadFile
            â†“
        Validate
            â†“
        Temporary File
            â†“
        PaddleOCREngine
            â†“
        OCRDocument
            â†“
        OCRUploadResponse
    """

    filename = _validate_filename(
        file.filename,
    )

    temporary_path: Path | None = None

    try:
        temporary_path, file_size = _save_upload_file(
            file,
            filename,
        )

        ocr_document = ocr_engine.process(
            temporary_path,
        )

        if ocr_document is None:
            raise RuntimeError(
                "OCR Engine khÃ´ng tráº£ vá» OCRDocument."
            )

        return OCRUploadResponse.from_ocr_document(
            ocr_document,
            filename=filename.name,
            content_type=file.content_type,
            file_size=file_size,
            file_path=str(temporary_path),
        )

    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc

    except (
        FileReadError,
        InvalidFileError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except EmptyOCRResultError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR Runtime tháº¥t báº¡i: {exc}",
        ) from exc

    finally:
        try:
            file.file.close()
        except Exception:
            pass


@router.post(
    "/ai",
    response_model=OCRAIResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Upload file, OCR vÃ  xá»­ lÃ½ báº±ng AI",
)
def upload_ocr_ai(
    file: UploadFile = File(...),
    instruction: str = Form(...),
) -> OCRAIResponseSchema:
    """
    Sprint 14.4 â€” OCR + AI.

    Pipeline:

        UploadFile
            â†“
        Validate
            â†“
        Temporary File
            â†“
        PaddleOCREngine
            â†“
        OCRDocument
            â†“
        OCRAIService
            â†“
        AssistantService
            â†“
        AI Answer
    """

    filename = _validate_filename(
        file.filename,
    )

    temporary_path: Path | None = None

    try:
        temporary_path, file_size = _save_upload_file(
            file,
            filename,
        )

        # 1. OCR
        ocr_document = ocr_engine.process(
            temporary_path,
        )

        if ocr_document is None:
            raise RuntimeError(
                "OCR Engine khÃ´ng tráº£ vá» OCRDocument."
            )

        # 2. OCR â†’ AI
        ocr_ai_service = get_ocr_ai_service()

        result = ocr_ai_service.process(
            document=ocr_document,
            instruction=instruction,
        )

        return OCRAIResponseSchema(
            success=True,
            filename=filename.name,
            content_type=file.content_type,
            file_size=file_size,
            ocr_text=result.ocr_text,
            instruction=result.instruction,
            answer=result.answer,
            metadata=result.metadata,
        )

    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc

    except (
        FileReadError,
        InvalidFileError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except EmptyOCRResultError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except (
        InvalidOCRDocumentError,
        EmptyOCRTextError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except OCRAIInstructionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except OCRAIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR + AI Runtime tháº¥t báº¡i: {exc}",
        ) from exc

    finally:
        try:
            file.file.close()
        except Exception:
            pass
@router.post(
    "/rag",
    response_model=OCRRAGResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Upload file, OCR vÃ  xá»­ lÃ½ báº±ng RAG",
)
def upload_ocr_rag(
    file: UploadFile = File(...),
    instruction: str = Form(...),
) -> OCRRAGResponseSchema:
    """
    Sprint 14.5 â€” OCR + RAG.

    Pipeline:

        UploadFile
            â†“
        Validate
            â†“
        Temporary File
            â†“
        PaddleOCREngine
            â†“
        OCRDocument
            â†“
        OCRRAGService
            â†“
        AssistantService
            â†“
        Knowledge Base / RAG
            â†“
        Answer + Sources
    """

    filename = _validate_filename(
        file.filename,
    )

    temporary_path: Path | None = None

    try:
        temporary_path, file_size = _save_upload_file(
            file,
            filename,
        )

        # ====================================================
        # 1. OCR
        # ====================================================

        ocr_document = ocr_engine.process(
            temporary_path,
        )

        if ocr_document is None:
            raise RuntimeError(
                "OCR Engine khÃ´ng tráº£ vá» OCRDocument."
            )

        # ====================================================
        # 2. OCR â†’ RAG
        # ====================================================

        from app.ocr.rag_runtime import (
            get_ocr_rag_service,
        )

        ocr_rag_service = (
            get_ocr_rag_service()
        )

        result = ocr_rag_service.process(
            document=ocr_document,
            instruction=instruction,
        )

        # ====================================================
        # 3. API Response
        # ====================================================

        return OCRRAGResponseSchema(
            success=True,
            filename=filename.name,
            content_type=file.content_type,
            file_size=file_size,
            ocr_text=result.ocr_text,
            instruction=result.instruction,
            answer=result.answer,
            sources=result.sources,
            metadata=result.metadata,
        )

    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc

    except (
        FileReadError,
        InvalidFileError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except EmptyOCRResultError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except (
        InvalidOCRDocumentError,
        EmptyOCRTextError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except OCRRAGInstructionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except OCRRAGServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR + RAG Runtime tháº¥t báº¡i: {exc}",
        ) from exc

    finally:
        try:
            file.file.close()
        except Exception:
            pass        

