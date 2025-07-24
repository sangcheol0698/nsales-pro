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
  private activeRequests = new Set<string>();
  private abortController: AbortController | null = null;

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

  async sendMessageWithFilesStreaming(
    content: string,
    sessionId: string,
    files: File[],
    model?: string,
    webSearch?: boolean,
    onChunk: (chunk: ChatStreamChunk) => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    // 중복 요청 방지
    const requestId = `${sessionId}_${Date.now()}_${Math.random()}`;
    
    if (this.activeRequests.has(requestId)) {
      console.warn('🚫 Duplicate file upload request prevented:', requestId);
      return;
    }
    
    // 기존 요청 중단
    if (this.abortController) {
      console.log('📋 Aborting previous file upload request');
      this.abortController.abort();
    }
    
    this.abortController = new AbortController();
    this.activeRequests.add(requestId);
    console.log('🚀 Starting file upload stream:', requestId);
    
    try {
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

      await fetchEventSource(`${this.baseURL}/chat/messages/with-files/stream`, {
        method: 'POST',
        body: formData,
        signal: this.abortController.signal,
        onmessage: (event) => {
          try {
            const chunk: ChatStreamChunk = JSON.parse(event.data);
            onChunk(chunk);
          } catch (error) {
            console.error('Failed to parse file upload SSE chunk:', error);
          }
        },
        onerror: (error) => {
          console.error('File upload SSE connection error:', error);
          onError?.(error instanceof Error ? error : new Error('File upload SSE connection failed'));
        },
      });
      
      console.log('✅ File upload stream completed successfully:', requestId);
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('📋 File upload stream aborted:', requestId);
      } else {
        console.error('❌ File upload stream failed:', requestId, error);
        onError?.(error instanceof Error ? error : new Error('File upload stream failed'));
      }
    } finally {
      this.activeRequests.delete(requestId);
      if (this.abortController?.signal.aborted === false) {
        this.abortController = null;
      }
    }
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
    const data: ChatHistory = response.data;
    
    // Google Tools 메시지에서 JSON 마크다운 블록 제거
    data.messages = data.messages.map(message => {
      // Assistant 메시지이고 Google Tools를 사용한 경우
      if (message.role === 'assistant' && 
          message.toolCall && 
          ['get_calendar_events', 'get_emails', 'create_calendar_event', 'send_email', 'find_free_time'].includes(message.toolCall) &&
          message.toolStatus === 'completed') {
        
        // 디버깅을 위한 로그
        console.log('🔍 원본 메시지 내용:', message.content);
        console.log('🔍 메시지 길이:', message.content.length);
        console.log('🔍 JSON 패턴 매치:', message.content.match(/```json/gi));
        
        // JSON 마크다운 블록 제거 (여러 패턴 시도)
        let cleanedContent = message.content;
        
        // 가장 간단하고 확실한 방법: 코드 블록 전체 제거
        const codeBlockPattern = /```[\s\S]*?```/g;
        const matches = cleanedContent.match(codeBlockPattern);
        
        if (matches) {
          console.log('🔍 찾은 코드 블록들:', matches);
          matches.forEach((match, index) => {
            // JSON을 포함하는 코드 블록만 제거
            if (match.toLowerCase().includes('json') || match.includes('"id":') || match.includes('"title":')) {
              console.log(`🗑️ 제거할 코드 블록 ${index + 1}:`, match.substring(0, 100) + '...');
              cleanedContent = cleanedContent.replace(match, '');
            }
          });
        }
        
        console.log('✨ 정리된 메시지 내용:', cleanedContent);
        
        return {
          ...message,
          content: cleanedContent.trim()
        };
      }
      
      return message;
    });
    
    return data;
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
