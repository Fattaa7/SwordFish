from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MetaModel(BaseModel):
    author: Optional[str] = None
    pages: Optional[int] = None
    tags: Optional[List[str]] = None

class DocumentCreate(BaseModel):
    title: Optional[str] = None 
    language: str
    meta: Optional[MetaModel]

class DocumentResponse(BaseModel):
    id: int
    source_id: int
    title: str
    language: str
    meta: Optional[MetaModel]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }