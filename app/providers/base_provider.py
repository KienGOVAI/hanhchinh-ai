"""
Base Provider
-------------

Lớp cơ sở cho toàn bộ AI Provider.
"""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Base class của toàn bộ AI Provider.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Tên Provider.
        """
        ...

    @abstractmethod
    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Sinh nội dung từ AI.

        Parameters
        ----------
        prompt : str
            Prompt hoàn chỉnh.

        Returns
        -------
        str
            Nội dung AI sinh ra.
        """
        ...

    def health_check(self) -> bool:
        """
        Kiểm tra Provider có sẵn sàng hay không.

        Có thể override ở từng Provider nếu cần.
        """
        return True