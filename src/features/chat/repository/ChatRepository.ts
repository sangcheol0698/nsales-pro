import { fetchEventSource } from '@microsoft/fetch-event-source';
import axios from 'axios';
import type {
  ChatRequest,
  ChatResponse,
  ChatSession,
  ChatStreamChunk,
  ChatMessage,
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
    files: File[]
  ): Promise<ChatResponse> {
    const formData = new FormData();
    formData.append('content', content);
    formData.append('sessionId', sessionId);
    
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
}