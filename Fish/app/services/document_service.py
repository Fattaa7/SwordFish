from sqlalchemy.orm import Session
from app.utility.text_extractor import convert_file_to_markdown
from app.repositories.source_repository import SourceRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document_schema import DocumentCreate
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.chunk_service import ChunkService
from pathlib import Path


class DocumentService:
    @staticmethod
    def create(db: Session, document: DocumentCreate, source_id: int, owner_id: int):
        ### First, Parse the source to extract Text ###
        try:
            source_path = Path(document.source_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")

            destination_file = source_path.with_suffix(".md")
            md_text = convert_file_to_markdown(str(source_path), str(destination_file))
            
            if not md_text:
                raise ValueError("Failed to extract text from the document")
                
            destination_file = str(destination_file.absolute())
            
        except Exception as e:
            raise ValueError(f"Failed to process the document {document.source_path}: {e}") from e
        

        destination_file = str(destination_file)
        print(f"Converted document saved to: {destination_file}")

        SourceRepo = SourceRepository(db)
        repo = DocumentRepository(db)

        # Check if source exists and user has permission
        source = SourceRepo.get_by_id(source_id)
        if not source or source.workspace.owner_id != owner_id:
            raise ValueError("Source not found or you do not have permission to access it")
        
        # Create document via repository
        Doc = repo.create(document=document, source_id=source_id, uri_path=destination_file)
        # Create chunks for the document
        
        ChunkService.create_chunks_for_document(db, Doc.id, destination_file)

        return Doc



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