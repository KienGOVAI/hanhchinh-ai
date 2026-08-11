"""
Base Parser
-----------

Interface chung cho tất cả Document Parser.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from app.knowledge.models.parsed_document import (
    ParsedDocument,
)


class ParserError(Exception):
    """Lỗi chung của Parser."""


class UnsupportedFileTypeError(ParserError):
    """Định dạng file không được hỗ trợ."""


class FileReadError(ParserError):
    """Không thể đọc file."""


class InvalidDocumentError(ParserError):
    """Tài liệu không hợp lệ."""


class EmptyDocumentError(ParserError):
    """Tài liệu không có nội dung."""


class BaseParser(ABC):
    """
    Interface chung cho Document Parser.
    """

    @abstractmethod
    def parse(
        self,
        file_path: str | Path,
    ) -> ParsedDocument:
        """
        Đọc và phân tích tài liệu.
        """

        raise NotImplementedError