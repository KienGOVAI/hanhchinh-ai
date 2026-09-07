from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VoiceInput:
    """
    Dữ liệu đầu vào cho Voice/Speech-to-Text.

    Có thể nhận audio từ:
    - file upload
    - microphone
    - API request
    - nguồn audio khác
    """

    audio_path: str
    language: str = "vi"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.audio_path, str):
            raise TypeError("audio_path phải là chuỗi.")

        if not self.audio_path.strip():
            raise ValueError("audio_path không được để trống.")

        if not isinstance(self.language, str):
            raise TypeError("language phải là chuỗi.")

        if not self.language.strip():
            raise ValueError("language không được để trống.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata phải là dict.")


@dataclass
class VoiceResult:
    """
    Kết quả Speech-to-Text.

    text:
        Nội dung lời nói sau khi chuyển thành văn bản.

    confidence:
        Độ tin cậy của engine, nếu engine cung cấp.

    language:
        Ngôn ngữ được sử dụng để nhận dạng.

    duration:
        Thời lượng audio, nếu xác định được.

    metadata:
        Thông tin bổ sung từ engine/runtime.
    """

    text: str
    confidence: float | None = None
    language: str = "vi"
    duration: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError("text phải là chuỗi.")

        if self.confidence is not None:
            if not isinstance(self.confidence, (int, float)):
                raise TypeError("confidence phải là số hoặc None.")

            if not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("confidence phải nằm trong khoảng 0.0 đến 1.0.")

        if not isinstance(self.language, str):
            raise TypeError("language phải là chuỗi.")

        if self.duration is not None:
            if not isinstance(self.duration, (int, float)):
                raise TypeError("duration phải là số hoặc None.")

            if float(self.duration) < 0:
                raise ValueError("duration không được âm.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata phải là dict.")