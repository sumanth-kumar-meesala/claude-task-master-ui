/**
 * Chat Service - handles agent chat interactions
 */

import { BaseApiService } from './api';
import type { ApiResponse } from '@/types/common';

// Chat Types
export interface ChatMessage {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  agentId?: string;
  agentName?: string;
  metadata?: Record<string, any>;
}

export interface ChatSession {
  id: string;
  projectId: string;
  title: string;
  messages: ChatMessage[];
  participants: string[]; // Agent IDs
  created_at: string;
  updated_at: string;
  status: 'active' | 'archived';
}

export interface SendMessageRequest {
  sessionId?: string;
  message: string;
  agentId: string; // 'all' for crew, specific ID for individual agent
  context?: {
    project_id: string;
    project_name?: string;
    project_description?: string;
    project_requirements?: string;
    tech_stack?: string[];
    previous_messages?: ChatMessage[];
  };
}

export interface SendMessageResponse {
  message: ChatMessage;
  session: ChatSession;
}



// Chat Service
export class ChatService extends BaseApiService {
  constructor() {
    super('/api/v1');
  }

  /**
   * Create a new chat session
   */
  async createChatSession(projectId: string, agentIds: string[]): Promise<ApiResponse<ChatSession>> {
    return this.post('/chat/sessions', {
      project_id: projectId,
      participants: agentIds,
      title: `Chat Session - ${new Date().toLocaleDateString()}`
    });
  }

  /**
   * Get chat sessions for a project
   */
  async getChatSessions(projectId: string): Promise<ApiResponse<{ sessions: ChatSession[] }>> {
    return this.get(`/chat/sessions?project_id=${projectId}`);
  }

  /**
   * Get a specific chat session
   */
  async getChatSession(sessionId: string): Promise<ApiResponse<ChatSession>> {
    return this.get(`/chat/sessions/${sessionId}`);
  }

  /**
   * Complete a chat session
   */
  async completeChatSession(sessionId: string): Promise<ApiResponse<any>> {
    return this.post(`/chat/sessions/${sessionId}/complete`, {});
  }

  /**
   * Get generated files from an orchestration
   */
  async getOrchestrationFiles(orchestrationId: string): Promise<ApiResponse<{
    orchestration_id: string;
    files: Record<string, string>;
    file_paths: string[];
  }>> {
    return this.get(`/chat/orchestrations/${orchestrationId}/files`);
  }

  /**
   * Send a message to agents
   */
  async sendMessage(request: SendMessageRequest): Promise<ApiResponse<SendMessageResponse>> {
    // Use longer timeout for agent execution (2 minutes)
    return this.post('/chat/messages', request, { timeout: 120000 });
  }



  /**
   * Save project overview
   */
  async saveProjectOverview(projectId: string, overviewData: any): Promise<ApiResponse<any>> {
    // Use longer timeout for overview save (1 minute)
    return this.post('/chat/overview/save', {
      project_id: projectId,
      overview_data: overviewData
    }, { timeout: 60000 });
  }

  /**
   * Generate project files based on conversation
   */
  async generateProjectFiles(request: {
    project_id: string;
    project_name: string;
    project_description?: string;
    requirements?: string;
    tech_stack?: string[];
    conversation_history?: Array<{
      type: string;
      content: string;
      agent?: string;
      timestamp: string;
    }>;
    agents: string[];
  }): Promise<ApiResponse<any>> {
    // Use longer timeout for file generation (3 minutes)
    return this.post('/chat/generate-files', request, { timeout: 180000 });
  }



  /**
   * Get all orchestration sessions for a project
   */
  async getProjectOrchestrationSessions(projectId: string): Promise<ApiResponse<{
    project_id: string;
    sessions: Array<{
      id: string;
      project_id: string;
      name?: string;
      description?: string;
      status: string;
      created_at: string;
      updated_at: string;
      started_at?: string;
      completed_at?: string;
      duration?: number;
      agent_results: any;
      metadata: any;
    }>;
    total_sessions: number;
  }>> {
    return this.get(`/orchestration/projects/${projectId}/sessions`);
  }

  /**
   * Get detailed information about a specific orchestration session
   */
  async getOrchestrationSessionDetails(sessionId: string): Promise<ApiResponse<any>> {
    return this.get(`/orchestration/sessions/${sessionId}/details`);
  }

  /**
   * Restore an orchestration session from database to active memory
   */
  async restoreOrchestrationSession(sessionId: string): Promise<ApiResponse<any>> {
    return this.post(`/orchestration/sessions/${sessionId}/restore`, {});
  }

  /**
   * Get project overview
   */
  async getProjectOverview(projectId: string): Promise<ApiResponse<any>> {
    const response = await this.get<ApiResponse<any>>(`/chat/overview/${projectId}`);
    // Extract overview data from metadata for easier frontend consumption
    if (response.data && response.data.metadata && response.data.metadata.overview_data) {
      return {
        ...response,
        data: response.data.metadata.overview_data
      };
    }
    return response;
  }

  /**
   * Get all project overviews
   */
  async getAllProjectOverviews(): Promise<ApiResponse<{ overviews: any[] }>> {
    const response = await this.get<ApiResponse<{ overviews: any[] }>>('/chat/overviews');
    // Extract overview data from metadata for each overview
    if (response.data && response.data.overviews) {
      const processedOverviews = response.data.overviews.map((overview: any) => ({
        ...overview,
        overview_data: overview.metadata?.overview_data || {}
      }));
      return {
        ...response,
        data: { overviews: processedOverviews }
      };
    }
    return response;
  }



  /**
   * Get authentication headers
   */
  private getAuthHeaders(): Record<string, string> {
    // Add authentication headers if needed
    return {};
  }
}

// Create and export service instance
export const chatService = new ChatService();

// Utility functions for chat
export const chatUtils = {
  /**
   * Format message timestamp
   */
  formatMessageTime(timestamp: string | Date): string {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  },

  /**
   * Format message date
   */
  formatMessageDate(timestamp: string | Date): string {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  },

  /**
   * Group messages by date
   */
  groupMessagesByDate(messages: ChatMessage[]): Record<string, ChatMessage[]> {
    const grouped: Record<string, ChatMessage[]> = {};
    
    messages.forEach(message => {
      const dateKey = this.formatMessageDate(message.timestamp);
      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      grouped[dateKey].push(message);
    });
    
    return grouped;
  },

  /**
   * Generate session title from messages
   */
  generateSessionTitle(messages: ChatMessage[]): string {
    const userMessages = messages.filter(m => m.type === 'user');
    if (userMessages.length > 0) {
      const firstMessage = userMessages[0].content;
      return firstMessage.length > 50 
        ? firstMessage.substring(0, 50) + '...'
        : firstMessage;
    }
    return `Chat Session - ${new Date().toLocaleDateString()}`;
  },

  /**
   * Extract keywords from messages for search
   */
  extractKeywords(messages: ChatMessage[]): string[] {
    const text = messages
      .filter(m => m.type === 'user')
      .map(m => m.content)
      .join(' ');
    
    // Simple keyword extraction (can be enhanced with NLP)
    const words = text
      .toLowerCase()
      .replace(/[^\w\s]/g, '')
      .split(/\s+/)
      .filter(word => word.length > 3);
    
    // Remove duplicates and return top keywords
    return [...new Set(words)].slice(0, 10);
  },

  /**
   * Calculate session duration
   */
  calculateSessionDuration(messages: ChatMessage[]): number {
    if (messages.length < 2) return 0;
    
    const firstMessage = new Date(messages[0].timestamp);
    const lastMessage = new Date(messages[messages.length - 1].timestamp);
    
    return lastMessage.getTime() - firstMessage.getTime();
  },

  /**
   * Get session statistics
   */
  getSessionStats(session: ChatSession): {
    messageCount: number;
    userMessages: number;
    agentMessages: number;
    duration: number;
    participantCount: number;
  } {
    const userMessages = session.messages.filter(m => m.type === 'user').length;
    const agentMessages = session.messages.filter(m => m.type === 'agent').length;
    
    return {
      messageCount: session.messages.length,
      userMessages,
      agentMessages,
      duration: this.calculateSessionDuration(session.messages),
      participantCount: session.participants.length,
    };
  },
};
