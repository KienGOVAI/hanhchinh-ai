from app.voice import BaseVoice, VoiceFactory, VoiceInput, VoiceResult


class DummyVoiceEngine(BaseVoice):
    def transcribe(self, voice_input: VoiceInput) -> VoiceResult:
        return VoiceResult(
            text="Xin chào Hành Chính AI",
            confidence=1.0,
            language=voice_input.language,
        )


def test_voice_input():
    voice_input = VoiceInput(
        audio_path="sample.wav",
        language="vi",
    )

    assert voice_input.audio_path == "sample.wav"
    assert voice_input.language == "vi"


def test_voice_result():
    result = VoiceResult(
        text="Xin chào",
        confidence=0.95,
        language="vi",
    )

    assert result.text == "Xin chào"
    assert result.confidence == 0.95


def test_voice_factory():
    VoiceFactory.clear()

    VoiceFactory.register(
        "dummy",
        DummyVoiceEngine,
    )

    engine = VoiceFactory.create("dummy")

    result = engine.transcribe(
        VoiceInput(
            audio_path="sample.wav",
            language="vi",
        )
    )

    assert isinstance(engine, DummyVoiceEngine)
    assert result.text == "Xin chào Hành Chính AI"
    assert "dummy" in VoiceFactory.available()

    VoiceFactory.clear()