"""
Document Builder
----------------

Sinh và lưu văn bản Word.
"""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.schemas.document import DocumentRequest
from app.templates.factory import TemplateFactory


class DocumentBuilder:
    """
    Builder sinh văn bản Word.
    """

    OUTPUT_DIR = Path("output")

    def __init__(self):

        self.OUTPUT_DIR.mkdir(
            exist_ok=True
        )

    # =====================================================
    # PUBLIC
    # =====================================================

    def build(
        self,
        data: DocumentRequest,
    ) -> dict:
        """
        Sinh văn bản.
        """

        template = TemplateFactory.create(
            data.type
        )

        if template is None:

            raise ValueError(
                f"Không tìm thấy Template '{data.type}'."
            )

        document = template.build(
            data
        )

        filepath = self._build_output_path(
            data.type
        )

        document.save(filepath)

        return {
            "success": True,
            "file_name": filepath.name,
            "file_path": str(filepath),
        }

    # =====================================================
    # PRIVATE
    # =====================================================

    def _build_output_path(
        self,
        document_type: str,
    ) -> Path:
        """
        Sinh tên file đầu ra.
        """

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        unique = uuid4().hex[:8]

        filename = (
            f"{document_type}_{timestamp}_{unique}.docx"
        )

        return self.OUTPUT_DIR / filename