from sqlalchemy.orm import Session
from app.schemas.answer_schema import AnswerResponse
from app.models.answer import Answer
from app.repositories.answer_repository import AnswerRepository
from app.repositories.chunk_repository import ChunkRepository
from app.models.query import Query
from app.repositories.query_repository import QueryRepository
from app.repositories.conversation_repository import ConversationRepository
from app.utility.OpenAi.embedding import get_chunk_embedding
from app.utility.OpenAi.prompt import ask_openai
from app.models.conversation import Conversation


class QueryService:
    @staticmethod
    def create_query(db: Session, conversation_id: int, workspace_id: int, text: str, user_id: int) -> AnswerResponse:
        # ✅ Check conversation belongs to this user
        convRepo = ConversationRepository(db)
        convo = convRepo.get_by_id(conversation_id, workspace_id, user_id)
        if not convo:
            raise ValueError("Conversation not found or not yours")


        query = Query(
            conversation_id=conversation_id, 
            owner_id=user_id,
            workspace_id=workspace_id,
            query_text=text
        )
        queryResponse = QueryRepository(db).create(query)

        query_embedding = get_chunk_embedding(queryResponse.query_text)

        chunkRepo = ChunkRepository(db)
        similar_chunks = chunkRepo.search_similar_chunks(query_embedding, workspace_id)
        print(f"Found {len(similar_chunks)} similar chunks")
        if not similar_chunks:
            return {"query": query, "response": "No relevant information found in the workspace."}
        # turn to list of texts
        prepared_chunks = [f"{chunk.text}\n\n{chunk.title} (Page {chunk.page_number})" for chunk in similar_chunks]

        print(f"Similar Chunks: {prepared_chunks}")
        
        # Step 3: Use OpenAI to generate a response
        response = ask_openai(queryResponse.query_text, prepared_chunks)

        citations = [
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "title": chunk.title,
                "page_number": chunk.page_number,
                "source_uri": chunk.source_uri
            }
            for chunk in similar_chunks
        ]

        answer = Answer(
            query_id=queryResponse.id,
            conversation_id=conversation_id,
            text=response,
            sources=citations
        )

        
        try:
            created_answer = AnswerRepository(db).create(answer)
            print(f"Created answer: {created_answer}")
            print(f"Answer ID: {created_answer.id if created_answer else 'None'}")
            print(f"Answer sources: {created_answer.sources}")
            print(f"Answer text length: {len(created_answer.text) if created_answer.text else 0}")
            print(f"About to return answer: {type(created_answer)}")
            return created_answer
        except Exception as e:
            print(f"Exception in QueryService.create_query: {e}")
            print(f"Exception type: {type(e)}")
            raise
         

    @staticmethod
    def list_queries(db: Session, conversation_id: int, workspace_id: int, user_id: int):
        # ✅ Check conversation belongs to this user
        convRepo = ConversationRepository(db)
        convo = convRepo.get_by_id(conversation_id, workspace_id, user_id)
        if not convo:
            raise ValueError("Conversation not found or not yours")

        return QueryRepository(db).list_by_conversation(conversation_id)
