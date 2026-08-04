"""
Document Service
----------------

Điều phối toàn bộ quy trình sinh văn bản.
"""

from app.conversation.conversation_service import (
    ConversationService,
)
from app.documents.document_factory import (
    DocumentFactory,
)
from app.schemas.document import (
    DocumentRequest,
    DocumentResponse,
)
from app.services.ai_service import (
    AIService,
)
from app.services.document_builder import (
    DocumentBuilder,
)


def generate_document(
    data: DocumentRequest,
) -> DocumentResponse:
    """
    Sinh văn bản hoàn chỉnh.
    """

    try:

        # ==================================================
        # DOCUMENT
        # ==================================================

        document = DocumentFactory.create(
            data.type
        )

        # ==================================================
        # CONVERSATION
        # ==================================================

        conversation_service = ConversationService()

        conversation = conversation_service.create(
            title=data.title,
        )

        conversation_service.add_user_message(
            conversation.conversation_id,
            data.prompt,
        )

        history = conversation_service.history(
            conversation.conversation_id
        )

        # ==================================================
        # AI SERVICE
        # ==================================================

        ai_service = AIService()

        ai_content = ai_service.generate_document(
            document_type=document.document_type,
            title=data.title,
            content=data.prompt,
            history=history,
        )

        if not isinstance(ai_content, str):
            raise TypeError(
                f"AIService phải trả về str, nhận được "
                f"{type(ai_content).__name__}"
            )

        ai_content = ai_content.strip()

        if not ai_content:
            raise RuntimeError(
                "AI không sinh được nội dung."
            )

        # ==================================================
        # SAVE CONVERSATION
        # ==================================================

        conversation_service.add_assistant_message(
            conversation.conversation_id,
            ai_content,
        )

        # ==================================================
        # BUILD WORD
        # ==================================================

        data.prompt = ai_content
        data.content = ai_content
        builder = DocumentBuilder()

        result = builder.build(
            data
        )

        # ==================================================
        # RESPONSE
        # ==================================================

        return DocumentResponse(
            success=result["success"],
            provider=data.provider,
            document_type=document.document_type,
            file_name=result["file_name"],
            content=ai_content,
            message="Sinh văn bản thành công.",
        )

    except Exception as ex:

        return DocumentResponse(
            success=False,
            provider=data.provider,
            document_type=data.type,
            file_name="",
            content="",
            message=str(ex),
        )