import datetime
from pydantic import BaseModel

# For creating a query
class QueryCreate(BaseModel):
    text: str  # the actual query content

# For responding with query data
class QueryResponse(BaseModel):
    id: int
    query_text: str
    created_at: datetime.datetime

    model_config = {
        "from_attributes": True  # allows conversion from SQLAlchemy model
    }
