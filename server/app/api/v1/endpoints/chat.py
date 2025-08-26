from fastapi import APIRouter, Depends, HTTPException
from app.models.requests import QueryRequests
from app.models.responses import QueryResponse
from app.services.hearsona_service import HearsonaService
from app.api.dependencies import get_hearsona_service

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(
    request: QueryRequests,
    hearsona_service: HearsonaService = Depends(get_hearsona_service)
):
    try:
        generation_result, assistant_reply = hearsona_service.prompt_process(
            request.user_input,
            request.settings
        )

        if assistant_reply == "Audio generation failed. Please Try again.":
            return QueryResponse(status="error", message=assistant_reply)
        
        return QueryResponse(
            status="success",
            message=assistant_reply,
            audio_base64=generation_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")