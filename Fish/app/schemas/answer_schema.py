import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class CitationSchema(BaseModel):
    """
    Compatible with fish-engine's native Citation contract (source_index, chunk_id: str,
    document_id: str, page_number, storage_uri, score, snippet, metadata) as well as any
    legacy SwordFish citation rows.
    """
    source_index: Optional[int] = None
    chunk_id: Union[str, int]
    document_id: Union[str, int]
    page_number: Optional[int] = None
    storage_uri: Optional[str] = None
    score: Optional[float] = None
    snippet: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Legacy optional fields for backwards compatibility with older DB rows
    title: Optional[str] = None
    source_uri: Optional[str] = None


class AnswerCreate(BaseModel):
    text: str
    sources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AnswerResponse(BaseModel):
    id: int
    query_id: Optional[int] = None
    conversation_id: Optional[int] = None
    text: str
    sources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
