import React from 'react';
import {
  Sparkles,
  List,
  Folder,
  MessageSquare,
  LogOut,
  Plus,
} from 'lucide-react';
import { ActivePage, Workspace, Conversation, User } from '../../types';
import swordfishIcon from '../../assets/swordfishIcon.png';

interface SidebarProps {
  activePage: ActivePage;
  onSelectPage: (page: ActivePage) => void;
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  onSelectWorkspace: (ws: Workspace) => void;
  onOpenCreateWorkspace: () => void;
  conversations: Conversation[];
  activeConversation: Conversation | null;
  onSelectConversation: (conv: Conversation) => void;
  onCreateConversation: () => void;
  onOpenApiKeyModal: () => void;
  user: User;
  onLogout: () => void;
}

function formatWorkspaceDate(iso: string): string {
  try {
    const d = new Date(iso);
    return `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear()}`;
  } catch {
    return '9/7/2025';
  }
}

function formatShortDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } catch {
    return 'Sep 7';
  }
}

export const Sidebar: React.FC<SidebarProps> = ({
  activePage,
  onSelectPage,
  workspaces,
  activeWorkspace,
  onSelectWorkspace,
  onOpenCreateWorkspace,
  conversations,
  activeConversation,
  onSelectConversation,
  onCreateConversation,
  onOpenApiKeyModal,
  user,
  onLogout,
}) => {
  return (
    <aside className="w-[235px] shrink-0 bg-white dark:bg-slate-900 rounded-2xl m-2.5 mr-0 px-3.5 py-4 flex flex-col justify-between shadow-soft border border-slate-100 dark:border-slate-800 select-none">
      {/* Top & Middle Scrollable Content */}
      <div className="flex flex-col min-h-0 flex-1 overflow-hidden">
        {/* Brand Header */}
        <div
          onClick={() => onSelectPage('chat')}
          className="flex flex-col items-center pt-1 pb-4 cursor-pointer group"
        >
          <img
            src={swordfishIcon}
            alt="SwordFish AI"
            className="w-11 h-11 object-contain mb-1.5 transition-transform group-hover:scale-105"
          />
          <h1 className="text-[20px] font-extrabold text-[#111C44] dark:text-white tracking-tight">
            SwordFish AI
          </h1>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-1 mb-3 px-1">
          <button
            type="button"
            onClick={() => onSelectPage('chat')}
            className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-[12.5px] font-medium transition-colors cursor-pointer ${
              activePage === 'chat'
                ? 'text-[#111C44] dark:text-white font-semibold'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Sparkles className="w-4 h-4 text-[#3762F0]" />
            <span>Chat UI</span>
          </button>

          <button
            type="button"
            onClick={() => onSelectPage('sources')}
            className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-[12.5px] font-medium transition-colors cursor-pointer ${
              activePage === 'sources'
                ? 'text-[#111C44] dark:text-white font-semibold'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <List className="w-4 h-4 text-[#3762F0]" />
            <span>Sources</span>
          </button>
        </nav>

        {/* Sources Quick Card */}
        <div className="rounded-xl border border-slate-100 dark:border-slate-800 bg-[#FBFCFE] dark:bg-slate-800/40 p-3 mb-3.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <List className="w-3.5 h-3.5 text-slate-700 dark:text-slate-200" />
              <span className="text-[12px] font-semibold text-slate-800 dark:text-slate-100">
                Sources
              </span>
            </div>
            <button
              type="button"
              onClick={() => onSelectPage('sources')}
              className="inline-flex items-center gap-0.5 bg-[#3762F0] hover:bg-blue-600 text-white text-[11px] font-medium px-2.5 py-0.5 rounded-full shadow-xs transition-colors cursor-pointer"
            >
              <Plus className="w-3 h-3" />
              <span>Add</span>
            </button>
          </div>
          <p className="text-[11px] text-slate-400 dark:text-slate-400 mt-1.5 leading-snug">
            Manage your document sources
          </p>
        </div>

        {/* Workspaces Header */}
        <div className="rounded-xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-800/40 px-3 py-2 flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-1.5">
            <Folder className="w-3.5 h-3.5 text-slate-700 dark:text-slate-200" />
            <span className="text-[12px] font-semibold text-slate-800 dark:text-slate-100">
              Workspaces
            </span>
          </div>
          <button
            type="button"
            onClick={onOpenCreateWorkspace}
            className="inline-flex items-center gap-0.5 bg-[#3762F0] hover:bg-blue-600 text-white text-[11px] font-medium px-2.5 py-0.5 rounded-full shadow-xs transition-colors cursor-pointer"
          >
            <Plus className="w-3 h-3" />
            <span>New</span>
          </button>
        </div>

        {/* Workspaces List */}
        <div className="rounded-xl border border-slate-100 dark:border-slate-800 divide-y divide-slate-100 dark:divide-slate-800 overflow-y-auto max-h-[195px] mb-3.5 shrink-0">
          {workspaces.map((ws) => {
            const isSelected = activeWorkspace?.id === ws.id;
            return (
              <button
                key={ws.id}
                type="button"
                onClick={() => onSelectWorkspace(ws)}
                className={`w-full text-left px-3 py-2 transition-colors cursor-pointer block ${
                  isSelected
                    ? 'bg-[#EBF2FF] dark:bg-blue-950/60 border-l-[3px] border-l-[#3762F0]'
                    : 'bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                }`}
              >
                <div className="text-[12px] font-medium text-slate-800 dark:text-slate-100 truncate">
                  {ws.name}
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">
                  Created: {formatWorkspaceDate(ws.created_at)}
                </div>
              </button>
            );
          })}
        </div>

        {/* Conversations Section */}
        <div className="flex flex-col min-h-0 flex-1 border-t border-slate-100 dark:border-slate-800 pt-3">
          <div className="flex items-center justify-between px-1 mb-2">
            <span className="text-[11px] font-medium text-slate-400">
              Conversations
            </span>
            <button
              type="button"
              onClick={onCreateConversation}
              className="inline-flex items-center gap-0.5 text-[11px] font-semibold text-[#2563EB] hover:text-blue-700 cursor-pointer"
            >
              <Plus className="w-3 h-3" />
              <span>New</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto pr-0.5 space-y-1">
            {conversations.length === 0 ? (
              <p className="text-[11px] text-slate-400 px-1 py-1 leading-relaxed">
                No conversations yet. Create a new one to get started.
              </p>
            ) : (
              conversations.map((conv) => {
                const isSelected = activeConversation?.id === conv.id && activePage === 'chat';
                return (
                  <button
                    key={conv.id}
                    type="button"
                    onClick={() => {
                      onSelectConversation(conv);
                      onSelectPage('chat');
                    }}
                    className={`w-full text-left px-2.5 py-2 rounded-lg flex items-start gap-2 transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-[#EBF2FF] dark:bg-blue-950/60 border border-blue-200/80 dark:border-blue-800 text-[#2563EB]'
                        : 'hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    <MessageSquare
                      className={`w-3.5 h-3.5 mt-0.5 shrink-0 ${
                        isSelected ? 'text-[#2563EB]' : 'text-slate-400'
                      }`}
                    />
                    <div className="min-w-0 flex-1">
                      <div
                        className={`text-[11.5px] truncate ${
                          isSelected
                            ? 'font-semibold text-[#2563EB] dark:text-blue-400'
                            : 'font-medium text-slate-700 dark:text-slate-200'
                        }`}
                      >
                        {conv.title}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {formatShortDate(conv.created_at)}
                      </div>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Bottom Sticky Actions */}
      <div className="pt-3 mt-2 border-t border-slate-100 dark:border-slate-800">
        <button
          type="button"
          onClick={onOpenApiKeyModal}
          className="w-full py-2 rounded-full bg-[#111C44] hover:bg-[#1B2B65] text-white text-[11.5px] font-semibold shadow-xs transition-colors cursor-pointer mb-2.5"
        >
          Set API Key
        </button>

        <div className="flex items-center justify-between px-1.5 py-1 rounded-full bg-slate-50/80 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-6 h-6 rounded-full bg-[#111C44] text-white text-[11px] font-semibold flex items-center justify-center shrink-0">
              {user.email.charAt(0).toUpperCase()}
            </div>
            <span className="text-[11px] font-medium text-slate-700 dark:text-slate-300 truncate">
              {user.email}
            </span>
          </div>
          <button
            type="button"
            onClick={onLogout}
            title="Sign Out"
            className="p-1 text-slate-400 hover:text-slate-700 dark:hover:text-white transition-colors shrink-0 cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
};
