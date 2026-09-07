from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel

from app.voice.base import BaseVoice
from app.voice.models import VoiceInput, VoiceResult


class FasterWhisperVoiceEngine(BaseVoice):
    """Voice Engine sử dụng faster-whisper để Speech-to-Text."""

    def __init__(
        self,
        model_size: str | None = None,
        device: str | None = None,
        compute_type: str | None = None,
        download_root: str | None = None,
    ) -> None:
        self.model_size = (
            model_size or os.getenv("VOICE_MODEL_SIZE", "small")
        ).strip()

        self.device = (
            device or os.getenv("VOICE_DEVICE", "cpu")
        ).strip().lower()

        self.compute_type = (
            compute_type or os.getenv("VOICE_COMPUTE_TYPE", "int8")
        ).strip().lower()

        self.download_root = download_root or os.getenv("VOICE_MODEL_DIR")

        if not self.model_size:
            raise ValueError("model_size không được để trống.")

        if not self.device:
            raise ValueError("device không được để trống.")

        if not self.compute_type:
            raise ValueError("compute_type không được để trống.")

        model_kwargs: dict[str, Any] = {
            "device": self.device,
            "compute_type": self.compute_type,
        }

        if self.download_root:
            model_kwargs["download_root"] = self.download_root

        self.model = WhisperModel(
            self.model_size,
            **model_kwargs,
        )

    def transcribe(self, voice_input: VoiceInput) -> VoiceResult:
        """Chuyển file audio thành văn bản."""

        audio_path = Path(voice_input.audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy file audio: {audio_path}"
            )

        if not audio_path.is_file():
            raise ValueError(
                f"Audio path không phải file: {audio_path}"
            )

        started_at = time.perf_counter()

        segments, info = self.model.transcribe(
            str(audio_path),
            language=voice_input.language,
            beam_size=5,
            vad_filter=True,
        )

        texts: list[str] = []

        for segment in segments:
            text = segment.text.strip()
            if text:
                texts.append(text)

        text = " ".join(texts).strip()

        elapsed = time.perf_counter() - started_at

        duration = getattr(info, "duration", None)
        detected_language = getattr(
            info,
            "language",
            voice_input.language,
        )

        language_probability = getattr(
            info,
            "language_probability",
            None,
        )

        metadata: dict[str, Any] = {
            "engine": "faster-whisper",
            "model": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "processing_time_seconds": round(elapsed, 3),
            "audio_path": str(audio_path),
        }

        if language_probability is not None:
            metadata["language_probability"] = float(
                language_probability
            )

        return VoiceResult(
            text=text,
            confidence=None,
            language=detected_language,
            duration=float(duration) if duration is not None else None,
            metadata=metadata,
        )