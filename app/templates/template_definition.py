"""
Template Definition
-------------------

Định nghĩa metadata của một Word Template.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateDefinition:
    """
    Metadata của một template.
    """

    # ==========================
    # Thông tin cơ bản
    # ==========================

    template_name: str

    display_name: str

    description: str

    # ==========================
    # File
    # ==========================

    file_name: str

    file_extension: str = ".docx"

    # ==========================
    # Đường dẫn
    # ==========================

    template_folder: str = "templates"

    # ==========================
    # Trạng thái
    # ==========================

    enabled: bool = True

    version: str = "1.0"

    author: str = "HanhChinhAI"

    # ==========================
    # Thuộc tính
    # ==========================

    supports_header: bool = True

    supports_footer: bool = True

    supports_signature: bool = True