from __future__ import annotations

import os
from typing import Type

from app.voice.base import BaseVoice


class VoiceFactory:
    _engines: dict[str, Type[BaseVoice]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        engine_class: Type[BaseVoice],
    ) -> None:
        if not isinstance(name, str):
            raise TypeError("Tên Voice Engine phải là chuỗi.")

        name = name.strip().lower()

        if not name:
            raise ValueError("Tên Voice Engine không được để trống.")

        if not issubclass(engine_class, BaseVoice):
            raise TypeError(
                "Voice Engine phải kế thừa BaseVoice."
            )

        cls._engines[name] = engine_class

    @classmethod
    def create(
        cls,
        name: str,
        **kwargs,
    ) -> BaseVoice:
        if not isinstance(name, str):
            raise TypeError("Tên Voice Engine phải là chuỗi.")

        name = name.strip().lower()

        if name not in cls._engines:
            available = ", ".join(sorted(cls._engines)) or "chưa có"

            raise ValueError(
                f"Không tìm thấy Voice Engine '{name}'. "
                f"Engine hiện có: {available}."
            )

        engine_class = cls._engines[name]

        return engine_class(**kwargs)

    @classmethod
    def create_default(cls, **kwargs) -> BaseVoice:
        engine_name = os.getenv(
            "VOICE_ENGINE",
            "faster-whisper",
        ).strip().lower()

        return cls.create(
            engine_name,
            **kwargs,
        )

    @classmethod
    def available(cls) -> list[str]:
        return sorted(cls._engines.keys())

    @classmethod
    def clear(cls) -> None:
        cls._engines.clear()