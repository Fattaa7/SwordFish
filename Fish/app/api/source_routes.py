from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.services.source_service import SourceService
from app.models.user import User
from app.core.dependencies import get_current_user, get_db
from app.schemas.source_schema import SourceResponse
from typing import List

router = APIRouter(prefix="/workspaces/{workspace_id}/sources", tags=["Sources"])



@router.get("/sources/{source_id}/download")
async def download_source(workspace_id: int, source_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Download a source file by its ID"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return SourceService.download_source(db, source_id, workspace_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))




@router.post("/upload", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(workspace_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Upload a file and create a source with extracted metadata"""
    try:
        return SourceService.upload_file(db, workspace_id, file, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))





@router.post("/url", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_url_source(
    workspace_id: int,
    url: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a source from a URL"""
    try:
        return SourceService.create_from_url(db, workspace_id, url, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))






@router.get("/", response_model=List[SourceResponse])
def get_sources(
    workspace_id: int,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get all sources for a workspace"""
    try:
        return SourceService.get_sources_by_workspace(db, workspace_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






@router.get("/{source_id}", response_model=SourceResponse)
def get_source(
    workspace_id: int,
    source_id: int,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get a specific source by ID"""
    try:
        return SourceService.get_source_by_id(db, workspace_id, source_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    workspace_id: int,
    source_id: int,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Delete a specific source by ID"""
    try:
        SourceService.delete_source(db, workspace_id, source_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

