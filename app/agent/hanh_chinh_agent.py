"""
Hành Chính AI Agent
-------------------
"""

from app.agent.agent import Agent


class HanhChinhAgent(Agent):

    def __init__(
        self,
        planner,
        dispatcher,
    ):

        self.planner = planner
        self.dispatcher = dispatcher

    # ============================================

    def execute(
        self,
        request: str,
    ):

        plan = self.planner.plan(
            request
        )

        result = self.dispatcher.dispatch(
            plan
        )

        return result