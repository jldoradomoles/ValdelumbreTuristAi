from __future__ import annotations

from datetime import time

from app.models.poi import POI

DAY_MAP: dict[str, int] = {
    "L": 1,
    "M": 2,
    "X": 3,
    "J": 4,
    "V": 5,
    "S": 6,
    "D": 7,
}


def parse_abierto_en(value: str) -> tuple[int, time]:
    parts = value.split("-", 1)
    if len(parts) != 2:
        raise ValueError(f"Formato inválido: '{value}'. Esperado: X-HH:MM")
    day_char, time_str = parts
    day = DAY_MAP.get(day_char.upper())
    if day is None:
        raise ValueError(f"Día no reconocido: '{day_char}'. Válidos: {', '.join(DAY_MAP)}")
    try:
        h, m = time_str.split(":")
        return day, time(int(h), int(m))
    except (ValueError, TypeError) as e:
        raise ValueError(f"Hora inválida: '{time_str}'. Esperado: HH:MM") from e


def is_open_at(poi: POI, day: int, t: time) -> bool:
    if poi.horario.always_open:
        return True
    if poi.horario_desconocido:
        return False
    for franja in poi.horario.franjas:
        if day in franja.dias:
            abre = time.fromisoformat(franja.abre)
            cierra = time.fromisoformat(franja.cierra)
            if abre <= t < cierra:
                return True
    return False


def filter_pois(
    pois: list[POI],
    *,
    categoria: str | None = None,
    accesible: bool | None = None,
    abierto_en: str | None = None,
) -> list[POI]:
    result = pois

    if categoria is not None:
        result = [p for p in result if p.categoria == categoria]

    if accesible is not None:
        result = [p for p in result if p.accesible is not None and p.accesible == accesible]

    if abierto_en is not None:
        day, t = parse_abierto_en(abierto_en)
        result = [p for p in result if is_open_at(p, day, t)]

    return result
