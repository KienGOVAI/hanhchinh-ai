from app.voice.base import BaseVoice
from app.voice.factory import VoiceFactory
from app.voice.models import VoiceInput, VoiceResult
from app.voice.engine import FasterWhisperVoiceEngine


VoiceFactory.register(
    "faster-whisper",
    FasterWhisperVoiceEngine,
)


__all__ = [
    "BaseVoice",
    "VoiceFactory",
    "VoiceInput",
    "VoiceResult",
    "FasterWhisperVoiceEngine",
]