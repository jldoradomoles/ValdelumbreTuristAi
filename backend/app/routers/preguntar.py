from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.api import PreguntarRequest, PreguntarResponse

router = APIRouter()


@router.post("/preguntar", response_model=PreguntarResponse)
async def preguntar(request: Request, body: PreguntarRequest):
    assistant = request.app.state.assistant
    try:
        result = await assistant.ask(body.pregunta, body.idioma)
    except RuntimeError as exc:
        return JSONResponse(
            status_code=503,
            content={"detail": str(exc), "llm_provider": settings.LLM_PROVIDER},
        )
    return PreguntarResponse(
        respuesta=result.text,
        pois=result.poi_ids,
        llm_provider=settings.LLM_PROVIDER,
    )
