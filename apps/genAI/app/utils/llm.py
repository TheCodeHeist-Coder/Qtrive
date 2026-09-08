from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from app.utils.config import GOOGLE_API_KEY, GROQ_API_KEY, require

GROQ_MODEL = "openai/gpt-oss-120b"
GOOGLE_MODEL = "gemini-3-flash-preview"

_groq_llm = None
_google_llm = None


def get_groq_llm():
    """Build the Groq client on first use.

    Constructing these at import time makes a missing API key crash the
    whole service on startup, including endpoints such as /health and
    /docs that need no key at all.
    """

    global _groq_llm

    if _groq_llm is None:
        _groq_llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=require("GROQ_API_KEY", GROQ_API_KEY),
        )

    return _groq_llm


def get_google_llm():
    """Build the Gemini client on first use."""

    global _google_llm

    if _google_llm is None:
        _google_llm = ChatGoogleGenerativeAI(
            model=GOOGLE_MODEL,
            api_key=require("GOOGLE_API_KEY", GOOGLE_API_KEY),
        )

    return _google_llm
