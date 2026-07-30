"""
Tool Interface
--------------

Định nghĩa interface chuẩn cho tất cả Tool.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """
    Kết quả thực thi Tool.
    """

    success: bool

    output: Any = None

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class Tool(ABC):
    """
    Abstract Tool.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Tên Tool.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Mô tả Tool.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        """
        Thực thi Tool.
        """
        raise NotImplementedError
    from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """
    Kết quả thực thi Tool.
    """

    success: bool

    output: Any = None

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )