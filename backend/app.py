"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.ask import router as ask_router
from api.audio import router as audio_router
from api.documents import router as documents_router
from api.hindi import router as hindi_router
from api.quiz import router as quiz_router
from api.saksham import router as saksham_router
from api.simplify import router as simplify_router
from api.summary import router as summary_router
from api.upload import router as upload_router
from api.responses import error_response
from config.settings import get_settings
from database.db import init_db
from exceptions import SakshamError
from services.knowledge_service import build_saksham_index

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    settings.ensure_directories()
    init_db()
    build_saksham_index()
    logger.info("Saksham AI backend started")
    yield
    logger.info("Saksham AI backend shutting down")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(ask_router)
app.include_router(summary_router)
app.include_router(quiz_router)
app.include_router(hindi_router)
app.include_router(simplify_router)
app.include_router(documents_router)
app.include_router(audio_router)
app.include_router(saksham_router)

app.mount("/audio", StaticFiles(directory=str(settings.audio_dir)), name="audio_files")


@app.exception_handler(SakshamError)
async def saksham_error_handler(request: Request, exc: SakshamError):
    """Handle Saksham application errors."""
    return error_response(exc.message, status_code=400)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"success": True, "data": {"status": "healthy"}}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=settings.debug)
