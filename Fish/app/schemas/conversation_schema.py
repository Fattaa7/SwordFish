import datetime
from pydantic import BaseModel, EmailStr

class ConversationCreate(BaseModel):
    pass

class ConversationResponse(BaseModel):
    id: int
    title: str
    is_private: bool
    created_at: datetime.datetime

    model_config = {
        "from_attributes": True
    }
