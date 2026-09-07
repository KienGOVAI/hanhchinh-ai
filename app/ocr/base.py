"""
OCR Base Interface
------------------

Interface chung cho tất cả OCR Engine.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from app.ocr.models import OCRDocument


class OCRError(Exception):
    """Lỗi chung của OCR."""


class UnsupportedFileTypeError(OCRError):
    """Định dạng file không được OCR hỗ trợ."""


class FileReadError(OCRError):
    """Không thể đọc file đầu vào."""


class InvalidFileError(OCRError):
    """File đầu vào không hợp lệ."""


class EmptyOCRResultError(OCRError):
    """OCR không nhận được nội dung."""


class BaseOCR(ABC):
    """
    Interface chung cho OCR Engine.

    Mọi OCR Engine cụ thể phải triển khai
    phương thức `process()`.
    """

    @abstractmethod
    def process(
        self,
        file_path: str | Path,
    ) -> OCRDocument:
        """
        Thực hiện OCR trên file đầu vào.

        Parameters
        ----------
        file_path:
            Đường dẫn tới file cần OCR.

        Returns
        -------
        OCRDocument:
            Kết quả OCR đã được chuẩn hóa.
        """

        raise NotImplementedError