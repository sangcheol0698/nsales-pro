import { fetchEventSource } from '@microsoft/fetch-event-source';
import axios from 'axios';
import type {
  ChatRequest,
  ChatResponse,
  ChatSession,
  ChatStreamChunk,
  EnhancedChatRequest,
  ToolsStatus,
} from '../entity/ChatMessage';
import type { ChatHistory, ChatSearch, ChatSessionList } from '../entity/ChatSearch';

export class ChatRepository {
  private baseURL = 'http://localhost:8000/api/v1';

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await axios.post(`${this.baseURL}/chat/messages`, request);
    return response.data;
  }

  async sendMessageWithFiles(
    content: string,
    sessionId: string,
    files: File[],
    model?: string,
    webSearch?: boolean
  ): Promise<ChatResponse> {
    const formData = new FormData();
    formData.append('content', content);
    formData.append('sessionId', sessionId);
    if (model) {
      formData.append('model', model);
    }
    if (webSearch) {
      formData.append('webSearch', 'true');
    }

    // 파일들을 FormData에 추가
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await axios.post(`${this.baseURL}/chat/messages/with-files`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async streamMessage(
    request: ChatRequest,
    onChunk: (chunk: ChatStreamChunk) => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    try {
      await fetchEventSource(`${this.baseURL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        onmessage: (event) => {
          try {
            const chunk: ChatStreamChunk = JSON.parse(event.data);
            onChunk(chunk);
          } catch (error) {
            console.error('Failed to parse SSE chunk:', error);
          }
        },
        onerror: (error) => {
          console.error('SSE connection error:', error);
          onError?.(error instanceof Error ? error : new Error('SSE connection failed'));
        },
      });
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error('Stream failed'));
    }
  }

  async createSession(title?: string): Promise<ChatSession> {
    const response = await axios.post(`${this.baseURL}/chat/sessions`, { title });
    return response.data;
  }

  async getSession(sessionId: string): Promise<ChatSession> {
    const response = await axios.get(`${this.baseURL}/chat/sessions/${sessionId}`);
    return response.data;
  }

  async getSessions(search: ChatSearch): Promise<ChatSessionList> {
    const response = await axios.get(`${this.baseURL}/chat/sessions`, { params: search });
    return response.data;
  }

  async updateSession(sessionId: string, title: string): Promise<void> {
    await axios.patch(`${this.baseURL}/chat/sessions/${sessionId}`, { title });
  }

  async deleteSession(sessionId: string): Promise<void> {
    await axios.delete(`${this.baseURL}/chat/sessions/${sessionId}`);
  }

  async getMessageHistory(sessionId: string): Promise<ChatHistory> {
    const response = await axios.get(`${this.baseURL}/chat/sessions/${sessionId}/messages`);
    return response.data;
  }

  async deleteMessage(messageId: string): Promise<void> {
    await axios.delete(`${this.baseURL}/chat/messages/${messageId}`);
  }

  async regenerateMessage(messageId: string): Promise<ChatResponse> {
    const response = await axios.post(`${this.baseURL}/chat/messages/${messageId}/regenerate`);
    return response.data;
  }

  // 프로덕션에서는 필요 없음 (서버에서 초기 데이터 제공)
  async initializeDemoData(): Promise<void> {
    // 서버에서 자동으로 데모 데이터를 제공하므로 아무것도 하지 않음
  }

  // ===== Enhanced Chat API with Tools =====

  /**
   * Enhanced Chat API로 메시지 전송 (Tools 지원)
   */
  async sendEnhancedMessage(
    request: EnhancedChatRequest,
    onChunk: (chunk: ChatStreamChunk) => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    try {
      await fetchEventSource(`${this.baseURL}/chat/enhanced`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        onmessage: (event) => {
          try {
            const chunk: ChatStreamChunk = JSON.parse(event.data);
            onChunk(chunk);
          } catch (error) {
            console.error('Failed to parse Enhanced SSE chunk:', error);
          }
        },
        onerror: (error) => {
          console.error('Enhanced SSE connection error:', error);
          onError?.(error instanceof Error ? error : new Error('Enhanced SSE connection failed'));
        },
      });
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error('Enhanced stream failed'));
    }
  }

  /**
   * Tools 시스템 상태 조회
   */
  async getToolsStatus(): Promise<ToolsStatus> {
    const response = await axios.get(`${this.baseURL}/tools/status`);
    return response.data;
  }

  /**
   * 사용 가능한 도구 목록 조회
   */
  async getAvailableTools(): Promise<{ tools: Record<string, ToolInfo[]>; schemas: any[] }> {
    const response = await axios.get(`${this.baseURL}/tools/list`);
    return response.data;
  }
}
