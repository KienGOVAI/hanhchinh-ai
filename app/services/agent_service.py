"""
Agent Service
"""

from app.agent.agent_factory import AgentFactory
from app.agent.agent_request import AgentRequest


class AgentService:

    def __init__(self):

        self.agent = AgentFactory.create()

    def execute(
        self,
        prompt: str,
        session_id: str,
    ):

        request = AgentRequest(
            user_input=prompt,
            session_id=session_id,
        )

        return self.agent.execute(
            request
        )