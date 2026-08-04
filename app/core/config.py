"""
Application Configuration
-------------------------

Quản lý toàn bộ cấu hình hệ thống.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ==========================================================
# BASE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

# ==========================================================
# APP
# ==========================================================

APP_NAME = os.getenv("APP_NAME", "Hành Chính AI")

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

HOST = os.getenv("HOST", "0.0.0.0")

PORT = int(os.getenv("PORT", "8000"))

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "hanhchinh-ai-secret",
)

# ==========================================================
# DATABASE
# ==========================================================

DATABASE_URL = os.getenv("DATABASE_URL", "")

# ==========================================================
# AI
# ==========================================================

AI_PROVIDER = os.getenv(
    "AI_PROVIDER",
    "ollama",
).lower()

# ==========================================================
# OLLAMA
# ==========================================================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b",
)

OLLAMA_TIMEOUT = int(
    os.getenv("OLLAMA_TIMEOUT", "300")
)

# ==========================================================
# GEMINI
# ==========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "",
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)
# ==========================================================
# OPENAI
# ==========================================================

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "",
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4.1-mini",
)

OPENAI_TIMEOUT = int(
    os.getenv("OPENAI_TIMEOUT", "300")
)
# ==========================================================
# OPENROUTER
# ==========================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "",
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "deepseek/deepseek-chat-v3-0324:free",
)

OPENROUTER_TIMEOUT = int(
    os.getenv("OPENROUTER_TIMEOUT", "120")
)