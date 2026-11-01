import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class WorkspacePipelineConfig(BaseModel):
    preset: Literal["bedrock_enterprise", "balanced", "deep", "fast", "custom"] = "bedrock_enterprise"
    chunker: Literal["semantic", "recursive", "sentence", "token"] = "semantic"
    chunk_size: int = 2048
    embedder_provider: Literal["bedrock", "openai"] = "bedrock"
    embedder_model: str = "amazon.titan-embed-text-v2:0"
    retriever_strategy: Literal["hybrid", "vector", "lexical"] = "hybrid"
    top_k: int = 20
    reranker_enabled: bool = True
    rerank_top_k: int = 10
    min_rerank_score: float = 0.0
    window_size: int = 1
    generator_provider: Literal["bedrock", "openai"] = "bedrock"
    generator_model: str = "us.meta.llama3-3-70b-instruct-v1:0"
    temperature: float = 0.0
    conversational_memory: bool = True
    semantic_cache: bool = True
    guardrails_enabled: bool = False


class WorkspaceCreate(BaseModel):
    name: str
    pipeline_config: WorkspacePipelineConfig = Field(
        default_factory=WorkspacePipelineConfig
    )


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    pipeline_config: Optional[dict] = None
    created_at: datetime.datetime

    model_config = {
        "from_attributes": True
    }
