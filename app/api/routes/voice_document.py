"""
Voice + Document API
--------------------

Sprint 15.5 — Voice + Document.

Pipeline:

    UploadFile
        ↓
    Validate
        ↓
    Temporary Audio
        ↓
    VoiceInput
        ↓
    Faster-Whisper
        ↓
    Transcript
        ↓
    VoiceDocumentService
        ↓
    AIService
        ↓
    DocumentBuilder
        ↓
    DOCX
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.document import DocumentResponse
from app.voice.document import VoiceDocumentService
from app.voice.engine import FasterWhisperVoiceEngine
from app.voice.models import VoiceInput


router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


SUPPORTED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".ogg",
    ".flac",
    ".webm",
}


voice_engine = FasterWhisperVoiceEngine(
    model_size="tiny",
    device="cpu",
    compute_type="int8",
)

voice_document_service = VoiceDocumentService()


@router.post(
    "/document",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload audio, AI và sinh DOCX",
    description=(
        "Sprint 15.5 — Voice + Document.\n\n"
        "Pipeline:\n\n"
        "    UploadFile\n"
        "        ↓\n"
        "    Validate\n"
        "        ↓\n"
        "    Temporary Audio\n"
        "        ↓\n"
        "    VoiceInput\n"
        "        ↓\n"
        "    Faster-Whisper\n"
        "        ↓\n"
        "    Transcript\n"
        "        ↓\n"
        "    VoiceDocumentService\n"
        "        ↓\n"
        "    AIService\n"
        "        ↓\n"
        "    DocumentBuilder\n"
        "        ↓\n"
        "    DOCX"
    ),
)
def upload_voice_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    title: str = Form(...),
    provider: str = Form("ollama"),
) -> DocumentResponse:
    """
    Upload audio → transcribe → AI → build DOCX.
    """

    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Định dạng audio không được hỗ trợ: "
                f"{extension or '(không có phần mở rộng)'}."
            ),
        )

    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:
            temp_path = temp_file.name
            temp_file.write(file.file.read())

        # FasterWhisperVoiceEngine nhận VoiceInput,
        # không nhận trực tiếp chuỗi đường dẫn.
        voice_input = VoiceInput(
            audio_path=temp_path,
        )

        transcription = voice_engine.transcribe(
            voice_input,
        )

        transcript = transcription.text.strip()

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Không nhận dạng được nội dung từ audio.",
            )

        result = voice_document_service.process(
            transcript=transcript,
            document_type=document_type,
            title=title,
            provider=provider,
            metadata={
                "pipeline_stage": "voice_document",
                "voice_engine": "faster-whisper",
                "voice_model": "tiny",
                "voice_language": "vi",
                "voice_duration": transcription.duration,
                "original_filename": filename,
                "transcript": transcript,
            },
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.message,
            )

        if not result.file_name:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI xử lý thành công nhưng không tạo được file DOCX.",
            )

        return result

    except HTTPException:
        raise

    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex),
        ) from ex

    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except OSError:
                pass
