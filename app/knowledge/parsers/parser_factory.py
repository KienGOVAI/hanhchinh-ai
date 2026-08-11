"""
Parser Factory
--------------

Tạo Parser phù hợp với loại file.
"""

from pathlib import Path

from app.knowledge.parsers.base_parser import (
    BaseParser,
    UnsupportedFileTypeError,
)

from app.knowledge.parsers.docx_parser import (
    DOCXParser,
)

from app.knowledge.parsers.pdf_parser import (
    PDFParser,
)

from app.knowledge.parsers.text_parser import (
    TextParser,
)


class ParserFactory:
    """
    Factory tạo Document Parser.
    """

    _parsers = {
        ".pdf": PDFParser,
        ".docx": DOCXParser,
        ".txt": TextParser,
    }

    @classmethod
    def create(
        cls,
        file_path: str | Path,
    ) -> BaseParser:

        extension = Path(
            file_path
        ).suffix.lower()

        parser_class = cls._parsers.get(
            extension
        )

        if parser_class is None:
            supported = ", ".join(
                sorted(cls._parsers.keys())
            )

            raise UnsupportedFileTypeError(
                f"Định dạng '{extension}' "
                f"chưa được hỗ trợ. "
                f"Định dạng hỗ trợ: {supported}"
            )

        return parser_class()