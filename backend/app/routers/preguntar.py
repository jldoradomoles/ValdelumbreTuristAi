from __future__ import annotations

from fastapi import APIRouter, Request

from app.models.api import PreguntarRequest, PreguntarResponse

router = APIRouter()


@router.post("/preguntar", response_model=PreguntarResponse)
async def preguntar(request: Request, body: PreguntarRequest):
    assistant = request.app.state.assistant
    result = await assistant.ask(body.pregunta, body.idioma)
    return PreguntarResponse(respuesta=result.text, pois=result.poi_ids)
