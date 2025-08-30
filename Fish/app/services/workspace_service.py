from sqlalchemy.orm import Session
from app.repositories.chunk_repository import ChunkRepository
from app.utility.OpenAi.embedding import get_chunk_embedding
from app.utility.OpenAi.prompt import ask_openai
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceResponse

class WorkspaceService:
    @staticmethod
    def create_workspace(db: Session, workspace: WorkspaceCreate, owner_id: int) -> WorkspaceResponse:
        repo = WorkspaceRepository(db)

        # Create workspace via repository
        return repo.create(name=workspace.name, owner_id=owner_id)

    @staticmethod
    def get_workspace(db: Session, workspace_id: int, owner_id: int):
        repo = WorkspaceRepository(db)
        workspace = repo.get_by_id(workspace_id)

        if not workspace:
            raise ValueError("Workspace not found")

        if workspace.owner_id != owner_id:
            raise ValueError("You do not have permission to access this workspace")

        return workspace
    
    @staticmethod
    def list_workspaces(db: Session, owner_id: int):
        repo = WorkspaceRepository(db)
        return repo.list_by_owner(owner_id)
    

    @staticmethod
    def query_workspace(db: Session, workspace_id: int, query: str, owner_id: int):
                # Step 1: Embed the query
        query_embedding = get_chunk_embedding(query)

        # Step 2: Search for similar chunks
        chunkRepo = ChunkRepository(db)
        similar_chunks = chunkRepo.search_similar_chunks(query_embedding, workspace_id)
        print(f"Found {len(similar_chunks)} similar chunks")
        if not similar_chunks:
            return {"query": query, "response": "No relevant information found in the workspace."}
        # turn to list of texts
        similar_chunks = [f"{chunk.text}\n\n{chunk.title} (Page {chunk.page_number})" for chunk in similar_chunks]

        print(f"Similar Chunks: {similar_chunks}")
        
        # Step 3: Use OpenAI to generate a response
        response = ask_openai(query, similar_chunks)
