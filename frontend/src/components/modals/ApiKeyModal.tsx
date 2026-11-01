import React, { useState, useEffect } from 'react';
import { X, Key, RotateCcw, Server } from 'lucide-react';
import { isDemoMode, setDemoMode, mockStore } from '../../api/client';

interface ApiKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfigChanged: () => void;
}

export const ApiKeyModal: React.FC<ApiKeyModalProps> = ({
  isOpen,
  onClose,
  onConfigChanged,
}) => {
  const [openAiKey, setOpenAiKey] = useState('');
  const [cohereKey, setCohereKey] = useState('');
  const [demo, setDemo] = useState(true);
  const [savedNotice, setSavedNotice] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setOpenAiKey(localStorage.getItem('sf_openai_key') || '');
      setCohereKey(localStorage.getItem('sf_cohere_key') || '');
      setDemo(isDemoMode());
      setSavedNotice(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('sf_openai_key', openAiKey.trim());
    localStorage.setItem('sf_cohere_key', cohereKey.trim());
    setDemoMode(demo);
    setSavedNotice(true);
    onConfigChanged();
    setTimeout(() => {
      onClose();
    }, 400);
  };

  const handleResetMock = () => {
    mockStore.reset();
    onConfigChanged();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-[1px]">
      <div className="w-full max-w-[420px] bg-white dark:bg-slate-900 rounded-xl shadow-modal border border-slate-100 dark:border-slate-800 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-[#3762F0]" />
            <h3 className="text-[15px] font-semibold text-slate-900 dark:text-white">
              API Key & Engine Configuration
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors p-1 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-[12px] font-medium text-slate-700 dark:text-slate-300 mb-1">
              OpenAI API Key (Embeddings & Generation)
            </label>
            <input
              type="password"
              value={openAiKey}
              onChange={(e) => setOpenAiKey(e.target.value)}
              placeholder="sk-..."
              className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-[13px] text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            />
          </div>

          <div>
            <label className="block text-[12px] font-medium text-slate-700 dark:text-slate-300 mb-1">
              Cohere API Key (Rerank 3.5)
            </label>
            <input
              type="password"
              value={cohereKey}
              onChange={(e) => setCohereKey(e.target.value)}
              placeholder="cohere-..."
              className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-[13px] text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            />
          </div>

          <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Server className="w-4 h-4 text-slate-500" />
                <div>
                  <p className="text-[12px] font-medium text-slate-800 dark:text-slate-200">
                    Interactive Demo / Showcase Mode
                  </p>
                  <p className="text-[11px] text-slate-400">
                    Use built-in RAG fixtures when FastAPI Docker is offline
                  </p>
                </div>
              </div>
              <input
                type="checkbox"
                checked={demo}
                onChange={(e) => setDemo(e.target.checked)}
                className="h-4 w-4 accent-[#3762F0] rounded cursor-pointer"
              />
            </div>
          </div>

          {savedNotice && (
            <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
              Settings saved!
            </p>
          )}

          <div className="flex items-center justify-between pt-3">
            <button
              type="button"
              onClick={handleResetMock}
              className="inline-flex items-center gap-1.5 text-[11px] text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Demo Fixtures
            </button>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 text-[12px] font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-1.5 rounded-full bg-[#3762F0] hover:bg-blue-600 text-white text-[12px] font-medium shadow-sm transition-all cursor-pointer"
              >
                Save Key
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
