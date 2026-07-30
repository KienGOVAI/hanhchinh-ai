from dataclasses import dataclass, field
from typing import Any


@dataclass
class StepResult:

    step_id: str

    tool_name: str

    success: bool

    output: Any = None

    error: str | None = None


@dataclass
class ExecutionResult:

    success: bool

    results: list[StepResult] = field(
        default_factory=list
    )

    final_output: Any = None