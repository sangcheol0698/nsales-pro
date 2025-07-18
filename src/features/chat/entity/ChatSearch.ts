export interface ChatSearch {
  query?: string
  sessionId?: string
  startDate?: string
  endDate?: string
  page: number
  size: number
  sort?: string
}

export interface ChatSessionList {
  sessions: ChatSession[]
  totalElements: number
  totalPages: number
  currentPage: number
  size: number
}

export interface ChatHistory {
  messages: ChatMessage[]
  sessionId: string
  totalCount: number
}

import type { ChatSession, ChatMessage } from './ChatMessage'