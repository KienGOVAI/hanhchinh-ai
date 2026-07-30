"""
Document Parser
---------------

Đọc tài liệu và chuyển thành plain text.

Hỗ trợ:

- PDF
- DOCX
- TXT
- Markdown
"""

from pathlib import Path

from docx import Document
import fitz


class DocumentParser:
    """
    Parser tài liệu.
    """

    SUPPORTED_TYPES = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
    }

    def parse(self, path: Path) -> str:
        """
        Parse tài liệu.

        Returns:
            Plain text
        """

        suffix = path.suffix.lower()

        if suffix not in self.SUPPORTED_TYPES:
            raise ValueError(
                f"Không hỗ trợ định dạng '{suffix}'."
            )

        if suffix == ".pdf":
            return self._parse_pdf(path)

        if suffix == ".docx":
            return self._parse_docx(path)

        if suffix == ".txt":
            return self._parse_text(path)

        if suffix == ".md":
            return self._parse_text(path)

        return ""

    # =====================================================

    def _parse_pdf(
        self,
        path: Path
    ) -> str:

        document = fitz.open(path)

        pages = []

        for page in document:

            pages.append(
                page.get_text()
            )

        document.close()

        return "\n".join(pages)

    # =====================================================

    def _parse_docx(
        self,
        path: Path
    ) -> str:

        document = Document(path)

        paragraphs = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:

                paragraphs.append(text)

        return "\n".join(paragraphs)

    # =====================================================

    def _parse_text(
        self,
        path: Path
    ) -> str:

        return path.read_text(
            encoding="utf-8"
        )