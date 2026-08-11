"""
Text Parser
-----------

Parser cho file TXT.
"""

from pathlib import Path

from app.knowledge.models.parsed_document import (
    ParsedDocument,
    ParsedPage,
)

from app.knowledge.parsers.base_parser import (
    BaseParser,
    EmptyDocumentError,
    FileReadError,
)


class TextParser(BaseParser):
    """
    Parser file TXT.
    """

    def parse(
        self,
        file_path: str | Path,
    ) -> ParsedDocument:

        path = Path(file_path)

        if not path.exists():
            raise FileReadError(
                f"Không tìm thấy file: {path}"
            )

        try:
            text = path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError as exc:
            raise FileReadError(
                f"Không thể đọc file UTF-8: {path}"
            ) from exc
        except OSError as exc:
            raise FileReadError(
                f"Không thể đọc file: {path}"
            ) from exc

        text = self._normalize(text)

        if not text:
            raise EmptyDocumentError(
                f"Tài liệu rỗng: {path}"
            )

        page = ParsedPage(
            page_number=1,
            text=text,
        )

        return ParsedDocument(
            text=text,
            source=path.name,
            pages=[page],
            metadata={
                "format": "txt",
                "filename": path.name,
            },
        )

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Chuẩn hóa whitespace nhưng không phá cấu trúc dòng.
        """

        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        return "\n".join(
            line
            for line in lines
            if line
        ).strip()