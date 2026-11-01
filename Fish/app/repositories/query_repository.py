from sqlalchemy.orm import Session
from app.schemas.query_schema import QueryCreate, QueryResponse
from app.models.query import Query


class QueryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, query: Query) -> QueryResponse:
        self.db.add(query)
        self.db.commit()
        self.db.refresh(query)
        return query

    def list_by_conversation(self, conversation_id: int) -> list[QueryResponse]:
        return (
            self.db.query(Query)
            .filter(Query.conversation_id == conversation_id)
            .order_by(Query.created_at)
            .all()
        )

    def get_by_id(
        self,
        query_id: int,
        conversation_id: int,
        workspace_id: int | None = None,
        user_id: int | None = None,
    ) -> QueryResponse | None:
        query = self.db.query(Query).filter(
            Query.id == query_id,
            Query.conversation_id == conversation_id,
        )
        if workspace_id is not None:
            query = query.filter(Query.workspace_id == workspace_id)
        if user_id is not None:
            query = query.filter(Query.owner_id == user_id)
        return query.first()
