from __future__ import annotations

from app.agent.execution_plan import ExecutionPlan
from app.agent.execution_result import (
    ExecutionResult,
    StepResult,
)
from app.agent.tool_registry import ToolRegistry
from app.agent.tools.tool import ToolRequest


class ToolDispatcher:

    def __init__(
        self,
        registry: ToolRegistry,
    ):
        self.registry = registry

    # =====================================

    def dispatch(
        self,
        plan: ExecutionPlan,
    ) -> ExecutionResult:

        results = []

        context = {}

        for step in plan.steps:

            tool = self.registry.get(
                step.tool_name
            )

            request = ToolRequest(

                parameters=step.parameters
            )

            tool_result = tool.execute(
                request
            )

            results.append(

                StepResult(

                    step_id=step.id,

                    tool_name=step.tool_name,

                    success=tool_result.success,

                    output=tool_result.output,

                    error=tool_result.error,
                )
            )

            if not tool_result.success:

                return ExecutionResult(

                    success=False,

                    results=results,

                    final_output=None,
                )

            context[step.id] = tool_result.output

        return ExecutionResult(

            success=True,

            results=results,

            final_output=results[-1].output
            if results
            else None,
        )