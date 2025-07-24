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
            aria-label="채팅 지우기"
            class="h-8 w-8 p-0"
          >
            <RotateCcw class="h-3 w-3" />
          </Button>
          
          <Button
            v-if="onMinimize"
            variant="ghost"
            size="sm"
            @click="onMinimize"
            aria-label="채팅 최소화"
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
import { ref, nextTick, onMounted, watch } from 'vue'
import { Bot, RotateCcw, Minimize2, ChevronDown } from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Avatar, AvatarFallback } from '@/core/components/ui/avatar'
import { useToast } from '@/core/composables'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'
import MessageSearch from './MessageSearch.vue'
import KeyboardShortcuts from './KeyboardShortcuts.vue'
import { ChatRepository } from '../repository/ChatRepository'
import { createChatMessage } from '../entity/ChatMessage'
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
const showScrollToBottom = ref(false)

const scrollAreaRef = ref()
const chatInputRef = ref()

const sendMessage = async (content: string, files?: File[], model?: string, webSearch?: boolean, useEnhancedAPI?: boolean) => {
  if ((!content.trim() && (!files || files.length === 0)) || isLoading.value) return

  isLoading.value = true
  
  try {
    // 세션이 없으면 새로 생성
    if (!currentSession.value) {
      currentSession.value = await chatRepository.createSession('New Chat')
    }

    let response: any
    
    // 파일이 첨부된 경우도 스트리밍 방식으로 처리
    if (files && files.length > 0) {
      console.log('🖼️ Sending message with files (streaming):', files.map(f => f.name))
      
      // 사용자 메시지 먼저 추가 (파일 정보 포함)
      const userMessage = createChatMessage('user', content, currentSession.value.id)
      // 파일 정보를 메시지에 추가
      userMessage.attachedFiles = files.map(file => ({
        name: file.name,
        size: file.size,
        type: file.type
      }))
      messages.value.push(userMessage)
      
      await scrollToBottom()

      // AI 응답을 위한 임시 메시지 (이미지 분석 중 상태)
      const assistantMessage = createChatMessage('assistant', '', currentSession.value.id)
      assistantMessage.isAnalyzing = true
      assistantMessage.analyzingType = files.some(f => f.type.startsWith('image/')) ? 'image' : 'document'
      messages.value.push(assistantMessage)
      
      await scrollToBottom()

      // 파일 업로드 처리 (기존 API 사용 + 분석 상태 시뮬레이션)
      try {
        // 분석 시간 시뮬레이션 (이미지는 더 오래)
        const analysisTime = files.some(f => f.type.startsWith('image/')) ? 2000 : 1000
        
        // 분석 시뮬레이션
        setTimeout(() => {
          if (assistantMessage.isAnalyzing) {
            assistantMessage.isAnalyzing = false
            delete assistantMessage.analyzingType
          }
        }, analysisTime)
        
        // 기존 파일 업로드 API 호출
        const response = await chatRepository.sendMessageWithFiles(
          content,
          currentSession.value.id,
          files,
          model,
          webSearch
        )
        
        // 분석 완료 후 응답 처리
        if (response?.userMessage && response?.aiMessage) {
          // 기존 사용자 메시지와 분석 중 메시지 제거
          if (messages.value.length >= 2) {
            messages.value.splice(-2, 2)
          }
          
          // 새로운 사용자 메시지 추가 (파일 정보 포함)
          const newUserMessage = {
            id: response.userMessage.id,
            content: response.userMessage.content,
            role: response.userMessage.role,
            timestamp: new Date(response.userMessage.timestamp),
            sessionId: response.userMessage.sessionId,
            attachedFiles: files.map(file => ({
              name: file.name,
              size: file.size,
              type: file.type
            }))
          }
          messages.value.push(newUserMessage)
          
          // AI 응답 메시지 추가
          messages.value.push({
            id: response.aiMessage.id,
            content: response.aiMessage.content,
            role: response.aiMessage.role,
            timestamp: new Date(response.aiMessage.timestamp),
            sessionId: response.aiMessage.sessionId
          })
          
          await scrollToBottom()
          
          toast.success('파일 분석 완료', {
            description: `${files.length}개의 파일이 성공적으로 분석되었습니다.`
          })
        }
      } catch (error) {
        console.error('File upload error:', error)
        
        // 분석 실패 상태로 변경
        if (assistantMessage.isAnalyzing) {
          assistantMessage.isAnalyzing = false
          assistantMessage.content = '파일 분석 중 오류가 발생했습니다.'
        }
        
        toast.error('파일 업로드 실패', {
          description: '파일 업로드 중 오류가 발생했습니다.',
        })
      }
      
      // 파일 업로드 완료 후 최종 스크롤
      setTimeout(() => {
        scrollToBottom(true)
      }, 300)
      return // 파일 업로드의 경우 여기서 종료
    } else if (useEnhancedAPI) {
      // Enhanced Chat API 사용 (AI Tools 지원)
      console.log('🚀 Using Enhanced Chat API with Tools support')
      
      // 사용자 메시지 추가
      const userMessage = createChatMessage('user', content, currentSession.value.id)
      messages.value.push(userMessage)
      
      // 스크롤을 최하단으로
      await scrollToBottom()

      // AI 응답을 위한 임시 메시지
      const assistantMessage = createChatMessage('assistant', '', currentSession.value.id)
      messages.value.push(assistantMessage)
      
      await scrollToBottom()

      // Enhanced Chat API로 스트리밍 응답 받기
      let fullContent = ''
      let lastScrollTime = 0
      await chatRepository.sendEnhancedMessage(
        {
          message: content,
          sessionId: currentSession.value.id,
          model: model || 'gpt-3.5-turbo',
          webSearch: webSearch
        },
        (chunk) => {
          if (!chunk.isComplete) {
            // Tool 실행 상태 처리
            if (chunk.toolCall) {
              const lastMessage = messages.value[messages.value.length - 1]
              if (lastMessage.role === 'assistant') {
                lastMessage.toolCall = chunk.toolCall
                lastMessage.toolStatus = chunk.toolStatus
                lastMessage.toolResult = chunk.toolResult
              }
              
              if (chunk.toolStatus === 'running') {
                console.log(`🔧 Tool ${chunk.toolCall} 실행 중...`)
              } else if (chunk.toolStatus === 'completed') {
                console.log(`✅ Tool ${chunk.toolCall} 완료:`, chunk.toolResult)
              } else if (chunk.toolStatus === 'error') {
                console.log(`❌ Tool ${chunk.toolCall} 오류`)
              }
            }
            
            fullContent += chunk.content
            // 마지막 메시지 업데이트
            const lastMessage = messages.value[messages.value.length - 1]
            if (lastMessage.role === 'assistant') {
              lastMessage.content = fullContent
            }
            
            // 스크롤 최적화
            const hasCodeOrMarkdown = fullContent.includes('```') || 
                                    fullContent.includes('##') || 
                                    fullContent.includes('**') ||
                                    fullContent.includes('[') ||
                                    fullContent.includes('|')
            
            const scrollInterval = hasCodeOrMarkdown ? 50 : 100
            const now = Date.now()
            if (now - lastScrollTime > scrollInterval) {
              scrollToBottom(hasCodeOrMarkdown)
              lastScrollTime = now
            }
          }
        },
        (error) => {
          console.error('Enhanced Chat error:', error)
          toast.error('AI 응답 실패', {
            description: 'AI Tools 시스템 응답 중 오류가 발생했습니다.',
          })
          
          // 오류 발생 시 빈 AI 메시지 제거
          if (messages.value[messages.value.length - 1]?.content === '') {
            messages.value.pop()
          }
        }
      )
    } else {
      // 기존 스트리밍 API 사용
      // 사용자 메시지 추가
      const userMessage = createChatMessage('user', content, currentSession.value.id)
      messages.value.push(userMessage)
      
      // 스크롤을 최하단으로
      await scrollToBottom()

      // AI 응답을 위한 임시 메시지
      const assistantMessage = createChatMessage('assistant', '', currentSession.value.id)
      messages.value.push(assistantMessage)
      
      await scrollToBottom()

      // 기존 스트리밍으로 응답 받기
      let fullContent = ''
      let lastScrollTime = 0
      await chatRepository.streamMessage(
        {
          content: content,
          sessionId: currentSession.value.id,
          model: model,
          webSearch: webSearch
        },
        (chunk) => {
          if (!chunk.isComplete) {
            // Tool Calling 상태 체크 (기존 API용)
            if (chunk.toolCall) {
              if (chunk.toolStatus === 'running') {
                console.log(`🔄 Tool ${chunk.toolCall} 실행 중...`)
              } else if (chunk.toolStatus === 'completed') {
                console.log(`✅ Tool ${chunk.toolCall} 완료`)
              } else if (chunk.toolStatus === 'error') {
                console.log(`❌ Tool ${chunk.toolCall} 오류`)
              }
            }
            
            fullContent += chunk.content
            // 마지막 메시지 업데이트
            const lastMessage = messages.value[messages.value.length - 1]
            if (lastMessage.role === 'assistant') {
              lastMessage.content = fullContent
            }
            
            const hasCodeOrMarkdown = fullContent.includes('```') || 
                                    fullContent.includes('##') || 
                                    fullContent.includes('**') ||
                                    fullContent.includes('[') ||
                                    fullContent.includes('|')
            
            const scrollInterval = hasCodeOrMarkdown ? 50 : 100
            const now = Date.now()
            if (now - lastScrollTime > scrollInterval) {
              scrollToBottom(hasCodeOrMarkdown)
              lastScrollTime = now
            }
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
    }
    
    // 파일이 없는 경우에만 스트리밍 완료 후 최종 스크롤
    if (!files || files.length === 0) {
      setTimeout(() => {
        scrollToBottom(true)
      }, 300)
      return // 스트리밍의 경우 여기서 종료
    }

    // 파일 업로드 응답 처리
    if (response?.userMessage && response?.aiMessage) {
      // 사용자 메시지 추가
      messages.value.push({
        id: response.userMessage.id,
        content: response.userMessage.content,
        role: response.userMessage.role,
        timestamp: new Date(response.userMessage.timestamp),
        sessionId: response.userMessage.sessionId
      })
      
      // AI 응답 메시지 추가
      messages.value.push({
        id: response.aiMessage.id,
        content: response.aiMessage.content,
        role: response.aiMessage.role,
        timestamp: new Date(response.aiMessage.timestamp),
        sessionId: response.aiMessage.sessionId
      })
      
      await scrollToBottom()
      
      toast.success('파일 업로드 완료', {
        description: `${files?.length}개의 파일이 성공적으로 분석되었습니다.`
      })
    }
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
    let lastScrollTime = 0
    await chatRepository.streamMessage(
      {
        content: previousUserMessage.content,
        sessionId: currentSession.value?.id || '',
        model: 'gpt-4o', // 재생성에서는 기본 모델 사용
        webSearch: false // 재생성에서는 웹 검색 비활성화
      },
      (chunk) => {
        if (!chunk.isComplete) {
          // Tool Calling 상태 체크
          if (chunk.toolCall) {
            if (chunk.toolStatus === 'running') {
              console.log(`🔄 Tool ${chunk.toolCall} 재실행 중...`)
            } else if (chunk.toolStatus === 'completed') {
              console.log(`✅ Tool ${chunk.toolCall} 재실행 완료`)
            } else if (chunk.toolStatus === 'error') {
              console.log(`❌ Tool ${chunk.toolCall} 재실행 오류`)
            }
          }
          
          fullContent += chunk.content
          // 마지막 메시지 업데이트
          const lastMessage = messages.value[messages.value.length - 1]
          if (lastMessage.role === 'assistant') {
            lastMessage.content = fullContent
          }
          // 코드 블록이나 마크다운 감지 시 더 자주 스크롤
          const hasCodeOrMarkdown = fullContent.includes('```') || 
                                  fullContent.includes('##') || 
                                  fullContent.includes('**') ||
                                  fullContent.includes('[') ||
                                  fullContent.includes('|')
          
          const scrollInterval = hasCodeOrMarkdown ? 50 : 100 // 코드가 있으면 더 자주
          const now = Date.now()
          if (now - lastScrollTime > scrollInterval) {
            scrollToBottom(hasCodeOrMarkdown)
            lastScrollTime = now
          }
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
    // 재생성 완료 후 최종 스크롤
    setTimeout(() => {
      scrollToBottom(true)
    }, 300)
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

const scrollToBottom = async (force = false) => {
  // 여러 번의 nextTick을 통해 마크다운 렌더링 완료 대기
  await nextTick()
  await nextTick()
  
  const scrollElement = scrollAreaRef.value
  if (scrollElement) {
    const targetScrollTop = scrollElement.scrollHeight
    
    // 부드러운 스크롤 애니메이션
    if (force || Math.abs(scrollElement.scrollTop - targetScrollTop) > 100) {
      scrollElement.scrollTo({
        top: targetScrollTop,
        behavior: 'smooth'
      })
    } else {
      scrollElement.scrollTop = targetScrollTop
    }
    
    // 코드 블록 등의 지연 렌더링을 위한 추가 체크
    setTimeout(() => {
      if (scrollElement.scrollTop < scrollElement.scrollHeight - scrollElement.clientHeight - 50) {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }
    }, 150)
  }
}

const handleScroll = async (event: Event) => {
  const target = event.target as HTMLDivElement
  const { scrollTop, scrollHeight, clientHeight } = target
  
  // 스크롤 하단 버튼 표시/숨김
  const isNearBottom = scrollTop + clientHeight >= scrollHeight - 100
  showScrollToBottom.value = !isNearBottom
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
    
    // 세션 로드시 항상 마지막 메시지로 스크롤
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
    showScrollToBottom.value = false
    
    loadSession()
  } else {
    messages.value = []
    currentSession.value = undefined
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