<template>
  <Card class="flex flex-col h-full">
    <CardHeader class="pb-3 border-b">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Avatar class="h-8 w-8">
            <AvatarFallback class="bg-primary text-primary-foreground">
              AI
            </AvatarFallback>
          </Avatar>
          <div>
            <h3 class="font-semibold">Sales Assistant</h3>
            <p class="text-xs text-foreground/70">
              {{ isConnected ? '온라인' : '연결 중...' }}
            </p>
          </div>
        </div>
        
        <div class="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            @click="clearChat"
            :disabled="messages.length === 0"
          >
            <RotateCcw class="h-4 w-4" />
          </Button>
          
          <Button
            v-if="onMinimize"
            variant="ghost"
            size="sm"
            @click="onMinimize"
          >
            <Minimize2 class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </CardHeader>

    <CardContent class="flex-1 flex flex-col p-0 overflow-hidden">
      <ScrollArea ref="scrollAreaRef" class="flex-1 p-4">
        <div v-if="messages.length === 0" class="text-center py-8">
          <div class="text-foreground/70">
            <Bot class="h-12 w-12 mx-auto mb-4 opacity-50" />
            <h4 class="font-medium mb-2">안녕하세요! 👋</h4>
            <p class="text-sm">
              영업 데이터나 프로젝트에 대해 궁금한 것이 있으시면 언제든 물어보세요.
            </p>
          </div>
        </div>
        
        <div v-else>
          <ChatMessage
            v-for="message in messages"
            :key="message.id"
            :message="message"
          />
        </div>
      </ScrollArea>

      <ChatInput
        ref="chatInputRef"
        :disabled="isLoading"
        :is-loading="isLoading"
        @submit="sendMessage"
      />
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onMounted, watch } from 'vue'
import { Bot, RotateCcw, Minimize2 } from 'lucide-vue-next'
import { Card, CardContent, CardHeader } from '@/core/components/ui/card'
import { Button } from '@/core/components/ui/button'
import { Avatar, AvatarFallback } from '@/core/components/ui/avatar'
import { ScrollArea } from '@/core/components/ui/scroll-area'
import { useToast } from '@/core/composables'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'
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

const scrollAreaRef = ref()
const chatInputRef = ref()

const sendMessage = async (content: string) => {
  if (!content.trim() || isLoading.value) return

  // 사용자 메시지 추가
  const userMessage = createChatMessage('user', content, currentSession.value?.id)
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

const scrollToBottom = async () => {
  await nextTick()
  const scrollElement = scrollAreaRef.value?.$el?.querySelector('[data-radix-scroll-area-content]')
  if (scrollElement) {
    scrollElement.scrollTop = scrollElement.scrollHeight
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
    loadSession()
  } else {
    messages.value = []
    currentSession.value = undefined
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