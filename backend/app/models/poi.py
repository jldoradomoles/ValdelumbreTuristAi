from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class LocalizedText(BaseModel):
    es: str
    en: str


class Franja(BaseModel):
    dias: list[int]
    abre: str
    cierra: str
    temporada: str | None = None


class Horario(BaseModel):
    always_open: bool
    franjas: list[Franja]


class Precio(BaseModel):
    tipo: Literal["gratis", "fijo", "rango", "desconocido"]
    valor: float | None = None
    min: float | None = None
    max: float | None = None


class POI(BaseModel):
    id: str
    nombre: LocalizedText
    categoria: str
    descripcion: LocalizedText
    lat: float
    lon: float
    accesible: bool | None
    horario: Horario
    horario_desconocido: bool = False
    precio: Precio
    etiquetas: list[str]
