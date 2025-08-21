from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document_schema import DocumentCreate, DocumentResponse

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, document_id: int):
        return self.db.query(Document).filter(Document.id == document_id).first()

    def get_by_source_id(self, source_id: int):
        return self.db.query(Document).filter(Document.source_id == source_id).first()

    def create(self, document: DocumentCreate, source_id: int) -> Document:
        db_document = Document(
            source_id=source_id,
            title=document.title or "Untitled Document",
            language=document.language,
            meta=document.meta.dict() if document.meta else None
        )
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        return db_document

    def update(self, document_id: int, document: DocumentCreate) -> Document:
        db_document = self.get_by_id(document_id)
        if not db_document:
            raise ValueError("Document not found")
        
        if document.title is not None:
            db_document.title = document.title
        if document.language is not None:
            db_document.language = document.language
        if document.meta is not None:
            db_document.meta = document.meta.dict()
        
        self.db.commit()
        self.db.refresh(db_document)
        return db_document

    def delete(self, document_id: int):
        db_document = self.get_by_id(document_id)
        if db_document:
            self.db.delete(db_document)
            self.db.commit()
            return True
        return False
