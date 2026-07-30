"""
Intent Classifier Interface
"""

from abc import ABC, abstractmethod

from app.agent.intents.intent import Intent


class IntentClassifier(ABC):

    @abstractmethod
    def classify(
        self,
        request: str,
    ) -> Intent:
        raise NotImplementedError