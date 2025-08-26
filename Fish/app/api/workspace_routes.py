from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.dependencies import get_current_user, get_db
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceResponse
from app.schemas.token_schema import Token
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.dependencies import get_current_user, get_db
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceResponse
from app.schemas.token_schema import Token
from app.repositories.chunk_repository import ChunkRepository
from app.utility.OpenAi.prompt import ask_openai
from app.utility.OpenAi.embedding import get_chunk_embedding
from fastapi.security import OAuth2PasswordRequestForm



router = APIRouter(prefix="/workspace", tags=["Workspace"])


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(workspace: WorkspaceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return WorkspaceService.create_workspace(db, workspace, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return WorkspaceService.get_workspace(db, workspace_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    




@router.post("/{workspace_id}/query")
def query_workspace(workspace_id: int, query: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        # Step 1: Embed the query
        query_embedding = get_chunk_embedding(query)

        # Step 2: Search for similar chunks
        chunkRepo = ChunkRepository(db)
        similar_chunks = chunkRepo.search_similar_chunks(query_embedding, workspace_id)
        print(f"Found {len(similar_chunks)} similar chunks")
        if not similar_chunks:
            return {"query": query, "response": "No relevant information found in the workspace."}
        # turn to list of texts
        similar_chunks = [f"{chunk.text}\n\n(Page {chunk.page_number})" for chunk in similar_chunks]

        print(f"Similar Chunks: {similar_chunks}")
        
        # Step 3: Use OpenAI to generate a response
        response = ask_openai(query, similar_chunks)

        # Step 4: Return the response
        return {"query": query, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))