from fastapi import APIRouter
from .endpoints import health, chat, sessions

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])

api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])

api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])