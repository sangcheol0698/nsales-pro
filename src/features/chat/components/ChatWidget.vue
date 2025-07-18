<template>
  <div class="relative h-full w-full overflow-hidden">
    <!-- 채팅 헤더 - 절대 위치 고정 -->
    <div class="absolute top-0 left-0 right-0 z-20 p-4 border-b border-border bg-background/95 backdrop-blur-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Avatar class="h-6 w-6">
            <AvatarFallback class="bg-primary text-primary-foreground text-xs">
              AI
            </AvatarFallback>
          </Avatar>
          <div>
            <h3 class="font-semibold text-sm">Sales Assistant</h3>
            <p class="text-xs text-muted-foreground">
              {{ isConnected ? '온라인' : '연결 중...' }}
            </p>
          </div>
        </div>
        
        <div class="flex items-center gap-1">
          <MessageSearch
            :messages="messages"
            @select-message="scrollToMessage"
          />
          
          <KeyboardShortcuts />
          
          <Button
            variant="ghost"
            size="sm"
            @click="clearChat"
            :disabled="messages.length === 0"
            :aria-label="$t ? $t('chat.clearChat') : '채팅 지우기'"
            class="h-8 w-8 p-0"
          >
            <RotateCcw class="h-3 w-3" />
          </Button>
          
          <Button
            v-if="onMinimize"
            variant="ghost"
            size="sm"
            @click="onMinimize"
            :aria-label="$t ? $t('chat.minimizeChat') : '채팅 최소화'"
            class="h-8 w-8 p-0"
          >
            <Minimize2 class="h-3 w-3" />
          </Button>
        </div>
      </div>
    </div>

    <!-- 메시지 영역 - 절대 위치로 스크롤 영역 완전 분리 -->
    <div 
      ref="scrollAreaRef" 
      class="absolute top-[73px] bottom-[140px] left-0 right-0 overflow-y-auto overscroll-contain p-4 scroll-smooth scrollbar-gutter-stable"
      @scroll="handleScroll"
      style="scrollbar-width: thin;"
    >
      <!-- 로딩 더 많은 메시지 -->
      <div 
        v-if="isLoadingMore"
        class="flex items-center justify-center py-4"
      >
        <div class="flex items-center gap-2 text-sm text-muted-foreground">
          <div class="w-2 h-2 bg-current rounded-full animate-bounce"></div>
          <div class="w-2 h-2 bg-current rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
          <div class="w-2 h-2 bg-current rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          <span>이전 메시지를 불러오는 중...</span>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div v-if="messages.length === 0" class="text-center py-8">
        <div class="text-foreground/70">
          <Bot class="h-12 w-12 mx-auto mb-4 opacity-50" />
          <h4 class="font-medium mb-2">안녕하세요! 👋</h4>
          <p class="text-sm">
            영업 데이터나 프로젝트에 대해 궁금한 것이 있으시면 언제든 물어보세요.
          </p>
        </div>
      </div>
      
      <!-- 메시지 목록 -->
      <div v-else class="space-y-4">
        <ChatMessage
          v-for="message in messages"
          :key="message.id"
          :message="message"
          :is-typing="isLoading && message === messages[messages.length - 1] && message.role === 'assistant' && !message.content"
          @regenerate="handleRegenerateMessage"
          @delete="handleDeleteMessage"
        />
      </div>
      
      <!-- 스크롤 다운 버튼 -->
      <Transition
        enter-active-class="transition-all duration-300"
        leave-active-class="transition-all duration-300"
        enter-from-class="opacity-0 translate-y-2"
        leave-to-class="opacity-0 translate-y-2"
      >
        <Button
          v-if="showScrollToBottom"
          @click="scrollToBottom"
          size="sm"
          class="fixed bottom-36 right-6 rounded-full shadow-lg bg-primary hover:bg-primary/90 text-primary-foreground z-30"
        >
          <ChevronDown class="h-4 w-4" />
        </Button>
      </Transition>
    </div>

    <!-- 채팅 입력 영역 - 절대 위치 하단 고정 -->
    <div class="absolute bottom-0 left-0 right-0 z-20 border-t border-border bg-background">
      <ChatInput
        ref="chatInputRef"
        :disabled="isLoading"
        :is-loading="isLoading"
        @submit="sendMessage"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onMounted, watch } from 'vue'
import { Bot, RotateCcw, Minimize2, ChevronDown } from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Avatar, AvatarFallback } from '@/core/components/ui/avatar'
import { useToast } from '@/core/composables'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'
import MessageSearch from './MessageSearch.vue'
import KeyboardShortcuts from './KeyboardShortcuts.vue'
import { ChatRepository } from '../repository/ChatRepository'
import { createChatMessage, createChatSession } from '../entity/ChatMessage'
import type { ChatMessage as ChatMessageType, ChatSession } from '../entity/ChatMessage'

interface Props {
  sessionId?: string
  onMinimize?: () => void
}

const props = defineProps<Props>()

const toast = useToast()
const chatRepository = new ChatRepository()

const messages = ref<ChatMessageType[]>([])
const currentSession = ref<ChatSession>()
const isLoading = ref(false)
const isConnected = ref(true)
const isLoadingMore = ref(false)
const showScrollToBottom = ref(false)
const currentPage = ref(0)
const hasMoreMessages = ref(true)

const scrollAreaRef = ref()
const chatInputRef = ref()

const sendMessage = async (content: string, files?: File[]) => {
  if ((!content.trim() && (!files || files.length === 0)) || isLoading.value) return

  // 사용자 메시지 추가 (파일 정보 포함)
  let messageContent = content
  if (files && files.length > 0) {
    const fileInfo = files.map(file => `[첨부파일: ${file.name}]`).join(' ')
    messageContent = content ? `${content}\n\n${fileInfo}` : fileInfo
  }
  
  const userMessage = createChatMessage('user', messageContent, currentSession.value?.id)
  messages.value.push(userMessage)
  
  // 스크롤을 최하단으로
  await scrollToBottom()
  
  isLoading.value = true
  
  try {
    // 세션이 없으면 새로 생성
    if (!currentSession.value) {
      currentSession.value = await chatRepository.createSession('New Chat')
    }

    // AI 응답을 위한 임시 메시지
    const assistantMessage = createChatMessage('assistant', '', currentSession.value.id)
    messages.value.push(assistantMessage)
    
    await scrollToBottom()

    // 스트리밍으로 응답 받기
    let fullContent = ''
    await chatRepository.streamMessage(
      {
        content: content,
        sessionId: currentSession.value.id,
      },
      (chunk) => {
        if (!chunk.isComplete) {
          fullContent += chunk.content
          // 마지막 메시지 업데이트
          const lastMessage = messages.value[messages.value.length - 1]
          if (lastMessage.role === 'assistant') {
            lastMessage.content = fullContent
          }
          scrollToBottom()
        }
      },
      (error) => {
        console.error('Chat error:', error)
        toast.error('AI 응답 실패', {
          description: 'AI 응답 중 오류가 발생했습니다.',
        })
        
        // 오류 발생 시 빈 AI 메시지 제거
        if (messages.value[messages.value.length - 1]?.content === '') {
          messages.value.pop()
        }
      }
    )
  } catch (error) {
    console.error('Send message error:', error)
    toast.error('메시지 전송 실패', {
      description: '메시지 전송 중 오류가 발생했습니다.',
    })
  } finally {
    isLoading.value = false
  }
}

const clearChat = () => {
  messages.value = []
  currentSession.value = undefined
  nextTick(() => {
    try {
      if (chatInputRef.value && typeof chatInputRef.value.focus === 'function') {
        chatInputRef.value.focus()
      }
    } catch (error) {
      console.warn('Failed to focus chat input:', error)
    }
  })
}

const handleRegenerateMessage = async (messageId: string) => {
  try {
    const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
    if (messageIndex === -1) return

    // 해당 메시지와 그 이후 메시지들 제거
    messages.value.splice(messageIndex)
    
    // 이전 사용자 메시지 찾기
    const previousUserMessage = messages.value
      .slice()
      .reverse()
      .find(msg => msg.role === 'user')
    
    if (!previousUserMessage) {
      toast.error('재생성 실패', {
        description: '이전 사용자 메시지를 찾을 수 없습니다.'
      })
      return
    }

    // 새 AI 메시지 생성
    const assistantMessage = createChatMessage('assistant', '', currentSession.value?.id)
    messages.value.push(assistantMessage)
    
    await scrollToBottom()
    isLoading.value = true

    // 스트리밍으로 재생성
    let fullContent = ''
    await chatRepository.streamMessage(
      {
        content: previousUserMessage.content,
        sessionId: currentSession.value?.id || ''
      },
      (chunk) => {
        if (!chunk.isComplete) {
          fullContent += chunk.content
          // 마지막 메시지 업데이트
          const lastMessage = messages.value[messages.value.length - 1]
          if (lastMessage.role === 'assistant') {
            lastMessage.content = fullContent
          }
          scrollToBottom()
        }
      },
      (error) => {
        console.error('Regenerate error:', error)
        toast.error('재생성 실패', {
          description: '메시지 재생성 중 오류가 발생했습니다.'
        })
      }
    )
  } catch (error) {
    console.error('Regenerate message error:', error)
    toast.error('재생성 실패', {
      description: '메시지 재생성 중 오류가 발생했습니다.'
    })
  } finally {
    isLoading.value = false
  }
}

const handleDeleteMessage = async (messageId: string) => {
  try {
    const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
    if (messageIndex === -1) return

    // UI에서 메시지 제거
    messages.value.splice(messageIndex, 1)
    
    // 서버에서도 메시지 삭제 (옵션)
    // await chatRepository.deleteMessage(messageId)
    
    toast.success('메시지 삭제', {
      description: '메시지가 삭제되었습니다.'
    })
  } catch (error) {
    console.error('Delete message error:', error)
    toast.error('삭제 실패', {
      description: '메시지 삭제 중 오류가 발생했습니다.'
    })
  }
}

const scrollToBottom = async () => {
  await nextTick()
  const scrollElement = scrollAreaRef.value
  if (scrollElement) {
    scrollElement.scrollTop = scrollElement.scrollHeight
  }
}

const handleScroll = async (event: Event) => {
  const target = event.target as HTMLDivElement
  const { scrollTop, scrollHeight, clientHeight } = target
  
  // 스크롤 하단 버튼 표시/숨김
  const isNearBottom = scrollTop + clientHeight >= scrollHeight - 100
  showScrollToBottom.value = !isNearBottom
  
  // 무한 스크롤 - 상단에 도달했을 때 이전 메시지 로드
  if (scrollTop <= 50 && !isLoadingMore.value && hasMoreMessages.value) {
    await loadMoreMessages()
  }
}

const loadMoreMessages = async () => {
  if (!currentSession.value || isLoadingMore.value || !hasMoreMessages.value) return
  
  isLoadingMore.value = true
  
  try {
    // 현재 스크롤 위치 저장
    const scrollElement = scrollAreaRef.value
    const previousScrollHeight = scrollElement?.scrollHeight || 0
    
    // 다음 페이지 메시지 로드 (실제 구현에서는 API 호출)
    currentPage.value++
    
    // 데모: 더 많은 메시지 시뮬레이션
    const moreMessages = await simulateLoadMoreMessages(currentSession.value.id, currentPage.value)
    
    if (moreMessages.length > 0) {
      // 새 메시지를 기존 메시지 앞에 추가
      messages.value.unshift(...moreMessages)
      
      // 스크롤 위치 유지
      await nextTick()
      if (scrollElement) {
        const newScrollHeight = scrollElement.scrollHeight
        scrollElement.scrollTop = newScrollHeight - previousScrollHeight
      }
    } else {
      hasMoreMessages.value = false
    }
  } catch (error) {
    console.error('Load more messages error:', error)
    toast.error('메시지 로드 실패', {
      description: '이전 메시지를 불러오는 중 오류가 발생했습니다.'
    })
  } finally {
    isLoadingMore.value = false
  }
}

// 더 많은 메시지 로드 시뮬레이션 함수
const simulateLoadMoreMessages = async (sessionId: string, page: number) => {
  // 실제 구현에서는 API 호출로 대체
  return new Promise<ChatMessageType[]>((resolve) => {
    setTimeout(() => {
      if (page > 3) {
        resolve([]) // 더 이상 메시지가 없음
        return
      }
      
      const moreMessages: ChatMessageType[] = []
      for (let i = 0; i < 5; i++) {
        moreMessages.push({
          id: `demo-${page}-${i}`,
          content: `이전 메시지 ${page}-${i + 1}`,
          role: i % 2 === 0 ? 'user' : 'assistant',
          timestamp: new Date(Date.now() - (page * 24 * 60 * 60 * 1000) - (i * 60 * 60 * 1000)),
          sessionId
        })
      }
      resolve(moreMessages)
    }, 1000)
  })
}

// 메시지 검색 결과로 스크롤
const scrollToMessage = (messageId: string) => {
  const messageElement = document.querySelector(`[data-message-id="${messageId}"]`)
  if (messageElement) {
    messageElement.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'center' 
    })
    // 하이라이트 효과
    messageElement.classList.add('ring-2', 'ring-primary', 'ring-offset-2')
    setTimeout(() => {
      messageElement.classList.remove('ring-2', 'ring-primary', 'ring-offset-2')
    }, 2000)
  }
}

const loadSession = async () => {
  if (!props.sessionId) return
  
  try {
    const session = await chatRepository.getSession(props.sessionId)
    currentSession.value = session
    
    // 메시지 히스토리 로드
    const history = await chatRepository.getMessageHistory(props.sessionId)
    messages.value = history.messages
    
    await scrollToBottom()
  } catch (error) {
    console.error('Load session error:', error)
    toast.error('채팅 세션 로드 실패', {
      description: '채팅 세션을 불러오는 중 오류가 발생했습니다.',
    })
  }
}

// sessionId가 변경될 때마다 새 세션 로드
watch(() => props.sessionId, (newSessionId) => {
  if (newSessionId) {
    // 상태 초기화
    currentPage.value = 0
    hasMoreMessages.value = true
    isLoadingMore.value = false
    showScrollToBottom.value = false
    
    loadSession()
  } else {
    messages.value = []
    currentSession.value = undefined
    currentPage.value = 0
    hasMoreMessages.value = true
    isLoadingMore.value = false
    showScrollToBottom.value = false
  }
}, { immediate: true })

onMounted(() => {
  nextTick(() => {
    try {
      if (chatInputRef.value && typeof chatInputRef.value.focus === 'function') {
        chatInputRef.value.focus()
      }
    } catch (error) {
      console.warn('Failed to focus chat input:', error)
    }
  })
})
</script>