from sqlalchemy.orm import Session
from app.schemas.query_schema import QueryResponse
from app.utility.rerank import rerank
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
    
        list_of_texts = [chunk.text for chunk in similar_chunks]
        reranked_results = rerank(queryResponse.query_text, list_of_texts)
        print(f"Reranked Results: {reranked_results}")
    
        # keep reranked chunks (could filter by score if you want)
        filtered_chunks = [similar_chunks[rank.index] for rank in reranked_results.results]
    
        print(f"Found {len(filtered_chunks)} similar chunks")
        if not filtered_chunks:
            return {"query": query, "response": "No relevant information found in the workspace."}
    
        # prepare text with metadata for LLM
        prepared_chunks = [
            f"{chunk.text}\n\n{chunk.title} (Page {chunk.page_number})"
            for chunk in filtered_chunks
        ]
        print(f"Similar Chunks: {prepared_chunks}")
    
        # Step 3: Use OpenAI
        result = ask_openai(queryResponse.query_text, prepared_chunks)
        print(f"OpenAI Result: {result}")
    
        # 🔑 Map back used indices to real chunks
        used_citations = [
            {
                "chunk_id": filtered_chunks[i].id,
                "document_id": filtered_chunks[i].document_id,
                "title": filtered_chunks[i].title,
                "page_number": filtered_chunks[i].page_number,
                "source_uri": filtered_chunks[i].source_uri
            }
            for i in result["used_chunk_ids"] if i < len(filtered_chunks)
        ]
    
        answer = Answer(
            query_id=queryResponse.id,
            conversation_id=conversation_id,
            text=result["answer"],
            sources=used_citations
        )
    
        try:
            created_answer = AnswerRepository(db).create(answer)
            return created_answer
        except Exception as e:
            raise ValueError(f"Failed to create answer: {e}") from e
             

    @staticmethod
    def list_queries(db: Session, conversation_id: int, workspace_id: int, user_id: int) -> list[QueryResponse]:
        # ✅ Check conversation belongs to this user
        convRepo = ConversationRepository(db)
        convo = convRepo.get_by_id(conversation_id, workspace_id, user_id)
        if not convo:
            raise ValueError("Conversation not found or not yours")

        return QueryRepository(db).list_by_conversation(conversation_id)

    @staticmethod
    def list_answers(db: Session, query_id: int, conversation_id: int, workspace_id: int, user_id: int) -> list[AnswerResponse]:
        # ✅ Check conversation belongs to this user
        convRepo = ConversationRepository(db)
        convo = convRepo.get_by_id(conversation_id, workspace_id, user_id)
        if not convo:
            raise ValueError("Conversation not found or not yours")

        # ✅ Check query belongs to this conversation
        queryRepo = QueryRepository(db)
        query = queryRepo.get_by_id(query_id, conversation_id)
        if not query:
            raise ValueError("Query not found or does not belong to this conversation")

        return AnswerRepository(db).list_by_query(query_id)