from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.services.document_service import DocumentService
from app.models.user import User
from app.core.dependencies import get_current_user, get_db
from app.schemas.document_schema import DocumentResponse
from typing import List

router = APIRouter(prefix="/workspaces/{workspace_id}/documents", tags=["documents"])



@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    workspace_id: int,
    document_id: int,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get a specific document by ID within a workspace"""
    try:
        return DocumentService.get_document(db, workspace_id, document_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

