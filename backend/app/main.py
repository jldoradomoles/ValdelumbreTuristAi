from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.data.loader import load_pois
from app.data.store import POIStore
from app.llm.factory import create_llm_assistant
from app.routers import pois, preguntar
from app.services.assistant_service import AssistantService


@asynccontextmanager
async def lifespan(app: FastAPI):
    poi_list = load_pois(settings.DATA_PATH)
    app.state.store = POIStore(poi_list)
    llm = create_llm_assistant(settings)
    app.state.assistant = AssistantService(app.state.store, llm)
    yield


app = FastAPI(title="Valdelumbre Tourist API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pois.router)
app.include_router(preguntar.router)
