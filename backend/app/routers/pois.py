from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.models.api import POIListResponse, POIResponse
from app.models.poi import POI
from app.services.filter_service import filter_pois

router = APIRouter()


def _project(poi: POI, idioma: str) -> POIResponse:
    return POIResponse(
        id=poi.id,
        nombre=getattr(poi.nombre, idioma),
        categoria=poi.categoria,
        descripcion=getattr(poi.descripcion, idioma),
        lat=poi.lat,
        lon=poi.lon,
        accesible=poi.accesible,
        horario=poi.horario,
        horario_desconocido=poi.horario_desconocido,
        precio=poi.precio,
        etiquetas=poi.etiquetas,
    )


@router.get("/pois", response_model=POIListResponse)
def list_pois(
    request: Request,
    categoria: str | None = None,
    accesible: bool | None = None,
    abierto_en: str | None = None,
    idioma: Literal["es", "en"] = "es",
):
    store = request.app.state.store
    try:
        pois = filter_pois(
            store.list_all(),
            categoria=categoria,
            accesible=accesible,
            abierto_en=abierto_en,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    projected = [_project(p, idioma) for p in pois]
    return POIListResponse(total=len(projected), pois=projected)


@router.get("/pois/{poi_id}", response_model=POIResponse)
def get_poi(
    request: Request,
    poi_id: str,
    idioma: Literal["es", "en"] = "es",
):
    store = request.app.state.store
    poi = store.get(poi_id)
    if poi is None:
        raise HTTPException(status_code=404, detail=f"POI '{poi_id}' no encontrado")
    return _project(poi, idioma)
