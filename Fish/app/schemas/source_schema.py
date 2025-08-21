import datetime
from pydantic import BaseModel, field_validator
from typing import Optional
from app.models.source import MimeType, SourceStatus, SourceType


class SourceCreate(BaseModel):
    type: SourceType
    url: Optional[str] = None
    storage_path: Optional[str] = None

    # @field_validator("url")
    # def validate_url(cls, v, values):
    #     if values.get("type") == SourceType.URL and not v:
    #         raise ValueError("URL is required when type is URL")
    #     return v

    # @field_validator("storage_path")
    # def validate_storage_path(cls, v, values):
    #     if values.get("type") == SourceType.FILE and not v:
    #         raise ValueError("storage_path is required when type is FILE")
    #     return v


class SourceResponse(BaseModel):
    id: int
    workspace_id: int
    type: SourceType
    status: SourceStatus
    url: Optional[str] = None
    storage_path: Optional[str] = None
    mime_type: Optional[MimeType] = None
    checksum: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {
        "from_attributes": True
    }