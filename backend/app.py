"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.ask import router as ask_router
from api.audio import router as audio_router
from api.documents import router as documents_router
from api.hindi import router as hindi_router
from api.localize import router as localize_router
from api.quiz import router as quiz_router
from api.quiz_explain import router as quiz_explain_router
from api.saksham import router as saksham_router
from api.simplify import router as simplify_router
from api.summary import router as summary_router
from api.upload import router as upload_router
from api.voice import router as voice_router
from api.responses import error_response
from ai.embeddings import preload_embedding_model
from config.settings import get_settings
from database.db import init_db
from exceptions import SakshamError
from services.cache_version import purge_caches_on_version_change
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
    purge_caches_on_version_change(settings)
    init_db()
    build_saksham_index()
    preload_embedding_model()
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
app.include_router(quiz_explain_router)
app.include_router(hindi_router)
app.include_router(localize_router)
app.include_router(simplify_router)
app.include_router(documents_router)
app.include_router(audio_router)
app.include_router(saksham_router)
app.include_router(voice_router)

app.mount("/audio", StaticFiles(directory=str(settings.audio_dir)), name="audio_files")
app.mount("/static", StaticFiles(directory=str(settings.base_dir / "static")), name="static_files")

# Mount and serve compiled React frontend assets (Frontend Bundling)
import os
from fastapi.responses import FileResponse

dist_dir = settings.base_dir.parent / "frontend" / "dist"
if os.path.exists(dist_dir / "index.html"):
    app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="react_assets")

@app.get("/dyslexia-demo")
def dyslexia_demo():
    """Redirect to the dyslexia mode demo page."""
    return RedirectResponse(url="/static/dyslexia_demo.html")


@app.exception_handler(SakshamError)
async def saksham_error_handler(request: Request, exc: SakshamError):
    """Handle Saksham application errors."""
    return error_response(exc.message, status_code=400)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"success": True, "data": {"status": "healthy"}}


# Catch-all route to serve the React SPA index.html for all frontend pages
if os.path.exists(dist_dir / "index.html"):
    @app.get("/{catchall:path}")
    async def serve_react_app(catchall: str):
        # Skip API endpoints or custom paths that start with audio/static/health
        if catchall.startswith(("api/", "audio/", "static/", "health")):
            return error_response("Not Found", status_code=404)
        return FileResponse(str(dist_dir / "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=settings.debug)
