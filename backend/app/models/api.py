from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.models.poi import Horario, Precio


class POIResponse(BaseModel):
    id: str
    nombre: str
    categoria: str
    descripcion: str
    lat: float
    lon: float
    accesible: bool | None
    horario: Horario
    horario_desconocido: bool
    precio: Precio
    etiquetas: list[str]


class POIListResponse(BaseModel):
    total: int
    pois: list[POIResponse]


class PreguntarRequest(BaseModel):
    pregunta: str = Field(..., min_length=1, max_length=500)
    idioma: Literal["es", "en"] = "es"


class PreguntarResponse(BaseModel):
    respuesta: str
    pois: list[str]
    llm_provider: str = ""
