from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.dependencies import get_current_user, get_db
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceResponse
from app.schemas.token_schema import Token
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