from sqlalchemy.orm import Session
from app.core.rag_pipeline import get_rag_pipeline
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
            is_private=True,
        )
        return repo.create(new_conversation)

    @staticmethod
    def list_conversations(
        db: Session, workspace_id: int, user_id: int
    ) -> list[Conversation]:
        repo = ConversationRepository(db)
        return repo.list_by_owner(user_id, workspace_id)

    @staticmethod
    def name_conversation(
        db: Session,
        conversation_id: int,
        workspace_id: int,
        query_text: str,
        user_id: int,
    ):
        repo = ConversationRepository(db)
        conversation = repo.get_by_id(conversation_id, workspace_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found or not yours")

        prompt = (
            f"Provide a concise and descriptive title (max 5 words, no quotes) for a conversation based on the "
            f"following query: '{query_text}'."
        )
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        pipeline = get_rag_pipeline(workspace.pipeline_config if workspace else None)
        title = pipeline.generator.generate_text(
            prompt,
            system_prompt="You are a helpful assistant.",
        )
        conversation.title = title.strip().strip('"')
        repo.update(conversation)
        return conversation

    @staticmethod
    def get_conversation(
        db: Session, conversation_id: int, workspace_id: int, user_id: int
    ) -> Conversation | None:
        repo = ConversationRepository(db)
        return repo.get_by_id(conversation_id, workspace_id, user_id)

    @staticmethod
    def delete_all_conversations(db: Session, workspace_id: int, user_id: int):
        repo = ConversationRepository(db)
        conversations = repo.delete_all(workspace_id)
