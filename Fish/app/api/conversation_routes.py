from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.conversation_schema import ConversationResponse
from app.schemas.query_schema import QueryResponse
from app.schemas.answer_schema import AnswerResponse
from app.services.conversation_service import ConversationService
from app.services.query_service import QueryService
from app.models.user import User
from app.models.conversation import Conversation
from app.models.query import Query
from app.models.answer import Answer
from app.core.dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.dependencies import get_current_user, get_db



router = APIRouter(prefix="/workspaces/{workspace_id}/conversations", tags=["Conversations"])


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return ConversationService.create_conversation(db, workspace_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[ConversationResponse])
def list_conversations(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return ConversationService.list_conversations(db, workspace_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/{conversation_id}/queries", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
def create_query(workspace_id: int, conversation_id: int, text: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return QueryService.create_query(db, conversation_id, workspace_id, text, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))