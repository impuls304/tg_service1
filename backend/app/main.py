from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import models  # noqa: F401 - ensures models are registered
from .api.routes import portfolio, requests, services
from .core.config import get_settings
from .core.logging import configure_logging
from .database import Base, engine
from .schemas import APIHealth
from .telegram.bot import router as telegram_router

settings = get_settings()
configure_logging(settings.log_level)


def _mount_frontend(app: FastAPI, frontend_dir: Path) -> None:
    if not frontend_dir.exists():
        return

    app.mount(
        settings.static_mount_path,
        StaticFiles(directory=str(frontend_dir), html=True),
        name="web",
    )

    index_file = frontend_dir / "index.html"

    @app.get("/", include_in_schema=False)
    async def root_index() -> FileResponse:
        if not index_file.exists():
            raise HTTPException(status_code=404, detail="Frontend is not built yet")
        return FileResponse(index_file)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def startup_event() -> None:
        Base.metadata.create_all(bind=engine)

    app.include_router(services.router, prefix="/api")
    app.include_router(portfolio.router, prefix="/api")
    app.include_router(requests.router, prefix="/api")
    app.include_router(telegram_router)

    _mount_frontend(app, settings.frontend_dir)

    @app.get("/api/health", response_model=APIHealth, tags=["system"])
    async def healthcheck() -> APIHealth:
        return APIHealth(status="ok", timestamp=datetime.utcnow())

    return app


app = create_app()
