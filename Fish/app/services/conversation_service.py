from sqlalchemy.orm import Session
from app.repositories.chunk_repository import ChunkRepository
from app.utility.OpenAi.prompt import ask_openai_simple
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
    
    @staticmethod
    def name_conversation(db: Session, conversation_id: int, workspace_id: int, query_text: str, user_id: int):
        repo = ConversationRepository(db)
        conversation = repo.get_by_id(conversation_id, workspace_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found or not yours")
        
        prompt = f"Provide a concise and descriptive title for a conversation based on the following query: '{query_text}'. The title should be brief and to the point."
        title = ask_openai_simple(prompt)
        conversation.title = title.strip().strip('"')
        repo.update(conversation)
        return conversation
    
    @staticmethod
    def get_conversation(db: Session, conversation_id: int, workspace_id: int, user_id: int) -> Conversation | None:
        repo = ConversationRepository(db)
        return repo.get_by_id(conversation_id, workspace_id, user_id)