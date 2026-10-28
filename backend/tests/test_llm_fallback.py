import pytest

from app.llm.fallback import FallbackAssistant
from app.data.store import POIStore


@pytest.fixture
def fallback():
    return FallbackAssistant()


class TestFallbackAssistant:
    @pytest.mark.asyncio
    async def test_wine_question(self, fallback: FallbackAssistant, store: POIStore):
        candidates = store.search_text("vino bodega cata", "es")
        result = await fallback.answer("¿Dónde puedo probar vino de la zona?", "es", candidates)
        assert "poi-008" in result.poi_ids

    @pytest.mark.asyncio
    async def test_accessible_museums(self, fallback: FallbackAssistant, store: POIStore):
        candidates = store.search_text("museo accesible", "es")
        result = await fallback.answer(
            "Voy en silla de ruedas, ¿qué puedo visitar de museos?", "es", candidates,
        )
        for pid in result.poi_ids:
            poi = store.get(pid)
            assert poi is not None
            assert poi.accesible is True
        assert "poi-013" not in result.poi_ids

    @pytest.mark.asyncio
    async def test_nonexistent_returns_empty(self, fallback: FallbackAssistant, store: POIStore):
        candidates = store.search_text("tirolina aventura", "es")
        result = await fallback.answer("¿Hay algún sitio de aventura con tirolina?", "es", candidates)
        assert result.poi_ids == []

    @pytest.mark.asyncio
    async def test_english(self, fallback: FallbackAssistant, store: POIStore):
        candidates = store.search_text("park playground trail", "en")
        result = await fallback.answer("Where is a park or playground?", "en", candidates)
        assert len(result.poi_ids) > 0
        assert result.text.startswith("Based on the catalog")

    @pytest.mark.asyncio
    async def test_open_monday(self, fallback: FallbackAssistant, store: POIStore):
        candidates = store.search_text("abierto lunes 12:00", "es")
        result = await fallback.answer("¿Qué está abierto un lunes a las 12:00?", "es", candidates)
        ids = set(result.poi_ids)
        assert "poi-003" not in ids
