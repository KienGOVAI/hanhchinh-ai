"""
Prompt Validator
----------------

Kiểm tra Prompt trước khi gửi tới AI.
"""


class PromptValidator:

    MAX_PROMPT_LENGTH = 50000

    @classmethod
    def validate(
        cls,
        prompt: str,
    ) -> tuple[bool, str]:
        """
        Kiểm tra Prompt hợp lệ.

        Returns
        -------
        (True, "OK")
            Prompt hợp lệ.

        (False, "Lý do")
            Prompt không hợp lệ.
        """

        if not prompt:
            return False, "Prompt rỗng."

        prompt = prompt.strip()

        if not prompt:
            return False, "Prompt rỗng."

        if len(prompt) > cls.MAX_PROMPT_LENGTH:
            return (
                False,
                f"Prompt vượt quá {cls.MAX_PROMPT_LENGTH:,} ký tự."
            )

        # =====================================================
        # Không kiểm tra tiêu đề cứng nữa.
        # Chỉ cần Prompt có nội dung là hợp lệ.
        # =====================================================

        return True, "OK"