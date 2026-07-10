from app.services.prompt_service import PromptService


class PromptBuilder:

    def __init__(self):
        self.prompt_service = PromptService()

    def build(
        self,
        document_type: str,
        title: str,
        content: str
    ) -> str:

        # Đọc Prompt cơ sở
        system_prompt = self.prompt_service.load(document_type)

        # Ghép Prompt hoàn chỉnh
        final_prompt = f"""
{system_prompt}

========================================

THÔNG TIN NGƯỜI DÙNG

Tiêu đề:

{title}

----------------------------------------

Nội dung:

{content}

========================================

YÊU CẦU

Viết hoàn chỉnh nội dung văn bản.

Không giải thích.

Không thêm ghi chú.

Chỉ trả về nội dung văn bản.
"""

        return final_prompt