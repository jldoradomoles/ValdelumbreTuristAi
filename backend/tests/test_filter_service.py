from datetime import time

import pytest

from app.data.store import POIStore
from app.services.filter_service import filter_pois, is_open_at, parse_abierto_en


class TestParseAbiertoEn:
    def test_lunes(self):
        day, t = parse_abierto_en("L-12:00")
        assert day == 1
        assert t == time(12, 0)

    def test_domingo(self):
        day, t = parse_abierto_en("D-09:00")
        assert day == 7
        assert t == time(9, 0)

    def test_miercoles(self):
        day, t = parse_abierto_en("X-18:30")
        assert day == 3
        assert t == time(18, 30)

    def test_case_insensitive(self):
        day, _ = parse_abierto_en("l-10:00")
        assert day == 1

    def test_invalid_day(self):
        with pytest.raises(ValueError, match="Día no reconocido"):
            parse_abierto_en("Z-12:00")

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            parse_abierto_en("12:00")


class TestFilterPois:
    def test_abierto_lunes_12(self, store: POIStore):
        result = filter_pois(store.list_all(), abierto_en="L-12:00")
        ids = {p.id for p in result}
        for expected in ["poi-001", "poi-002", "poi-005", "poi-006", "poi-010"]:
            assert expected in ids, f"{expected} debería estar abierto L-12:00"
        for excluded in ["poi-003", "poi-008", "poi-015"]:
            assert excluded not in ids, f"{excluded} no debería estar abierto L-12:00"

    def test_categoria_museo(self, store: POIStore):
        result = filter_pois(store.list_all(), categoria="museo")
        ids = {p.id for p in result}
        assert ids == {"poi-003", "poi-013", "poi-015"}

    def test_accesible_true(self, store: POIStore):
        result = filter_pois(store.list_all(), accesible=True)
        for p in result:
            assert p.accesible is True
        ids = {p.id for p in result}
        assert "poi-013" not in ids
        assert "poi-011" not in ids

    def test_accesible_excludes_null(self, store: POIStore):
        result_true = filter_pois(store.list_all(), accesible=True)
        result_false = filter_pois(store.list_all(), accesible=False)
        null_ids = {p.id for p in store.list_all() if p.accesible is None}
        for p in result_true:
            assert p.id not in null_ids
        for p in result_false:
            assert p.id not in null_ids

    def test_combined_filters(self, store: POIStore):
        result = filter_pois(store.list_all(), categoria="museo", accesible=True)
        ids = {p.id for p in result}
        assert ids == {"poi-003", "poi-015"}
