from sqlalchemy.orm import Session
from app.schemas.conversation_schema import ConversationResponse
from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, conversation_id: int, workspace_id: int, owner_id: int) -> ConversationResponse | None:
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.workspace_id == workspace_id,
                Conversation.owner_id == owner_id
            )
            .first()
        )

    def create(self, conv: Conversation) -> ConversationResponse:
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def list_by_owner(self, owner_id: int, workspace_id: int) -> list[ConversationResponse]:
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.owner_id == owner_id,
                Conversation.workspace_id == workspace_id
            )
            .all()
        )
