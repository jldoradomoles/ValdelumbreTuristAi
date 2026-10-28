from fastapi.testclient import TestClient

from app.data.loader import load_pois
from app.data.store import POIStore
from app.main import app
from tests.conftest import DATA_PATH

import pytest


@pytest.fixture(scope="module")
def client():
    poi_list = load_pois(DATA_PATH)
    app.state.store = POIStore(poi_list)
    with TestClient(app) as c:
        yield c


class TestListPois:
    def test_returns_17(self, client: TestClient):
        resp = client.get("/pois")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 17

    def test_idioma_en(self, client: TestClient):
        resp = client.get("/pois", params={"idioma": "en"})
        data = resp.json()
        first = data["pois"][0]
        assert isinstance(first["nombre"], str)
        assert first["nombre"] != ""

    def test_categoria_monumento(self, client: TestClient):
        resp = client.get("/pois", params={"categoria": "monumento"})
        data = resp.json()
        for poi in data["pois"]:
            assert poi["categoria"] == "monumento"

    def test_abierto_en_lunes_12(self, client: TestClient):
        resp = client.get("/pois", params={"abierto_en": "L-12:00"})
        ids = {p["id"] for p in resp.json()["pois"]}
        for expected in ["poi-001", "poi-002", "poi-005", "poi-006", "poi-010"]:
            assert expected in ids
        for excluded in ["poi-003", "poi-008", "poi-015"]:
            assert excluded not in ids

    def test_accesible_true(self, client: TestClient):
        resp = client.get("/pois", params={"accesible": True})
        for poi in resp.json()["pois"]:
            assert poi["accesible"] is True

    def test_invalid_abierto_en(self, client: TestClient):
        resp = client.get("/pois", params={"abierto_en": "invalid"})
        assert resp.status_code == 422


class TestGetPoi:
    def test_existing(self, client: TestClient):
        resp = client.get("/pois/poi-001")
        assert resp.status_code == 200
        assert resp.json()["id"] == "poi-001"

    def test_discarded_poi_004(self, client: TestClient):
        resp = client.get("/pois/poi-004")
        assert resp.status_code == 404

    def test_nonexistent(self, client: TestClient):
        resp = client.get("/pois/poi-999")
        assert resp.status_code == 404

    def test_idioma_en(self, client: TestClient):
        resp = client.get("/pois/poi-001", params={"idioma": "en"})
        assert resp.json()["nombre"] == "Valdelumbre Castle"
