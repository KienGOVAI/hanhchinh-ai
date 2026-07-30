"""
Planner Interface
-----------------
"""

from abc import ABC, abstractmethod

from app.agent.agent_request import AgentRequest
from app.agent.execution_plan import ExecutionPlan
from app.agent.intents.intent import Intent


class Planner(ABC):
    """
    Interface lập kế hoạch thực thi.
    """

    @abstractmethod
    def plan(
        self,
        request: AgentRequest,
        intent: Intent,
    ) -> ExecutionPlan:
        """
        Sinh Execution Plan.
        """
        raise NotImplementedError