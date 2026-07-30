from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionPlan:
    """
    Kế hoạch thực thi do Planner sinh ra.
    """

    tool_name: str

    parameters: dict[str, Any] = field(
        default_factory=dict
    )