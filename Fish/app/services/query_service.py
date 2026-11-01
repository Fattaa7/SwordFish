import json
from typing import Dict, Iterator, List
from sqlalchemy.orm import Session

from app.core.rag_pipeline import get_rag_pipeline
from app.models.answer import Answer
from app.models.query import Query
from app.repositories.answer_repository import AnswerRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.query_repository import QueryRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.answer_schema import AnswerResponse
from app.schemas.query_schema import QueryResponse


class QueryService:
    @staticmethod
    def _build_chat_history(
        db: Session,
        conversation_id: int,
        current_query_id: int,
        max_messages: int = 6,
    ) -> List[Dict[str, str]]:
        """
        Loads the last `max_messages` (up to 3 user/assistant turns) from this conversation
        prior to `current_query_id`, formatted for `fish-engine`'s `chat_history` parameter.
        """
        prior_queries = [
            q
            for q in QueryRepository(db).list_by_conversation(conversation_id)
            if q.id != current_query_id
        ]
        if not prior_queries:
            return []

        answers_by_qid: Dict[int, Answer] = {}
        for ans in AnswerRepository(db).list_by_conversation(conversation_id):
            if ans.query_id not in answers_by_qid:
                answers_by_qid[ans.query_id] = ans

        history: List[Dict[str, str]] = []
        for q in prior_queries[-(max_messages // 2) :]:
            history.append({"role": "user", "content": q.query_text})
            ans = answers_by_qid.get(q.id)
            if ans and ans.text:
                history.append({"role": "assistant", "content": ans.text})
        return history[-max_messages:]

    @staticmethod
    def create_query(
        db: Session,
        conversation_id: int,
        workspace_id: int,
        text: str,
        user_id: int,
    ) -> AnswerResponse:
        # 1. Verify conversation and workspace ownership
        conv_repo = ConversationRepository(db)
        convo = conv_repo.get_by_id(conversation_id, workspace_id, user_id)
        if not convo:
            raise ValueError("Conversation not found or not yours")

        workspace = WorkspaceRepository(db).get_by_id(workspace_id)
        if not workspace or workspace.owner_id != user_id:
            raise ValueError("Workspace not found or not yours")

        cfg = workspace.pipeline_config or {}

        # 2. Persist user query in SwordFish's `queries` table
        query = Query(
            conversation_id=conversation_id,
            owner_id=user_id,
            workspace_id=workspace_id,
            query_text=text,
        )
        query_response = QueryRepository(db).create(query)

        # 3. Load multi-turn conversational history (if enabled on workspace)
        chat_history = (
            QueryService._build_chat_history(db, conversation_id, query_response.id)
            if cfg.get("conversational_memory", True)
            else None
        )

        # 4. Execute full RAG flow via fish-engine's native `pipeline.ask()`
        pipeline = get_rag_pipeline(cfg)
        gen_result = pipeline.ask(
            query=query_response.query_text,
            top_k=int(cfg.get("top_k", 20)),
            rerank_top_k=int(cfg.get("rerank_top_k", 10)),
            filters={"workspace_id": str(workspace_id)},
            chat_history=chat_history or None,
        )

        trace_dict = None
        if pipeline.last_trace is not None:
            trace_dict = pipeline.last_trace.model_dump(
                exclude={"spans": {"__all__": {"input_payload", "output_payload"}}}
            )

        meta = {
            "model_id": gen_result.model_id,
            "latency_ms": gen_result.latency_ms,
            "input_tokens_count": gen_result.input_tokens_count,
            "output_tokens_count": gen_result.output_tokens_count,
            "rewritten_query": gen_result.metadata.get("rewritten_query"),
            "cached": bool(gen_result.metadata.get("cached", False)),
            "trace": trace_dict,
        }

        answer = Answer(
            query_id=query_response.id,
            conversation_id=conversation_id,
            text=gen_result.answer,
            sources=[c.model_dump() for c in gen_result.citations],
            meta=meta,
        )

        try:
            return AnswerRepository(db).create(answer)
        except Exception as e:
            raise ValueError(f"Failed to create answer: {e}") from e

    @staticmethod
    def stream_query(
        db: Session,
        conversation_id: int,
        workspace_id: int,
        text: str,
        user_id: int,
    ) -> Iterator[str]:
        """
        Server-Sent Events (SSE) generator powered by `fish-engine`'s `pipeline.ask_stream()`.
        Persists the Query and final Answer + Citations + Trace in PostgreSQL.
        """
        conv_repo = ConversationRepository(db)
        convo = conv_repo.get_by_id(conversation_id, workspace_id, user_id)
        if not convo:
            raise ValueError("Conversation not found or not yours")

        workspace = WorkspaceRepository(db).get_by_id(workspace_id)
        if not workspace or workspace.owner_id != user_id:
            raise ValueError("Workspace not found or not yours")

        cfg = workspace.pipeline_config or {}

        query = Query(
            conversation_id=conversation_id,
            owner_id=user_id,
            workspace_id=workspace_id,
            query_text=text,
        )
        query_response = QueryRepository(db).create(query)

        chat_history = (
            QueryService._build_chat_history(db, conversation_id, query_response.id)
            if cfg.get("conversational_memory", True)
            else None
        )

        pipeline = get_rag_pipeline(cfg)
        yield f"event: query\ndata: {json.dumps({'id': query_response.id, 'query_text': query_response.query_text})}\n\n"

        tokens: List[str] = []
        citations_list: List[dict] = []

        for event_item in pipeline.ask_stream(
            query=query_response.query_text,
            top_k=int(cfg.get("top_k", 20)),
            rerank_top_k=int(cfg.get("rerank_top_k", 10)),
            filters={"workspace_id": str(workspace_id)},
            chat_history=chat_history or None,
        ):
            ev = event_item.get("event")
            data = event_item.get("data")
            if ev == "token":
                tokens.append(str(data))
                yield f"event: token\ndata: {json.dumps({'delta': str(data)})}\n\n"
            elif ev == "citations":
                citations_list = [
                    c.model_dump() if hasattr(c, "model_dump") else c for c in (data or [])
                ]
            elif ev == "error":
                yield f"event: error\ndata: {json.dumps({'error': str(data)})}\n\n"
                return

        full_text = "".join(tokens)
        trace_dict = None
        if pipeline.last_trace is not None:
            trace_dict = pipeline.last_trace.model_dump(
                exclude={"spans": {"__all__": {"input_payload", "output_payload"}}}
            )

        meta = {
            "model_id": getattr(pipeline.generator, "model_name", None),
            "latency_ms": trace_dict.get("total_latency_ms") if trace_dict else None,
            "rewritten_query": (
                pipeline.last_trace.metadata.get("rewritten_query")
                if pipeline.last_trace
                else None
            ),
            "cached": False,
            "trace": trace_dict,
        }

        answer = Answer(
            query_id=query_response.id,
            conversation_id=conversation_id,
            text=full_text,
            sources=citations_list,
            meta=meta,
        )
        saved_answer = AnswerRepository(db).create(answer)
        payload = AnswerResponse.model_validate(saved_answer).model_dump(mode="json")
        yield f"event: done\ndata: {json.dumps(payload)}\n\n"

    @staticmethod
    def list_queries(
        db: Session,
        conversation_id: int,
        workspace_id: int,
        user_id: int,
    ) -> list[QueryResponse]:
        conv_repo = ConversationRepository(db)
        convo = conv_repo.get_by_id(conversation_id, workspace_id, user_id)
        if not convo:
            raise ValueError("Conversation not found or not yours")

        return QueryRepository(db).list_by_conversation(conversation_id)

    @staticmethod
    def list_answers(
        db: Session,
        query_id: int,
        conversation_id: int,
        workspace_id: int,
        user_id: int,
    ) -> list[AnswerResponse]:
        conv_repo = ConversationRepository(db)
        convo = conv_repo.get_by_id(conversation_id, workspace_id, user_id)
        if not convo:
            raise ValueError("Conversation not found or not yours")

        query = QueryRepository(db).get_by_id(query_id, conversation_id, workspace_id, user_id)
        if not query:
            raise ValueError("Query not found or not yours")

        return AnswerRepository(db).list_by_query(query_id)
