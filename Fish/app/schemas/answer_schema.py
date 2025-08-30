import datetime
from pydantic import BaseModel

class Citation(BaseModel):
    chunk_id: int
    document_id: int
    title: str
    page_number: int | None = None
    source_uri: str | None = None

class AnswerCreate(BaseModel):
    text: str
    sources: list[Citation] | None = []

class AnswerResponse(BaseModel):
    id: int
    text: str
    sources: list[Citation] | None = []
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
