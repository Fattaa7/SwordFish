import React, { useState, useRef, useEffect } from 'react';
import {
  Search,
  Moon,
  Sun,
  ChevronDown,
  LogOut,
  Plus,
  Key,
} from 'lucide-react';
import { Workspace, User, ActivePage } from '../../types';

interface TopNavbarProps {
  activePage: ActivePage;
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  onSelectWorkspace: (ws: Workspace) => void;
  onOpenCreateWorkspace: () => void;
  user: User;
  darkMode: boolean;
  onToggleDarkMode: () => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onOpenApiKeyModal: () => void;
  onLogout: () => void;
}

export const TopNavbar: React.FC<TopNavbarProps> = ({
  workspaces,
  activeWorkspace,
  onSelectWorkspace,
  onOpenCreateWorkspace,
  user,
  darkMode,
  onToggleDarkMode,
  searchQuery,
  onSearchChange,
  onOpenApiKeyModal,
  onLogout,
}) => {
  const [wsDropdownOpen, setWsDropdownOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  const wsRef = useRef<HTMLDivElement>(null);
  const userRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (wsRef.current && !wsRef.current.contains(e.target as Node)) {
        setWsDropdownOpen(false);
      }
      if (userRef.current && !userRef.current.contains(e.target as Node)) {
        setUserDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="w-full px-6 pt-4 pb-2 flex items-start justify-between shrink-0">
      {/* Breadcrumb & Page Heading */}
      <div>
        <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
          <span>Pages</span>
          <span>/</span>
          <span className="text-slate-700 dark:text-slate-300">Chat UI</span>
        </div>
        <h2 className="text-[24px] font-extrabold text-[#111C44] dark:text-white tracking-tight mt-0.5">
          Chat UI
        </h2>
      </div>

      {/* Right Floating Pill Toolbar */}
      <div className="bg-white dark:bg-slate-900 rounded-full px-3 py-1.5 shadow-[0_6px_24px_rgba(15,23,42,0.06)] border border-slate-100 dark:border-slate-800 flex items-center gap-3">
        {/* Search Input Pill */}
        <div className="bg-[#F4F7FE] dark:bg-slate-800 rounded-full px-3 py-1.5 flex items-center gap-2 w-44">
          <Search className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400 shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search"
            className="bg-transparent text-[12px] text-slate-700 dark:text-slate-200 placeholder:text-slate-400 focus:outline-none w-full"
          />
        </div>

        {/* Dark / Light Mode Toggle */}
        <button
          type="button"
          onClick={onToggleDarkMode}
          title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          className="p-1.5 text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-white transition-colors cursor-pointer"
        >
          {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-3.5 h-3.5 fill-slate-500" />}
        </button>

        {/* Workspace Dropdown Selector */}
        <div ref={wsRef} className="relative">
          <button
            type="button"
            onClick={() => setWsDropdownOpen(!wsDropdownOpen)}
            className="flex items-center gap-1.5 text-[12px] font-semibold text-slate-800 dark:text-slate-200 hover:text-blue-600 transition-colors px-1.5 py-1 cursor-pointer"
          >
            {/* Three-dot triangle icon matching the screenshot */}
            <svg
              className="w-3.5 h-3.5 text-slate-700 dark:text-slate-300"
              viewBox="0 0 16 16"
              fill="currentColor"
            >
              <circle cx="8" cy="4" r="1.8" />
              <circle cx="4.5" cy="11" r="1.8" />
              <circle cx="11.5" cy="11" r="1.8" />
            </svg>
            <span className="max-w-[120px] truncate">
              {activeWorkspace?.name || 'Select Workspace'}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
          </button>

          {wsDropdownOpen && (
            <div className="absolute right-0 mt-2 w-52 bg-white dark:bg-slate-900 rounded-xl shadow-modal border border-slate-100 dark:border-slate-800 py-1.5 z-40">
              <div className="px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Switch Workspace
              </div>
              <div className="max-h-56 overflow-y-auto">
                {workspaces.map((ws) => (
                  <button
                    key={ws.id}
                    type="button"
                    onClick={() => {
                      onSelectWorkspace(ws);
                      setWsDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-[12px] flex items-center justify-between transition-colors cursor-pointer ${
                      activeWorkspace?.id === ws.id
                        ? 'bg-blue-50/80 dark:bg-blue-950/50 text-[#2563EB] font-semibold'
                        : 'text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    <span className="truncate">{ws.name}</span>
                    {activeWorkspace?.id === ws.id && (
                      <span className="w-1.5 h-1.5 rounded-full bg-[#2563EB]" />
                    )}
                  </button>
                ))}
              </div>
              <div className="border-t border-slate-100 dark:border-slate-800 mt-1 pt-1 px-1.5">
                <button
                  type="button"
                  onClick={() => {
                    setWsDropdownOpen(false);
                    onOpenCreateWorkspace();
                  }}
                  className="w-full flex items-center gap-1.5 px-2 py-1.5 text-[12px] font-medium text-[#2563EB] hover:bg-blue-50 dark:hover:bg-blue-950/40 rounded-lg cursor-pointer"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Create New Workspace</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User Profile Pill Dropdown */}
        <div ref={userRef} className="relative">
          <button
            type="button"
            onClick={() => setUserDropdownOpen(!userDropdownOpen)}
            className="flex items-center gap-2 pl-1 pr-1.5 py-0.5 rounded-full hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <div className="w-7 h-7 rounded-full bg-[#2563EB] text-white text-[12px] font-semibold flex items-center justify-center shadow-xs">
              {user.email.charAt(0).toUpperCase()}
            </div>
            <span className="text-[12px] font-medium text-slate-700 dark:text-slate-200 hidden sm:inline">
              {user.email}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
          </button>

          {userDropdownOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-900 rounded-xl shadow-modal border border-slate-100 dark:border-slate-800 py-1.5 z-40">
              <div className="px-3.5 py-2 border-b border-slate-100 dark:border-slate-800">
                <p className="text-[11px] text-slate-400">Signed in as</p>
                <p className="text-[12px] font-semibold text-slate-800 dark:text-white truncate">
                  {user.email}
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  setUserDropdownOpen(false);
                  onOpenApiKeyModal();
                }}
                className="w-full text-left px-3.5 py-2 text-[12px] text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-2 cursor-pointer"
              >
                <Key className="w-3.5 h-3.5 text-slate-400" />
                <span>API Key & Engine Settings</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setUserDropdownOpen(false);
                  onLogout();
                }}
                className="w-full text-left px-3.5 py-2 text-[12px] text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 flex items-center gap-2 cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
