from sqlalchemy.orm import Session
from app.tasks.document_tasks import process_file_task
from app.schemas.document_schema import DocumentCreate, MetaModel
from app.services.document_service import DocumentService
from app.utility.metadata_extractor import MetadataExtractor
from app.repositories.source_repository import SourceRepository
from app.schemas.source_schema import SourceCreate, SourceResponse
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.core.auth.password import hash_password, verify_password
from app.schemas.token_schema import Token
from app.core.auth.jwt import create_access_token
from app.models.source import SourceStatus, SourceType
import os
import tempfile
import shutil
from fastapi import UploadFile
from typing import List
from fastapi.responses import FileResponse



class SourceService:

    @staticmethod
    def upload_file(db: Session, workspace_id: int, file: UploadFile, owner_id: int) -> SourceResponse:
        """Upload a file and create a source with extracted metadata"""
        temp_path = None
        try:
            # Use the helper function to create a temporary file
            temp_path = create_temp_file(file)

            # Create source data
            source_data = SourceCreate(type=SourceType.FILE, storage_path=temp_path, url=None)
            
            ### Use Celery task to process the file in background ###
            # Create source and extract metadata
            return SourceService.create_source(db, workspace_id, source_data, owner_id)
            
        except Exception as e:
            # Clean up temporary file if it exists
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
        
    @staticmethod
    def create_document(db: Session, created: SourceResponse, owner_id: int) -> None:
        """
        Creates a document associated with a source.

        Args:
            db (Session): Database session.
            source_meta (dict): Extracted metadata from the source.
            source (SourceCreate): The source data.
            created: The created source object.
            owner_id (int): ID of the owner.
        """
        # Extract metadata from the source
        source_meta = SourceService._extract_source_metadata(created)

        # Create document creation request
        document = DocumentCreate(
            title=source_meta["title"],
            language=source_meta["language"],
            source_path=created.storage_path,
            meta=MetaModel(
                author=source_meta["meta"]["author"],
                pages=source_meta["meta"]["pages"],
                tags=source_meta["meta"]["tags"]
            )
        )

        # Create document associated with the source
        DocumentService.create(db, document=document, source_id=created.id, owner_id=owner_id)



    @staticmethod
    def create_source(db: Session, workspace_id: int, source: SourceCreate, owner_id: int) -> SourceResponse:
        repo = SourceRepository(db)

        # Check if workspace exists and user has permission
        workspace = WorkspaceRepository(db).get_by_id(workspace_id)
        if not workspace or workspace.owner_id != owner_id:
            raise ValueError("Workspace not found or you do not have permission to access it")

        # Create source via repository
        created = repo.create(source=source, workspace_id=workspace_id)

        ############# Create associated document #############
        if not created:
            raise ValueError("Failed to create source")


        # Use the new helper method to create the document
        process_file_task.delay(created.id, owner_id)

        return created


    @staticmethod
    def download_source(db: Session, source_id: int, workspace_id: int) -> FileResponse:
        """Download the source file by ID"""
        repo = SourceRepository(db)
        source = repo.get_by_id(source_id)
        if not source or not source.storage_path or not os.path.exists(source.storage_path):
            raise ValueError("Source not found or file does not exist")
        
        return FileResponse(source.storage_path, media_type="application/pdf", filename=str(source.id)+ ".pdf")
    

    @staticmethod
    def create_from_url(db: Session, workspace_id: int, url: str, owner_id: int) -> SourceResponse:
        """Create a source from a URL"""
        try:
            source_data = SourceCreate(type=SourceType.URL, url=url, storage_path=None)
            return SourceService.create_source(db, workspace_id, source_data, owner_id)
            
        except Exception as e:
            raise e

    @staticmethod
    def get_sources_by_workspace(db: Session, workspace_id: int, owner_id: int) -> List[SourceResponse]:
        """Get all sources for a workspace"""
        # Check if workspace exists and user has permission
        workspace = WorkspaceRepository(db).get_by_id(workspace_id)
        if not workspace or workspace.owner_id != owner_id:
            raise ValueError("Workspace not found or you do not have permission to access it")
        
        repo = SourceRepository(db)
        return repo.get_by_workspace_id(workspace_id)

    @staticmethod
    def get_source_by_id(db: Session, workspace_id: int, source_id: int, owner_id: int) -> SourceResponse:
        """Get a specific source by ID within a workspace"""
        # Check if workspace exists and user has permission
        workspace = WorkspaceRepository(db).get_by_id(workspace_id)
        if not workspace or workspace.owner_id != owner_id:
            raise ValueError("Workspace not found or you do not have permission to access it")
        
        repo = SourceRepository(db)
        source = repo.get_by_id(source_id)
        
        if not source or source.workspace_id != workspace_id:
            raise ValueError("Source not found")
        
        return source

    @staticmethod
    def delete_source(db: Session, workspace_id: int, source_id: int, owner_id: int) -> bool:
        """Delete a source by ID within a workspace"""
        # Check if workspace exists and user has permission
        workspace = WorkspaceRepository(db).get_by_id(workspace_id)
        if not workspace or workspace.owner_id != owner_id:
            raise ValueError("Workspace not found or you do not have permission to access it")
        
        repo = SourceRepository(db)
        source = repo.get_by_id(source_id)
        
        if not source or source.workspace_id != workspace_id:
            raise ValueError("Source not found")
        
        # Delete the source
        return repo.delete(source_id)
    
    @staticmethod
    def _extract_source_metadata(source: SourceResponse) -> dict:
        """
        Extract metadata from the source based on its type and content
        """
        try:
            if source.type == SourceType.FILE and source.storage_path:
                # For file uploads, extract metadata from the file
                if os.path.exists(source.storage_path):
                    metadata = MetadataExtractor.extract_metadata(source.storage_path)
                else:
                    # If file doesn't exist on disk, use basic metadata
                    metadata = {
                        "title": os.path.basename(source.storage_path),
                        "language": "unknown",
                        "meta": {
                            "author": None,
                            "pages": None,
                            "tags": []
                        }
                    }
            elif source.type == SourceType.URL and source.url:
                # For URLs, extract basic metadata
                metadata = {
                    "title": f"Document from {source.url}",
                    "language": "unknown",
                    "meta": {
                        "author": None,
                        "pages": None,
                        "tags": []
                    }
                }
            else:
                # Fallback metadata
                metadata = {
                    "title": "Untitled Document",
                    "language": "unknown",
                    "meta": {
                        "author": None,
                        "pages": None,
                        "tags": []
                    }
                }
            
            return metadata
            
        except Exception as e:
            # Return basic metadata if extraction fails
            return {
                "title": "Document",
                "language": "unknown",
                "meta": {
                    "author": None,
                    "pages": None,
                    "tags": [],
                    "error": str(e)
                }
            }
        

def create_temp_file(file: UploadFile) -> str:
    """
    Saves an uploaded file to a temporary directory with its original filename.
    If a file with the same name already exists, appends _1, _2, etc.

    Args:
        file (UploadFile): The uploaded file.

    Returns:
        str: The path to the saved temporary file.
    """
    # Ensure we have a temporary directory
    temp_dir = tempfile.gettempdir()

    # Get original name safely
    base_name = os.path.splitext(file.filename or "uploaded_file")[0]
    extension = os.path.splitext(file.filename or "")[1]

    # Start with the original name
    final_name = f"{base_name}{extension}"
    final_path = os.path.join(temp_dir, final_name)

    # If it exists, append _1, _2, etc.
    counter = 1
    while os.path.exists(final_path):
        final_name = f"{base_name}_{counter}{extension}"
        final_path = os.path.join(temp_dir, final_name)
        counter += 1

    # Save file contents
    with open(final_path, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    return final_path
