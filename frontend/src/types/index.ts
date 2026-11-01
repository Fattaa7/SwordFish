export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export type PipelinePresetId = 'bedrock_enterprise' | 'balanced' | 'deep' | 'fast' | 'custom';

export interface WorkspacePipelineConfig {
  preset: PipelinePresetId;
  chunker: 'semantic' | 'recursive' | 'sentence' | 'token';
  chunk_size: number;
  embedder_provider: 'bedrock' | 'openai';
  embedder_model: string;
  retriever_strategy: 'hybrid' | 'vector' | 'lexical';
  top_k: number;
  reranker_enabled: boolean;
  rerank_top_k: number;
  min_rerank_score: number;
  window_size: number;
  generator_provider: 'bedrock' | 'openai';
  generator_model: string;
  temperature: number;
  conversational_memory: boolean;
  semantic_cache: boolean;
  guardrails_enabled: boolean;
}

export const DEFAULT_PIPELINE_CONFIG: WorkspacePipelineConfig = {
  preset: 'bedrock_enterprise',
  chunker: 'semantic',
  chunk_size: 2048,
  embedder_provider: 'bedrock',
  embedder_model: 'amazon.titan-embed-text-v2:0',
  retriever_strategy: 'hybrid',
  top_k: 20,
  reranker_enabled: true,
  rerank_top_k: 10,
  min_rerank_score: 0.0,
  window_size: 1,
  generator_provider: 'bedrock',
  generator_model: 'us.meta.llama3-3-70b-instruct-v1:0',
  temperature: 0.0,
  conversational_memory: true,
  semantic_cache: true,
  guardrails_enabled: false,
};

export interface Workspace {
  id: number;
  name: string;
  owner_id: number;
  pipeline_config?: Partial<WorkspacePipelineConfig> | null;
  created_at: string;
}

export interface WorkspaceCreate {
  name: string;
  pipeline_config?: WorkspacePipelineConfig;
}

export type SourceStatus = 'uploaded' | 'processing' | 'processed' | 'failed';
export type SourceType = 'file' | 'url';

export interface Source {
  id: number;
  workspace_id: number;
  type: SourceType;
  status: SourceStatus;
  url?: string | null;
  storage_path?: string | null;
  mime_type?: string | null;
  checksum?: string | null;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  is_private: boolean;
  created_at: string;
}

export interface Citation {
  source_index?: number;
  chunk_id: string | number;
  document_id: string | number;
  page_number?: number | null;
  storage_uri?: string | null;
  score?: number | null;
  snippet?: string | null;
  metadata?: {
    title?: string;
    swordfish_document_id?: number;
    source_id?: number;
    source_uri?: string;
    workspace_id?: string;
    [key: string]: unknown;
  };
  // Legacy fields for older DB rows
  title?: string;
  source_uri?: string | null;
  excerpt?: string;
}

export interface StageSpan {
  span_id: string;
  parent_span_id?: string | null;
  stage_name: string;
  class_name: string;
  latency_ms: number;
  input_tokens?: number | null;
  output_tokens?: number | null;
  error?: string | null;
  metadata?: Record<string, unknown>;
}

export interface PipelineTrace {
  trace_id: string;
  operation: string;
  total_latency_ms: number;
  spans: StageSpan[];
  metadata?: Record<string, unknown>;
}

export interface AnswerMeta {
  model_id?: string | null;
  latency_ms?: number | null;
  input_tokens_count?: number | null;
  output_tokens_count?: number | null;
  rewritten_query?: string | null;
  cached?: boolean;
  trace?: PipelineTrace | null;
}

export interface QueryItem {
  id: number;
  query_text: string;
  created_at: string;
}

export interface AnswerItem {
  id: number;
  query_id?: number;
  conversation_id?: number;
  text: string;
  sources: Citation[];
  meta?: AnswerMeta | null;
  created_at: string;
}

export interface ChatTurn {
  id: string;
  query: QueryItem;
  answer?: AnswerItem;
  isStreaming?: boolean;
}

export type ActivePage = 'chat' | 'sources';
