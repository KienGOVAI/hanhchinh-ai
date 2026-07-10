import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(BASE_DIR))

from app.providers.ollama_provider import OllamaProvider

provider = OllamaProvider()

result = provider.generate(
    "Hãy trả lời đúng duy nhất một từ: OK"
)

print(result)