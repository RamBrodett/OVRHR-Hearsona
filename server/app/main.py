from fastapi import FastAPI as fAPI
from contextlib import asynccontextmanager as aCM
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.services.hearsona_service import HearsonaService
from app.api.v1.router import api_router

@aCM
async def lifespan(app: fAPI):
    """Application lifespan events"""

    hearsona_service = HearsonaService()
    await hearsona_service.initialize()
    app.state.hearsona_service = hearsona_service
    print("[Startup] Hearsona backend started successfully")

    yield

    hearsona_service.cleanup()
    print("[Shutdown] Hearsona backend shutdown complete")


def create_app() -> fAPI:
    """FastAPI application factory"""
    settings = get_settings()

    app = fAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.api_version,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins= settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers
    )
    
    app.include_router(api_router, prefix="/api/v1")

    return app

app = create_app()

