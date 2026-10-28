import pytest
from fastapi.testclient import TestClient

from app.data.loader import load_pois
from app.data.store import POIStore
from app.llm.fallback import FallbackAssistant
from app.main import app
from app.services.assistant_service import AssistantService
from tests.conftest import DATA_PATH


@pytest.fixture(scope="module")
def client():
    poi_list = load_pois(DATA_PATH)
    store = POIStore(poi_list)
    app.state.store = store
    app.state.assistant = AssistantService(store, FallbackAssistant())
    with TestClient(app) as c:
        yield c


class TestPreguntar:
    def test_valid_question(self, client: TestClient):
        resp = client.post("/preguntar", json={"pregunta": "¿Dónde puedo probar vino?", "idioma": "es"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["respuesta"], str)
        assert len(data["respuesta"]) > 0
        assert isinstance(data["pois"], list)
        assert "poi-008" in data["pois"]

    def test_empty_question(self, client: TestClient):
        resp = client.post("/preguntar", json={"pregunta": "", "idioma": "es"})
        assert resp.status_code == 422

    def test_invalid_idioma(self, client: TestClient):
        resp = client.post("/preguntar", json={"pregunta": "Hola", "idioma": "fr"})
        assert resp.status_code == 422

    def test_default_idioma(self, client: TestClient):
        resp = client.post("/preguntar", json={"pregunta": "¿Qué museos hay?"})
        assert resp.status_code == 200

    def test_english(self, client: TestClient):
        resp = client.post("/preguntar", json={"pregunta": "Where can I taste wine?", "idioma": "en"})
        assert resp.status_code == 200
        data = resp.json()
        assert "Based on the catalog" in data["respuesta"]

    def test_no_results(self, client: TestClient):
        resp = client.post("/preguntar", json={"pregunta": "¿Hay algún sitio de aventura con tirolina?", "idioma": "es"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["pois"] == []
