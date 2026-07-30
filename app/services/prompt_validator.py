"""
Prompt Validator
----------------
Kiểm tra Prompt trước khi gửi tới AI.
"""

from typing import Tuple


class PromptValidator:

    MAX_PROMPT_LENGTH = 50000

    @classmethod
    def validate(cls, prompt: str) -> Tuple[bool, str]:
        """
        Returns
        -------
        (True, "OK")
            Prompt hợp lệ

        (False, "Lý do")
            Prompt không hợp lệ
        """

        if not prompt:
            return False, "Prompt rỗng."

        prompt = prompt.strip()

        if len(prompt) == 0:
            return False, "Prompt rỗng."

        if len(prompt) > cls.MAX_PROMPT_LENGTH:
            return (
                False,
                f"Prompt vượt quá {cls.MAX_PROMPT_LENGTH:,} ký tự."
            )

        if "SYSTEM PROMPT" not in prompt:
            return (
                False,
                "Thiếu System Prompt."
            )

        if "YÊU CẦU NGƯỜI DÙNG" not in prompt:
            return (
                False,
                "Thiếu User Prompt."
            )

        return True, "OK"