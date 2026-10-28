from app.models.poi import POI


def test_poi_004_discarded(pois: list[POI]):
    ids = {p.id for p in pois}
    assert "poi-004" not in ids
    assert len(pois) == 17


def test_poi_011_coords_swapped(pois: list[POI]):
    poi_011 = next(p for p in pois if p.id == "poi-011")
    assert poi_011.lat > 40, f"lat should be ~40.x, got {poi_011.lat}"
    assert poi_011.lon < 0, f"lon should be ~-3.x, got {poi_011.lon}"


def test_poi_013_no_injection(pois: list[POI]):
    poi_013 = next(p for p in pois if p.id == "poi-013")
    assert "ignora" not in poi_013.descripcion.es.lower()
    assert "IMPORTANTE" not in poi_013.descripcion.es
    assert "tapices flamencos" in poi_013.descripcion.es.lower()


def test_precio_normalized(pois: list[POI]):
    by_id = {p.id: p for p in pois}

    assert by_id["poi-001"].precio.tipo == "fijo"
    assert by_id["poi-001"].precio.valor == 4.5

    assert by_id["poi-002"].precio.tipo == "gratis"

    assert by_id["poi-003"].precio.tipo == "gratis"

    assert by_id["poi-009"].precio.tipo == "rango"
    assert by_id["poi-009"].precio.min == 25
    assert by_id["poi-009"].precio.max == 35

    assert by_id["poi-016"].precio.tipo == "desconocido"


def test_poi_018_horario_desconocido(pois: list[POI]):
    poi_018 = next(p for p in pois if p.id == "poi-018")
    assert poi_018.horario_desconocido is True
    assert poi_018.horario.always_open is False
    assert len(poi_018.horario.franjas) == 0
