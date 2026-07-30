"""
Prompt Registry
---------------

Quản lý đăng ký và tra cứu Prompt.
"""

from typing import Dict


class PromptRegistry:

    _PROMPTS: Dict[str, Dict[str, str]] = {}

    @classmethod
    def register(
        cls,
        document_type: str,
        category: str,
        prompt_name: str
    ):
        """
        Đăng ký Prompt mới.
        """

        cls._PROMPTS[document_type] = {
            "category": category,
            "prompt_name": prompt_name
        }

    @classmethod
    def get(cls, document_type: str):

        if document_type not in cls._PROMPTS:
            raise ValueError(
                f"Không tìm thấy Prompt cho '{document_type}'."
            )

        return cls._PROMPTS[document_type]

    @classmethod
    def exists(cls, document_type: str):

        return document_type in cls._PROMPTS

    @classmethod
    def unregister(cls, document_type: str):

        if document_type in cls._PROMPTS:
            del cls._PROMPTS[document_type]

    @classmethod
    def clear(cls):

        cls._PROMPTS.clear()

    @classmethod
    def list(cls):

        return sorted(cls._PROMPTS.keys())


# =====================================================
# Đăng ký Prompt mặc định của hệ thống
# =====================================================

PromptRegistry.register(
    "cong_van",
    "document",
    "cong_van"
)

PromptRegistry.register(
    "ke_hoach",
    "document",
    "ke_hoach"
)

PromptRegistry.register(
    "bao_cao",
    "document",
    "bao_cao"
)

PromptRegistry.register(
    "thong_bao",
    "document",
    "thong_bao"
)

PromptRegistry.register(
    "giay_moi",
    "document",
    "giay_moi"
)

PromptRegistry.register(
    "quyet_dinh",
    "document",
    "quyet_dinh"
)