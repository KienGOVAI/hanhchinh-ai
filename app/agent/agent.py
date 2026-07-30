"""
Agent Core
----------

Agent trung tâm điều phối toàn bộ hệ thống.
"""

from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """
    Abstract Agent.
    """

    @abstractmethod
    def execute(
        self,
        request: str,
    ) -> Any:
        """
        Thực hiện yêu cầu của người dùng.
        """
        raise NotImplementedError