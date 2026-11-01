import React, { useState, useEffect, useCallback } from 'react';
import {
  User,
  Workspace,
  WorkspacePipelineConfig,
  Conversation,
  Source,
  ChatTurn,
  ActivePage,
} from './types';
import {
  apiClient,
  decodeJwtEmail,
  registerUnauthorizedHandler,
  setDemoMode,
} from './api/client';
import { Sidebar } from './components/layout/Sidebar';
import { TopNavbar } from './components/layout/TopNavbar';
import { ChatView } from './components/chat/ChatView';
import { SourcesView } from './components/sources/SourcesView';
import { AuthView } from './components/auth/AuthView';
import { CreateWorkspaceModal } from './components/modals/CreateWorkspaceModal';
import { ApiKeyModal } from './components/modals/ApiKeyModal';

export function App() {
  const [user, setUser] = useState<User | null>(() => {
    // 1. Check if redirected back from Google OAuth with ?token=...
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    if (urlToken) {
      const email = decodeJwtEmail(urlToken) || 'ahmed1999fattah@gmail.com';
      const oauthUser: User = {
        id: 3,
        email,
        created_at: new Date().toISOString(),
      };
      localStorage.setItem('sf_token', urlToken);
      localStorage.setItem('sf_user', JSON.stringify(oauthUser));
      setDemoMode(false);
      window.history.replaceState({}, document.title, window.location.pathname);
      return oauthUser;
    }

    const savedUser = localStorage.getItem('sf_user');
    const savedToken = localStorage.getItem('sf_token');
    if (savedUser && savedToken && savedToken !== 'mock-jwt-token-swordfish-ai') {
      try {
        return JSON.parse(savedUser);
      } catch {
        return null;
      }
    }
    return null;
  });

  const [darkMode, setDarkMode] = useState<boolean>(() => {
    return localStorage.getItem('sf_dark_mode') === 'true';
  });

  const [activePage, setActivePage] = useState<ActivePage>('chat');
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspace, setActiveWorkspace] = useState<Workspace | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [sources, setSources] = useState<Source[]>([]);

  const [isSubmittingChat, setIsSubmittingChat] = useState(false);
  const [isUploadingSource, setIsUploadingSource] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const [createWsModalOpen, setCreateWsModalOpen] = useState(false);
  const [apiKeyModalOpen, setApiKeyModalOpen] = useState(false);

  // Register 401 handler and ensure Live Backend mode
  useEffect(() => {
    setDemoMode(false);
    registerUnauthorizedHandler(() => {
      setUser(null);
    });
  }, []);

  // Sync dark mode class on <html>
  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('sf_dark_mode', String(darkMode));
  }, [darkMode]);

  const loadWorkspaces = useCallback(async () => {
    if (!user) return;
    try {
      const list = await apiClient.listWorkspaces();
      setWorkspaces(list);
      setActiveWorkspace((prev) => {
        if (prev && list.some((w) => w.id === prev.id)) {
          return list.find((w) => w.id === prev.id) || list[0] || null;
        }
        // Prefer "Test Workspace" (id=12) on initial load so user sees the Alchemist data immediately
        return (
          list.find((w) => w.name === 'Test Workspace') ||
          list[0] ||
          null
        );
      });
    } catch (err) {
      console.error('Failed to load workspaces:', err);
    }
  }, [user]);

  useEffect(() => {
    loadWorkspaces();
  }, [loadWorkspaces]);

  const loadWorkspaceDetails = useCallback(async (ws: Workspace | null) => {
    if (!ws) {
      setConversations([]);
      setActiveConversation(null);
      setSources([]);
      setTurns([]);
      return;
    }

    try {
      const [convList, srcList] = await Promise.all([
        apiClient.listConversations(ws.id),
        apiClient.listSources(ws.id),
      ]);

      setConversations(convList);
      setSources(srcList);

      // Prefer conversation 31 or 203 ("Santiago's Discovery of His Personal Legend") if present
      const preferredConv =
        convList.find((c) => c.id === 31 || c.id === 203) ||
        convList[0] ||
        null;
      setActiveConversation(preferredConv);
    } catch (err) {
      console.error('Failed to load workspace details:', err);
    }
  }, []);

  useEffect(() => {
    loadWorkspaceDetails(activeWorkspace);
  }, [activeWorkspace, loadWorkspaceDetails]);

  useEffect(() => {
    const fetchTurns = async () => {
      if (!activeWorkspace || !activeConversation) {
        setTurns([]);
        return;
      }
      try {
        const chatTurns = await apiClient.listChatTurns(
          activeWorkspace.id,
          activeConversation.id
        );
        setTurns(chatTurns);
      } catch (err) {
        console.error('Failed to load conversation turns:', err);
      }
    };
    fetchTurns();
  }, [activeWorkspace, activeConversation]);

  // Poll sources every 3s if any source in activeWorkspace is currently uploading/processing in Celery
  useEffect(() => {
    if (!activeWorkspace) return;
    const hasPending = sources.some((s) => {
      const st = (s.status || '').toLowerCase();
      return st === 'uploaded' || st === 'processing';
    });
    if (!hasPending) return;

    const timer = setInterval(async () => {
      try {
        const refreshed = await apiClient.listSources(activeWorkspace.id);
        setSources(refreshed);
      } catch {
        // Ignore polling errors
      }
    }, 3000);

    return () => clearInterval(timer);
  }, [activeWorkspace, sources]);

  const handleCreateWorkspace = async (
    name: string,
    pipelineConfig: WorkspacePipelineConfig
  ) => {
    const created = await apiClient.createWorkspace(name, pipelineConfig);
    setWorkspaces((prev) => [created, ...prev]);
    setActiveWorkspace(created);
  };

  const handleCreateConversation = async () => {
    if (!activeWorkspace) return;
    const created = await apiClient.createConversation(activeWorkspace.id);
    setConversations((prev) => [created, ...prev]);
    setActiveConversation(created);
    setTurns([]);
    setActivePage('chat');
  };

  const handleSendMessage = async (text: string) => {
    if (!activeWorkspace) return;
    setIsSubmittingChat(true);

    try {
      let targetConv = activeConversation;
      if (!targetConv) {
        targetConv = await apiClient.createConversation(activeWorkspace.id);
        setConversations((prev) => [targetConv!, ...prev]);
        setActiveConversation(targetConv);
      }

      const { turn, updatedTitle } = await apiClient.submitQuery(
        activeWorkspace.id,
        targetConv.id,
        text
      );

      setTurns((prev) => [...prev, turn]);

      if (updatedTitle) {
        setConversations((prev) =>
          prev.map((c) => (c.id === targetConv!.id ? { ...c, title: updatedTitle } : c))
        );
        setActiveConversation((prev) =>
          prev && prev.id === targetConv!.id ? { ...prev, title: updatedTitle } : prev
        );
      }
    } finally {
      setIsSubmittingChat(false);
    }
  };

  const handleUploadFile = async (file: File) => {
    if (!activeWorkspace) return;
    setIsUploadingSource(true);
    try {
      const uploaded = await apiClient.uploadSourceFile(activeWorkspace.id, file);
      setSources((prev) => [uploaded, ...prev]);
    } finally {
      setIsUploadingSource(false);
    }
  };

  const handleAddUrl = async (url: string) => {
    if (!activeWorkspace) return;
    setIsUploadingSource(true);
    try {
      const created = await apiClient.createUrlSource(activeWorkspace.id, url);
      setSources((prev) => [created, ...prev]);
    } finally {
      setIsUploadingSource(false);
    }
  };

  const handleDeleteSource = async (sourceId: number) => {
    if (!activeWorkspace) return;
    await apiClient.deleteSource(activeWorkspace.id, sourceId);
    setSources((prev) => prev.filter((s) => s.id !== sourceId));
  };

  const handleDownloadSource = async (sourceId: number, filename: string) => {
    if (!activeWorkspace) return;
    await apiClient.downloadSource(activeWorkspace.id, sourceId, filename);
  };

  const handleLogout = () => {
    localStorage.removeItem('sf_token');
    localStorage.removeItem('sf_user');
    setUser(null);
  };

  if (!user) {
    return (
      <AuthView
        onLoginSuccess={(loggedInUser) => {
          setUser(loggedInUser);
        }}
      />
    );
  }

  const filteredWorkspaces = searchQuery.trim()
    ? workspaces.filter((w) =>
        w.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : workspaces;

  const filteredConversations = searchQuery.trim()
    ? conversations.filter((c) =>
        c.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : conversations;

  return (
    <div className="h-screen w-screen overflow-hidden flex bg-[#F4F7FE] dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      {/* Left Sidebar */}
      <Sidebar
        activePage={activePage}
        onSelectPage={setActivePage}
        workspaces={filteredWorkspaces}
        activeWorkspace={activeWorkspace}
        onSelectWorkspace={(ws) => {
          setActiveWorkspace(ws);
        }}
        onOpenCreateWorkspace={() => setCreateWsModalOpen(true)}
        conversations={filteredConversations}
        activeConversation={activeConversation}
        onSelectConversation={(conv) => setActiveConversation(conv)}
        onCreateConversation={handleCreateConversation}
        onOpenApiKeyModal={() => setApiKeyModalOpen(true)}
        user={user}
        onLogout={handleLogout}
      />

      {/* Right Main Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        <TopNavbar
          activePage={activePage}
          workspaces={workspaces}
          activeWorkspace={activeWorkspace}
          onSelectWorkspace={(ws) => setActiveWorkspace(ws)}
          onOpenCreateWorkspace={() => setCreateWsModalOpen(true)}
          user={user}
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode(!darkMode)}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onOpenApiKeyModal={() => setApiKeyModalOpen(true)}
          onLogout={handleLogout}
        />

        {activePage === 'chat' ? (
          <ChatView
            activeWorkspace={activeWorkspace}
            turns={turns}
            isSubmitting={isSubmittingChat}
            onSendMessage={handleSendMessage}
            onNewChat={handleCreateConversation}
          />
        ) : (
          <SourcesView
            activeWorkspace={activeWorkspace}
            sources={sources}
            isUploading={isUploadingSource}
            onUploadFile={handleUploadFile}
            onAddUrl={handleAddUrl}
            onRefresh={async () => {
              if (activeWorkspace) {
                const refreshed = await apiClient.listSources(activeWorkspace.id);
                setSources(refreshed);
              }
            }}
            onDeleteSource={handleDeleteSource}
            onDownloadSource={handleDownloadSource}
            onNavigateToChat={() => setActivePage('chat')}
          />
        )}
      </div>

      {/* Modals */}
      <CreateWorkspaceModal
        isOpen={createWsModalOpen}
        onClose={() => setCreateWsModalOpen(false)}
        onCreate={handleCreateWorkspace}
      />

      <ApiKeyModal
        isOpen={apiKeyModalOpen}
        onClose={() => setApiKeyModalOpen(false)}
        onConfigChanged={() => {
          loadWorkspaces();
          if (activeWorkspace) {
            loadWorkspaceDetails(activeWorkspace);
          }
        }}
      />
    </div>
  );
}

export default App;
