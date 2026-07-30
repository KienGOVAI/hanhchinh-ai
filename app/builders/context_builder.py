"""
Context Builder
---------------
Chịu trách nhiệm:
- Sinh Context chuẩn cho AI
- Quy định vai trò AI
- Quy định ngôn ngữ
- Quy định phong cách
- Quy định định dạng đầu ra
"""

from datetime import datetime


class ContextBuilder:
    """
    Xây dựng Context gửi cho Prompt Builder.
    """

    def __init__(self):
        self.role = "Chuyên gia hành chính công Việt Nam"

        self.language = "Tiếng Việt"

        self.style = "Văn phong hành chính"

        self.output = "Markdown"

    def build(
        self,
        document_type: str = "",
        extra_context: str = ""
    ) -> str:
        """
        Trả về Context hoàn chỉnh.
        """

        today = datetime.now().strftime("%d/%m/%Y")

        context = f"""
VAI TRÒ

{self.role}

====================================

NGÀY HỆ THỐNG

{today}

====================================

NGÔN NGỮ

{self.language}

====================================

PHONG CÁCH

{self.style}

====================================

LOẠI VĂN BẢN

{document_type}

====================================

ĐỊNH DẠNG ĐẦU RA

{self.output}

====================================

THÔNG TIN BỔ SUNG

{extra_context}
"""

        return context.strip()