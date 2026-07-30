"""
Memory Interface
"""

from abc import ABC, abstractmethod

from app.agent.memory.conversation import Conversation


class Memory(ABC):

    @abstractmethod
    def get(
        self,
        session_id: str,
    ) -> Conversation:
        ...

    @abstractmethod
    def save(
        self,
        conversation: Conversation,
    ) -> None:
        ...