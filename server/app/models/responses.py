from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BaseResponse(BaseModel):
    status: str
    message: Optional[str] = None

class QueryResponse(BaseResponse):
    audio_base64: Optional[str] = None

