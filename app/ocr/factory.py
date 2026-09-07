"""
OCR Factory
-----------

Factory chuẩn hóa việc khởi tạo OCR Engine.

Sprint 14.1 chỉ định nghĩa contract.
Engine cụ thể sẽ được triển khai ở Sprint 14.2.
"""

from app.ocr.base import BaseOCR


class OCRFactoryError(Exception):
    """Lỗi khi khởi tạo OCR Engine."""


class OCRFactory:
    """
    Factory cho OCR Engine.

    Sprint 14.1:
        - Chỉ quản lý Engine đã được đăng ký.
        - Không chứa logic OCR.
        - Không phụ thuộc thư viện OCR cụ thể.
    """

    _engines: dict[str, type[BaseOCR]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        engine_class: type[BaseOCR],
    ) -> None:
        """
        Đăng ký một OCR Engine.
        """

        normalized_name = name.strip().lower()

        if not normalized_name:
            raise OCRFactoryError(
                "Tên OCR Engine không được để trống."
            )

        if not issubclass(engine_class, BaseOCR):
            raise OCRFactoryError(
                "OCR Engine phải kế thừa BaseOCR."
            )

        cls._engines[normalized_name] = engine_class

    @classmethod
    def create(
        cls,
        name: str,
    ) -> BaseOCR:
        """
        Tạo OCR Engine theo tên đã đăng ký.
        """

        normalized_name = name.strip().lower()

        engine_class = cls._engines.get(
            normalized_name
        )

        if engine_class is None:
            raise OCRFactoryError(
                f"OCR Engine chưa được đăng ký: {name}"
            )

        return engine_class()

    @classmethod
    def is_registered(
        cls,
        name: str,
    ) -> bool:
        """
        Kiểm tra OCR Engine đã được đăng ký hay chưa.
        """

        return name.strip().lower() in cls._engines

    @classmethod
    def registered_engines(cls) -> list[str]:
        """
        Trả về danh sách OCR Engine đã đăng ký.
        """

        return sorted(cls._engines.keys())