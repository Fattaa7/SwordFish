from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.conversation_schema import ConversationResponse
from app.schemas.query_schema import QueryCreate, QueryResponse
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
    
@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(workspace_id: int, conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        convo = ConversationService.get_conversation(db, conversation_id, workspace_id, current_user.id)
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return convo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/{conversation_id}/queries", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
def create_query(workspace_id: int, conversation_id: int, query: QueryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        response =  QueryService.create_query(db, conversation_id, workspace_id, query.text, current_user.id)
        if len(QueryService.list_queries(db, conversation_id, workspace_id, current_user.id)) == 1:
            convo = ConversationService.name_conversation(db, conversation_id, workspace_id, query.text, current_user.id)
            print(f"Conversation renamed to: {convo.title}")
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{conversation_id}/queries", response_model=list[QueryResponse])
def list_queries(workspace_id: int, conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return QueryService.list_queries(db, conversation_id, workspace_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{conversation_id}/answers", response_model=list[AnswerResponse])
def list_answers(workspace_id: int, conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        queries = QueryService.list_queries(db, conversation_id, workspace_id, current_user.id)
        if not queries:
            return []
        all_answers = []
        for query in queries:
            answers = QueryService.list_answers(db, query.id, conversation_id, workspace_id, current_user.id)
            all_answers.extend(answers)
        return all_answers
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))