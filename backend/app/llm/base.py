from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.models.poi import POI


class AssistantAnswer(BaseModel):
    text: str
    poi_ids: list[str]


class LLMAssistant(ABC):
    @abstractmethod
    async def answer(
        self,
        question: str,
        idioma: str,
        candidate_pois: list[POI],
    ) -> AssistantAnswer: ...
