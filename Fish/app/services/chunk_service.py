from sqlalchemy.orm import Session
from app.utility.text_extractor import convert_file_to_markdown, split_markdown_into_pages
from app.repositories.source_repository import SourceRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
from app.schemas.document_schema import DocumentCreate
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.user_schema import UserCreate
from app.core.auth.password import hash_password, verify_password
from app.schemas.token_schema import Token
from app.core.auth.jwt import create_access_token
from pathlib import Path
from app.models.chunk import Chunk
from app.utility.chunker import chunk_file, chunk_markdown_text
from app.utility.OpenAi.embedding import get_chunk_embedding


class ChunkService:
    @staticmethod
    def create_chunks_for_document(db: Session, document_id: int, file_path: str):
        """Create chunks for a given document and store them in the database."""

        # Split the markdown file into pages first
        pages = split_markdown_into_pages(file_path)

        chunk_instances = []
        for page_number, page_text in enumerate(pages, start=1):
            # Chunk within each page
            chunks = chunk_markdown_text(page_text)

            for idx, chunk in enumerate(chunks):
                # Get embedding for the chunk text
                embeddawy = get_chunk_embedding(chunk.text)

                chunk_instance = Chunk(
                    document_id=document_id,
                    index=idx,
                    token_count=chunk.token_count,
                    text=chunk.text,
                    embedding=embeddawy,
                    page_number=page_number + 1  # <-- new field
                )
                chunk_instances.append(chunk_instance)

        print(f"Creating {len(chunk_instances)} chunks for document ID {document_id}")

        # Bulk save chunks to the database
        chunkRepo = ChunkRepository(db)
        chunkRepo.bulk_create(chunk_instances)
