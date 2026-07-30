"""
Agent Validator
---------------

Kiểm tra tính hợp lệ của Agent trước khi thực thi.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.agent.agent_request import AgentRequest
from app.agent.execution_plan import ExecutionPlan
from app.agent.execution_result import ExecutionResult
from app.agent.tool_registry import ToolRegistry


@dataclass(slots=True)
class ValidationResult:
    """
    Kết quả kiểm tra.
    """

    success: bool

    errors: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)


class AgentValidator:

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:

        self.registry = registry

    # ==========================================
    # Validate Request
    # ==========================================

    def validate_request(
        self,
        request: AgentRequest,
    ) -> ValidationResult:

        result = ValidationResult(True)

        if not request.user_input.strip():

            result.success = False

            result.errors.append(
                "User input is empty."
            )

        return result

    # ==========================================
    # Validate Plan
    # ==========================================

    def validate_plan(
        self,
        plan: ExecutionPlan,
    ) -> ValidationResult:

        result = ValidationResult(True)

        if not plan.steps:

            result.success = False

            result.errors.append(
                "Execution plan is empty."
            )

            return result

        for step in plan.steps:

            if not self.registry.exists(
                step.tool_name
            ):

                result.success = False

                result.errors.append(

                    f"Tool '{step.tool_name}' is not registered."
                )

        return result

    # ==========================================
    # Validate Result
    # ==========================================

    def validate_result(
        self,
        execution: ExecutionResult,
    ) -> ValidationResult:

        result = ValidationResult(True)

        if not execution.success:

            result.warnings.append(
                "Execution completed with failures."
            )

        if not execution.results:

            result.warnings.append(
                "No execution steps were recorded."
            )

        return result