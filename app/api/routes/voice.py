from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.voice import VoiceUploadResponse
from app.schemas.voice_ai import VoiceAIResponse
from app.voice import VoiceFactory, VoiceInput
from app.voice.ai import VoiceAIService


router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


SUPPORTED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".mp4",
    ".aac",
    ".flac",
    ".ogg",
    ".webm",
}


_voice_ai_service: VoiceAIService | None = None


def configure_voice_ai_service(service: VoiceAIService) -> None:
    global _voice_ai_service
    _voice_ai_service = service


def get_voice_ai_service() -> VoiceAIService:
    if _voice_ai_service is None:
        raise HTTPException(
            status_code=503,
            detail="Voice AI Service chưa được cấu hình.",
        )

    return _voice_ai_service


def _validate_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Tên file audio không được để trống.",
        )

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Định dạng audio không được hỗ trợ: {extension}. "
                f"Hỗ trợ: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            ),
        )

    return extension


def _transcribe_audio(
    file: UploadFile,
) -> tuple[str, str, float | None, dict]:
    extension = _validate_filename(file.filename)

    raise RuntimeError(
        "_transcribe_audio không được gọi trực tiếp."
    )


@router.post(
    "/upload",
    response_model=VoiceUploadResponse,
)
async def upload_voice(
    file: UploadFile = File(...),
) -> VoiceUploadResponse:
    extension = _validate_filename(file.filename)

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="File audio rỗng.",
        )

    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        engine = VoiceFactory.create(
            "faster-whisper",
            model_size=os.getenv(
                "VOICE_MODEL_SIZE",
                "tiny",
            ),
            device=os.getenv(
                "VOICE_DEVICE",
                "cpu",
            ),
            compute_type=os.getenv(
                "VOICE_COMPUTE_TYPE",
                "int8",
            ),
        )

        result = engine.transcribe(
            VoiceInput(
                audio_path=temp_path,
                language="vi",
                metadata={
                    "original_filename": file.filename,
                },
            )
        )

        metadata = dict(result.metadata)
        metadata["original_filename"] = file.filename

        return VoiceUploadResponse(
            success=True,
            file_name=file.filename or "",
            text=result.text,
            language=result.language,
            confidence=result.confidence,
            duration=result.duration,
            metadata=metadata,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Voice Transcription lỗi: {exc}",
        ) from exc

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass


@router.post(
    "/ai",
    response_model=VoiceAIResponse,
)
async def voice_ai(
    file: UploadFile = File(...),
) -> VoiceAIResponse:
    extension = _validate_filename(file.filename)

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="File audio rỗng.",
        )

    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        engine = VoiceFactory.create(
            "faster-whisper",
            model_size=os.getenv(
                "VOICE_MODEL_SIZE",
                "tiny",
            ),
            device=os.getenv(
                "VOICE_DEVICE",
                "cpu",
            ),
            compute_type=os.getenv(
                "VOICE_COMPUTE_TYPE",
                "int8",
            ),
        )

        voice_result = engine.transcribe(
            VoiceInput(
                audio_path=temp_path,
                language="vi",
                metadata={
                    "original_filename": file.filename,
                },
            )
        )

        ai_service = get_voice_ai_service()

        ai_result = ai_service.process(
            transcript=voice_result.text,
            metadata=voice_result.metadata,
        )

        metadata = dict(voice_result.metadata)
        metadata["original_filename"] = file.filename
        metadata["pipeline_stage"] = "voice_ai"

        if isinstance(ai_result.metadata, dict):
            metadata["ai"] = ai_result.metadata

        return VoiceAIResponse(
            success=True,
            file_name=file.filename or "",
            transcript=voice_result.text,
            answer=ai_result.answer,
            language=voice_result.language,
            duration=voice_result.duration,
            metadata=metadata,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Voice + AI lỗi: {exc}",
        ) from exc

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass