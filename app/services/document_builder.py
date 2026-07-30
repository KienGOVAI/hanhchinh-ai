from pathlib import Path
from datetime import datetime

from app.templates.factory import TemplateFactory


class DocumentBuilder:

    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def build(self, data):

        # =====================================
        # Chọn Template
        # =====================================

        template = TemplateFactory.create(
            data.type,
        )

        # =====================================
        # Sinh Word
        # =====================================

        doc = template.build(
            data,
        )

        # =====================================
        # Tên file
        # =====================================

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = (
            f"{data.type}_{timestamp}.docx"
        )

        filepath = self.output_dir / filename

        # =====================================
        # Lưu file
        # =====================================

        doc.save(filepath)

        return {
            "success": True,
            "file_name": filename,
            "file_path": str(filepath),
        }