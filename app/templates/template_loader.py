"""
Template Loader
---------------

Chịu trách nhiệm nạp Word Template.
"""

from pathlib import Path

from docx import Document

from app.templates.template_definition import (
    TemplateDefinition,
)
from app.templates.template_factory import (
    TemplateFactory,
)


class TemplateLoader:
    """
    Loader quản lý Word Template.
    """

    ROOT = Path("templates")

    # =====================================================
    # PUBLIC
    # =====================================================

    def load(
        self,
        template_name: str,
    ) -> Document:
        """
        Nạp Template Word.
        """

        return Document(
            self.get_path(
                template_name
            )
        )

    def get_path(
        self,
        template_name: str,
    ) -> Path:
        """
        Trả về đường dẫn Template.
        """

        template = TemplateFactory.create(
            template_name
        )

        path = self._build_path(
            template
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Không tìm thấy Template: {path}"
            )

        return path

    def exists(
        self,
        template_name: str,
    ) -> bool:
        """
        Kiểm tra Template tồn tại.
        """

        try:

            return self.get_path(
                template_name
            ).exists()

        except Exception:

            return False

    def list_templates(
        self,
        enabled_only: bool = False,
    ) -> list[TemplateDefinition]:
        """
        Danh sách Template.
        """

        return TemplateFactory.all(
            enabled_only=enabled_only
        )

    # =====================================================
    # PRIVATE
    # =====================================================

    def _build_path(
        self,
        template: TemplateDefinition,
    ) -> Path:
        """
        Sinh đường dẫn đầy đủ tới Template.
        """

        return (
            self.ROOT
            / template.template_folder
            / template.file_name
        )