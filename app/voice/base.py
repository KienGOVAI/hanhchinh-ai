from __future__ import annotations

from abc import ABC, abstractmethod

from app.voice.models import VoiceInput, VoiceResult


class BaseVoice(ABC):
    """
    Interface chuẩn cho Voice/Speech-to-Text Engine.

    Sprint 15.2 sẽ triển khai engine cụ thể từ interface này.
    """

    @abstractmethod
    def transcribe(self, voice_input: VoiceInput) -> VoiceResult:
        """
        Chuyển audio thành văn bản.

        Args:
            voice_input: Dữ liệu audio đầu vào.

        Returns:
            VoiceResult chứa transcript.
        """
        raise NotImplementedError