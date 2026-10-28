from pathlib import Path

import pytest

from app.data.loader import load_pois
from app.data.store import POIStore

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "references" / "datos" / "pois.json"


@pytest.fixture(scope="session")
def pois():
    return load_pois(DATA_PATH)


@pytest.fixture(scope="session")
def store(pois):
    return POIStore(pois)
