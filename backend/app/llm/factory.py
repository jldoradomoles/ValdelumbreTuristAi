from __future__ import annotations

from app.config import Settings
from app.llm.base import LLMAssistant


def create_llm_assistant(settings: Settings) -> LLMAssistant:
    if settings.LLM_PROVIDER == "claude":
        from app.llm.claude import ClaudeAssistant
        return ClaudeAssistant(api_key=settings.ANTHROPIC_API_KEY)

    from app.llm.fallback import FallbackAssistant
    return FallbackAssistant()
