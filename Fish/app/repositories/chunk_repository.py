from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.source import Source
from app.models.chunk import Chunk
from app.schemas.document_schema import DocumentCreate, DocumentResponse
from pgvector.sqlalchemy import Vector
from sqlalchemy import select
from typing import List


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_create(self, chunk_instances: list):
        """Bulk create chunk instances in the database."""
        self.db.bulk_save_objects(chunk_instances)
        self.db.commit()

    def get_by_document_id(self, document_id: int):
        return self.db.query(Chunk).filter(Chunk.document_id == document_id).first()
    
    def search_similar_chunks(self, embedding: list, workspace_id: int, top_k: int = 5) -> List[Chunk]:
        """
        Search for the most similar chunks based on the provided embedding.
        Uses pgvector's <-> operator (cosine distance).
        """
        stmt = (
            select(Chunk)
            .join(Chunk.document)             # Chunk → Document
            .join(Document.source)            # Document → Source
            .join(Source.workspace)           # Source → Workspace
            .where(Source.workspace_id == workspace_id)
            .order_by(Chunk.embedding.cosine_distance(embedding))  # or l2_distance
            .limit(top_k)
        )
        return self.db.scalars(stmt).all()
