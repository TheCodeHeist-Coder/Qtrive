import os
from pathlib import Path

from dotenv import load_dotenv

# Load apps/genAI/.env explicitly. A bare load_dotenv() searches from the
# current working directory, which misses the file when the service is
# started from the repo root (for example via `pnpm dev`).
SERVICE_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(SERVICE_ROOT / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


class MissingAPIKey(RuntimeError):
    """Raised when a request needs a provider key that is not configured."""


def require(name: str, value: str | None) -> str:
    if not value:
        raise MissingAPIKey(
            f"{name} is not set. Add it to apps/genAI/.env "
            f"(see .env.example)."
        )

    return value
