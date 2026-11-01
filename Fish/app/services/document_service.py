import mimetypes
from pathlib import Path
import requests
from sqlalchemy.orm import Session

from app.core.rag_pipeline import get_rag_pipeline
from app.models.source import SourceType
from app.repositories.document_repository import DocumentRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.document_schema import DocumentCreate

from fish_engine.models import RawDocument


class DocumentService:
    @staticmethod
    def create(db: Session, document: DocumentCreate, source_id: int, owner_id: int):
        source_repo = SourceRepository(db)
        doc_repo = DocumentRepository(db)

        # 1. Verify source exists and belongs to the user's workspace
        source = source_repo.get_by_id(source_id)
        if not source or source.workspace.owner_id != owner_id:
            raise ValueError("Source not found or you do not have permission to access it")

        # 2. Load raw document content (File or URL)
        if source.type == SourceType.URL and source.url:
            resp = requests.get(source.url, timeout=30)
            resp.raise_for_status()
            raw_content = resp.text
            source_name = f"url_source_{source.id}.txt"
            mime_type = "text/plain"
            uri_reference = source.url
        else:
            if not document.source_path:
                raise ValueError("Source file path is missing")
            source_path = Path(document.source_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")
            raw_content = source_path.read_bytes()
            source_name = source_path.name
            guessed_mime, _ = mimetypes.guess_type(source_name)
            mime_type = guessed_mime or "application/pdf"
            uri_reference = str(source_path)

        # 3. Create or reuse Document metadata record in SwordFish's relational `documents` table
        existing_docs = list(source.documents or [])
        if existing_docs:
            doc_record = existing_docs[0]
        else:
            doc_record = doc_repo.create(
                document=document,
                source_id=source_id,
                uri_path=uri_reference,
            )

        # 4. Run full ingestion (Parse -> Semantic Chunk -> Store Chunks -> Embed -> Index pgvector) via fish-engine
        doc_identifier = f"doc_{doc_record.id}_{source_name}"
        raw_doc = RawDocument(
            filename=doc_identifier,
            mime_type=mime_type,
            content=raw_content,
            metadata={
                "workspace_id": str(source.workspace_id),
                "swordfish_document_id": doc_record.id,
                "source_id": source.id,
                "title": document.title,
                "source_uri": uri_reference,
            },
        )

        pipeline = get_rag_pipeline(source.workspace.pipeline_config)
        chunk_count = pipeline.ingest(raw_doc, overwrite=True)

        print(
            f"[SwordFish x fish-engine] Ingested Document ID {doc_record.id} "
            f"('{document.title}') -> {chunk_count} chunks indexed in PostgresStore."
        )
        return doc_record

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

        if document.source.workspace.owner_id != owner_id:
            raise ValueError("You do not have permission to access this document")

        return document
