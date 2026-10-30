"""Central configuration. All secrets come from environment variables (.env)."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

NAME = os.getenv("ASSISTANT_NAME", "Jarvis")
LANG = os.getenv("SPEECH_LANG", "en-IN")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Jaipur")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "claude-haiku-5-5")
try:
    AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "200"))
except ValueError:
    AI_MAX_TOKENS = 200
AI_MAX_TOKENS = min(max(AI_MAX_TOKENS, 1), 1000)
DB_PATH = Path(os.getenv("DB_PATH", Path(__file__).resolve().parent.parent / "jarvis.db"))
HTTP_TIMEOUT = 6