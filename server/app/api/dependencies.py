from fastapi import Depends, Request
from app.services.hearsona_service import HearsonaService

async def get_hearsona_service(request: Request) -> HearsonaService:
    """Get HearsonaService instance."""
    return request.app.state.hearsona_service
