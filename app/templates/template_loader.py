"""
Template Loader
---------------

Chịu trách nhiệm nạp các file Word Template.
"""

from pathlib import Path
from docx import Document

from app.templates.template_factory import TemplateFactory


class TemplateLoader:
    """
    Nạp và quản lý Word Template.
    """

    def __init__(self):
        self.root = Path("templates")

    def get_path(self, template_name: str) -> Path:
        """
        Trả về đường dẫn tuyệt đối của template.
        """

        template = TemplateFactory.create(template_name)

        path = (
            self.root
            / template.template_folder
            / template.file_name
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy Template: {path}"
            )

        return path

    def load(self, template_name: str) -> Document:
        """
        Nạp file Word và trả về đối tượng Document.
        """

        path = self.get_path(template_name)

        return Document(path)

    def exists(self, template_name: str) -> bool:
        """
        Kiểm tra template có tồn tại trên ổ đĩa.
        """

        try:
            path = self.get_path(template_name)
            return path.exists()
        except Exception:
            return False

    def list_templates(self):
        """
        Trả về toàn bộ template đã đăng ký.
        """

        return TemplateFactory.all()