export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date | string
  sessionId?: string
  // Tool execution 관련 필드들
  toolCall?: string // 실행된 도구 이름
  toolStatus?: 'running' | 'completed' | 'error' // 도구 실행 상태
  toolResult?: any // 도구 실행 결과
  // 파일 첨부 관련 필드들
  attachedFiles?: Array<{
    name: string
    size: number
    type: string
  }>
  // 분석 상태 관련 필드들
  isAnalyzing?: boolean
  analyzingType?: 'image' | 'document'
}

export interface ChatSession {
  id: string
  title: string
  messageCount: number
  createdAt: Date | string
  updatedAt: Date | string
  // AI 제목 생성 관련 필드들
  titleGenerated?: boolean
  titleGeneratedAt?: Date | string
}

export interface ChatRequest {
  content: string
  sessionId: string
  model?: string
  webSearch?: boolean
}

// Enhanced Chat API 요청 인터페이스
export interface EnhancedChatRequest {
  message: string
  sessionId: string
  model?: string
  webSearch?: boolean
}

// Tool 관련 인터페이스들
export interface ToolInfo {
  name: string
  description: string
}

export interface ToolsStatus {
  available: boolean
  status: {
    total_tools: number
    categories: Record<string, number>
    tools: string[]
  }
  tools: Record<string, ToolInfo[]>
  google_auth_status: boolean
}

export interface ChatResponse {
  id: string
  content: string
  role: string
  timestamp: Date | string
  sessionId: string
}

export interface ChatStreamChunk {
  id: string
  content: string
  role: string
  timestamp: Date | string
  sessionId: string
  isComplete: boolean
  // Enhanced Chat API와 호환되도록 필드명 업데이트
  toolCall?: string // 실행된 도구 이름
  toolStatus?: 'running' | 'completed' | 'error' // 도구 실행 상태
  toolResult?: any // 도구 실행 결과
}

export const createChatMessage = (
  role: 'user' | 'assistant',
  content: string,
  sessionId?: string
): ChatMessage => ({
  id: crypto.randomUUID(),
  role,
  content,
  timestamp: new Date(),
  sessionId,
})

export const createChatSession = (title: string = 'New Chat'): ChatSession => ({
  id: crypto.randomUUID(),
  title,
  messageCount: 0,
  createdAt: new Date(),
  updatedAt: new Date(),
  titleGenerated: false,
  titleGeneratedAt: undefined,
})