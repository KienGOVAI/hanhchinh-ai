from app.agent.intents.intent import Intent
from app.agent.intents.intent_classifier import IntentClassifier
from app.agent.intents import intents


class RuleBasedClassifier(
    IntentClassifier
):

    def classify(
        self,
        request: str,
    ) -> Intent:

        text = request.lower()

        if any(
            keyword in text
            for keyword in [
                "soạn",
                "quyết định",
                "công văn",
                "thông báo",
                "kế hoạch",
                "tờ trình",
            ]
        ):
            return Intent(

                name=intents.DOCUMENT,

                confidence=0.95,
            )

        if any(
            keyword in text
            for keyword in [
                "tra cứu",
                "nghị định",
                "thông tư",
                "luật",
                "quy định",
            ]
        ):
            return Intent(

                name=intents.RAG,

                confidence=0.90,
            )

        if any(
            keyword in text
            for keyword in [
                "ocr",
                "quét",
                "ảnh",
                "pdf",
            ]
        ):
            return Intent(

                name=intents.OCR,

                confidence=0.90,
            )

        return Intent(

            name=intents.CHAT,

            confidence=0.60,
        )