"""
Prompt Builder
--------------

Ghép System Prompt + Document Prompt + Knowledge
+ Conversation History + User Request.
"""

from app.conversation.conversation_history import (
    ConversationHistory,
)
from app.documents.document_definition import (
    DocumentDefinition,
)
from app.services.prompt_loader import (
    PromptLoader,
)


class PromptBuilder:
    """
    Xây dựng Prompt hoàn chỉnh để gửi tới AI.
    """

    SECTION = "=" * 20

    CONTEXT_TITLE = "KNOWLEDGE"

    HISTORY_TITLE = "CONVERSATION HISTORY"

    USER_REQUEST_TITLE = "CURRENT USER REQUEST"

    def __init__(self):

        self.loader = PromptLoader()

    def build(
        self,
        document: DocumentDefinition,
        user_input: str,
        context: str = "",
        history: ConversationHistory | None = None,
    ) -> str:
        """
        Sinh Prompt hoàn chỉnh.
        """

        # =====================================
        # SYSTEM PROMPT
        # =====================================

        system_prompt = self.loader.load(
            "system",
            "system",
        ).strip()

        if not system_prompt:
            raise ValueError(
                "System Prompt đang trống."
            )

        # =====================================
        # DOCUMENT PROMPT
        # =====================================

        document_prompt = self.loader.load(
            document.prompt_category,
            document.prompt_name,
        ).strip()

        if not document_prompt:
            raise ValueError(
                "Document Prompt đang trống."
            )

        parts: list[str] = [
            system_prompt,
            "",
            document_prompt,
        ]

        # =====================================
        # KNOWLEDGE
        # =====================================

        if context.strip():

            parts.extend(
                [
                    "",
                    self.SECTION,
                    self.CONTEXT_TITLE,
                    self.SECTION,
                    "",
                    context.strip(),
                ]
            )

        # =====================================
        # HISTORY
        # =====================================

        if history and not history.is_empty():

            history_text = history.to_prompt()

            if history_text:

                parts.extend(
                    [
                        "",
                        self.SECTION,
                        self.HISTORY_TITLE,
                        self.SECTION,
                        "",
                        history_text,
                    ]
                )

        # =====================================
        # USER REQUEST
        # =====================================

        parts.extend(
            [
                "",
                self.SECTION,
                self.USER_REQUEST_TITLE,
                self.SECTION,
                "",
                user_input.strip(),
            ]
        )

        return "\n".join(parts).strip()