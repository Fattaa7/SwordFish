from sqlalchemy.orm import Session
from app.models.source import Source, SourceStatus
from app.schemas.source_schema import SourceCreate, SourceResponse 

class SourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, source_id: int) -> SourceResponse:
        return self.db.query(Source).filter(Source.id == source_id).first()

    def get_by_workspace_id(self, workspace_id: int):
        return self.db.query(Source).filter(Source.workspace_id == workspace_id).all()

    def create(self, source: SourceCreate, workspace_id: int) -> SourceResponse: 
        db_source = Source(
            workspace_id=workspace_id,
            type=source.type,
            status=SourceStatus.UPLOADED,  # Set initial status
            url=source.url,
            storage_path=source.storage_path,
            mime_type=None,  # Will be set during metadata extraction
            checksum=None,    # Will be set during metadata extraction
            error=None
        )
        self.db.add(db_source)
        self.db.commit()
        self.db.refresh(db_source)
        return db_source

    def update(self, source: SourceResponse) -> SourceResponse:
        db_source = self.get_by_id(source.id)
        if not db_source:
            return None
    
        # Explicitly map fields like in create
        db_source.type = source.type
        db_source.status = source.status
        db_source.url = source.url
        db_source.storage_path = source.storage_path
        db_source.mime_type = source.mime_type
        db_source.checksum = source.checksum
        db_source.error = source.error
    
        self.db.commit()
        self.db.refresh(db_source)
        return db_source
    

    def delete(self, source_id: int) -> bool:
        """Delete a source by ID"""
        source = self.get_by_id(source_id)
        if source:
            self.db.delete(source)
            self.db.commit()
            return True
        return False
