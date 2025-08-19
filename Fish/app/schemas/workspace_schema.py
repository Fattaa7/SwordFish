import datetime
from pydantic import BaseModel

class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime.datetime


    model_config = {
        "from_attributes": True
    }
 