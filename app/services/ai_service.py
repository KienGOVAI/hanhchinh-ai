"""
AI Service
----------

Điều phối toàn bộ quá trình sinh Prompt và gọi AI.
"""

from app.builders.context_builder import ContextBuilder
from app.builders.prompt_builder import PromptBuilder
from app.conversation.conversation_history import (
    ConversationHistory,
)
from app.documents.document_factory import DocumentFactory
from app.providers.provider_factory import ProviderFactory
from app.services.prompt_validator import PromptValidator


class AIService:
    """
    AI Service.
    """

    def __init__(self):

        self.context_builder = ContextBuilder()

        self.prompt_builder = PromptBuilder()

        self.provider = ProviderFactory.create()

    # =====================================================
    # GENERATE DOCUMENT
    # =====================================================

    def generate_document(
        self,
        *,
        document_type: str,
        title: str,
        content: str,
        extra_context: str = "",
        history: ConversationHistory | None = None,
    ) -> str:
        """
        Sinh nội dung văn bản bằng AI.
        """

        # =====================================
        # DOCUMENT
        # =====================================

        document = DocumentFactory.create(
            document_type
        )

        # =====================================
        # CONTEXT
        # =====================================

        context = self.context_builder.build(
            document_type=document.document_type,
            extra_context=extra_context,
        )

        # =====================================
        # PROMPT
        # =====================================

        prompt = self.prompt_builder.build(
            document=document,
            user_input=f"{title}\n\n{content}",
            context=context,
            history=history,
        )

        # =====================================
        # VALIDATE
        # =====================================

        valid, message = PromptValidator.validate(
            prompt
        )

        if not valid:
            raise ValueError(message)

        # =====================================
        # PROVIDER HEALTH CHECK
        # =====================================

        if not self.provider.health_check():
            raise RuntimeError(
                f"Provider '{self.provider.provider_name}' không sẵn sàng."
            )

        # =====================================
        # AI GENERATE
        # =====================================

        answer = self.provider.generate(prompt)

        # =====================================
        # VALIDATE RESULT
        # =====================================

        if not isinstance(answer, str):
            raise TypeError(
                f"{self.provider.provider_name} phải trả về str, "
                f"nhận được {type(answer).__name__}."
            )

        answer = answer.strip()

        if not answer:
            raise RuntimeError(
                f"{self.provider.provider_name} trả về nội dung rỗng."
            )

        return answer