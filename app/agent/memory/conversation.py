"""
Conversation Model
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.agent.memory.message import Message


@dataclass(slots=True)
class Conversation:
    session_id: str

    messages: list[Message] = field(
        default_factory=list
    )

    def add(self, message: Message):

        self.messages.append(message)

    def last(self):

        if not self.messages:
            return None

        return self.messages[-1]