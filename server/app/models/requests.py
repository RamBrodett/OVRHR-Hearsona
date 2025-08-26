from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class QueryRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=1000)
    settings: Dict[str, Any] = Field(default_factory=dict)

class ExportChatRequest(BaseModel):
    id_input: str = Field(..., min_length=1)