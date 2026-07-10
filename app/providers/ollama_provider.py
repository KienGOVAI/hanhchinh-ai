import requests


class OllamaProvider:

    BASE_URL = "http://localhost:11434/api/generate"

    MODEL = "qwen3:8b"

    def generate(
        self,
        prompt: str
    ) -> str:

        payload = {
            "model": self.MODEL,
            "prompt": prompt,
            "stream": False
        }

        try:

            response = requests.post(
                self.BASE_URL,
                json=payload,
                timeout=300
            )

            response.raise_for_status()

            data = response.json()

            return data["response"]

        except Exception as ex:

            return f"Lỗi Ollama:\n\n{ex}"