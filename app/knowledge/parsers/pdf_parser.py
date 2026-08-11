"""
PDF Parser
----------

Parser PDF sử dụng PyMuPDF.
"""

from pathlib import Path

import fitz

from app.knowledge.models.parsed_document import (
    ParsedDocument,
    ParsedPage,
)

from app.knowledge.parsers.base_parser import (
    BaseParser,
    EmptyDocumentError,
    FileReadError,
    InvalidDocumentError,
)


class PDFParser(BaseParser):
    """
    Parser PDF.
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
            pdf = fitz.open(path)
        except Exception as exc:
            raise InvalidDocumentError(
                f"Không thể mở PDF: {path}"
            ) from exc

        try:
            if pdf.page_count == 0:
                raise EmptyDocumentError(
                    f"PDF không có trang: {path}"
                )

            pages: list[ParsedPage] = []

            for index, page in enumerate(
                pdf,
                start=1,
            ):
                text = page.get_text(
                    "text"
                )

                text = self._normalize(text)

                pages.append(
                    ParsedPage(
                        page_number=index,
                        text=text,
                    )
                )

            full_text = "\n\n".join(
                page.text
                for page in pages
                if page.text
            ).strip()

            if not full_text:
                raise EmptyDocumentError(
                    "PDF không chứa text. "
                    "Có thể đây là PDF scan và cần OCR."
                )

            metadata = dict(
                pdf.metadata or {}
            )

            metadata.update(
                {
                    "format": "pdf",
                    "filename": path.name,
                    "page_count": pdf.page_count,
                }
            )

            return ParsedDocument(
                text=full_text,
                source=path.name,
                pages=pages,
                metadata=metadata,
            )

        finally:
            pdf.close()

    @staticmethod
    def _normalize(text: str) -> str:
        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        return "\n".join(
            line
            for line in lines
            if line
        ).strip()