from sqlalchemy.orm import Session
from app.repositories.chunk_repository import ChunkRepository
from app.utility.OpenAi.embedding import get_chunk_embedding
from app.utility.OpenAi.prompt import ask_openai
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceResponse
from app.models.workspace import Workspace
from app.models.conversation import Conversation

class ConversationService:

    @staticmethod
    def create_conversation(db: Session, workspace_id: int, user_id: int):
        repo = ConversationRepository(db)

        # Create new conversation
        new_conversation = Conversation(
            title="New Conversation",
            workspace_id=workspace_id,
            owner_id=user_id,
            is_private=True
        )
        return repo.create(new_conversation)
    
    @staticmethod
    def list_conversations(db: Session, workspace_id: int, user_id: int) -> list[Conversation]:
        repo = ConversationRepository(db)
        return repo.list_by_owner(user_id, workspace_id)