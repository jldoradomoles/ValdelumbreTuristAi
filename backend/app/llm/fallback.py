from __future__ import annotations

import re
from datetime import time

from app.llm.base import AssistantAnswer, LLMAssistant
from app.models.poi import POI
from app.services.filter_service import is_open_at

ACCESSIBILITY_KEYWORDS = {
    "es": ["accesible", "silla de ruedas", "movilidad reducida", "discapacidad"],
    "en": ["accessible", "wheelchair", "disability", "reduced mobility"],
}

DAY_KEYWORDS_ES: dict[str, int] = {
    "lunes": 1, "martes": 2, "miércoles": 3, "miercoles": 3,
    "jueves": 4, "viernes": 5, "sábado": 6, "sabado": 6, "domingo": 7,
}

DAY_KEYWORDS_EN: dict[str, int] = {
    "monday": 1, "tuesday": 2, "wednesday": 3,
    "thursday": 4, "friday": 5, "saturday": 6, "sunday": 7,
}

TIME_PATTERN = re.compile(r"(\d{1,2})[:\.](\d{2})")


class FallbackAssistant(LLMAssistant):
    async def answer(
        self,
        question: str,
        idioma: str,
        candidate_pois: list[POI],
    ) -> AssistantAnswer:
        q_lower = question.lower()

        day, t = _extract_day_time(q_lower, idioma)
        if day is not None and t is not None:
            filtered = [p for p in candidate_pois if is_open_at(p, day, t)]
        else:
            filtered = _score_candidates(q_lower, idioma, candidate_pois)

        if _mentions_accessibility(q_lower, idioma):
            filtered = [p for p in filtered if p.accesible is True]

        if not filtered:
            text = (
                "No he encontrado puntos de interés que coincidan con tu consulta."
                if idioma == "es"
                else "I could not find any points of interest matching your query."
            )
            return AssistantAnswer(text=text, poi_ids=[])

        lines: list[str] = []
        for poi in filtered:
            name = getattr(poi.nombre, idioma, poi.nombre.es)
            desc = getattr(poi.descripcion, idioma, poi.descripcion.es)
            lines.append(f"- **{name}**: {desc}")

        header = (
            "Según el catálogo, estos puntos de interés coinciden con tu consulta:"
            if idioma == "es"
            else "Based on the catalog, these points of interest match your query:"
        )
        text = header + "\n" + "\n".join(lines)
        poi_ids = [p.id for p in filtered]
        return AssistantAnswer(text=text, poi_ids=poi_ids)


STOP_WORDS = {
    "es": {"qué", "que", "hay", "un", "una", "el", "la", "los", "las", "de", "del",
           "en", "con", "por", "para", "a", "al", "es", "está", "son", "dónde", "donde",
           "cómo", "como", "cuál", "cual", "algún", "algun", "alguna", "puedo", "puede",
           "sitio", "lugar", "visitar", "abierto", "abierta"},
    "en": {"what", "where", "is", "are", "the", "a", "an", "to", "do", "with",
           "can", "i", "something", "any", "some", "there"},
}

SYNONYMS: dict[str, list[str]] = {
    "kids": ["familias", "infantil", "playground", "children"],
    "children": ["familias", "infantil", "playground"],
    "outdoors": ["naturaleza", "senderismo", "ruta", "parque", "nature", "trail", "park"],
    "outdoor": ["naturaleza", "senderismo", "ruta", "parque", "nature", "trail", "park"],
    "family": ["familias"],
    "families": ["familias"],
    "hiking": ["senderismo", "ruta"],
    "nature": ["naturaleza"],
}

CATEGORY_KEYWORDS: dict[str, str] = {
    "museo": "museo",
    "museos": "museo",
    "museum": "museo",
    "museums": "museo",
    "monumento": "monumento",
    "monument": "monumento",
    "restaurante": "gastronomia",
    "restaurant": "gastronomia",
    "ruta": "ruta",
    "trail": "ruta",
}


def _stem_es(token: str) -> str:
    if token.endswith("es") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and len(token) > 3:
        return token[:-1]
    return token


def _expand_tokens(tokens: list[str]) -> list[str]:
    expanded: list[str] = []
    for t in tokens:
        expanded.append(t)
        stemmed = _stem_es(t)
        if stemmed != t:
            expanded.append(stemmed)
        for syn in SYNONYMS.get(t, []):
            expanded.append(syn)
    return expanded


def _detect_category(tokens: list[str]) -> str | None:
    for t in tokens:
        if t in CATEGORY_KEYWORDS:
            return CATEGORY_KEYWORDS[t]
        stemmed = _stem_es(t)
        if stemmed in CATEGORY_KEYWORDS:
            return CATEGORY_KEYWORDS[stemmed]
    return None


def _score_candidates(q: str, idioma: str, candidates: list[POI]) -> list[POI]:
    stops = STOP_WORDS.get(idioma, STOP_WORDS["es"])
    raw = re.sub(r"[¿?¡!.,;:\"'()]+", "", q).split()
    tokens = [t for t in raw if t not in stops and len(t) > 2]
    if not tokens:
        return candidates

    category = _detect_category(tokens)
    if category:
        cat_filtered = [p for p in candidates if p.categoria == category]
        if cat_filtered:
            candidates = cat_filtered

    expanded = _expand_tokens(tokens)

    result: list[POI] = []
    for poi in candidates:
        name = getattr(poi.nombre, idioma, poi.nombre.es).lower()
        desc = getattr(poi.descripcion, idioma, poi.descripcion.es).lower()
        tags = " ".join(poi.etiquetas).lower()
        corpus = f"{name} {desc} {poi.categoria} {tags}"
        if any(t in corpus for t in expanded):
            result.append(poi)
    return result


def _mentions_accessibility(q: str, idioma: str) -> bool:
    keywords = ACCESSIBILITY_KEYWORDS.get(idioma, ACCESSIBILITY_KEYWORDS["es"])
    return any(kw in q for kw in keywords)


def _extract_day_time(q: str, idioma: str) -> tuple[int | None, time | None]:
    day_map = DAY_KEYWORDS_ES if idioma == "es" else DAY_KEYWORDS_EN
    day: int | None = None
    for word, d in day_map.items():
        if word in q:
            day = d
            break

    t: time | None = None
    match = TIME_PATTERN.search(q)
    if match:
        try:
            t = time(int(match.group(1)), int(match.group(2)))
        except ValueError:
            pass

    return day, t
