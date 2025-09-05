from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from app.models.chunk import Chunk
from app.repositories.chunk_repository import ChunkRepository
from app.utility.text_extractor import split_markdown_into_pages
from app.utility.chunker import chunk_markdown_text
from app.utility.OpenAi.embedding_mock import batch_get_chunk_embeddings, get_chunk_embedding  # must support batch input



class ChunkService:
    @staticmethod
    def create_chunks_for_document(db: Session, document_id: int, file_path: str, source_path: str, title: str = "Untitled Document"):
        """
        Optimized: Split document into pages, process pages in parallel,
        batch embedding per page, bulk save all chunks.
        """
        pages = split_markdown_into_pages(file_path)
        all_chunks = []

        def process_page(page_number, page_text):
            # Chunk text within page
            chunks = chunk_markdown_text(page_text)

            # Batch embeddings
            texts = [chunk.text for chunk in chunks]
            embeddings = batch_get_chunk_embeddings(texts)  # return list of embeddings

            chunk_instances = []
            for idx, chunk in enumerate(chunks):
                chunk_instances.append(
                    Chunk(
                        document_id=document_id,
                        title=title,
                        index=idx,
                        token_count=chunk.token_count,
                        text=chunk.text,
                        embedding=embeddings[idx],
                        source_uri=str(source_path),
                        page_number=page_number
                    )
                )
            return chunk_instances

        # Threaded page processing
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(process_page, i + 1, page) for i, page in enumerate(pages)]
            for future in as_completed(futures):
                all_chunks.extend(future.result())

        # Bulk insert into DB
        chunkRepo = ChunkRepository(db)
        chunkRepo.bulk_create(all_chunks)
        print(f"Created {len(all_chunks)} chunks for document ID {document_id}")
