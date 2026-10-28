from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.models.poi import POI, Franja, Horario, LocalizedText, Precio

DUPLICATE_IDS = {"poi-004"}

SWAPPED_COORDS_IDS = {"poi-011"}

INJECTION_PATTERN = re.compile(
    r"\s*IMPORTANTE\s+PARA\s+EL\s+ASISTENTE\s*:.*",
    re.IGNORECASE | re.DOTALL,
)


def load_pois(path: Path) -> list[POI]:
    raw: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    pois: list[POI] = []
    for entry in raw:
        if entry["id"] in DUPLICATE_IDS:
            continue
        poi = _clean_entry(entry)
        pois.append(poi)
    return pois


def _clean_entry(raw: dict[str, Any]) -> POI:
    lat = raw["lat"]
    lon = raw["lon"]
    if raw["id"] in SWAPPED_COORDS_IDS:
        lat, lon = lon, lat

    descripcion_es = raw["descripcion"]["es"]
    descripcion_es = INJECTION_PATTERN.sub("", descripcion_es).strip()

    franjas = [
        Franja(**f) for f in raw["horario"].get("franjas", [])
    ]
    horario = Horario(always_open=raw["horario"]["always_open"], franjas=franjas)
    horario_desconocido = not horario.always_open and len(horario.franjas) == 0

    return POI(
        id=raw["id"],
        nombre=LocalizedText(es=raw["nombre"]["es"], en=raw["nombre"]["en"]),
        categoria=raw["categoria"],
        descripcion=LocalizedText(es=descripcion_es, en=raw["descripcion"]["en"]),
        lat=lat,
        lon=lon,
        accesible=raw["accesible"],
        horario=horario,
        horario_desconocido=horario_desconocido,
        precio=_normalize_precio(raw["precio"]),
        etiquetas=raw.get("etiquetas", []),
    )


def _normalize_precio(value: Any) -> Precio:
    if value is None:
        return Precio(tipo="desconocido")

    if isinstance(value, (int, float)):
        if value == 0:
            return Precio(tipo="gratis")
        return Precio(tipo="fijo", valor=float(value))

    if isinstance(value, str):
        if value.lower() == "gratis":
            return Precio(tipo="gratis")
        match = re.match(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", value)
        if match:
            return Precio(tipo="rango", min=float(match.group(1)), max=float(match.group(2)))

    return Precio(tipo="desconocido")
