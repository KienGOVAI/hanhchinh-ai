"""
Default Planner
"""

from app.agent.agent_request import AgentRequest
from app.agent.execution_plan import (
    ExecutionPlan,
    ExecutionStep,
)
from app.agent.intents.intent import Intent
from app.agent.intents import intents


class DefaultPlanner:

    def plan(
        self,
        request: AgentRequest,
        intent: Intent,
    ) -> ExecutionPlan:

        steps = []

        # -------------------------
        # Soạn văn bản
        # -------------------------

        if intent.name == intents.DOCUMENT:

            steps.append(

                ExecutionStep(

                    tool_name="document",

                    parameters={

                        "prompt": request.user_input
                    }
                )
            )

        # -------------------------
        # Tra cứu
        # -------------------------

        elif intent.name == intents.RAG:

            steps.append(

                ExecutionStep(

                    tool_name="rag",

                    parameters={

                        "question": request.user_input
                    }
                )
            )

        # -------------------------
        # OCR
        # -------------------------

        elif intent.name == intents.OCR:

            steps.append(

                ExecutionStep(

                    tool_name="ocr",

                    parameters={}
                )
            )

        # -------------------------
        # Chat
        # -------------------------

        else:

            steps.append(

                ExecutionStep(

                    tool_name="chat",

                    parameters={

                        "prompt": request.user_input
                    }
                )
            )

        return ExecutionPlan(
            steps=steps
        )