from sqlalchemy.orm import Session
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


class SourceService:
    @staticmethod
    def create(db: Session, workspace_id: int, source: SourceCreate, owner_id: int) -> SourceResponse:
        repo = SourceRepository(db)

        # Check if workspace exists and user has permission
        workspace = WorkspaceRepository(db).get_by_id(workspace_id)
        if not workspace or workspace.owner_id != owner_id:
            raise ValueError("Workspace not found or you do not have permission to access it")

        # Create source via repository
        created = repo.create(source=source, workspace_id=workspace_id)

        if not created:
            raise ValueError("Failed to create source")

        # Extract metadata from the source
        source_meta = SourceService._extract_source_metadata(created, source)
        print(f"Extracted metadata: {source_meta}")

        # Create document creation request
        req = DocumentCreate(
            title=source_meta["title"],
            language=source_meta["language"],
            meta=MetaModel(
                author=source_meta["meta"]["author"],
                pages=source_meta["meta"]["pages"],
                tags=source_meta["meta"]["tags"]
            )
        )

        # Create document associated with the source
        DocumentService.create(db, document=req, source_id=created.id, owner_id=owner_id)

        return created

    @staticmethod
    def upload_file(db: Session, workspace_id: int, file: UploadFile, owner_id: int) -> SourceResponse:
        """Upload a file and create a source with extracted metadata"""
        temp_path = None
        try:
            # Create a temporary file to store the upload
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                # Copy the uploaded file to the temporary file
                shutil.copyfileobj(file.file, temp_file)
                temp_path = temp_file.name
            
            # Create source data
            source_data = SourceCreate(
                type=SourceType.FILE,
                storage_path=temp_path,
                url=None
            )
            
            # Create source and extract metadata
            return SourceService.create(db, workspace_id, source_data, owner_id)
            
        except Exception as e:
            # Clean up temporary file if it exists
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e

    @staticmethod
    def create_from_url(db: Session, workspace_id: int, url: str, owner_id: int) -> SourceResponse:
        """Create a source from a URL"""
        try:
            source_data = SourceCreate(
                type=SourceType.URL,
                url=url,
                storage_path=None
            )
            
            return SourceService.create(db, workspace_id, source_data, owner_id)
            
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
    def _extract_source_metadata(source: SourceResponse, source_create: SourceCreate) -> dict:
        """
        Extract metadata from the source based on its type and content
        """
        try:
            if source_create.type == SourceType.FILE and source_create.storage_path:
                # For file uploads, extract metadata from the file
                if os.path.exists(source_create.storage_path):
                    metadata = MetadataExtractor.extract_metadata(source_create.storage_path)
                else:
                    # If file doesn't exist on disk, use basic metadata
                    metadata = {
                        "title": os.path.basename(source_create.storage_path),
                        "language": "unknown",
                        "meta": {
                            "author": None,
                            "pages": None,
                            "tags": []
                        }
                    }
            elif source_create.type == SourceType.URL and source_create.url:
                # For URLs, extract basic metadata
                metadata = {
                    "title": f"Document from {source_create.url}",
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