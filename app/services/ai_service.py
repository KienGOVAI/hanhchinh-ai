"""
AI Service
----------

Chịu trách nhiệm:

- Lấy DocumentDefinition
- Xây dựng Context
- Gọi PromptBuilder để sinh Prompt
- Kiểm tra Prompt
- Gửi Prompt tới AI Provider
"""

from app.builders.context_builder import ContextBuilder
from app.builders.prompt_builder import PromptBuilder
from app.documents.document_factory import DocumentFactory
from app.providers.provider_factory import ProviderFactory
from app.services.prompt_validator import PromptValidator


class AIService:
    """
    AI Service
    """

    def __init__(self):
        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()
        self.provider = ProviderFactory.create()

    def generate_document(
        self,
        document_type: str,
        title: str,
        content: str,
        extra_context: str = ""
    ):
        """
        Sinh văn bản bằng AI.

        Parameters
        ----------
        document_type : str
            Loại văn bản (cong_van, ke_hoach, thong_bao, ...)
        title : str
            Tiêu đề văn bản
        content : str
            Nội dung yêu cầu
        extra_context : str
            Ngữ cảnh bổ sung
        """

        # =====================================
        # Lấy Document Definition
        # =====================================

        document = DocumentFactory.create(document_type)

        # =====================================
        # Build Context
        # =====================================

        context = self.context_builder.build(
            document_type=document.document_type,
            extra_context=extra_context
        )

        # =====================================
        # Build Prompt
        # =====================================

        prompt = self.prompt_builder.build(
            document=document,
            user_input=f"{title}\n\n{content}",
            context=context
        )

        # =====================================
        # Validate Prompt
        # =====================================

        valid, message = PromptValidator.validate(prompt)

        if not valid:
            raise ValueError(message)

        # =====================================
        # Generate Document
        # =====================================

        return self.provider.generate(prompt)