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
    def create_chunks_for_document(db: Session, document_id: int, file_path: str, source_path: str, title: str = "Untitled Document"):
        """Create chunks for a given document and store them in the database."""

        print(f"Starting chunk creation for document ID: {document_id}")
        print(f"File path: {file_path}")
        
        # Split the markdown file into pages first
        print("Splitting markdown into pages...")
        pages = split_markdown_into_pages(file_path)
        print(f"Split into {len(pages)} pages")

        chunk_instances = []
        for page_number, page_text in enumerate(pages, start=1):
            print(f"Processing page {page_number}...")
            # Chunk within each page
            chunks = chunk_markdown_text(page_text)
            print(f"Page {page_number} split into {len(chunks)} chunks")

            for idx, chunk in enumerate(chunks):
                print(f"Getting embedding for chunk {idx+1}/{len(chunks)} on page {page_number}...")
                # Get embedding for the chunk text
                embeddawy = get_chunk_embedding(chunk.text)
                print(f"Embedding received for chunk {idx+1}")

                chunk_instance = Chunk(
                    document_id=document_id,
                    title=title,
                    index=idx,
                    token_count=chunk.token_count,
                    text=chunk.text,
                    embedding=embeddawy,
                    source_uri=str(source_path),
                    page_number=page_number + 1  # <-- new field
                )
                chunk_instances.append(chunk_instance)

        print(f"Creating {len(chunk_instances)} chunks for document ID {document_id}")

        # Bulk save chunks to the database
        chunkRepo = ChunkRepository(db)
        chunkRepo.bulk_create(chunk_instances)
