from __future__ import annotations

from app.models.poi import POI


class POIStore:
    def __init__(self, pois: list[POI]) -> None:
        self._by_id: dict[str, POI] = {p.id: p for p in pois}

    def get(self, poi_id: str) -> POI | None:
        return self._by_id.get(poi_id)

    def list_all(self) -> list[POI]:
        return list(self._by_id.values())

    def search_text(self, query: str, idioma: str = "es") -> list[POI]:
        tokens = query.lower().split()
        if not tokens:
            return self.list_all()

        scored: list[tuple[int, POI]] = []
        for poi in self._by_id.values():
            name = getattr(poi.nombre, idioma, poi.nombre.es).lower()
            desc = getattr(poi.descripcion, idioma, poi.descripcion.es).lower()
            tags = " ".join(poi.etiquetas).lower()
            corpus = f"{name} {desc} {poi.categoria} {tags}"
            score = sum(1 for t in tokens if t in corpus)
            if score > 0:
                scored.append((score, poi))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [poi for _, poi in scored]
