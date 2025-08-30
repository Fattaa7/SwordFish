from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any


class ChunkResponse(BaseModel):
    id: int
    document_id: int
    title: Optional[str]
    index: int
    text: str
    token_count: Optional[int]
    page_number: Optional[int]
    meta: Optional[Dict[str, Any]]
    
    # Source info
    source_uri: Optional[str]
    
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }
