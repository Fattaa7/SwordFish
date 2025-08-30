from sqlalchemy.orm import Session
from app.models.answer import Answer
from app.schemas.answer_schema import AnswerResponse


class AnswerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, answer: Answer) -> AnswerResponse:
        """Create and store a new answer."""
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def list_by_query(self, query_id: int) -> list[AnswerResponse]:
        """List all answers for a given query."""
        return (
            self.db.query(Answer)
            .filter(Answer.query_id == query_id)
            .order_by(Answer.created_at)
            .all()
        )

    def list_by_conversation(self, conversation_id: int) -> list[AnswerResponse]:
        """List all answers for a given conversation."""
        return (
            self.db.query(Answer)
            .filter(Answer.conversation_id == conversation_id)
            .order_by(Answer.created_at)
            .all()
        )

    def get_by_id(self, answer_id: int, query_id: int | None = None) -> AnswerResponse | None:
        """Retrieve a specific answer, optionally filtered by query."""
        query = self.db.query(Answer).filter(Answer.id == answer_id)
        if query_id is not None:
            query = query.filter(Answer.query_id == query_id)
        return query.first()
