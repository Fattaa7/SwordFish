import React, { useState, useRef } from 'react';
import {
  Paperclip,
  Link2,
  Plus,
  FileText,
  ChevronDown,
  Trash2,
  MessageSquare,
  Globe,
  Download,
} from 'lucide-react';
import { Workspace, Source } from '../../types';

interface SourcesViewProps {
  activeWorkspace: Workspace | null;
  sources: Source[];
  isUploading: boolean;
  onUploadFile: (file: File) => Promise<void>;
  onAddUrl: (url: string) => Promise<void>;
  onRefresh: () => Promise<void>;
  onDeleteSource: (sourceId: number) => Promise<void>;
  onDownloadSource: (sourceId: number, filename: string) => Promise<void>;
  onNavigateToChat: () => void;
}

function getSourceDisplayName(source: Source): string {
  if (source.type === 'url' && source.url) {
    return source.url;
  }
  if (source.storage_path) {
    const parts = source.storage_path.split(/[/\\]/);
    return parts[parts.length - 1] || 'Document.pdf';
  }
  return `Source_${source.id}.pdf`;
}

function formatRelativeTime(iso: string): string {
  try {
    const diffMs = Date.now() - new Date(iso).getTime();
    const diffHours = Math.round(diffMs / (1000 * 3600));
    if (diffHours <= 0) return 'Added just now';
    if (diffHours === 1) return 'Added 1 hour ago';
    if (diffHours < 24) return `Added ${diffHours} hours ago`;
    const diffDays = Math.round(diffHours / 24);
    return `Added ${diffDays} day${diffDays === 1 ? '' : 's'} ago`;
  } catch {
    return 'Added 3 hours ago';
  }
}

export const SourcesView: React.FC<SourcesViewProps> = ({
  activeWorkspace,
  sources,
  isUploading,
  onUploadFile,
  onAddUrl,
  onRefresh,
  onDeleteSource,
  onDownloadSource,
  onNavigateToChat,
}) => {
  const [activeTab, setActiveTab] = useState<'file' | 'url'>('file');
  const [urlInput, setUrlInput] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [openActionId, setOpenActionId] = useState<number | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const wsName = activeWorkspace?.name || 'Test Workspace';

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setErrorMsg(null);
      try {
        await onUploadFile(file);
      } catch (err: unknown) {
        setErrorMsg(err instanceof Error ? err.message : 'File upload failed');
      }
      e.target.value = '';
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setErrorMsg(null);
      try {
        await onUploadFile(file);
      } catch (err: unknown) {
        setErrorMsg(err instanceof Error ? err.message : 'File upload failed');
      }
    }
  };

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = urlInput.trim();
    if (!trimmed) return;
    setErrorMsg(null);
    try {
      await onAddUrl(trimmed);
      setUrlInput('');
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'URL ingestion failed');
    }
  };

  return (
    <div className="flex-1 overflow-y-auto px-6 pb-8 pt-2">
      <div className="max-w-[760px] w-full mx-auto bg-white dark:bg-slate-900 rounded-2xl shadow-card border border-slate-100 dark:border-slate-800 p-6 space-y-5">
        {/* Top Card: Add Sources */}
        <div className="rounded-xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-[0_2px_12px_rgba(15,23,42,0.03)] p-5">
          <h3 className="text-[14px] font-semibold text-slate-900 dark:text-white mb-3.5">
            Add Sources to {wsName}
          </h3>

          {errorMsg && (
            <div className="mb-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 px-3 py-2 text-xs text-red-600 dark:text-red-300">
              {errorMsg}
            </div>
          )}

          {/* Tabs */}
          <div className="border-b border-slate-100 dark:border-slate-800 flex items-center gap-5 mb-4">
            <button
              type="button"
              onClick={() => setActiveTab('file')}
              className={`inline-flex items-center gap-1.5 pb-2.5 text-[12px] font-medium transition-colors border-b-2 -mb-px cursor-pointer ${
                activeTab === 'file'
                  ? 'border-[#3762F0] text-[#3762F0]'
                  : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              <Paperclip className="w-3.5 h-3.5" />
              <span>Upload File</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('url')}
              className={`inline-flex items-center gap-1.5 pb-2.5 text-[12px] font-medium transition-colors border-b-2 -mb-px cursor-pointer ${
                activeTab === 'url'
                  ? 'border-[#3762F0] text-[#3762F0]'
                  : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              <Link2 className="w-3.5 h-3.5" />
              <span>Add URL</span>
            </button>
          </div>

          {activeTab === 'file' ? (
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border border-dashed rounded-xl py-9 px-4 flex flex-col items-center justify-center text-center cursor-pointer transition-all ${
                isDragging
                  ? 'border-[#3762F0] bg-blue-50/40 dark:bg-blue-950/30'
                  : 'border-slate-200 dark:border-slate-700 bg-[#F8FAFC] dark:bg-slate-800/40 hover:border-blue-400'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.md,.doc,.docx"
                onChange={handleFileChange}
                className="hidden"
              />
              <Plus className="w-7 h-7 text-slate-400 mb-2 stroke-[1.75]" />
              <p className="text-[12.5px] font-medium text-slate-800 dark:text-slate-200">
                {isUploading
                  ? 'Uploading & dispatching Celery processing task...'
                  : 'Drag & drop a file here, or click to select'}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                Supports PDF, TXT, MD, DOC, DOCX (max 50MB)
              </p>
            </div>
          ) : (
            <form onSubmit={handleUrlSubmit} className="flex items-center gap-2.5 py-3">
              <input
                type="url"
                required
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://example.com/documentation-or-article"
                className="flex-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-[#F8FAFC] dark:bg-slate-800 px-3.5 py-2.5 text-[12.5px] text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-blue-500"
              />
              <button
                type="submit"
                disabled={isUploading || !urlInput.trim()}
                className="px-4 py-2.5 rounded-lg bg-[#3762F0] hover:bg-blue-600 text-white text-[12px] font-medium shadow-xs transition-all disabled:opacity-50 cursor-pointer"
              >
                {isUploading ? 'Adding...' : 'Add URL'}
              </button>
            </form>
          )}
        </div>

        {/* Bottom Card: Sources in Workspace */}
        <div className="rounded-xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-[0_2px_12px_rgba(15,23,42,0.03)] p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-[14px] font-semibold text-slate-900 dark:text-white">
              Sources in {wsName}
            </h3>

            <button
              type="button"
              onClick={onRefresh}
              className="px-3 py-1 rounded-lg bg-[#F8FAFC] hover:bg-slate-100 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-[11px] font-semibold border border-slate-100 dark:border-slate-700 transition-colors cursor-pointer"
            >
              Refresh
            </button>
          </div>

          {sources.length === 0 ? (
            <div className="py-6 text-center">
              <p className="text-[12.5px] text-slate-500 dark:text-slate-400">
                No sources found in this workspace.
              </p>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-1">
                Upload files or add URLs to get started.
              </p>
            </div>
          ) : (
            <div>
              <div className="space-y-2.5">
                {sources.map((src) => {
                  const displayName = getSourceDisplayName(src);
                  const statusLower = (src.status || '').toLowerCase();
                  const isReady = statusLower === 'processed';
                  const isProcessing =
                    statusLower === 'processing' || statusLower === 'uploaded';

                  return (
                    <div
                      key={src.id}
                      className="rounded-xl bg-[#F8FAFC] dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 px-4 py-3.5 flex items-center justify-between relative"
                    >
                      <div className="min-w-0 pr-4">
                        <div className="flex items-center gap-2 flex-wrap">
                          {src.type === 'url' ? (
                            <Globe className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          ) : (
                            <FileText className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          )}
                          <span className="text-[13px] font-medium text-slate-900 dark:text-white truncate">
                            {displayName}
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-[9.5px] font-bold uppercase tracking-wide ${
                              isReady
                                ? 'bg-[#DCFCE7] text-[#15803D] dark:bg-emerald-950/70 dark:text-emerald-300'
                                : isProcessing
                                ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 animate-pulse'
                                : 'bg-red-100 text-red-700'
                            }`}
                          >
                            {isReady
                              ? 'READY'
                              : isProcessing
                              ? 'PROCESSING'
                              : statusLower.toUpperCase()}
                          </span>
                        </div>

                        <div className="text-[11px] text-slate-400 mt-1">
                          {src.type === 'url' ? 'URL' : 'File'} • {formatRelativeTime(src.created_at)}
                        </div>
                      </div>

                      {/* Actions Dropdown */}
                      <div className="relative">
                        <button
                          type="button"
                          onClick={() =>
                            setOpenActionId(openActionId === src.id ? null : src.id)
                          }
                          className="inline-flex items-center gap-1 text-[11.5px] font-semibold text-slate-700 dark:text-slate-200 hover:text-blue-600 px-2 py-1 rounded-md cursor-pointer"
                        >
                          <span>Actions</span>
                          <ChevronDown className="w-3 h-3" />
                        </button>

                        {openActionId === src.id && (
                          <div className="absolute right-0 mt-1 w-44 bg-white dark:bg-slate-900 rounded-xl shadow-modal border border-slate-100 dark:border-slate-800 py-1 z-30">
                            <button
                              type="button"
                              onClick={() => {
                                setOpenActionId(null);
                                onNavigateToChat();
                              }}
                              className="w-full text-left px-3 py-1.5 text-[11.5px] text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-2 cursor-pointer"
                            >
                              <MessageSquare className="w-3.5 h-3.5 text-[#3762F0]" />
                              <span>Query in Chat</span>
                            </button>
                            {src.type === 'file' && (
                              <button
                                type="button"
                                onClick={async () => {
                                  setOpenActionId(null);
                                  await onDownloadSource(src.id, displayName);
                                }}
                                className="w-full text-left px-3 py-1.5 text-[11.5px] text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-2 cursor-pointer"
                              >
                                <Download className="w-3.5 h-3.5 text-slate-500" />
                                <span>Download File</span>
                              </button>
                            )}
                            <button
                              type="button"
                              onClick={async () => {
                                setOpenActionId(null);
                                await onDeleteSource(src.id);
                              }}
                              className="w-full text-left px-3 py-1.5 text-[11.5px] text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 flex items-center gap-2 cursor-pointer"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                              <span>Delete Source</span>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="text-[11px] text-slate-400 text-center mt-4">
                {sources.length} source{sources.length === 1 ? '' : 's'} total
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
