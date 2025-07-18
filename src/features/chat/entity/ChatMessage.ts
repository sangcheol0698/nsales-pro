export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date | string
  sessionId?: string
}

export interface ChatSession {
  id: string
  title: string
  messageCount: number
  createdAt: Date | string
  updatedAt: Date | string
}

export interface ChatRequest {
  content: string
  sessionId: string
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
})