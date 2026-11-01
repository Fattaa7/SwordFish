import React, { useState, useEffect, useRef } from 'react';
import { X, ChevronDown, ChevronUp, Cpu, Sparkles, Zap, Layers } from 'lucide-react';
import {
  WorkspacePipelineConfig,
  DEFAULT_PIPELINE_CONFIG,
  PipelinePresetId,
} from '../../types';

interface CreateWorkspaceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (name: string, pipelineConfig: WorkspacePipelineConfig) => Promise<void>;
}

const PRESETS: Record<
  Exclude<PipelinePresetId, 'custom'>,
  {
    title: string;
    subtitle: string;
    badge: string;
    config: WorkspacePipelineConfig;
  }
> = {
  bedrock_enterprise: {
    title: 'AWS Bedrock Enterprise',
    subtitle: 'Semantic Chunker • Titan v2 (1024d) • Hybrid + Cohere Rerank 3.5 • Llama 3.3 70B',
    badge: 'Recommended',
    config: {
      ...DEFAULT_PIPELINE_CONFIG,
      preset: 'bedrock_enterprise',
      chunker: 'semantic',
      chunk_size: 2048,
      embedder_provider: 'bedrock',
      embedder_model: 'amazon.titan-embed-text-v2:0',
      retriever_strategy: 'hybrid',
      top_k: 20,
      reranker_enabled: true,
      rerank_top_k: 10,
      window_size: 1,
      generator_provider: 'bedrock',
      generator_model: 'us.meta.llama3-3-70b-instruct-v1:0',
      conversational_memory: true,
      semantic_cache: true,
      guardrails_enabled: false,
    },
  },
  balanced: {
    title: 'Balanced Hybrid RAG (OpenAI)',
    subtitle: 'Semantic Chunker • text-embedding-3-small (1536d) • Hybrid + Rerank • GPT-4o-mini',
    badge: 'OpenAI',
    config: {
      ...DEFAULT_PIPELINE_CONFIG,
      preset: 'balanced',
      chunker: 'semantic',
      chunk_size: 2048,
      embedder_provider: 'openai',
      embedder_model: 'text-embedding-3-small',
      retriever_strategy: 'hybrid',
      top_k: 20,
      reranker_enabled: true,
      rerank_top_k: 10,
      window_size: 1,
      generator_provider: 'openai',
      generator_model: 'gpt-4o-mini',
      conversational_memory: true,
      semantic_cache: true,
      guardrails_enabled: false,
    },
  },
  deep: {
    title: 'High-Precision Deep RAG',
    subtitle: 'Semantic Chunker • Hybrid RRF (top_k=30) • Window ±2 • Guardrails Enabled',
    badge: 'Deep Context',
    config: {
      ...DEFAULT_PIPELINE_CONFIG,
      preset: 'deep',
      chunker: 'semantic',
      chunk_size: 2048,
      embedder_provider: 'bedrock',
      embedder_model: 'amazon.titan-embed-text-v2:0',
      retriever_strategy: 'hybrid',
      top_k: 30,
      reranker_enabled: true,
      rerank_top_k: 12,
      window_size: 2,
      generator_provider: 'bedrock',
      generator_model: 'us.meta.llama3-3-70b-instruct-v1:0',
      conversational_memory: true,
      semantic_cache: true,
      guardrails_enabled: true,
    },
  },
  fast: {
    title: 'Fast & Lightweight',
    subtitle: 'Recursive Chunker • Vector Search (top_k=8) • No Reranker • Low Latency',
    badge: 'Fastest',
    config: {
      ...DEFAULT_PIPELINE_CONFIG,
      preset: 'fast',
      chunker: 'recursive',
      chunk_size: 1024,
      embedder_provider: 'bedrock',
      embedder_model: 'amazon.titan-embed-text-v2:0',
      retriever_strategy: 'vector',
      top_k: 8,
      reranker_enabled: false,
      rerank_top_k: 8,
      window_size: 0,
      generator_provider: 'bedrock',
      generator_model: 'us.meta.llama3-3-70b-instruct-v1:0',
      conversational_memory: true,
      semantic_cache: true,
      guardrails_enabled: false,
    },
  },
};

export const CreateWorkspaceModal: React.FC<CreateWorkspaceModalProps> = ({
  isOpen,
  onClose,
  onCreate,
}) => {
  const [name, setName] = useState('');
  const [config, setConfig] = useState<WorkspacePipelineConfig>(
    PRESETS.bedrock_enterprise.config
  );
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setName('');
      setConfig(PRESETS.bedrock_enterprise.config);
      setShowAdvanced(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const selectPreset = (presetKey: Exclude<PipelinePresetId, 'custom'>) => {
    setConfig({ ...PRESETS[presetKey].config });
  };

  const updateField = <K extends keyof WorkspacePipelineConfig>(
    key: K,
    value: WorkspacePipelineConfig[K]
  ) => {
    setConfig((prev) => ({
      ...prev,
      preset: 'custom',
      [key]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;
    setSubmitting(true);
    try {
      await onCreate(trimmed, config);
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-10 pb-8 overflow-y-auto bg-slate-900/45 backdrop-blur-[1.5px] animate-fadeIn">
      <div className="w-full max-w-[540px] bg-white dark:bg-slate-900 rounded-2xl shadow-modal border border-slate-100 dark:border-slate-800 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-[#3762F0] flex items-center justify-center">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-[15.5px] font-bold text-slate-900 dark:text-white leading-tight">
                Create New Workspace
              </h3>
              <p className="text-[11px] text-slate-400">
                Powered by <span className="font-semibold text-[#3762F0]">fish-engine</span> RAG Pipeline Builder
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors p-1 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Workspace Name */}
          <div>
            <label className="block text-[12px] font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Workspace Name
            </label>
            <input
              ref={inputRef}
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Engineering Docs, Legal Contracts, Q4 Research..."
              className="w-full rounded-xl border-[1.5px] border-[#3762F0] bg-white dark:bg-slate-800 px-3.5 py-2 text-[13px] text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            />
          </div>

          {/* Pipeline Presets */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-[12px] font-semibold text-slate-700 dark:text-slate-300">
                RAG Pipeline Preset (Set at Workspace Creation)
              </label>
              <span className="text-[10.5px] text-slate-400">
                Consistent across all workspace documents
              </span>
            </div>

            <div className="grid grid-cols-1 gap-2">
              {(Object.keys(PRESETS) as Array<Exclude<PipelinePresetId, 'custom'>>).map(
                (key) => {
                  const p = PRESETS[key];
                  const isSelected = config.preset === key;
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => selectPreset(key)}
                      className={`w-full text-left rounded-xl p-3 border transition-all cursor-pointer ${
                        isSelected
                          ? 'border-[#3762F0] bg-blue-50/50 dark:bg-blue-950/30 shadow-2xs'
                          : 'border-slate-200/80 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/40 dark:bg-slate-800/40'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[12.5px] font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
                          {key === 'bedrock_enterprise' && (
                            <Sparkles className="w-3.5 h-3.5 text-[#3762F0]" />
                          )}
                          {key === 'fast' && <Zap className="w-3.5 h-3.5 text-amber-500" />}
                          {(key === 'balanced' || key === 'deep') && (
                            <Layers className="w-3.5 h-3.5 text-indigo-500" />
                          )}
                          {p.title}
                        </span>
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                            isSelected
                              ? 'bg-[#3762F0] text-white'
                              : 'bg-slate-200/70 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                          }`}
                        >
                          {p.badge}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        {p.subtitle}
                      </p>
                    </button>
                  );
                }
              )}
            </div>
          </div>

          {/* Advanced Customize Accordion */}
          <div className="border border-slate-200/80 dark:border-slate-800 rounded-xl overflow-hidden">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800/60 flex items-center justify-between text-[12px] font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-100/80 dark:hover:bg-slate-800 transition-colors cursor-pointer"
            >
              <span>
                Advanced Customize Pipeline
                {config.preset === 'custom' && (
                  <span className="ml-2 text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
                    Custom
                  </span>
                )}
              </span>
              {showAdvanced ? (
                <ChevronUp className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              )}
            </button>

            {showAdvanced && (
              <div className="p-3.5 space-y-3 bg-white dark:bg-slate-900 text-[12px]">
                <div className="grid grid-cols-2 gap-3">
                  {/* Chunker */}
                  <div>
                    <label className="block text-[11px] font-medium text-slate-500 mb-1">
                      Chunker Strategy
                    </label>
                    <select
                      value={config.chunker}
                      onChange={(e) =>
                        updateField(
                          'chunker',
                          e.target.value as WorkspacePipelineConfig['chunker']
                        )
                      }
                      className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2.5 py-1.5 text-[12px]"
                    >
                      <option value="semantic">SemanticChunker (Chonkie)</option>
                      <option value="recursive">RecursiveChunker</option>
                      <option value="sentence">SentenceChunker</option>
                      <option value="token">TokenChunker</option>
                    </select>
                  </div>

                  {/* Retriever */}
                  <div>
                    <label className="block text-[11px] font-medium text-slate-500 mb-1">
                      Retriever Strategy
                    </label>
                    <select
                      value={config.retriever_strategy}
                      onChange={(e) =>
                        updateField(
                          'retriever_strategy',
                          e.target.value as WorkspacePipelineConfig['retriever_strategy']
                        )
                      }
                      className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2.5 py-1.5 text-[12px]"
                    >
                      <option value="hybrid">Hybrid (Vector + BM25 RRF)</option>
                      <option value="vector">Vector Only (pgvector HNSW)</option>
                      <option value="lexical">Lexical Only (Postgres FTS)</option>
                    </select>
                  </div>

                  {/* Embedder Provider */}
                  <div>
                    <label className="block text-[11px] font-medium text-slate-500 mb-1">
                      Embedding Provider
                    </label>
                    <select
                      value={config.embedder_provider}
                      onChange={(e) => {
                        const prov = e.target.value as 'bedrock' | 'openai';
                        setConfig((prev) => ({
                          ...prev,
                          preset: 'custom',
                          embedder_provider: prov,
                          embedder_model:
                            prov === 'bedrock'
                              ? 'amazon.titan-embed-text-v2:0'
                              : 'text-embedding-3-small',
                        }));
                      }}
                      className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2.5 py-1.5 text-[12px]"
                    >
                      <option value="bedrock">AWS Bedrock Titan v2 (1024d)</option>
                      <option value="openai">OpenAI text-embedding-3 (1536d)</option>
                    </select>
                  </div>

                  {/* Generator Provider & Model */}
                  <div>
                    <label className="block text-[11px] font-medium text-slate-500 mb-1">
                      LLM Generator
                    </label>
                    <select
                      value={`${config.generator_provider}:${config.generator_model}`}
                      onChange={(e) => {
                        const [prov, mod] = e.target.value.split(':');
                        setConfig((prev) => ({
                          ...prev,
                          preset: 'custom',
                          generator_provider: prov as 'bedrock' | 'openai',
                          generator_model: mod,
                        }));
                      }}
                      className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2.5 py-1.5 text-[12px]"
                    >
                      <option value="bedrock:us.meta.llama3-3-70b-instruct-v1:0">
                        Bedrock • Llama 3.3 70B Instruct
                      </option>
                      <option value="openai:gpt-4o-mini">OpenAI • GPT-4o-mini</option>
                      <option value="openai:gpt-4o">OpenAI • GPT-4o</option>
                    </select>
                  </div>

                  {/* Top-K & Window Size */}
                  <div>
                    <label className="block text-[11px] font-medium text-slate-500 mb-1">
                      Retrieve Top-K / Rerank Top-K
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min={1}
                        max={50}
                        value={config.top_k}
                        onChange={(e) => updateField('top_k', Number(e.target.value) || 20)}
                        className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2.5 py-1 text-[12px]"
                      />
                      <span className="text-slate-400">→</span>
                      <input
                        type="number"
                        min={1}
                        max={30}
                        value={config.rerank_top_k}
                        onChange={(e) =>
                          updateField('rerank_top_k', Number(e.target.value) || 10)
                        }
                        className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2.5 py-1 text-[12px]"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-500 mb-1">
                      Context Window Hydration (±chunks)
                    </label>
                    <select
                      value={config.window_size}
                      onChange={(e) => updateField('window_size', Number(e.target.value))}
                      className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2.5 py-1.5 text-[12px]"
                    >
                      <option value={0}>0 (Matched chunk only)</option>
                      <option value={1}>±1 Adjacent chunks</option>
                      <option value={2}>±2 Adjacent chunks</option>
                    </select>
                  </div>
                </div>

                {/* Feature Toggles */}
                <div className="pt-2 border-t border-slate-100 dark:border-slate-800 grid grid-cols-2 gap-2 text-[11.5px]">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.reranker_enabled}
                      onChange={(e) => updateField('reranker_enabled', e.target.checked)}
                      className="rounded text-[#3762F0]"
                    />
                    <span>Cohere Rerank 3.5</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.conversational_memory}
                      onChange={(e) =>
                        updateField('conversational_memory', e.target.checked)
                      }
                      className="rounded text-[#3762F0]"
                    />
                    <span>Conversational Memory Rewrite</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.semantic_cache}
                      onChange={(e) => updateField('semantic_cache', e.target.checked)}
                      className="rounded text-[#3762F0]"
                    />
                    <span>PostgreSQL Semantic Cache</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.guardrails_enabled}
                      onChange={(e) => updateField('guardrails_enabled', e.target.checked)}
                      className="rounded text-[#3762F0]"
                    />
                    <span>PII & Injection Guardrails</span>
                  </label>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 text-[12px] font-medium text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || !name.trim()}
              className="px-5 py-2 rounded-full bg-[#3762F0] hover:bg-blue-600 text-white text-[12.5px] font-semibold shadow-sm transition-all disabled:opacity-50 cursor-pointer"
            >
              {submitting ? 'Creating Workspace...' : 'Create Workspace'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
