from __future__ import annotations

from app.data.store import POIStore
from app.llm.base import AssistantAnswer, LLMAssistant


class AssistantService:
    def __init__(self, store: POIStore, llm: LLMAssistant) -> None:
        self._store = store
        self._llm = llm

    async def ask(self, question: str, idioma: str) -> AssistantAnswer:
        return await self._llm.answer(question, idioma, self._store.list_all())
