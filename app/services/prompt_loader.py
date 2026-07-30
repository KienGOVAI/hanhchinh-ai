"""
Prompt Loader
--------------
Chịu trách nhiệm:
- Đọc Prompt từ thư mục prompts
- Cache Prompt để tăng tốc
- Kiểm tra Prompt có tồn tại hay không
"""

from pathlib import Path
from functools import lru_cache


class PromptLoader:
    """
    Load Prompt Markdown từ thư mục app/prompts
    """

    # app/services -> app -> prompts
    PROMPT_ROOT = Path(__file__).resolve().parent.parent / "prompts"

    @classmethod
    @lru_cache(maxsize=128)
    def load(cls, category: str, prompt_name: str) -> str:
        """
        Đọc Prompt.

        Ví dụ:
            PromptLoader.load("document", "ke_hoach")

        =>
        app/prompts/document/ke_hoach.md
        """

        file_path = cls.PROMPT_ROOT / category / f"{prompt_name}.md"

        if not file_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy Prompt:\n{file_path}"
            )

        return file_path.read_text(
            encoding="utf-8"
        )

    @classmethod
    def exists(cls, category: str, prompt_name: str) -> bool:
        """
        Kiểm tra Prompt có tồn tại hay không.
        """

        file_path = cls.PROMPT_ROOT / category / f"{prompt_name}.md"

        return file_path.exists()

    @classmethod
    def clear_cache(cls):
        """
        Xóa cache.
        Dùng khi chỉnh sửa Prompt trong lúc phát triển.
        """

        cls.load.cache_clear()