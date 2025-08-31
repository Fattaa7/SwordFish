# app/tasks/document_tasks.py
from app.models.source import SourceStatus
from app.repositories.source_repository import SourceRepository
from app.celery import celery_app
from app.db.database import SessionLocal

@celery_app.task(name="process_file_task")
def process_file_task(source_id: int, owner_id: int):
    from app.services.source_service import SourceService
    db = SessionLocal()
    source = None
    repo = None
    
    try:
        repo = SourceRepository(db)

        # Fetch source from DB
        source = repo.get_by_id(source_id)
        if not source:
            print(f"Source {source_id} not found")
            return

        # Update status to PROCESSING
        source.status = SourceStatus.PROCESSING
        repo.update(source)

        # Process and create document
        SourceService.create_document(db, source, owner_id)

        # Update status to COMPLETED
        source.status = SourceStatus.PROCESSED
        repo.update(source)
        print(f"File processing completed for source ID: {source_id}")

    except Exception as e:
        if source and repo:
            try:
                source.status = SourceStatus.FAILED
                source.error = str(e)
                repo.update(source)
            except Exception as update_error:
                print(f"Error updating source status: {update_error}")
        print(f"Error processing file task: {e}")
    finally:
        db.close()
