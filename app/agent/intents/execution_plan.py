from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionStep:

    tool_name: str

    parameters: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ExecutionPlan:

    steps: list[ExecutionStep] = field(
        default_factory=list
    )