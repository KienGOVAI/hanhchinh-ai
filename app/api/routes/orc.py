"""
OCR API Routes
==============

Sprint 14.3:
    14.3.1 - OCR API Schema
    14.3.2 - OCR Router Integration
    14.3.3 - OCR Upload Validation
    14.3.4 - OCR Runtime
    14.3.5 - OCR API Response
    14.3.6 - OCR API Test
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.ocr.base import (
    EmptyOCRResultError,
    FileReadError,
    InvalidFileError,
    UnsupportedFileTypeError,
)
from app.ocr.engine import PaddleOCREngine
from app.schemas.ocr import OCRUploadResponse


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
    """Kiểm tra tên và extension của file upload."""

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File upload không có tên.",
        )

    path = Path(filename)

    if not path.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên file không hợp lệ.",
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "Định dạng file chưa được hỗ trợ: "
                f"{extension or '(không có extension)'}."
            ),
        )

    return path


@router.post(
    "/upload",
    response_model=OCRUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload file để thực hiện OCR",
)
def upload_ocr_file(
    file: UploadFile,
) -> OCRUploadResponse:
    """
    Upload file ảnh/PDF và thực hiện OCR.

    Pipeline:

        UploadFile
            ↓
        Validate
            ↓
        Temporary File
            ↓
        PaddleOCREngine
            ↓
        OCRDocument
            ↓
        OCRUploadResponse
    """

    filename = _validate_filename(
        file.filename,
    )

    temporary_path: Path | None = None

    try:
        # 1. Lưu file upload vào temporary file
        suffix = filename.suffix.lower()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temporary_file:
            temporary_path = Path(
                temporary_file.name,
            )

            shutil.copyfileobj(
                file.file,
                temporary_file,
            )

        file_size = temporary_path.stat().st_size

        # 2. OCR Runtime
        ocr_document = ocr_engine.process(
            temporary_path,
        )

        if ocr_document is None:
            raise RuntimeError(
                "OCR Engine không trả về OCRDocument."
            )

        # 3. Sprint 14.3.5:
        #    Chuyển OCRDocument thành API response chuẩn.
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
            detail=f"OCR Runtime thất bại: {exc}",
        ) from exc

    finally:
        try:
            file.file.close()
        except Exception:
            pass
