"""
In-memory Conversation Store
"""

from app.agent.memory.conversation import Conversation
from app.agent.memory.memory import Memory


class InMemoryMemory(
    Memory
):

    def __init__(self):

        self._memory = {}

    def get(
        self,
        session_id: str,
    ) -> Conversation:

        if session_id not in self._memory:

            self._memory[session_id] = Conversation(
                session_id=session_id
            )

        return self._memory[
            session_id
        ]

    def save(
        self,
        conversation: Conversation,
    ):

        self._memory[
            conversation.session_id
        ] = conversation