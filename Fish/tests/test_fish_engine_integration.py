from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

from app.schemas.answer_schema import AnswerResponse, CitationSchema
from app.schemas.workspace_schema import (
    WorkspaceCreate,
    WorkspacePipelineConfig,
    WorkspaceResponse,
)
from app.services.query_service import QueryService
from fish_engine.models import Citation, GenerationResult, PipelineTrace, StageSpan
from fish_engine.pipeline.chunkers import RecursiveChunker, SemanticChunker
from fish_engine.pipeline.retrievers import (
    HybridRetriever,
    LexicalRetriever,
    VectorRetriever,
)


def test_workspace_pipeline_config_defaults_and_custom():
    default_ws = WorkspaceCreate(name="Default Enterprise WS")
    assert default_ws.pipeline_config.preset == "bedrock_enterprise"
    assert default_ws.pipeline_config.chunker == "semantic"
    assert default_ws.pipeline_config.embedder_provider == "bedrock"
    assert default_ws.pipeline_config.retriever_strategy == "hybrid"
    assert default_ws.pipeline_config.reranker_enabled is True
    assert default_ws.pipeline_config.conversational_memory is True
    assert default_ws.pipeline_config.semantic_cache is True

    custom_ws = WorkspaceCreate(
        name="Fast Vector WS",
        pipeline_config=WorkspacePipelineConfig(
            preset="fast",
            chunker="recursive",
            chunk_size=1024,
            embedder_provider="openai",
            embedder_model="text-embedding-3-small",
            retriever_strategy="vector",
            top_k=8,
            reranker_enabled=False,
            window_size=0,
            generator_provider="openai",
            generator_model="gpt-4o-mini",
        ),
    )
    dumped = custom_ws.pipeline_config.model_dump()
    assert dumped["preset"] == "fast"
    assert dumped["chunker"] == "recursive"
    assert dumped["embedder_provider"] == "openai"
    assert dumped["retriever_strategy"] == "vector"
    assert dumped["reranker_enabled"] is False


def test_answer_response_accepts_native_fish_engine_citations_and_telemetry():
    native_citation = Citation(
        source_index=1,
        chunk_id="50e81cac-81fb-446c-a4a2-0b1cc56b8388",
        document_id="doc_1_grok.pdf",
        page_number=21,
        snippet="KGS uses two tables: one for unused keys and one for used keys.",
        score=0.96,
        metadata={
            "workspace_id": "1",
            "title": "Grokking the System Design Interview",
            "swordfish_document_id": 1,
            "source_id": 1,
        },
    )

    resp = AnswerResponse(
        id=10,
        query_id=5,
        conversation_id=1,
        text="KGS pre-generates keys into two tables [Source 1].",
        sources=[native_citation.model_dump()],
        meta={
            "model_id": "us.meta.llama3-3-70b-instruct-v1:0",
            "latency_ms": 1420.5,
            "input_tokens_count": 3200,
            "output_tokens_count": 115,
            "rewritten_query": "How does KGS handle concurrency in TinyURL?",
            "cached": False,
        },
        created_at=datetime.utcnow(),
    )

    assert resp.id == 10
    assert len(resp.sources) == 1
    assert resp.sources[0]["chunk_id"] == "50e81cac-81fb-446c-a4a2-0b1cc56b8388"
    assert resp.sources[0]["metadata"]["title"] == "Grokking the System Design Interview"
    assert resp.meta["rewritten_query"] == "How does KGS handle concurrency in TinyURL?"

    # Also verify CitationSchema validates both native and legacy shapes
    validated_native = CitationSchema(**native_citation.model_dump())
    assert validated_native.source_index == 1
    validated_legacy = CitationSchema(chunk_id=1, document_id=1, title="Legacy Doc", page_number=4)
    assert validated_legacy.title == "Legacy Doc"


def test_get_rag_pipeline_factory_dimensions_and_strategies():
    from sqlalchemy import create_engine
    import app.core.rag_pipeline as rp

    test_engine = create_engine("sqlite:///:memory:")
    rp._pipeline_cache.clear()

    with patch.object(rp, "engine", test_engine):
        # 1. Default Bedrock Enterprise preset -> 1024d table + HybridRetriever + SemanticChunker
        p_bedrock = rp.get_rag_pipeline({"preset": "bedrock_enterprise"})
        assert isinstance(p_bedrock.chunker, SemanticChunker)
        assert isinstance(p_bedrock.retriever, HybridRetriever)
        assert p_bedrock.chunk_store.vector_table_name == "fish_vectors_1024"
        assert p_bedrock.query_rewriter is not None

        # Cached singleton for identical config
        assert rp.get_rag_pipeline({"preset": "bedrock_enterprise"}) is p_bedrock

        # 2. OpenAI Fast Vector preset -> 1536d table + VectorRetriever + RecursiveChunker
        p_openai = rp.get_rag_pipeline(
            {
                "preset": "fast",
                "chunker": "recursive",
                "embedder_provider": "openai",
                "embedder_model": "text-embedding-3-small",
                "retriever_strategy": "vector",
                "reranker_enabled": False,
                "generator_provider": "openai",
                "generator_model": "gpt-4o-mini",
            }
        )
        assert p_openai is not p_bedrock
        assert isinstance(p_openai.chunker, RecursiveChunker)
        assert isinstance(p_openai.retriever, VectorRetriever)
        assert p_openai.chunk_store.vector_table_name == "fish_vectors_1536"
        assert p_openai.reranker is None

        # 3. Lexical retriever option
        p_lex = rp.get_rag_pipeline(
            {
                "preset": "custom",
                "retriever_strategy": "lexical",
                "reranker_enabled": False,
            }
        )
        assert isinstance(p_lex.retriever, LexicalRetriever)


def test_query_service_create_query_delegates_to_pipeline_ask():
    mock_db = MagicMock()

    mock_convo = MagicMock()
    mock_convo.id = 1

    mock_ws = MagicMock()
    mock_ws.id = 1
    mock_ws.owner_id = 1
    mock_ws.pipeline_config = {
        "top_k": 15,
        "rerank_top_k": 5,
        "conversational_memory": True,
    }

    mock_saved_query = MagicMock()
    mock_saved_query.id = 99
    mock_saved_query.query_text = "How does it prevent collisions?"

    mock_prior_q = MagicMock()
    mock_prior_q.id = 98
    mock_prior_q.query_text = "How does KGS work?"

    mock_prior_a = MagicMock()
    mock_prior_a.query_id = 98
    mock_prior_a.text = "KGS pre-generates 6-character keys."

    native_cit = Citation(
        source_index=1,
        chunk_id="cid-123",
        document_id="doc_1_grok.pdf",
        page_number=21,
        snippet="KGS synchronizes access to unused keys.",
        score=0.95,
        metadata={"title": "grok.pdf", "source_id": 1},
    )
    fake_gen_result = GenerationResult(
        query="How does it prevent collisions?",
        answer="It synchronizes access to the unused key table [Source 1].",
        source_chunks=[],
        citations=[native_cit],
        model_id="us.meta.llama3-3-70b-instruct-v1:0",
        latency_ms=850.0,
        input_tokens_count=1200,
        output_tokens_count=45,
        metadata={"rewritten_query": "How does KGS prevent key collisions?"},
    )

    mock_pipeline = MagicMock()
    mock_pipeline.ask.return_value = fake_gen_result
    mock_pipeline.last_trace = PipelineTrace(
        trace_id="trace-1",
        operation="ask",
        total_latency_ms=910.0,
        spans=[
            StageSpan(
                span_id="s1",
                stage_name="retrieve",
                class_name="HybridRetriever",
                latency_ms=120.0,
            )
        ],
    )

    with (
        patch("app.services.query_service.ConversationRepository") as MockConvRepo,
        patch("app.services.query_service.WorkspaceRepository") as MockWsRepo,
        patch("app.services.query_service.QueryRepository") as MockQueryRepo,
        patch("app.services.query_service.AnswerRepository") as MockAnsRepo,
        patch("app.services.query_service.get_rag_pipeline", return_value=mock_pipeline),
    ):
        MockConvRepo.return_value.get_by_id.return_value = mock_convo
        MockWsRepo.return_value.get_by_id.return_value = mock_ws
        MockQueryRepo.return_value.create.return_value = mock_saved_query
        MockQueryRepo.return_value.list_by_conversation.return_value = [
            mock_prior_q,
            mock_saved_query,
        ]
        MockAnsRepo.return_value.list_by_conversation.return_value = [mock_prior_a]
        MockAnsRepo.return_value.create.side_effect = lambda ans: ans

        created_answer = QueryService.create_query(
            db=mock_db,
            conversation_id=1,
            workspace_id=1,
            text="How does it prevent collisions?",
            user_id=1,
        )

        mock_pipeline.ask.assert_called_once_with(
            query="How does it prevent collisions?",
            top_k=15,
            rerank_top_k=5,
            filters={"workspace_id": "1"},
            chat_history=[
                {"role": "user", "content": "How does KGS work?"},
                {"role": "assistant", "content": "KGS pre-generates 6-character keys."},
            ],
        )

        assert created_answer.text == "It synchronizes access to the unused key table [Source 1]."
        assert len(created_answer.sources) == 1
        assert created_answer.sources[0]["chunk_id"] == "cid-123"
        assert created_answer.sources[0]["metadata"]["title"] == "grok.pdf"
        assert created_answer.meta["rewritten_query"] == "How does KGS prevent key collisions?"
        assert created_answer.meta["trace"]["total_latency_ms"] == 910.0


def test_query_service_list_answers_and_conversation_answers():
    from app.repositories.query_repository import QueryRepository

    mock_db = MagicMock()
    repo = QueryRepository(mock_db)
    repo.get_by_id(query_id=10, conversation_id=4, workspace_id=3, user_id=1)

    with (
        patch("app.services.query_service.ConversationRepository") as MockConvRepo,
        patch("app.services.query_service.QueryRepository", wraps=QueryRepository),
        patch("app.services.query_service.AnswerRepository") as MockAnsRepo,
    ):
        MockConvRepo.return_value.get_by_id.return_value = MagicMock(id=4)
        mock_db.query.return_value.filter.return_value.filter.return_value.filter.return_value.first.return_value = MagicMock(id=10)
        MockAnsRepo.return_value.list_by_query.return_value = [MagicMock(id=100, text="ans1")]
        MockAnsRepo.return_value.list_by_conversation.return_value = [
            MagicMock(id=100, text="ans1"),
            MagicMock(id=101, text="ans2"),
        ]

        res_single = QueryService.list_answers(
            db=mock_db,
            query_id=10,
            conversation_id=4,
            workspace_id=3,
            user_id=1,
        )
        assert len(res_single) == 1

        res_convo = QueryService.list_conversation_answers(
            db=mock_db,
            conversation_id=4,
            workspace_id=3,
            user_id=1,
        )
        assert len(res_convo) == 2

