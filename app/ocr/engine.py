"""
PaddleOCR Engine
----------------

OCR Engine sử dụng PaddleOCR.

Input:
    PDF / Image / Scan

Output:
    OCRDocument
"""

from pathlib import Path
from typing import Any

from app.ocr.base import (
    BaseOCR,
    EmptyOCRResultError,
    FileReadError,
    InvalidFileError,
    UnsupportedFileTypeError,
)
from app.ocr.models import (
    OCRBlock,
    OCRDocument,
    OCRPage,
)


class PaddleOCREngine(BaseOCR):
    """
    OCR Engine sử dụng PaddleOCR.

    Engine chịu trách nhiệm:
        - nhận file ảnh/PDF
        - chạy OCR
        - chuẩn hóa kết quả
        - trả về OCRDocument
    """

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

    def __init__(
        self,
        lang: str = "vi",
    ) -> None:
        """
        Khởi tạo PaddleOCR.

        Parameters
        ----------
        lang:
            Ngôn ngữ OCR.
            Mặc định tiếng Việt.
        """

        self.lang = lang
        self._ocr: Any = None

    def _get_ocr(self) -> Any:
        """
        Lazy-load PaddleOCR.

        Chỉ khởi tạo model khi thực sự OCR,
        tránh load model ngay khi import module.

        Tắt oneDNN/MKLDNN để tránh lỗi PIR runtime
        trên PaddlePaddle 3.x + CPU Windows.
        """

        if self._ocr is not None:
            return self._ocr

        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise RuntimeError(
                "Chưa cài PaddleOCR. "
                "Hãy chạy: pip install paddleocr"
            ) from exc

        self._ocr = PaddleOCR(
            lang=self.lang,
            enable_mkldnn=False,
        )

        return self._ocr

    def _validate_file(
        self,
        file_path: str | Path,
    ) -> Path:
        """
        Kiểm tra file đầu vào.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileReadError(
                f"Không tìm thấy file: {path}"
            )

        if not path.is_file():
            raise InvalidFileError(
                f"Đường dẫn không phải file: {path}"
            )

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                f"Định dạng file chưa được hỗ trợ: "
                f"{extension}"
            )

        return path

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> float | None:
        """
        Chuyển confidence về float an toàn.
        """

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _build_document(
        self,
        source: Path,
        pages: list[OCRPage],
    ) -> OCRDocument:
        """
        Ghép kết quả các trang thành OCRDocument.
        """

        if not pages:
            raise EmptyOCRResultError(
                "OCR không nhận được nội dung."
            )

        text_parts = [
            page.text.strip()
            for page in pages
            if page.text.strip()
        ]

        text = "\n\n".join(text_parts).strip()

        if not text:
            raise EmptyOCRResultError(
                "OCR không nhận được nội dung văn bản."
            )

        return OCRDocument(
            text=text,
            source=str(source),
            pages=pages,
            metadata={
                "engine": "paddleocr",
                "language": self.lang,
                "page_count": len(pages),
            },
        )

    def process(
        self,
        file_path: str | Path,
    ) -> OCRDocument:
        """
        Thực hiện OCR trên file.

        Parameters
        ----------
        file_path:
            Đường dẫn PDF hoặc ảnh.

        Returns
        -------
        OCRDocument:
            Kết quả OCR đã chuẩn hóa.
        """

        path = self._validate_file(file_path)

        ocr = self._get_ocr()

        try:
            result = ocr.predict(
                str(path)
            )
        except Exception as exc:
            raise RuntimeError(
                f"PaddleOCR xử lý thất bại: {path}"
            ) from exc

        pages: list[OCRPage] = []

        for page_index, page_result in enumerate(
            result,
            start=1,
        ):
            page_texts: list[str] = []
            blocks: list[OCRBlock] = []

            rec_texts = page_result.get(
                "rec_texts",
                [],
            )

            rec_scores = page_result.get(
                "rec_scores",
                [],
            )

            for index, text in enumerate(
                rec_texts
            ):
                if not text:
                    continue

                clean_text = str(text).strip()

                if not clean_text:
                    continue

                confidence = None

                if index < len(rec_scores):
                    confidence = self._safe_float(
                        rec_scores[index]
                    )

                blocks.append(
                    OCRBlock(
                        text=clean_text,
                        confidence=confidence,
                    )
                )

                page_texts.append(
                    clean_text
                )

            page_text = "\n".join(
                page_texts
            ).strip()

            if page_text:
                page_confidences = [
                    block.confidence
                    for block in blocks
                    if block.confidence is not None
                ]

                page_confidence = (
                    sum(page_confidences)
                    / len(page_confidences)
                    if page_confidences
                    else None
                )

                pages.append(
                    OCRPage(
                        page_number=page_index,
                        text=page_text,
                        confidence=page_confidence,
                        blocks=blocks,
                        metadata={
                            "engine": "paddleocr",
                        },
                    )
                )

        return self._build_document(
            source=path,
            pages=pages,
        )