"""
Voice Conversation API
----------------------

Sprint 15.6.3

Pipeline:

    Audio
      ↓
    Faster-Whisper
      ↓
    Transcript
      ↓
    ConversationService
      ↓
    ConversationHistory
      ↓
    AssistantService + Memory
      ↓
    Save Assistant Message
      ↓
    HTTP Response
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field

from app.api.routes.assistant import (
    get_assistant_service,
    get_conversation_service,
)
from app.knowledge.assistant.assistant_service import (
    AssistantResponse,
)
from app.voice.conversation import (
    VoiceConversationService,
)
from app.voice.engine import (
    FasterWhisperVoiceEngine,
)
from app.voice.models import VoiceInput


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


# ============================================================
# SCHEMA
# ============================================================

class VoiceConversationResponse(BaseModel):
    success: bool = True
    conversation_id: str
    file_name: str
    transcript: str
    answer: str
    language: str = "vi"
    duration: float | None = None
    citations: list[Any] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    message: str = "Voice Conversation xử lý thành công."


# ============================================================
# RUNTIME
# ============================================================

voice_engine = FasterWhisperVoiceEngine(
    model_size="tiny",
    device="cpu",
    compute_type="int8",
)


SUPPORTED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".ogg",
    ".flac",
    ".webm",
}


# ============================================================
# HELPERS
# ============================================================

def _validate_filename(
    filename: str | None,
) -> str:
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên file không hợp lệ.",
        )

    suffix = Path(filename).suffix.lower()

    if suffix not in SUPPORTED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Định dạng audio không được hỗ trợ. "
                "Cho phép: "
                + ", ".join(
                    sorted(SUPPORTED_AUDIO_EXTENSIONS)
                )
            ),
        )

    return Path(filename).name


def _save_upload_file(
    file: UploadFile,
    filename: str,
) -> Path:
    suffix = Path(filename).suffix.lower()

    temporary_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    )

    temporary_path = Path(
        temporary_file.name
    )

    try:
        while True:
            chunk = file.file.read(1024 * 1024)

            if not chunk:
                break

            temporary_file.write(chunk)

    finally:
        temporary_file.close()

    return temporary_path


def _build_response(
    *,
    conversation_id: str,
    filename: str,
    transcript: str,
    language: str,
    voice_result_metadata: dict[str, Any],
    duration: float | None,
    assistant_response: AssistantResponse,
) -> VoiceConversationResponse:
    return VoiceConversationResponse(
        success=True,
        conversation_id=conversation_id,
        file_name=filename,
        transcript=transcript,
        answer=assistant_response.answer,
        language=language,
        duration=duration,
        citations=list(
            assistant_response.citations
        ),
        metadata=dict(
            assistant_response.metadata
        ),
        message="Voice Conversation xử lý thành công.",
    )


# ============================================================
# API
# ============================================================

@router.post(
    "/conversation",
    response_model=VoiceConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload audio và tiếp tục hội thoại với AI",
)
def upload_voice_conversation(
    file: UploadFile = File(...),
    conversation_id: str = Form(...),
    language: str = Form("vi"),
) -> VoiceConversationResponse:
    """
    Sprint 15.6.3 — Voice + Conversation.

    Audio
        ↓
    Faster-Whisper
        ↓
    Transcript
        ↓
    Conversation History
        ↓
    Assistant + Memory
        ↓
    Save User + Assistant
        ↓
    Response
    """

    filename = _validate_filename(
        file.filename
    )

    if not isinstance(language, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="language phải là chuỗi.",
        )

    language = language.strip()

    if not language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="language không được để trống.",
        )

    temporary_path: Path | None = None

    try:
        # --------------------------------------------------------
        # 1. VERIFY CONVERSATION
        # --------------------------------------------------------

        conversation_service = (
            get_conversation_service()
        )

        conversation_service.get(
            conversation_id.strip()
        )

        # --------------------------------------------------------
        # 2. SAVE AUDIO
        # --------------------------------------------------------

        temporary_path = _save_upload_file(
            file,
            filename,
        )

        # --------------------------------------------------------
        # 3. VOICE → TRANSCRIPT
        # --------------------------------------------------------

        voice_input = VoiceInput(
            audio_path=str(temporary_path),
            language=language,
        )

        voice_result = voice_engine.transcribe(
            voice_input
        )

        transcript = voice_result.text.strip()

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Voice Engine không tạo được transcript.",
            )

        # --------------------------------------------------------
        # 4. CONVERSATION + MEMORY + AI
        # --------------------------------------------------------

        assistant_service = (
            get_assistant_service()
        )

        voice_conversation_service = (
            VoiceConversationService(
                conversation_service=conversation_service,
                assistant_service=assistant_service,
            )
        )

        assistant_response = (
            voice_conversation_service.process(
                transcript=transcript,
                conversation_id=conversation_id,
                metadata={
                    "file_name": filename,
                    "language": language,
                    "voice_duration": voice_result.duration,
                    "voice_metadata": dict(
                        voice_result.metadata
                    ),
                },
            )
        )

        # --------------------------------------------------------
        # 5. RESPONSE
        # --------------------------------------------------------

        return _build_response(
            conversation_id=conversation_id,
            filename=filename,
            transcript=transcript,
            language=language,
            voice_result_metadata=dict(
                voice_result.metadata
            ),
            duration=voice_result.duration,
            assistant_response=assistant_response,
        )

    except HTTPException:
        raise

    except ValueError as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ex),
        ) from ex

    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex),
        ) from ex

    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(
                    missing_ok=True
                )
            except Exception:
                pass
