/**
 * API Client for MAHER AI Backend
 *
 * This module provides a secure interface to the backend API.
 * The backend handles model provider routing (MetaBrain primary, Gemini fallback).
 * All AI calls go through the backend proxy to protect credentials.
 */

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Provider-agnostic request interface (backend handles routing)
interface GenerateRequest {
  contents: Array<{
    role: string;
    parts: Array<{ text: string }>;
  }>;
  systemInstruction?: string;
  agentId?: string;  // Optional: for knowledge context
  generationConfig?: {
    temperature?: number;
    topK?: number;
    topP?: number;
    maxOutputTokens?: number;
    stopSequences?: string[];
  };
}

// Backward compatibility alias
type GeminiGenerateRequest = GenerateRequest;

interface KnowledgeDocument {
  id: string;
  filename: string;
  extension: string;
  size: number;
  word_count: number;
  char_count: number;
  summary: string;
  content: string;
  uploaded_at: string;
}

interface AgentData {
  id: string;
  name: string;
  description: string;
  systemPrompt: string;
  category: string;
  iconSVG?: string;
  iconBackgroundColor?: string;
  defaultProvider: string;
  displayProviderName: string;
  status: 'draft' | 'published';
  statusText: string;
  statusClass: string;
  isSystem: boolean;
  createdBy: string;
  createdAt?: string;
  updatedAt?: string;
  networkId?: string;
  department?: string;
  // Skill fields
  toolSchema?: object | null;
  implementationType?: string;
  skillVersion?: string;
  isSkill?: boolean;
}

interface CreateAgentRequest {
  name: string;
  description: string;
  systemPrompt: string;
  category: string;
  iconSVG?: string;
  iconBackgroundColor?: string;
  defaultProvider?: string;
  displayProviderName?: string;
  status?: 'draft' | 'published';
  networkId?: string;
  department?: string;
  // Skill fields
  toolSchema?: object | null;
  implementationType?: string;
  skillVersion?: string;
}

interface UpdateAgentRequest {
  name?: string;
  description?: string;
  systemPrompt?: string;
  category?: string;
  iconSVG?: string;
  iconBackgroundColor?: string;
  defaultProvider?: string;
  displayProviderName?: string;
  networkId?: string;
  department?: string;
  // Skill fields
  toolSchema?: object | null;
  implementationType?: string;
  skillVersion?: string;
}

interface SkillSchemaRequest {
  name: string;
  category: string;
  taskDefinition: string;
  requiredExpertise?: string;
  decisionAuthority?: string;
}

interface SkillSchemaResponse {
  success: boolean;
  tool_schema?: object;
  error?: string;
}

interface SkillsOrchestratorRequest {
  input: string;
  history?: Array<{ role: string; content: string }>;
  system_prompt?: string;
}

interface SkillsOrchestratorResponse {
  success: boolean;
  response: string;
  skills_used: string[];
  provider: string;
  elapsed_sec: number;
}

interface KnowledgeUploadResponse {
  success: boolean;
  agent_id: string;
  processed_files: Array<{
    id: string;
    filename: string;
    size: number;
    word_count: number;
  }>;
  total_files: number;
  errors?: string[];
  partial_success?: boolean;
}

interface KnowledgeSummary {
  total_files: number;
  total_size: number;
  total_words: number;
  file_types: Record<string, number>;
  files: Array<{
    filename: string;
    extension: string;
    size: number;
    word_count: number;
    summary: string;
  }>;
}

// Response interface (Gemini-compatible format used by all providers)
interface GenerateResponse {
  candidates: Array<{
    content: {
      parts: Array<{ text: string }>;
      role: string;
    };
    finishReason: string;
    index: number;
  }>;
  usageMetadata?: {
    promptTokenCount: number;
    candidatesTokenCount: number;
    totalTokenCount: number;
  };
}

// Backward compatibility alias
type GeminiResponse = GenerateResponse;

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Generate AI response (routed to MetaBrain or Gemini by backend)
   */
  async generateContent(request: GeminiGenerateRequest): Promise<GeminiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  /**
   * Stream AI response (uses Gemini streaming or MetaBrain single-chunk)
   */
  async *streamContent(request: GeminiGenerateRequest): AsyncGenerator<any, void, unknown> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.error || `HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Response body is not readable');
      }

      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            yield data;
          } catch (e) {
            // Skip invalid JSON lines
            console.warn('Invalid JSON in stream:', line);
          }
        }
      }
    } catch (error) {
      console.error('Streaming Error:', error);
      throw error;
    }
  }

  /**
   * Get available AI model providers and their status
   */
  async getModels(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/models`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get Models Error:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Health Check Error:', error);
      throw error;
    }
  }

  /**
   * Upload knowledge files for an agent
   */
  async uploadKnowledge(agentId: string, files: File[], onProgress?: (progress: number) => void): Promise<KnowledgeUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('agent_id', agentId);

      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch(`${this.baseUrl}/knowledge/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Upload failed' }));
        throw new Error(error.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Knowledge Upload Error:', error);
      throw error;
    }
  }

  /**
   * Get agent's knowledge base
   */
  async getAgentKnowledge(agentId: string): Promise<{
    agent_id: string;
    knowledge: {
      agent_id: string;
      documents: KnowledgeDocument[];
      created_at: string;
      updated_at?: string;
    };
    summary: KnowledgeSummary;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/knowledge/agents/${agentId}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get Agent Knowledge Error:', error);
      throw error;
    }
  }

  /**
   * Delete all knowledge for an agent
   */
  async deleteAgentKnowledge(agentId: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/knowledge/agents/${agentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Delete Agent Knowledge Error:', error);
      throw error;
    }
  }

  /**
   * Delete a specific file from agent's knowledge
   */
  async deleteKnowledgeFile(agentId: string, fileId: string): Promise<{
    success: boolean;
    message: string;
    remaining_files: number;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/knowledge/agents/${agentId}/files/${fileId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Delete Knowledge File Error:', error);
      throw error;
    }
  }

  // ============================================================================
  // Agent Management Methods
  // ============================================================================

  /**
   * Get all agents
   * @param includeDrafts - Include draft agents (default: false, only published)
   * @param category - Filter by category
   */
  async getAgents(includeDrafts: boolean = false, category?: string, viewMode: 'personal' | 'all' = 'personal'): Promise<{
    success: boolean;
    agents: AgentData[];
    count: number;
  }> {
    try {
      const params = new URLSearchParams();
      if (includeDrafts) params.append('include_drafts', 'true');
      if (category) params.append('category', category);
      if (viewMode) params.append('view_mode', viewMode);

      const sessionId = this.getSessionId();

      const url = `${this.baseUrl}/agents${params.toString() ? '?' + params.toString() : ''}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId || '',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get Agents Error:', error);
      throw error;
    }
  }

  /**
   * Get a single agent by ID
   */
  async getAgent(agentId: string): Promise<{
    success: boolean;
    agent: AgentData;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/${agentId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get Agent Error:', error);
      throw error;
    }
  }

  /**
   * Create a new agent
   */
  async createAgent(agentData: CreateAgentRequest): Promise<{
    success: boolean;
    message: string;
    agent: AgentData;
  }> {
    try {
      const sessionId = this.getSessionId();
      const response = await fetch(`${this.baseUrl}/agents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId || '',
        },
        body: JSON.stringify(agentData),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Create failed' }));
        throw new Error(error.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Create Agent Error:', error);
      throw error;
    }
  }

  /**
   * Update an existing agent
   */
  async updateAgent(agentId: string, agentData: UpdateAgentRequest): Promise<{
    success: boolean;
    message: string;
    agent: AgentData;
  }> {
    try {
      const sessionId = this.getSessionId();
      const response = await fetch(`${this.baseUrl}/agents/${agentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId || '',
        },
        body: JSON.stringify(agentData),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Update failed' }));
        throw new Error(error.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Update Agent Error:', error);
      throw error;
    }
  }

  /**
   * Publish an agent (change from draft to published)
   */
  async publishAgent(agentId: string): Promise<{
    success: boolean;
    message: string;
    agent: AgentData;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/${agentId}/publish`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Publish failed' }));
        throw new Error(error.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Publish Agent Error:', error);
      throw error;
    }
  }

  /**
   * Delete an agent
   */
  async deleteAgent(agentId: string): Promise<{
    success: boolean;
    message: string;
  }> {
    try {
      const sessionId = this.getSessionId();
      const response = await fetch(`${this.baseUrl}/agents/${agentId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId || '',
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Delete failed' }));
        throw new Error(error.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Delete Agent Error:', error);
      throw error;
    }
  }

  // ============================================================================
  // Authentication Methods
  // ============================================================================

  /**
   * Get session ID from localStorage
   */
  private getSessionId(): string | null {
    return localStorage.getItem('maher_session_id');
  }

  /**
   * Get user role from localStorage
   */
  getUserRole(): 'guest' | 'admin' | null {
    return localStorage.getItem('maher_user_role') as 'guest' | 'admin' | null;
  }

  /**
   * Check if user is admin
   */
  isAdmin(): boolean {
    return this.getUserRole() === 'admin';
  }

  /**
   * Admin login
   */
  async adminLogin(password: string): Promise<{
    success: boolean;
    role: string;
    session_id: string;
    error?: string;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Store session
        localStorage.setItem('maher_session_id', data.session_id);
        localStorage.setItem('maher_user_role', data.role);
      }

      return data;
    } catch (error) {
      console.error('Admin Login Error:', error);
      throw error;
    }
  }

  /**
   * Create or retrieve guest session
   */
  async createGuestSession(): Promise<{
    session_id: string;
    role: string;
  }> {
    try {
      const existingSession = this.getSessionId();

      const response = await fetch(`${this.baseUrl}/auth/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: existingSession,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Store session
      localStorage.setItem('maher_session_id', data.session_id);
      localStorage.setItem('maher_user_role', data.role);

      return data;
    } catch (error) {
      console.error('Create Guest Session Error:', error);
      throw error;
    }
  }

  /**
   * Verify current session
   */
  async verifySession(): Promise<{
    valid: boolean;
    role?: string;
  }> {
    try {
      const sessionId = this.getSessionId();

      if (!sessionId) {
        return { valid: false };
      }

      const response = await fetch(`${this.baseUrl}/auth/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (!response.ok) {
        return { valid: false };
      }

      const data = await response.json();

      if (data.valid && data.role) {
        localStorage.setItem('maher_user_role', data.role);
      }

      return data;
    } catch (error) {
      console.error('Verify Session Error:', error);
      return { valid: false };
    }
  }

  /**
   * Logout (delete session)
   */
  async logout(): Promise<{ success: boolean }> {
    try {
      const sessionId = this.getSessionId();

      if (!sessionId) {
        return { success: true };
      }

      const response = await fetch(`${this.baseUrl}/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });

      // Clear local storage regardless of response
      localStorage.removeItem('maher_session_id');
      localStorage.removeItem('maher_user_role');

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Logout Error:', error);
      // Still clear local storage
      localStorage.removeItem('maher_session_id');
      localStorage.removeItem('maher_user_role');
      throw error;
    }
  }

  // ============================================================================
  // Skills Methods
  // ============================================================================

  /**
   * Generate an OpenAI function-calling tool_schema from agent wizard data.
   * Called by AI Studio's "Generate Skill Schema" button.
   */
  async generateSkillSchema(request: SkillSchemaRequest): Promise<SkillSchemaResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/skills/generate-schema`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      return await response.json();
    } catch (error) {
      console.error('Generate Skill Schema Error:', error);
      throw error;
    }
  }

  /**
   * Get all published agents that have a tool_schema (i.e. are registered skills).
   */
  async getSkillAgents(): Promise<{ success: boolean; skills: AgentData[]; count: number }> {
    try {
      const response = await fetch(`${this.baseUrl}/skills/agents`);
      return await response.json();
    } catch (error) {
      console.error('Get Skill Agents Error:', error);
      throw error;
    }
  }

  /**
   * Process a request through the Skills Orchestrator (GPT-OSS native function calling).
   * Falls back to hybrid orchestrator response shape for backward compatibility.
   */
  async processWithSkillsOrchestrator(
    request: SkillsOrchestratorRequest
  ): Promise<SkillsOrchestratorResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/skills-orchestrator/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(err.error || `HTTP ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Skills Orchestrator Error:', error);
      throw error;
    }
  }

  /**
   * Hot-reload the skills registry (admin only).
   * Call after publishing a new skill from AI Studio.
   */
  async reloadSkills(): Promise<{ success: boolean; skills_count: number }> {
    try {
      const sessionId = this.getSessionId();
      const response = await fetch(`${this.baseUrl}/skills-orchestrator/reload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId || '',
        },
      });
      return await response.json();
    } catch (error) {
      console.error('Reload Skills Error:', error);
      throw error;
    }
  }

  /**
   * Get analytics dashboard data (admin only)
   */
  async getAnalytics(): Promise<{
    total_visits: number;
    total_chats: number;
    total_agents: number;
    active_users: number;
    visits_today: number;
    chats_today: number;
    top_agents: Array<{ agent: string; count: number }>;
    recent_activity: Array<{
      id: number;
      agent: string;
      messages: number;
      time: string;
    }>;
  }> {
    try {
      const sessionId = this.getSessionId();

      const response = await fetch(`${this.baseUrl}/admin/analytics`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId || '',
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unauthorized' }));
        throw new Error(error.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get Analytics Error:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const apiClient = new APIClient();

// Export types (includes backward-compatible aliases)
export type {
  GenerateRequest,
  GenerateResponse,
  GeminiGenerateRequest,
  GeminiResponse,
  KnowledgeDocument,
  KnowledgeUploadResponse,
  KnowledgeSummary,
  AgentData,
  CreateAgentRequest,
  UpdateAgentRequest
};
