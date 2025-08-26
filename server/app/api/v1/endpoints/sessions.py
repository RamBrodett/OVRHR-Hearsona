from fastapi import APIRouter, Depends, HTTPException
from app.models.requests import ExportChatRequest
from app.models.responses import BaseResponse
from app.services.hearsona_service import HearsonaService
from app.api.dependencies import get_hearsona_service

router = APIRouter()

@router.post("/export", response_model=BaseResponse)
async def export_chat_endpoint(
    request: ExportChatRequest,
    hearsona_service: HearsonaService = Depends(get_hearsona_service)
):
    """
    Endpoint to export chat history.
    """
    try:
        if hearsona_service.export_chat(id=request.id_input):
            return BaseResponse(status='success')
        return BaseResponse(success=False, message="Export failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.post("/new")
async def new_user_session(
    hearsona_service: HearsonaService = Depends(get_hearsona_service)
):
    try:
        hearsona_service.change_user()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.post("/restart")
async def restart_session(
    hearsona_service: HearsonaService = Depends(get_hearsona_service)
):
    try:
        hearsona_service.start_over_context()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")