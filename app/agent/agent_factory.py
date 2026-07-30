"""
Agent Factory
-------------
Khởi tạo Hành Chính AI Agent với đầy đủ các thành phần.
"""

from app.agent.default_planner import DefaultPlanner
from app.agent.hanh_chinh_agent import HanhChinhAgent
from app.agent.intents.rule_based_classifier import RuleBasedClassifier
from app.agent.memory.in_memory import InMemoryMemory
from app.agent.tool_dispatcher import ToolDispatcher
from app.agent.tool_registry import ToolRegistry
from app.agent.agent_validator import AgentValidator

# Các Tool cần được import và đăng ký
from app.agent.tools.chat_tool import ChatTool
from app.agent.tools.document_tool import DocumentTool
from app.agent.tools.rag_tool import RAGTool


class AgentFactory:

    @staticmethod
    def create() -> HanhChinhAgent:

        registry = ToolRegistry()

        registry.register(ChatTool())
        registry.register(DocumentTool())
        registry.register(RAGTool())

        dispatcher = ToolDispatcher(registry)

        validator = AgentValidator(registry)

        memory = InMemoryMemory()

        classifier = RuleBasedClassifier()

        planner = DefaultPlanner()

        return HanhChinhAgent(
            planner=planner,
            dispatcher=dispatcher,
            registry=registry,
            validator=validator,
            memory=memory,
            intent_classifier=classifier,
        )