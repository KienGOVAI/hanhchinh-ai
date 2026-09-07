"""
Voice Conversation Service
--------------------------

Sprint 15.6.2

Pipeline:

    Voice Transcript
          ↓
    ConversationService
          ↓
    ConversationHistory
          ↓
    AssistantService
          ↓
    Assistant Response
          ↓
    Save Assistant Message

Mục tiêu:
    Voice sử dụng hệ thống Conversation hiện có của dự án.
    Không tạo Conversation system mới.
"""

from __future__ import annotations

from typing import Any

from app.conversation.conversation_history import ConversationHistory
from app.conversation.conversation_service import ConversationService
from app.knowledge.assistant.assistant_service import (
    AssistantResponse,
    AssistantService,
)


class VoiceConversationService:
    """
    Điều phối Voice + Conversation + AI.

    Service này nhận transcript đã được Voice Engine xử lý,
    đưa transcript vào Conversation hiện tại, lấy History,
    gửi History + câu hỏi hiện tại cho AssistantService,
    sau đó lưu câu trả lời của Assistant vào Conversation.
    """

    def __init__(
        self,
        conversation_service: ConversationService,
        assistant_service: AssistantService,
    ) -> None:
        if conversation_service is None:
            raise ValueError(
                "conversation_service không được để trống."
            )

        if assistant_service is None:
            raise ValueError(
                "assistant_service không được để trống."
            )

        self.conversation_service = conversation_service
        self.assistant_service = assistant_service

    # =========================================================
    # VALIDATION
    # =========================================================

    @staticmethod
    def _validate_transcript(
        transcript: str,
    ) -> str:
        """
        Kiểm tra và chuẩn hóa transcript.
        """

        if not isinstance(transcript, str):
            raise TypeError(
                "transcript phải là chuỗi."
            )

        normalized = transcript.strip()

        if not normalized:
            raise ValueError(
                "transcript không được để trống."
            )

        return normalized

    @staticmethod
    def _validate_conversation_id(
        conversation_id: str,
    ) -> str:
        """
        Kiểm tra conversation_id.
        """

        if not isinstance(
            conversation_id,
            str,
        ):
            raise TypeError(
                "conversation_id phải là chuỗi."
            )

        normalized = conversation_id.strip()

        if not normalized:
            raise ValueError(
                "conversation_id không được để trống."
            )

        return normalized

    # =========================================================
    # CONVERSATION
    # =========================================================

    def get_history(
        self,
        conversation_id: str,
    ) -> ConversationHistory:
        """
        Lấy ConversationHistory của conversation hiện tại.
        """

        conversation_id = (
            self._validate_conversation_id(
                conversation_id
            )
        )

        return self.conversation_service.history(
            conversation_id
        )

    # =========================================================
    # PROCESS
    # =========================================================

    def process(
        self,
        *,
        transcript: str,
        conversation_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> AssistantResponse:
        """
        Xử lý một lượt Voice Conversation.

        Pipeline:

            transcript
                ↓
            validate
                ↓
            save USER message
                ↓
            load History
                ↓
            AssistantService(question, history)
                ↓
            save ASSISTANT message
                ↓
            return response
        """

        transcript = self._validate_transcript(
            transcript
        )

        conversation_id = (
            self._validate_conversation_id(
                conversation_id
            )
        )

        # =====================================================
        # 1. VERIFY CONVERSATION
        # =====================================================

        self.conversation_service.get(
            conversation_id
        )

        # =====================================================
        # 2. SAVE USER / VOICE MESSAGE
        # =====================================================

        self.conversation_service.add_user_message(
            conversation_id,
            transcript,
        )

        # =====================================================
        # 3. LOAD HISTORY
        # =====================================================

        history = self.get_history(
            conversation_id
        )

        # =====================================================
        # 4. AI + MEMORY
        # =====================================================

        response = self.assistant_service.answer(
            transcript,
            history=history,
        )

        if not isinstance(
            response,
            AssistantResponse,
        ):
            raise TypeError(
                "AssistantService phải trả về "
                "AssistantResponse."
            )

        # =====================================================
        # 5. SAVE ASSISTANT MESSAGE
        # =====================================================

        self.conversation_service.add_assistant_message(
            conversation_id,
            response.answer,
        )

        # =====================================================
        # 6. RESPONSE METADATA
        # =====================================================

        response.metadata = dict(
            response.metadata
        )

        response.metadata.update(
            {
                "pipeline_stage": (
                    "voice_conversation"
                ),
                "conversation_id": (
                    conversation_id
                ),
                "transcript": transcript,
                "history_message_count": (
                    history.count()
                ),
                "history_used": True,
            }
        )

        if metadata:
            response.metadata.update(
                metadata
            )

        return response