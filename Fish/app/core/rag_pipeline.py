"""
SwordFish Dynamic Per-Workspace RAG Pipeline Factory using `fish-engine` SDK building blocks.

Assembles a workspace-scoped RAG `Pipeline` via `PipelineBuilder` from the workspace's
stored `pipeline_config` (set once at workspace creation):
- Parser:         `RouterParser` + `PyMuPDFParser` (PDF, DOCX, TXT, MD, CSV, HTML)
- Chunker:        `SemanticChunker` | `RecursiveChunker` | `SentenceChunker` | `TokenChunker`
- Embedder:       `BedrockEmbedder` (`amazon.titan-embed-text-v2:0`) | `OpenAIEmbedder`
- Store:          `PostgresStore` (`chunks`, `fish_vectors_{dimension}`, `fish_documents`)
- Retriever:      `HybridRetriever` | `VectorRetriever` | `LexicalRetriever`
- Reranker:       `CohereReranker` (`rerank-v3.5`) + score threshold post-retrieve transform
- Window:         Adjacent chunk window hydration (`window_size`)
- Query Rewriter: `ConversationalQueryRewriter` (resolves follow-up pronouns using `chat_history`)
- Cache:          `SqlAlchemySemanticCache` (workspace-filtered semantic response cache)
- Guardrails:     `InputGuardrail` + `OutputGuardrail`
- Generator:      `BedrockGenerator` (`us.meta.llama3-3-70b-instruct-v1:0`) | `OpenAIGenerator`
"""

import json
from typing import Dict, List, Optional

from app.core.config import settings
from app.db.database import SessionLocal, engine
from app.schemas.workspace_schema import WorkspacePipelineConfig

from fish_engine.models import ChunkDataScored
from fish_engine.pipeline import ConversationalQueryRewriter, Pipeline, PipelineBuilder
from fish_engine.pipeline.cache import SqlAlchemySemanticCache
from fish_engine.pipeline.chunkers import (
    RecursiveChunker,
    SemanticChunker,
    SentenceChunker,
    TokenChunker,
)
from fish_engine.pipeline.embedders import BedrockEmbedder, OpenAIEmbedder
from fish_engine.pipeline.generators import BedrockGenerator, OpenAIGenerator
from fish_engine.pipeline.guardrails import InputGuardrail, OutputGuardrail
from fish_engine.pipeline.parsers import PyMuPDFParser, RouterParser
from fish_engine.pipeline.rerankers import CohereReranker
from fish_engine.pipeline.retrievers import (
    HybridRetriever,
    LexicalRetriever,
    VectorRetriever,
)
from fish_engine.pipeline.stores import PostgresStore

SWORDFISH_RAG_SYSTEM_PROMPT = (
    "You are a retrieval QA assistant for SwordFish AI. "
    "Answer the user's question using ONLY the provided source blocks. "
    "You may use logical reasoning, but do not make up facts. "
    "Whenever you use information from a source block, cite it inline using [Source X] "
    "(where X is the Source number shown in the block header). "
    "If the provided sources do not contain enough evidence to answer the question, "
    "state clearly that no relevant information was found in the workspace."
)

SWORDFISH_EMPTY_CONTEXT_RESPONSE = (
    "No relevant information found in the workspace. "
    "Please upload and process a document in Sources first."
)

_pipeline_cache: Dict[str, Pipeline] = {}


def get_rag_pipeline(pipeline_config: Optional[dict] = None) -> Pipeline:
    """
    Constructs (and caches by normalized config JSON) a `fish-engine` `Pipeline`
    matching the workspace's `pipeline_config`.
    """
    cfg = WorkspacePipelineConfig(**(pipeline_config or {})).model_dump()
    cache_key = json.dumps(cfg, sort_keys=True)
    if cache_key in _pipeline_cache:
        return _pipeline_cache[cache_key]

    # 1. Parser
    pdf_parser = PyMuPDFParser(use_ocr=False)
    parser = RouterParser(
        fast_pdf_parser=pdf_parser,
        deep_pdf_parser=pdf_parser,
    )

    # 2. Chunker
    chunker_type = cfg.get("chunker", "semantic")
    chunk_size = int(cfg.get("chunk_size", 2048))
    if chunker_type == "recursive":
        chunker = RecursiveChunker(chunk_size=chunk_size)
    elif chunker_type == "sentence":
        chunker = SentenceChunker(chunk_size=chunk_size, chunk_overlap=min(128, chunk_size // 4))
    elif chunker_type == "token":
        chunker = TokenChunker(chunk_size=chunk_size, chunk_overlap=min(128, chunk_size // 4))
    else:
        chunker = SemanticChunker(
            embedding_model="minishlab/potion-base-8M",
            threshold=0.5,
            chunk_size=chunk_size,
            min_sentences_per_chunk=1,
        )

    # 3. Embedder
    embedder_provider = cfg.get("embedder_provider", "bedrock")
    embedder_model = cfg.get("embedder_model", "amazon.titan-embed-text-v2:0")
    if embedder_provider == "openai":
        if not embedder_model or "titan" in embedder_model:
            embedder_model = "text-embedding-3-small"
        embedder = OpenAIEmbedder(
            model_name=embedder_model,
            api_key=settings.OPENAI_API_KEY,
        )
    else:
        if not embedder_model or "text-embedding" in embedder_model:
            embedder_model = "amazon.titan-embed-text-v2:0"
        embedder = BedrockEmbedder(
            model_name=embedder_model,
            region_name=settings.BEDROCK_REGION,
            api_key=settings.BEDROCK_API_KEY,
        )

    # 4. PostgresStore (dimension-scoped vector table so workspaces with 1024d vs 1536d never collide)
    store = PostgresStore(
        engine=engine,
        dimension=embedder.dimension,
        vector_table_name=f"fish_vectors_{embedder.dimension}",
    )

    # 5. Retriever
    vec_ret = VectorRetriever(
        embedder=embedder,
        vector_index=store,
        chunk_store=store,
    )
    lex_ret = LexicalRetriever(chunk_store=store)
    retriever_strategy = cfg.get("retriever_strategy", "hybrid")
    if retriever_strategy == "vector":
        retriever = vec_ret
    elif retriever_strategy == "lexical":
        retriever = lex_ret
    else:
        retriever = HybridRetriever(
            retrievers=[vec_ret, lex_ret],
        )

    # 6. Generator
    gen_provider = cfg.get("generator_provider", "bedrock")
    gen_model = cfg.get("generator_model", "us.meta.llama3-3-70b-instruct-v1:0")
    temperature = float(cfg.get("temperature", 0.0))
    if gen_provider == "openai":
        if not gen_model or "llama" in gen_model or "claude" in gen_model or "amazon" in gen_model:
            gen_model = "gpt-4o-mini"
        generator = OpenAIGenerator(
            model_name=gen_model,
            api_key=settings.OPENAI_API_KEY,
            system_prompt=SWORDFISH_RAG_SYSTEM_PROMPT,
            temperature=temperature,
        )
    else:
        if not gen_model or gen_model.startswith("gpt-"):
            gen_model = "us.meta.llama3-3-70b-instruct-v1:0"
        generator = BedrockGenerator(
            model_name=gen_model,
            region_name=settings.BEDROCK_REGION,
            api_key=settings.BEDROCK_API_KEY,
            system_prompt=SWORDFISH_RAG_SYSTEM_PROMPT,
            temperature=temperature,
        )

    # 7. Assemble Pipeline via PipelineBuilder
    min_score = float(cfg.get("min_rerank_score", 0.0))

    def _filter_low_relevance(chunks: List[ChunkDataScored]) -> List[ChunkDataScored]:
        return [
            c for c in chunks if (c.rerank_score is None or c.rerank_score > min_score)
        ]

    builder = (
        PipelineBuilder()
        .with_parser(parser)
        .with_chunker(chunker)
        .with_embedder(embedder)
        .with_store(store)
        .with_retriever(retriever)
        .with_window_size(int(cfg.get("window_size", 1)))
        .add_post_retrieve_transform(_filter_low_relevance)
        .with_empty_context_response(SWORDFISH_EMPTY_CONTEXT_RESPONSE)
        .with_generator(generator)
    )

    if cfg.get("reranker_enabled", True) and settings.COHERE_API_KEY:
        builder.with_reranker(
            CohereReranker(
                model_name="rerank-v3.5",
                api_key=settings.COHERE_API_KEY,
            )
        )

    if cfg.get("conversational_memory", True):
        builder.with_query_rewriter(ConversationalQueryRewriter(generator=generator))

    if cfg.get("semantic_cache", True):
        builder.with_semantic_cache(
            SqlAlchemySemanticCache(session_factory=SessionLocal)
        )

    if cfg.get("guardrails_enabled", False):
        builder.with_input_guardrail(InputGuardrail())
        builder.with_output_guardrail(OutputGuardrail(enforce_citations=False))

    pipeline = builder.build()
    _pipeline_cache[cache_key] = pipeline
    return pipeline
