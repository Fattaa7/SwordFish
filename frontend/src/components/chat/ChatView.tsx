import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  FileText,
  Activity,
  ChevronDown,
  ChevronUp,
  Sparkles,
  ExternalLink,
  Zap,
} from 'lucide-react';
import { Workspace, ChatTurn, Citation } from '../../types';
import { apiClient } from '../../api/client';

interface ChatViewProps {
  activeWorkspace: Workspace | null;
  turns: ChatTurn[];
  isSubmitting: boolean;
  onSendMessage: (text: string) => Promise<void>;
  onNewChat: () => void;
}

function formatMessageTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  } catch {
    return '12:04 PM';
  }
}

function getCitationTitle(cit: Citation): string {
  return (
    cit.metadata?.title ||
    cit.title ||
    String(cit.document_id || 'Document').replace(/^doc_\d+_/, '')
  );
}

function getCitationIndex(cit: Citation, fallbackIdx: number): number {
  if (typeof cit.source_index === 'number') return cit.source_index;
  if (typeof cit.chunk_id === 'number') return cit.chunk_id;
  return fallbackIdx + 1;
}

function getCitationSnippet(cit: Citation): string | undefined {
  return cit.snippet || cit.excerpt || undefined;
}

function getCitationSourceId(cit: Citation): number | undefined {
  const sid = cit.metadata?.source_id;
  return typeof sid === 'number' ? sid : undefined;
}

export const ChatView: React.FC<ChatViewProps> = ({
  activeWorkspace,
  turns,
  isSubmitting,
  onSendMessage,
  onNewChat,
}) => {
  const [inputText, setInputText] = useState('');
  const [selectedCitationKey, setSelectedCitationKey] = useState<string | null>(null);
  const [openTraceTurnId, setOpenTraceTurnId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [turns, isSubmitting]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = inputText.trim();
    if (!trimmed || isSubmitting) return;
    setInputText('');
    await onSendMessage(trimmed);
  };

  /**
   * Renders assistant text with interactive `[Source X]` or `[X]` inline citation badges
   * that highlight/toggle the corresponding Citation Card when clicked.
   */
  const renderFormattedAnswer = (
    text: string,
    turnId: string,
    citations: Citation[]
  ): React.ReactNode => {
    const parts = text.split(/(\[Source\s+\d+\]|\[\d+\])/gi);
    return parts.map((part, idx) => {
      const match = part.match(/^\[(?:Source\s+)?(\d+)\]$/i);
      if (match) {
        const num = parseInt(match[1], 10);
        const matchedCit =
          citations.find((c, i) => getCitationIndex(c, i) === num) || citations[0];
        const citKey = matchedCit
          ? `${turnId}-cit-${getCitationIndex(matchedCit, 0)}`
          : `${turnId}-cit-${num}`;
        const title = matchedCit ? getCitationTitle(matchedCit) : `Source ${num}`;
        const page = matchedCit?.page_number ? ` • p.${matchedCit.page_number}` : '';

        return (
          <button
            key={idx}
            type="button"
            onClick={() =>
              setSelectedCitationKey((prev) => (prev === citKey ? null : citKey))
            }
            title={`${title}${page}`}
            className="inline-flex items-center gap-1 mx-0.5 px-1.5 py-0.5 rounded-md bg-blue-100/90 hover:bg-blue-200 dark:bg-blue-900/60 dark:hover:bg-blue-800 text-[#1D4ED8] dark:text-blue-200 text-[11px] font-semibold transition-colors cursor-pointer align-baseline"
          >
            <span>Source {num}</span>
          </button>
        );
      }
      return <React.Fragment key={idx}>{part}</React.Fragment>;
    });
  };

  const wsCfg = activeWorkspace?.pipeline_config;

  return (
    <div className="flex-1 flex flex-col min-h-0 px-6 pb-4">
      <div className="max-w-[920px] w-full mx-auto flex-1 flex flex-col min-h-0 bg-white dark:bg-slate-900 rounded-2xl shadow-card border border-slate-100 dark:border-slate-800 overflow-hidden">
        {/* Top Chat Header */}
        <div className="px-5 py-3.5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div>
              <h3 className="text-[13.5px] font-semibold text-slate-900 dark:text-white leading-tight">
                RAG Chat
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                {activeWorkspace?.name || 'Workspace'}
              </p>
            </div>

            {wsCfg && (
              <div className="hidden sm:flex items-center gap-1.5 pl-2 border-l border-slate-200 dark:border-slate-800">
                <span className="px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/60 text-[#3762F0] dark:text-blue-300 text-[10px] font-semibold">
                  {wsCfg.retriever_strategy === 'hybrid'
                    ? 'Hybrid RRF'
                    : wsCfg.retriever_strategy === 'lexical'
                    ? 'Lexical BM25'
                    : 'Vector HNSW'}
                </span>
                {wsCfg.reranker_enabled !== false && (
                  <span className="px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 text-[10px] font-semibold">
                    Cohere Rerank 3.5
                  </span>
                )}
                <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 text-[10px] font-medium">
                  {wsCfg.generator_model?.includes('llama')
                    ? 'Llama 3.3 70B'
                    : wsCfg.generator_model || 'Bedrock'}
                </span>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={onNewChat}
            className="inline-flex items-center gap-1.5 bg-[#3762F0] hover:bg-blue-600 text-white text-[11.5px] font-medium px-3.5 py-1.5 rounded-full shadow-xs transition-all cursor-pointer"
          >
            <Send className="w-3 h-3" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Message List / Empty State */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
          {turns.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center py-16">
              <p className="text-[15px] font-medium text-slate-500 dark:text-slate-400">
                Start chatting with your data
              </p>
              <p className="text-[12px] text-slate-400 dark:text-slate-500 mt-1.5 max-w-md">
                Ask questions about your documents and get AI-powered answers with inline source citations and telemetry traces powered by{' '}
                <span className="font-semibold text-[#3762F0]">fish-engine</span>.
              </p>
            </div>
          ) : (
            turns.map((turn) => {
              const citations = turn.answer?.sources || [];
              const meta = turn.answer?.meta;
              const trace = meta?.trace;
              const isTraceOpen = openTraceTurnId === turn.id;
              const totalMs =
                meta?.latency_ms ?? trace?.total_latency_ms ?? null;

              return (
                <div key={turn.id} className="space-y-4">
                  {/* User Message Bubble (Right-aligned) */}
                  <div className="flex justify-end">
                    <div className="bg-[#3762F0] text-white rounded-xl px-4 py-3 max-w-[75%] shadow-xs">
                      <p className="text-[13px] leading-relaxed">{turn.query.query_text}</p>
                      <div className="text-[10px] text-blue-100/90 mt-1.5 text-right">
                        {formatMessageTime(turn.query.created_at)}
                      </div>
                    </div>
                  </div>

                  {/* Assistant Answer Card (Left-aligned) */}
                  {turn.answer && (
                    <div className="flex justify-start">
                      <div className="bg-[#F9FAFC] dark:bg-slate-800/70 border border-slate-100/90 dark:border-slate-800 rounded-xl px-5 py-4 max-w-[88%] text-slate-800 dark:text-slate-100">
                        {/* Rewritten Query Indicator (when ConversationalQueryRewriter resolved follow-up context) */}
                        {meta?.rewritten_query &&
                          meta.rewritten_query.trim().toLowerCase() !==
                            turn.query.query_text.trim().toLowerCase() && (
                            <div className="mb-2.5 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-50/80 dark:bg-indigo-950/50 border border-indigo-100 dark:border-indigo-900 text-[11px] text-indigo-700 dark:text-indigo-300">
                              <Sparkles className="w-3 h-3 shrink-0" />
                              <span>
                                Searched as:{' '}
                                <strong className="font-semibold">
                                  "{meta.rewritten_query}"
                                </strong>
                              </span>
                            </div>
                          )}

                        {/* Main Answer Body with interactive [Source X] pills */}
                        <div className="text-[13px] leading-[1.7] text-slate-800 dark:text-slate-200 whitespace-pre-line">
                          {renderFormattedAnswer(turn.answer.text, turn.id, citations)}
                        </div>

                        {/* Interactive Source Citation Cards */}
                        {citations.length > 0 && (
                          <div className="mt-4 pt-3 border-t border-slate-200/60 dark:border-slate-700/60">
                            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-400 mb-2 flex items-center gap-1.5">
                              <FileText className="w-3.5 h-3.5 text-[#3762F0]" />
                              <span>Verified Citations ({citations.length})</span>
                            </div>

                            <div className="flex flex-wrap gap-2">
                              {citations.map((cit, idx) => {
                                const srcIdx = getCitationIndex(cit, idx);
                                const citKey = `${turn.id}-cit-${srcIdx}`;
                                const isSelected = selectedCitationKey === citKey;
                                const title = getCitationTitle(cit);

                                return (
                                  <button
                                    key={`${cit.chunk_id}-${idx}`}
                                    type="button"
                                    onClick={() =>
                                      setSelectedCitationKey(isSelected ? null : citKey)
                                    }
                                    className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-left transition-all cursor-pointer ${
                                      isSelected
                                        ? 'bg-[#3762F0] text-white border-[#3762F0] shadow-xs'
                                        : 'bg-white dark:bg-slate-900 hover:bg-blue-50/60 dark:hover:bg-slate-800 border-slate-200/80 dark:border-slate-700 text-slate-700 dark:text-slate-200'
                                    }`}
                                  >
                                    <span
                                      className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                                        isSelected
                                          ? 'bg-white/20 text-white'
                                          : 'bg-blue-100 dark:bg-blue-900/60 text-[#1D4ED8] dark:text-blue-200'
                                      }`}
                                    >
                                      #{srcIdx}
                                    </span>
                                    <span className="text-[11.5px] font-semibold truncate max-w-[180px]">
                                      {title}
                                    </span>
                                    {cit.page_number && (
                                      <span
                                        className={`text-[10.5px] ${
                                          isSelected
                                            ? 'text-blue-100'
                                            : 'text-slate-400 dark:text-slate-400'
                                        }`}
                                      >
                                        p.{cit.page_number}
                                      </span>
                                    )}
                                    {typeof cit.score === 'number' && (
                                      <span
                                        className={`text-[10px] font-mono px-1 rounded ${
                                          isSelected
                                            ? 'bg-white/15 text-white'
                                            : 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300'
                                        }`}
                                      >
                                        {(cit.score * 100).toFixed(0)}%
                                      </span>
                                    )}
                                  </button>
                                );
                              })}
                            </div>

                            {/* Expanded Citation Snippet Drawer */}
                            {citations.map((cit, idx) => {
                              const srcIdx = getCitationIndex(cit, idx);
                              const citKey = `${turn.id}-cit-${srcIdx}`;
                              if (selectedCitationKey !== citKey) return null;

                              const title = getCitationTitle(cit);
                              const snippet = getCitationSnippet(cit);
                              const sourceId = getCitationSourceId(cit);

                              return (
                                <div
                                  key={`drawer-${citKey}`}
                                  className="mt-2.5 p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-blue-200/80 dark:border-blue-800/70 shadow-2xs text-[12px] text-slate-700 dark:text-slate-300 animate-fadeIn"
                                >
                                  <div className="flex items-center justify-between gap-2 pb-2 mb-2 border-b border-slate-100 dark:border-slate-800">
                                    <div className="flex items-center gap-2">
                                      <span className="px-2 py-0.5 rounded-md bg-blue-100 dark:bg-blue-900/60 text-[#1D4ED8] dark:text-blue-200 text-[10.5px] font-bold">
                                        Source {srcIdx}
                                      </span>
                                      <span className="font-semibold text-slate-900 dark:text-white">
                                        {title}
                                      </span>
                                      {cit.page_number && (
                                        <span className="text-[11px] text-slate-500">
                                          • Page {cit.page_number}
                                        </span>
                                      )}
                                      {typeof cit.score === 'number' && (
                                        <span className="text-[10.5px] font-mono text-emerald-600 dark:text-emerald-400">
                                          • Score: {cit.score.toFixed(3)}
                                        </span>
                                      )}
                                    </div>

                                    <div className="flex items-center gap-2">
                                      {activeWorkspace && sourceId && (
                                        <button
                                          type="button"
                                          onClick={() =>
                                            apiClient.downloadSource(
                                              activeWorkspace.id,
                                              sourceId,
                                              `${title}.pdf`
                                            )
                                          }
                                          className="inline-flex items-center gap-1 text-[11px] font-medium text-[#3762F0] hover:underline cursor-pointer"
                                        >
                                          <ExternalLink className="w-3 h-3" />
                                          <span>Download Source</span>
                                        </button>
                                      )}
                                      <button
                                        type="button"
                                        onClick={() => setSelectedCitationKey(null)}
                                        className="text-[11px] text-slate-400 hover:text-slate-600 cursor-pointer"
                                      >
                                        Close
                                      </button>
                                    </div>
                                  </div>

                                  {snippet ? (
                                    <p className="text-[12px] leading-relaxed text-slate-600 dark:text-slate-300 italic bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-lg border border-slate-100 dark:border-slate-800">
                                      "{snippet}"
                                    </p>
                                  ) : (
                                    <p className="text-[11.5px] text-slate-400 italic">
                                      Chunk ID: {String(cit.chunk_id)}
                                    </p>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        )}

                        {/* Footer: Timestamp + Collapsible fish-engine Pipeline Trace Pill */}
                        <div className="mt-3 pt-2 flex flex-wrap items-center justify-between gap-2 text-[10.5px] text-slate-400">
                          <span>{formatMessageTime(turn.answer.created_at)}</span>

                          {(totalMs !== null || meta?.model_id || meta?.cached) && (
                            <button
                              type="button"
                              onClick={() =>
                                setOpenTraceTurnId(isTraceOpen ? null : turn.id)
                              }
                              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200/80 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 font-medium transition-colors cursor-pointer"
                            >
                              <Activity className="w-3 h-3 text-[#3762F0]" />
                              {meta?.cached && (
                                <span className="inline-flex items-center gap-0.5 text-amber-600 dark:text-amber-400 font-semibold">
                                  <Zap className="w-2.5 h-2.5" /> Cache Hit •
                                </span>
                              )}
                              {totalMs !== null && (
                                <span>{(totalMs / 1000).toFixed(2)}s</span>
                              )}
                              {meta?.model_id && (
                                <span className="hidden sm:inline text-slate-400">
                                  •{' '}
                                  {meta.model_id.includes('llama')
                                    ? 'Llama 3.3 70B'
                                    : meta.model_id}
                                </span>
                              )}
                              {(meta?.input_tokens_count || meta?.output_tokens_count) && (
                                <span className="hidden md:inline text-slate-400">
                                  •{' '}
                                  {(meta.input_tokens_count || 0) +
                                    (meta.output_tokens_count || 0)}{' '}
                                  tok
                                </span>
                              )}
                              {trace?.spans && trace.spans.length > 0 && (
                                <>
                                  {isTraceOpen ? (
                                    <ChevronUp className="w-3 h-3" />
                                  ) : (
                                    <ChevronDown className="w-3 h-3" />
                                  )}
                                </>
                              )}
                            </button>
                          )}
                        </div>

                        {/* Expanded StageProfiler Telemetry Breakdown */}
                        {isTraceOpen && trace?.spans && trace.spans.length > 0 && (
                          <div className="mt-2.5 p-3 rounded-xl bg-slate-900 text-slate-200 text-[11px] font-mono space-y-1.5 animate-fadeIn">
                            <div className="flex items-center justify-between text-[10px] uppercase tracking-wider text-slate-400 pb-1 border-b border-slate-800">
                              <span>fish-engine StageProfiler Trace</span>
                              <span>Total: {trace.total_latency_ms.toFixed(0)} ms</span>
                            </div>
                            {trace.spans.map((sp) => (
                              <div
                                key={sp.span_id}
                                className="flex items-center justify-between gap-2 py-0.5"
                              >
                                <div className="flex items-center gap-2 truncate">
                                  <span className="text-blue-400 font-semibold">
                                    {sp.stage_name}
                                  </span>
                                  <span className="text-slate-400">({sp.class_name})</span>
                                </div>
                                <span className="text-emerald-400 shrink-0">
                                  {sp.latency_ms.toFixed(1)} ms
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}

          {isSubmitting && (
            <div className="flex justify-start">
              <div className="bg-[#F9FAFC] dark:bg-slate-800/70 border border-slate-100 dark:border-slate-800 rounded-xl px-5 py-3.5 text-[12.5px] text-slate-500 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-[#3762F0] animate-ping" />
                <span>
                  Running fish-engine pipeline (Retrieve → Rerank → Generate with Citations)...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Bottom Input Bar */}
        <form
          onSubmit={handleSubmit}
          className="px-4 py-3 border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center gap-3 shrink-0"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask a question about your workspace documents..."
            disabled={isSubmitting}
            className="flex-1 bg-[#F8FAFC] dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700 rounded-full px-4 py-2.5 text-[13px] text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-blue-400 transition-colors"
          />

          <button
            type="submit"
            disabled={!inputText.trim() || isSubmitting}
            className={`inline-flex items-center gap-1.5 px-4 py-2.5 rounded-full text-white text-[12.5px] font-medium transition-all cursor-pointer ${
              inputText.trim() && !isSubmitting
                ? 'bg-[#3762F0] hover:bg-blue-600 shadow-xs'
                : 'bg-[#9DB5FA] dark:bg-blue-800/50 cursor-not-allowed'
            }`}
          >
            <Send className="w-3.5 h-3.5" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
};
