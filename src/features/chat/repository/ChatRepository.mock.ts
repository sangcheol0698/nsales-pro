import type {
  ChatRequest,
  ChatResponse,
  ChatSession,
  ChatStreamChunk,
  ChatMessage,
} from '../entity/ChatMessage';
import type { ChatHistory, ChatSearch, ChatSessionList } from '../entity/ChatSearch';

export class ChatRepository {
  private sessions: ChatSession[] = [];
  private messages: Map<string, ChatMessage[]> = new Map();

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    // 모킹된 응답을 시뮬레이션
    await this.delay(500);
    
    const response: ChatResponse = {
      id: this.generateId(),
      content: this.generateMockResponse(request.content),
      role: 'assistant',
      timestamp: new Date(),
      sessionId: request.sessionId,
    };

    // 메시지를 저장
    const sessionMessages = this.messages.get(request.sessionId) || [];
    
    // 사용자 메시지 추가
    const userMessage: ChatMessage = {
      id: this.generateId(),
      content: request.content,
      role: 'user',
      timestamp: new Date(),
      sessionId: request.sessionId,
    };
    
    sessionMessages.push(userMessage, response);
    this.messages.set(request.sessionId, sessionMessages);

    return response;
  }

  async streamMessage(
    request: ChatRequest,
    onChunk: (chunk: ChatStreamChunk) => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    try {
      const response = this.generateMockResponse(request.content);
      const words = response.split(' ');
      
      // 사용자 메시지 먼저 저장
      const sessionMessages = this.messages.get(request.sessionId) || [];
      const userMessage: ChatMessage = {
        id: this.generateId(),
        content: request.content,
        role: 'user',
        timestamp: new Date(),
        sessionId: request.sessionId,
      };
      sessionMessages.push(userMessage);
      
      const assistantId = this.generateId();
      let accumulated = '';
      
      // 스트리밍 시뮬레이션
      for (let i = 0; i < words.length; i++) {
        await this.delay(100);
        
        const word = words[i];
        accumulated += (i > 0 ? ' ' : '') + word;
        
        const chunk: ChatStreamChunk = {
          id: assistantId,
          content: word,
          role: 'assistant',
          timestamp: new Date(),
          sessionId: request.sessionId,
          isComplete: i === words.length - 1,
        };
        
        onChunk(chunk);
      }
      
      // 완성된 응답 저장
      const assistantMessage: ChatMessage = {
        id: assistantId,
        content: accumulated,
        role: 'assistant',
        timestamp: new Date(),
        sessionId: request.sessionId,
      };
      
      sessionMessages.push(assistantMessage);
      this.messages.set(request.sessionId, sessionMessages);
      
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error('Stream failed'));
    }
  }

  async createSession(title?: string): Promise<ChatSession> {
    await this.delay(200);
    
    const session: ChatSession = {
      id: this.generateId(),
      title: title || `새 채팅 ${this.sessions.length + 1}`,
      createdAt: new Date(),
      updatedAt: new Date(),
      messageCount: 0,
    };
    
    this.sessions.unshift(session);
    this.messages.set(session.id, []);
    
    return session;
  }

  async getSession(sessionId: string): Promise<ChatSession> {
    await this.delay(100);
    
    const session = this.sessions.find(s => s.id === sessionId);
    if (!session) {
      throw new Error('Session not found');
    }
    
    return session;
  }

  async getSessions(search: ChatSearch): Promise<ChatSessionList> {
    await this.delay(200);
    
    let filteredSessions = [...this.sessions];
    
    // 검색 필터 적용
    if (search.query) {
      filteredSessions = filteredSessions.filter(session =>
        session.title.toLowerCase().includes(search.query!.toLowerCase())
      );
    }
    
    // 페이징 적용
    const start = search.page * search.size;
    const end = start + search.size;
    const pagedSessions = filteredSessions.slice(start, end);
    
    return {
      sessions: pagedSessions,
      totalElements: filteredSessions.length,
      totalPages: Math.ceil(filteredSessions.length / search.size),
      currentPage: search.page,
      size: search.size,
    };
  }

  async updateSession(sessionId: string, title: string): Promise<void> {
    await this.delay(200);
    
    const session = this.sessions.find(s => s.id === sessionId);
    if (!session) {
      throw new Error('Session not found');
    }
    
    session.title = title;
    session.updatedAt = new Date();
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.delay(200);
    
    const index = this.sessions.findIndex(s => s.id === sessionId);
    if (index === -1) {
      throw new Error('Session not found');
    }
    
    this.sessions.splice(index, 1);
    this.messages.delete(sessionId);
  }

  async getMessageHistory(sessionId: string): Promise<ChatHistory> {
    await this.delay(100);
    
    const messages = this.messages.get(sessionId) || [];
    
    return {
      messages,
      sessionId,
      totalCount: messages.length,
    };
  }

  async deleteMessage(messageId: string): Promise<void> {
    await this.delay(200);
    
    for (const [sessionId, messages] of this.messages.entries()) {
      const index = messages.findIndex(m => m.id === messageId);
      if (index !== -1) {
        messages.splice(index, 1);
        this.messages.set(sessionId, messages);
        return;
      }
    }
    
    throw new Error('Message not found');
  }

  async regenerateMessage(messageId: string): Promise<ChatResponse> {
    await this.delay(500);
    
    for (const [sessionId, messages] of this.messages.entries()) {
      const index = messages.findIndex(m => m.id === messageId);
      if (index !== -1) {
        const message = messages[index];
        const newResponse: ChatResponse = {
          id: this.generateId(),
          content: this.generateMockResponse("다시 생성해주세요"),
          role: 'assistant',
          timestamp: new Date(),
          sessionId,
        };
        
        messages[index] = newResponse;
        this.messages.set(sessionId, messages);
        
        return newResponse;
      }
    }
    
    throw new Error('Message not found');
  }

  private generateId(): string {
    return 'mock_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private generateMockResponse(userMessage: string): string {
    const responses = [
      `안녕하세요! "${userMessage}"에 대해 답변드리겠습니다. 이것은 모킹된 응답입니다.`,
      `네, 말씀하신 "${userMessage}"와 관련하여 도움을 드릴 수 있습니다. 영업 데이터를 분석해보면 좋은 인사이트를 얻을 수 있을 것 같습니다.`,
      `좋은 질문이네요! "${userMessage}"에 대한 답변을 드리자면, 프로젝트 관리 측면에서 몇 가지 제안사항이 있습니다.`,
      `"${userMessage}"에 대해 자세히 설명해드리겠습니다. 현재 시스템에서 확인 가능한 정보를 바탕으로 분석해보겠습니다.`,
      `네, 이해했습니다. "${userMessage}"와 관련하여 다음과 같은 정보를 제공할 수 있습니다. 추가로 궁금한 점이 있으시면 언제든 말씀해주세요.`,
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  }

  // 초기 데모 데이터 생성
  async initializeDemoData(): Promise<void> {
    if (this.sessions.length === 0) {
      // 데모 세션들 생성
      const demoSessions: ChatSession[] = [
        {
          id: 'demo_1',
          title: '영업 데이터 분석',
          createdAt: new Date(Date.now() - 86400000), // 1일 전
          updatedAt: new Date(Date.now() - 3600000), // 1시간 전
          messageCount: 6,
        },
        {
          id: 'demo_2',
          title: '프로젝트 현황 조회',
          createdAt: new Date(Date.now() - 172800000), // 2일 전
          updatedAt: new Date(Date.now() - 7200000), // 2시간 전
          messageCount: 4,
        },
        {
          id: 'demo_3',
          title: '고객사 정보 문의',
          createdAt: new Date(Date.now() - 259200000), // 3일 전
          updatedAt: new Date(Date.now() - 10800000), // 3시간 전
          messageCount: 8,
        },
      ];
      
      this.sessions = demoSessions;
      
      // 데모 메시지들 생성
      this.messages.set('demo_1', [
        {
          id: 'msg_1',
          content: '이번 분기 영업 성과는 어떤가요?',
          role: 'user',
          timestamp: new Date(Date.now() - 3600000),
          sessionId: 'demo_1',
        },
        {
          id: 'msg_2',
          content: '이번 분기 영업 성과를 분석해보겠습니다. 전체적으로 목표 대비 115% 달성했으며, 특히 새로운 고객 확보 부분에서 좋은 성과를 보였습니다.',
          role: 'assistant',
          timestamp: new Date(Date.now() - 3580000),
          sessionId: 'demo_1',
        },
      ]);
      
      this.messages.set('demo_2', [
        {
          id: 'msg_3',
          content: '진행 중인 프로젝트 목록을 보여주세요',
          role: 'user',
          timestamp: new Date(Date.now() - 7200000),
          sessionId: 'demo_2',
        },
        {
          id: 'msg_4',
          content: '현재 진행 중인 프로젝트는 총 12개입니다. 그 중 5개는 개발 단계, 4개는 테스트 단계, 3개는 배포 준비 단계에 있습니다.',
          role: 'assistant',
          timestamp: new Date(Date.now() - 7180000),
          sessionId: 'demo_2',
        },
      ]);
      
      this.messages.set('demo_3', []);
    }
  }
}