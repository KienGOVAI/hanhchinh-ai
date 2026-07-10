from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "Hành Chính AI")
APP_VERSION = os.getenv("APP_VERSION", "0.0.1")

DEBUG = os.getenv("DEBUG", "True")

DATABASE_URL = os.getenv("DATABASE_URL", "")

# ==========================================
# AI CONFIG
# ==========================================

AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "deepseek/deepseek-chat-v3-0324:free"
)

# Ollama
OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b"
)