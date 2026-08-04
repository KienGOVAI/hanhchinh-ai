"""
Prompt Context
--------------

Đóng gói toàn bộ dữ liệu được sử dụng để xây dựng Prompt.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class PromptContext:
    """
    Chứa toàn bộ ngữ cảnh trước khi gửi tới PromptBuilder.
    """

    context: str = ""

    knowledge: str = ""

    memory: str = ""

    examples: list[str] = field(default_factory=list)

    metadata: dict[str, str] = field(default_factory=dict)

    def has_context(self) -> bool:
        """
        Có ngữ cảnh hay không.
        """
        return bool(self.context.strip())

    def has_knowledge(self) -> bool:
        """
        Có tri thức bổ sung hay không.
        """
        return bool(self.knowledge.strip())

    def has_memory(self) -> bool:
        """
        Có bộ nhớ hội thoại hay không.
        """
        return bool(self.memory.strip())

    def has_examples(self) -> bool:
        """
        Có ví dụ Few-shot hay không.
        """
        return len(self.examples) > 0