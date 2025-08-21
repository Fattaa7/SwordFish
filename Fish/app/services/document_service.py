from sqlalchemy.orm import Session
from app.repositories.document_repository import DocumentRepository
from app.schemas.document_schema import DocumentCreate
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.user_schema import UserCreate
from app.core.auth.password import hash_password, verify_password
from app.schemas.token_schema import Token
from app.core.auth.jwt import create_access_token

class DocumentService:
    @staticmethod
    def create(db: Session, document: DocumentCreate, source_id: int, owner_id: int):
        repo = DocumentRepository(db)

        # Create document via repository
        return repo.create(document=document, source_id=source_id)
    
    @staticmethod
    def get_document(db: Session, workspace_id: int, document_id: int, owner_id: int):
        """Get a specific document by ID within a workspace"""

        workspace = WorkspaceRepository(db).get_by_id(workspace_id)
        if not workspace or workspace.owner_id != owner_id:
            raise ValueError("Workspace not found or you do not have permission to access it")
        
        repo = DocumentRepository(db)
        document = repo.get_by_id(document_id)

        if not document:
            raise ValueError("Document not found")

        # Check if the document belongs to the source owned by the user
        if document.source.workspace.owner_id != owner_id:
            raise ValueError("You do not have permission to access this document")

        return document