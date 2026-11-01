import {
  User,
  TokenResponse,
  Workspace,
  WorkspacePipelineConfig,
  DEFAULT_PIPELINE_CONFIG,
  Source,
  Conversation,
  QueryItem,
  AnswerItem,
  ChatTurn,
} from '../types';
import {
  MOCK_USER,
  INITIAL_MOCK_WORKSPACES,
  INITIAL_MOCK_SOURCES,
  INITIAL_MOCK_CONVERSATIONS,
  INITIAL_MOCK_CHAT_TURNS,
  generateMockAnswer,
} from './mockData';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class MockStore {
  workspaces: Workspace[];
  sources: Record<number, Source[]>;
  conversations: Record<number, Conversation[]>;
  chatTurns: Record<number, ChatTurn[]>;

  constructor() {
    const savedWs = localStorage.getItem('sf_mock_workspaces');
    const savedSrc = localStorage.getItem('sf_mock_sources');
    const savedConv = localStorage.getItem('sf_mock_conversations');
    const savedTurns = localStorage.getItem('sf_mock_turns');

    this.workspaces = savedWs ? JSON.parse(savedWs) : [...INITIAL_MOCK_WORKSPACES];
    this.sources = savedSrc ? JSON.parse(savedSrc) : JSON.parse(JSON.stringify(INITIAL_MOCK_SOURCES));
    this.conversations = savedConv
      ? JSON.parse(savedConv)
      : JSON.parse(JSON.stringify(INITIAL_MOCK_CONVERSATIONS));
    this.chatTurns = savedTurns
      ? JSON.parse(savedTurns)
      : JSON.parse(JSON.stringify(INITIAL_MOCK_CHAT_TURNS));
  }

  save() {
    localStorage.setItem('sf_mock_workspaces', JSON.stringify(this.workspaces));
    localStorage.setItem('sf_mock_sources', JSON.stringify(this.sources));
    localStorage.setItem('sf_mock_conversations', JSON.stringify(this.conversations));
    localStorage.setItem('sf_mock_turns', JSON.stringify(this.chatTurns));
  }

  reset() {
    localStorage.removeItem('sf_mock_workspaces');
    localStorage.removeItem('sf_mock_sources');
    localStorage.removeItem('sf_mock_conversations');
    localStorage.removeItem('sf_mock_turns');
    this.workspaces = [...INITIAL_MOCK_WORKSPACES];
    this.sources = JSON.parse(JSON.stringify(INITIAL_MOCK_SOURCES));
    this.conversations = JSON.parse(JSON.stringify(INITIAL_MOCK_CONVERSATIONS));
    this.chatTurns = JSON.parse(JSON.stringify(INITIAL_MOCK_CHAT_TURNS));
  }
}

export const mockStore = new MockStore();

export function isDemoMode(): boolean {
  const mode = localStorage.getItem('sf_demo_mode');
  // Default to FALSE so the app connects directly to the live FastAPI backend at localhost:8000
  return mode === 'true';
}

export function setDemoMode(enabled: boolean): void {
  localStorage.setItem('sf_demo_mode', String(enabled));
}

export function decodeJwtEmail(token: string): string | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
    return payload.sub || null;
  } catch {
    return null;
  }
}

function getAuthHeaders(extraHeaders: Record<string, string> = {}): HeadersInit {
  const token = localStorage.getItem('sf_token');
  const apiKey = localStorage.getItem('sf_openai_key');
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(apiKey ? { 'X-OpenAI-Key': apiKey } : {}),
    ...extraHeaders,
  };
}

let onUnauthorizedCallback: (() => void) | null = null;

export function registerUnauthorizedHandler(cb: () => void) {
  onUnauthorizedCallback = cb;
}

function checkUnauthorized(res: Response) {
  if (res.status === 401 && !isDemoMode()) {
    localStorage.removeItem('sf_token');
    localStorage.removeItem('sf_user');
    onUnauthorizedCallback?.();
    throw new Error('Session expired or unauthorized. Please sign in.');
  }
}

export const apiClient = {
  getBaseUrl: () => API_BASE_URL,

  async checkHealth(): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      return res.ok;
    } catch {
      return false;
    }
  },

  async login(email: string, password: string): Promise<{ token: TokenResponse; user: User }> {
    if (!isDemoMode()) {
      const body = new URLSearchParams();
      body.append('username', email);
      body.append('password', password);

      const res = await fetch(`${API_BASE_URL}/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Invalid email or password' }));
        throw new Error(err.detail || 'Invalid credentials');
      }

      const tokenData: TokenResponse = await res.json();
      const user: User = {
        id: 1,
        email,
        created_at: new Date().toISOString(),
      };
      return { token: tokenData, user };
    }

    // Demo Mode login
    await new Promise((r) => setTimeout(r, 300));
    const user: User = {
      ...MOCK_USER,
      email: email || MOCK_USER.email,
    };
    return {
      token: { access_token: 'mock-jwt-token-swordfish-ai', token_type: 'bearer' },
      user,
    };
  },

  async register(email: string, password: string): Promise<User> {
    if (!isDemoMode()) {
      const res = await fetch(`${API_BASE_URL}/users/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
        throw new Error(err.detail || 'Registration failed');
      }
      return res.json();
    }

    await new Promise((r) => setTimeout(r, 300));
    return {
      id: Date.now(),
      email,
      created_at: new Date().toISOString(),
    };
  },

  getGoogleLoginUrl(email?: string): string {
    const query = email?.trim() ? `?email=${encodeURIComponent(email.trim())}` : '';
    return `${API_BASE_URL}/users/auth/google/login${query}`;
  },

  async listWorkspaces(): Promise<Workspace[]> {
    if (!isDemoMode()) {
      const res = await fetch(`${API_BASE_URL}/workspaces/`, {
        headers: getAuthHeaders(),
      });
      checkUnauthorized(res);
      if (!res.ok) {
        throw new Error('Failed to load workspaces from backend');
      }
      return res.json();
    }
    return [...mockStore.workspaces];
  },

  async createWorkspace(
    name: string,
    pipelineConfig: WorkspacePipelineConfig = DEFAULT_PIPELINE_CONFIG
  ): Promise<Workspace> {
    if (!isDemoMode()) {
      const res = await fetch(`${API_BASE_URL}/workspaces/`, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ name, pipeline_config: pipelineConfig }),
      });
      checkUnauthorized(res);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Failed to create workspace' }));
        throw new Error(err.detail || 'Failed to create workspace');
      }
      return res.json();
    }

    const newWs: Workspace = {
      id: Date.now(),
      name,
      owner_id: 1,
      pipeline_config: pipelineConfig,
      created_at: new Date().toISOString(),
    };
    mockStore.workspaces = [newWs, ...mockStore.workspaces];
    mockStore.sources[newWs.id] = [];
    mockStore.conversations[newWs.id] = [];
    mockStore.save();
    return newWs;
  },

  async listSources(workspaceId: number): Promise<Source[]> {
    if (!isDemoMode()) {
      const res = await fetch(`${API_BASE_URL}/workspaces/${workspaceId}/sources/`, {
        headers: getAuthHeaders(),
      });
      checkUnauthorized(res);
      if (!res.ok) {
        return [];
      }
      return res.json();
    }
    return [...(mockStore.sources[workspaceId] || [])];
  },

  async uploadSourceFile(workspaceId: number, file: File): Promise<Source> {
    if (!isDemoMode()) {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API_BASE_URL}/workspaces/${workspaceId}/sources/upload`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData,
      });
      checkUnauthorized(res);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'File upload failed' }));
        throw new Error(err.detail || 'File upload failed');
      }
      return res.json();
    }

    await new Promise((r) => setTimeout(r, 600));
    const newSource: Source = {
      id: Date.now(),
      workspace_id: workspaceId,
      type: 'file',
      status: 'processed',
      storage_path: `/tmp/${file.name}`,
      mime_type: file.type || 'application/pdf',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    const existing = mockStore.sources[workspaceId] || [];
    mockStore.sources[workspaceId] = [newSource, ...existing];
    mockStore.save();
    return newSource;
  },

  async createUrlSource(workspaceId: number, url: string): Promise<Source> {
    if (!isDemoMode()) {
      const formData = new FormData();
      formData.append('url', url);
      const res = await fetch(`${API_BASE_URL}/workspaces/${workspaceId}/sources/url`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData,
      });
      checkUnauthorized(res);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'URL ingestion failed' }));
        throw new Error(err.detail || 'URL ingestion failed');
      }
      return res.json();
    }

    await new Promise((r) => setTimeout(r, 500));
    const newSource: Source = {
      id: Date.now(),
      workspace_id: workspaceId,
      type: 'url',
      status: 'processed',
      url,
      mime_type: 'text/html',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    const existing = mockStore.sources[workspaceId] || [];
    mockStore.sources[workspaceId] = [newSource, ...existing];
    mockStore.save();
    return newSource;
  },

  async deleteSource(workspaceId: number, sourceId: number): Promise<void> {
    if (!isDemoMode()) {
      const res = await fetch(`${API_BASE_URL}/workspaces/${workspaceId}/sources/${sourceId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      checkUnauthorized(res);
      if (!res.ok && res.status !== 204) {
        const err = await res.json().catch(() => ({ detail: 'Failed to delete source' }));
        throw new Error(err.detail || 'Failed to delete source');
      }
      return;
    }

    const existing = mockStore.sources[workspaceId] || [];
    mockStore.sources[workspaceId] = existing.filter((s) => s.id !== sourceId);
    mockStore.save();
  },

  async downloadSource(workspaceId: number, sourceId: number, filename: string): Promise<void> {
    if (!isDemoMode()) {
      const res = await fetch(
        `${API_BASE_URL}/workspaces/${workspaceId}/sources/sources/${sourceId}/download`,
        {
          headers: getAuthHeaders(),
        }
      );
      checkUnauthorized(res);
      if (!res.ok) {
        throw new Error('Failed to download source file');
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    }
  },

  async listConversations(workspaceId: number): Promise<Conversation[]> {
    if (!isDemoMode()) {
      const res = await fetch(`${API_BASE_URL}/workspaces/${workspaceId}/conversations/`, {
        headers: getAuthHeaders(),
      });
      checkUnauthorized(res);
      if (!res.ok) {
        return [];
      }
      return res.json();
    }
    return [...(mockStore.conversations[workspaceId] || [])];
  },

  async createConversation(workspaceId: number, title = 'New Conversation'): Promise<Conversation> {
    if (!isDemoMode()) {
      const res = await fetch(`${API_BASE_URL}/workspaces/${workspaceId}/conversations/`, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      });
      checkUnauthorized(res);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Failed to create conversation' }));
        throw new Error(err.detail || 'Failed to create conversation');
      }
      return res.json();
    }

    const newConv: Conversation = {
      id: Date.now(),
      title,
      is_private: true,
      created_at: new Date().toISOString(),
    };
    const existing = mockStore.conversations[workspaceId] || [];
    mockStore.conversations[workspaceId] = [newConv, ...existing];
    mockStore.chatTurns[newConv.id] = [];
    mockStore.save();
    return newConv;
  },

  async listChatTurns(workspaceId: number, conversationId: number): Promise<ChatTurn[]> {
    if (!isDemoMode()) {
      const [queriesRes, answersRes] = await Promise.all([
        fetch(`${API_BASE_URL}/workspaces/${workspaceId}/conversations/${conversationId}/queries`, {
          headers: getAuthHeaders(),
        }),
        fetch(`${API_BASE_URL}/workspaces/${workspaceId}/conversations/${conversationId}/answers`, {
          headers: getAuthHeaders(),
        }),
      ]);

      checkUnauthorized(queriesRes);
      if (queriesRes.ok && answersRes.ok) {
        const queries: QueryItem[] = await queriesRes.json();
        const answers: AnswerItem[] = await answersRes.json();
        return queries.map((q, idx) => ({
          id: `turn-${q.id}`,
          query: q,
          answer: answers.find((a) => a.query_id === q.id) || answers[idx],
        }));
      }
      return [];
    }

    return [...(mockStore.chatTurns[conversationId] || [])];
  },

  async submitQuery(
    workspaceId: number,
    conversationId: number,
    text: string
  ): Promise<{ turn: ChatTurn; updatedTitle?: string }> {
    const queryItem: QueryItem = {
      id: Date.now(),
      query_text: text,
      created_at: new Date().toISOString(),
    };

    if (!isDemoMode()) {
      const res = await fetch(
        `${API_BASE_URL}/workspaces/${workspaceId}/conversations/${conversationId}/queries`,
        {
          method: 'POST',
          headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify({ text }),
        }
      );

      checkUnauthorized(res);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Failed to process query' }));
        throw new Error(err.detail || 'Failed to process query');
      }

      const answer: AnswerItem = await res.json();

      // Fetch updated conversation to get backend-generated title if renamed
      let updatedTitle: string | undefined;
      try {
        const convRes = await fetch(
          `${API_BASE_URL}/workspaces/${workspaceId}/conversations/${conversationId}`,
          { headers: getAuthHeaders() }
        );
        if (convRes.ok) {
          const convData: Conversation = await convRes.json();
          updatedTitle = convData.title;
        }
      } catch {
        // Ignore title fetch error
      }

      return {
        turn: {
          id: `turn-${queryItem.id}`,
          query: queryItem,
          answer,
        },
        updatedTitle,
      };
    }

    await new Promise((r) => setTimeout(r, 650));
    const answer = generateMockAnswer(text);
    const turn: ChatTurn = {
      id: `turn-${queryItem.id}`,
      query: queryItem,
      answer,
    };

    const existingTurns = mockStore.chatTurns[conversationId] || [];
    mockStore.chatTurns[conversationId] = [...existingTurns, turn];

    let updatedTitle: string | undefined;
    if (existingTurns.length === 0) {
      updatedTitle = text.length > 26 ? `${text.slice(0, 26)}...` : text;
      const convs = mockStore.conversations[workspaceId] || [];
      mockStore.conversations[workspaceId] = convs.map((c) =>
        c.id === conversationId ? { ...c, title: updatedTitle! } : c
      );
    }

    mockStore.save();
    return { turn, updatedTitle };
  },
};
