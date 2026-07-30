"""
Document Definition
-------------------

Định nghĩa metadata của một loại văn bản.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentDefinition:
    """
    Định nghĩa metadata của một loại văn bản.
    """

    # ==========================
    # Thông tin cơ bản
    # ==========================

    document_type: str

    display_name: str

    description: str

    # ==========================
    # Prompt
    # ==========================

    prompt_category: str = "document"

    prompt_name: str = ""

    # ==========================
    # Template
    # ==========================

    template_name: str = ""

    # ==========================
    # Output
    # ==========================

    output_folder: str = ""

    # ==========================
    # Giao diện
    # ==========================

    icon: str = "📄"

    # ==========================
    # Quản lý
    # ==========================

    enabled: bool = True

    version: str = "1.0"

    author: str = "HanhChinhAI"

    category: str = "van_ban_hanh_chinh"