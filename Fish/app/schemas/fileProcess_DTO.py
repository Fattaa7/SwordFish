# app/schemas/source.py
from pydantic import BaseModel
from typing import Optional

class FileProcessDTO(BaseModel):
    workspace_id: int
    owner_id: int
    storage_path: str
    filename: Optional[str] = None
